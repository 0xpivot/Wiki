---
tags: [vapt, recon, beginner]
difficulty: beginner
module: "05 - Recon"
topic: "05.21 Port Scanning with Nmap"
---

# 05.21 — Port Scanning with Nmap

## What is a Port Scanner?

Every server runs multiple services, each listening on a specific port number (0–65535). A port scanner sends packets to each port and interprets the response to determine:
- Is a service listening? (open / closed / filtered)
- What service is it?
- What version?
- Any known vulnerabilities?

```
CONCEPT:
  Client → SYN packet to port 80 → Server
  Server → SYN-ACK (port OPEN!)  → Client
  Client → RST (tear down)        → Server
  
  Client → SYN packet to port 23 → Server
  Server → RST (port CLOSED)      → Client
  
  Client → SYN packet to port 8443 → Firewall drops → (no response = FILTERED)
```

---

## Nmap Fundamentals

```bash
# BASIC SYNTAX:
nmap [OPTIONS] TARGET

# TARGET FORMATS:
nmap 192.168.1.1              # single IP
nmap 192.168.1.1-20           # range
nmap 192.168.1.0/24           # CIDR block
nmap scanme.nmap.org          # hostname
nmap -iL targets.txt          # from file
```

---

## Port Selection

```bash
# TOP 1000 PORTS (default — most common services):
nmap target.com

# TOP 100 PORTS (faster):
nmap --top-ports 100 target.com

# ALL 65535 PORTS (comprehensive — slow!):
nmap -p- target.com
nmap -p 1-65535 target.com

# SPECIFIC PORTS:
nmap -p 80,443,8080,8443 target.com

# SPECIFIC PORT RANGE:
nmap -p 1-1000 target.com

# COMMON WEB PORTS:
nmap -p 80,443,8080,8443,8000,8008,8888,3000,5000,4000,9000 target.com

# COMMON DB PORTS:
nmap -p 1433,3306,5432,6379,27017,5984,9200,9300 target.com
# MSSQL, MySQL, PostgreSQL, Redis, MongoDB, CouchDB, Elasticsearch
```

---

## Scan Types

```bash
# TCP SYN SCAN (default, stealthy — doesn't complete handshake):
nmap -sS target.com   # requires root/sudo

# TCP CONNECT SCAN (full handshake — no root required):
nmap -sT target.com   # use when you can't run as root

# UDP SCAN (finds DNS, SNMP, DHCP, NTP):
nmap -sU target.com   # slow! use -p for specific UDP ports
nmap -sU -p 53,161,67,123 target.com

# COMBINED TCP + UDP:
nmap -sS -sU -p T:80,443,U:53,161 target.com

# NULL, FIN, XMAS (firewall evasion — bypass stateless firewalls):
nmap -sN target.com   # NULL scan (no flags)
nmap -sF target.com   # FIN scan
nmap -sX target.com   # XMAS scan (FIN+PSH+URG)
# On closed ports: RST
# On open ports: no response (= filtered/open)
# Does NOT work on Windows (Windows sends RST for all)
```

---

## Service and Version Detection

```bash
# SERVICE VERSION DETECTION:
nmap -sV target.com
# Reveals: Apache 2.4.41, OpenSSH 7.9, nginx 1.18.0

# VERSION INTENSITY (0=light, 9=most aggressive):
nmap -sV --version-intensity 9 target.com

# COMBINE WITH SYN SCAN:
nmap -sS -sV target.com

# AGGRESSIVE MODE (OS + version + scripts + traceroute):
nmap -A target.com
# = -O -sV -sC --traceroute combined

# EXAMPLE OUTPUT:
# 22/tcp  open  ssh     OpenSSH 7.9 (protocol 2.0)
# 80/tcp  open  http    Apache httpd 2.4.41 ((Ubuntu))
# 443/tcp open  https   Apache httpd 2.4.41 ((Ubuntu))
# 8080/tcp open http    Jetty 9.4.28
```

---

## Nmap Scripting Engine (NSE)

NSE scripts automate vulnerability detection and service enumeration.

```bash
# DEFAULT SCRIPTS (safe, commonly useful):
nmap -sC target.com
# = --script=default

# SPECIFIC SCRIPT:
nmap --script=http-title target.com
nmap --script=http-headers target.com
nmap --script=http-robots.txt target.com

# SCRIPT CATEGORIES:
nmap --script=vuln target.com        # known vulnerabilities!
nmap --script=auth target.com        # authentication tests
nmap --script=brute target.com       # brute force (careful!)
nmap --script=discovery target.com   # additional discovery

# MULTIPLE SCRIPTS:
nmap --script="http-* and not brute" target.com
nmap --script="smtp-*" -p 25 target.com

# USEFUL SPECIFIC SCRIPTS:
nmap --script=http-methods target.com  # HTTP methods allowed
nmap --script=http-cors target.com     # CORS misconfiguration
nmap --script=http-auth target.com     # auth info
nmap --script=ssl-enum-ciphers target.com  # SSL/TLS ciphers
nmap --script=ssl-heartbleed target.com   # HeartBleed check
nmap --script=smb-vuln-ms17-010 target.com  # EternalBlue!
nmap --script=ftp-anon target.com          # anonymous FTP
nmap --script=rdp-enum-encryption target.com

# FULL COMBO:
nmap -sS -sV -sC -O -p- target.com --script=vuln -oA full-scan
```

---

## Speed and Timing

```bash
# TIMING TEMPLATES (T0=slowest/stealthy, T5=fastest/aggressive):
nmap -T0 target.com   # paranoid — 5 min between probes
nmap -T1 target.com   # sneaky
nmap -T2 target.com   # polite (2x slower than default)
nmap -T3 target.com   # normal (DEFAULT)
nmap -T4 target.com   # aggressive (recommended for pentests)
nmap -T5 target.com   # insane (may miss ports!)

# RATE LIMITING:
nmap --min-rate 100 target.com   # minimum 100 packets/sec
nmap --max-rate 500 target.com   # max 500 packets/sec
nmap --max-retries 1 target.com  # fewer retries = faster

# FAST SCAN OF ALL PORTS:
nmap -T4 -p- --min-rate 5000 target.com
```

---

## Output Formats

```bash
# NORMAL OUTPUT:
nmap -oN scan.txt target.com

# XML OUTPUT (for import into other tools):
nmap -oX scan.xml target.com

# GREPABLE OUTPUT (easy to parse with grep/awk):
nmap -oG scan.gnmap target.com

# ALL FORMATS SIMULTANEOUSLY:
nmap -oA scan-results target.com
# Creates: scan-results.nmap, scan-results.xml, scan-results.gnmap

# VERBOSE (more detail during scan):
nmap -v target.com
nmap -vv target.com  # even more verbose
```

---

## Real-World VAPT Workflow

```bash
# PHASE 1: FAST HOST DISCOVERY (is it alive?):
nmap -sn target.com                   # Ping scan, no port scan

# PHASE 2: FAST TOP-PORT SCAN:
nmap -T4 --top-ports 1000 -sV target.com -oA phase2-top1000

# PHASE 3: FULL PORT SCAN (background, takes longer):
nmap -T4 -p- --min-rate 5000 target.com -oA phase3-full

# PHASE 4: DETAILED SCAN ON OPEN PORTS (from phase 3):
OPEN_PORTS=$(grep "/open/" phase3-full.gnmap | grep -oP '\d+/open' | cut -d/ -f1 | tr '\n' ',')
nmap -sS -sV -sC -O -p "$OPEN_PORTS" target.com --script=vuln -oA phase4-detailed

# FINDINGS TO NOTE:
# - Non-standard ports running standard services (SSH on 2222, RDP on 3389)
# - Version numbers → check CVE databases!
# - Services that shouldn't be public (Redis, MongoDB, Elasticsearch)
# - Management interfaces (Webmin, cPanel, Plesk)
```

---

## Common Findings and Their Significance

```
PORT  SERVICE    FINDING
22    SSH        Weak cipher? Password auth? Old version?
23    Telnet     CRITICAL — cleartext! Should not exist!
25    SMTP       Open relay? Version disclosure?
53    DNS        Zone transfer? Version?
80    HTTP       Web app testing scope
443   HTTPS      TLS version, weak ciphers, cert info
445   SMB        EternalBlue, auth, shares
1433  MSSQL      Default credentials, xp_cmdshell?
3306  MySQL      Public-facing! No auth?
3389  RDP        BlueKeep? NLA? Default creds?
5432  PostgreSQL  Public-facing? Default postgres/postgres?
6379  Redis       No auth! Public-facing Redis = game over
8080  HTTP-Alt    Dev server? Admin panel? Jenkins?
8443  HTTPS-Alt   Admin SSL? Tomcat manager?
9200  Elastic     Kibana/ES no auth? All data exposed!
27017 MongoDB     No auth MongoDB = game over
```

---

## Related Notes
- [[22 - Banner Grabbing]] — manual service info extraction
- [[23 - Service Version Detection]] — deep version fingerprinting
- [[24 - OS Fingerprinting]] — OS detection techniques
- [[25 - WAF Detection]] — WAF before scanning
