---
tags: [interview, active-directory, qna, scenario]
difficulty: expert
module: "Interview Prep - Active Directory"
topic: "QnA - AD Module 63"
---

# Expert Active Directory Q&A: Kerberoasting

```text
+-------------------+                                  +-------------------+
|                   |           TGS-REQ (SPN)          |                   |
|   Attacker Node   | -------------------------------> | Domain Controller |
|   (Valid TGT)     |                                  |       (KDC)       |
|                   | <------------------------------- |                   |
+-------------------+    TGS-REP (Enc Service Ticket)  +-------------------+
         |
         | Extract Ticket Blob
         v
+-------------------+
|                   |
|   Hashcat / JtR   |  ---> Dictionary Attack / Brute Force
|                   |
+-------------------+
         |
         v
  [Plaintext Password of Service Account]
```

## Formal Technical Questions

### Q1: Explain the fundamental mechanics of Service Principal Names (SPNs). Why are user-associated SPNs targeted in Kerberoasting, while computer-associated SPNs are generally ignored?
**Expert Answer:**
An SPN (Service Principal Name) is a unique identifier for a service instance within Active Directory. It maps a service (like HTTP, MSSQL, or CIFS) to the AD account under which that service runs.
Kerberoasting exploits how the KDC issues Service Tickets. When any authenticated user requests a Ticket Granting Service (TGS) ticket for a specific SPN, the KDC encrypts a portion of that TGS ticket using the long-term key (password hash) of the account associated with that SPN.
We target **User Accounts** with SPNs (Service Accounts) because these accounts are created by human administrators. They often have weak, human-readable passwords that rarely rotate, making them susceptible to offline brute-forcing.
Conversely, **Computer Accounts** (which natively have SPNs like `HOST/MachineName`) have highly complex, randomly generated 120-character passwords that rotate automatically every 30 days. Cracking a TGS ticket encrypted with a Computer Account's hash is computationally infeasible.

### Q2: Dissect the cryptographic structure of the TGS-REP message. Which specific field is vulnerable to offline cracking, and how does the KDC construct it?
**Expert Answer:**
The TGS-REP (Ticket Granting Service Reply) contains two primary components:
1. **The Service Ticket (Ticket):** Intended for the target service.
2. **The Client's encrypted payload:** Encrypted with the Client's TGT session key, containing the new Service Session Key.
The vulnerability lies entirely within the **Service Ticket**. The KDC structures the Service Ticket to include the client's identity, group memberships (PAC - Privilege Attribute Certificate), and the Service Session Key. 
Crucially, the KDC encrypts this entire structure using the target service account's password hash (NTLM/AES key). The attacker requests the ticket but never presents it to the service. Instead, they extract the encrypted `enc-part` of the Service Ticket from the TGS-REP and feed it into a password cracker. The cracker attempts to decrypt the blob using a dictionary of passwords. If the decryption yields a valid ASN.1 structure, the password is correct.

### Q3: Discuss the implications of RC4 (Type 23) versus AES-256 (Type 18) encryption in Kerberoasting. How does an attacker attempt to force a downgrade?
**Expert Answer:**
The encryption algorithm used for the Service Ticket dictates the cracking difficulty.
- **RC4-HMAC (Type 23):** Uses the MD4-based NTLM hash. It is incredibly fast to crack (billions of hashes per second on modern GPUs).
- **AES-256-CTS-HMAC-SHA1-96 (Type 18):** Uses key derivation functions (PBKDF2) with thousands of iterations. Cracking AES Kerberos tickets is exponentially slower and practically impossible unless the password is very weak.
**Downgrade Attacks:** When requesting the TGS via `Rubeus` or `GetUserSPNs.py`, an attacker can modify the TGS-REQ to specify that their client *only* supports RC4. If the target service account's `msDS-SupportedEncryptionTypes` attribute allows RC4 (which is common unless explicitly disabled), the KDC will downgrade the encryption and issue an RC4-encrypted TGS ticket, vastly accelerating the offline cracking process.

## Scenario-Based Questions

### Q4: You are on a Red Team engagement. The environment uses a highly tuned SIEM that strictly monitors and alerts on massive spikes in Event ID 4769 (A Kerberos service ticket was requested). How do you execute Kerberoasting while evading this detection?
**Expert Answer:**
Standard Kerberoasting tools indiscriminately request TGS tickets for *every* SPN in the domain simultaneously. This creates a massive, noisy spike of `4769` events from a single IP address, instantly triggering the SIEM.
To evade this:
1. **Targeted Enumeration:** I will query LDAP for users with SPNs (`userPrincipalName=*` and `servicePrincipalName=*`) but NOT request the tickets yet.
2. **Filtering:** I will filter the list based on high-value targets (e.g., accounts in the `Domain Admins` group or SQL admins).
3. **Slow and Low:** I will manually request a TGS for a single high-value SPN using native Windows tools (e.g., `Add-Type -AssemblyName System.IdentityModel; New-Object System.IdentityModel.Tokens.KerberosRequestorSecurityToken -ArgumentList "MSSQLSvc/db01.local"`) or Rubeus with a delay.
4. **Time Dilution:** I will spread 2-3 targeted requests over a period of days, blending in with legitimate service authentication traffic and staying under the SIEM's volumetric threshold.

### Q5: You compromise a low-privileged user in a forest. You identify a Service Account with an SPN, but it is configured with Unconstrained Delegation. How does this alter your attack path compared to standard Kerberoasting?
**Expert Answer:**
If a service account is configured with Unconstrained Delegation (UD), its value extends far beyond just cracking its password.
Standard Kerberoasting would have me crack the password to access the service. However, UD means that any user authenticating to this service will leave their TGT in the service's memory (LSASS).
Instead of just Kerberoasting, if I can compromise this service account (perhaps its password is weak and I crack it), I can then monitor its memory. I can use techniques like the "Printer Bug" (SpoolSample) or PetitPotam to coerce a high-privileged account (like a Domain Controller machine account) to authenticate to my compromised UD service. The DC's TGT is cached in memory, I extract it, and instantly DCSync the domain. The Kerberoast was merely the gateway to leveraging the UD misconfiguration.

### Q6: You have localized Admin rights on a server, but no domain privileges. You want to perform a Kerberoast, but you do not want to generate network traffic that NDRs might catch. Can you extract Kerberos material from memory to achieve the same result?
**Expert Answer:**
Yes, if I have local Administrator or SYSTEM privileges on a machine, I can extract Kerberos tickets directly from memory (LSASS) using tools like Mimikatz (`sekurlsa::tickets /export`) or Rubeus (`dump`).
Whenever legitimate users or services on that machine request TGS tickets to access other services in the domain, those tickets are cached in memory. By dumping these tickets, I can extract the encrypted Service Ticket blobs locally without generating any new `4769` events or anomalous TGS-REQ network traffic. I then take these dumped `.kirbi` files offline, convert them to Hashcat format using `kirbi2john`, and crack them. This is an entirely passive variation of Kerberoasting.

## Deep-Dive Defensive Questions

### Q7: Explain the specific log parameters in Event ID 4769 that a Blue Team must analyze to differentiate a legitimate TGS request from a malicious Kerberoasting attempt.
**Expert Answer:**
Differentiating malicious requests relies on analyzing the context and cryptography of **Event ID 4769**:
- **Ticket Encryption Type:** Malicious requests often force RC4 downgrades. If the domain usually operates on AES (0x12 or 0x13), a `4769` event with Ticket Encryption Type `0x17` (RC4) is highly suspicious.
- **Service Name anomalies:** Legitimate clients usually request tickets for specific services they are accessing. Kerberoasting tools request tickets for *all* service accounts. A single user requesting tickets for 50 different service names in 1 second is impossible for a human.
- **Failure Code:** `0x0` means success. We look for spikes of `0x0` across multiple distinct SPNs from a single `Client Address`.
- **Client IP Address:** Is the request originating from a standard user workstation, or a segment that shouldn't be bulk-requesting SQL and IIS tickets?

### Q8: What architectural changes can an organization implement to completely neutralize the threat of Kerberoasting without breaking service functionality?
**Expert Answer:**
The ultimate mitigation for Kerberoasting is eliminating the use of human-managed passwords for service accounts.
1. **Group Managed Service Accounts (gMSA):** Transition all compatible services (IIS, SQL, Exchange) to gMSAs. gMSAs are managed by the Domain Controllers. They utilize complex, 120-character passwords that are automatically rotated every 30 days. Kerberoasting a gMSA is possible, but cracking the resulting hash is mathematically impossible.
2. **Enforcing AES Encryption:** Disable RC4 entirely within the domain. Update the `msDS-SupportedEncryptionTypes` on all service accounts to require AES-256. While AES tickets can technically be roasted, the cracking speed drops from billions/second to hundreds/second, making all but the weakest passwords resilient.
3. **Password Policies:** For services that cannot support gMSAs, enforce a separate fine-grained password policy for service accounts requiring 30+ character random strings, effectively replicating the gMSA protection manually.

### Q9: Discuss the deployment and operational mechanics of "Honey SPNs". How do they catch attackers early in the kill chain?
**Expert Answer:**
A Honey SPN is a deceptive Active Directory account designed purely for detection.
1. **Creation:** The Blue Team creates a user account with an attractive name (e.g., `svc_vcenter_admin`).
2. **SPN Assignment:** An arbitrary SPN is registered to the account (e.g., `setspn -s VMWare/vcenter.local svc_vcenter_admin`).
3. **Password:** A massively long, uncrackable password is set.
4. **Monitoring:** An alert is created in the SIEM for any **Event ID 4769** where the `Service Name` equals `svc_vcenter_admin`.
Since this service does not actually exist, no legitimate software or user will ever request a TGS for it. The only way a TGS is requested is if an attacker or automated tool (like BloodHound or Rubeus) runs an LDAP query for all SPNs and bulk-requests tickets. The moment the Honey SPN is requested, a high-fidelity alert is triggered, exposing the compromised workstation's IP address immediately.

## Real-World Attack Scenario
During a Purple Team exercise, the attackers compromised a standard developer workstation. Knowing the SIEM was actively alerting on rapid `4769` spikes, they opted for a targeted approach. They utilized a custom LDAP query to identify user accounts with both an SPN and the string "admin" in their description. They found `svc_sql_maint`. Using Rubeus, they crafted a single TGS-REQ forcing an RC4 downgrade (`/enctype:rc4`). The SIEM recorded a single RC4 ticket request but did not trigger the volumetric alert threshold. The extracted hash was cracked via Hashcat using a rule-based dictionary attack, revealing the password `Autumn2021!`. This account was a member of the Domain Admins group due to a legacy misconfiguration, leading to full domain compromise within 4 hours.

## Chaining Opportunities
- **Kerberoasting + Silver Ticket:** If the Kerberoast is successful and the plaintext password (or NTLM hash) of the service account is obtained, the attacker can forge a Silver Ticket (TGS) to access that service persistently, bypassing the need to interact with the KDC.
- **Kerberoasting + Targeted Ransomware:** Compromising a backup service account via Kerberoasting allows attackers to delete enterprise backups before deploying ransomware.
- **Kerberoasting + Privilege Escalation:** If the roasted service account has administrative rights over other servers, it provides a lateral movement path to systems that might contain Domain Admin tokens.

## Related Notes
- [[01 - Active Directory Basics]]
- [[62 - AS-REP Roasting]]
- [[Silver Ticket Attacks]]
- [[Cryptography - NTLM and Kerberos Algorithms]]
- [[Defensive Security - Active Directory Hardening]]
