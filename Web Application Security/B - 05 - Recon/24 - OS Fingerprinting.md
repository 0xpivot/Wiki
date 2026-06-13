---
tags: [vapt, recon, intermediate]
difficulty: intermediate
module: "05 - Recon"
topic: "05.24 OS Fingerprinting"
---

# 05.24 — OS Fingerprinting

## What is it?

OS fingerprinting determines the operating system running on a target host. Knowing the OS narrows the attack surface dramatically — Windows hosts have different vulnerabilities than Linux, and different Linux distros have different package versions. OS information directs you toward platform-specific exploits and configurations.

---

## How OS Fingerprinting Works

```
ACTIVE FINGERPRINTING:
  Send specially crafted TCP/IP packets → observe responses
  Different OSes implement TCP/IP stack slightly differently:
  
  PROBE TYPE              WHAT IT TESTS
  TCP ISN Sampling      → How the OS generates sequence numbers
  IP ID Sampling        → How IP identification numbers increment
  TCP Options           → Which TCP options the OS supports (window size, timestamp, SACK)
  TCP Timestamp         → Timestamp behavior
  RST Flag              → How the OS sends TCP resets
  ICMP Echo             → Response to ICMP packets
  
  Nmap compares response fingerprint against a DB of 5000+ OS signatures!

PASSIVE FINGERPRINTING:
  Analyze traffic already flowing without sending extra packets
  Tools: p0f, Ettercap, NetworkMiner
  Works on captured pcap files too!
```

---

## Nmap OS Detection

```bash
# BASIC OS DETECTION:
sudo nmap -O target.com

# AGGRESSIVE (more accurate, more intrusive):
sudo nmap -O --osscan-guess target.com

# WITH INTENSITY:
sudo nmap -O --osscan-limit target.com   # only scan likely targets
sudo nmap --fuzzy target.com             # = --osscan-guess

# COMBINED WITH VERSION + SCRIPTS:
sudo nmap -A target.com    # = -O -sV -sC --traceroute

# EXAMPLE OUTPUT:
# OS DETECTION RESULTS:
# Running: Linux 4.X|5.X
# OS CPE: cpe:/o:linux:linux_kernel:4 cpe:/o:linux:linux_kernel:5
# OS details: Linux 4.15 - 5.6
# Network Distance: 1 hop
#
# Running: Microsoft Windows 10|2016|2019
# OS CPE: cpe:/o:microsoft:windows
# OS details: Microsoft Windows 10 1903 - 20H2 or Windows Server 2016

# NOTE: Requires root/sudo for raw packet manipulation
# If no root: nmap -A still attempts some OS guessing via TCP behavior
```

---

## TTL-Based OS Guessing

TTL (Time To Live) in IP packets is set differently by default per OS.

```
DEFAULT INITIAL TTL VALUES:
  64  → Linux, macOS, iOS, Android, FreeBSD
  128 → Windows (all versions)
  255 → Solaris, network devices (Cisco IOS, F5)
  
HOW TO USE:
  ping target.com → note the TTL in the reply
  
  TTL received: 59  → 64 - 5 hops = started at 64 → LINUX!
  TTL received: 121 → 128 - 7 hops = started at 128 → WINDOWS!
  TTL received: 250 → 255 - 5 hops = started at 255 → NETWORK DEVICE!

QUICK CHECK:
  ping -c 1 target.com | grep ttl
  # 64 bytes from 203.0.113.1: icmp_seq=1 ttl=56 time=14.2 ms
  # TTL 56 → started at 64 → Linux (8 hops away)

WITH CURL:
  curl -sI https://target.com --resolve "target.com:443:IP" | head
  # Check HTTP headers for OS hints instead
```

---

## p0f (Passive OS Fingerprinting)

```bash
# INSTALL:
apt install p0f

# LISTEN ON INTERFACE:
sudo p0f -i eth0

# ANALYZE PCAP FILE:
sudo p0f -r capture.pcap

# OUTPUT EXAMPLE:
# [+] Detected connection from 203.0.113.1
#     OS: Linux 3.11 - 4.x
#     Dist: 4 hops
#     Link: Ethernet or modem

# DAEMONIZE WITH LOG:
sudo p0f -i eth0 -o /var/log/p0f.log -d

# USEFUL FOR:
# - Passive fingerprinting (zero packets sent!)
# - Works on captured traffic (pcap)
# - IDS/IPS won't detect it (no outbound probes)
```

---

## Web Application OS Clues

Even without port scanning, HTTP responses often leak OS information:

```bash
# HTTP HEADERS REVEALING OS:
curl -sI https://target.com

# LINUX INDICATORS:
Server: Apache/2.4.41 (Ubuntu)     → Ubuntu Linux
Server: Apache/2.4.37 (centos)     → CentOS Linux
Server: nginx/1.14.0 (Ubuntu)      → Ubuntu Linux
X-Powered-By: PHP/7.4.3            → often Linux (more common on Linux)

# WINDOWS INDICATORS:
Server: Microsoft-IIS/10.0         → Windows Server 2016/2019!
X-Powered-By: ASP.NET              → Windows Server with IIS!
X-AspNet-Version: 4.0.30319        → Windows with .NET!
Set-Cookie: ASP.NET_SessionId=     → Windows/.NET stack!
NTLM auth in WWW-Authenticate →    → Windows AD environment!

# PATH SEPARATORS IN ERRORS:
# Windows paths: C:\inetpub\wwwroot\index.asp
# Linux paths: /var/www/html/index.php

# CAUSE ERRORS TO REVEAL PATHS:
curl https://target.com/NONEXISTENT_FILE_12345
# "C:\inetpub\wwwroot\NONEXISTENT_FILE_12345" → Windows!
# "/var/www/html/NONEXISTENT_FILE_12345" → Linux!

# FILE CASING (Linux is case-sensitive, Windows is not):
curl -sI https://target.com/INDEX.PHP    # try uppercase
curl -sI https://target.com/index.php
# If both return 200 → Windows (case-insensitive)!
# If only lowercase returns 200 → Linux (case-sensitive)!
```

---

## Metasploit OS Detection

```bash
# WITHIN METASPLOIT:
msfconsole

use auxiliary/scanner/portscan/tcp
set RHOSTS target.com
set PORTS 22,80,443
run

# AFTER PORT SCAN:
use auxiliary/scanner/ssh/ssh_version
set RHOSTS target.com
run
# [+] 10.0.0.1:22 - SSH server version: SSH-2.0-OpenSSH_7.6p1 Ubuntu-4ubuntu0.3

# SMBD (SMB OS detection - Windows):
use auxiliary/scanner/smb/smb_version
set RHOSTS target.com
run
# [+] 10.0.0.1:445 Windows 10 Pro 19041 (x64) (name:PC) (domain:WORKGROUP)
```

---

## OS-Specific Attack Implications

```
LINUX DISCOVERED:
  → Check SSH version → old OpenSSH → user enumeration
  → Look for CGI files → Shellshock (CVE-2014-6271)?
  → Check for exposed .bash_history, .bashrc
  → Kernel version for local privilege escalation
  → Check NFS exports: showmount -e target.com
  
WINDOWS DISCOVERED:
  → IIS version → WebDAV? ASP.NET debug mode?
  → RPC/DCOM services → EternalBlue, EternalRomance
  → SMB → MS17-010 (EternalBlue)?
  → RDP → BlueKeep (CVE-2019-0708)?
  → NTLM authentication? → relay attacks
  
WINDOWS SERVER 2003/2008:
  → Likely unpatched! High probability of MS08-067, MS17-010
  
LINUX KERNEL 2.6.x:
  → Dirty Cow (CVE-2016-5195) privilege escalation!
  
NETWORK DEVICE (TTL≈255):
  → Default credentials?
  → Cisco IOS version → specific CVEs
  → SNMP community strings (public/private)?
```

---

## CPE (Common Platform Enumeration)

Nmap outputs CPE strings which are machine-readable OS/service identifiers.

```
CPE FORMAT: cpe:/type:vendor:product:version
  cpe:/o:linux:linux_kernel:4.15     → Linux kernel 4.15
  cpe:/o:microsoft:windows_10:1903   → Windows 10 1903
  cpe:/a:apache:http_server:2.4.41   → Apache 2.4.41
  cpe:/a:mysql:mysql:5.7.36          → MySQL 5.7.36

USE CPE TO FIND CVEs:
  # NVD CVE search by CPE:
  curl "https://services.nvd.nist.gov/rest/json/cves/2.0?cpeName=cpe:2.3:a:apache:http_server:2.4.49:*:*:*:*:*:*:*"

  # vulners by CPE:
  curl "https://vulners.com/api/v3/burp/software/?software=apache&version=2.4.49&type=software"
```

---

## Related Notes
- [[21 - Port Scanning with Nmap]] — port scanning
- [[22 - Banner Grabbing]] — service banner extraction
- [[23 - Service Version Detection]] — version fingerprinting
- [[Module 08 - Network Infrastructure]] — network-level attacks
