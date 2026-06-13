---
tags: [active-directory, azure, hybrid, exchange, vapt]
difficulty: expert
module: "65 - Hybrid Identity, Entra ID, and Exchange Attacks"
topic: "65.15 DPAPI and DPAPI-NG Master Key Extraction"
---
# DPAPI and DPAPI-NG Master Key Extraction

## 1. Introduction to Data Protection API (DPAPI)
The Data Protection API (DPAPI) is a deeply embedded cryptographic subsystem built into the Windows operating system. It exposes a set of programmatic interfaces (primarily `CryptProtectData` and `CryptUnprotectData`) that permit applications to seamlessly encrypt and decrypt highly sensitive data. The cornerstone of DPAPI is that the symmetric encryption key is implicitly derived from the currently logged-on user's credentials, eliminating the need for applications to manage their own cryptographic keys or prompt the user for additional passwords.

**The Critical Scope of DPAPI Protection:**
DPAPI is the silent guardian of some of the most sensitive data on a Windows endpoint. It protects:
*   Web browser password vaults and session cookies (Google Chrome, Microsoft Edge, Chromium-based browsers).
*   Encrypting File System (EFS) private keys.
*   Wireless network (Wi-Fi) passwords.
*   RDP saved credentials and Connection Manager profiles.
*   Outlook and Exchange authentication tokens.
*   Azure AD / Entra ID Primary Refresh Tokens (PRTs), the cornerstone of modern cloud identity.

Consequently, the extraction of DPAPI Master Keys is an incredibly lucrative post-exploitation objective for advanced threat actors aiming to achieve massive privilege escalation, lateral movement to cloud environments, or catastrophic data exfiltration.

## 2. Core DPAPI Architecture and The Master Key Concept
When an application invokes DPAPI to encrypt data, the data is not directly encrypted with the user's password. Instead, it is encrypted using a unique, randomly generated symmetric key. This symmetric key is, in turn, cryptographically protected by a **DPAPI Master Key**.

*   **Storage Location:** Master Keys are persisted locally on the file system within the user's profile: `%APPDATA%\\Microsoft\\Protect\\{User_SID}\\`.
*   **Local Protection:** The Master Key file itself is encrypted. The encryption key is derived from the user's plaintext password (specifically, utilizing a SHA-1 hash of the password combined with a salt).
*   **The Domain Backup Mechanism:** In an enterprise Active Directory environment, a critical usability issue arises: if an administrator resets a user's password, or if the user changes it from a different machine, the local Master Key on their workstation can no longer be decrypted, resulting in catastrophic data loss. 
To solve this, AD implements a backup mechanism. When a Master Key is created, a copy is encrypted using the public key of the Domain Controller. This is known as the **DPAPI Domain Backup Key**.

### 2.1 Attack Architecture Diagram (Local vs. Domain Exploitation)
```text
  +-----------------------+      (1) Local Extraction (Requires User Password/Hash)
  |   Encrypted Payload   | <-------------------------------------------------------+
  |  (e.g., Chrome DB)    |                                                         |
  +-----------------------+                                                         |
            |                                                                       |
            V                                                                       |
  [ DPAPI Master Key ] <--- Encrypted by ---> [ User's Plaintext Password / Hash ]  |
  (Stored on Local Disk)                                                            |
            ^                                                                       |
            |                    (2) Domain Extraction (Requires Domain Admin)      |
            +-----------------------------------------------------------------------+
  [ DPAPI Backup Key ] <--- Encrypted by ---> [ Domain Controller Private Key ]
  (Stored in AD / LSA)                        (The Ultimate Cryptographic Target)
```

## 3. Offensive Strategies: Extracting the Keys
Attackers typically pursue two primary avenues to decrypt DPAPI-protected data, depending on their level of access: Local Extraction (User-level compromise) and Domain Extraction (Enterprise-level compromise).

### 3.1 Local Extraction (User Level Compromise)
If an attacker compromises a user's workstation and establishes a session acting as that user, they can interact with the DPAPI API directly. Because Windows handles the decryption transparently within the context of the logged-on user, the attacker can leverage tools to request decryption.

**Memory Extraction Using Mimikatz:**
If the victim user is currently logged on (an active interactive session), the decrypted Master Key resides temporarily in LSASS memory for performance reasons. An attacker with local administrator or SYSTEM privileges can extract it directly from memory without ever needing to crack or know the user's plaintext password.
```text
mimikatz # privilege::debug
mimikatz # sekurlsa::dpapi
```
This command dumps all currently decrypted Master Keys from memory.

**Offline Decryption Techniques:**
If the attacker exfiltrates the encrypted Master Key file from the disk, they must possess the user's plaintext password, NTLM hash, or SHA1 hash to decrypt it offline. This is heavily utilized in forensic analysis or offline cracking scenarios.
```text
# Decrypting an offline Master Key file using a known password via Mimikatz
mimikatz # dpapi::masterkey /in:"C:\\Users\\victim\\AppData\\Roaming\\Microsoft\\Protect\\{SID}\\key_file" /sid:{SID} /password:Winter2024!
```

### 3.2 Domain Extraction (The Golden Key Scenario)
If an attacker successfully escalates privileges to Domain Admin or equivalent Tier-0 status, their primary cryptographic objective is to extract the **DPAPI Domain Backup Key**.
This represents the holy grail of DPAPI exploitation. Possessing the Domain Backup Key allows the attacker to unilaterally decrypt *any* user's Master Key across the entire Active Directory domain, completely bypassing the need to know any user's individual password or hash.

**Extracting the Backup Key:**
The Backup Key is stored securely as an LSA secret on Domain Controllers.
*Executing Mimikatz on a compromised Domain Controller:*
```text
mimikatz # lsadump::backupkeys /system:dc01.corp.local /export
```
This operation exports the Domain Backup Key as a `.pvk` (Private Key) file to the disk.

**Weaponizing the Backup Key:**
Once the `.pvk` file is obtained, the attacker can silently dump a user's profile from any workstation or file share in the enterprise, extract the encrypted Master Key, and use the stolen `.pvk` to decrypt it offline.
```text
# Decrypting a user's Master Key using the stolen Domain Backup Key
mimikatz # dpapi::masterkey /in:"path_to_master_key" /pvk:ntds_guid.pvk
```
With the decrypted Master Key in hand, the attacker has unfettered access to decrypt the user's Entra ID PRTs, Chrome passwords, and all other DPAPI-protected material.

## 4. DPAPI-NG (Cryptography Next Generation DPAPI)
DPAPI-NG represents the modern, heavily upgraded iteration of the API, introduced in Windows 8 and Windows Server 2012. 
Crucially, DPAPI-NG shifts the cryptographic paradigm. Instead of relying strictly on user passwords for encryption, DPAPI-NG relies on Active Directory security descriptors (ACLs).

**The Operational Mechanics:**
Data is encrypted against a defined "Protection Descriptor Rule". For example, a rule might state: "Permit decryption only if the requesting user is a member of the group `SID:S-1-5-21-...-512` (Domain Admins)".
The actual encryption and decryption keys are managed centrally by the Key Distribution Service (KDS) running on Domain Controllers.

**Modern Use Cases:**
*   **Windows LAPS:** The modern implementation of LAPS heavily relies on DPAPI-NG to securely encrypt local administrator passwords stored within AD.
*   **gMSA Infrastructure:** The KDS infrastructure is the foundational cryptography layer for both DPAPI-NG and Group Managed Service Accounts.

### 4.1 Attacking DPAPI-NG Infrastructure
To decrypt DPAPI-NG protected data, an attacker cannot simply extract a static Master Key from a user's profile. They must operate within the context of a user or computer account that satisfies the specific Protection Descriptor Rule.

If the rule authorizes the "Helpdesk" group to decrypt the data, the attacker must first compromise a Helpdesk user account and then request the decryption material from the KDS on the DC.

**The Tier-0 Offline Bypass:**
If an attacker acts as a Domain Admin, they can dump the KDS Root Keys directly from Active Directory.
```powershell
# Exporting KDS Root Keys using the DSInternals PowerShell module
Get-ADDBKdsRootKey -DistinguishedName "CN=Master Root Keys,CN=Group Key Distribution Service,CN=Services,CN=Configuration,DC=corp,DC=local"
```
Possessing the KDS Root Key empowers the attacker to calculate the DPAPI-NG decryption keys entirely offline. This bypasses all AD ACL restrictions, network boundaries, and auditing mechanisms, allowing for the silent decryption of all Windows LAPS passwords globally.

## 5. Defense, Mitigation, and Detective Controls
### 5.1 Protecting the Backup Key Architecture
*   **Rigorous Tier-0 Isolation:** The DPAPI Domain Backup Key and KDS Root Keys reside exclusively on Domain Controllers. Absolute protection of Domain Controllers and adherence to the AD Tier Model is the only true defense. Once Tier-0 falls, all DPAPI data across the enterprise is considered compromised.
*   **Implement Credential Guard:** Mandate Windows Defender Credential Guard across all compatible workstations. Credential Guard utilizes Virtualization-Based Security (VBS) to isolate the LSASS process, making it exponentially more difficult for attackers to execute `sekurlsa::dpapi` and extract Master Keys from active memory.

### 5.2 Browser Security and Token Hardening
*   **Enforce Browser Isolation:** Educate users and employ policies to prevent the storage of critical enterprise passwords in local browsers. Mandate the use of enterprise-managed password managers that establish their own robust encryption boundaries separate from DPAPI.
*   **Device Bound Tokens (TPM):** For protecting Azure AD / Entra ID PRTs, ensure all devices are hybrid-joined and equipped with TPM 2.0. Even if an attacker extracts the DPAPI keys, modern PRTs are cryptographically bound to the physical TPM hardware and cannot be replayed or utilized on an attacker's infrastructure.

### 5.3 Advanced Threat Detection
*   **Monitoring LSA Secrets Extraction:** Aggressively monitor for any processes attempting to access LSA secrets remotely or locally on Domain Controllers. Advanced tools dumping the Backup Key invariably trigger high-severity alerts in platforms like Microsoft Defender for Identity (MDI), often labeled as "Suspected DPAPI Backup Key Extraction".
*   **Analyzing Suspicious RPC Traffic:** Tools like Impacket's `dpapi.py` generate distinct, recognizable RPC calls over the SMB protocol when attempting remote key extraction. Network detection logic should be tuned to identify these anomalous RPC patterns targeting DCs.

## 6. Anatomy of the Master Key Blob
The DPAPI Master key on disk has a header format that specifies which hashing algorithm (SHA1, SHA512) and symmetric algorithm (3DES, AES) are used for its own encryption. Mimikatz and specialized parsers like DonPAPI read this header to understand how to derive the correct decryption routine from the user's password.

## 7. Chaining Opportunities
*   [[22 - Microsoft 365 Token Theft]] - The extraction of DPAPI keys is the absolute prerequisite for stealing and decrypting Entra ID Primary Refresh Tokens (PRTs) from a compromised workstation, facilitating a pivot to the cloud.
*   [[12 - Bypassing LAPS Local Admin Password Solution]] - Modern Windows LAPS relies entirely on DPAPI-NG. Dumping the KDS Root Keys defeats Windows LAPS encryption globally, granting local admin access everywhere.
*   [[21 - Pass the Cookie and Session Hijacking]] - Extracting DPAPI keys enables the offline decryption of Chrome/Edge SQLite databases, yielding active session cookies for immediate hijacking of web applications.

## 8. Related Notes
*   [[06 - Credential Dumping Techniques]]
*   [[13 - Extracting gMSA Group Managed Service Accounts]]
*   [[16 - Windows Cryptography Architecture CNG]]
*   [[24 - Active Directory Access Control Lists ACLs]]

## Real-World Attack Scenario
## Real-World Attack Scenario: DPAPI Master Key Extraction

**1. Context and Environment:**
The attacker has compromised the laptop of a senior software engineer at a tech startup. The laptop is joined to Entra ID (Azure AD), and the user heavily relies on Google Chrome to store passwords for various cloud infrastructure portals (AWS, Azure, internal DevOps tools). The attacker has established a C2 beacon running with the engineer's local user context but wants to extract the saved Chrome passwords to pivot to the cloud.

**2. Attacker Thought Process:**
"Chrome encrypts its password database using Windows DPAPI, specifically tied to the user's login credentials. I can download the SQLite database file, but it's useless without the decryption key. Since I'm running in the context of the active user session, I can interact with the DPAPI subsystem. I don't need the user's plaintext password; I can use Mimikatz to extract the decrypted Master Key directly from LSASS memory, or I can use specialized tools that interact with the DPAPI APIs locally to decrypt the blobs on the fly."

**3. Reconnaissance and Enumeration:**
The attacker navigates to the user's AppData directory to locate the Chrome `Login Data` database and the `Local State` file, which contains the DPAPI-encrypted key used for the SQLite database.
```bash
# Locating the target files
cd "C:\Users\s.engineer\AppData\Local\Google\Chrome\User Data\Default\"
dir "Login Data"
```
They also verify that the `mimikatz` module can be loaded into memory without triggering the local AV/EDR solution by utilizing a heavily obfuscated reflective DLL injection technique via their C2 framework.

**4. Exploitation and Execution:**
Since the user is actively logged in, the DPAPI Master Key is currently decrypted and cached in LSASS memory. The attacker elevates to local SYSTEM (via a local privilege escalation exploit) and uses Mimikatz to extract the Master Key from memory.
```text
# Inside the C2 console
beacon> elevate system
beacon> mimikatz privilege::debug
beacon> mimikatz sekurlsa::dpapi
```
Mimikatz successfully outputs the decrypted Master Key (a long hex string). The attacker downloads the `Login Data` and `Local State` files to their attack infrastructure. Offline, they use a Python script (`mimikatz` offline or a custom script) to decrypt the `Local State` key using the extracted Master Key, and then decrypt the SQLite database.
```bash
# Offline decryption
python3 chrome_decrypt.py --master-key "eb41...[REDACTED]...9f" --local-state "Local State" --login-data "Login Data"
```

**5. Post-Exploitation and Outcome:**
The python script successfully decrypts the Chrome password database, outputting a cleartext list of over 150 credentials. Among these are the engineer's AWS IAM access keys and the credentials for the corporate password manager vault. The attacker immediately uses the AWS keys to access the cloud environment, bypassing the corporate VPN and AD entirely, leading to a massive data breach of the company's production databases.

