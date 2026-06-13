---
tags: [vapt, methodology, scanning, beginner]
difficulty: beginner
module: "04 - VAPT Methodology"
topic: "04.04 Scanning and Enumeration Phase"
---

# 04.04 — Scanning and Enumeration Phase

## What is it?

Scanning and enumeration transforms the list of discovered targets (from recon) into a detailed map of attack surfaces: open ports, running services, versions, web directories, and parameters. This phase makes active contact with the target and may be detectable.

---

## Port Scanning

```
WHAT IT IS:
  Probe each port (0-65535) to see if a service is listening.
  
  TCP PORT STATES:
  OPEN     → service listening, connection accepted
  CLOSED   → port reachable but no service
  FILTERED → firewall dropping packets (no response)
  
NMAP SCAN TYPES:
  
  SYN Scan (-sS, stealth):
    Client → SYN → Target
    Client ← SYN/ACK ← Target (if open)
    Client → RST → Target (don't complete handshake!)
    → Faster, less logged than full TCP connect
    Requires root/admin privileges

  Connect Scan (-sT):
    Full TCP handshake → more detectable
    Doesn't require root

  UDP Scan (-sU):
    Services like DNS (53), DHCP (67), SNMP (161) use UDP
    Slower → UDP has no ACK
    
  Null/FIN/Xmas (-sN, -sF, -sX):
    Send unusual flag combinations → evade some firewalls
    Response determines if port is open|closed|filtered
```

---

## Nmap: Essential Commands

```bash
# BASIC SCANS:

# Top 1000 ports (default):
nmap target.com

# Full port scan (all 65535):
nmap -p- target.com

# Service/version detection:
nmap -sV target.com

# OS detection:
nmap -O target.com

# Aggressive scan (OS, versions, scripts, traceroute):
nmap -A target.com

# COMBINED RECOMMENDED SCAN:
nmap -sC -sV -p- -oA nmap-output target.com
# -sC = default scripts
# -sV = service/version detection
# -p- = all ports
# -oA = output in all formats

# STEALTH SCAN (root required):
nmap -sS -T2 target.com    # T2 = slower, less detectable

# NETWORK SCAN (find live hosts):
nmap -sn 192.168.1.0/24    # ping sweep, no port scan

# SPECIFIC PORTS:
nmap -p 80,443,8080,8443,8888 target.com
nmap -p 1-1024 target.com
```

---

## Nmap Scripting Engine (NSE)

```bash
# Run all default scripts:
nmap -sC target.com

# Specific script categories:
nmap --script=vuln target.com           # Known vulnerability checks
nmap --script=auth target.com           # Auth bypass tests
nmap --script=default target.com        # Default scripts

# Specific scripts:
nmap --script=http-enum target.com -p 80  # Directory enumeration
nmap --script=ssl-heartbleed target.com   # Test for Heartbleed
nmap --script=http-headers target.com     # Show HTTP headers
nmap --script=banner target.com           # Grab service banners

# HTTP scripts:
nmap -p 80 --script=http-title,http-auth,http-methods target.com
```

---

## Web Application Scanning

```bash
# NIKTO (comprehensive web scanner):
nikto -h https://target.com
nikto -h https://target.com -Tuning x   # x = specific checks
# Reports: outdated software, dangerous files, config issues

# GOBUSTER (directory brute force):
gobuster dir \
  -u https://target.com \
  -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt \
  -x php,html,js,txt,json \  # file extensions
  -t 50 \                     # threads
  -o gobuster-output.txt

# FFUF (fast fuzzer - more flexible):
ffuf -u https://target.com/FUZZ \
  -w /usr/share/seclists/Discovery/Web-Content/common.txt \
  -mc 200,301,302,403 \      # match these status codes
  -fc 404 \                   # filter 404s
  -o ffuf-output.json -of json

# API endpoint discovery:
ffuf -u https://target.com/api/FUZZ \
  -w /usr/share/seclists/Discovery/Web-Content/api/api-endpoints.txt

# Parameter discovery:
arjun -u https://target.com/api/user --get    # GET params
arjun -u https://target.com/api/user --post   # POST params
# OR:
x8 -u https://target.com/api/user -X GET
```

---

## Service Enumeration

```bash
# HTTP banner grabbing:
curl -sI https://target.com  # server headers
curl -s https://target.com/robots.txt  # always check!
curl -s https://target.com/sitemap.xml

# SSH enumeration (version, auth methods):
ssh target.com  # see banner
nmap --script=ssh-auth-methods target.com -p 22

# FTP (sometimes misconfigured):
nmap --script=ftp-anon target.com -p 21  # anonymous login?
ftp target.com  # try anonymous:anonymous

# SMTP enumeration:
nmap --script=smtp-commands target.com -p 25
# VRFY admin → reveals valid users!

# SMB enumeration (if port 445 open):
nmap --script=smb-enum-shares,smb-enum-users target.com
smbclient -L //target.com -N   # null session
crackmapexec smb target.com --shares

# SNMP enumeration (if port 161 open):
snmpwalk -c public -v1 target.com   # default community string!
nmap --script=snmp-info target.com -p 161
```

---

## Mapping the Attack Surface

```
WHAT TO DOCUMENT AFTER SCANNING:

NETWORK:
  - Open ports and services
  - Service versions (check for CVEs immediately!)
  - OS type and version
  
WEB:
  - All discovered directories
  - All discovered files (robots.txt, sitemap.xml, backup files)
  - API endpoints
  - All input parameters

SUMMARY TABLE:
  IP          Port   Service     Version         Notes
  10.10.10.1  22     OpenSSH     8.2p1 Ubuntu   check for CVE-2020-15778
  10.10.10.1  80     Apache      2.4.41          check for CVE-2021-41773
  10.10.10.1  443    HTTPS       TLS 1.2         check cipher suites
  10.10.10.1  3306   MySQL       5.7.31          exposed! no firewall
```

---

## Related Notes
- [[03 - Reconnaissance Phase]] — previous phase
- [[05 - Vulnerability Identification Phase]] — next phase
- [[Module 05 - Recon]] — full tool usage details
- [[01.21 - Packet Structure Reading Raw Traffic]] — Nmap scan types and TCP flags
