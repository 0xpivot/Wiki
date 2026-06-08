---
tags: [vapt, recon, dns, beginner]
difficulty: beginner
module: "05 - Recon"
topic: "05.07 DNS Enumeration (dig, nslookup, dnsx)"
---

# 05.07 — DNS Enumeration

## What is it?

DNS enumeration extracts information about a domain's DNS infrastructure: all subdomains, IP addresses, mail servers, and any information leak in DNS records. DNS is often overlooked but reveals significant infrastructure detail.

---

## DNS Record Types Reference

```
A       → IPv4 address (192.168.1.1)
AAAA    → IPv6 address (2001:db8::1)
CNAME   → Canonical name/alias (www → target.com)
MX      → Mail server (priority + hostname)
NS      → Nameserver
TXT     → Text data (SPF, DKIM, DMARC, verification)
SOA     → Start of Authority (zone settings, serial number)
PTR     → Reverse DNS (IP to hostname)
SRV     → Service locator (_sip._tcp.target.com → SIP server)
CAA     → Which CAs can issue certs for this domain
HINFO   → Host info (OS/CPU — rarely set, leaks info if set!)
LOC     → Geographic location (rarely set)
NAPTR   → Naming Authority Pointer (used in VoIP)
```

---

## dig Command Reference

```bash
# Basic lookup:
dig target.com          → A record (IPv4)
dig target.com A        → explicit A record
dig target.com MX       → mail server
dig target.com NS       → nameservers
dig target.com TXT      → text records (SPF, DKIM, verification)
dig target.com AAAA     → IPv6
dig target.com ANY      → all records (some servers block this)

# Format options:
dig target.com +short   → just the answer
dig target.com +noall +answer  → only answer section
dig target.com A @8.8.8.8     → use specific resolver (Google DNS)
dig target.com A @ns1.target.com  → ask authoritative server directly

# Reverse lookup:
dig -x 203.0.113.1 +short  → IP → hostname
dig -x 203.0.113.1 @8.8.8.8 → use specific resolver

# Zone transfer:
dig axfr @ns1.target.com target.com  → AXFR (full zone)
dig ixfr @ns1.target.com target.com  → IXFR (incremental)

# MX analysis:
dig target.com MX +short
# Priority + Hostname:
# 10 aspmx.l.google.com → Google Workspace
# 20 mail.target.com    → self-hosted secondary

# SPF analysis:
dig target.com TXT +short | grep "spf"
# "v=spf1 include:sendgrid.net include:mailchimp.com ~all"
# → Third-party mail services used!
```

---

## Email Infrastructure from DNS

```bash
# MX RECORDS REVEAL EMAIL PROVIDER:
dig target.com MX +short

# INTERPRETATION:
# *.google.com or *.googlemail.com → Google Workspace (formerly G Suite)
# *.protection.outlook.com → Microsoft 365
# *.amazonses.com → Amazon SES (bulk email only)
# *.mimecast.com → Mimecast (email security)
# mail.target.com → Self-hosted (interesting!)

# SPF RECORD (who can send email as target.com):
dig target.com TXT +short | grep "v=spf"
# "v=spf1 include:mailchimp.com include:salesforce.com include:sendgrid.net ~all"
# → MailChimp, Salesforce, SendGrid can spoof as target.com!
# → If you compromise these → send phishing as target.com!

# DMARC RECORD:
dig _dmarc.target.com TXT +short
# "v=DMARC1; p=reject; rua=mailto:dmarc@target.com"
# p=none  → no enforcement → easy to spoof!
# p=reject → strict → hard to spoof

# DKIM (per selector):
dig selector1._domainkey.target.com TXT +short
# If missing or weak → email spoofing possible!
```

---

## DNS Brute Force Tools

```bash
# DNSX (fast DNS resolver):
dnsx -l wordlist.txt -d target.com -a -aaaa -cname
cat subdomains.txt | dnsx -resp    # resolve list of subdomains

# FIERCE (older but reliable):
fierce --domain target.com

# GOBUSTER DNS mode:
gobuster dns -d target.com \
  -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt \
  -t 50 -o gobuster-dns.txt

# MASSDNS (ultra-fast):
massdns -r /usr/share/massdns/lists/resolvers.txt \
  -t A \
  -o S \
  wordlist_with_domain.txt > massdns-output.txt

# Generate wordlist with domain prepended:
awk '{print $1".target.com"}' \
  /usr/share/seclists/Discovery/DNS/subdomains-top1million-110000.txt \
  > dns-wordlist.txt

# AMASS (most comprehensive):
amass enum -passive -d target.com -o amass-passive.txt
amass enum -active -d target.com -o amass-active.txt  # DNS brute
```

---

## DNSSEC Analysis

```bash
# Check if DNSSEC is enabled:
dig target.com DS +short   → if empty → no DNSSEC parent delegation
dig target.com DNSKEY +short  → if empty → DNSSEC not configured

# DNSSEC validation:
dig target.com A +dnssec @8.8.8.8
# Look for "ad" flag in flags → Authenticated Data = DNSSEC verified!

# DNSSEC attacks (if not enabled):
# DNS cache poisoning possible (Kaminsky attack)
# Man-in-the-middle DNS responses possible

# Check NSEC/NSEC3 for zone walking:
dig target.com NSEC   → if returned → zone walking possible!
# Zone walking reveals ALL subdomains in the zone!
```

---

## Interesting DNS Findings

```bash
# SUBDOMAIN TAKEOVER VIA DANGLING CNAME:
dig deleted.target.com CNAME +short
# → deleted.target.com → target.github.io
# → If target.github.io is unclaimed → subdomain takeover!
# Check: curl -s deleted.target.com | grep "There isn't a GitHub Pages site here"

# INTERNAL HOSTNAMES LEAKED:
# Sometimes internal DNS resolves externally:
dig internal-app.target.com A +short
# → 10.10.10.5 (private IP!) → internal service exists!

# CLOUD METADATA REVEALED:
dig api.target.com CNAME +short
# → elasticbeanstalk.amazonaws.com → hosted on AWS Elastic Beanstalk!
# Now you know → AWS-specific attacks, IAM issues

# SERVICE DISCOVERY VIA SRV:
dig _http._tcp.target.com SRV +short
dig _sip._tcp.target.com SRV +short
dig _xmpp-server._tcp.target.com SRV +short
```

---

## Related Notes
- [[06 - WHOIS and Domain Lookup]] — domain ownership
- [[08 - Subdomain Enumeration]] — finding more subdomains
- [[28 - Virtual Host Enumeration]] — vhost discovery on same IP
