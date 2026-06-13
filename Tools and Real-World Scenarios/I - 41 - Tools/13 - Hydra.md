---
tags: [tools, vapt, utility]
difficulty: intermediate
module: "41 - Tools"
topic: "41.13 Hydra"
---

# 41.13 Hydra: Advanced Network Logon Cracker

## Introduction

`Hydra` (specifically THC-Hydra) is a very fast, highly parallelized network logon cracker built to brute-force and dictionary attack authentication services across a vast array of protocols. When penetration testers or attackers find a network service (like SSH, FTP, HTTP, RDP, or SMB) requiring credentials, Hydra is often the tool used to blindly guess passwords until access is granted.

It is an indispensable tool in the network penetration testing phase, particularly for attacking internal corporate environments where weak passwords or default credentials are rampant.

### Why Hydra?
- **Protocol Support**: Supports over 50 protocols, including HTTP(S)-FORM-GET/POST, SSH, FTP, Telnet, SMB, RDP, VNC, MySQL, PostgreSQL, and SIP.
- **Speed**: Highly parallelized C code makes it extremely fast on modern hardware.
- **Flexibility**: Can target single hosts, lists of hosts, single usernames, lists of usernames, and lists of passwords simultaneously.

## Architecture and Execution Flow

```text
+-------------------+       +-----------------------+       +-------------------+
|                   |       |                       |       |                   |
|   Wordlists       | ----> |      Hydra Engine     | ----> |   Target Service  |
| (Users, Passwords)|       |  (Parallel Threads)   |       |   (SSH, FTP, HTTP)|
|                   |       |                       |       |                   |
+-------------------+       +-----------+-----------+       +---------+---------+
                                        |                             |
                                        | 1. Connect & Authenticate   |
                                        |---------------------------->|
                                        |                             |
                                        | 2. Connection Refused       |
                                        |<----------------------------|
                                        |                             |
                                        | 3. Authenticate (Next Pass) |
                                        |---------------------------->|
                                        |                             |
                                        | 4. Success (Valid Creds)    |
                                        |<----------------------------|
```

Hydra loads the target specifications, protocol modules, and wordlists into memory. It then spawns multiple tasks based on the user-defined thread count. Each task establishes a connection to the target service using the specified protocol, attempts a username/password combination, and evaluates the response (e.g., checking for "Login incorrect" versus a successful prompt).

## Core Concepts

1. **Modules**: Hydra uses protocol-specific modules. The way it authenticates to FTP is entirely different from how it authenticates to an HTTP form.
2. **Parallelism (-t)**: The number of simultaneous connections made to the target. Too high, and the service will crash or drop packets. Too low, and the attack takes forever.
3. **Wordlists (-L, -P)**: The success of Hydra depends entirely on the quality of the wordlists used (e.g., `rockyou.txt` or custom generated lists).

## Installation and Setup

Hydra is natively installed on Kali Linux and Parrot OS.
For Debian-based systems:
```bash
sudo apt-get update
sudo apt-get install hydra
```
If you need the GUI version (though the CLI is highly recommended for stability and scriptability):
```bash
sudo apt-get install hydra-gtk
```

## Detailed Usage and Methodology

### Basic Syntax
The standard syntax for Hydra is:
```bash
hydra [OPTIONS] -l <username> -p <password> <target_IP> <protocol>
```

### Attack Vectors

1. **Single User, Wordlist for Passwords**:
   Useful when you know a valid username (like `root` or `admin`) and want to guess the password.
   ```bash
   hydra -l admin -P /usr/share/wordlists/rockyou.txt 192.168.1.100 ssh
   ```

2. **Wordlist for Users, Single Password (Password Spraying)**:
   Highly effective in Active Directory environments to avoid account lockouts. You try a common password (like `Summer2023!`) against a list of hundreds of users.
   ```bash
   hydra -L users.txt -p 'Summer2023!' 192.168.1.100 smb
   ```

3. **Wordlist for Both (Cluster Bomb)**:
   Attempts every combination of user and password. This is extremely noisy and slow.
   ```bash
   hydra -L users.txt -P passwords.txt 192.168.1.100 ftp
   ```

### Tuning Performance and Reliability

- `-t <num>`: Set the number of parallel tasks (default is 16). For fragile services like RDP, drop this to 4.
  ```bash
  hydra -t 4 -l admin -P passwords.txt 192.168.1.100 rdp
  ```
- `-V` or `-vV`: Very verbose mode. Shows every attempt as it happens. Essential for troubleshooting if the module is actually working.
- `-f`: Exit after the first valid pair is found. Highly recommended when you only need one foothold.
- `-s <port>`: Specify a non-standard port.
  ```bash
  hydra -s 2222 -l root -P passwords.txt 192.168.1.100 ssh
  ```

### Advanced: HTTP Form Brute-Forcing

Brute-forcing web login pages requires specific syntax to tell Hydra where to POST the data, what the parameters are, and how to identify a failed login.

The format for the `http-post-form` module is:
`"<URI>:<Form_Parameters>:<Failure_String>"`

```bash
hydra -l admin -P passwords.txt 192.168.1.100 http-post-form "/login.php:user=^USER^&pass=^PASS^:F=Login failed"
```
- `^USER^` and `^PASS^` are placeholders Hydra replaces dynamically.
- `F=Login failed` tells Hydra that if it sees "Login failed" in the HTML response, the guess was wrong.

*Tip: For complex web logins, Burp Suite Intruder or `ffuf` is often preferred over Hydra due to better handling of CSRF tokens and complex headers.*

### Resuming Sessions
If an attack takes days, you can restore a stopped session using the `.hydra/hydra.restore` file.
```bash
hydra -R
```

## Security and Ethical Considerations
- **Account Lockouts**: Brute-forcing heavily will lock out accounts in environments with password policies (e.g., AD). Password spraying (one password across many users) is safer.
- **Service Disruption**: High thread counts (`-t 64`) against legacy services (like old Telnet or FTP servers) can cause Denial of Service (DoS) by exhausting connection pools.
- **Noise**: Hydra is the opposite of stealthy. It generates massive authentication failure logs on the target system.

## Chaining Opportunities
- Use `enum4linux` or [[14 - CrackMapExec NetExec]] to harvest valid usernames from SMB, then feed that list into Hydra to attack SSH.
- If Hydra compromises an SSH or RDP credential, use it to pivot into the internal network.
- Use [[08 - Feroxbuster]] to find hidden login pages, then point Hydra's `http-post-form` module at them.

## Related Notes
- [[14 - CrackMapExec NetExec]]
- [[08 - Feroxbuster]]
- [[01 - Burp Suite]]
