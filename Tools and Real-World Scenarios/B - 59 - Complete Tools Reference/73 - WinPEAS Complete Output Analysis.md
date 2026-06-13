---
tags: [tools, privesc, enumeration, vapt]
difficulty: advanced
module: "59 - Complete Tools Reference"
topic: "59.73 WinPEAS Complete Output Analysis"
---

# WinPEAS: Complete Output Analysis

## 1. Introduction to WinPEAS

`WinPEAS` (Windows Privilege Escalation Awesome Scripts) is the premier automated enumeration tool for Windows environments. It is part of the PEASS (Privilege Escalation Awesome Scripts SUITE) family, sharing the same design philosophy as its Linux counterpart, LinPEAS. Written primarily in C# (with older batch/PowerShell versions available), WinPEAS leverages native Windows APIs, WMI (Windows Management Instrumentation), and registry queries to systematically identify vectors for local privilege escalation.

Windows privilege escalation is inherently different from Linux. While Linux focuses heavily on file permissions, SUID binaries, and plain text configurations, Windows privilege escalation heavily involves the Registry, Windows Services, Active Directory domain configurations, COM objects, and Access Control Lists (ACLs). WinPEAS parses this complex ecosystem and highlights misconfigurations.

## 2. ASCII Architecture Diagram

```text
+-----------------------------------------------------------------------------------+
|                            WinPEAS Execution Flow                                 |
|                                                                                   |
|  +-----------------+       +---------------------------------------------------+  |
|  |                 |       |               Data Collection Engine              |  |
|  |    Attacker     |------>| 1. System Info (OS build, patches, LAPS status)   |  |
|  |  (Low Priv cmd) |       | 2. User & Group Privileges (SeImpersonate, etc.)  |  |
|  +-----------------+       | 3. Windows Services (Unquoted paths, weak ACLs)   |  |
|                            | 4. Scheduled Tasks & Autoruns                     |  |
|                            | 5. Registry Analysis (AlwaysInstallElevated, SAM) |  |
|                            | 6. Network (Active Connections, Firewall rules)   |  |
|                            | 7. File System (SAM/SYSTEM backups, DPAPI keys)   |  |
|                            | 8. Credential Hunting (Vault, Browsers, Unattend) |  |
|                            +---------------------------------------------------+  |
|                                                    |                              |
|                                                    v                              |
|                            +---------------------------------------------------+  |
|                            |         Access Control Analysis (ACLs)            |  |
|                            | Evaluates SDDLs (Security Descriptor Definition   |  |
|                            | Language) to determine if current user has        |  |
|                            | GenericWrite, WriteDacl, or FullControl over      |  |
|                            | sensitive objects (services, registry keys, files)|  |
|                            +---------------------------------------------------+  |
|                                                    |                              |
|                                                    v                              |
|                            +---------------------------------------------------+  |
|                            |                 Colorized Output                  |  |
|                            | [RED/YELLOW] 99% Certain Privilege Escalation     |  |
|                            | [RED] High Probability Vector / Critical Finding  |  |
|                            | [CYAN] Notable Finding, Requires Investigation    |  |
|                            | [GREEN] Standard Configuration / Safe             |  |
|                            +---------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

## 3. Deployment and Execution

### 3.1 Antivirus and EDR Considerations
Unlike Linux environments where LinPEAS often runs unimpeded, Windows Defender and third-party EDR solutions aggressively flag WinPEAS executables and scripts. Executing the standard `winPEASany.exe` on disk will almost certainly result in the file being quarantined and an alert being generated.

**Evasion Strategies:**
1.  **Obfuscation:** Compiling from source with heavy obfuscation and string encryption.
2.  **In-Memory Execution (PowerShell):** Bypassing AMSI (Antimalware Scan Interface) and executing a PowerShell implementation of WinPEAS entirely in memory.
3.  **Command-Line Parameter Dropping:** Executing only specific modules of WinPEAS to reduce the behavioral signature.

```cmd
:: Executing specific modules to minimize noise
winPEASany.exe quiet servicesinfo
winPEASany.exe quiet credentials
```

### 3.2 Output Redirection
The output in the Windows command prompt can be difficult to scroll through. Redirecting output with color stripping is often necessary for offline analysis.
```cmd
winPEASany.exe quiet cmd > output.txt
```

## 4. Analyzing the Output: Section by Section

### 4.1 System Information
- **OS Version & Patch Level:** Highlights missing KBs (Knowledge Base articles) that correspond to known local privilege escalation CVEs (e.g., PrintNightmare, PetitPotam, various ALPC bugs).
- **LAPS (Local Administrator Password Solution):** Indicates if LAPS is installed. If so, local admin passwords rotate automatically, making local credential dumping less useful for lateral movement.

### 4.2 User Privileges (Critical)
Windows assigns specific "Tokens" to users. Certain privileges are inherently dangerous and can be abused.
- **`SeImpersonatePrivilege` / `SeAssignPrimaryTokenPrivilege`:** If the user possesses these tokens (common for service accounts like IIS `NETWORK SERVICE`), it is a guaranteed privilege escalation vector. Attackers utilize tools like "Potato" variants (JuicyPotato, RoguePotato, GodPotato) to force SYSTEM to authenticate to an attacker-controlled COM server, intercept the SYSTEM token, and impersonate it.
- **`SeBackupPrivilege` / `SeRestorePrivilege`:** Allows the user to bypass file ACLs and read any file on the system, including the `SAM` and `SYSTEM` registry hives, leading to credential dumping.

### 4.3 Services Information (Highly Actionable)
Windows services run in the background, frequently as `NT AUTHORITY\SYSTEM`. Misconfigurations here are primary vectors.
- **Unquoted Service Paths:** If a service path contains spaces but is not enclosed in quotes (e.g., `C:\Program Files\App\service.exe`), the Windows service control manager will attempt to execute `C:\Program.exe` or `C:\Program Files\App.exe` first. If the attacker has write access to the root of the `C:\` drive or the `Program Files` directory, they can place a malicious executable named `Program.exe`, which will be executed as SYSTEM when the service starts. WinPEAS flags these explicitly.
- **Weak Service Permissions (Service ACLs):** The DACL of the service itself might allow a low-privileged user to modify the service configuration (`SERVICE_CHANGE_CONFIG`). The attacker can simply run:
  `sc config VulnerableService binpath= "net localgroup administrators username /add"`
- **Modifiable Binary Paths:** Even if the service configuration is locked down, the actual executable file (e.g., `service.exe`) or its parent directory might be writable by standard users.

### 4.4 Registry Analysis
- **AlwaysInstallElevated:** If both the `HKCU` and `HKLM` keys for `AlwaysInstallElevated` are set to `1`, any user can install `.msi` packages with SYSTEM privileges. The attacker generates a malicious MSI payload using `msfvenom` and executes it.
- **AutoLogon Credentials:** System administrators occasionally configure machines to automatically log in, storing the plaintext password in the registry under `Winlogon`. WinPEAS extracts these keys.
- **SAM & SYSTEM Backup Files:** WinPEAS checks for the presence of registry backups in locations like `C:\Windows\Repair\` or `C:\Windows\System32\config\RegBack\`. These backups can be exfiltrated and cracked offline to obtain local hashes.

### 4.5 File System and Scheduled Tasks
- **Scheduled Tasks:** Tasks scheduled to run as `SYSTEM` or other privileged users. Similar to services, if the binary path is writable or unquoted, it can be hijacked.
- **Unattended Installation Files:** `unattend.xml` or `sysprep.inf` files left over from OS deployment often contain base64 encoded local administrator passwords. WinPEAS automatically hunts for these files.
- **WSUS Configuration:** If the system is configured to receive updates from a local WSUS server without requiring HTTPS, attackers can spoof the WSUS server and push malicious updates as SYSTEM.

### 4.6 Passwords and Credentials
WinPEAS thoroughly interrogates the system for stored secrets.
- **Windows Vault & Credential Manager:** Extracts saved passwords for network shares, RDP sessions, or web applications.
- **Browser Profiles:** Checks for Chrome, Edge, and Firefox profiles containing saved passwords and cookies.
- **PowerShell History (`ConsoleHost_history.txt`):** Users frequently type passwords directly into PowerShell scripts or command line arguments. WinPEAS dumps the history file.

## 5. Interpreting Advanced Output

### 5.1 Understanding SDDL
WinPEAS output frequently references SDDL (Security Descriptor Definition Language) strings.
Example: `D:(A;;CCLCSWRPWPDTLOCRRC;;;SY)(A;;CCDCLCSWRPWPDTLOCRSDRCWDWO;;;BA)(A;;CCLCSWLOCRRC;;;IU)(A;;CCLCSWLOCRRC;;;SU)`
While complex, WinPEAS attempts to translate these into readable formats. The key identifier to look for in the translated output is `WriteData`, `AppendData`, or `GenericAll` assigned to `BUILTIN\Users` or `Everyone`.

### 5.2 DLL Hijacking Identification
While WinPEAS does not actively exploit DLL hijacking, it identifies directories in the system `%PATH%` that are writable by standard users. If an application (running as SYSTEM) attempts to load a DLL that does not exist in its application directory, it will search the `%PATH%`. An attacker can place a malicious DLL in the writable directory to gain execution.

## 6. Chaining Opportunities
- **[[Potato Privilege Escalation]]:** Triggered immediately upon finding `SeImpersonatePrivilege` in WinPEAS output.
- **[[Token Impersonation Techniques]]:** Understanding how the underlying mechanics of WinPEAS's privilege findings work.
- **[[74 - Seatbelt C Host Enumeration]]:** Seatbelt offers a more focused, often more stealthy, alternative to WinPEAS for situational awareness.
- **[[Unquoted Service Path Exploitation]]:** The direct exploitation step following a WinPEAS finding in the Services section.

## 7. Related Notes
- [[Windows Privilege Escalation Methodology]]: Broad overview of attacking Windows hosts.
- [[Abusing Windows Registry for Privesc]]: Deep dive into `AlwaysInstallElevated` and SAM extraction.
- [[AMSI Bypass Techniques]]: Required reading to execute WinPEAS in memory against modern defenses.
