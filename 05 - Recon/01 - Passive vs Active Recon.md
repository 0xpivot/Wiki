---
tags: [vapt, recon, beginner]
difficulty: beginner
module: "05 - Recon"
topic: "05.01 Passive vs Active Recon"
---

# 05.01 — Passive vs Active Recon

## What is it?

Reconnaissance is split into two categories based on whether you make direct contact with the target systems. This distinction matters both legally (passive is always fine, active may have legal implications) and operationally (active leaves log traces, passive doesn't).

---

## Passive Recon

```
DEFINITION:
  Gathering intelligence WITHOUT sending packets to the target.
  You use third-party resources — internet archives, public databases,
  search engines — that already have information about the target.
  
  Target has NO WAY to detect that you are researching them.
  No entries in target's logs.

SOURCES:
  ┌─────────────────────────────────────────────────────────┐
  │ PASSIVE RECON SOURCES                                   │
  │                                                         │
  │ Search Engines:  Google, Bing, Shodan, Censys           │
  │ DNS Data:        SecurityTrails, Passive DNS             │
  │ Certificate CT:  crt.sh, Cert.sh                        │
  │ Web Archives:    Wayback Machine (archive.org)          │
  │ Code Repos:      GitHub, GitLab (public repos)          │
  │ Social Media:    LinkedIn, Twitter                      │
  │ Breach Data:     Have I Been Pwned, DeHashed            │
  │ WHOIS:           Domain registrar records               │
  │ Job Postings:    LinkedIn, Indeed (reveals tech stack!) │
  │ Business Data:   LinkedIn, Crunchbase, OpenCorporates   │
  └─────────────────────────────────────────────────────────┘
```

---

## Active Recon

```
DEFINITION:
  Sending packets DIRECTLY to target systems.
  Target can detect activity in logs and WAF alerts.
  
  Requires authorization!
  Even "gentle" active recon like DNS lookups against target's 
  authoritative nameserver creates log entries.

ACTIVITIES:
  ┌─────────────────────────────────────────────────────────┐
  │ ACTIVE RECON ACTIVITIES                                 │
  │                                                         │
  │ Low-Impact:                                             │
  │   - DNS queries to target's nameserver                 │
  │   - HTTP HEAD requests to check if hosts exist         │
  │   - Browser page load (no exploitation)                │
  │                                                         │
  │ Medium-Impact (clearly active):                         │
  │   - Port scanning (Nmap)                               │
  │   - Directory brute forcing                            │
  │   - Subdomain brute forcing via DNS                    │
  │   - Banner grabbing                                     │
  │                                                         │
  │ High-Impact (aggressive):                              │
  │   - Vulnerability scanning (Nikto, Burp scanner)       │
  │   - Web crawling / spidering                           │
  │   - Exploitation attempts                              │
  └─────────────────────────────────────────────────────────┘
```

---

## Why the Distinction Matters

```
LEGAL:
  Passive: No legal risk (viewing public info)
  Active: Requires authorization (CFAA applies to unauthorized access)
  
  Bug bounty: active recon usually allowed on in-scope targets
  Pre-authorization: passive only!
  
OPERATIONAL (OPSEC):
  Passive: Target cannot detect → maintain stealth
  Active: Target may detect → alerts, IP blocking, evidence of intent
  
  For red team engagements: stay passive as long as possible!
  For time-boxed pentests: balance speed vs stealth

PRACTICAL WORKFLOW:
  1. PASSIVE FIRST (always)
     → Gather everything from OSINT
     → Build initial target map
  
  2. ACTIVE SECOND (with authorization)
     → Verify OSINT findings
     → Discover what OSINT missed
     → Map exact attack surface
```

---

## OSINT Framework

```
OSINT Framework (osintframework.com):
  Organized collection of OSINT resources by category:
  
  Domain/IP → Robtex, Shodan, ViewDNS, DNSlytics
  Email → EmailRep, Hunter.io, Have I Been Pwned
  Username → Sherlock, UserSearch, WhatsMyName
  Social → Social Searcher, Pipl
  Images → TinEye, Google Images
  Dark Web → Various (be careful of legal implications)

RECON-NG (framework):
  Modular recon framework (like Metasploit but for OSINT):
  recon-ng
  > marketplace install all
  > modules search domain
  > use recon/domains-hosts/shodan_hostname
  > options set SOURCE target.com
  > run
```

---

## Passive Recon Checklist

```
DOMAIN:
  [ ] WHOIS data (registrar, registrant, dates, nameservers)
  [ ] DNS records (A, AAAA, MX, TXT, CNAME, NS, SOA)
  [ ] Historical DNS via SecurityTrails
  
INFRASTRUCTURE:
  [ ] Shodan/Censys search for domain/IP
  [ ] Certificate transparency (crt.sh) for subdomains
  [ ] Reverse IP lookup (who shares this IP?)
  [ ] BGP/ASN lookup (IP ranges owned by target)
  
APPLICATIONS:
  [ ] Wayback Machine (old URLs, endpoints, content)
  [ ] Google cache of pages
  [ ] Google dorking for sensitive files
  [ ] Shodan for exposed services
  
PEOPLE/ORGANIZATION:
  [ ] LinkedIn employees, job titles, tech stacks
  [ ] GitHub public repos (code, credentials, configs)
  [ ] HaveIBeenPwned domain search (breached accounts)
  [ ] Job postings (tech stack from requirements)
```

---

## Related Notes
- [[02 - OSINT]] — full OSINT techniques
- [[04.03 - Reconnaissance Phase]] — recon in methodology context
- [[21 - Port Scanning with Nmap]] — active scanning techniques
