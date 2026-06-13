---
tags: [network, basics, foundations, vapt]
difficulty: beginner
module: "70 - Network Foundations and Core Concepts"
topic: "70.10 FTP TFTP and Telnet Protocols"
---

# FTP, TFTP, and Telnet Protocols

## 1. Introduction to Legacy Cleartext Protocols
Before the widespread adoption of encryption standards like TLS and SSH, network administration and file transfers were conducted using cleartext protocols. FTP, TFTP, and Telnet are foundational protocols that played a massive role in the early Internet. However, because they transmit all data—including authentication credentials and payload content—in plain, unencrypted text, they represent significant security risks in modern environments. Understanding how they work is critical for VAPT, as they are still frequently encountered in legacy systems, IoT devices, and internal network infrastructure.

## 2. FTP (File Transfer Protocol) Basics
FTP is a standard network protocol used for the transfer of computer files between a client and server. It operates at the application layer and is built on a client-server model architecture.

Unlike HTTP, which uses a single connection for both control commands and data transfer, FTP uses **Out-of-Band** control. It establishes two distinct TCP connections:
1.  **Command/Control Channel (Port 21):** Used to send commands (e.g., `USER`, `PASS`, `LIST`, `RETR`, `STOR`) and receive server response codes (e.g., `230 User logged in`, `331 Password required`). This channel remains open for the duration of the session.
2.  **Data Channel (Port 20 or High Random Port):** A temporary connection spawned specifically to transfer the actual file contents or directory listings. It opens, transfers the data, and immediately closes.

## 3. Active vs. Passive Mode FTP
The way the Data Channel is established is determined by the FTP mode. This distinction is crucial for understanding firewall configurations and potential firewall traversal vulnerabilities.

*   **Active Mode:**
    *   The client connects from a random high port (e.g., 1026) to the server's command port 21.
    *   When data transfer is needed, the client starts listening on a new port (e.g., 1027) and sends a `PORT` command to the server (e.g., `PORT 192,168,1,10,4,3` meaning IP 192.168.1.10, Port 1027).
    *   The **Server** initiates a new TCP connection from its Data Port 20 back to the client's listening port 1027.
    *   *Problem:* Modern client-side firewalls and NAT drop this incoming connection from the server.

*   **Passive Mode (PASV):**
    *   Designed to fix the firewall issues of Active Mode.
    *   The client connects to port 21. When data transfer is needed, the client sends the `PASV` command.
    *   The **Server** opens a random high listening port (e.g., 2045) and replies with the port details.
    *   The **Client** initiates the data connection from its own random high port to the server's new random high port.
    *   *Advantage:* Because the client initiates both connections, NAT and client firewalls allow the traffic.

## 4. Anonymous FTP
A widely used feature of FTP is "Anonymous" access. It allows users to connect to the server without needing an actual account. Typically, the username is `anonymous` or `ftp`, and the password is traditionally the user's email address (though modern implementations usually accept any string). From a security perspective, misconfigured anonymous FTP can lead to severe information disclosure or remote code execution if the anonymous user has write privileges to web-accessible directories.

## 5. TFTP (Trivial File Transfer Protocol)
TFTP is a stripped-down, lightweight cousin of FTP. It operates over **UDP Port 69**.
*   **Key Characteristics:**
    *   **No Authentication:** TFTP has absolutely no mechanism for usernames or passwords. If you know the file name and the server is running, you can read or write to it.
    *   **No Directory Listing:** You cannot issue a `DIR` or `LIST` command. You must know the exact path and filename to request it.
    *   **Lock-step protocol:** Because it uses UDP, it implements its own simplistic reliability layer. It sends one block of data (512 bytes) and waits for an acknowledgment (ACK) before sending the next block.
*   **Common Uses:** Bootstrapping diskless nodes (PXE boot), transferring firmware or configuration files to network routers and switches (Cisco), and IP phones.

## 6. Telnet Protocol
Telnet (Teletype Network) operates on **TCP Port 23**. It was the original protocol for providing a bidirectional interactive text-oriented communication facility using a virtual terminal connection.
*   **Network Virtual Terminal (NVT):** Telnet provides a universal abstraction of a terminal, ensuring that different operating systems (UNIX, Windows, Mainframes) can communicate.
*   **In-band Signaling:** Unlike FTP, Telnet sends both commands and data over the exact same connection. Telnet commands are embedded within the data stream, prefixed by the Interpret as Command (IAC) escape character (byte 255).
*   **Security Posture:** Telnet provides no encryption. Every keystroke, including administrative passwords, is transmitted in cleartext.

## 7. Security Vulnerabilities and Attack Vectors
*   **Cleartext Sniffing (FTP/Telnet):** Because data is unencrypted, an attacker on the same local network segment can use tools like Wireshark or `tcpdump` to perform ARP spoofing and seamlessly capture usernames, passwords, and the full content of file transfers and terminal sessions.
*   **Brute Force Attacks:** Legacy FTP and Telnet services often lack modern account lockout protections, making them prime targets for automated dictionary attacks using tools like Hydra or Medusa.
*   **FTP Bounce Attack:** An attacker can use the `PORT` command in Active Mode FTP to tell the FTP server to open a data connection to a third-party machine. This can be used to scan internal networks or bypass firewalls by making the FTP server act as a proxy.
*   **TFTP Directory Traversal / Config Extraction:** Since TFTP requires no authentication, attackers often use Metasploit modules to extract `startup-config` or `running-config` files from routers, which often contain hashed or plaintext passwords. If directory traversal is possible, attackers can pull files like `/etc/passwd`.

## 8. Modern Secure Replacements
*   **Telnet -> SSH:** Secure Shell (TCP Port 22) provides a fully encrypted tunnel with strong cryptographic host and client authentication.
*   **FTP -> SFTP / FTPS:** SFTP (SSH File Transfer Protocol) runs entirely over the secure SSH port 22. FTPS (FTP over SSL/TLS) adds a TLS encryption layer to traditional FTP connections.
*   **TFTP -> SCP / HTTPS:** For modern infrastructure provisioning, fetching configs via HTTPS or SCP is vastly preferred.

## 9. ASCII Diagram: Active vs. Passive FTP

```text
================= ACTIVE FTP (Server initiates data connection) =================

  [Client] (IP: 10.0.0.5)                                [FTP Server] (IP: 192.168.1.100)
    |                                                             |
    | (1) Command Channel: SYN (Src Port 1026) -----------------> | (Port 21)
    |                                                             |
    | (2) Client sends PORT command: "PORT 10,0,0,5,4,3" -------> | (Client listening on 1027)
    |                                                             |
    | (Port 1027) <-----(3) Data Channel: SYN (Src Port 20) ----- | (Port 20)
    |      (Blocked by Client Firewall!)                          |

================= PASSIVE FTP (Client initiates both connections) ===============

  [Client] (IP: 10.0.0.5)                                [FTP Server] (IP: 192.168.1.100)
    |                                                             |
    | (1) Command Channel: SYN (Src Port 1026) -----------------> | (Port 21)
    |                                                             |
    | (2) Client sends PASV command ----------------------------> |
    |                                                             |
    | <-----(3) Server replies: "Entering Passive Mode            |
    |           192,168,1,100,7,251" (Listening on 2043) -------- |
    |                                                             |
    | (4) Data Channel: SYN (Src Port 1027) --------------------> | (Port 2043)
    |      (Allowed by Client Firewall!)                          |
```

## 10. Chaining Opportunities
*   **TFTP Read to Credential Reuse:** Extracting a Cisco router configuration file via TFTP, cracking the Type 7 or Type 5 passwords offline, and then using those credentials to log into the administrative SSH interface.
*   **Anonymous FTP to Web Shell RCE:** Identifying an Anonymous FTP server that shares the same physical directory as the organization's public web server. The attacker uploads a PHP web shell via FTP and then executes it via the browser.
*   **Telnet Sniffing to Lateral Movement:** Capturing a domain administrator's credentials who is carelessly using Telnet to manage an old internal switch, then passing those credentials into SMB/WMI to take over the Domain Controller.

## 11. Related Notes
*   [[08 - HTTP HTTPS and TLS Handshake Explained]]
*   [[01 - Network Basics]]
*   [[05 - Network Scanning and Enumeration]]
