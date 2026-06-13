---
tags: [ssh, brute-force, weak-keys, version-vulns, crypto]
difficulty: beginner
module: "35 - Network Protocol Attacks"
topic: "35.02 SSH"
---

# SSH — Brute Force, Weak Keys, Version Vulns

## 1. Introduction to Secure Shell (SSH)
Secure Shell (SSH) is a cryptographic network protocol used for secure data communication, remote command-line login, remote command execution, and other secure network services between two networked computers. It connects, via a secure channel over an insecure network, a server and a client application.

Operating by default on **TCP Port 22**, SSH was designed as a secure, encrypted replacement for legacy cleartext protocols such as Telnet, rlogin, and rsh. It provides strong authentication, protecting communications with strong cryptography.

Despite its inherently robust design, SSH implementations, server configurations, and user practices are frequently targeted by attackers. This is primarily due to the high-value access SSH provides—often granting direct root or administrative shell access to critical infrastructure.

### 1.1 The SSH Handshake and Cryptographic Protocol
Before data can be transmitted securely, the SSH client and server must negotiate parameters and establish a secure tunnel. This process includes several phases:
1. **Version Exchange:** The client and server exchange SSH version strings to ensure protocol compatibility (e.g., `SSH-2.0-OpenSSH_8.2p1`).
2. **Key Exchange (KEX):** They agree on a cryptographic algorithm for key exchange (commonly Diffie-Hellman or Elliptic Curve Diffie-Hellman) and establish a shared secret master key. This master key is used to generate session keys for symmetric encryption (like AES-GCM).
3. **Server Authentication:** The server proves its identity to the client using a host key (e.g., RSA, Ed25519). The client typically checks this key against a `known_hosts` file to prevent Man-in-the-Middle (MITM) attacks.
4. **User Authentication:** The secure tunnel is now established. Within this encrypted tunnel, the client authenticates to the server using a password, public key, keyboard-interactive, or other configured authentication methods.

## 2. ASCII Diagram: SSH Attack Vectors

```text
    [Attacker Infrastructure]
        |
        |-- 1. Automated Brute Force / Dictionary Attacks (Hydra, Ncrack)
        |      Attempts thousands of user/pass combos against Port 22.
        |
        |-- 2. Exploiting Weak/Predictable Keys (e.g., Debian PRNG flaw)
        |      Tests pre-computed finite sets of compromised private keys.
        |
        |-- 3. Version/Implementation Exploits (e.g., libssh Auth Bypass)
        |      Sends malformed packets to bypass authentication entirely.
        |
        V
    [Corporate Firewall / Perimeter] 
        | (Allows TCP Port 22)
        V
    [SSH Server (sshd)]
        |-- Validates Auth Request
        |-- If successful, spawns Shell (bash/sh)
        V
    [System Root / User Access Granted]
```

## 3. Credential Brute Force and Dictionary Attacks
The single most common attack against SSH on the public internet is attempting to systematically guess the username and password.

**The Mechanics:**
Attackers leverage automated tools to rapidly try combinations of common, default usernames (e.g., root, admin, user, test, oracle, pi) and passwords derived from massive leaked databases or comprehensive dictionaries (like `rockyou.txt` or SecLists).

**The Risk:**
If successful, the attacker gains shell access with the exact privileges of the compromised user. Because many administrators unfortunately allow direct `root` login over SSH, a successful brute force can immediately yield complete, unhindered system compromise.

**Exploitation Examples:**
Using Hydra (A fast, flexible network login cracker):
```bash
hydra -l root -P /usr/share/wordlists/rockyou.txt ssh://10.10.10.150 -t 4 -V
```
Using Ncrack (Designed specifically for high-speed network authentication cracking):
```bash
ncrack -p 22 --user root -P /usr/share/wordlists/passwords.txt 10.10.10.150
```

**Advanced Tactics (Botnets & Low-and-Slow):**
Modern SSH brute forcing is rarely conducted from a single attacker IP address. Attackers utilize distributed botnets to perform "low and slow" brute forcing. A botnet might test only a few passwords per hour from thousands of different IP addresses globally. This effectively evades standard rate-limiting, Fail2Ban setups, and account lockout policies that monitor single IP thresholds.

## 4. Weak Keys and Predictability Vulnerabilities
SSH security relies fundamentally on the unpredictability of the cryptographic keys generated. If the Random Number Generator (RNG) used during key generation is flawed, the resulting keys can be mathematically predicted or calculated.

### 4.1 The Debian OpenSSL PRNG Flaw (CVE-2008-0166)
One of the most infamous and catastrophic SSH vulnerabilities occurred in Debian-based distributions (including Ubuntu) between 2006 and 2008.

**The Flaw:**
A well-meaning package maintainer attempted to fix memory-leak warnings from an analysis tool (Valgrind) by removing lines of code in OpenSSL. Crucially, these lines were responsible for adding environmental entropy to the Pseudo-Random Number Generator (PRNG). 
As a direct result, the PRNG's seed was based *only* on the current Process ID (PID). Since standard Linux PIDs are typically limited to a maximum of 32,768, there were only 32,768 possible SSH keys generated for any given architecture, key size, and key type during that period.

**The Attack:**
Instead of brute-forcing passwords (which has millions of possibilities), an attacker could simply generate all 32,768 possible private keys. They could then systematically attempt to authenticate with each one until successful.

**Exploitation:**
Attackers utilized pre-computed databases of these weak keys. Tools like `g0tmi1k's debian-ssh` exploit pack allowed attackers to rapidly test all known vulnerable keys against a server in minutes.
```bash
python debian-ssh.py -h 10.10.10.50 -u root -k /path/to/weak_keys_dir/
```

### 4.2 Reused and Hardcoded Host Keys
In embedded systems, IoT devices, or hastily cloned Virtual Machines, SSH host keys are sometimes hardcoded into the firmware or cloned directly rather than being dynamically generated upon first boot.
If an attacker can extract the private host key from firmware or a similar device, they can perform highly effective Man-in-the-Middle (MITM) attacks against other devices sharing the same key on the network. This allows them to decrypt traffic or seamlessly impersonate the server.

## 5. Version Vulnerabilities and Implementation Flaws
While the underlying SSH protocol is mathematically secure, the specific software implementations (such as OpenSSH, Dropbear, or libssh) can contain critical, exploitable flaws in their code.

### 5.1 libssh Authentication Bypass (CVE-2018-10933)
A critical vulnerability in the `libssh` library allowed a remote attacker to bypass the authentication process entirely.

**The Mechanics:**
During the standard authentication process, the client is supposed to send an `SSH2_MSG_USERAUTH_REQUEST` message containing their credentials. However, if a malicious client prematurely sent an `SSH2_MSG_USERAUTH_SUCCESS` message instead, the vulnerable server implementation would incorrectly accept it. The server assumed the authentication had already completed successfully.

**The Impact:**
This resulted in a complete authentication bypass, granting the attacker an immediate shell session without needing any valid credentials.

### 5.2 OpenSSH Username Enumeration (CVE-2018-15473)
Certain versions of OpenSSH (prior to 7.7) were vulnerable to user enumeration due to how they inconsistently handled malformed authentication requests.

**The Mechanics:**
If a client sent a public key authentication request but intentionally malformed the packet structure, the server's response time or the specific error it returned would differ depending on whether the requested username actually existed on the system or not.

**The Impact:**
Attackers could compile a verified, valid list of users on the system. This makes subsequent brute-force attacks exponentially more targeted and efficient, as they no longer waste time guessing passwords for non-existent users.

## 6. Defensive Strategies & Mitigation

### 6.1 Securing Authentication Methods
- **Disable Password Authentication:** The single most effective defense is to completely disable passwords. Set `PasswordAuthentication no` in `/etc/ssh/sshd_config` and strictly mandate Public Key Authentication.
- **Disable Root Login:** Prevent direct root access by setting `PermitRootLogin no`. Administrators must log in as a standard, unprivileged user and use `sudo` to escalate privileges when necessary.
- **Implement Multi-Factor Authentication (MFA):** Integrate PAM (Pluggable Authentication Modules) with solutions like Google Authenticator (TOTP) or Duo Security to require a physical token or time-based code in addition to keys/passwords.

### 6.2 Network-Level Defenses
- **Change Default Port:** While technically "security through obscurity," moving SSH off Port 22 (e.g., to Port 2222 or 65022) significantly reduces background internet noise and automated botnet brute-forcing by removing the service from mass scanners' default targeting.
- **Port Knocking / Single Packet Authorization:** Require clients to send a specific, secret sequence of packets or a cryptographically signed packet before the firewall dynamically opens the SSH port for their specific IP.
- **Rate Limiting & IP Banning:** Use `iptables` rules, Fail2Ban, or `sshguard` to automatically monitor logs and temporarily or permanently block IP addresses that exhibit brute-force behavior.

### 6.3 Cryptographic Hardening
- **Disable Weak Ciphers/MACs:** Configure `sshd_config` to explicitly allow only strong, modern ciphers (e.g., `aes256-gcm@openssh.com`, `chacha20-poly1305@openssh.com`) and robust Key Exchange algorithms (e.g., `curve25519-sha256`). Deprecate older algorithms like 3DES, RC4, or SHA1.
- **Audit Authorized Keys:** Regularly audit `~/.ssh/authorized_keys` files across all user accounts to ensure no persistent backdoors have been silently added by an attacker during a prior breach.

## 7. Advanced Exploitation: Pivoting and Tunneling over SSH
Once an attacker successfully compromises an SSH account, SSH provides excellent built-in pivoting capabilities that allow the attacker to traverse deeper into the network.

### 7.1 Local Port Forwarding
Allows the attacker to tunnel access to internal services that are blocked by firewalls but accessible from the compromised SSH server.
```bash
ssh -L local_port:target_internal_ip:target_internal_port compromised_user@ssh_server_ip
```

### 7.2 Dynamic Port Forwarding (SOCKS Proxy)
Turns the compromised SSH server into a SOCKS5 proxy, allowing the attacker to route entire tools like Nmap, Burp Suite, or Metasploit directly into the internal network.
```bash
ssh -D 1080 compromised_user@ssh_server_ip
```
Attackers then configure their local tools via `proxychains` to route through `127.0.0.1:1080`.

## 8. Chaining Opportunities
- **Username Enum to Targeted Brute Force:** Use OpenSSH user enumeration vulnerabilities to find valid system accounts, then feed only those valid accounts into Hydra for a highly targeted, stealthy brute force. -> [[12 - Password Cracking Strategies]]
- **SSH Pivoting to Internal Exploitation:** Use an initial SSH foothold to create a SOCKS proxy, then safely exploit an internal, non-routable SMB vulnerability (like EternalBlue) through the proxy tunnel. -> [[08 - Pivoting and Tunneling]]
- **Key Extraction from Web Shell:** Exploit a vulnerable web application to gain RCE, read the web user's `id_rsa` file, and use it to SSH laterally to other internal backend servers. -> [[05 - Remote Code Execution]]

## 9. Related Notes
- [[01 - FTP — Anonymous Login, Bounce Attack, Credential Brute Force]]
- [[03 - Telnet — Cleartext Protocol Attacks]]
- [[08 - Pivoting and Tunneling]]
- [[13 - Cryptography Basics]]

---
*End of Note*
