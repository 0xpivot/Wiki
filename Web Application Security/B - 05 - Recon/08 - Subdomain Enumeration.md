---
tags: [vapt, recon, beginner]
difficulty: beginner
module: "05 - Recon"
topic: "05.08 Subdomain Enumeration (amass, subfinder, assetfinder)"
---

# 05.08 — Subdomain Enumeration

## What is it?

Subdomain enumeration discovers all subdomains of a target domain. Subdomains often host forgotten apps, development environments, admin panels, and older software with vulnerabilities. Every subdomain is a separate attack surface — and often the weakest link.

---

## Why Subdomains Matter

```
target.com          → main site, probably well-hardened
api.target.com      → API → different codebase, different team
dev.target.com      → DEVELOPMENT SERVER! → weak auth, debug mode!
staging.target.com  → staging → often with real data!
admin.target.com    → admin panel → high value!
old.target.com      → forgotten → old software → unpatched CVEs!
vpn.target.com      → VPN portal → credential attacks
mail.target.com     → email server
jenkins.target.com  → CI/CD → source code access!
grafana.target.com  → monitoring → credentials, internal info
jira.target.com     → project management → internal info
git.target.com      → code repository → source code!
```

---

## Passive Subdomain Discovery

```bash
# SUBFINDER (aggregates multiple sources):
subfinder -d target.com -o subfinder-output.txt
subfinder -d target.com -silent | httpx -status-code
# Sources: Certspotter, CertDB, CommonCrawl, crt.sh, GitHub,
#          HackerTarget, PassiveDNS, Shodan, VirusTotal, etc.

# ASSETFINDER (focused on passive sources):
assetfinder --subs-only target.com

# AMASS (most comprehensive — all sources):
amass enum -passive -d target.com -o amass-passive.txt
# Takes longer but more comprehensive

# GITHUB SUBLIST3R (multiple search engines):
sublist3r -d target.com -o sublist3r-output.txt -t 50

# FINDOMAIN:
findomain -t target.com -u findomain-output.txt

# CROBAT (RAPID7 SONAR project):
crobat -s target.com
```

---

## Certificate Transparency (Best Passive Source)

```bash
# CRT.SH (free, no API key needed):
curl -s "https://crt.sh/?q=%.target.com&output=json" | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
names = set()
for cert in data:
    for name in cert['name_value'].split('\n'):
        names.add(name.strip())
for name in sorted(names):
    print(name)
" > crt-subdomains.txt

# Filter wildcards and clean:
grep -v "^\*\." crt-subdomains.txt | sort -u > clean-subs.txt

# FACEBOOK CT (different data set):
curl -s "https://api.facebook.com/certificates?query=target.com&fields=domains&limit=10000" | \
  python3 -c "import json,sys; d=json.load(sys.stdin); [print(x) for cert in d.get('data',[]) for x in cert.get('domains',[])]"
```

---

## Active Subdomain Brute Force

```bash
# GOBUSTER DNS:
gobuster dns \
  -d target.com \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt \
  -t 100 \
  -o gobuster-dns.txt

# FFUF DNS mode:
ffuf -u https://FUZZ.target.com \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt \
  -mc 200,301,302,403 \
  -t 100

# MASSDNS (fastest, needs list with full domains):
cat /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt | \
  awk '{print $1".target.com"}' > dns-bruteforce-list.txt
massdns -r /usr/share/massdns/lists/resolvers.txt \
  -t A -o S dns-bruteforce-list.txt -w massdns-output.txt

# AMASS active mode (brute + permutations):
amass enum -active -brute -d target.com \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt \
  -o amass-active.txt

# Wordlists to use (in order of effectiveness):
# 1. /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt
# 2. /usr/share/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt
# 3. /usr/share/seclists/Discovery/DNS/dns-Jhaddix.txt
# 4. Custom wordlist from app-specific terms (app name, products, etc.)
```

---

## Permutation-Based Enumeration

```bash
# ALTDNS (generate permutations of known subdomains):
# If you found: api.target.com, dev.target.com, staging.target.com
# Altdns generates: dev-api.target.com, api-dev.target.com, etc.

altdns -i found-subs.txt -o permutations.txt \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt

# GOTATOR:
gotator -sub found-subs.txt -perm permutations-wordlist.txt > permuted-subs.txt

# DNSGEN:
cat found-subs.txt | dnsgen - | massdns -r resolvers.txt -t A -o S -
```

---

## Post-Discovery: Validation and Probing

```bash
# HTTPX (probe which subdomains are live HTTP):
cat all-subdomains.txt | httpx \
  -status-code -title -tech-detect -follow-redirects \
  -o live-subdomains.txt

# HTTPROBE (simpler alternative to httpx):
cat all-subdomains.txt | httprobe

# EYE-WITNESS (screenshot live subdomains for visual review):
eyewitness -f live-subdomains.txt --web

# AQUATONE (screenshots + analysis):
cat all-subdomains.txt | aquatone -out aquatone-report/

# NUCLEI (scan all live subdomains for common vulns):
nuclei -l live-subdomains.txt -t ~/nuclei-templates/cves/ -o nuclei-results.txt
```

---

## Subdomain Takeover

```bash
# IF subdomain CNAME points to unclaimed external service:
dig old.target.com CNAME +short
# → old.target.com → target.github.io
# → GitHub Pages site doesn't exist!

# VERIFY TAKEOVER POSSIBLE:
curl -s http://old.target.com
# "There isn't a GitHub Pages site here" → TAKEOVER POSSIBLE!

# TOOLS:
subjack -w all-subdomains.txt -t 100 -ssl -v -o takeover-results.txt
subzy run --targets all-subdomains.txt

# COMMON TAKEOVER SERVICES:
# GitHub Pages, Heroku, Netlify, Surge, Unbounce
# Fastly, AWS S3, Azure, Shopify
# See: can-i-take-over-xyz.github.io
```

---

## Full Workflow

```bash
#!/bin/bash
DOMAIN=$1

# Passive sources:
subfinder -d $DOMAIN -silent > passive-subs.txt
assetfinder --subs-only $DOMAIN >> passive-subs.txt
curl -s "https://crt.sh/?q=%.${DOMAIN}&output=json" | \
  python3 -c "import json,sys; [print(x['name_value']) for x in json.load(sys.stdin)]" >> passive-subs.txt

# Active brute force:
gobuster dns -d $DOMAIN \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt \
  -t 100 -q >> passive-subs.txt

# Deduplicate:
sort -u passive-subs.txt > all-subs.txt

# Probe live:
cat all-subs.txt | httpx -silent -status-code > live-subs.txt

echo "Done! $(wc -l < all-subs.txt) total, $(wc -l < live-subs.txt) live"
```

---

## Related Notes
- [[07 - DNS Enumeration]] — DNS details
- [[09 - Certificate Transparency Logs]] — CT log sources
- [[28 - Virtual Host Enumeration]] — same IP, different hostnames
- [[26 - CDN Detection and Origin IP Discovery]] — CDN bypass via subdomain
