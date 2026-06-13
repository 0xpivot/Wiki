---
tags: [interview, network-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Network Security"
topic: "QnA - Network Module 51"
---

# Network QnA - Module 51 - Kerberos Network Level Attacks

## Custom ASCII Diagram: Kerberos Authentication Flow
```text
       [Client Workstation]                                  [Key Distribution Center (KDC)]
                |                                                           |
                |------------------ 1. AS-REQ (KRB_AS_REQ) ---------------->|
                |          Timestamp encrypted with User NTLM Hash          |
                |                                                           |
                |<----------------- 2. AS-REP (KRB_AS_REP) -----------------|
                |   Ticket Granting Ticket (TGT) + Session Key (Encrypted)  |
                |                                                           |
                |----------------- 3. TGS-REQ (KRB_TGS_REQ) --------------->|
                |   TGT + Authenticator + Service Principal Name (SPN)      |
                |                                                           |
                |<---------------- 4. TGS-REP (KRB_TGS_REP) ----------------|
                |    Service Ticket (Encrypted with SPN Hash) + Session Key |
                |                                                           |
                v                                                           v
      [Target Service Server] <----- 5. AP-REQ (KRB_AP_REQ) ------- [Client Workstation]
                                (Service Ticket + Authenticator)
```

## Formal Technical Questions

### Q1: Detail the cryptographic weaknesses exploited in AS-REP Roasting. Why does this attack not require network interception, and what exact cryptographic data is extracted?
**Answer:**
AS-REP Roasting exploits a specific configuration anomaly in Active Directory user accounts, namely the `DONT_REQ_PREAUTH` flag (represented by the UserAccountControl value 0x410000). 
Normally, during the Authentication Service Request (AS-REQ) phase, Kerberos enforces Pre-Authentication to prevent offline password guessing. The client must encrypt a timestamp using their password hash (RC4 or AES). The KDC validates this timestamp before issuing the Ticket Granting Ticket (TGT) in the AS-REP.
However, when `DONT_REQ_PREAUTH` is enabled, the KDC bypasses this validation entirely. An attacker can send a spoofed AS-REQ for the target user without possessing any credentials. The KDC responds immediately with an AS-REP.
The core vulnerability is cryptographic: a segment of the AS-REP message (the user's session key) is encrypted using the target user's long-term key (their password hash). The attacker isolates this encrypted block from the network packet and extracts it. Using offline brute-forcing tools like Hashcat (mode 18200) or John The Ripper, the attacker subjects the encrypted blob to dictionary attacks. If the password is weak, the hash is cracked.
Crucially, this does not require an On-Path (Man-in-the-Middle) position. The KDC directly routes the AS-REP to the attacker's IP address because the attacker originated the unauthenticated AS-REQ packet.

### Q2: Explain the mechanics of a Kerberoasting attack at the packet level. Which specific ticket is compromised, and what is the underlying encryption flaw that enables offline cracking?
**Answer:**
Kerberoasting targets the Ticket Granting Service (TGS) phase of the Kerberos exchange. Its success relies on the fundamental Kerberos principle that any authenticated domain user holds the right to request a Service Ticket for any Service Principal Name (SPN) registered within the Active Directory environment.
At the packet level, the sequence is:
1. The attacker, possessing a valid TGT for a low-privileged user, sends a `KRB_TGS_REQ` (identifiable by Event ID 4769) to the KDC. In this packet, they specify the target SPN (e.g., `MSSQLSvc/sql.corp.local:1433`).
2. The KDC processes the request, verifying the TGT. It then generates the Service Ticket. The encryption flaw lies here: the Service Ticket itself is encrypted using the password hash of the Active Directory account linked to the SPN. 
3. The KDC sends the `KRB_TGS_REP` back to the attacker.
The attacker never actually connects to the target service. Instead, they extract the encrypted Service Ticket from the `KRB_TGS_REP`. Service accounts often utilize RC4 encryption (Type `0x17`) due to legacy compatibility, though AES (Type `0x12` or `0x13`) can also be targeted. The attacker subjects this encrypted ticket to offline brute-forcing (Hashcat mode 13100). The vulnerability is systemic: the encryption strength of the entire service authentication mechanism rests solely on the entropy of the service account's password, which are notoriously rarely rotated and highly privileged.

### Q3: Contrast Unconstrained Delegation with Constrained Delegation. From an attacker's perspective, how does the exploitation path and post-exploitation impact differ significantly?
**Answer:**
Delegation is a mechanism allowing a front-end service to impersonate a user when accessing back-end network resources.
**Unconstrained Delegation:**
- **Mechanism:** When a user authenticates to a server configured with Unconstrained Delegation, the KDC embeds the user's forwardable TGT directly inside the AP-REQ. The server extracts this TGT and caches it in its Local Security Authority Subsystem Service (LSASS) memory.
- **Exploitation:** If an attacker achieves local administrator privileges on a server with Unconstrained Delegation, they can leverage tools like Mimikatz or Rubeus to scrape LSASS and extract all cached TGTs. The impact is catastrophic: if a Domain Administrator connects to this server (e.g., via RDP, SMB, or even Print Spooler coercion), the attacker steals their TGT and achieves immediate, full domain compromise.

**Constrained Delegation:**
- **Mechanism:** Designed to adhere to least privilege, Constrained Delegation utilizes Kerberos extensions: Service for User to Proxy (S4U2Proxy) and Service for User to Self (S4U2Self). It restricts the front-end server, allowing it to impersonate users *only* to explicitly defined target SPNs (configured via the `msDS-AllowedToDelegateTo` attribute).
- **Exploitation:** The attacker cannot extract universal, forwardable TGTs from memory. Instead, upon compromising the front-end service, the attacker abuses the `S4U2Self` extension to obtain a forwardable TGS for an arbitrary user (including Domain Admins) to the compromised service itself. Then, leveraging `S4U2Proxy`, the attacker forwards this ticket to the KDC to request a ticket for the specific backend service on behalf of the arbitrary user. The impact is geographically limited to the explicitly allowed SPNs, preventing immediate domain-wide compromise unless Resource-Based Constrained Delegation (RBCD) vulnerabilities provide a pivot.

### Q4: Explain the difference between a Golden Ticket and a Silver Ticket. Which requires interaction with the KDC?
**Answer:**
**Golden Ticket:**
A Golden Ticket is a forged Ticket Granting Ticket (TGT). To forge it, an attacker must have previously compromised the Domain Controller and extracted the password hash of the `krbtgt` account. Because the `krbtgt` hash is used by the KDC to encrypt all TGTs, possessing it allows the attacker to forge a TGT for any user, with any group memberships (including Domain Admins), and any lifetime. 
*KDC Interaction:* A Golden Ticket requires interacting with the KDC. The attacker presents the forged TGT to the KDC to request a Service Ticket (TGS-REQ).

**Silver Ticket:**
A Silver Ticket is a forged Service Ticket (TGS). To forge it, the attacker only needs the password hash of a specific target service account (e.g., an MS-SQL service or a specific computer account), often obtained via Kerberoasting. The attacker forges a TGS granting themselves administrative rights to that specific service.
*KDC Interaction:* A Silver Ticket requires zero interaction with the KDC. The attacker injects the forged TGS directly into their session and presents it to the target service (AP-REQ). The KDC is completely bypassed, making Silver Tickets exceptionally stealthy and difficult to detect via standard Event Logging.

## Scenario-Based Questions

### Q5: You are on a Red Team engagement and have compromised a standard domain user workstation. You perform Kerberoasting to extract service tickets, but you notice all returned tickets are encrypted with AES-256 (Encryption Type 0x12), and your brute-forcing attempts fail completely. How do you pivot to forcefully downgrade the encryption to RC4?
**Answer:**
If the domain enforces AES (encryption type 18 for AES-256-CTS-HMAC-SHA1-96), brute-forcing offline is computationally infeasible unless the underlying password is exceptionally weak. 
However, unless the domain administrators have explicitly eradicated RC4 via Group Policy ("Network security: Configure encryption types allowed for Kerberos"), a Kerberos downgrade attack is viable.
1. **Targeting the TGS-REQ:** I will construct a raw, custom `KRB_TGS_REQ` packet using advanced frameworks like Rubeus or a highly modified Impacket `GetUserSPNs.py` script. Within the request structure, I will specifically modify the `Encryption Types` (Etype) field located in the `req-body`. I will strip out the AES support flags completely and specify *only* `RC4-HMAC` (Type 0x17).
2. **KDC Response Mechanics:** Because the Active Directory environment still supports RC4 for backward compatibility with legacy systems, the KDC will accept the downgraded request. It will generate the Service Ticket and encrypt it using the target service account's RC4 hash instead of the AES key.
3. **Extraction and Cracking:** The KDC returns the `KRB_TGS_REP`. I extract the much weaker RC4-encrypted ticket and subject it to Hashcat (mode 13100), effectively bypassing the AES encryption policy entirely and successfully retrieving the plaintext credential.

### Q6: You are on a Red Team engagement and discover a machine with Unconstrained Delegation enabled. You monitor the host but cannot organically convince a highly privileged administrator to log in interactively. How do you engineer a scenario to forcefully capture a highly privileged TGT?
**Answer:**
To exploit Unconstrained Delegation without relying on passive, organic logons, I must actively coerce a high-value target (such as a Primary Domain Controller) to authenticate against my compromised host. I will utilize coercion protocols like MS-RPRN (Printer Bug) or MS-EFSRPC (PetitPotam).
1. **Establish Active Monitoring:** On the compromised machine featuring Unconstrained Delegation, I will deploy Rubeus in monitoring mode to aggressively scrape new tickets from LSASS: `Rubeus.exe monitor /interval:1`.
2. **Execute Coercion Attack:** Operating from a separate pivot machine or via an established C2 channel, I will trigger the coercion. For example, using the SpoolSample exploit against the Domain Controller: `SpoolSample.exe <Domain-Controller-IP> <Compromised-Unconstrained-IP>`.
3. **Capture the TGT:** The Domain Controller's Print Spooler service, operating as the highly privileged `SYSTEM` account (which maps to the DC's machine account `DC$`), will attempt to authenticate back to the Unconstrained machine. Because the target machine has Unconstrained Delegation, the DC securely embeds its own forwardable TGT within the authentication payload.
4. **Pass-the-Ticket and DCSync:** Rubeus intercepts this authentication and extracts the base64-encoded TGT for `DC$`. I immediately inject this ticket into my current session memory (`Rubeus.exe ptt /ticket:<base64-string>`). Operating under the context of the Domain Controller's machine account, I execute a DCSync attack via Mimikatz or Impacket to remotely dump the entire NTDS.dit database, achieving total domain supremacy.

### Q7: You've extracted a user's NTLM hash via an SMB relay attack but cannot crack it. You need to access a specific Kerberized service (e.g., MSSQL) that does not accept NTLM authentication. How do you proceed?
**Answer:**
This scenario requires transitioning from NTLM authentication to Kerberos authentication without knowing the plaintext password. The technique required is Overpass-the-Hash (also known as Pass-the-Key).
1. **The Overpass Process:** I will use the compromised NTLM hash (or AES key, if obtained) to request a valid Kerberos Ticket Granting Ticket (TGT) directly from the KDC. Tools like Mimikatz (`sekurlsa::pth`) or Rubeus (`asktgt`) facilitate this. 
2. **Execution:** Using Rubeus, the command would be `Rubeus.exe asktgt /user:<Username> /rc4:<NTLM_Hash> /ptt`. Rubeus crafts an AS-REQ packet, encrypting the timestamp using the provided NTLM hash (RC4 key). 
3. **KDC Validation:** The KDC receives the AS-REQ, decrypts the timestamp using its copy of the user's hash, and validates it. It then returns a legitimate TGT in the AS-REP.
4. **Accessing the Service:** With the TGT successfully injected into my logon session memory (`/ptt`), the Windows OS natively handles the rest. When I attempt to access the MSSQL service, Windows automatically requests a TGS using the forged TGT and authenticates seamlessly via Kerberos, completely bypassing the need for the plaintext password.

## Deep-Dive Defensive Questions

### Q8: How do you architect a robust detection mechanism for Overpass-the-Hash (Pass-the-Key) attacks using Windows Event Logs? Be highly specific regarding Event IDs and required telemetry correlation.
**Answer:**
Detecting Overpass-the-Hash requires identifying the unnatural injection of cryptographic keys to generate an AS-REQ. I would construct a detection logic pipeline monitoring the following telemetry points:
1. **Event ID 4624 (Successful Logon) Analysis:** Focus heavily on Logon Type 9 (NewCredentials). Attackers utilizing tools like Mimikatz explicitly create a new logon session using Logon Type 9 to safely hold the injected NTLM hash or AES keys without corrupting the current session.
2. **Event ID 4768 (A Kerberos authentication ticket (TGT) was requested):** This is the foundational indicator. Detection requires correlating the `Client Address` and `User` fields. If a TGT is suddenly requested for an administrative account (e.g., `Domain Admin`) from an IP address mapped to a standard user workstation (rather than a dedicated Admin Jump Server), it represents a high-fidelity anomaly.
3. **Encryption Type Anomalies:** Within Event 4768, closely monitor the `Ticket Encryption Type` field. If the enterprise environment natively defaults to AES-256 (0x12) for all Kerberos transactions, but an AS-REQ suddenly surfaces requesting RC4 (0x17), it strongly implies an attacker is utilizing a tool like Rubeus to attempt an Overpass-the-Hash attack using an older, captured NTLM hash instead of the AES key.
4. **Logon ID Mismatch Correlation:** Attackers injecting keys typically do so within a session spawned by a completely different underlying user. Correlating the `Subject Logon ID` found in Event 4768 with the originating `Logon ID` in Event 4624 can reveal this impersonation anomaly, triggering a high-priority alert.

### Q9: Explain the architectural concept of Kerberos FAST (Flexible Authentication Secure Tunneling), also known as Kerberos Armoring. How does this protocol extension natively mitigate AS-REP Roasting?
**Answer:**
Kerberos FAST (defined in RFC 6113) establishes a protected, encrypted tunnel between the client endpoint and the Key Distribution Center (KDC) to encapsulate the vulnerable AS-REQ and AS-REP exchanges.
In a legacy Kerberos environment without FAST, the AS-REQ and AS-REP packets are transmitted largely in plaintext, leaving them highly susceptible to offline dictionary attacks (AS-REP Roasting) and spoofing.
When FAST is implemented and enforced:
1. **Tunnel Establishment:** The client endpoint first authenticates the machine itself to the KDC, utilizing the computer account's existing TGT. This establishes an encrypted, secure tunnel.
2. **Encapsulation:** The user's actual AS-REQ payload is wrapped inside an AP-REQ (utilizing the machine's session key) and transmitted entirely within this secure tunnel.
3. **Secure Delivery:** The KDC processes the AS-REQ and transmits the AS-REP back to the client, encrypted securely within the same tunnel framework.
**Mitigation of AS-REP Roasting:**
Because an attacker operating on the network or from an unmanaged device does not possess the legitimate machine account's TGT or session key, they are fundamentally incapable of establishing the FAST tunnel. If the Domain Controller is configured via Group Policy to *require* FAST for pre-authentication, any bare, unarmored AS-REQ packet (the hallmark of an AS-REP roasting attempt) will be aggressively rejected by the KDC, returning `KDC_ERR_PREAUTH_REQUIRED` and `KDC_ERR_FAST_REQUIRED` errors. Consequently, the attacker cannot retrieve the AS-REP encrypted blob required for offline cracking, neutralizing the attack vector at the protocol level.

### Q10: What are the specific Active Directory attributes and Event IDs you would monitor to detect a Golden Ticket attack, and why are they reliable indicators?
**Answer:**
A Golden Ticket attack involves forging a TGT using the compromised `krbtgt` account hash. Because the attacker generates the ticket offline, there is no AS-REQ sent to the KDC, making traditional AS-REQ monitoring blind to the creation of the ticket.
Detection must focus on the *usage* of the forged ticket (the TGS-REQ phase).
1. **Event ID 4769 (A Kerberos service ticket was requested):** Monitor this event when the TGT is presented.
2. **Domain SID Mismatch:** A heavily reliable indicator is analyzing the User SID within the forged ticket. Attackers often forge the ticket to include the `Enterprise Admins` group (RID 519). If the domain SID in the ticket doesn't perfectly match the actual domain SID, or if RIDs are injected that do not exist, it's a clear indicator of forgery.
3. **Ticket Lifetime Anomalies:** Default Kerberos TGT lifetime is 10 hours. Attackers forging Golden Tickets often specify lifetimes of 10 years (or arbitrarily long periods). Monitoring Event 4769 for ticket lifetimes exceeding the domain policy maximum is a high-fidelity alert.
4. **Encryption Downgrades:** If the `krbtgt` password was dumped as an NTLM hash (RC4), the forged Golden Ticket will often use RC4 (0x17) encryption. If the domain enforces AES-256 for the `krbtgt` account, seeing a TGS-REQ utilizing an RC4-encrypted TGT is highly suspicious.

### Q11: Discuss the implications of a Bronze Bit vulnerability (CVE-2020-17049) in the context of Kerberos delegation. How does it allow bypassing S4U2Proxy restrictions?
**Answer:**
The Bronze Bit vulnerability (CVE-2020-17049) fundamentally undermines the security of Kerberos Constrained Delegation by tampering with the Forwardable flag in the PAC (Privilege Attribute Certificate).
**Context:** In Constrained Delegation, the S4U2Self extension allows a service to request a TGS for a user to itself. By default, this ticket is *not* forwardable unless the user's account is explicitly configured as "Trusted to authenticate for delegation". If it's not forwardable, the service cannot use S4U2Proxy to access backend services on behalf of the user.
**The Vulnerability:** The Bronze Bit vulnerability stems from a flaw in how the KDC validates the PAC signature when processing an S4U2Proxy request. An attacker who has compromised a service configured with Constrained Delegation can manipulate the Service Ticket obtained via S4U2Self. They intentionally flip the "Forwardable" bit (the 'Bronze Bit') in the ticket's flags to true. 
Because of the CVE, the KDC failed to properly validate the PAC signature of the modified ticket against the original request state. Consequently, the KDC accepts the tampered ticket and successfully executes the S4U2Proxy request, issuing a ticket to the backend service.
**Implications:** This allows an attacker to completely bypass the "Trusted to authenticate for delegation" restriction. If they compromise *any* service with Constrained Delegation, they can impersonate *any* user to the allowed backend services, escalating privileges far beyond the intended architectural design.

## Real-World Attack Scenario
An Advanced Persistent Threat (APT) group infiltrates a corporate network via a sophisticated spear-phishing payload, establishing a low-privileged beacon on a marketing workstation. During internal reconnaissance, they execute `Rubeus.exe asreproast /format:hashcat` and successfully harvest an AS-REP blob for the `svc_backup` account. This account was vulnerable because the IT team had previously disabled Pre-Authentication to support a legacy backup software deployment.
The APT cracks the hash offline within minutes utilizing an AWS GPU rig. Reconnaissance reveals `svc_backup` is a member of the powerful `Server Operators` group. Leveraging the newly acquired credentials, they attempt to map the `C$` administrative share on the primary Domain Controller but encounter "Access Denied" due to UAC remote restrictions preventing local admin token elevation over network logons.
To bypass this, they pivot to exploiting Kerberos Constrained Delegation. They identify an internal web server that is trusted for delegation to the CIFS service on the Domain Controller. They abuse the compromised `svc_backup` credentials to request an S4U2Self ticket, asserting they are the Domain Admin. They subsequently utilize S4U2Proxy to obtain a CIFS ticket specifically for the DC. They inject this ticket into memory and utilize `wmiexec.py` to seamlessly execute commands, establishing a persistent, SYSTEM-level C2 session directly on the Domain Controller, achieving total network dominance.

## Chaining Opportunities
- **AS-REP Roasting chained with Constrained Delegation:** As demonstrated in the scenario, weak service account passwords obtained via AS-REP Roasting can rapidly unlock extensive delegation abuse vectors, allowing lateral movement across administrative boundaries.
- **Coercion (PetitPotam/DFSCoerce) chained with Unconstrained Delegation:** Forcing high-value targets (such as DCs or Exchange servers) to authenticate to a host configured with Unconstrained Delegation leads to the immediate theft of highly privileged machine account TGTs, instantly enabling DCSync capabilities.
- **Kerberoasting chained with Silver Ticket Forgery:** Extracting the service account hash via Kerberoasting, and subsequently utilizing that hash to forge a Silver Ticket (TGS). This allows the attacker to maintain persistent, administrative access to that specific service indefinitely without ever interacting with the KDC again, evading standard authentication logging.

## Related Notes
- [[51 - Active Directory Delegation Attacks]]
- [[51 - Kerberos Protocol Deep Dive]]
- [[51 - Forging Tickets Golden and Silver]]
- [[51 - Overpass the Hash Concepts]]
- [[51 - KDC Architecture and Cryptography]]
