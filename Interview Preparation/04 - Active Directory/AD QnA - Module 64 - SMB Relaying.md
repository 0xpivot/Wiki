---
tags: [interview, active-directory, qna, scenario]
difficulty: expert
module: "Interview Prep - Active Directory"
topic: "QnA - AD Module 64"
---

# Expert Active Directory Q&A: SMB Relaying

```text
                                  +-------------------+
                                  |                   | (SMB Auth Attempt)
                                  |    Victim Host    | ---------------------+
                                  | (Coerced by Petit)|                      |
                                  +-------------------+                      v
                                                                   +-------------------+
                                                                   |                   |  (Relay Auth Payload)
                                                                   |   Attacker Node   | ------------------------+
                                                                   |   (ntlmrelayx)    |                         |
                                                                   +-------------------+                         |
                                                                                                                 v
                                                                                                       +-------------------+
                                                                                                       |                   |
                                                                                                       |   Target Server   |
                                                                                                       |  (SMB / LDAP/S)   |
                                                                                                       +-------------------+
```

## Formal Technical Questions

### Q1: Detail the mechanics of the NTLMv2 Challenge-Response protocol over SMB. Exactly how does an attacker intercept and relay this authentication?
**Expert Answer:**
The NTLMv2 authentication over SMB operates in a three-way handshake:
1. **Type 1 (Negotiate):** The client sends a Negotiate message indicating its capabilities to the server (or attacker acting as the server).
2. **Type 2 (Challenge):** The server generates a random 8-byte server challenge and sends it back to the client.
3. **Type 3 (Authenticate):** The client takes its NTLM password hash, uses it to encrypt the server's challenge (along with a client challenge and timestamp), and sends this encrypted response back to the server. The server verifies this by checking it against the Domain Controller (via Netlogon).
**The Relay Attack:** The attacker positions themselves in the middle. When the Victim sends the Type 1 message to the Attacker, the Attacker suspends the connection, opens a new connection to the Target Server, and sends a Type 1. The Target Server replies with a Type 2 Challenge. The Attacker forwards *this exact challenge* back to the Victim. The Victim encrypts it, thinking it is authenticating to the Attacker, and sends the Type 3 response. The Attacker forwards this valid response to the Target Server. Since the challenge was signed by the victim's valid hash, the Target Server accepts the authentication, granting the attacker access as the victim.

### Q2: Discuss the three states of SMB Signing (`Disabled`, `Enabled`, `Required`) and their impact on SMB Relaying.
**Expert Answer:**
SMB Signing provides integrity to SMB traffic by signing packets with a session key derived during authentication.
- **Required:** The server mandates that all SMB packets be cryptographically signed. If an attacker relays authentication, they cannot sign subsequent packets because they do not possess the victim's actual password hash (only the challenge-response). The connection is dropped. Relaying to an SMB server with signing `Required` is impossible.
- **Enabled:** The server supports signing but does not mandate it. If the client wants to sign, it will; otherwise, it won't. This state is vulnerable to relay attacks because the attacker (acting as the client to the target server) simply negotiates the connection *without* signing.
- **Disabled:** Signing is not supported. Highly vulnerable to relay attacks.
*Note: By default in AD, Domain Controllers have SMB Signing `Required`, while standard Windows workstations and servers only have it `Enabled`, making lateral movement across servers trivial via relay.*

### Q3: What is Cross-Protocol Relaying? Provide examples of how an attacker can relay an SMB authentication attempt to a completely different protocol.
**Expert Answer:**
NTLM authentication is encapsulated within Application Layer protocols (like SMB, HTTP, LDAP). Because the NTLM challenge-response blobs are protocol-agnostic, an attacker can capture NTLM authentication over one protocol and relay it to another.
- **SMB to LDAP:** An attacker captures an incoming SMB connection and relays the NTLM blob to the Domain Controller over LDAP. This is incredibly powerful because if the relayed account has high privileges (e.g., an Exchange Server or Domain Admin), the attacker can execute LDAP operations, such as creating new computer accounts or modifying AD object ACLs (like setting Resource-Based Constrained Delegation).
- **SMB to MSSQL:** Relaying incoming SMB traffic to a database server to execute SQL queries as the compromised user.
- **HTTP to SMB:** Tricking a user into authenticating to an attacker's web server, then relaying that HTTP NTLM auth to an SMB share to gain code execution.

## Scenario-Based Questions

### Q4: You are on a Red Team engagement. You have identified a critical Application Server with SMB Signing set to "Enabled" (Not Required). However, the network is quiet and no one is naturally authenticating to your attacker machine. How do you force authentication to execute the relay?
**Expert Answer:**
I must coerce authentication. I will utilize MS-RPC vulnerabilities or intended features that force a machine account to authenticate to a supplied UNC path.
1. **PetitPotam (MS-EFSRPC):** I send an unauthenticated RPC call (`EfsRpcOpenFileRaw`) to a Domain Controller or high-value server, instructing it to access a file on my attacker machine (`\\Attacker-IP\share`). The target machine will attempt to authenticate to me over SMB using its Machine Account (e.g., `DC01$`).
2. **PrinterBug (MS-RPRN):** If the Print Spooler service is enabled, I use `SpoolSample` to trigger the `RpcRemoteFindFirstPrinterChangeNotification` function, forcing the target to authenticate to my IP.
3. Once the target machine reaches out to my attacker machine over SMB, I use `ntlmrelayx.py` to intercept and relay that high-privileged authentication to the target Application Server, dumping local hashes or executing a reverse shell.

### Q5: You successfully coerced a Domain Controller (`DC01$`) to authenticate to your attacker machine via SMB. You attempt to relay this to another Domain Controller over SMB, but it fails. Why did it fail, and how do you pivot to successfully exploit this coercion?
**Expert Answer:**
It failed because Domain Controllers have SMB Signing `Required` by default. You cannot relay SMB to SMB when the target requires signing.
To exploit this, I must perform a Cross-Protocol Relay. I will configure `ntlmrelayx` to relay the incoming SMB connection to the target Domain Controller over **LDAP** or **HTTP** (Active Directory Certificate Services).
- **Relay to LDAPS:** I relay `DC01$` to LDAP. Since `DC01$` has `Enterprise Admin` tier rights over the domain, I can use the relay to grant my low-privileged user `DCSync` rights, or configure RBCD on other domain objects.
- **Relay to AD CS (HTTP):** I relay the authentication to the Certificate Authority web enrollment interface (`/certsrv`). Since HTTP does not natively enforce signing like SMB, the CA accepts the authentication and issues a valid Client Authentication Certificate for `DC01$`. I can then use this certificate to request a TGT as the DC, completely compromising the domain.

### Q6: During an SMB relay attack, the target organization implements session multiplexing restrictions and drops your relayed connections. How do you evade this and maintain access?
**Expert Answer:**
Some EDRs or network controls attempt to detect relaying by tracking the MUX ID (Multiplex ID) in the SMB headers or looking for protocol anomalies introduced by tools like Impacket.
To evade this:
1. **Interactive SOCKS Proxy:** Instead of immediately executing a payload, I configure `ntlmrelayx` with the `-socks` flag. This catches the relayed session and holds it open, exposing it via a local SOCKS4 proxy. I can then use native Windows tools (proxying through `proxychains`) to interact with the target SMB share natively, which looks identical to legitimate traffic.
2. **Dropping to NTLMv1:** If the domain is misconfigured to support NTLMv1 (`LmCompatibilityLevel` <= 2), I can downgrade the authentication. NTLMv1 challenge-responses can be easily cracked via rainbow tables (Crack.sh) into the actual NTLM hash. I wouldn't even need to relay; I would just crack the hash and perform Pass-the-Hash.

## Deep-Dive Defensive Questions

### Q7: Explain the concept of Extended Protection for Authentication (EPA) and how it hardens protocols against Cross-Protocol Relaying.
**Expert Answer:**
SMB Signing protects SMB-to-SMB relaying, but fails against Cross-Protocol relaying (e.g., SMB to HTTP). EPA mitigates this.
EPA binds the cryptographic channel (like TLS) to the authentication channel (NTLM). It uses a Channel Binding Token (CBT) and a Service Principal Name (SPN) target name validation.
When EPA is required, the client securely hashes the TLS certificate of the server it thinks it's talking to and includes it in the NTLM response. If an attacker relays this to a different server, the target server checks the CBT against its own TLS certificate. Since they won't match, the target server detects the relay and drops the connection. Furthermore, if the client includes the SPN it intends to reach (e.g., `HTTP/Attacker`), the target server (e.g., `LDAP/DC01`) will reject the auth because the target SPN does not match its own.

### Q8: What specific Windows Event IDs and patterns should a SOC monitor to detect anomalous NTLM relaying activity within the network?
**Expert Answer:**
Relaying creates distinct authentication trails that can be correlated:
- **Event ID 4624 (Logon):** Look for Type 3 (Network Logon) events where the `Workstation Name` (the machine where the request originated) does not match the actual `Source IP Address`. In a relay attack, the attacker forwards the victim's hostname, but the IP will be the attacker's IP.
- **Anomalous Service Executions (Event 7045):** NTLM relay tools often execute payloads by creating temporary Windows Services (e.g., `BVTExe.exe` or randomized 8-character strings). Monitoring for remote service creation from unexpected IPs is critical.
- **LDAP Anomalies:** If relaying to LDAP, monitor for **Event ID 5136** (Directory Object Modified) where critical attributes like `msDS-AllowedToActOnBehalfOfOtherIdentity` (RBCD) are modified by machine accounts in unexpected contexts.

### Q9: Hardening LDAP is critical to preventing SMB-to-LDAP relaying. Discuss the implementation and impact of LDAP Signing and LDAP Channel Binding.
**Expert Answer:**
By default, AD allows simple binds and unencrypted LDAP traffic.
1. **LDAP Signing:** Enforced via GPO (`Domain controller: LDAP server signing requirements -> Require signing`). This mandates that all LDAP traffic must be digitally signed, much like SMB Signing. If an attacker relays an SMB auth to LDAP, they cannot sign the subsequent LDAP queries, breaking tools like `ntlmrelayx` when it tries to execute directory searches or modifications.
2. **LDAP Channel Binding:** To prevent relaying to LDAPS (LDAP over SSL), Channel Binding must be enforced. This utilizes EPA. The Domain Controller verifies the CBT in the NTLM auth over the TLS channel. If an attacker relays traffic, the TLS bindings won't match, and the DC will reject the LDAPS connection.
Implementing both prevents almost all variations of Cross-Protocol NTLM relaying targeting the directory structure.

## Real-World Attack Scenario
During an assumed-breach engagement, the Red Team noted that SMB Signing was disabled across all internal server subnets. However, direct SMB relaying was triggering EDR alerts upon payload execution (service creation). The team pivoted to Cross-Protocol relaying. They used the `PrinterBug` to coerce the primary Exchange Server to authenticate to their Kali Linux machine. They ran `ntlmrelayx -t ldap://domain_controller --escalate-user attacker_user`. The tool intercepted the Exchange Server's authentication, relayed it to the DC over LDAP, and abused the Exchange Server's high privileges to grant the `attacker_user` account `DCSync` rights. Within minutes, the team dumped the `krbtgt` hash and achieved total domain compromise without dropping a single payload on an endpoint.

## Chaining Opportunities
- **SMB Relay + AD CS (PetitPotam):** Coercing a DC to authenticate to an attacker, relaying that to the AD CS Web Enrollment interface to obtain a DC certificate, enabling instant domain takeover.
- **SMB Relay + RBCD:** Relaying a high-privilege machine account to LDAP to write the RBCD attribute onto a target server, allowing the attacker to spoof any user on that server.
- **LLMNR/NBT-NS Poisoning + SMB Relay:** Using Responder to poison broadcast name resolution protocols, capturing the NTLM auth of victims mistyping UNC paths, and relaying them to target database servers.

## Related Notes
- [[01 - Active Directory Basics]]
- [[Active Directory Certificate Services (AD CS) Attacks]]
- [[Resource-Based Constrained Delegation (RBCD)]]
- [[Cryptography - NTLM and Kerberos Algorithms]]
- [[Defensive Security - Active Directory Hardening]]
