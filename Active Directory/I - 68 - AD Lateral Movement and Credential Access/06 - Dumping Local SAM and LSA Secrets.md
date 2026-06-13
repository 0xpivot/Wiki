---
tags: [active-directory, intermediate, lateral-movement, vapt]
difficulty: intermediate
module: "68 - AD Lateral Movement and Credential Access"
topic: "68.06 Dumping Local SAM and LSA Secrets"
---

# 68.06 Dumping Local SAM and LSA Secrets

## Introduction and Overview

The Security Account Manager (SAM) and the Local Security Authority (LSA) Secrets are two of the most critical credential storage mechanisms on a Windows operating system. As an attacker or a red teamer, gaining administrative privileges on a compromised host often leads to dumping these databases. By extracting information from the SAM and LSA Secrets, an attacker can harvest local administrator hashes, cached domain credentials, plaintext passwords stored by specific services, and other sensitive key material. This information forms the backbone of lateral movement operations and local privilege escalation persistence.

This document covers the deep technical mechanics of how Windows stores credentials within the registry, how the LSA protects them, the tools and techniques used to extract them, and how an attacker can leverage this information to pivot within an Active Directory environment. 

## Deep Dive: Security Account Manager (SAM)

The SAM database, stored on disk at `%SystemRoot%\System32\config\SAM`, is a registry file that stores local user accounts and their associated passwords. These passwords are not stored in plaintext; instead, they are hashed. Depending on the configuration and age of the system, you may find LM (LAN Manager) hashes or NT (New Technology) hashes, although modern Windows environments almost exclusively use NT hashes (NTLM).

The SAM database is mounted in the Windows Registry at `HKEY_LOCAL_MACHINE\SAM`. By default, only the `SYSTEM` account has permission to read the contents of this registry hive. Even an Administrator account must impersonate `SYSTEM` or modify the registry permissions to extract its contents while the operating system is running.

### How the SAM Protects Hashes

To prevent offline extraction of hashes, Windows uses a layered encryption approach:
1. **Boot Key (Syskey):** Starting with Windows NT 4.0 SP3, Microsoft introduced Syskey. The boot key encrypts the password hashes stored in the SAM database. The boot key itself is stored in the `SYSTEM` registry hive (`%SystemRoot%\System32\config\SYSTEM`).
2. **SAM Database Keys:** The SAM database contains specific keys that are encrypted using the boot key. 
3. **User Account Hashes:** The user's NT hash is encrypted using the keys derived from the SAM database keys.

Therefore, to successfully decrypt and dump the hashes offline, you need both the SAM database file and the SYSTEM registry hive.

## Deep Dive: Local Security Authority (LSA) Secrets

LSA Secrets is a secure storage area used by the Local Security Authority Subsystem Service (LSASS) in Windows. It stores highly sensitive data required by the operating system and various services. The data stored in LSA Secrets can be extremely lucrative for an attacker.

The LSA Secrets are stored in the registry under `HKEY_LOCAL_MACHINE\SECURITY\Policy\Secrets`. Like the SAM hive, this key is only accessible by the `SYSTEM` account.

### What is stored in LSA Secrets?

- **Service Account Passwords:** Passwords for Windows services that are configured to run as a specific user account (e.g., a SQL server service account or an IIS application pool identity). These are often stored in plaintext or reversibly encrypted.
- **Scheduled Task Credentials:** Passwords for accounts used to execute scheduled tasks.
- **Autologon Passwords:** If a system is configured to log in automatically, the plaintext password is stored here (`DefaultPassword`).
- **Computer Account Passwords:** The password for the local computer account (e.g., `MACHINE$`) used to authenticate the computer to the Active Directory domain. This is rotated every 30 days by default.
- **Cached Domain Credentials:** While technically stored in the `SECURITY\Cache` registry key, they are managed by the LSA. These are MSCash/DCC2 hashes.
- **DPAPI Master Keys:** Data Protection API master keys for the `SYSTEM` account.

Like the SAM database, LSA Secrets are encrypted using the Boot Key (Syskey) stored in the SYSTEM registry hive.

## ASCII Diagram: The SAM and LSA Extraction Architecture

```text
+-----------------------------------------------------------------------------------+
|                         Compromised Windows Endpoint                              |
|                                                                                   |
|  +--------------------+                                                           |
|  | Administrator/     | ----[Impersonates]----> +--------------------+            |
|  | High Priv User     |                         | NT AUTHORITY\SYSTEM|            |
|  +--------------------+                         +--------------------+            |
|          |                                                |                       |
|          | (Needs SYSTEM access to read hives)            | (Has Read Access)     |
|          v                                                v                       |
|  +-----------------------------------------------------------------------------+  |
|  |                                Windows Registry                             |  |
|  |                                                                             |  |
|  |  +------------------+    +------------------+    +------------------+       |  |
|  |  | HKLM\SYSTEM      |    | HKLM\SAM         |    | HKLM\SECURITY    |       |  |
|  |  | (Contains Boot   |    | (Encrypted local |    | (Encrypted LSA   |       |  |
|  |  |  Key / Syskey)   |    |  hashes)         |    |  Secrets)        |       |  |
|  |  +------------------+    +------------------+    +------------------+       |  |
|  |          |                        |                       |                 |  |
|  +----------|------------------------|-----------------------|-----------------+  |
|             |                        |                       |                    |
+-------------|------------------------|-----------------------|--------------------+
              |                        |                       |
              v                        v                       v
      [Extract Boot Key] ----> [Decrypt SAM Hashes]    [Decrypt LSA Secrets]
                                       |                       |
                                       v                       v
                           +----------------------+  +-------------------------+
                           |  Local NT Hashes     |  | Plaintext Passwords,    |
                           |  (Administrator, etc)|  | Service Accounts,       |
                           |                      |  | Machine Account Pass    |
                           +----------------------+  +-------------------------+
                                       |                       |
                                       +-----------+-----------+
                                                   |
                                                   v
                                   [Lateral Movement & Escalation]
```

## Methodology: Techniques for Extraction

There are two primary methodologies for extracting the SAM and LSA Secrets: **Offline Extraction** and **Online Extraction** (using API calls or memory reading).

### 1. Offline Extraction (Registry Hive Dumping)

This is one of the most operationally safe methods because it relies on native Windows commands and administrative access, bypassing many EDR/AV mechanisms that monitor memory access to LSASS.

#### Step-by-step Execution

First, the attacker uses the `reg.exe` utility to save copies of the `SAM`, `SYSTEM`, and `SECURITY` hives to disk. Because `reg.exe` interacts with the registry API, it can extract the data even though the files on disk (`C:\Windows\System32\config\SAM`) are locked by the operating system.

```cmd
C:\> reg save HKLM\SAM C:\temp\sam.save
C:\> reg save HKLM\SYSTEM C:\temp\system.save
C:\> reg save HKLM\SECURITY C:\temp\security.save
```

Once the files are saved, the attacker exfiltrates these files to their local attack machine.

#### Parsing the Hives Offline

Tools like `secretsdump.py` from Impacket or `Mimikatz` (running locally on the attacker box) can be used to parse these files and decrypt the secrets.

Using Impacket:
```bash
# Extracting SAM hashes and LSA secrets locally
impacket-secretsdump -sam sam.save -system system.save -security security.save LOCAL
```

Using Mimikatz offline:
```text
mimikatz # lsadump::sam /sam:sam.save /system:system.save
mimikatz # lsadump::secrets /system:system.save /security:security.save
```

### 2. Online Extraction (Memory / API Interaction)

If the attacker wants to extract the secrets directly on the target machine without saving files to disk (which might be caught by File Integrity Monitoring or AV scanning the `.save` files), they can inject into memory or use specific APIs.

#### Mimikatz

Mimikatz requires elevating to `SYSTEM` and obtaining debug privileges (`SeDebugPrivilege`).

```text
mimikatz # privilege::debug
Privilege '20' OK

mimikatz # token::elevate
Token Id  : 0
User name :
SID name  : NT AUTHORITY\SYSTEM

mimikatz # lsadump::sam
[... outputs SAM hashes ...]

mimikatz # lsadump::secrets
[... outputs LSA secrets ...]
```

#### CrackMapExec / NetExec

These tools automate the process of connecting to a remote machine, executing a payload (often using `secretsdump.py` logic), and returning the results, all without dropping files.

```bash
# Dumping SAM remotely
nxc smb 192.168.1.100 -u Administrator -p 'Password123' --sam

# Dumping LSA remotely
nxc smb 192.168.1.100 -u Administrator -p 'Password123' --lsa
```

### 3. Volume Shadow Copies (VSS)

Another stealthy method to extract the locked registry hive files is by creating a Volume Shadow Copy of the `C:\` drive. The files within the shadow copy are not locked by the operating system.

```cmd
vssadmin create shadow /for=C:
```
After creating the shadow copy, the attacker can copy the raw files:
```cmd
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SAM C:\temp\sam.hive
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SYSTEM C:\temp\system.hive
copy \\?\GLOBALROOT\Device\HarddiskVolumeShadowCopy1\Windows\System32\config\SECURITY C:\temp\security.hive
```

## Defensive Considerations and Mitigations

Defending against SAM and LSA dumping relies on a defense-in-depth strategy:

1. **Local Administrator Password Solution (LAPS):** Implement Microsoft LAPS (or Windows LAPS) to randomize and rotate the local administrator passwords across the domain. If an attacker dumps the SAM on one machine, they cannot use that hash to authenticate to other machines (preventing lateral movement via lateral account sharing).
2. **Credential Guard:** Windows Defender Credential Guard uses virtualization-based security to isolate secrets so that only privileged system software can access them. This makes it significantly harder to dump LSA secrets.
3. **Restricting Debug Privileges:** Ensure that only explicitly required accounts have `SeDebugPrivilege`. By default, local administrators have it, but it can be removed via Group Policy.
4. **EDR and Telemetry:** Monitor for anomalous registry access, particularly `reg save` commands targeting the SAM, SYSTEM, or SECURITY hives. Alert on the execution of known dumping tools or unexpected API calls into LSASS.


## Real-World Attack Scenario
In a recent red team engagement evaluating a retail chain's point-of-sale (POS) network, the attackers managed to exploit a vulnerable web application running on a legacy Windows server in the DMZ. After escalating privileges to `NT AUTHORITY\SYSTEM` using a well-known kernel exploit (PrintNightmare), the attackers found themselves isolated; the server could not reach the internal Active Directory domain controllers due to strict firewall rules.

Unable to perform traditional domain enumeration or pass-the-hash attacks across the network, the attackers pivoted to extracting local credentials to see if password reuse could facilitate lateral movement. Their target was the local Security Account Manager (SAM) database and the LSA Secrets, which often store service account passwords, cached domain hashes, and VPN configurations.

The local EDR actively blocked tools like Mimikatz or heavily obfuscated PowerShell scripts attempting to read the SAM database directly. Therefore, the attacker opted to use the built-in Windows Volume Shadow Copy (VSS) service and standard registry commands to create offline backups of the necessary registry hives.

```cmd
C:\> reg save HKLM\SYSTEM C:\Temp\system.save
The operation completed successfully.

C:\> reg save HKLM\SAM C:\Temp\sam.save
The operation completed successfully.

C:\> reg save HKLM\SECURITY C:\Temp\security.save
The operation completed successfully.
```

These commands executed cleanly, as backing up registry hives is a common administrative task that EDRs rarely block outright. The attacker then compressed the three `.save` files into a single ZIP archive and exfiltrated them via an outbound HTTPS connection to their command-and-control server.

```bash
# On the attacker's offline Linux machine
secretsdump.py -sam sam.save -system system.save -security security.save LOCAL
```

Using Impacket's `secretsdump.py` on their local machine, the attacker extracted the NTLM hashes of all local accounts. Crucially, extracting the LSA Secrets (from the `SECURITY` hive) revealed a plaintext password for a legacy service account: `svc_backup : B@ckupR0utine2021!`. 

Testing this newly discovered password against the external VPN portal, the attackers found that the `svc_backup` account was still active in Active Directory and lacked Multi-Factor Authentication (MFA). By simply connecting to the VPN using the extracted plaintext password, the attackers bypassed the heavily fortified DMZ firewall, directly dropping into the internal corporate network and bypassing months of perimeter defense configurations.

## Chaining Opportunities

- **[[07 - Pass-the-Hash PtH Mechanics and Execution]]**: Once you have extracted the NT hash from the SAM database, you can use it to authenticate to other systems without needing to crack the hash into plaintext.
- **[[08 - Over-Pass-the-Hash Pass-the-Key]]**: If the LSA secrets yield the machine account password hash (or you crack an administrator password), you can forge Kerberos tickets.
- **[[11 - LSASS Memory Dumping Techniques]]**: While SAM and LSA secrets are stored on disk/registry, dumping the LSASS process memory can yield cleartext passwords of logged-on users.

## Related Notes

- [[01 - Active Directory Lateral Movement Overview]]
- [[02 - Local Administrator Password Solution LAPS]]
- [[05 - Windows Token Impersonation]]
- [[12 - Credential Guard Bypass Strategies]]
