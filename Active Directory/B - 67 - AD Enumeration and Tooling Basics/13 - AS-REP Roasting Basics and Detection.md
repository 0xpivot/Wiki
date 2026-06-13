---
tags: [active-directory, basics, enumeration, vapt]
difficulty: beginner
module: "67 - AD Enumeration and Tooling Basics"
topic: "67.13 AS-REP Roasting Basics and Detection"
---

# AS-REP Roasting Basics and Detection

## 1. Executive Summary & Introduction
AS-REP Roasting is an offensive technique targeting Active Directory (AD) environments that exploits a specific, often legacy-driven, user account configuration: **"Do not require Kerberos preauthentication"** (known as `DONT_REQ_PREAUTH`). When this setting is enabled on a user account, any unauthenticated attacker can request a Kerberos Authentication Service Response (AS-REP) for that user from the Key Distribution Center (KDC/Domain Controller).

The critical flaw lies in the structure of the AS-REP message. A portion of the AS-REP is encrypted using the user's password hash. Because the attacker does not need to authenticate to request this message, they can easily retrieve it, take it offline, and subject it to a brute-force or dictionary attack. If the user possesses a weak password, the attacker can recover the plaintext password, granting them full access to the account.

While less common than Kerberoasting, AS-REP Roasting requires zero initial privileges—an attacker does not even need a valid domain user account to perform the attack, only network line-of-sight to a Domain Controller.

## 2. Technical Mechanisms and Kerberos Deep Dive
### 2.1 Standard Kerberos Pre-Authentication
In a typical Kerberos authentication flow:
1. **AS-REQ (Authentication Service Request)**: The user sends a request to the KDC to obtain a Ticket Granting Ticket (TGT). By default, AD requires pre-authentication. This means the AS-REQ must include a timestamp encrypted with the user's password hash (the `padata` field).
2. **KDC Verification**: The KDC attempts to decrypt this timestamp using the user's hash stored in NTDS.dit. If successful, it proves the user knows their password without transmitting it over the network.
3. **AS-REP (Authentication Service Response)**: The KDC replies with a TGT and a session key, part of which is encrypted with the user's hash.

### 2.2 The DONT_REQ_PREAUTH Vulnerability
When "Do not require Kerberos preauthentication" is checked (UserAccountControl attribute flag `0x00400000` / 4194304):
1. **AS-REQ**: The attacker sends an AS-REQ for the target user *without* the encrypted timestamp.
2. **KDC Verification**: The KDC checks the user's settings, sees pre-authentication is disabled, and skips the timestamp verification.
3. **AS-REP**: The KDC blindly generates the AS-REP and sends it back to the attacker.

The attacker intercepts the AS-REP. Inside this response is the `enc-part`, which contains the logon session key encrypted with the target user's RC4 or AES key (derived from their password). The attacker extracts this encrypted blob.

### 2.3 Offline Cracking
Once the attacker possesses the AS-REP, no further communication with the DC is required. They use tools like Hashcat or John the Ripper to attempt to decrypt the `enc-part`. If a guessed password successfully decrypts the blob, the attacker has discovered the user's plaintext password.

## 3. Visual Attack Flow Diagram
```text
+-------------------+                                  +---------------------+
|   Attacker        |                                  |   Domain Controller |
|   (Unauthenticated|                                  |   (KDC)             |
+-------+-----------+                                  +----------+----------+
        |                                                         |
        | 1. Identify Target (e.g., via anonymous LDAP or guess)  |
        |-------------------------------------------------------->|
        |                                                         |
        | 2. Send AS-REQ for 'VulnerableUser'                     |
        |    (NO Pre-Authentication data included)                |
        |-------------------------------------------------------->|
        |                                                         |
        | 3. KDC checks UserAccountControl (DONT_REQ_PREAUTH = 1) |
        |                                                         |
        | 4. Send AS-REP                                          |
        |    (Contains Encrypted Session Key via User Hash)       |
        |<--------------------------------------------------------|
        |                                                         |
        | 5. Attacker extracts encrypted AS-REP blob              |
        |                                                         |
+-------+-----------+                                             |
| Offline Cracking  |                                             |
| (Hashcat Mode     |                                             |
|  18200 / 11400)   |                                             |
+-------------------+                                             |
```

## 4. Execution and Tooling
### 4.1 Enumeration
An attacker with a valid domain account can query LDAP for users with the `DONT_REQ_PREAUTH` flag.
```powershell
# Using PowerView
Get-DomainUser -PreauthNotRequired -Properties samaccountname

# Using native ADModule
Get-ADUser -Filter {DoesNotRequirePreAuth -eq $True} -Properties DoesNotRequirePreAuth
```

### 4.2 Exploitation / Roasting
If the attacker does not have an account but has a list of usernames, they can spray AS-REQ packets to see which users return an AS-REP.
```bash
# Using Impacket (GetNPUsers.py) - No credentials needed, just a username list!
GetNPUsers.py domain.local/ -usersfile users.txt -format hashcat -outputfile asreps.txt -dc-ip 192.168.1.10
```
If the attacker already has domain credentials, they can request hashes for all vulnerable accounts in the domain automatically:
```bash
# Using Impacket with credentials
GetNPUsers.py domain.local/jsmith:Password123! -request -format hashcat -outputfile asreps.txt -dc-ip 192.168.1.10
```
Alternatively, using Rubeus on a Windows host:
```cmd
Rubeus.exe asreproast /format:hashcat /outfile:hashes.txt
```

### 4.3 Offline Cracking
The extracted hashes are formatted for Hashcat.
```bash
# Hashcat module 18200 (Kerberos 5, etype 23, AS-REP)
hashcat -m 18200 asreps.txt rockyou.txt -r rules/best64.rule

# For AES-256 (etype 18), use mode 19700
hashcat -m 19700 asreps_aes.txt rockyou.txt
```

## 5. Security Posture and Mitigations
### 5.1 Why does this setting exist?
The `DONT_REQ_PREAUTH` setting is a legacy feature, historically required by older applications, Unix-based systems lacking proper Kerberos support, or specific smart card authentication configurations. In modern AD environments, there is rarely a legitimate business justification for it.

### 5.2 Remediation
The definitive fix is to enable Kerberos pre-authentication for all users.
1. Open Active Directory Users and Computers (ADUC).
2. Navigate to the user's properties -> Account tab.
3. Under Account options, ensure **"Do not require Kerberos preauthentication"** is **UNCHECKED**.
4. Regularly audit AD for any users with `UserAccountControl` containing `0x00400000` via automated PowerShell scripts.

## 6. Detection Engineering
Detecting AS-REP roasting is easier than Kerberoasting because AS-REQ events without pre-authentication are anomalies in modern networks.

### 6.1 Event ID 4768 (A Kerberos authentication ticket (TGT) was requested)
When an AS-REP is successfully requested, Event 4768 is logged on the Domain Controller.
- **Detection Logic**: Monitor Event ID 4768 where:
  - `Pre-Authentication Type` is `0` or blank (indicating no pre-auth was used).
  - `Ticket Encryption Type` is `0x17` (RC4) or `0x12/0x11` (AES), corresponding to the hash format extracted.
  - Exclude known, legitimate legacy service accounts if absolutely necessary, but alert on any standard user or admin account.

### 6.2 Event ID 4771 (Kerberos pre-authentication failed)
If an attacker attempts to roast an account that *does* require pre-authentication, the KDC responds with an error.
- **Detection Logic**: Repeated 4771 events from a single IP, particularly with error code `0x11` (KDC_ERR_PREAUTH_REQUIRED).

### 6.3 Honey Accounts
Create a decoy user account (e.g., `svc_backup_exec`) with a very strong, uncrackable password. Enable "Do not require Kerberos preauthentication" on this account.
Any attempt to request an AS-REP for this account is a guaranteed high-fidelity alert of an active AS-REP Roasting attack on the network.

### 6.4 KQL Query for Detection
```kql
SecurityEvent
| where EventID == 4768
| where PreAuthenticationType == 0 or isempty(PreAuthenticationType)
| project TimeGenerated, AccountName, ClientAddress, TicketEncryptionType
```

## 7. Real-World Case Study
During a recent internal VAPT engagement for a healthcare provider, the testing team utilized an unauthenticated network connection (plugging into a lobby ethernet port). With no domain credentials, the team used `GetNPUsers.py` against a list of 1,000 common names they scraped from the company website. One account, `b.smith`, was configured without pre-authentication. The team retrieved the AS-REP, cracked the RC4 hash using Hashcat in 3 minutes (the password was `Summer2025`), and gained their first set of domain credentials, paving the way for full domain compromise within 48 hours.

## 8. Chaining Opportunities
- **[[12 - Password Spraying Basics and Lockout Policies]]**: If AS-REP roasting fails (e.g., strong password), the targeted accounts might still be susceptible to a long-term password spray.
- **[[14 - Kerberoasting Basics and Identification]]**: Often performed in tandem. An attacker will check for AS-REP roasting, and then move to Kerberoasting once they have a valid TGT.

## 9. Related Notes
- [[12 - Password Spraying Basics and Lockout Policies]]
- [[14 - Kerberoasting Basics and Identification]]
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

During a compromise assessment for a retail company, I sought to escalate my initial unauthenticated access. I had captured a list of valid domain usernames during my passive enumeration phase but lacked passwords. Active Directory provides a unique attack vector called AS-REP Roasting, which targets a specific, often legacy-driven misconfiguration in Kerberos authentication.

**Thought Process:**
By default, Kerberos requires pre-authentication (sending an encrypted timestamp) before the Domain Controller will issue a Ticket Granting Ticket (TGT). However, administrators sometimes disable the "Do not require Kerberos preauthentication" setting for specific service accounts or applications that do not support modern Kerberos flows. If this setting is disabled, anyone can request a TGT for that user. The DC will respond with an AS-REP message containing a chunk of data encrypted with the user's password hash. I could request this offline, requiring zero authentication, and then crack the hash at my leisure.

**Execution:**
 Armed with a text file containing over 1,000 valid domain usernames (`domain_users.txt`), I used Impacket's `GetNPUsers.py` script. This tool automatically requests TGTs for the provided users and parses the responses, looking for accounts where pre-authentication is disabled.
```bash
impacket-GetNPUsers retail.local/ -usersfile domain_users.txt -format hashcat -outputfile asrep_hashes.txt -dc-ip 192.168.100.10
```
The script immediately returned a hit for a user named `svc_scanner`, appending the extracted AS-REP hash string (starting with `$krb5asrep$23$`) to the output file. 

To recover the plaintext password, I transferred the `asrep_hashes.txt` file to my dedicated GPU cracking rig and used Hashcat with a robust wordlist and ruleset.
```bash
hashcat -m 18200 asrep_hashes.txt /usr/share/wordlists/rockyou.txt -r /usr/share/hashcat/rules/best64.rule
```

**Outcome:**
The Hashcat process cracked the AS-REP hash in under 45 minutes, revealing the password `Sc@nn3r!2018`. Because AS-REP Roasting does not require the attacker to send any login failures, the attack completely bypassed the domain's account lockout policies and generated no standard authentication failure logs. The compromised `svc_scanner` account granted me an authenticated foothold, proving that legacy Kerberos configurations present a massive, unauthenticated risk to the entire domain.

