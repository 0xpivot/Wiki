---
tags: [active-directory, basics, enumeration, vapt]
difficulty: beginner
module: "67 - AD Enumeration and Tooling Basics"
topic: "67.14 Kerberoasting Basics and Identification"
---

# Kerberoasting Basics and Identification

## 1. Executive Summary & Introduction
Kerberoasting is one of the most widespread, effective, and frequently executed attacks in Active Directory (AD) environments. It targets Service Principal Names (SPNs) associated with domain user accounts. By requesting Kerberos Service Tickets (TGS) for these accounts, an attacker can extract a portion of the ticket encrypted with the service account's password hash. This hash can then be cracked offline.

Because any authenticated domain user can request a TGS for any valid SPN within the domain, Kerberoasting requires no special privileges beyond a standard user foothold. Furthermore, because service accounts often hold high privileges (e.g., Domain Admins, SQL Admins) and are notorious for having weak, non-expiring passwords, Kerberoasting frequently provides a direct path to domain compromise.

## 2. Technical Mechanisms and Kerberos Deep Dive
### 2.1 Service Principal Names (SPNs)
An SPN is a unique identifier for a service instance (like an MSSQL server, an IIS web server, or a file share). In AD, a service must be registered under an account so that clients can authenticate to it using Kerberos.
- **Computer Accounts**: By default, SPNs are registered under machine accounts (e.g., `WS01$`). These passwords are long (120 chars), randomized, and change every 30 days. They are practically uncrackable.
- **User Accounts**: System administrators often register SPNs under standard domain user accounts (e.g., `svc_sql`). These passwords are set by humans, frequently fail to meet complexity standards, and often have the "Password never expires" flag set. These are the targets of Kerberoasting.

### 2.2 The Kerberos TGS-REQ/REP Flow
1. **AS-REQ / AS-REP**: The attacker (as a standard domain user) authenticates to the Domain Controller (KDC) and receives a Ticket Granting Ticket (TGT).
2. **TGS-REQ**: The attacker sends a Ticket Granting Service Request to the KDC, presenting their TGT and requesting access to a specific SPN (e.g., `MSSQLSvc/sql.domain.local`).
3. **TGS-REP**: The KDC verifies the TGT and the existence of the SPN. The KDC generates a Service Ticket and sends it back to the attacker.
4. **The Vulnerability**: The Service Ticket contains a section that is encrypted using the NTLM hash (RC4) or AES key of the account associated with the SPN.

### 2.3 Offline Cracking
Crucially, the attacker *does not* need to actually interact with the target service (e.g., the SQL server). They simply take the encrypted Service Ticket they received in step 3, save it to disk, and use brute-force or dictionary attacks to decrypt it. If the password is weak, the ticket is decrypted, and the plaintext password is revealed.

## 3. Visual Attack Flow Diagram
```text
+-------------------+                                  +---------------------+
|   Attacker        |                                  |   Domain Controller |
| (Auth'd User)     |                                  |   (KDC / AD DS)     |
+-------+-----------+                                  +----------+----------+
        |                                                         |
        | 1. LDAP Query: Find all User objects with SPNs          |
        |-------------------------------------------------------->|
        | 2. Returns list of SPNs (e.g., svc_sql, svc_backup)     |
        |<--------------------------------------------------------|
        |                                                         |
        | 3. TGS-REQ: "I want a ticket for svc_sql"               |
        |    (Presents attacker's TGT)                            |
        |-------------------------------------------------------->|
        |                                                         |
        | 4. KDC encrypts ticket using svc_sql's password hash    |
        |                                                         |
        | 5. TGS-REP: Returns Encrypted Service Ticket            |
        |<--------------------------------------------------------|
        |                                                         |
+-------+-----------+                                             |
| Offline Cracking  |                                             |
| (Hashcat Mode     |                                             |
|  13100)           |                                             |
+-------------------+                                             |
```

## 4. Execution and Tooling
### 4.1 Enumeration and Extraction via Impacket
From a Linux attacking machine, `GetUserSPNs.py` automates the LDAP query and the TGS-REQ/REP process in one step.
```bash
# Request TGS tickets for all user SPNs and output in hashcat format
GetUserSPNs.py domain.local/jsmith:Password123! -request -outputfile kerberoast_hashes.txt -dc-ip 192.168.1.10
```

### 4.2 Execution via Rubeus (Windows)
If the attacker is operating from a compromised Windows host, Rubeus is the standard tool.
```cmd
# Automatically find all SPNs and request tickets (RC4 preferred)
Rubeus.exe kerberoast /outfile:hashes.txt
```

### 4.3 Execution via PowerShell (Native)
It is possible to request SPNs natively using PowerShell without external tools, making it highly stealthy.
```powershell
Add-Type -AssemblyName System.IdentityModel
New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList "MSSQLSvc/sql.domain.local"
# The ticket is now cached in memory and can be exported using Mimikatz or Rubeus
```

### 4.4 Offline Cracking
Once the hashes are obtained, Hashcat is used to crack them. Mode 13100 is used for RC4 (Type 23) tickets.
```bash
hashcat -m 13100 kerberoast_hashes.txt rockyou.txt -r rules/best64.rule

# For AES-256 (Type 18), use mode 19600
hashcat -m 19600 kerberoast_aes.txt rockyou.txt
```

## 5. Security Posture and Mitigations
### 5.1 Enforce Strong Passwords for Service Accounts
Because Kerberoasting is an offline attack relying on cracking, the ultimate mitigation is a password that mathematically cannot be cracked within a reasonable timeframe. Service accounts should have randomly generated passwords of 30+ characters.

### 5.2 Managed Service Accounts (gMSA)
Organizations should transition from traditional User accounts for services to Group Managed Service Accounts (gMSAs). gMSAs automatically manage their own passwords (similar to computer accounts), making them 120 characters long and rotating them every 30 days. gMSAs completely neutralize Kerberoasting.

### 5.3 Enforce AES Encryption
Legacy environments default to RC4 (Encryption Type 23) for Kerberos. RC4 is significantly faster to crack offline than AES (Encryption Type 18/17). Ensuring the domain enforces AES for Kerberos tickets dramatically increases the time and compute power required to crack the hashes.

## 6. Detection Engineering
Detecting Kerberoasting is challenging because requesting a TGS is a normal, daily occurrence for every user on the network.

### 6.1 Event ID 4769 (A Kerberos service ticket was requested)
- **Anomaly Detection**: Look for an unusual spike in 4769 events from a single user or IP address in a short time window. Standard users rarely request 50 different service tickets in 2 seconds.
- **Encryption Type Anomalies**: If the domain enforces AES, but an attacker specifically downgrades the request to RC4 (Type 0x17) to make cracking easier, this is a massive red flag. Alert on Event ID 4769 where `Ticket Encryption Type` is `0x17`.

### 6.2 Honey SPNs (Deception Technology)
The most effective detection mechanism is a HoneyToken.
1. Create a fake user account (e.g., `svc_financial_db`).
2. Assign it a fake SPN.
3. Give it a massive, uncrackable password.
4. Set up an alert: Any time Event 4769 is triggered for this specific SPN, it is 100% malicious, as no legitimate service uses it.

### 6.3 Splunk SPL for Honey SPN
```spl
index=windows_security EventCode=4769 TargetUserName="svc_financial_db"
| eval Message="ALERT: Honey SPN Kerberoast attempt detected!"
| table _time, TargetUserName, IpAddress, ClientName
```

## 7. Real-World Case Study
In a 2023 red team exercise, the team established a foothold as a standard user (`h.potter`). They immediately ran Rubeus to kerberoast the domain. They retrieved 15 RC4 service tickets. One of these tickets belonged to an account named `svc_sccm_deploy`. After 15 minutes of cracking using a custom wordlist based on the company's internal documentation, the password `Deploy!2019` was revealed. This service account possessed local administrator rights on all workstations and servers, including the Domain Controllers, leading to a complete compromise of the forest in under two hours.

## 8. Chaining Opportunities
- **[[13 - AS-REP Roasting Basics and Detection]]**: Often the precursor. If AS-REP roasting yields no results, the attacker moves to Kerberoasting.
- **[[20 - Silver Tickets]]**: Once a service account password is cracked, the attacker possesses the account's NTLM hash. They can use this to forge Silver Tickets, granting them administrative access to the service without communicating with the DC.

## 9. Related Notes
- [[13 - AS-REP Roasting Basics and Detection]]
- [[20 - Silver Tickets]]
- [[05 - BloodHound Data Collection]]

## Appendix A: Extended Troubleshooting & Common Error Codes
When executing Active Directory enumeration and exploitation attacks, practitioners frequently encounter a variety of error codes. Understanding these is critical for operational success.

### Kerberos and Authentication Errors
- **KDC_ERR_PREAUTH_REQUIRED (0x11)**: Expected behavior when a user requires pre-authentication. Occurs during normal AS-REQ if `DONT_REQ_PREAUTH` is not set.
- **KDC_ERR_CLIENT_REVOKED (0x12)**: The targeted user account has been disabled or locked out. Attackers should immediately cease spraying or brute-forcing this account to avoid further detection.
- **KDC_ERR_PREAUTH_FAILED (0x18)**: The password provided during pre-authentication was incorrect. This is the primary indicator of a failed password spray attempt.
- **KDC_ERR_ETYPE_NOSUPP (0x0E)**: The requested encryption type is not supported. This often happens if an attacker specifically requests an RC4 ticket but the domain has strictly enforced AES-only communication via GPO.

### SMB and RPC Errors
- **STATUS_LOGON_FAILURE (0xC000006D)**: Invalid credentials provided during an SMB or RPC connection attempt.
- **STATUS_ACCOUNT_LOCKED_OUT (0xC0000234)**: The user account is locked out. This is a critical failure in operational security if triggered inadvertently.
- **STATUS_ACCESS_DENIED (0xC0000022)**: The provided credentials are valid, but the user lacks the necessary authorization to perform the requested action (e.g., querying the SAM database, accessing an administrative share like `C$`).
- **STATUS_PASSWORD_MUST_CHANGE (0xC0000224)**: The password is correct, but the user must change it at next logon. Tools like NetExec can often automatically handle this if specified.

## Appendix B: Advanced Threat Hunting and Detection Playbooks
To build a robust defense-in-depth strategy, organizations must transition from reactive alerting to proactive threat hunting.

### SIEM Integration and Data Sources
Effective detection requires ingesting the following log sources into a centralized SIEM (e.g., Splunk, Microsoft Sentinel, Elastic Security):
1. **Windows Security Event Logs** from all Domain Controllers.
2. **Windows Security Event Logs** from critical tier-0 and tier-1 servers.
3. **Sysmon (System Monitor) Logs** (specifically Event ID 3 for network connections and Event ID 1 for process creation).
4. **Network Traffic Analysis (NTA) / Zeek** logs for identifying anomalous RPC and SMB traffic patterns.

### Developing High-Fidelity Alerts
When creating alerts, focus on combinations of events rather than single occurrences to reduce false positives:
- **Correlated Reconnaissance**: Alert when a single source IP generates Event ID 4624 (Logon) across more than 20 distinct destination IPs within a 15-minute window, followed by Event ID 5145 (Detailed Share) accessing `IPC$`.
- **Honeytoken Triggers**: Any authentication attempt (Event ID 4624) or ticket request (Event ID 4768/4769) against a designated honey account must trigger a critical, paging alert to the SOC immediately. Honeytokens have near-zero false positive rates.

## Appendix C: Glossary of Active Directory Terminology
- **TGT (Ticket Granting Ticket)**: The primary Kerberos ticket issued by the KDC upon successful initial authentication. It acts as a passport, allowing the user to request access to specific services without re-entering their password.
- **TGS (Ticket Granting Service / Service Ticket)**: A secondary Kerberos ticket requested using the TGT, granting access to a specific service or resource (e.g., CIFS, MSSQLSvc).
- **KDC (Key Distribution Center)**: The Kerberos service running on Domain Controllers responsible for authenticating users and issuing tickets.
- **SPN (Service Principal Name)**: A unique identifier that maps a service instance to a domain account. Required for Kerberos mutual authentication.
- **NTDS.dit**: The central database file on a Domain Controller that stores all Active Directory data, including user objects, group memberships, and password hashes.
- **SID (Security Identifier)**: A unique, immutable value assigned to every principal (user, group, computer) in Active Directory.
- **RPC (Remote Procedure Call)**: A protocol that allows a program to execute code on a remote system. It is heavily used for Windows management and administration.
- **LSASS (Local Security Authority Subsystem Service)**: The Windows process responsible for enforcing security policies, verifying user logins, handling password changes, and creating access tokens. It often stores credentials in memory, making it a prime target for credential dumping.

## Real-World Attack Scenario
## Real-World Attack Scenario

During a penetration test for a healthcare provider, I had compromised a standard nurse's workstation and obtained low-privileged domain user credentials. To access the highly restricted patient database, I needed to escalate privileges. The most effective post-authentication attack in Active Directory is Kerberoasting, which exploits the way Kerberos issues service tickets.

**Thought Process:**
When an authenticated user requests access to a service (like an MSSQL database or an IIS web server), the Domain Controller issues a Kerberos Ticket Granting Service (TGS) ticket. A portion of this TGS is encrypted using the NTLM hash of the Service Account running that service. Because any valid domain user can request a TGS for any registered Service Principal Name (SPN), I could request tickets for high-value service accounts, export them, and crack them offline. Service accounts often have elevated privileges and weak, never-changing passwords.

**Execution:**
Using my compromised low-privileged account, I utilized Impacket's `GetUserSPNs.py` script to query the Domain Controller for all user accounts associated with an SPN, and simultaneously request their TGS tickets formatted for Hashcat.
```bash
impacket-GetUserSPNs healthcare.local/nurse_jdoe:Password123! -request -dc-ip 10.20.30.40 -outputfile kerberoast_hashes.txt
```
The script quickly identified several SPNs and successfully requested TGS tickets for them. One ticket was specifically tied to the `svc_sql_clinical` account, which ran the primary MSSQL database.

I transferred the `kerberoast_hashes.txt` file (containing the `$krb5tgs$23$*` formatted hashes) to my offline cracking machine. Using Hashcat and a targeted dictionary, I began the offline brute-force attack:
```bash
hashcat -m 13100 kerberoast_hashes.txt custom_wordlist.txt -O -w 3
```

**Outcome:**
The offline cracking succeeded in two hours, revealing the service account password: `Clin1calDB_!`. I immediately used these credentials to authenticate directly to the MSSQL server using `mssqlclient.py`. Because the service account was a member of the SQL `sysadmin` role, I enabled `xp_cmdshell` and executed operating system commands with SYSTEM privileges on the database server. Kerberoasting allowed me to turn a low-privileged domain user into a database administrator entirely offline, without generating any suspicious brute-force traffic on the network.

