---
tags: [interview, api-security, qna, scenario]
difficulty: expert
module: "Interview Prep - API Security"
topic: "QnA - API Module 32"
---

# Broken Authentication (Kerberos and NTLM Infrastructure Attacks)

Authentication protocols form the perimeter of digital identities within enterprise infrastructure. When protocols like Kerberos or NTLM are misconfigured, downgraded, or manipulated, Broken Authentication vulnerabilities arise. These flaws allow attackers to forge identities, bypass access controls, and move laterally without exploiting software vulnerabilities. This module dissects advanced authentication attacks, cryptographic downgrades, and token impersonation.

## Formal Technical Questions

### Q1: Detail the cryptographic flaws in the Kerberos AS-REP response that allow for offline brute-forcing in Broken Authentication attacks.
Kerberos authentication begins with the Authentication Service (AS) exchange. A client sends an AS-REQ to the Key Distribution Center (KDC). If Pre-Authentication is disabled for the user (`DONT_REQUIRE_PREAUTH` flag is set in UserAccountControl), the KDC immediately responds with an AS-REP containing a Ticket Granting Ticket (TGT) and a session key encrypted with the user's password hash.

The broken authentication flaw occurs due to the cryptographic implementation. The encrypted portion of the AS-REP message is signed and encrypted using the target user's long-term key (their NT hash or AES key). Attackers can request this AS-REP on behalf of any user lacking Pre-Auth without knowing their password (AS-REP Roasting). Once the encrypted blob is retrieved, the attacker extracts the `enc-part` and performs an offline dictionary attack using tools like Hashcat (Mode 18200). If the environment allows RC4-HMAC (encryption type 0x17), the brute-forcing is exponentially faster than AES-256 (0x12), leading to rapid plaintext password recovery and complete authentication bypass.

### Q2: How does an attacker abuse NTLM relaying to bypass authentication on LDAP/SMB, and what specific protocol features enable this?
NTLM is a challenge-response authentication protocol that suffers from a fundamental Broken Authentication flaw: it does not cryptographically bind the authentication attempt to the specific service or channel being accessed, unless specific mitigations are enforced.

An attacker performs an NTLM relay attack by positioning themselves between a client and a target server (via LLMNR/NBT-NS poisoning, ARP spoofing, or forced coercion like PetitPotam). 
1. The victim client connects to the attacker machine, initiating NTLM auth.
2. The attacker machine relays the Type 1 (Negotiate) message to the target server.
3. The target server replies with a Type 2 (Challenge) message.
4. The attacker relays the Challenge back to the client.
5. The client encrypts the challenge, producing a Type 3 (Authenticate) message, and sends it to the attacker.
6. The attacker relays the valid Type 3 message to the target server.

Because the challenge was successfully answered using the client's valid hash, the target server authenticates the attacker as the client. This bypasses authentication completely. This is enabled because NTLM lacks mandatory Server Principal Name (SPN) target validation and Channel Binding Tokens (CBT) by default, allowing the authentication context to be lifted and shifted to a different protocol or host (e.g., relaying from SMB to LDAP or HTTP to AD CS).

### Q3: Explain the mechanics of a Pass-the-Ticket (PtT) attack. How does the attacker inject the ticket into the Local Security Authority (LSA) to bypass the authentication boundary?
Pass-the-Ticket (PtT) is a post-exploitation broken authentication technique where an attacker steals a valid Kerberos Ticket Granting Ticket (TGT) or Ticket Granting Service (TGS) ticket and uses it to authenticate to network services without knowing the user's password or hash.

The Local Security Authority (LSA) subsystem within Windows (`lsass.exe`) manages authentication tokens and Kerberos tickets. When a user authenticates, their tickets are stored in the LSA credential cache (memory). 
To execute PtT, the attacker extracts tickets (usually `.kirbi` files) from disk or memory using tools like Mimikatz (`sekurlsa::tickets /export`) or Rubeus (`dump`). To bypass the authentication boundary, the attacker uses an API call like `LsaCallAuthenticationPackage` to interface with the Kerberos authentication package (`KERBEROS_NAME`). The attacker provides the stolen ticket blob, and the LSA injects it directly into the current logon session's credential cache. Subsequent requests to network resources will use this injected ticket within the AP-REQ, and the target service will implicitly trust the authentication because the ticket is cryptographically signed by the KDC, unaware that the physical user never authentically logged in.

## Scenario-Based Questions

### Q1: Red Team Scenario: You found an exposed IIS server with NTLM authentication enabled. How do you chain this with AD CS to achieve domain admin?
**Scenario Context:** NTLM relaying to Active Directory Certificate Services (AD CS) Web Enrollment (ESC8).
**Execution:**
1. I establish an NTLM relay server using `ntlmrelayx.py`, configuring the target as the AD CS web enrollment endpoint (`http://pki.domain.local/certsrv/certfnsh.asp`) and specifying the Web Server or User certificate template.
2. I force the target IIS server (or a Domain Controller) to authenticate to my relay server. I can use coercion techniques like `ShadowCoerce` (MS-FSRVP) or `PetitPotam` (MS-EFSRPC) targeting the machine account of the server.
3. The server connects to my relay via SMB. My relay takes the NTLM authentication and forwards it over HTTP to the AD CS server.
4. Because the HTTP endpoint does not enforce Extended Protection for Authentication (EPA) or require SMB signing, the AD CS server accepts the relayed authentication.
5. `ntlmrelayx` requests a client authentication certificate for the coerced machine account.
6. I receive a Base64 encoded PFX certificate. I use `Rubeus asktgt` or `certipy` with this certificate to request a Kerberos TGT for the coerced machine account (PKINIT). If I coerced a DC, I now have a TGT for the DC and can DCSync the entire domain.

### Q2: Threat Hunting Scenario: You observe multiple Event ID 4769s with RC4 encryption (0x17) requested from a single host for various service accounts. What is happening and how do you confirm?
**Investigation Methodology:**
Event ID 4769 represents a "Kerberos Service Ticket Requested" (TGS-REQ).
1. **Identify the Attack:** A single host rapidly requesting TGS tickets for multiple, distinct Service Principal Names (SPNs), specifically utilizing RC4 encryption (`Ticket Options: 0x40810000` and `Ticket Encryption Type: 0x17`), is the exact signature of a **Kerberoasting** attack. The attacker is requesting service tickets to extract the encrypted payload and brute-force the service account passwords offline.
2. **Confirmation:** I will query the SIEM for Event ID 4769 where `Client Address` matches the anomalous host.
3. I will aggregate the `ServiceName` field. If the count of distinct `ServiceName` values (excluding machine accounts ending in `$`) exceeds a typical threshold (e.g., > 10 distinct services within 1 minute), it is unequivocally an automated Kerberoasting attack using tools like Rubeus or Invoke-Kerberoast.
4. I will also check for RC4 downgrade anomalies. If the domain supports AES (0x12), but the attacker explicitly requested RC4 to make cracking easier, this confirms malicious intent.

### Q3: Incident Response: A domain controller's KRBTGT account hash was compromised. Walk me through the remediation and the forensic artifacts of Golden Ticket usage.
**Remediation (The Double Reset):**
The KRBTGT account hash is the root cryptographic key for the domain's Kerberos infrastructure. Compromise means the attacker can forge Golden Tickets (TGTs) with arbitrary lifetimes and privileges.
1. To remediate, the KRBTGT password must be reset **twice**. 
2. The KDC maintains the current password and the previous password (to allow for replication latency and ticket renewal). 
3. Resetting it once invalidates the *current* keys, but the attacker's Golden Ticket might still work using the *previous* keys. Resetting it a second time (allowing for sufficient replication time between DCs before the second reset) pushes the compromised key out of the history, completely invalidating all forged tickets.

**Forensic Artifacts:**
- **Event ID 4624 (Logon):** Look for Logon Type 3 (Network). Anomalous Golden Tickets often have missing or mismatched Account Domain fields, or the `TargetUserName` might be an account that doesn't exist.
- **Ticket Lifetimes:** Legitimate TGTs adhere to the domain's MaxTicketAge policy (default 10 hours). Golden Tickets generated by Mimikatz historically defaulted to 10 years. Extracting tickets from RAM on compromised endpoints and checking the `EndTime` field is a dead giveaway.
- **Event ID 4769 (TGS Request):** A Golden Ticket is used to request TGS tickets. If the TGT used was forged offline, the DC has no record of the initial AS-REQ (Event ID 4768) for that user's session. A 4769 without a preceding 4768 for the same user logon ID is highly suspicious.

## Deep-Dive Defensive Questions

### Q1: Design a comprehensive detection strategy for Silver Tickets bypassing local authentication.
**Architecture Design:**
A Silver Ticket is a forged TGS ticket. The attacker uses the compromised NTLM hash of a *target service account* (e.g., a SQL server or CIFS share) to forge a ticket. The DC is never contacted; the ticket is presented directly to the service.
1. **PAC Validation Configuration:** Enforce strict Privilege Attribute Certificate (PAC) validation. When a service receives a TGS, it must verify the PAC signature with the Domain Controller (via NETLOGON). If the Silver Ticket was forged without the KRBTGT hash, the PAC signature will be invalid.
2. **Endpoint Logging:** Monitor Event ID 4624 on target servers. Focus on Logon Type 3.
3. **Kerberos Anomaly Detection:** Silver Tickets often contain flawed fields. Correlate the `SubjectUserName` in the 4624 event against the domain user database. Attackers often forge tickets for high-privileged users (e.g., `Administrator`) that may not actually be actively logging into that specific SQL server.
4. **EDR Hooks:** Utilize EDR telemetry to monitor process injection targeting the LSASS process space, specifically tracking `LsaCallAuthenticationPackage` API calls which are necessary to inject the forged ticket into the local cache.

### Q2: How do you enforce Channel Binding and Extended Protection for Authentication (EPA) across an enterprise to mitigate NTLM broken authentication?
**Implementation Strategy:**
1. **Audit Mode First:** NTLM modifications will break legacy applications. Enable EPA in audit-only mode across IIS, Exchange, and LDAP infrastructure. Review Event ID 4624 (NTLM auditing) to identify services failing channel binding checks.
2. **LDAP Signing and Channel Binding:** Configure the Group Policy "Domain controller: LDAP server channel binding token requirements" to `Always`. This mitigates LDAP relay attacks.
3. **IIS Extended Protection:** In IIS Manager, under Authentication -> Windows Authentication -> Advanced Settings, set "Extended Protection" to `Require`. This binds the outer TLS channel securely to the inner NTLM authentication, ensuring the challenge cannot be relayed from an unencrypted or differently-encrypted channel.
4. **SMB Signing:** Enforce SMB Signing via GPO (`Microsoft network server: Digitally sign communications (always)`) to prevent NTLM relaying to SMB endpoints, rendering the relayed authentication useless.

### Q3: Discuss the structure of the Privilege Attribute Certificate (PAC) and how modern Windows versions (e.g., PAC Signatures) attempt to prevent authentication bypasses.
The PAC is a proprietary Microsoft extension to the Kerberos protocol, embedded within the `authorization-data` field of the ticket. It contains the user's Group SIDs, User SID, logon times, and password policies. This is how Windows enforces authorization post-authentication.

To prevent tampering (Broken Authentication/Forged Authorization), the PAC contains two cryptographic signatures:
1. **Server Signature:** Signed with the long-term key of the target service account.
2. **KDC Signature:** Signed with the KRBTGT key.

Modern mitigations (such as those introduced for CVE-2021-42287 and CVE-2022-37967, "PAC Signatures"):
Microsoft introduced the **Ticket Signature** and the **Full PAC Signature**. Previously, attackers could forge a PAC, encrypt it with a known service key, and bypass the KDC. Now, Windows strictly enforces that the PAC must contain a signature validating the routing and request path of the ticket, signed by the KRBTGT. Furthermore, the KDC issues a specific signature validating the original requester. If a service receives a ticket without these modern PAC signatures (or if the signatures fail cryptographic verification), the authentication request is instantly rejected, effectively killing traditional Silver Ticket and Bronze Ticket attacks.

## Custom ASCII Diagram

```text
+-----------------------------------------------------------------------------------------+
|                    Kerberos TGT/TGS Flow & Broken Auth (Kerberoasting)                  |
|                                                                                         |
| [Attacker/Client]                                                  [Key Distribution]   |
|       |                                                             [Center (DC)]       |
|       | 1. AS-REQ (Request TGT for Attacker Account)                      |             |
|       |------------------------------------------------------------------>|             |
|       |                                                                   |             |
|       | 2. AS-REP (Contains TGT encrypted with KRBTGT)                    |             |
|       |<------------------------------------------------------------------|             |
|       |                                                                   |             |
|       | 3. TGS-REQ (Request Ticket for target SPN: MSSQLSvc/db.local)     |             |
|       |    * Attacker explicitly requests RC4 (0x17) encryption           |             |
|       |------------------------------------------------------------------>|             |
|       |                                                                   |             |
|       | 4. TGS-REP (Contains Service Ticket encrypted with Target Hash)   |             |
|       |<------------------------------------------------------------------|             |
|       |                                                                                 |
|       +--------------------------------------------------------+                        |
|       | Offline Brute-Force Phase (Broken Authentication)      |                        |
|       |--------------------------------------------------------|                        |
|       | a. Extract Service Ticket from memory (Rubeus)         |                        |
|       | b. Pass to Hashcat / John The Ripper                   |                        |
|       | c. Brute-force RC4-HMAC to recover plaintext password  |                        |
|       | d. Gain access to Service Account (Potential DA)       |                        |
|       +--------------------------------------------------------+                        |
+-----------------------------------------------------------------------------------------+
```

## Real-World Attack Scenario

In a recent engagement against a large healthcare provider, the Red Team leveraged a chained Broken Authentication attack against legacy infrastructure. Initial access was gained via an unprotected network jack in a clinic waiting room. The attacker initiated an LLMNR poisoning attack using Responder.

Within minutes, an IT administrator's laptop, attempting to resolve a mistyped file share name, fell victim to the poison. The laptop automatically attempted to authenticate to the attacker's rogue SMB server using NTLMv2.

Instead of cracking the NTLMv2 hash offline (which was highly complex and resisted brute-forcing), the attacker utilized NTLM relaying. They relayed the incoming SMB authentication directly to the primary Domain Controller's LDAP interface (`ldap://dc01.med.local`). Because the domain had not enforced LDAP signing or Channel Binding, the Domain Controller accepted the relayed authentication as the IT Administrator.

Operating within the context of the Domain Admin via the relayed session, the attacker executed a malicious LDAP modify command to create a new Domain Admin account. The entire authentication mechanism was bypassed without ever needing to crack a password, demonstrating a critical failure in the environment's authentication perimeter protocols.

## Chaining Opportunities

- **Broken Authentication to Object Level Abuse:** Relaying NTLM authentication to LDAP to modify the DACL of an object, granting the attacker `GenericAll` over a sensitive group.
- **Broken Authentication to Unrestricted Resource Consumption:** Forging thousands of Kerberos AS-REQ requests with invalid timestamps to trigger account lockouts across the entire domain, causing a massive denial of service.
- **Broken Authentication to Function Level Bypasses:** Using a Pass-the-Ticket attack to access a server via RPC, and then leveraging a named pipe impersonation vulnerability (Function Level) to escalate from the relayed user context to SYSTEM on the host.

## Related Notes
- [[Kerberos Internals and Cryptography]]
- [[NTLM Authentication Flow and Relaying]]
- [[Active Directory Certificate Services (AD CS) Abuse]]
- [[Pass-the-Ticket and LSA Memory Structures]]
- [[Privilege Attribute Certificate (PAC) Validation]]
- [[Extended Protection for Authentication (EPA)]]
