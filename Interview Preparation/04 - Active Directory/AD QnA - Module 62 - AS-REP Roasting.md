---
tags: [interview, active-directory, qna, scenario]
difficulty: expert
module: "Interview Prep - Active Directory"
topic: "QnA - AD Module 62"
---

# Expert Active Directory Q&A: AS-REP Roasting

```text
+-------------------+                                  +-------------------+
|                   |           AS-REQ (No Pre-Auth)   |                   |
|   Attacker Node   | -------------------------------> | Domain Controller |
|                   |                                  |       (KDC)       |
|                   | <------------------------------- |                   |
+-------------------+    AS-REP (Encrypted TGT Blob)   +-------------------+
         |
         | Capture Encrypted Blob
         v
+-------------------+
|                   |
|   Hashcat / JtR   |  ---> Dictionary Attack / Brute Force
|                   |
+-------------------+
         |
         v
  [Plaintext Password]
```

## Formal Technical Questions

### Q1: Dissect the mechanics of Kerberos Pre-Authentication. Why exactly does the "Do not require Kerberos preauthentication" (DONT_REQ_PREAUTH) flag introduce a vulnerability?
**Expert Answer:**
Kerberos Pre-Authentication is a security mechanism designed to prevent offline password guessing. In a standard AS-REQ (Authentication Service Request), the client encrypts a timestamp using their password hash (NTLM/AES key) and sends it to the Key Distribution Center (KDC). The KDC decrypts this timestamp. If successful, it proves the client knows the password *before* the KDC issues the Ticket Granting Ticket (TGT).
When the `DONT_REQ_PREAUTH` flag (UserAccountControl attribute bit `4194304`) is set on an account, the KDC bypasses this validation step. An attacker can send a spoofed AS-REQ for that user without knowing the password. The KDC responds with an AS-REP containing the TGT. 
Crucially, a portion of the AS-REP message—specifically, the session key used to protect the TGT—is encrypted with the user's password hash. Because the attacker receives this encrypted blob without ever authenticating, they can extract it and perform an offline brute-force attack to recover the plaintext password.

### Q2: Detail the cryptographic structure of the AS-REP encrypted blob. How does it differ fundamentally from the blob cracked in a Kerberoasting attack?
**Expert Answer:**
In AS-REP Roasting, the target of the offline crack is the encrypted part of the `AS-REP` message (specifically, the `enc-part` of the AS-REP, which contains the TGT session key and logon data). This blob is encrypted using the client user's long-term key (their password hash). 
In contrast, Kerberoasting targets the `TGS-REP` message. The vulnerable component is the Service Ticket itself, which is encrypted using the long-term key of the *Service Account* (the SPN owner), not the requesting user.
Therefore:
- **AS-REP Roasting** attacks the *User's* password hash. It requires no initial domain credentials (if querying blindly) and targets the AS exchange.
- **Kerberoasting** attacks the *Service Account's* password hash. It requires a valid TGT (any valid domain user) to request a TGS and targets the TGS exchange.

### Q3: Explain the role of encryption types (enctypes) in Kerberos. How can an attacker manipulate the AS-REQ to force a downgrade to a weaker algorithm like RC4 (Type 23)?
**Expert Answer:**
Active Directory supports multiple encryption types, most notably RC4-HMAC (Type 23) and AES-128/AES-256 (Types 17 and 18). AES is significantly stronger and harder to crack offline than RC4.
When an attacker crafts an AS-REQ, they specify a list of supported encryption types in the request body. If the KDC and the target account support the requested enctype, the KDC will use it to encrypt the AS-REP blob.
To force a downgrade, an attacker simply modifies the AS-REQ to *only* advertise support for RC4 (Type 23). If the target account's `msDS-SupportedEncryptionTypes` attribute allows RC4 (which is common for backwards compatibility), the KDC complies and returns an RC4-encrypted AS-REP. This is highly advantageous for the attacker, as RC4 hashes crack exponentially faster in Hashcat compared to AES.

## Scenario-Based Questions

### Q4: You are on a Red Team engagement. You have plugged a rogue device into the network (physical access) but you have zero domain credentials. How do you identify and roast AS-REP vulnerable accounts?
**Expert Answer:**
Without domain credentials, I cannot perform authenticated LDAP queries to search for the `userAccountControl:1.2.840.113556.1.4.803:=4194304` filter. I must operate blindly or passively.
1. **Passive Reconnaissance:** I can listen to broadcast traffic (LLMNR/NBT-NS) or capture unencrypted LDAP traffic on the wire. Sometimes scripts or services transmit user lists in plaintext.
2. **Username Enumeration:** I will use anonymous LDAP binding (if permitted) or RPC null sessions to pull the domain user list. If those are blocked, I can use Kerberos username enumeration via `Kerbrute`. By sending AS-REQ packets for a dictionary of usernames, the KDC responds with `KDC_ERR_PREAUTH_REQUIRED` for valid users, and `KDC_ERR_C_PRINCIPAL_UNKNOWN` for invalid ones.
3. **Blind Roasting:** Once I compile a valid list of usernames, I use Impacket's `GetNPUsers.py` with the `-no-pass` flag and the username list. The tool loops through the list, requests a TGT for each without pre-auth, and automatically captures the AS-REP hash for any account configured with `DONT_REQ_PREAUTH`.

### Q5: You successfully execute an AS-REP roast against a high-value target (e.g., a Database Administrator), but your offline cracking rig indicates the hash will take 10 years to crack due to a high-entropy password policy. What are your alternative attack paths?
**Expert Answer:**
If the password cannot be cracked, the AS-REP hash itself is largely useless for lateral movement (you cannot pass the AS-REP hash directly). The attack path must pivot.
1. **Targeted Disruption (Risky):** I know the username exists. I could intentionally lock out the account via password spraying, potentially forcing a helpdesk interaction that I could intercept or socially engineer.
2. **Re-Evaluating the Account:** I would pivot back to enumeration. Does this DBA account have an SPN? If so, I could attempt Kerberoasting, though it would likely have the same complex password. 
3. **Alternative Avenues:** I must abandon the AS-REP crack and look elsewhere in the domain. I would hunt for SMB shares, exposed web interfaces, or other vulnerabilities like SMB relaying or exploiting legacy systems where the DBA might have left a session, allowing me to steal a token instead of cracking the password.

### Q6: Compare the OPSEC considerations of executing AS-REP roasting from a compromised Windows workstation using Rubeus versus pivoting traffic to an attacker-controlled Linux machine using Impacket.
**Expert Answer:**
- **Windows (Rubeus):** Executing `Rubeus asreproast` on a compromised endpoint is highly effective but risky. Rubeus is written in C# and is heavily fingerprinted by EDRs (like Microsoft Defender for Endpoint). Running it requires either dropping the binary to disk (high risk) or executing it in-memory via reflective injection or BOFs (medium risk, but AMSI/ETW might still catch it). However, it blends well with native Kerberos traffic patterns.
- **Linux (Impacket):** Using `GetNPUsers.py` through a SOCKS proxy (e.g., Chisel) moves the execution off the endpoint. The compromised Windows machine only acts as a network router. This entirely bypasses local EDR memory scanning, AMSI, and ETW. The downside is that Impacket's Kerberos implementation can sometimes be fingerprinted at the network layer (e.g., anomalies in packet structure compared to the native Windows Kerberos client), which a sophisticated NDR (Network Detection and Response) solution might flag.

## Deep-Dive Defensive Questions

### Q7: How can a SOC dynamically detect AS-REP roasting in real-time? Specify the exact Event IDs and parameters to monitor.
**Expert Answer:**
AS-REP roasting generates highly specific Windows Security Event logs on the Domain Controllers.
The primary event to monitor is **Event ID 4768: A Kerberos authentication ticket (TGT) was requested**.
To differentiate a legitimate AS-REQ from an AS-REP roast, analysts must filter for:
- `Pre-Authentication Type: 0` (This indicates pre-auth was bypassed).
- `Ticket Options: 0x40810010` (Standard for Impacket/Rubeus requests).
- `Ticket Encryption Type: 0x17` (RC4). If the domain predominantly uses AES, a sudden spike in RC4 AS-REQs is a massive anomaly.
Additionally, monitoring for a single source IP address requesting TGTs for multiple different users with Pre-Auth Type 0 in a short time frame is a high-confidence indicator of an automated tool like `GetNPUsers.py`.

### Q8: Explain the concept of "HoneyTokens" in the context of AS-REP roasting and how they can act as an early warning system.
**Expert Answer:**
A HoneyToken is a deceptive AD account specifically crafted to lure attackers. 
To build an AS-REP HoneyToken, the Blue Team creates a fake, highly attractive user account (e.g., `svc_sql_admin` or `admin_backup`). 
1. They set a massive, uncrackable 128-character password.
2. They enable the "Do not require Kerberos preauthentication" flag.
3. They set aggressive alerting in the SIEM for any **Event ID 4768** involving this specific account.
Since this account has no legitimate business purpose, it will never legitimately request a TGT. If an attacker runs `Rubeus` or `GetNPUsers.py` across the domain, they will inevitably pull the AS-REP hash for this HoneyToken. The moment the KDC generates the AS-REP, the SIEM fires an alert, instantly notifying the SOC of a Kerberos-based attack phase, including the source IP of the compromised machine.

### Q9: What are the root causes for the "Do not require Kerberos preauthentication" flag being enabled in enterprise environments, and how do you systematically audit and remediate it?
**Expert Answer:**
The root cause is almost always legacy application compatibility. Certain older applications, mainframes, or third-party UNIX integrations that rely on outdated Kerberos stacks do not support the Pre-Authentication exchange natively. Administrators enable this flag as a quick fix to get the application to authenticate.
**Auditing:** 
Use PowerShell to query LDAP for accounts with this flag:
```powershell
Get-ADUser -Filter {DoesNotRequirePreAuth -eq $true} -Properties DoesNotRequirePreAuth
```
**Remediation:**
1. **Identify Business Need:** Trace where the account is used. If it's an old service, evaluate if it can be upgraded to support modern Kerberos.
2. **Disable the Flag:** Uncheck "Do not require Kerberos preauthentication" in ADUC.
3. **If unavoidable:** If the application strictly requires it, mitigate the risk by ensuring the account has a complex, 30+ character randomly generated password that rotates frequently. Restrict the account's logon hours and lateral movement capabilities using Windows Firewall and strict ACLs so that even if cracked, the blast radius is minimal.

## Real-World Attack Scenario
During an objective-based Red Team engagement, the team gained initial access via a phishing payload that executed on a standard user's machine. The network was highly monitored, and running BloodHound was deemed too risky. The operator initiated a SOCKS proxy and executed `GetNPUsers.py -no-pass` using a curated list of common service account names. 
The KDC returned an AS-REP hash for `svc_jenkins_deploy`. The hash was extracted and sent to a GPU cracking rig. Because the service account password had not been changed in 5 years and was derived from the company name (`CompanyName2018!`), Hashcat cracked the RC4 hash in under 4 minutes. The team used this plaintext credential to access the Jenkins deployment server, extract SSH keys, and pivot into the restricted production AWS environment, achieving full objective compromise without ever triggering endpoint EDR alerts.

## Chaining Opportunities
- **AS-REP Roasting + Pass the Hash (PtH):** Once the plaintext password is cracked, the NTLM hash can be generated and used for PtH to move laterally without triggering plaintext credential detections.
- **AS-REP Roasting + LDAP Enumeration:** The cracked credential can be used to perform deep authenticated LDAP queries to map the domain and identify Tier-0 attack paths.
- **Targeted AS-REP Roasting via ACL Abuse:** If an attacker has `GenericWrite` over an account, they can manually enable the `DONT_REQ_PREAUTH` flag via PowerView, roast the hash, crack it, and gain the user's password, effectively bypassing the need to reset the password and alert the user.

## Related Notes
- [[01 - Active Directory Basics]]
- [[61 - AD Enumeration and BloodHound]]
- [[63 - Kerberoasting]]
- [[Cryptography - NTLM and Kerberos Algorithms]]
- [[Defensive Security - Active Directory Hardening]]
