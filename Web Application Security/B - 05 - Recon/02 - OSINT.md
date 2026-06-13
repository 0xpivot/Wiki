---
tags: [vapt, recon, osint, beginner]
difficulty: beginner
module: "05 - Recon"
topic: "05.02 OSINT — Open Source Intelligence"
---

# 05.02 — OSINT

## What is it?

OSINT (Open Source Intelligence) is intelligence gathered from publicly available sources. In VAPT, OSINT reveals infrastructure details, technology stacks, employee information, historical configurations, and sometimes credentials — all without touching the target directly.

---

## OSINT Categories and Tools

```
CATEGORY          WHAT YOU FIND                   TOOLS
─────────────────────────────────────────────────────────────
Domain/DNS        Subdomains, nameservers,         WHOIS, dig, SecurityTrails
                  IP addresses, DNS history        Passive DNS, ViewDNS.info

Infrastructure    Exposed services, ports,         Shodan, Censys, FOFA
                  service banners, server OS       Zoomeye, GreyNoise

Certificates      Subdomains, certificate          crt.sh, Cert.sh, Facebook CT
                  history, SANs

Archives          Old endpoints, deleted pages,    Wayback Machine
                  historical configs               CachedView, Cachedpage

Code Repos        Credentials, API keys,           GitHub, GitLab (public repos)
                  internal URLs, algorithms        TruffleHog, Gitrob

Breached Data     Emails in breaches,              HaveIBeenPwned, DeHashed
                  leaked passwords                 Snusbase, WeLeakInfo

Social/People     Employee names, tech stack,      LinkedIn, Twitter
                  internal tools                   Glassdoor, job boards

Business          Company structure, acquisitions, Crunchbase, OpenCorporates
                  subsidiaries (expanded scope)    LinkedIn, Companies House
```

---

## Key OSINT Techniques

```bash
# HAVE I BEEN PWNED — check company email domain:
# https://haveibeenpwned.com/DomainSearch
# API: 
curl -H "hibp-api-key: <KEY>" \
  "https://haveibeenpwned.com/api/v3/breacheddomain/target.com"
# Tells you: how many accounts from target.com are in breaches!
# If many breaches → password reuse likely → password spraying opportunity!

# HUNTER.IO — find employee email addresses:
# https://hunter.io/
curl "https://api.hunter.io/v2/domain-search?domain=target.com&api_key=YOUR_KEY"
# Returns: emails found online for the domain, email format pattern!
# Email format: firstname.lastname@target.com → now you can guess all emails!

# THEHARVESTOR — aggregated email/subdomain finding:
theHarvester -d target.com -b all -l 500
# Searches: Google, Bing, LinkedIn, Twitter, Shodan, etc.
# Returns: emails, subdomains, hosts, IPs, URLs

# MALTEGO — visual OSINT graph (GUI tool):
# Maps relationships between domains, IPs, people, emails
# Community edition is free

# OSINT INDUSTRIES / INTELLIGENCE FRAMEWORK:
# osintframework.com — categorized links to all OSINT resources
```

---

## GitHub OSINT

```bash
# Search GitHub for target:
# https://github.com/search?q=target.com&type=code

# Common patterns to search:
site:github.com "target.com" "password"
site:github.com "target.com" "api_key"
site:github.com "target.com" "secret"
site:github.com "target.com" "internal"
site:github.com target.com ".env"
site:github.com target.com "database_url"

# Search GitHub API:
curl "https://api.github.com/search/code?q=target.com+password&sort=indexed" \
  -H "Authorization: token YOUR_GITHUB_TOKEN"

# GitLeaks — scan repos for secrets:
gitleaks detect --source /path/to/cloned/repo -v

# TruffleHog — scan GitHub user/org:
trufflehog github --org=TargetOrg --token=YOUR_TOKEN

# Gitrob — search user/org repos for sensitive files:
gitrob analyze user/org
```

---

## LinkedIn OSINT

```
WHAT TO FIND:
  1. Employee names and job titles
     → "Security Engineer at Target Corp" → tech stack knowledge
     → "Formerly at Target Corp" → may still have access
  
  2. Job postings (company posts these):
     "Looking for React developer familiar with our Redis + PostgreSQL stack"
     → Reveals: React (frontend), Redis (caching/sessions), PostgreSQL (database)
     
     "Kubernetes + AWS EKS experience required"
     → Container orchestration on AWS! → cloud attack surface!
  
  3. Tech stack from employee LinkedIn profiles:
     "Skills: Spring Boot, Kubernetes, PostgreSQL, Redis, RabbitMQ"
     → Full backend tech map!
  
  4. Network connections → org structure
     → Who reports to who → social engineering targets

TOOLS:
  LinkedIn Sales Navigator (paid but powerful)
  Linked-Recon: LinkedIn OSINT without account
  CrossLinked: generate email lists from LinkedIn
    crosslinked -f 'first.last@target.com' -j "Target Corp"
    → Generates likely email addresses!
```

---

## Breach Data Analysis

```bash
# DEHASHED (breach database search):
# https://dehashed.com/
# Paid service but very comprehensive

# FREE ALTERNATIVES:
# https://breachdirectory.org/ - check emails
# https://intelx.io/ - indexed breach data
# https://haveibeenpwned.com/ - individual check, free

# WHAT TO DO WITH BREACH DATA:
# 1. Find employee emails in breach database
# 2. Get hashed or plaintext passwords
# 3. Try cracking hashes:
hashcat -m 0 hashes.txt rockyou.txt    # MD5
hashcat -m 100 hashes.txt rockyou.txt  # SHA-1
hashcat -m 3200 hashes.txt rockyou.txt # bcrypt (slow!)

# 4. Test cracked passwords on target:
#    - VPN portal
#    - Email (OWA, webmail)
#    - LinkedIn login (to access company Slack?)
#    - SSH (if keys reused)
#    - Admin portals discovered during recon

# ETHICAL NOTE:
# Using breach data must be within scope and authorization
# Some engagement RoEs explicitly allow password spraying
```

---

## Passive Infrastructure Intelligence

```bash
# REVERSE IP LOOKUP — who else is on this server:
host target.com  # get IP
# Then: https://api.hackertarget.com/reverseiplookup/?q=<IP>
# → Other domains hosted on same IP → shared hosting → side-channel!

# BGP/ASN LOOKUP — IP ranges owned by target:
# https://bgp.he.net/
whois -h whois.radb.net -- '-i origin AS12345'  # get prefixes for ASN
# → Find all IP ranges! → scan these for exposed services!

# ROBTEX — all-in-one network OSINT:
# https://www.robtex.com/

# NETCRAFT — site report:
# https://sitereport.netcraft.com/?url=https://target.com
# → Hosting history, OS, web server, SSL cert details!
```

---

## Related Notes
- [[01 - Passive vs Active Recon]] — recon categories
- [[03 - Google Dorking]] — search engine OSINT
- [[11 - GitHub Dorking for Secrets]] — code repo OSINT
- [[12 - LinkedIn and Employee OSINT]] — people intelligence
