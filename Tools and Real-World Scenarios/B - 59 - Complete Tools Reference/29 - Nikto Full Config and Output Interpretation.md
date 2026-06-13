---
tags: [tools, web-testing, scanner, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.29 Nikto Full Config"
---

# Nikto: Full Configuration and Output Interpretation

## 1. Introduction and Core Concepts
Nikto is one of the oldest, most established open-source web server scanners in the cybersecurity industry. Written in Perl, Nikto performs comprehensive tests against web servers for multiple items, including over 7000 potentially dangerous files/programs, checks for outdated versions of over 1250 servers, and version specific problems on over 270 servers. It also checks for server configuration items such as the presence of multiple index files, HTTP server options, and attempts to identify installed web servers and software.

Despite its age, Nikto remains highly relevant because it catches misconfigurations, default files, and legacy vulnerabilities that modern, SPA-focused dynamic scanners often miss. However, because it relies on heavy, noisy dictionary-based brute-forcing, running it with default settings in a modern environment will almost certainly trigger Web Application Firewalls (WAFs) or Intrusion Prevention Systems (IPS). Understanding how to configure and interpret Nikto is essential.

## 2. How the Tool Works (Internal Mechanics)
Nikto is essentially a massive, highly structured HTTP client that runs sequentially through a flat database of signatures (located in `nikto_*.plugin` and `db_*.db` files). 

It begins with an aggressive reconnaissance phase: fetching the Server header, testing HTTP methods (OPTIONS, PUT, TRACE), and evaluating cookies for security flags. Next, it moves into the enumeration phase, brute-forcing directories and files based on its extensive databases. It uses heuristic checks to identify false-positive 404s (where a server returns a 200 OK for a non-existent page, often called a "soft 404").

### ASCII Diagram: Nikto Execution Flow

```text
[ Target Web Server: http://target.com ]
          ^
          | HTTP Requests
+---------------------------------------------------+
| Nikto Core Engine (Perl)                          |
|                                                   |
| +-----------------------------------------------+ |
| | 1. Pre-Flight Checks                          | |
| | - Server Header Grab (Apache? Nginx? IIS?)    | |
| | - Soft 404 Detection (Heuristic baseline)     | |
| | - HTTP Method Enumeration (OPTIONS, TRACE)    | |
| +-----------------------------------------------+ |
|          |                                        |
| +-----------------------------------------------+ |
| | 2. Database Execution Phase                   | |
| | - db_tests (7000+ signatures)                 | |
| | - db_outdated (Version checks)                | |
| | - db_variables (Default CGI, config files)    | |
| +-----------------------------------------------+ |
|          |                                        |
| +-----------------------------------------------+ |
| | 3. Evasion & Mutation (If Configured)         | |
| | - URL encoding, directory traversal injection | |
| +-----------------------------------------------+ |
+---------------------------------------------------+
          |
          v
[ Formatted Output: Txt, XML, HTML, CSV ]
```

## 3. Installation & Setup
Nikto is pre-installed on Kali Linux and most penetration testing distributions. However, keeping its database updated is crucial.

```bash
# Update Nikto databases to the latest version
nikto -update

# Run a basic check to verify
nikto -Version
```

If you are installing it manually from GitHub:
```bash
git clone https://github.com/sullo/nikto
cd nikto/program
perl nikto.pl -h http://example.com
```

## 4. Basic Usage & Common Flags
The simplest way to use Nikto is to point it at an IP address or hostname.

```bash
# Standard scan against a host
nikto -h 192.168.1.50

# Scan a specific port with SSL
nikto -h https://example.com -p 443

# Scan multiple ports
nikto -h 10.0.0.5 -p 80,443,8080,8443
```

### Core CLI Flags:
- `-h, -host`: Target host (IP or FQDN).
- `-p, -port`: Target port(s).
- `-ssl`: Force SSL mode on the port.
- `-Tuning`: Control which types of tests are executed.
- `-evasion`: Employ IDS/WAF evasion techniques.
- `-Format`: Output format (csv, htm, txt, xml).
- `-output`: Write output to a specific file.
- `-maxtime`: Maximum time (in seconds) the scan should run.

## 5. Advanced Configuration & Tuning
Running Nikto without tuning is generally a bad idea on production systems; it generates tens of thousands of requests.

### 5.1 Tuning Categories (The `-Tuning` Flag)
You can dramatically speed up Nikto and reduce noise by telling it exactly what to look for. The `-Tuning` flag uses a numbered system:
- `1` - Interesting File / Seen in logs
- `2` - Misconfiguration / Default File
- `3` - Information Disclosure
- `4` - Injection (XSS/Script/HTML)
- `5` - Remote File Retrieval - Inside Web Root
- `6` - Denial of Service
- `7` - Remote File Retrieval - Server Wide
- `8` - Command Execution / Remote Shell
- `9` - SQL Injection
- `0` - File Upload
- `a` - Authentication Bypass
- `b` - Software Identification
- `x` - Reverse Tuning Options (Exclude instead of Include)

**Example:** Run only Information Disclosure, Misconfigurations, and Command Execution checks:
```bash
nikto -h http://example.com -Tuning 238
```

**Example:** Run everything *except* Denial of Service (Crucial for production environments):
```bash
nikto -h http://example.com -Tuning x 6
```

### 5.2 Evasion Techniques
If you are testing behind an IDS or basic WAF, Nikto can mutate its requests. The `-evasion` flag uses numbered techniques:
- `1` - Random URI encoding (non-UTF8)
- `2` - Directory self-reference (`/./`)
- `3` - Premature URL ending
- `4` - Prepend long random string
- `5` - Fake parameter
- `6` - TAB as request spacer
- `7` - Change the case of the URL
- `8` - Use Windows directory separator (`\`)

**Example:** Use directory self-reference and random URI encoding:
```bash
nikto -h http://example.com -evasion 12
```

### 5.3 Authentication
Nikto can scan directories protected by Basic or NTLM authentication.
```bash
nikto -h http://example.com -id admin:password123
```

## 6. Output Formats & Interpretation
Nikto provides terminal output in real-time, but for reporting, you must use the `-Format` flag.

```bash
nikto -h http://example.com -Format xml -output nikto_report.xml
nikto -h http://example.com -Format htm -output nikto_report.html
```

### 6.1 Interpreting Output (False Positives)
Nikto is notorious for false positives, especially regarding "Soft 404s". 
If a server returns an HTTP 200 OK for every request (e.g., a Single Page Application redirecting everything to `index.html`), Nikto might claim it found 7,000 vulnerabilities.

**Red Flags to look for in output:**
- `OSVDB-XXXX: /phpmyadmin/: phpMyAdmin directory found` -> Highly critical, verify manually.
- `Allowed HTTP Methods: GET, HEAD, POST, PUT, DELETE, TRACE` -> Indicates severe misconfiguration, TRACE implies Cross-Site Tracing (XST).
- `Server leaks internal IP` -> Often found in IIS headers.

## 7. Real-world Scenarios
### 7.1 Legacy Corporate Environments
In internal penetration tests (Active Directory environments), you frequently encounter forgotten Tomcat servers, old Apache installs on IoT devices, or neglected printer management interfaces. Nikto shines here. Running Nikto against a `/24` subnet on port 80 and 8080 often uncovers `manager/html` interfaces with default credentials or exposed `phpinfo.php` files that modern scanners overlook because they don't brute-force legacy file paths as aggressively.

### 7.2 Discovering Git/SVN Exposures
Nikto has specific checks for `.git/config` and `.svn/entries`. Finding these allows an attacker to dump the entire source code repository of the web application.

## 8. Chaining Opportunities
Nikto is rarely used as a standalone automated exploit tool; it is a pointer tool.

1. **Nmap** -> Discover open HTTP/HTTPS ports across a subnet.
2. **Nikto** -> Feed the live IPs into Nikto to find low-hanging fruit (default files, exposed admin panels).
3. **Metasploit** -> If Nikto identifies an outdated Tomcat server (e.g., Tomcat 7), load the corresponding Metasploit module (`exploit/multi/http/tomcat_mgr_upload`) to gain a reverse shell.

### Nmap to Nikto Automation:
```bash
nmap -p80,443 192.168.1.0/24 -oG nmap.txt
cat nmap.txt | grep open | awk '{print $2}' > ips.txt
for ip in $(cat ips.txt); do nikto -h $ip -Tuning 238 -Format txt -output nikto_$ip.txt; done
```

## 9. Configuration File (`nikto.conf`)
For permanent tuning, edit `/etc/nikto.conf`.
Key parameters to modify:
- `USERAGENT`: Change the default Nikto user-agent to avoid instant blocking by WAFs.
  ```text
  USERAGENT=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36
  ```
- `MAX_WARN`: Lower this to prevent terminal flooding if the site returns soft 404s.

## 10. Related Notes
- [[04 - API4 — Lack of Resources & Rate Limiting]] - Nikto is extremely noisy and can test a server's rate-limiting capabilities.
- [[30 - Nuclei Writing Custom Templates]] - Nuclei is effectively the modern, YAML-based successor to Nikto.
- [[07 - API7 — Security Misconfiguration]] - The primary vulnerability category that Nikto identifies.
