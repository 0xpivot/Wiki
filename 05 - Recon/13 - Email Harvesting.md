---
tags: [vapt, recon, osint, beginner]
difficulty: beginner
module: "05 - Recon"
topic: "05.13 Email Harvesting (theHarvester)"
---

# 05.13 — Email Harvesting

## What is it?

Email harvesting collects email addresses associated with a target domain from publicly available sources — search engines, LinkedIn, data breaches, DNS, and public code repositories. Collected emails are used for phishing assessment, password spraying, social engineering identification, and breach checking.

---

## theHarvester

```bash
# INSTALL:
pip3 install theHarvester
# OR use Kali/ParrotOS (pre-installed)

# BASIC USAGE:
theHarvester -d target.com -b google

# ALL SOURCES:
theHarvester -d target.com -b all -l 500 -f harvest-results.html

# SPECIFIC SOURCES:
theHarvester -d target.com -b linkedin
theHarvester -d target.com -b github
theHarvester -d target.com -b shodan
theHarvester -d target.com -b twitter

# OPTIONS:
-d target.com   → target domain
-b all          → all search engines/sources
-l 500          → limit results to 500
-f filename     → save to file (html or xml)
-n              → perform DNS lookup on found hosts
-v              → verify host names via DNS

# WHAT IT FINDS:
  - Email addresses
  - Hosts/subdomains
  - IP addresses (via host lookup)
  - Virtual hosts
```

---

## SOURCES theHarvester Uses

```
SEARCH ENGINE SOURCES:
  google, bing, yahoo, duckduckgo, brave, baidu

SPECIALIZED SOURCES:
  github → GitHub public repos
  linkedin → LinkedIn public profiles (limited without credentials)
  shodan → Shodan host data
  censys → Censys certificate data
  hunter → Hunter.io email finding
  twitterapi → Twitter mentions

DATA BROKER SOURCES:
  dnsdumpster → DNS and subdomain data
  crtsh → Certificate transparency
  hackertarget → DNS, IP, host data
  intelx → Intelligence X database
  anubis → DNS brute-force
  rapiddns → Rapid DNS historical
  securitytrails → Historical DNS
```

---

## Hunter.io

```bash
# WEB INTERFACE: https://hunter.io/
# Finds emails AND the email format pattern!

# API (50 free searches/month):
# Find all emails for domain:
curl "https://api.hunter.io/v2/domain-search?domain=target.com&api_key=YOUR_KEY" | \
  python3 -m json.tool

# Response includes:
# - List of found emails
# - Email format pattern: {first}.{last}@target.com
# - Confidence score per email
# - Sources where found

# WHAT THIS TELLS YOU:
# Email format: {first}.{last} → john.smith@target.com
# → Now generate ALL employee emails:
awk '{
  first=tolower($1)
  last=tolower($2)
  print first"."last"@target.com"
}' employees.txt > emails.txt
```

---

## Email Enumeration from SMTP

```bash
# SMTP USER ENUMERATION (if port 25 open):

# VRFY command (verify if user exists):
nc target.com 25
VRFY admin
> 252 admin@target.com (may work on older servers)

# RCPT TO (many SMTP servers don't distinguish user vs domain):
RCPT TO:<admin@target.com>

# SMTP-USER-ENUM TOOL:
smtp-user-enum -M VRFY -U users.txt -t target.com
smtp-user-enum -M RCPT -U users.txt -t target.com -D target.com

# Nmap script:
nmap --script smtp-enum-users target.com -p 25 \
  --script-args smtp-enum-users.methods={VRFY,RCPT,EXPN}

# NOTE: Most modern SMTP servers block enumeration.
# Works against older Microsoft Exchange servers (pre-2010).
```

---

## Email in Job Postings and Web Pages

```bash
# GREP EMAIL ADDRESSES FROM WEB PAGES:
curl -s https://target.com | grep -oP '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'

# EXTRACT FROM WEBSITE (recursive):
wget -r --no-parent -l 2 https://target.com -q -O - | \
  grep -oP '[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}' | sort -u

# FROM GOOGLE CACHE:
googler -n 100 "site:target.com email" | grep "@target.com"

# FROM LINKEDIN (job postings):
# Often HR email is visible in job post applications
# "Please send CV to hr@target.com"

# FROM GITHUB COMMITS:
git log --format='%aN <%aE>' | sort -u | grep "@target.com"
# → Shows all Git authors with target.com emails!
```

---

## Email Breach Checking

```bash
# HAVE I BEEN PWNED (per email):
curl -H "hibp-api-key: YOUR_KEY" \
  "https://haveibeenpwned.com/api/v3/breachedaccount/john.smith@target.com"

# BATCH CHECK (with rate limiting):
while read email; do
  result=$(curl -s -H "hibp-api-key: YOUR_KEY" \
    "https://haveibeenpwned.com/api/v3/breachedaccount/$email")
  if [ "$result" != "" ]; then
    echo "$email: BREACHED"
    echo "$result" | python3 -m json.tool | grep "Name"
  fi
  sleep 1.5  # rate limit: max 1 req/1.5 seconds
done < emails.txt
```

---

## Related Notes
- [[12 - LinkedIn and Employee OSINT]] — finding employees
- [[02 - OSINT]] — OSINT framework
- [[04.07 - Post-Exploitation Phase]] — using creds found from emails
