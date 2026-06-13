---
tags: [tools, network, exploit, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.50 Hydra All Protocols Reference"
---

# Hydra All Protocols Reference

## 1. Introduction to THC-Hydra

Hydra (THC-Hydra) is the premier, parallelized network login cracker available to the cybersecurity community. While tools like Hashcat or John the Ripper are designed for *offline* password cracking (cracking cryptographic hashes stored locally), Hydra is designed for *online* brute-forcing and credential stuffing.

Hydra operates by rapidly bombarding a remote network service—such as SSH, FTP, HTTP forms, RDP, or databases—with thousands of login attempts using wordlists of usernames and passwords. It is highly optimized, supporting over 50 different protocols, and is an indispensable tool during both the enumeration and exploitation phases of a penetration test.

Given that weak passwords remain one of the most prevalent vulnerabilities globally, understanding how to configure Hydra for complex protocols, manage its timing constraints, and avoid account lockouts is critical for effective Red Teaming.

## 2. Core Architecture and Parallelization

Hydra achieves its speed through aggressive parallelization. Instead of trying one password and waiting for the server to respond, Hydra spawns dozens of concurrent tasks, maintaining multiple simultaneous connections to the target service.

### Connection State and Thread Management
Online brute-forcing is inherently constrained by the target server's capacity and network latency. If Hydra attacks too aggressively, the target service (e.g., the SSH daemon) might crash, or the underlying network infrastructure might drop the packets, leading to false negatives (Hydra missing the correct password).
Hydra manages this via a centralized thread pool that orchestrates connections based on protocol-specific modules.

### ASCII Architecture Diagram: Hydra Attack Flow

```text
+-----------------------------------------------------------------------------------+
|                            Hydra Brute-Force Architecture                         |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  +----------------+    +----------------+                                         |
|  | User Wordlist  |    | Pass Wordlist  |                                         |
|  | (users.txt)    |    | (rockyou.txt)  |                                         |
|  +-------+--------+    +-------+--------+                                         |
|          |                     |                                                  |
|          +--------+   +--------+                                                  |
|                   |   |                                                           |
|                   v   v                                                           |
|          +----------------------+                                                 |
|          | Target Combination   |  (e.g., admin:password123)                      |
|          | Generator Engine     |                                                 |
|          +--------+-------------+                                                 |
|                   |                                                               |
|                   v                                                               |
|          +----------------------+                                                 |
|          | Parallel Task Queue  |  (Controlled by -t threads)                     |
|          +---+----+---+----+----+                                                 |
|              |    |   |    |                                                      |
|   +----------+    |   |    +----------+                                           |
|   |               |   |               |                                           |
|   v               v   v               v                                           |
| +----+         +----+----+         +----+                                         |
| |Conn|         |Conn|Conn|         |Conn|   Protocol-Specific Modules             |
| |SSH |         |FTP |HTTP|         |RDP |   (Handle handshakes, encryption,       |
| +-+--+         +--+-+-+--+         +--+-+    and response parsing)                |
|   |               |   |               |                                           |
|===|===============|===|===============|===========================================|
|   |               |   |               |                                           |
|   v               v   v               v                                           |
| +---------------------------------------+                                         |
| |             Target Server             |                                         |
| |  (Evaluates credentials & responds)   |                                         |
| +---------------------------------------+                                         |
|                                                                                   |
+-----------------------------------------------------------------------------------+
```

## 3. The Core Syntax and Combinations

Hydra requires three primary components: the target IP, the credential lists, and the protocol to attack.

### Basic Syntax Structure
```bash
hydra -l <username> -P <passwords.txt> <IP> <protocol>
```

### Capital vs. Lowercase Flags
The most crucial distinction in Hydra's syntax is the capitalization of the credential flags:
- `-l <user>` : Specifies a single, static username (e.g., `-l admin`).
- `-L <file>` : Specifies a wordlist of multiple usernames (e.g., `-L users.txt`).
- `-p <pass>` : Specifies a single, static password (e.g., `-p Password123!`).
- `-P <file>` : Specifies a wordlist of passwords (e.g., `-P rockyou.txt`).

**Combinatorics:**
If you provide `-L users.txt` (10 users) and `-P rockyou.txt` (10 million passwords), Hydra will generate 100 million connection attempts, trying every password for the first user, then every password for the second, etc.

## 4. Attacking Standard Network Protocols

### SSH (Secure Shell)
SSH brute-forcing is common but slow due to cryptographic overhead.
```bash
hydra -l root -P rockyou.txt 10.10.10.50 ssh -t 4
```
*Tuning Note: SSH daemons typically severely rate-limit connections. Using a high thread count (`-t 16`) will cause the SSH server to drop connections, resulting in Hydra failing instantly. Always keep SSH threads low (`-t 4` or `-t 6`).*

### FTP (File Transfer Protocol)
FTP is plaintext and generally handles higher connection rates well.
```bash
hydra -L users.txt -P passwords.txt 10.10.10.21 ftp -t 16
```

### RDP (Remote Desktop Protocol)
RDP requires Network Level Authentication (NLA) negotiation.
```bash
hydra -l Administrator -P rockyou.txt 192.168.1.100 rdp -t 4
```

### SMB (Server Message Block)
Used heavily in Windows environments.
```bash
hydra -l Administrator -P passwords.txt 10.10.10.40 smb -t 16
```

## 5. Attacking Web Forms (HTTP GET / POST)

Brute-forcing web forms is vastly more complex than standard protocols because Hydra must be manually configured to understand the HTTP request structure, the form fields, and the server's failure/success responses.

### HTTP POST Form Structure
To attack a login form, you must use a proxy (like Burp Suite) to intercept the login request, then supply Hydra with three colon-separated fields:
1. **The Login Path:** E.g., `/login.php`
2. **The Request Body:** E.g., `user=^USER^&pass=^PASS^&Login=Submit`
3. **The Failure/Success Condition:** A string of text that appears on the page *only* when the login fails (e.g., `F=Incorrect password`) or succeeds (e.g., `S=Welcome back`).

### Example: HTTP POST Brute Force
```bash
hydra -l admin -P rockyou.txt 10.10.10.80 http-post-form "/admin/login.php:user=^USER^&password=^PASS^:F=Invalid credentials"
```

### Handling CSRF Tokens and Cookies
If the web application utilizes Anti-CSRF tokens, simple Hydra attacks will fail. You must pass custom headers or cookies. While Hydra supports this via the `H=` parameter, complex web brute-forcing is generally better handled by Burp Suite Intruder or custom Python scripts, as Hydra's HTTP parser is somewhat rigid.

## 6. Advanced Timing, Tuning, and OPSEC

Hydra is incredibly loud and will immediately alert any intrusion detection system or SIEM. Furthermore, indiscriminate brute-forcing guarantees Account Lockout in modern Active Directory environments.

### The Account Lockout Danger
In a corporate environment, AD policies usually lock an account after 3-5 failed attempts. If you use `-L users.txt -p Password1!`, you are testing one password across many users ("Password Spraying"). This is safe.
If you use `-l Administrator -P rockyou.txt`, you will instantly lock the Administrator account.

### Timing Parameters
- `-t <TASKS>`: The number of parallel connections. Defaults to 16. Lower this for SSH/RDP.
- `-W <SECONDS>`: Wait time between responses. Useful for rate-limited APIs.
- `-T <TASKS>`: Overall global tasks (useful for spreading load across multiple IPs).

### Bypassing First-Attempt Failures (`-e nsr`)
Often, default credentials or blank passwords work. The `-e` flag tests these automatically before starting the wordlist:
- `n` = null password
- `s` = password is the same as the username
- `r` = reverse of the username
```bash
hydra -l admin -P rockyou.txt 10.10.10.1 ftp -e nsr
```

## 7. Database and Specialized Protocol Attacks

Hydra is not limited to standard infrastructure protocols. It natively supports brute-forcing database engines, which is crucial during internal network penetration tests where DBA passwords might be weak or default.

### MySQL Database Attacks
Brute-forcing the root user of a MySQL server exposed internally:
```bash
hydra -l root -P rockyou.txt 10.10.10.60 mysql -t 4
```
*Note: MySQL often drops connections if authentication fails too many times in rapid succession. Lowering the thread count and using `-W 1` to add a delay can stabilize the attack.*

### PostgreSQL Database Attacks
Similarly, attacking a PostgreSQL instance:
```bash
hydra -l postgres -P rockyou.txt 10.10.10.61 postgres -t 4
```

### SNMP Community String Guessing
While technically not a standard "login", SNMP (Simple Network Management Protocol) relies on community strings for authentication. Hydra can quickly iterate through common strings like `public`, `private`, `manager`, etc.
```bash
hydra -P snmp_strings.txt 10.10.10.50 snmp -t 1
```

## 8. Password Spraying vs Brute Forcing Strategies

Password spraying is the inverse of brute-forcing. Instead of many passwords against one user, you test one highly probable password (e.g., `Summer2026!`) against hundreds of users to avoid account lockouts.

```bash
# Testing a single password against a list of users via SMB
hydra -L domain_users.txt -p "Welcome123!" 10.10.10.5 smb
```

A core methodology in professional Red Teaming is:
1. **Never** brute force AD accounts (unless the client explicitly asks to test lockout policies).
2. **Always** Password Spray, waiting at least 30 minutes between cycles to allow the AD Bad Password Count timer to reset.

## 9. Creating Custom Service Modules

For highly specialized proprietary protocols that Hydra does not natively support, users can write custom C modules. Because Hydra is open-source, the protocol handlers are simply C files (e.g., `hydra-ssh.c`, `hydra-http.c`). 
A skilled reverse engineer can dissect a proprietary binary protocol using Wireshark, write a new `hydra-custom.c` module that mimics the handshake and authentication packets, recompile Hydra, and successfully brute-force entirely custom corporate infrastructure.

## 10. Chaining Opportunities
- **Recon to Attack:** Use [[46 - Masscan High-Speed Port Scanner]] or [[47 - Rustscan Fast Pre-Scanner for Nmap]] to identify open SSH, FTP, or RDP ports across a large subnet, extract those IPs to a file, and use Hydra's `-M <ip_list.txt>` flag to attack all of them simultaneously.
- **Web App Escalation:** Identify hidden login portals via [[08 - FFuF Directory Fuzzing]] or [[17 - Gobuster Directory and DNS Enumeration]], then craft a Hydra `http-post-form` attack to gain access.
- **Post-Exploitation Pivot:** After gaining initial access via [[48 - Metasploit Auxiliary Exploits Post Modules]], use proxychains to route Hydra through your Meterpreter session to brute-force internal network services that are not exposed externally.

## 11. Related Notes
- [[46 - Masscan High-Speed Port Scanner]]
- [[47 - Rustscan Fast Pre-Scanner for Nmap]]
- [[08 - FFuF Directory Fuzzing]]
- [[17 - Gobuster Directory and DNS Enumeration]]
- [[48 - Metasploit Auxiliary Exploits Post Modules]]
