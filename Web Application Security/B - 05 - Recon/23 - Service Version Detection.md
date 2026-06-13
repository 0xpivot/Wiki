---
tags: [vapt, recon, intermediate]
difficulty: intermediate
module: "05 - Recon"
topic: "05.23 Service Version Detection"
---

# 05.23 — Service Version Detection

## What is it?

Service version detection goes beyond just knowing a port is open — it determines the exact software name, version number, and configuration. This enables targeted vulnerability research: a precise version number maps directly to known CVEs and exploits.

---

## Nmap Version Detection

```bash
# -sV ENABLES SERVICE/VERSION DETECTION:
nmap -sV target.com

# VERSION INTENSITY LEVELS (0–9):
nmap -sV --version-intensity 0 target.com   # lightest (fast, less accurate)
nmap -sV --version-intensity 5 target.com   # DEFAULT
nmap -sV --version-intensity 9 target.com   # most thorough (slow but complete)

# ALL PROBES (may be intrusive):
nmap -sV --version-all target.com

# LIGHTWEIGHT ALTERNATIVE:
nmap -sV --version-light target.com         # = intensity 2

# FULL AGGRESSIVE SCAN (version + OS + scripts):
nmap -A target.com

# SAMPLE OUTPUT:
# 22/tcp  open  ssh      OpenSSH 8.2p1 Ubuntu 4ubuntu0.3
# 80/tcp  open  http     nginx 1.18.0 (Ubuntu)
# 443/tcp open  ssl/http nginx 1.18.0 (Ubuntu)
# 3306/tcp open mysql    MySQL 5.7.36-0ubuntu0.18.04.1
# 8080/tcp open http     Jetty 9.4.31.v20200723
```

---

## WhatWeb (HTTP Service Fingerprinting)

```bash
# BASIC FINGERPRINT:
whatweb https://target.com

# AGGRESSIVE (more requests, better coverage):
whatweb -a 3 https://target.com

# DETAILED OUTPUT:
whatweb -v https://target.com

# MULTIPLE TARGETS:
whatweb -i targets.txt -a 3 --log-csv=results.csv

# OUTPUT FORMATS:
whatweb https://target.com --log-json=whatweb.json

# EXAMPLE OUTPUT:
# https://target.com [200 OK] 
#   Apache[2.4.41]
#   Bootstrap[4.5.2]
#   JQuery[3.5.1]
#   PHP[7.4.3]
#   WordPress[5.8.3]
#   Ubuntu
#   HTTPServer[Ubuntu Linux][Apache/2.4.41 (Ubuntu)]
```

---

## Masscan (Fastest Port Scanner)

```bash
# INSTALL:
apt install masscan

# FAST SCAN (1 million packets/sec — very fast!):
masscan -p1-65535 target.com --rate=1000000

# TOP 100 PORTS:
masscan -p$(python3 -c "
import nmap
nm = nmap.PortScanner()
print(','.join(map(str, nm.scan('127.0.0.1','--top-ports 100')['tcp'].keys())))
") target.com --rate=10000

# OUTPUT TO FILE:
masscan -p1-65535 192.168.1.0/24 --rate=10000 -oX masscan.xml
masscan -p1-65535 192.168.1.0/24 --rate=10000 -oL masscan.txt

# COMBINE WITH NMAP:
# First: masscan for fast open port discovery
masscan -p1-65535 target.com --rate=10000 -oL ports.txt

# Parse masscan output → run nmap version scan on open ports only:
grep "open" ports.txt | awk '{print $4}' | sort -u > open-ports.txt
nmap -sV -sC -p $(cat open-ports.txt | tr '\n' ',') target.com
```

---

## HTTPx (HTTP Service Fingerprinting)

```bash
# INSTALL:
go install -v github.com/projectdiscovery/httpx/cmd/httpx@latest

# BASIC SCAN:
echo "target.com" | httpx

# WITH TECHNOLOGY DETECTION:
echo "target.com" | httpx -tech-detect

# TITLE + STATUS + SERVER:
echo "target.com" | httpx -title -status-code -web-server

# FULL INFO:
echo "target.com" | httpx -title -status-code -web-server -tech-detect -follow-redirects

# FROM SUBDOMAINS LIST:
cat subdomains.txt | httpx -title -status-code -web-server -tech-detect -o httpx-results.txt

# EXAMPLE OUTPUT:
# https://target.com [200] [Target Homepage] [nginx/1.18.0] [Bootstrap,jQuery,WordPress]
# https://api.target.com [200] [API Gateway] [Express] [Node.js]
# https://admin.target.com [403] [Forbidden] [Apache/2.4.41]

# FILTER BY STATUS:
cat subdomains.txt | httpx -mc 200,301,302,401,403

# SCREENSHOT (with headless browser):
cat subdomains.txt | httpx -screenshot -o screenshots/
```

---

## CMSmap (CMS Version Detection)

```bash
# INSTALL:
git clone https://github.com/dionach/CMSmap.git

# BASIC SCAN (auto-detect CMS):
python3 cmsmap.py https://target.com

# SPECIFY CMS:
python3 cmsmap.py https://target.com -f W  # WordPress
python3 cmsmap.py https://target.com -f J  # Joomla
python3 cmsmap.py https://target.com -f D  # Drupal
python3 cmsmap.py https://target.com -f M  # Moodle

# OUTPUT:
python3 cmsmap.py https://target.com -o output.txt
```

### WordPress-Specific (WPScan)

```bash
# INSTALL:
gem install wpscan

# VERSION DETECTION:
wpscan --url https://target.com --enumerate

# WITH API TOKEN (CVE lookup):
wpscan --url https://target.com --enumerate --api-token YOUR_TOKEN

# PLUGIN ENUMERATION:
wpscan --url https://target.com --enumerate p --plugins-detection aggressive

# USER ENUMERATION:
wpscan --url https://target.com --enumerate u

# BRUTE FORCE (if authorized!):
wpscan --url https://target.com -U admin -P /usr/share/wordlists/rockyou.txt

# DETECTS:
# WordPress core version
# All installed plugins + versions
# All installed themes + versions  
# Usernames (via /wp-json/wp/v2/users)
# Known CVEs per component
```

---

## SSL/TLS Version Detection

```bash
# SSLSCAN (comprehensive TLS analysis):
sslscan target.com

# SHOWS:
# Supported TLS versions (1.0, 1.1, 1.2, 1.3)
# Cipher suites (ECDHE-RSA-AES256-GCM-SHA384, etc.)
# Heartbleed vulnerable?
# Certificate details

# TESTSSL.SH (most thorough):
./testssl.sh target.com
./testssl.sh --full target.com
./testssl.sh --severity HIGH target.com

# NMAP TLS:
nmap --script=ssl-enum-ciphers target.com -p 443
nmap --script=ssl-heartbleed target.com -p 443  # Heartbleed
nmap --script=ssl-dh-params target.com -p 443   # LOGJAM
nmap --script=ssl-poodle target.com -p 443      # POODLE

# OPENSSL:
openssl s_client -connect target.com:443 -tls1   2>&1 | head -1  # TLS 1.0
openssl s_client -connect target.com:443 -tls1_1 2>&1 | head -1  # TLS 1.1
# "CONNECTED" = supported (weak!)
```

---

## Service-Specific Version Commands

```bash
# MYSQL:
nmap --script=mysql-info target.com -p 3306
mysql -h target.com -e "SELECT VERSION();" 2>/dev/null

# POSTGRESQL:
psql -h target.com -U postgres -c "SELECT version();" 2>/dev/null

# REDIS:
redis-cli -h target.com INFO server | grep redis_version

# MONGODB:
mongo target.com --eval "db.version()" --quiet

# ELASTICSEARCH:
curl -s http://target.com:9200/ | python3 -m json.tool
# → {"version": {"number": "7.10.0"}}

# APACHE TOMCAT:
curl -sI http://target.com:8080/ | grep -i "server"
curl -s http://target.com:8080/manager/html  # Manager app → version!

# JENKINS:
curl -sI http://target.com:8080/ | grep "X-Jenkins:"
# X-Jenkins: 2.319.3
```

---

## CVE Research Workflow

```bash
# AFTER FINDING A VERSION:
# 1. SEARCHSPLOIT (local Exploit-DB):
searchsploit apache 2.4.49
searchsploit openssl 1.0.1

# 2. NATIONAL VULNERABILITY DATABASE:
# https://nvd.nist.gov/vuln/search

# 3. VULNERS (API-based):
curl "https://vulners.com/api/v3/search/lucene/?query=Apache+2.4.49"

# 4. SHODAN CVE SEARCH:
shodan search "apache 2.4.49 CVE"

# 5. GITHUB PoC SEARCH:
# site:github.com CVE-2021-41773 exploit

# 6. NUCLEI TEMPLATES:
nuclei -u https://target.com -t ~/nuclei-templates/cves/ -o cve-results.txt

# AUTOMATE VERSION → CVE MAPPING:
# Tools: vulnx, vulscan, metasploit search
msfconsole -q -x "search type:exploit apache 2.4.49; exit"
```

---

## Related Notes
- [[21 - Port Scanning with Nmap]] — finding open ports
- [[22 - Banner Grabbing]] — extracting banners manually
- [[24 - OS Fingerprinting]] — OS detection
- [[14 - Technology Fingerprinting]] — web tech detection
