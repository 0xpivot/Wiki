---
tags: [vapt, methodology, recon, beginner]
difficulty: beginner
module: "04 - VAPT Methodology"
topic: "04.03 Reconnaissance Phase"
---

# 04.03 — Reconnaissance Phase

## What is it?

Reconnaissance (recon) is the first phase of any assessment — gathering information about the target before any active testing. The more you know about your target, the more targeted and effective your attacks will be. Recon is split into passive (no direct interaction with target) and active (interact with target, potentially detectable).

---

## Phase Overview

```
RECONNAISSANCE PHASES:
  
  PASSIVE (OSINT):          ACTIVE:
  ┌─────────────┐           ┌──────────────────────┐
  │ No contact  │           │ Direct interaction   │
  │ with target │           │ Target may detect    │
  │             │           │                      │
  │ - Shodan    │           │ - DNS enumeration    │
  │ - crt.sh    │           │ - Port scanning      │
  │ - WHOIS     │           │ - Web crawling       │
  │ - Google    │           │ - Banner grabbing    │
  │ - LinkedIn  │           │ - Directory brute    │
  └─────────────┘           └──────────────────────┘
        |                           |
        └─────────┬─────────────────┘
                  ▼
        INTELLIGENCE GATHERED:
        - IP ranges and infrastructure
        - Subdomains and virtual hosts
        - Technologies and versions
        - Employees and emails
        - Historical data and leaks
```

---

## Passive Recon: OSINT Techniques

```bash
# DOMAIN AND IP ENUMERATION

# WHOIS - domain ownership:
whois target.com
# Reveals: registrar, registrant (if not private), nameservers, creation date

# DNS records:
dig target.com ANY +short
dig target.com MX
dig target.com TXT   # SPF/DKIM records → email providers used!
host -t ns target.com

# Reverse DNS (find hostnames for IP ranges):
for ip in $(seq 1 254); do host 10.10.10.$ip 2>/dev/null; done

# CERTIFICATE TRANSPARENCY LOGS (find subdomains!)
curl -s "https://crt.sh/?q=%.target.com&output=json" | \
  python3 -c "import json,sys; [print(x['name_value']) for x in json.load(sys.stdin)]" | \
  sort -u > subdomains.txt

# Shodan (scan results without touching target):
shodan search "hostname:target.com"
shodan host <ip>
# Reveals: open ports, services, banners, historical data!

# SecurityTrails / Censys (historical DNS):
# securitytrails.com → find old IPs (before CDN was added!)
# censys.io → comprehensive internet scan data

# Google Dorks:
site:target.com                    → all indexed pages
site:target.com -www              → find subdomains
inurl:admin site:target.com       → admin pages
filetype:pdf site:target.com      → exposed documents
intext:"internal use only" site:target.com → internal docs leaked
"target.com" filetype:sql         → SQL dumps
"target.com" "password"           → password files

# Wayback Machine (archived versions):
curl "https://web.archive.org/cdx/search/cdx?url=*.target.com&output=json" | \
  python3 -m json.tool | grep "urlkey"
# Historical URLs → deleted pages, old endpoints, old API versions!
```

---

## Passive Recon: Employee and Credential Intelligence

```bash
# LinkedIn (employees = attack targets for phishing, password spraying):
# Search: site:linkedin.com "target company" "security engineer"
# Reveals: names, job titles, tech stack from job descriptions

# HaveIBeenPwned (check if target emails in breaches):
# https://haveibeenpwned.com/DomainSearch (bulk, needs API)
curl -s https://haveibeenpwned.com/api/v3/breacheddomain/target.com

# GitHub (code leaks, credentials in public repos):
# site:github.com "target.com" "password"
# site:github.com "target.com" "api_key"
# site:github.com "target.com" "secret"
# Tools: gitrob, truffleHog, gitleaks

# Job postings (reveal tech stack!):
# LinkedIn, Indeed, Glassdoor → "Java Spring Boot", "Redis", "PostgreSQL"
# → Exact versions in job requirements!
```

---

## Active Recon: Subdomain Enumeration

```bash
# DNS brute force (most effective):
gobuster dns -d target.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt
ffuf -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt \
  -u https://FUZZ.target.com -mc 200,301,302,403

# Subfinder (aggregates multiple sources):
subfinder -d target.com -o subdomains.txt

# Amass (comprehensive, OSINT + brute):
amass enum -d target.com -o amass-results.txt

# Virtual host discovery (same IP, different Host header):
gobuster vhost -u https://target.com -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt
ffuf -w subdomains.txt -H "Host: FUZZ.target.com" -u https://target.com -mc 200

# Zone transfer (DNS misconfig → full subdomain list):
dig axfr @ns1.target.com target.com  # Often blocked but worth trying!
```

---

## Active Recon: Web Fingerprinting

```bash
# Technology detection:
whatweb -a 3 https://target.com   # -a 3 = aggressive
wappalyzer --url=https://target.com (CLI version)

# HTTP headers fingerprinting:
curl -sI https://target.com | grep -iE "server|x-powered-by|x-generator|x-aspnet"

# Web application fingerprinting:
nikto -h https://target.com    # basic scan + fingerprint
wafw00f https://target.com     # WAF detection

# Directory and file enumeration:
gobuster dir -u https://target.com -w /usr/share/seclists/Discovery/Web-Content/common.txt
ffuf -u https://target.com/FUZZ -w /usr/share/seclists/Discovery/Web-Content/directory-list-2.3-medium.txt -mc 200,301,302,403

# JavaScript file analysis (find API endpoints, keys):
# Download all JS files → grep for endpoints, secrets
curl -s https://target.com | grep -oP 'src="[^"]+"' | sed 's/src="//' | sed 's/"//'
```

---

## Recon Checklist

```
DOMAIN INTELLIGENCE:
  [ ] WHOIS data
  [ ] DNS records (A, AAAA, MX, TXT, CNAME, NS)
  [ ] Zone transfer attempt
  [ ] Certificate transparency (crt.sh)
  [ ] Historical DNS (SecurityTrails)

INFRASTRUCTURE:
  [ ] IP ranges (WHOIS, BGP lookups: bgp.he.net)
  [ ] Cloud provider (AWS/Azure/GCP IP ranges)
  [ ] CDN detection (Cloudflare, Fastly, Akamai)
  [ ] Origin IP discovery (bypass CDN)

APPLICATIONS:
  [ ] All subdomains enumerated
  [ ] Virtual hosts on same IP
  [ ] Technology fingerprinting
  [ ] Directory brute force
  [ ] JavaScript analysis

PEOPLE:
  [ ] Employee names and emails
  [ ] GitHub code exposure
  [ ] Credential leaks (HIBP)
  [ ] Job postings (tech stack)
```

---

## Related Notes
- [[04 - Scanning and Enumeration Phase]] — next phase
- [[Module 05 - Recon]] — full recon module with all tools
- [[01.15 - CDNs Content Delivery Networks]] — CDN origin IP discovery
- [[01.18 - Certificates and Certificate Authorities]] — crt.sh usage
