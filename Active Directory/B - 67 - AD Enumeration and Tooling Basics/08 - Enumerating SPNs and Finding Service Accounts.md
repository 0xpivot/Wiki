---
tags: [active-directory, basics, enumeration, vapt]
difficulty: beginner
module: "67 - AD Enumeration and Tooling Basics"
topic: "67.08 Enumerating SPNs and Finding Service Accounts"
---

# 08 - Enumerating SPNs and Finding Service Accounts

## 1. Introduction to Service Principal Names (SPNs)

In an Active Directory (AD) environment utilizing Kerberos authentication, a Service Principal Name (SPN) is a unique identifier for a service instance. SPNs are used by Kerberos authentication to associate a service instance with a service logon account. This allows a client application to request Kerberos tickets to authenticate to a service even if the client does not know the account name the service is running under.

When a user wants to access a service (e.g., a SQL server, an IIS web server, or an SMB share), they request a Ticket Granting Service (TGS) ticket from the Domain Controller. To identify which service they want to access, the client provides the SPN.

**SPN Format:**
`serviceclass/host:port/servicename`
Example: `MSSQLSvc/sqlprod01.domain.local:1433`

### 1.1 Types of Service Accounts
1. **Machine Accounts:** By default, services running under the `Local System` or `Network Service` context use the computer's machine account (e.g., `SQLPROD01$`). AD automatically manages these passwords, making them 120 characters long and rotating them every 30 days. They are highly secure.
2. **User Service Accounts:** Often, administrators configure services to run under standard domain user accounts (e.g., `svc_sql`). These accounts are standard AD users that have an SPN registered to them. Unlike machine accounts, their passwords are set by humans, rarely rotated, and often vulnerable to offline cracking.

## 2. The Vulnerability: Kerberoasting Concept

Because any authenticated domain user can query Active Directory for accounts with registered SPNs and subsequently request a TGS ticket for those services, an architectural flaw in Kerberos can be exploited. 

When the Domain Controller issues the TGS ticket for the requested service, a portion of that ticket is encrypted using the NTLM hash of the service account's password. The attacker can extract this ticket from memory, export it, and subject it to offline brute-force or dictionary attacks to recover the service account's cleartext password. This attack is known as **Kerberoasting**.

## 3. Architecture and Attack Flow Diagram

The following ASCII diagram illustrates the flow of SPN enumeration leading into a Kerberoasting attack.

```text
+-----------------------+                                      +-------------------------------+
|   Attacker Machine    |                                      |   Target Domain Controller    |
|   Domain Authenticated|                                      |        IP: 192.168.1.10       |
|   User: jsmith        |                                      |                               |
+-----------+-----------+                                      +---------------+---------------+
            |                                                                  |
            | 1. LDAP Query: Find users where servicePrincipalName=*           |
            |----------------------------------------------------------------->|
            |                                                                  |
            | 2. LDAP Response: Returns 'svc_sql' (SPN: MSSQLSvc/sql01)        |
            |<-----------------------------------------------------------------|
            |                                                                  |
            | 3. TGS-REQ: Request ticket for MSSQLSvc/sql01                    |
            |    (Using jsmith's valid TGT)                                    |
            |----------------------------------------------------------------->|
            |                                                                  |
            | 4. TGS-REP: Returns TGS Ticket encrypted with svc_sql's hash     |
            |<-----------------------------------------------------------------|
            |                                                                  |
            | 5. Attacker extracts TGS ticket from memory to disk              |
            |    (Format: $krb5tgs$23$...)                                     |
            |                                                                  |
+-----------+-----------+                                      +-------------------------------+
| 6. Offline Brute-force|                                      | DC behaves completely normally|
|    using Hashcat or   |                                      | according to the Kerberos     |
|    John the Ripper.   |                                      | protocol specifications.      |
+-----------------------+                                      +-------------------------------+
```

## 4. Enumeration Tooling Deep Dive

Enumerating SPNs is a standard step for any internal penetration test. The goal is to identify user accounts (not machine accounts) that have an SPN set.

### 4.1 Impacket - GetUserSPNs.py

Impacket provides a robust python script specifically designed to query AD for user accounts with SPNs and automatically export the vulnerable TGS tickets in a hashcat-crackable format.

**Command (Enumeration and Extraction):**
```bash
impacket-GetUserSPNs domain.local/jsmith:Password123 -dc-ip 192.168.1.10 -request
```

**Output Snippet:**
```text
ServicePrincipalName                 Name      MemberOf                                PasswordLastSet             LastLogon                   Delegation 
------------------------------------ --------- --------------------------------------- --------------------------- --------------------------- ----------
MSSQLSvc/sqlprod01.domain.local:1433 svc_sql   CN=Domain Admins,CN=Users,DC=domain,... 2019-04-12 10:22:00         2026-06-10 08:15:00         False     

$krb5tgs$23$*svc_sql$DOMAIN.LOCAL$domain.local/svc_sql*$6b746... <snip> ...
```
Notice that `svc_sql` is a member of Domain Admins. If the password is cracked, the attacker instantly compromises the entire domain.

### 4.2 PowerView (PowerShell)

PowerView is a powerful PowerShell tool for AD enumeration. It utilizes ADSI (Active Directory Service Interfaces) to query LDAP smoothly.

**Command:**
```powershell
Get-DomainUser -SPN | Select-Object samaccountname, serviceprincipalname, memberof
```
This command filters the AD users, displaying only those with an SPN attribute set, allowing the attacker to map out the attack surface before requesting tickets.

### 4.3 BloodHound

BloodHound uses graph theory to reveal hidden relationships within AD. Its data collector (`SharpHound`) automatically enumerates users with SPNs and calculates paths to domain dominance based on those accounts.

In the BloodHound UI, you can use the pre-built query:
**"Find all Kerberoastable Users"**
This visually plots the vulnerable service accounts and shows which high-privileged groups they belong to.

### 4.4 SetSPN.exe (Living off the Land)

`SetSPN.exe` is a native Windows binary used by administrators to read, modify, and delete SPN directory properties. Because it is a signed Microsoft binary, it is excellent for avoiding endpoint detection.

**Command:**
```cmd
setspn -T domain.local -Q */*
```
This queries the domain for all registered SPNs. You will need to manually filter out the machine accounts (those ending in `$`) to find the vulnerable user service accounts.

### 4.5 NetExec (formerly CrackMapExec)

NetExec can also perform LDAP enumeration to locate Kerberoastable accounts.

**Command:**
```bash
nxc ldap 192.168.1.10 -u jsmith -p Password123 --kerberoasting output_hashes.txt
```

## 5. Identifying the Value of Service Accounts

Not all service accounts are created equal. When an attacker enumerates SPNs, they prioritize targets based on:
1. **Group Membership:** Accounts belonging to `Domain Admins`, `Enterprise Admins`, or `Backup Operators` are the highest priority.
2. **Password Age:** A password last set in 2015 is highly likely to be weak and easily crackable compared to one set last month.
3. **Service Type:** `MSSQLSvc` accounts often have sysadmin rights on the database server. `HTTP` accounts might have local admin on the web server.

## 6. Defensive Considerations and Remediation

### 6.1 Implement Group Managed Service Accounts (gMSA)
The absolute best defense against Kerberoasting is to stop using standard user accounts for services. Group Managed Service Accounts (gMSA) provide the same functionality but the passwords are automatically generated, complex (120 characters), and rotated by the Domain Controller. They are impossible to crack offline.

### 6.2 Enforce Extremely Strong Passwords
If legacy applications do not support gMSAs, ensure the service account password is treated like a cryptographic key: minimum 30+ characters, randomly generated, and utilizing all character spaces.

### 6.3 Telemetry, Logging, and Detection
- **Event ID 4769 (A Kerberos service ticket was requested):** This event is noisy because TGS requests happen constantly. However, defenders can alert on anomalies:
  - TGS requests where the encryption type (`Ticket Options` / `Ticket Encryption Type`) is downgraded to RC4 (`0x17`). Modern Kerberoasting tools often request RC4 tickets because they are vastly faster to crack than AES-256 (`0x12`).
  - High velocity of TGS requests for *different* service accounts originating from a single user within a short time frame.
- **Honey SPNs:** Create a fake, highly attractive user account (e.g., `svc_domainadmin`) and register a fake SPN to it. Since no legitimate service uses this account, any TGS request (Event ID 4769) for this specific SPN is a guaranteed indicator of a Kerberoasting attack.

## 7. Chaining Opportunities

- **Kerberoasting -> Domain Admin:** The most common chain. Enumerate SPN -> Extract Ticket -> Crack offline -> Login as Domain Admin.
- **Silver Tickets:** If the service account password is recovered, the attacker possesses the NTLM hash. They can use this hash to forge their own TGS tickets (Silver Tickets) to access that specific service infinitely, bypassing the Domain Controller entirely. See `[[24 - Kerberos Silver Tickets]]`.
- **Targeted Lateral Movement:** If the account is a local administrator on a specific server (e.g., an IIS server), recovering the password allows lateral movement to that server to pivot further into the network.

## 8. Related Notes
- [[09 - Identifying Domain Controllers and Global Catalogs]]
- [[23 - Kerberoasting Attacks and Mitigation]]
- [[24 - Kerberos Silver Tickets]]
- [[13 - BloodHound and Active Directory Graph Analysis]]
- [[05 - Active Directory Architecture Overview]]

## Real-World Attack Scenario
## Real-World Attack Scenario

In a recent engagement for an e-commerce platform, I was operating from a standard developer's compromised workstation. To progress laterally and escalate privileges without relying on noisy exploit attempts, I focused on identifying high-value Service Principal Names (SPNs). Service accounts are often highly privileged and, critically, their passwords rarely change due to fear of breaking production services.

**Thought Process:**
By querying the Active Directory for accounts with registered SPNs, I could map out the internal infrastructure—identifying where MSSQL, Exchange, and IIS services were running. Furthermore, finding a user account (rather than a machine account) with an SPN would directly set up a Kerberoasting attack. My objective was to quietly extract all SPNs using built-in Windows tools or LDAP queries to avoid triggering endpoint detection and response (EDR) alerts associated with aggressive network scanning.

**Execution:**
To remain stealthy and "live off the land," I utilized the native `setspn.exe` utility, which is installed by default on Windows workstations, to list all SPNs in the domain:
```cmd
setspn.exe -T ecommerce.local -Q */*
```
The output generated a massive list of registered services. I redirected the output to a text file and filtered it for interesting services like SQL servers and web applications.
```cmd
setspn.exe -T ecommerce.local -Q */* > spns.txt
findstr /i "MSSQLSvc" spns.txt
```
I noticed a specific SPN: `MSSQLSvc/sql-prod-01.ecommerce.local:1433` registered to a domain user account named `svc_sql_admin` instead of a computer account. 

To gather more context about this service account without triggering alerts, I executed a targeted LDAP query using PowerShell's ADSI capabilities to check the account's group memberships and description:
```powershell
$Searcher = New-Object DirectoryServices.DirectorySearcher
$Searcher.Filter = "(samaccountname=svc_sql_admin)"
$Searcher.FindOne().Properties
```
The description field literally read: "Service account for PROD SQL - DO NOT CHANGE PWD".

**Outcome:**
By enumerating SPNs, I successfully mapped the location of the critical production database (`sql-prod-01`) and identified that it was running under the context of a highly privileged domain user account (`svc_sql_admin`). This discovery bypassed the need for network port scanning entirely. It immediately provided the exact target for a subsequent Kerberoasting attack, ultimately leading to the extraction and offline cracking of the `svc_sql_admin` password, granting administrative access to the sensitive customer database.

