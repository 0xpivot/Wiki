---
tags: [imap, pop3, email, brute-force, cleartext]
difficulty: beginner
module: "35 - Network Protocol Attacks"
topic: "35.05 IMAP/POP3"
---

# IMAP/POP3 — Credential Attacks

## 1. Introduction to Mail Retrieval Protocols
While SMTP is used to *send* and *relay* mail between servers, Post Office Protocol version 3 (POP3) and Internet Message Access Protocol (IMAP) are used by end-user client applications (like Microsoft Outlook, Mozilla Thunderbird, or Apple Mail) to *retrieve* email from the mail server.

Understanding the difference in their state machines and default configurations is critical for identifying vulnerabilities and exploiting weak mail infrastructure.

### 1.1 POP3 (Post Office Protocol v3)
- **Default Ports:** TCP Port 110 (Unencrypted/Cleartext), TCP Port 995 (POP3S - SSL/TLS Encrypted).
- **Architecture:** POP3 is designed to download emails from the server to the local client, and then (usually) delete them from the server. It operates as a "store-and-forward" service. It does not natively support complex folder structures on the server side.
- **State Machine:** Connection -> Authentication (USER/PASS commands) -> Transaction (LIST, RETR, DELE commands) -> Update (QUIT).

### 1.2 IMAP (Internet Message Access Protocol)
- **Default Ports:** TCP Port 143 (Unencrypted/Cleartext), TCP Port 993 (IMAPS - SSL/TLS Encrypted).
- **Architecture:** IMAP allows the client to interact with emails directly on the server without downloading them permanently. It supports complex folder hierarchies, flags (read/unread), and allows multiple clients to connect to the same mailbox simultaneously.
- **State Machine:** It is much more complex, utilizing tags for concurrent command processing. Commands like `LOGIN`, `SELECT INBOX`, `FETCH`.

## 2. ASCII Diagram: Cleartext Credential Interception

```text
    [Victim (Thunderbird Client)]
           |
           |--(1) Initiates Mail Sync (TCP Port 110 or 143)
           |      Sends: USER alice
           |      Sends: PASS SecretPassword!
           |
           |      [Attacker (ARP Spoofed / MITM)]
           |               |
           |<---(2) Captures packets using Wireshark--->|
           |               |
           |               V
           |      Reads POP3/IMAP traffic in cleartext.
           |      Extracts "alice" and "SecretPassword!"
           V
    [Corporate Mail Server (Exchange / Dovecot)]
           |
           |--(3) Validates and returns mail spool.
```

## 3. Cleartext Transmission Vulnerabilities
Just like legacy FTP and Telnet, the original RFCs for POP3 (RFC 1939) and IMAP (RFC 3501) did not mandate encryption. By default, on ports 110 and 143, the entire conversation—including the critical authentication phase—is sent in plain ASCII text.

**The Risk:**
Any attacker capable of intercepting network traffic (via ARP spoofing on a local LAN, rogue Wi-Fi access points, or compromised intermediate routers) can trivially extract employee email passwords. Because users frequently reuse their email passwords for Active Directory, VPNs, and internal portals, a compromised email credential often leads directly to total domain compromise.

**Exploitation Capture (POP3):**
```bash
tcpdump -i eth0 port 110 -A
```
*Output snippet:*
```text
C: USER jsmith
S: +OK User accepted
C: PASS Fall2025!
S: +OK Pass accepted
```

**Exploitation Capture (IMAP):**
```bash
tcpdump -i eth0 port 143 -A
```
*Output snippet:*
```text
C: A001 LOGIN "jsmith" "Fall2025!"
S: A001 OK LOGIN completed
```

## 4. Credential Brute Force and Dictionary Attacks
IMAP and POP3 services exposed to the public internet are constantly bombarded by automated brute-force attacks.

**The Mechanics:**
Attackers compile massive lists of compromised corporate email addresses (often gathered via OSINT, breached databases, or SMTP enumeration) and feed them into tools like Hydra or Ncrack against the target's public IP address.

**The Risk:**
Because mail servers must remain highly accessible for remote employees, administrators are often hesitant to implement aggressive account lockout policies (which can lead to self-inflicted Denial of Service if an attacker intentionally locks out the CEO). This allows attackers to perform "low and slow" password spraying attacks over weeks or months.

**Exploitation via Hydra:**
Targeting POP3:
```bash
hydra -L users.txt -P passwords.txt pop3://mail.example.com
```
Targeting IMAP:
```bash
hydra -L users.txt -P passwords.txt imap://mail.example.com
```

**Password Spraying:**
Instead of trying many passwords for one user (which triggers lockouts), attackers try *one* common password (e.g., `Company2026!`) against *every* user in the directory.
```bash
hydra -L all_employees.txt -p Company2026! imap://mail.example.com
```

## 5. Implementation Vulnerabilities and Exploits
Beyond credential theft, the underlying mail server software (like Dovecot, Courier, Microsoft Exchange, or legacy Sendmail) can contain exploitable bugs.

### 5.1 Buffer Overflows
Historically, complex IMAP server implementations have suffered from buffer overflows when processing excessively long folder names or malformed `FETCH` requests. This could lead to Remote Code Execution (RCE) with the privileges of the mail daemon.

### 5.2 Directory Traversal
If the mail server fails to sanitize mailbox names, an authenticated attacker might use directory traversal (`../`) to escape the mail spool directory (e.g., `/var/mail/`) and read arbitrary files on the server's filesystem, extracting configuration files or `/etc/passwd`.

## 6. Defensive Strategies & Mitigation

### 6.1 Enforce Strong Encryption (TLS/SSL)
The absolute minimum requirement for modern mail infrastructure is strictly enforcing encryption.
- **Implicit TLS:** Force clients to use Ports 993 (IMAPS) and 995 (POP3S). Close ports 110 and 143 at the firewall level.
- **Explicit TLS (STARTTLS):** If ports 110/143 must remain open for legacy clients, configure the server to *mandate* the `STARTTLS` command before accepting the `USER` or `LOGIN` commands. If the client refuses to upgrade to TLS, drop the connection.

### 6.2 Secure Authentication Mechanisms
- **Disable Cleartext Logins:** Configure Dovecot/Exchange to reject `plaintext` auth mechanisms unless the connection is already wrapped in a TLS tunnel.
- **Implement Multi-Factor Authentication (MFA):** For webmail and modern clients, enforce MFA (e.g., OAuth 2.0 tokens, Duo, Microsoft Authenticator). Legacy protocols like POP3/IMAP often struggle with standard MFA; in such cases, use "App Passwords" specifically generated for legacy clients, ensuring the user's primary Active Directory password is not exposed to the IMAP daemon.

### 6.3 Rate Limiting and Lockouts
- Implement strict, context-aware rate limiting. Ban IP addresses that fail authentication repeatedly using tools like Fail2Ban.
- Monitor for impossible travel (e.g., a successful IMAP login from New York, followed 5 minutes later by a POP3 login from Moscow).

## 7. Advanced Exploitation: Mail Spool Manipulation
If an attacker gains local access to the mail server, understanding how mail is stored is vital.
- **mbox format:** All emails for a user are stored in a single, massive plain-text file (usually `/var/mail/username` or `/var/spool/mail/username`). Attackers can simply `cat` or `grep` this file for passwords.
- **Maildir format:** Each email is stored as a separate file within directories (`tmp`, `new`, `cur`).
An attacker with local root can inject a malicious script directly into a user's `new` folder, disguised as an IT email, guaranteeing the user reads it.

## 8. Chaining Opportunities
- **IMAP Password Spray to VPN Access:** Perform a password spray against the public IMAP portal. Take the successfully cracked AD credentials and use them to log into the corporate SSL VPN. -> [[04 - VPN Security and Attacks]]
- **Cleartext Sniffing to O365 Takeover:** Use ARP spoofing to capture an unencrypted legacy IMAP login, then use those credentials to log into the victim's Microsoft 365 web portal, gaining access to SharePoint and OneDrive. -> [[16 - Cloud Security Vulnerabilities]]
- **Mail Read Access to Password Resets:** Once an attacker compromises an IMAP account, they can trigger password resets for the victim's social media, banking, and AWS accounts, intercepting the password reset links sent to the inbox. -> [[01 - Web Application Authentication]]

## 9. Related Notes
- [[04 - SMTP — Open Relay, User Enumeration (VRFY, EXPN), Spoofing]]
- [[02 - Man-in-the-Middle Attacks]]
- [[12 - Password Cracking Strategies]]
- [[15 - Social Engineering]]

---
*End of Note*
