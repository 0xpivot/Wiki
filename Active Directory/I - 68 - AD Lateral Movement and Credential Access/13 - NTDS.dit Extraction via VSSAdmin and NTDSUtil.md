---
tags: [active-directory, intermediate, lateral-movement, vapt]
difficulty: intermediate
module: "68 - AD Lateral Movement and Credential Access"
topic: "68.13 NTDS.dit Extraction"
---
# 13 - NTDS.dit Extraction via VSSAdmin and NTDSUtil

## 1. Introduction to NTDS.dit and Active Directory Architecture

The `NTDS.dit` (New Technology Directory Services Directory Information Tree) file is the absolute core of any Active Directory domain. It is the proprietary database that stores all Active Directory data. This includes information about user objects, groups, computers, Group Policy object links, and most critically, the password hashes (NTLM hashes and Kerberos keys) for every single user and machine account in the entire domain.

By default, this database file is located on Domain Controllers at `C:\Windows\NTDS\ntds.dit`. 

Because Active Directory is constantly running and servicing authentication requests, the `NTDS.dit` file is strictly locked by the Local Security Authority Subsystem Service (`lsass.exe`). Therefore, you cannot simply copy the file using standard Windows commands (like `copy` or `xcopy`) while the system is online. An attacker must bypass this file lock to successfully extract the database for offline analysis.

## 2. Core Extraction Methodologies and Prerequisites

To circumvent the file lock, attackers utilize native Windows administrative tools designed for backup, recovery, and replication. This methodology is heavily favored because it relies on "Living off the Land" (LotL) binaries—tools that are signed by Microsoft and already present on the system. The two most prominent tools for this operation are `vssadmin.exe` and `ntdsutil.exe`. 

**Prerequisites:**
Both methods absolutely require the attacker to possess **Domain Admin** or **Enterprise Admin** privileges, or at the bare minimum, local Administrator rights directly on the target Domain Controller. You cannot execute these operations from a standard user context or from a workstation.

### 2.1 The Volume Shadow Copy Service (VSS)

The Volume Shadow Copy Service (VSS) is a Windows framework that coordinates the actions required to create a consistent shadow copy (also known as a snapshot or a point-in-time copy) of the data that is to be backed up. By instructing VSS to create a shadow copy of the `C:` drive, the attacker creates a readable, point-in-time snapshot of the disk where `NTDS.dit` is *not* locked by the operating system, allowing a direct copy operation.

### 2.2 The Dependency: SYSTEM Registry Hive

Extracting the `NTDS.dit` file alone is entirely insufficient for an attacker. The sensitive data within `NTDS.dit` (the hashes) is encrypted using a key derived from the BootKey (also known as the SYSKEY). The BootKey is mathematically generated and securely stored inside the `SYSTEM` registry hive. Therefore, to decrypt the contents of `NTDS.dit` later, the attacker MUST extract both the `NTDS.dit` file AND the `SYSTEM` hive simultaneously.

## 3. Extraction via VSSAdmin

`vssadmin.exe` is the native command-line tool that manages the Volume Shadow Copy Service. 

### Step-by-Step Execution:

**Step 1: Create a Volume Shadow Copy**
The attacker issues a command to snapshot the drive containing the NTDS folder.
```cmd
vssadmin create shadow /for=C:
```
*Output snippet:*
`Successfully created shadow copy for 'C:\' Shadow Copy Volume Name: \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1`

**Step 2: Copy NTDS.dit from the Shadow Copy**
The attacker uses the Shadow Copy Volume Name (provided in the output) to access the snapshot and copy the database to a temporary directory.
```cmd
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\NTDS\ntds.dit C:\Temp\ntds.dit
```

**Step 3: Copy the SYSTEM Hive from the Shadow Copy**
Using the same volume name, the registry hive is copied.
```cmd
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SYSTEM C:\Temp\SYSTEM
```

**Step 4: Clean Up (OPSEC)**
To hide their tracks and free up disk space, the attacker deletes the shadow copy they just created.
```cmd
vssadmin delete shadows /shadow={Shadow-Copy-ID} /quiet
# Or delete all shadows generically:
vssadmin delete shadows /for=C: /quiet
```

## 4. Extraction via NTDSUtil

`ntdsutil.exe` is a command-line tool that provides management facilities for AD DS. It includes an `ifm` (Install From Media) media creation feature. This feature was designed to help administrators create deployment media for spinning up new branch Domain Controllers without needing to replicate the entire database over a slow WAN link. 

This feature automatically creates a VSS snapshot, extracts `NTDS.dit`, the `SYSTEM` registry hive, and the `SECURITY` registry hive, and packages them neatly into a designated folder.

### Step-by-Step Execution:

**Step 1: Execute NTDSUtil IFM creation**
An attacker can run this entirely non-interactively using command-line arguments:
```cmd
ntdsutil "ac i ntds" "ifm" "create full c:\Temp\ntds_dump" q q
```

*Explanation of parameters:*
- `ac i ntds`: Activate Instance NTDS.
- `ifm`: Enter the Install From Media context.
- `create full c:\Temp\ntds_dump`: Create a full backup in the specified directory.
- `q q`: Quit IFM context and quit NTDSUtil entirely.

**Step 2: Retrieve the Files**
Once complete, the directory `C:\Temp\ntds_dump` will contain two subdirectories:
- `Active Directory`: Contains `ntds.dit`
- `registry`: Contains the `SYSTEM` and `SECURITY` hives.

This method is frequently preferred by red teams because it requires a single command, handles the registry hives automatically, and naturally cleans up the shadow copy it creates, minimizing administrative overhead.

## 5. Visualizing the Attack Architecture

```text
+-----------------------------------------------------------------------+
|                    NTDS.dit Extraction Architecture                   |
+-----------------------------------------------------------------------+

[Attacker (Domain Admin on DC)]
         |
         | 1. Execute ntdsutil OR vssadmin
         v
+-----------------------+      2. Triggers     +------------------------+
|   VSS Service         | -------------------> | Volume Shadow Copy     |
|   (vssvc.exe)         |                      | Snapshot of C:\ Drive  |
+-----------------------+                      +------------------------+
                                                          |
         +------------------------------------------------+
         | 3. Copy locked files from Snapshot
         v
+-----------------------+      4. Exfiltrate   +------------------------+
| Extracted Files:      |                      | Attacker's Local       |
| - ntds.dit            | ===================> | Cracking Rig           |
| - SYSTEM hive         |         (SMB, HTTP,  +------------------------+
+-----------------------+          C2 Channel)             |
                                                           v
                                               +------------------------+
                                               | 5. Parse and Decrypt   |
                                               |    (SecretsDump)       |
                                               +------------------------+
```

## 6. Advanced OPSEC and Evasion Techniques

Extracting `NTDS.dit` is a massive red flag. Modern EDR solutions actively monitor for arguments passed to `ntdsutil.exe` and `vssadmin.exe`.

**Evasion Techniques:**
1. **WMI and PowerShell:** Invoking shadow copies via WMI (`Win32_ShadowCopy`) rather than the `vssadmin.exe` binary to bypass process creation monitoring on `vssadmin.exe`.
   ```powershell
   (gwmi -list win32_shadowcopy).Create('C:\','ClientAccessible')
   ```
2. **Esentutl:** Sometimes attackers use the native `esentutl.exe` tool (used for Exchange/AD database maintenance) to copy the file.
3. **NinjaCopy:** Using custom PowerShell scripts (like Invoke-NinjaCopy) to read the raw NTFS disk volumes and bypass file locking entirely without invoking VSS at all.
4. **VSSown.vbs:** A malicious VBScript that performs shadow copy operations via COM objects, completely avoiding command-line logging.

## 7. Defensive Considerations and Detection

### 7.1 Detection Strategies

- **Process Creation Logging (Event ID 4688):**
  Monitor for command lines containing:
  - `ntdsutil*ac i ntds*ifm*create full*`
  - `vssadmin*create shadow*`
  - `vssadmin*delete shadows*`
- **File System Monitoring:** Monitor the creation of large `.dit` files outside of the `C:\Windows\NTDS\` directory.
- **Sysmon Event ID 11 (File Create):** Alert on the creation of `ntds.dit` in temporary folders (e.g., `C:\Temp\`, `C:\Users\*\AppData\Local\Temp\`).
- **Network Telemetry:** Alert on massive data transfers originating from Domain Controllers to non-administrative workstations via SMB (exfiltration phase).

### 7.2 Mitigation Strategies

- **Least Privilege:** Ensure only strictly necessary accounts have Domain Admin privileges.
- **Tiered Administration:** Implement a Tier-0 administrative model. Domain admins should only log onto Domain Controllers, making it exponentially harder for an attacker to compromise a DA credential on a lower-tier workstation to launch this attack.
- **AppLocker / WDAC:** Restrict the execution of `vssadmin.exe` and `ntdsutil.exe` to specific administrative scripts or block them entirely if not used in standard operational procedures.

## Real-World Attack Scenario

During an assumed breach exercise against an energy sector client, the red team escalated their privileges to Domain Admin using an unpatched Active Directory Certificate Services (AD CS) misconfiguration (ESC1). To achieve their primary objective of full network persistence and demonstrating the risk of a total domain compromise, the team needed to extract the KRBTGT hash and the NTLM hashes of all enterprise users.

Since deploying specialized offensive tools directly onto a Domain Controller would likely trigger the client's aggressive EDR alerts, the red team opted for a "Living off the Land" approach. First, the attacker established a remote WinRM session to the primary Domain Controller from a compromised jump server:
```powershell
Enter-PSSession -ComputerName DC01.corp.local
```

Once connected, instead of manually creating shadow copies with `vssadmin`—which was heavily monitored—the attacker executed a single `ntdsutil` command to leverage the Install From Media (IFM) feature. This legitimate administrative mechanism securely snaps the database and registry hives into a specified directory:
```cmd
ntdsutil "ac i ntds" "ifm" "create full C:\PerfLogs\AD_Backup" q q
```

The EDR logged the process execution, but because `ntdsutil.exe` was running from an authenticated Domain Admin context performing a standard database action, it was classified as legitimate administrative behavior. The command successfully generated a VSS snapshot, exported `ntds.dit` to `C:\PerfLogs\AD_Backup\Active Directory\`, and dumped the `SYSTEM` and `SECURITY` hives to `C:\PerfLogs\AD_Backup\registry\`.

To exfiltrate the files, the attacker compressed the directory using native PowerShell:
```powershell
Compress-Archive -Path C:\PerfLogs\AD_Backup -DestinationPath C:\PerfLogs\AD_Backup.zip
```
The ZIP file was then downloaded over the existing WinRM session. Once the files were securely on the attacker's offline cracking rig, they used `secretsdump.py` to parse the database. They successfully extracted the KRBTGT hash to forge a Golden Ticket, ensuring long-term stealthy persistence, and initiated an offline dictionary attack against the extracted NTLM hashes to analyze the organization's password complexity compliance.

## 8. Chaining Opportunities

- **[[14 - Parsing NTDS.dit Secretsdump]]:** The immediate next step after extracting `NTDS.dit` is parsing the file offline to extract the NTLM hashes.
- **[[08 - Pass the Hash]]:** Once hashes are extracted, they can be used for Pass-the-Hash attacks across the enterprise.
- **[[18 - Golden Ticket Attacks]]:** Extracting `NTDS.dit` provides the KRBTGT hash, which is strictly required to forge Golden Tickets and establish domain persistence.
- **[[22 - DCSync Attacks]]:** An alternative to file extraction is DCSync, which pulls the hashes over the network using replication protocols.

## 9. Related Notes

- [[05 - Windows Post-Exploitation Enumeration]]
- [[20 - Kerberos Attacks Overview]]
- [[07 - DPAPI Extraction and Abuse]]
