---
tags: [windows, privesc, pentesting, red-team]
difficulty: advanced
module: "43 - Windows Privilege Escalation"
topic: "43.25 Abusing SeBackupPrivilege"
---

# 25 - Abusing SeBackupPrivilege and SeRestorePrivilege

## Executive Summary

The `SeBackupPrivilege` and `SeRestorePrivilege` are two of the most dangerous and abusable privileges that can be assigned to a user account or service principal within a Microsoft Windows environment. When a threat actor compromises an account holding either of these privileges, they obtain the ability to bypass standard file system access controls (NTFS DACLs) entirely. This effectively allows the attacker to read from or write to any file on the system, regardless of the permissions explicitly set by the system administrator. 

The most critical and common attack path leveraging these privileges leads to complete system compromise, typically through the extraction of highly sensitive credential files—such as the NTDS.dit active directory database or the local SAM registry hive—or by replacing critical system executables with malicious payloads.

## Theoretical Foundation

In the Windows security model, access to securable objects (files, directories, registry keys, etc.) is strictly governed by Discretionary Access Control Lists (DACLs). However, legitimate backup and restore operations inherently require the ability to traverse directories, copy data, and modify system files regardless of the object owner's explicit permissions. 

To facilitate this, Windows provides specialized privileges:

- **SeBackupPrivilege:** Grants the ability to traverse directories and read any file, bypassing all read-access and traverse-checking restrictions. The user effectively has universal "Read" access to the entire file system for the purpose of backing up data.
- **SeRestorePrivilege:** Grants the ability to write to any file and modify owner/permission settings, bypassing all write-access restrictions. The user effectively has universal "Write/Modify" access to the entire file system for the purpose of restoring data.

When a process requests a handle to a file using the `CreateFile` API and includes the `FILE_FLAG_BACKUP_SEMANTICS` flag, the operating system kernel checks if the calling process's access token holds the enabled backup/restore privileges. If present and enabled, standard DACL security checks are completely bypassed.

## Architecture and ASCII Diagram

```text
+--------------------------------------------------------------------+
|                Windows Access Control Mechanism                    |
|                                                                    |
|  +------------------+                    +----------------------+  |
|  |   User Process   |                    |   Kernel / SYSTEM    |  |
|  | (Low Privilege)  |                    | (High Privilege)     |  |
|  +--------+---------+                    +----------+-----------+  |
|           |                                         ^              |
|           | (1) CreateFile(FILE_FLAG_BACKUP)        |              |
|           v                                         |              |
|  +------------------+                    +----------+-----------+  |
|  | Access Token     |                    | Object Security      |  |
|  | [x] SeBackupPriv |                    | Descriptor (DACL)    |  |
|  +--------+---------+                    +----------+-----------+  |
|           |                                         |              |
|           +-----------------------------------------+              |
|                  (2) Authorization Check                           |
|                      - Token has SeBackupPrivilege                 |
|                      - DACL checks are BYPASSED                    |
|                      - Handle returned with READ access            |
+--------------------------------------------------------------------+
```

## Prerequisites and Environment Setup

To abuse these privileges, the following strict conditions must be met:

1. **Privilege Assignment:** The compromised account must have either `SeBackupPrivilege` or `SeRestorePrivilege` assigned to it by the system configuration (e.g., via Group Policy or Local Security Policy).
2. **Privilege Enablement:** The privileges must be active in the current access token. Some privileges are present in the token but disabled by default. They require programmatic enablement via the `AdjustTokenPrivileges` API before they can be actively used.

You can enumerate the privileges of your current process using the standard built-in utility:

```cmd
C:\> whoami /priv

PRIVILEGES INFORMATION
----------------------

Privilege Name                Description                               State
============================= ========================================= ========
SeBackupPrivilege             Back up files and directories             Disabled
SeRestorePrivilege            Restore files and directories             Disabled
```

## Detailed Exploitation Walkthrough

### Scenario 1: Credential Extraction via SeBackupPrivilege

The paramount objective when holding `SeBackupPrivilege` is extracting credential material. The local Security Account Manager (SAM) and SYSTEM registry hives contain local administrator hashes.

**Step 1: Circumventing File Locks**

Even possessing `SeBackupPrivilege`, you cannot simply use the `copy` command on live registry files located in `C:\Windows\System32\config\` because the OS holds an exclusive lock on them. However, you can utilize the built-in `reg.exe` utility, which natively understands how to interact with the configuration manager to save a copy.

```cmd
# Create a temporary directory for exfiltration
mkdir C:\temp

# Export the SAM hive
reg save HKLM\SAM C:\temp\SAM.save

# Export the SYSTEM hive (required for the boot key to decrypt SAM)
reg save HKLM\SYSTEM C:\temp\SYSTEM.save
```

*Note: If the `reg.exe` tool fails due to specific hardening, custom tools utilizing the Backup APIs directly must be deployed.*

**Step 2: Extracting the Active Directory Database (Domain Controllers)**

If operating on a Domain Controller, the ultimate prize is the `NTDS.dit` file. This file is exclusively locked and `reg.exe` cannot be used. A Volume Shadow Copy must be instantiated.

```cmd
# Create a volume shadow copy of the system drive
vssadmin create shadow /for=C:

# Identify the Shadow Copy Volume Name from the output
# Example: \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1

# Copy the NTDS.dit file from the shadow copy volume
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\NTDS\NTDS.dit C:\temp\NTDS.dit
```

**Step 3: Offline Hash Extraction**

Once the `SAM` and `SYSTEM` files (or the `NTDS.dit`) are successfully exfiltrated to the attacker's infrastructure, tools like Impacket's `secretsdump.py` are used to extract the NTLM hashes.

```bash
# On the attacker machine
impacket-secretsdump -sam SAM.save -system SYSTEM.save LOCAL
```

### Scenario 2: Binary Replacement via SeRestorePrivilege

With `SeRestorePrivilege`, the attacker gains universal write capabilities. This permits the replacement of legitimate system binaries within protected directories (e.g., `System32`) to achieve execution as the SYSTEM user.

**Step 1: Identifying a Target**

Identify a service that executes with SYSTEM privileges and is set to start automatically. The `Print Spooler` service (`spoolsv.exe`) or `Utilman.exe` (Utility Manager) are common targets.

**Step 2: Programmatic Execution and Replacement**

Standard command-line tools like `copy` or `move` do not automatically assert `SeRestorePrivilege` during file operations. Therefore, custom scripts or compiled binaries that invoke the `BackupWrite` API are necessary.

Using a well-known PowerShell script module (e.g., `SeRestoreAbuse.ps1`):

```powershell
# Import the module containing the API wrappers
Import-Module .\SeRestoreAbuse.ps1

# Overwrite the target executable with the malicious payload
Invoke-SeRestoreWrite -Source "C:\temp\malicious_payload.exe" -Destination "C:\Windows\System32\utilman.exe"
```

**Step 3: Triggering Execution**

Once replaced, trigger the execution of the payload. For `utilman.exe`, this involves locking the screen and pressing `Windows Key + U`. The system will execute the malicious payload as `NT AUTHORITY\SYSTEM`.

## Advanced Techniques & Bypasses

1. **Programmatic Privilege Enablement:**
   Since standard command shells do not actively assert these privileges, attackers rely on custom C# or C++ assemblies that explicitly call the Windows API function `AdjustTokenPrivileges`. Tools like `SeBackupPrivilegeCmdLets` or custom C++ loaders are frequently utilized.
2. **Extensible Storage Engine (ESE) API Abuse:**
   Advanced attackers can bypass the need for Volume Shadow Copies entirely when reading locked files like `NTDS.dit`. By leveraging the ESE APIs (esent.dll), they can directly parse and extract data from the live database file, circumventing file system locks stealthily.

## Indicators of Compromise (IoCs) & Detection Engineering

### Log Sources and Telemetry

1. **Windows Security Event Logs:**
   - `Event ID 4672` (Special Privileges Assigned to New Logon): Monitor for accounts receiving high-level privileges unexpectedly upon authentication.
   - `Event ID 4656` / `4663` (Object Access): If aggressive auditing is enabled, monitor for unexpected access to highly sensitive files like `NTDS.dit` or `SAM` from non-standard processes.
   - `Event ID 4688` (Process Creation): Look for suspicious usage of built-in administration tools.

2. **Sysmon (System Monitor):**
   - `Event ID 1` (Process creation): Monitor for commands involving `vssadmin create shadow`, `reg save HKLM\SAM`, or custom PowerShell scripts invoking backup APIs.
   - `Event ID 11` (FileCreate): Monitor for executable files dropped into sensitive directories by non-system processes.

### SIEM Detection Queries

```kql
// KQL Query: Detecting Volume Shadow Copy Creation
SecurityEvent
| where EventID == 4688
| where ProcessName endswith "vssadmin.exe" or ProcessName endswith "wmic.exe" or ProcessName endswith "powershell.exe"
| where CommandLine contains "create shadow" or CommandLine contains "shadowcopy"
| project TimeGenerated, Computer, Account, ProcessName, CommandLine
```

## Mitigation & Remediation

1. **Strict Principle of Least Privilege:**
   Never assign `SeBackupPrivilege` or `SeRestorePrivilege` to standard user accounts. Restrict these privileges strictly to dedicated, heavily monitored service accounts responsible for enterprise backup solutions.
2. **Tiered Administration:**
   Ensure that backup service accounts are treated as Tier 0 assets and are not allowed to log on interactively to lower-tier systems.
3. **Continuous Auditing:**
   Regularly audit User Rights Assignment via Group Policy to ensure these privileges have not been granted maliciously as a persistence mechanism.

## Chaining Opportunities

- **Initial Access Pivot:** Often, these privileges are acquired after compromising a mid-tier application server (like IIS or MSSQL), where service accounts are over-privileged by lazy administrators.
- **Persistence Mechanism:** Attackers may explicitly grant these privileges to a backdoor account to ensure they can modify system binaries or extract fresh credentials across reboots without needing standard local administrator rights.

## Related Notes
- [[26 - Insecure File Folder Permissions]]
- [[31 - Credential Dumping]]
- [[32 - Volume Shadow Copy Theft]]
