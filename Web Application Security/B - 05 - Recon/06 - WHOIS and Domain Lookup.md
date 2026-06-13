---
tags: [vapt, recon, osint, beginner]
difficulty: beginner
module: "05 - Recon"
topic: "05.06 WHOIS and Domain Lookup"
---

# 05.06 — WHOIS and Domain Lookup

## What is it?

WHOIS is a query protocol that reveals domain registration information — who owns a domain, when it was registered, nameservers, and contact information. In VAPT, WHOIS data reveals the target's infrastructure, helps identify related domains, and sometimes reveals direct contact info for social engineering or responsible disclosure.

---

## WHOIS Data Fields

```
whois target.com

RESPONSE:
  Domain Name: TARGET.COM
  Registry Domain ID: 123456789_DOMAIN_COM-VRSN
  Registrar WHOIS Server: whois.registrar.com
  Registrar URL: http://www.registrar.com
  Updated Date: 2024-01-15T10:00:00Z    ← recent change? why?
  Creation Date: 2010-03-22T14:33:00Z   ← how long established?
  Registry Expiry Date: 2025-03-22T14:33:00Z  ← expiry near? hijack?
  
  Registrar: GoDaddy.com, LLC           ← registrar
  
  Registrant Organization: Target Corp   ← company name
  Registrant Country: US
  
  Name Server: ns1.targetdns.com        ← authoritative nameserver
  Name Server: ns2.targetdns.com        ← zone transfer target!
  
  DNSSEC: unsigned                      ← no DNSSEC!
  
  Registrant Email: domains@target.com  ← often hidden now (GDPR)
  Admin Email: admin@target.com
  Tech Email: tech@target.com
```

---

## VAPT-Relevant WHOIS Findings

```
1. NAMESERVER IDENTIFICATION:
   Name Server: ns1.targetdns.com
   → Try zone transfer: dig axfr @ns1.targetdns.com target.com
   → Hosting DNS yourself? → DDoS target!

2. REGISTRATION DATE:
   Creation: 2010 → established company
   Creation: 2024 → new domain? → phishing? → no established security?
   
3. EXPIRY DATE (near!):
   Registry Expiry: 2024-04-01
   → Domain about to expire!
   → Domain hijacking possible if they forget to renew!
   → Register expired domain → intercept emails, subdomains!
   
4. REGISTRAR:
   GoDaddy, Namecheap → popular but public registrars
   → Sometimes registrar accounts are weaker link
   → Social engineering registrar to transfer domain (rare but real)

5. ORGANIZATION NAME:
   → Verify this matches the target you're testing
   → If it doesn't → you might be testing the wrong company!
```

---

## DNS Lookup Deep Dive

```bash
# ALL record types:
dig target.com ANY +short

# Specific record types:
dig target.com A     +short  → IPv4 address
dig target.com AAAA  +short  → IPv6 address
dig target.com MX    +short  → mail servers
dig target.com NS    +short  → nameservers
dig target.com TXT   +short  → SPF, DKIM, verification records
dig target.com CNAME +short  → canonical name (alias)
dig target.com SOA   +short  → Start of Authority (zone info)
dig target.com CAA   +short  → Certificate Authority Authorization

# What MX records reveal:
dig target.com MX +short
# → aspmx.l.google.com (G Suite email)
# → target-com.mail.protection.outlook.com (Office 365)
# → mail.target.com (self-hosted)
# → amazonses.com (AWS SES)
# Each reveals different attack surface!

# What TXT records reveal:
dig target.com TXT +short
# → "v=spf1 include:mailchip.com include:salesforce.com ~all"
# REVEALS: they use MailChimp + Salesforce → attack via these services!
# → "google-site-verification=xxx" → using Google services
# → "stripe-verification=xxx" → using Stripe
# → "MS=xxx" → Microsoft Office 365 setup

# Reverse DNS (PTR record):
dig -x 203.0.113.1 +short  → find hostname for IP
# Or: host 203.0.113.1
```

---

## Zone Transfer Attempt

```bash
# Get nameservers first:
dig target.com NS +short
# → ns1.target.com
# → ns2.target.com

# Attempt zone transfer (AXFR):
dig axfr @ns1.target.com target.com

# If successful: ENTIRE DNS zone!
# All subdomains, internal hostnames, internal IPs!

# Most modern nameservers reject AXFR from unauthorized IPs.
# But older/misconfigured ones still allow it!

# Check if any nameserver allows it:
for ns in $(dig target.com NS +short); do
  echo "=== Testing $ns ==="
  dig axfr @$ns target.com | head -20
done
```

---

## WHOIS for IP Addresses

```bash
# IP WHOIS (who owns this IP):
whois 203.0.113.1
# Reveals: organization, country, IP range, abuse contact

# Critical for verifying target IP is theirs:
# If WHOIS says "Cloudflare Inc" → the IP belongs to Cloudflare!
# If WHOIS says "Amazon" → AWS IP, not target's IP
# Only the IP that WHOIS says belongs to target → scan it!

# ARIN (American Registry for Internet Numbers):
whois -h whois.arin.net 203.0.113.1

# RIPE (European Registry):
whois -h whois.ripe.net 185.220.101.1

# Online tools:
# https://www.whois.com/whois/
# https://www.arin.net/resources/registry/whois/
# https://ipinfo.io/203.0.113.1
```

---

## Historical WHOIS and DNS

```bash
# SECURITYTRAILS (historical DNS + WHOIS):
# https://securitytrails.com/
# Reveals: past IP addresses, past nameservers, past MX records

# Why historical DNS matters:
# Company moved to Cloudflare 6 months ago.
# Old IP: 203.0.113.1 (before Cloudflare)
# New IP: Cloudflare
# 
# If old IP still serves the app → origin IP found → bypass Cloudflare!
# SecurityTrails shows historical A records → find old IP!

# VIEWDNS.INFO (multiple lookups):
# Reverse DNS, historical data, IP location
# https://viewdns.info/reverseip/?host=203.0.113.1
# → All domains hosted on same IP!
```

---

## Related Notes
- [[07 - DNS Enumeration]] — deeper DNS analysis
- [[08 - Subdomain Enumeration]] — finding subdomains
- [[26 - CDN Detection and Origin IP Discovery]] — using historical DNS for bypass
