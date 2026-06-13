---
tags: [interview, active-directory, qna, scenario]
difficulty: expert
module: "Interview Prep - Active Directory"
topic: "QnA - AD Module 66"
---

# QnA - AD Module 66: Local Privilege Escalation (Windows)

## Architecture Overview: Windows Privileges and Tokens

```text
+-------------------------------------------------------------+
|               Windows Access Token Architecture             |
+-------------------------------------------------------------+
| User: WIN-DC01\Sanchit (S-1-5-21-...-1001)                  |
|                                                             |
| +--------------------+   +--------------------------------+ |
| |   Group SIDs       |   |      Privileges Array          | |
| |--------------------|   |--------------------------------| |
| | - Administrators   |   | [X] SeDebugPrivilege           | |
| | - Users            |   | [X] SeImpersonatePrivilege     | |
| | - Interactive      |   | [ ] SeAssignPrimaryToken       | |
| +--------------------+   | [X] SeTakeOwnershipPrivilege   | |
|                          +--------------------------------+ |
|                                                             |
| Integrity Level: High (S-1-16-12288)                        |
| Token Type: Primary (Process) / Impersonation (Thread)      |
+-------------------------------------------------------------+
       |
       |  (Process Execution)
       v
+-----------------------+     +-------------------------------+
| Process: cmd.exe      | --> |  Securable Object (File/Reg)  |
| Security Descriptor   |     |  DACL: Allow SYSTEM Full      |
+-----------------------+     +-------------------------------+
```

## Formal Technical Questions

### Q1: Explain the difference between a Primary Token and an Impersonation Token, and how attackers leverage them for Privilege Escalation.
**Answer:**
A **Primary Token** is assigned to a process upon creation and represents the security context of the user account associated with that process. It is the default token used for any thread within the process unless explicitly overridden. 
An **Impersonation Token** is typically applied at the thread level, allowing a thread to execute in a security context different from the process's primary token. This is fundamentally designed for client/server models (e.g., a service impersonating a client to access files on their behalf).

**Attacker Leverage:** 
Attackers abuse impersonation tokens through privileges like `SeImpersonatePrivilege` or `SeAssignPrimaryTokenPrivilege`. If an attacker compromises a service account running with these privileges (such as `IIS AppPool` or `NETWORK SERVICE`), they can coerce a highly privileged process (like `SYSTEM`) into authenticating to a named pipe or COM object controlled by the attacker. By calling functions like `ImpersonateNamedPipeClient`, the attacker receives a SYSTEM impersonation token, which they can then use to spawn a new process via `CreateProcessAsUser` or `CreateProcessWithTokenW`, effectively elevating to SYSTEM.

### Q2: What are Unquoted Service Paths, and what are the exact prerequisites for this vulnerability to be exploitable?
**Answer:**
An **Unquoted Service Path** is a local privilege escalation vulnerability caused when a Windows service executable path contains spaces and is not enclosed in quotation marks.
Windows uses the `CreateProcess` API to launch the service. When parsing a space-separated unquoted path, Windows attempts to execute each segment of the path preceding the space, appending `.exe` sequentially, before moving to the next segment.

**Prerequisites for Exploitation:**
1. **Unquoted Path with Spaces:** The `ImagePath` registry value for the service must contain spaces and no surrounding quotes (e.g., `C:\Program Files\Enterprise App\service.exe`).
2. **Write Permissions:** The attacker must have `Write` or `Create files / write data` permissions in one of the directories along the path (e.g., `C:\` or `C:\Program Files\`).
3. **Service Execution Rights:** The attacker must be able to restart the service (using `sc stop` and `sc start`), or the system must be rebooted (if the service is set to Auto-start).
4. **Privileged Execution Context:** The service must execute in the context of a higher-privileged user (like `LocalSystem`).

### Q3: Detail the mechanics of the AlwaysInstallElevated vulnerability and how an attacker abuses it.
**Answer:**
`AlwaysInstallElevated` is a Windows policy setting that directs the Windows Installer engine (`msiexec.exe`) to execute Microsoft Installer (`.msi`) packages with elevated (SYSTEM) privileges, regardless of the privileges of the user executing them.

**Mechanics:**
This requires two specific registry keys to be set to `1`:
- `HKCU\SOFTWARE\Policies\Microsoft\Windows\Installer\AlwaysInstallElevated`
- `HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer\AlwaysInstallElevated`

**Exploitation:**
An attacker generates a malicious `.msi` payload using tools like `msfvenom` (e.g., `msfvenom -p windows/x64/exec CMD=cmd.exe -f msi -o payload.msi`). They then execute the file via the command line: 
`msiexec /quiet /qn /i payload.msi`. 
Because the policy forces the installer to run as SYSTEM, the embedded custom action (the payload) executes as `NT AUTHORITY\SYSTEM`.

---

## Scenario-Based Questions

### Scenario 1: You are on a Red Team engagement. You have obtained a reverse shell as a standard domain user. You check the system and note that UAC is enabled at the highest level. You cannot drop exploit binaries due to heavy EDR presence. How do you escalate privileges?
**Answer:**
Operating under heavy EDR constraints means fileless or living-off-the-land (LotL) techniques are strictly required. Given UAC is at the highest level (Always Notify), standard auto-elevation bypasses (like `fodhelper.exe` or `slui.exe` registry hijacks) might either be blocked, heavily monitored, or prompt the user.
1. **Enumeration:** First, I would thoroughly enumerate misconfigurations using built-in tools (e.g., `wmic`, `powershell`, `icacls`, `sc`) without dropping tools like WinPEAS. 
2. **DLL Hijacking via Environment Variables:** I'd look for native Scheduled Tasks or legitimate applications running as an elevated user (or SYSTEM) that load DLLs from predictable locations where the standard user has write access. Specifically, checking for missing DLLs (Phantom DLL hijacking).
3. **Weak Registry/Service Permissions:** If a service has weak registry permissions (modifying `ImagePath`), I can change the path to point to a native LOLBin (like `cmd.exe /c powershell -enc ...`) rather than dropping a binary.
4. **Token Abuse (If applicable):** If the user is part of specific groups (e.g., Backup Operators), I would leverage `SeBackupPrivilege` to extract the `SYSTEM` and `SAM` registry hives natively via `reg save`, exfiltrate them, crack the local administrator hash, and reuse it.

### Scenario 2: You find a scheduled task that runs a custom script every 5 minutes as `SYSTEM`. You do not have write access to the script itself, nor the directory it resides in. How can you still abuse this task for privilege escalation?
**Answer:**
This scenario requires looking for indirect modification vectors. Since the file and directory are immutable for the current user, the approach relies on dependencies or environmental factors.
1. **Dependency Hijacking (Path Interception):** I would examine the contents of the script. Does it call other executables or scripts without absolute paths? If the script executes `task.exe` instead of `C:\Secure\task.exe`, I can place a malicious `task.exe` in a directory that is earlier in the system's `%PATH%` environment variable, or modify the user's `%PATH%` if applicable.
2. **DLL Hijacking:** If the script calls an executable, does that executable load DLLs? I would use tools like Procmon (if I can simulate this locally) to find `NAME NOT FOUND` errors for DLLs, and plant a malicious DLL in a writable directory within the search order.
3. **Parameter Injection:** If the script reads arguments from a registry key or a secondary configuration file that I *do* have write access to, I can inject command-line arguments to achieve arbitrary code execution.
4. **Network Share Hijacking:** If the script calls a resource from a network share (e.g., `\\server\share\script.ps1`), I might attempt LLMNR/NBT-NS spoofing (if the network is vulnerable) to redirect the request to an SMB share I control, serving a malicious payload.

### Scenario 3: After executing `whoami /priv`, you notice `SeImpersonatePrivilege` is enabled. You are running as a local Service Account. EDR is heavily monitoring `cmd.exe` and `powershell.exe` execution from IIS worker processes. How do you exploit this without triggering the EDR?
**Answer:**
This is a classic `JuicyPotato` / `PrintSpoofer` scenario, but with EDR evasion requirements.
1. **Avoiding cmd/powershell:** The EDR detects suspicious child processes from `w3wp.exe` or `svchost.exe`. To evade this, the exploitation must not spawn a new shell process. 
2. **In-Memory/Reflective Execution:** Instead of executing an arbitrary binary, I would compile a custom C# application or use an advanced post-exploitation framework (like Cobalt Strike's `execute-assembly` or Covenant) that abuses the RPC/DCOM communication locally to force the SYSTEM account to authenticate.
3. **Direct Token Manipulation:** Once the `SYSTEM` impersonation token is obtained, rather than using it to call `CreateProcessWithToken`, I would use the token to inject a payload directly into an existing, legitimate SYSTEM process (e.g., `spoolsv.exe` or `services.exe`) using Windows APIs like `OpenProcess`, `VirtualAllocEx`, `WriteProcessMemory`, and `CreateRemoteThread`. 
4. **Token Duplication:** Alternatively, impersonate the token on the current thread, and execute actions (like adding a user to the Administrators group via direct Win32 API calls rather than `net localgroup`) directly within the context of the running process, completely avoiding process creation.

---

## Deep-Dive Defensive Questions

### Q1: What forensic artifacts and telemetry would you analyze to detect PrintSpoofer or RoguePotato attacks in a corporate environment?
**Answer:**
**Event Logging (Sysmon / Security Event Logs):**
1. **Event ID 4624 (Logon):** Look for an anomalous number of Logon Type 3 (Network) logons originating from `127.0.0.1` or `::1`, particularly targeting `NT AUTHORITY\SYSTEM`. 
2. **Event ID 4688 (Process Creation):** Detect suspicious parent-child relationships. A service process like `w3wp.exe` or `sqlservr.exe` should almost never spawn `cmd.exe`, `net.exe`, or `whoami.exe`. 
3. **Event ID 4673 (Sensitive Privilege Use):** Monitor for the active usage of `SeImpersonatePrivilege` or `SeAssignPrimaryTokenPrivilege`, especially from accounts other than the standard OS components.
4. **Named Pipe Creation (Sysmon Event ID 17/18):** `PrintSpoofer` creates specific named pipes (e.g., `\\.\pipe\test\pipe\spoolss`). Look for unexpected named pipes or pipes simulating Microsoft RPC interfaces.
5. **RPC Filters:** Network and host-level monitoring of RPC calls to `RpcRemoteFindFirstPrinterChangeNotificationEx` (used by PrintSpoofer to coerce authentication).

### Q2: How can an organization systematically prevent Unquoted Service Path vulnerabilities?
**Answer:**
1. **Proactive Scanning:** Implement continuous configuration management (e.g., SCCM, Ansible) or vulnerability scanners (Nessus, Qualys) to regularly query the registry `HKLM\System\CurrentControlSet\Services` for `ImagePath` values lacking quotes but containing spaces.
2. **Automated Remediation Scripts:** Deploy Group Policy (GPO) startup scripts or PowerShell Desired State Configuration (DSC) to automatically parse and append quotes to vulnerable service paths.
3. **Strict Directory Permissions:** Enforce the principle of least privilege on the filesystem. Standard users should never have `Write` or `Append` permissions to root paths like `C:\` or structural folders like `C:\Program Files`.
4. **Application Whitelisting:** Enforce Windows Defender Application Control (WDAC) or AppLocker policies to prevent the execution of untrusted unsigned binaries, neutralizing the threat even if a binary is placed in the unquoted path.

### Q3: How do you harden a system against AlwaysInstallElevated abuse?
**Answer:**
The mitigation is straightforward but requires strict governance:
1. **Disable the Policy:** Ensure that the `AlwaysInstallElevated` setting is expressly defined and set to `Disabled` in Group Policy under:
   - `Computer Configuration -> Administrative Templates -> Windows Components -> Windows Installer`
   - `User Configuration -> Administrative Templates -> Windows Components -> Windows Installer`
2. **Registry Auditing:** Create an audit rule or use Sysmon/EDR to monitor the registry paths `HKLM\SOFTWARE\Policies\Microsoft\Windows\Installer` and `HKCU\...` for any modifications attempting to set `AlwaysInstallElevated` to `1`.
3. **MSI Execution Monitoring:** Monitor Event ID 1040 (Windows Installer started) and Event ID 1042 (Windows Installer ended) in the Application log, cross-referencing with the user context. If a low-privileged user starts an MSI installation that immediately escalates to SYSTEM, it warrants an immediate alert.

---

## Real-World Attack Scenario
**The IIS Foothold to Domain Dominance:**
During an incident response engagement for a financial institution, responders discovered a breach originating from an unpatched deserialization vulnerability in a public-facing IIS web application. 
The threat actors initially gained execution as the `IIS APPPOOL\DefaultAppPool` identity. Using a highly obfuscated web shell, they identified that the IIS worker process held `SeImpersonatePrivilege`.
Instead of dropping standard exploits like JuicyPotato, the attackers loaded a custom, in-memory C# assembly via the web shell. This assembly invoked the `RpcRemoteFindFirstPrinterChangeNotification` API locally to force the SYSTEM account to authenticate to a malicious named pipe. They captured the SYSTEM token, impersonated it in the current thread, and used the elevated context to execute `minidump` on the `lsass.exe` process. 
They extracted the dump file natively via SMB, cracked a Domain Admin's NTLM hash offline, and proceeded to execute a Golden Ticket attack, dominating the entire Active Directory forest within 45 minutes of the initial breach.

---

## Chaining Opportunities
- **Lateral Movement:** Local privilege escalation is almost always the prerequisite to credential dumping (e.g., Mimikatz). Once SYSTEM is achieved, attackers dump credentials or kerberos tickets to execute [[AD QnA - Module 67 - Pass the Hash PtH]] or [[AD QnA - Module 68 - Pass the Ticket PtT]].
- **Persistence:** Elevated access allows the installation of rootkits, modifying scheduled tasks, or adding backdoors into legitimate binaries (DLL side-loading), ensuring long-term access.
- **Defense Evasion:** SYSTEM privileges allow attackers to blind EDR agents, clear Event Logs (Event ID 1102), and modify firewall rules to facilitate command and control communication.

---

## Related Notes
- [[Privilege Escalation Methodologies]]
- [[Windows Access Tokens Explained]]
- [[Living off the Land Binaries (LOLBins)]]
- [[Bypassing User Account Control (UAC)]]
- [[Active Directory - Service Accounts Security]]
