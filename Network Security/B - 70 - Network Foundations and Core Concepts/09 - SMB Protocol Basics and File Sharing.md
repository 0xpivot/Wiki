---
tags: [network, basics, foundations, vapt]
difficulty: beginner
module: "70 - Network Foundations and Core Concepts"
topic: "70.09 SMB Protocol Basics and File Sharing"
---

# SMB Protocol Basics and File Sharing

## 1. Overview of SMB
Server Message Block (SMB) is an application-layer network protocol primarily used for providing shared access to files, printers, serial ports, and miscellaneous communications between nodes on a network. Originating in the 1980s by IBM and heavily modified by Microsoft, it is the backbone of file sharing in Windows Active Directory environments. 

Modern SMB operates directly over TCP port 445. Historically, older versions of SMB (specifically NetBIOS over TCP/IP or NBT) utilized UDP ports 137/138 and TCP port 139.

## 2. Evolution and Dialects
The protocol has gone through multiple major revisions, known as dialects, primarily driven by the need for better performance over WANs and enhanced security.
*   **SMB 1.0 (CIFS):** Common Internet File System. Now considered obsolete and extremely insecure. It is "chatty" (requiring hundreds of round trips for small tasks), lacks mandatory encryption, and is highly vulnerable to remote code execution (RCE) flaws. Microsoft strongly recommends disabling it network-wide.
*   **SMB 2.0 / 2.1:** Introduced in Windows Vista / 7. Massively reduced the chattiness by allowing request compounding (sending multiple SMB commands in a single packet). Added support for larger MTUs and symbolic links.
*   **SMB 3.0:** Introduced with Windows 8 / Server 2012. A major security overhaul. Introduced **SMB Encryption** (AES-CCM), transparent failover, and SMB Multichannel (using multiple network interfaces for speed and fault tolerance).
*   **SMB 3.1.1:** Introduced in Windows 10. Required pre-authentication integrity checks (preventing downgrade MITM attacks) and added AES-GCM encryption for better performance.

## 3. Core Features: Shares and IPC
SMB exposes resources as "Shares". 
*   **Standard Shares:** User-created folders shared across the network (e.g., `\\Server\Marketing_Data`).
*   **Administrative/Hidden Shares:** Windows automatically creates hidden shares for administrative purposes. These end with a `$` and require local administrator privileges to access. Examples include `C$` (the entire C: drive) and `ADMIN$` (the Windows directory).
*   **Inter-Process Communication (IPC$):** A special, hidden share used for establishing temporary connections between clients and servers to facilitate named pipe communication, enumerate users/shares, and perform RPC (Remote Procedure Call) operations.

## 4. Named Pipes and MSRPC
One of the most complex and critical aspects of SMB is its role as a transport protocol for Microsoft Remote Procedure Call (MSRPC). SMB can transport MSRPC traffic using **Named Pipes**. A named pipe is a logical connection point that processes can use to exchange data.

Many critical Windows administrative tools and protocols run *over* SMB via named pipes, including:
*   `\pipe\lsarpc`: Used for LSA (Local Security Authority) policy, user enumeration, and domain trusts.
*   `\pipe\samr`: Used for Security Account Manager enumeration (querying users and groups).
*   `\pipe\srvsvc`: Used to query what shares are available on the server.
*   `\pipe\spoolss`: The Print Spooler service (infamously vulnerable to PrintNightmare).

## 5. Authentication Mechanisms
When a client connects to an SMB share, it must authenticate. SMB supports multiple authentication mechanisms encapsulated within SPNEGO (Simple and Protected GSSAPI Negotiation Mechanism).
*   **LM / NTLMv1:** Completely obsolete and easily cracked. Relies on weak cryptographic hashes.
*   **NTLMv2:** A challenge-response protocol. The server sends a random challenge, and the client responds with a hash calculated using the challenge and the user's password hash. Still widely used but highly susceptible to relay attacks.
*   **Kerberos:** The default and most secure authentication protocol in Active Directory environments. It relies on ticket-granting mechanisms and prevents relay attacks.

## 6. SMB Signing and SMB Encryption
To protect the integrity and confidentiality of SMB traffic:
*   **SMB Signing:** Ensures that SMB packets have not been intercepted or modified in transit (prevents MITM/Relay attacks). It cryptographically signs each packet. By default, it is **Required** on Domain Controllers, but only **Enabled (Optional)** on regular workstations and servers.
*   **SMB Encryption:** Protects the confidentiality of the data. While signing prevents modification, anyone with a packet sniffer can still read the files being transferred unless SMB Encryption (SMBv3) is enforced.

## 7. Security Vulnerabilities and Attack Vectors
SMB is arguably the most targeted protocol in internal penetration testing and ransomware campaigns.

*   **SMB Relay (NTLM Relaying):** If SMB Signing is not required, an attacker can position themselves in a MITM position (using tools like Responder via LLMNR/NBT-NS poisoning). When a victim attempts to authenticate, the attacker intercepts the NTLMv2 authentication attempt and seamlessly relays it to a target server. If the victim has administrative rights on the target, the attacker gains remote code execution.
*   **Pass-the-Hash (PtH):** Because Windows authentication relies on the NT hash rather than the plaintext password, an attacker who dumps the SAM database or LSASS memory can inject a captured NTLM hash directly into an SMB authentication session to gain access, without ever needing to crack the password.
*   **Null Sessions:** In older Windows environments (SMB1/early SMB2), an unauthenticated user could connect to the `IPC$` share without providing a username or password. From there, they could query MSRPC named pipes to enumerate the entire list of users, groups, and password policies on the domain.
*   **EternalBlue (MS17-010):** A devastating buffer overflow vulnerability in the SMBv1 protocol parsing logic. It allows an unauthenticated attacker to execute arbitrary shellcode at the `SYSTEM` level. It was the primary vector for the WannaCry and NotPetya ransomware worms.

## 8. ASCII Diagram: SMB NTLM Relay Attack Flow

```text
  [Victim Machine]                        [Attacker (MITM)]                        [Target Server]
    (IP: 192.168.1.10)                    (IP: 192.168.1.50)                     (IP: 192.168.1.100)
         |                                       |                                        |
         | (1) Victim tries to access            |                                        |
         |     \\nonexistent-share               |                                        |
         |     Attacker poisons LLMNR and says   |                                        |
         |     "I am nonexistent-share!"         |                                        |
         |                                       |                                        |
         | -- (2) SMB Negotiate Protocol ------> |                                        |
         |                                       | -- (3) SMB Negotiate Protocol -------> |
         |                                       |                                        |
         |                                       | <- (4) SMB Challenge (Challenge X) --- |
         | <- (5) SMB Challenge (Challenge X) -- |                                        |
         |                                       |                                        |
         | -- (6) NTLMv2 Response (Hash(X)) ---> |                                        |
         |                                       | -- (7) NTLMv2 Response (Hash(X)) ----> |
         |                                       |                                        |
         |                                       | <- (8) Auth Success (Access Granted) - |
         | <- (9) Drops connection / Error ----- |                                        |
         |                                       |                                        |
         |                                       | =====================================> |
         |                                       | Attacker executes PsExec / Service     |
         |                                       | creating SYSTEM level shell!           |
```

## 9. Chaining Opportunities
*   **LLMNR Poisoning to SMB Relay to RCE:** The classic internal network kill chain. Poison broadcast name resolution, capture the SMB authentication, relay it to a machine where SMB signing is disabled and the victim is a local admin, drop a payload, and gain a reverse shell.
*   **SMB Enumeration to Password Spraying:** Connecting to `IPC$` via a Null Session or low-privileged account to enumerate the Domain User list, then using that valid user list to perform a low-and-slow password spray attack against SMB or HTTP endpoints.
*   **BloodHound Collection over SMB:** Using a tool like SharpHound to query Active Directory structure, Group Policy, and session data over SMB MSRPC pipes to map out the fastest path to Domain Admin.

## 10. Related Notes
*   [[06 - DNS Protocol Basics and Name Resolution]]
*   [[01 - Network Basics]]
*   [[12 - Active Directory Foundations]]
