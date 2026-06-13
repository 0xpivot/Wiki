---
tags: [active-directory, azure, hybrid, exchange, vapt]
difficulty: expert
module: "65 - Hybrid Identity, Entra ID, and Exchange Attacks"
topic: "65.13 Extracting gMSA"
---
# Extracting gMSA (Group Managed Service Accounts)

## 1. Introduction to gMSAs
Group Managed Service Accounts (gMSAs) represent a highly secure, automated identity management paradigm introduced in Windows Server 2012. They are engineered to provide authenticated identity for services—such as IIS application pools, SQL Server instances, and Microsoft Exchange services—running across a farm of servers, entirely eliminating the need for human administrators to manually configure, store, or rotate service account passwords.

**Core Advantages of gMSA:**
*   **Automated Cryptography:** Active Directory automatically handles the generation, complexity enforcement, and rotation of the password (defaulting to a 30-day cycle).
*   **Zero Knowledge:** The plaintext password is fundamentally unknown to human administrators, removing the risk of credential sharing or weak passwords.
*   **Farm Support:** A single gMSA can be shared securely across multiple computer objects within a cluster or web farm.
*   **SPN Management:** Service Principal Names (SPNs) are automatically managed, mitigating misconfiguration risks that lead to Kerberoasting.

While gMSAs are exceptionally secure by design, the architectural mechanism by which authorized endpoint computers retrieve the gMSA password from Active Directory introduces an attack surface. If an attacker compromises the correct assets or identifies authorization misconfigurations, the gMSA payload can be extracted.

## 2. The gMSA Architecture and Password Retrieval Process
Understanding the extraction attack requires a deep comprehension of the legitimate gMSA password retrieval workflow.

1.  **Object Creation:** A privileged administrator (e.g., Domain Admin) creates the gMSA object in Active Directory (`msDS-GroupManagedServiceAccount`).
2.  **Authorization Definition:** The administrator explicitly defines which computer accounts (or security groups containing computer accounts) are legally permitted to request the password. This critical access control is stored in the `msDS-GroupMSAMembership` attribute of the gMSA object.
3.  **Key Distribution Services (KDS):** A KDS Root Key must be deployed within the AD forest. The KDS subsystem mathematically generates a deterministic password based on the KDS Root Key, the specific gMSA's object SID, and the current temporal interval.
4.  **Retrieval Request:** When an authorized computer requires the gMSA identity to instantiate a service, it issues an LDAP query to a Domain Controller, specifically requesting the `msDS-ManagedPassword` attribute of the gMSA object.
5.  **Validation and Delivery:** The Domain Controller validates the requesting computer against the `msDS-GroupMSAMembership` ACL. If authorized, the DC computes the current password dynamically and returns it to the client as a complex binary blob.

### 2.1 Attack Architecture Diagram
```text
  +-----------------------+      (1) Compromise Authorized Machine            +---------------------------+
  |       Attacker        | ================================================> |    Authorized Server      |
  |                       |      (e.g., via RCE, Phishing, Lateral Mvmt)      |    (e.g., IIS-WEB-01$)    |
  +-----------------------+                                                   +---------------------------+
            |                                                                              |
            | (2) Escalate to SYSTEM & Impersonate Computer Account                        |
            V                                                                              |
  +-----------------------+      (3) LDAP Query for msDS-ManagedPassword                   |
  |   Attacker Context    | ---------------------------------------------------------------+
  |   (IIS-WEB-01$)       |                                                                |
  +-----------------------+ <--------------------------------------------------------------+
            |                    (4) DC evaluates ACL & returns Password Blob              |
            |                                                                              V
            V                                                                 +---------------------------+
  [ Parse Binary Blob ]                                                       |   Domain Controller       |
  [ Extract NT Hash ]                                                         |   (KDS Service)           |
  [ Conduct PtH / Forgery ]                                                   +---------------------------+
```

## 3. Vulnerability and Exploitation Methodology
The vulnerability does not lie within the cryptography, but rather within the authorization boundaries. If an attacker achieves code execution on a machine that is authorized to retrieve the gMSA password, they can duplicate the legitimate request process. Furthermore, if the ACLs (`msDS-GroupMSAMembership`) are misconfigured to include overly broad groups, the attack surface expands exponentially.

### 3.1 Step 1: Reconnaissance (Identifying gMSAs and Authorization)
The first phase involves enumerating the environment to locate gMSA objects and, crucially, determining which entities possess the rights to read their passwords.

*Using PowerView for Enumeration:*
```powershell
# Retrieve all gMSA objects within the domain
Get-DomainManagedServiceAccount

# Interrogate the ACL to determine authorized password readers for a specific gMSA
Get-DomainObjectAcl -Identity "svc_sql_gmsa$" -ResolveGUIDs | ? { $_.ObjectAceType -eq 'msDS-GroupMSAMembership' }
```

*Using BloodHound:*
BloodHound visualizes this relationship via the highly critical `ReadGMSAPassword` edge. Path analysis revealing a route from a compromised user or machine to a gMSA node via this edge dictates immediate exploitability.

### 3.2 Step 2: Extracting the Password Blob
Extraction must occur from an authorized context. This typically means possessing a shell running as `NT AUTHORITY\SYSTEM` on the authorized computer (e.g., `IIS-WEB-01$`), or possessing the credentials/hash of that computer account.

The requested password is returned as an `MSDS-MANAGEDPASSWORD_BLOB`, a complex binary structure containing the current password, historical passwords, and metadata.

**Local Extraction via GMSAPasswordReader.exe (C#):**
Execute this tool on the authorized host as SYSTEM.
```cmd
# The tool queries LDAP, parses the blob, and outputs the NT hash
GMSAPasswordReader.exe --accountname svc_sql_gmsa
```

**Local Extraction via PowerShell (PowerView):**
```powershell
# Retrieve the raw binary blob
$blob = (Get-DomainObject -Identity "svc_sql_gmsa$")."msds-managedpassword"
# (Further scripting is required to parse the blob into an NT Hash)
```

**Remote Extraction via NetExec (Impacket):**
If the attacker possesses the NTLM hash or a valid Kerberos ticket for the authorized computer account, extraction can be performed remotely, bypassing the need for a shell on the target server.
```bash
# Utilizing the compromised machine account hash to extract the gMSA over LDAP
nxc ldap 192.168.1.10 -u 'IIS-WEB-01$' -H 'MACHINE_ACCOUNT_NT_HASH' --gmsa
```

### 3.3 Step 3: Parsing the Blob and Weaponization
The `msDS-ManagedPassword` blob contains the plaintext password, but the plaintext generated by KDS is a 256-byte random array of characters that is highly unmanageable and largely useless for interactive logins. Attackers focus entirely on the derived NT Hash.

**Weaponization Vectors:**
Once the NT Hash of the gMSA is extracted, it can be weaponized in several high-impact ways:
1.  **Pass-the-Hash (PtH):** Authenticate directly to services or endpoints where the gMSA has been granted administrative or access privileges (e.g., logging into an MSSQL database as the service account).
2.  **Silver Tickets (Service Ticket Forgery):** Because gMSAs are designed to run services, they inevitably have Service Principal Names (SPNs) registered. Obtaining the gMSA NT hash provides the RC4 key (or AES keys if extracted via advanced memory analysis) required to cryptographically forge Kerberos Service Tickets.
    *   *Scenario:* The extracted gMSA runs the MSSQL service. The attacker forges a Silver Ticket to access the database with `sysadmin` privileges, completely bypassing standard authentication.

## 4. Advanced Scenario: DACL Misconfigurations and MachineAccountQuota
Administrators occasionally misconfigure gMSA authorization. Instead of restricting `msDS-GroupMSAMembership` to a highly specific security group containing only the required servers, they might mistakenly add the `Domain Computers` group or, worse, an `Authenticated Users` group.

**The MachineAccountQuota Exploit Chain:**
If `Domain Computers` is authorized, any domain user can exploit this via the default `MachineAccountQuota` setting (which defaults to 10).
1.  The attacker, possessing only standard user credentials, creates a new, rogue computer account in AD.
2.  The attacker authenticates to LDAP using the credentials of the newly created rogue computer account.
3.  Because the rogue computer is a member of `Domain Computers`, it is legally authorized to request the gMSA password blob.
This specific misconfiguration allows a zero-privilege domain user to instantly escalate to gMSA compromise.

## 5. Defense, Mitigation, and Detective Controls
### 5.1 Enforcing the Principle of Least Privilege
*   **Strict Membership Auditing:** Ensure the `msDS-GroupMSAMembership` attribute contains only the absolute minimum required computer objects. Never use broad groups like `Domain Computers`.
*   **Nullify MachineAccountQuota:** Set the domain-level `MachineAccountQuota` attribute to `0`. This prevents standard users from creating rogue computer accounts, severing the misconfiguration exploit chain.

### 5.2 Detective and Monitoring Strategies
*   **Monitor Targeted LDAP Queries:** Hunt for LDAP queries specifically requesting the `msDS-ManagedPassword` attribute. While this is a legitimate operational request, anomalous patterns emerge:
    *   Queries originating from workstation subnets instead of server VLANs.
    *   Queries originating from a user context rather than a `SYSTEM` or computer account context.
*   **Active Directory Object Auditing (Event ID 4662):** Configure SACLs to audit read access on gMSA objects. Monitor for Event ID 4662 where the Object Type is a gMSA and the properties accessed include the managed password attribute.
*   **Monitoring Attribute Modifications (Event ID 4690/4742):** Rigorously monitor for any changes to the gMSA object itself, specifically unauthorized modifications to the `msDS-GroupMSAMembership` attribute, which indicates an attacker attempting to authorize their own systems.

## 6. Cryptographic Anatomy of the Blob
The `MSDS-MANAGEDPASSWORD_BLOB` is structured as follows:
- Version field
- Reserved fields
- Length of the current password
- Current password (unicode string)
- Length of previous password
- Previous password (unicode string)
Tools like `gMSADumper` explicitly extract these Unicode strings and MD4 hash them to derive the standard NTLM hash.

## 7. Chaining Opportunities
*   [[14 - GPO Abuse at Scale]] - Attackers who compromise a GPO can deploy a scheduled task running as SYSTEM on authorized servers to execute the extraction script and silently relay the gMSA hash back to Command and Control (C2).
*   [[08 - Silver Tickets and SPN Forgery]] - The primary weaponization mechanism for an extracted gMSA hash is forging a Silver Ticket for the services it operates, ensuring persistent and undetectable access.
*   [[15 - DPAPI and DPAPI-NG Master Key Extraction]] - If a gMSA is utilized to run an IIS web service, its user profile might contain DPAPI keys required to decrypt sensitive data such as `web.config` connection strings.

## 8. Related Notes
*   [[01 - Kerberoasting and AS-REP Roasting]]
*   [[20 - Lateral Movement Techniques]]
*   [[24 - Active Directory Access Control Lists ACLs]]
*   [[06 - Credential Dumping Techniques]]

## Real-World Attack Scenario
## Real-World Attack Scenario: Extracting gMSA Passwords

**1. Context and Environment:**
The target is a healthcare organization that has modernized its service accounts by deploying Group Managed Service Accounts (gMSA) for its SQL Server infrastructure. The attacker has gained a foothold on a seemingly unimportant web server (`WEB02`) in the DMZ. The objective is to pivot into the internal network and access the heavily guarded database servers.

**2. Attacker Thought Process:**
"I'm on a web server that communicates with an internal SQL cluster. The SQL services are running under a gMSA (`svc_sql_prod$`). gMSAs are highly secure because AD manages their 120-character passwords automatically. However, the machines authorized to use the gMSA must be able to read its password from AD. If `WEB02` or a user I've compromised on it is in the allowed PrincipalsAllowedToRetrieveManagedPassword group, I can simply ask the Domain Controller for the plaintext password of the SQL service account."

**3. Reconnaissance and Enumeration:**
The attacker queries Active Directory to find out exactly which accounts are authorized to retrieve the password for the target gMSA.
```powershell
# Using PowerView to check gMSA configuration
Get-DomainObject -Identity "svc_sql_prod$" -Properties msds-groupmsamembership
```
The output reveals that a security group `SG-Web-Tier` is allowed to retrieve the password. The attacker checks the membership of this group and confirms that the compromised machine account, `WEB02$`, is a member.

**4. Exploitation and Execution:**
Since the attacker has local SYSTEM privileges on `WEB02`, they can operate in the context of the `WEB02$` machine account. They use a tool like `GMSAPasswordReader` or Mimikatz to request the current gMSA password directly from the Key Distribution Center (KDC) on the Domain Controller.
```bash
# Using Mimikatz as SYSTEM on the compromised host
mimikatz # privilege::debug
mimikatz # token::elevate
mimikatz # lsadump::dcsync /domain:corp.local /user:svc_sql_prod$
```
Alternatively, using a lightweight PowerShell script to read the `msDS-ManagedPassword` blob and decrypt it locally using the machine's context:
```powershell
# Using a custom script to extract the password blob
Import-Module .\GMSA-Reader.ps1
Get-gMSAPassword -AccountName svc_sql_prod$
```
The script decrypts the blob and outputs the NT hash and the cleartext 120-character password.

**5. Post-Exploitation and Outcome:**
Armed with the NT hash of `svc_sql_prod$`, the attacker performs a Pass-the-Hash attack to authenticate to the internal SQL server cluster.
```bash
impacket-mssqlclient -hashes :<NTHash> corp/svc_sql_prod\$@10.20.30.40
```
Because the SQL service account has `sysadmin` privileges on the database, the attacker enables `xp_cmdshell` and executes system-level commands on the internal database server, successfully bridging the DMZ and establishing a firm foothold in the secure internal network tier.

