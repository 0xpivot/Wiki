---
tags: [vapt, recon, intermediate]
difficulty: intermediate
module: "05 - Recon"
topic: "05.26 CDN Detection and Origin IP Discovery"
---

# 05.26 — CDN Detection and Origin IP Discovery

## What is a CDN?

A Content Delivery Network (CDN) places servers at geographic locations globally, caching content close to users. From a VAPT perspective, CDNs hide the real origin server's IP address — finding the origin IP often lets you bypass rate limiting, WAF rules, and access controls configured only on the CDN edge.

```
USER → [CDN EDGE NODE (local)] → [ORIGIN SERVER (hidden)]
         ↑
   User sees this IP (CDN IP)
   Not the real server!
   
WHY ORIGIN IP MATTERS:
  → Direct origin access bypasses CDN-level WAF
  → Rate limiting only on CDN, not origin
  → Origin may expose different services (admin panels, dev endpoints)
  → May have open ports blocked at CDN level
  → Origin IP reveals hosting provider → more infrastructure recon
```

---

## CDN Detection

```bash
# METHOD 1: IP OWNERSHIP CHECK
dig +short target.com | while read ip; do
  echo "$ip:"
  whois "$ip" | grep -E "OrgName|org-name|netname|descr" | head -2
done

# CDN IP RANGE OWNERS:
# Cloudflare, Inc.           → Cloudflare CDN
# Amazon.com, Inc.           → AWS CloudFront
# Fastly, Inc.               → Fastly CDN
# Akamai Technologies, Inc.  → Akamai CDN
# Sucuri Inc.                → Sucuri CDN/WAF
# Incapsula Inc.             → Imperva CDN
# CDNetworks, Inc.           → CDNetworks
# Limelight Networks         → Edgio CDN

# METHOD 2: HTTP HEADERS REVEALING CDN
curl -sI https://target.com

# CLOUDFLARE:
# CF-RAY: 7abc123-SIN
# Server: cloudflare

# AWS CLOUDFRONT:
# X-Amz-Cf-Id: xxxxxxxxxx
# Via: 1.1 abcd1234.cloudfront.net (CloudFront)
# X-Cache: Hit from cloudfront

# FASTLY:
# X-Served-By: cache-lax12345-LAX
# X-Cache: HIT
# Fastly-Debug-Digest

# AKAMAI:
# X-Check-Cacheable: YES
# Akamai-Cache-Status: Hit

# SUCURI:
# X-Sucuri-ID: 
# X-Sucuri-Cache: HIT

# METHOD 3: NMAP SCRIPT:
nmap --script http-headers target.com | grep -iE "cloudflare|cloudfront|akamai|fastly"
```

---

## Origin IP Discovery Techniques

### Technique 1: DNS History

```bash
# SECURITYTRAILS (historical DNS records):
# API: https://api.securitytrails.com/v1/history/target.com/dns/a
curl -s "https://api.securitytrails.com/v1/history/target.com/dns/a" \
  -H "apikey: YOUR_KEY" | python3 -m json.tool

# PASSIVE DNS DATABASES (some free):
# https://dnsdumpster.com
# https://hackertarget.com/reverse-dns-lookup/
# https://viewdns.info/iphistory/?domain=target.com

# WAYBACK MACHINE DNS:
# Old DNS records sometimes still have origin IP
```

### Technique 2: SSL Certificate Research

```bash
# SHODAN - FIND ORIGIN SERVER BY SSL CERT:
# When a CDN is added, the origin keeps the same SSL cert
# Search Shodan for servers with that SSL cert:
shodan search "ssl.cert.subject.cn:target.com" | grep -v "CDN_IP_RANGES"

# CENSYS:
# Search for: parsed.names: target.com
# Filter by: NOT in CDN IP ranges

# CERTIFICATE TRANSPARENCY:
curl -s "https://crt.sh/?q=target.com&output=json" | \
  python3 -c "
import json, sys
data = json.load(sys.stdin)
for cert in data:
    print(cert.get('ip_addresses', ''), cert.get('name_value', ''))
" 2>/dev/null
```

### Technique 3: DNS Records Other Than A

```bash
# MX RECORDS (email server often not behind CDN):
dig MX target.com +short
# mail.target.com → resolve this → often origin IP range!
nslookup mail.target.com  # → 203.0.113.5 → same /24 as origin?

# SPF RECORD (contains direct IP of mail server):
dig TXT target.com | grep spf
# v=spf1 ip4:203.0.113.1/24 include:... → origin IP range!

# TXT RECORDS (sometimes leak internal IPs):
dig TXT target.com

# NS RECORDS (check if nameservers reveal hosting):
dig NS target.com +short
# ns1.linode.com → hosted on Linode → look for Linode IPs

# SOA RECORD (email in SOA sometimes reveals hosting):
dig SOA target.com
```

### Technique 4: Subdomain Enumeration

```bash
# SUBDOMAINS OFTEN NOT BEHIND CDN:
# Find all subdomains:
subfinder -d target.com -silent | while read sub; do
  ip=$(dig +short "$sub" | head -1)
  [ -n "$ip" ] && echo "$sub → $ip"
done | sort -t'>' -k2

# LOOK FOR NON-CDN IPs:
# Cloudflare: 103.21.244.0/22, 104.16.0.0/13, 172.64.0.0/13, 198.41.128.0/17
# If a subdomain resolves to a different IP range → potential origin!

# COMMON UNPROTECTED SUBDOMAINS:
for sub in dev staging test beta api-old admin mail ftp cpanel direct origin; do
  ip=$(dig +short "$sub.target.com" | head -1)
  [ -n "$ip" ] && echo "$sub.target.com → $ip"
done

# DIRECT/ORIGIN SUBDOMAINS:
# direct.target.com
# origin.target.com
# backend.target.com
# server.target.com
```

### Technique 5: HTTP Header Leakage

```bash
# FORCE TARGET TO MAKE OUTBOUND REQUEST (SSRF-like):
# If you control a server, make target send request to it
# → your server logs the source IP = origin IP!

# PINGBACK/SSRF TO YOUR SERVER:
# Send email → check email headers for origin SMTP IP
# Submit URL to target → target fetches it → check your server access.log

# HEADERS THAT SOMETIMES LEAK ORIGIN IP:
curl -sI https://target.com | grep -iE "x-real-ip|x-origin|x-backend|x-upstream|via"
# Via: 1.1 origin-web-01 (squid/4.14) → internal hostname!
# X-Backend: web-03.internal → internal hostname!
```

### Technique 6: Favicon Hash (Shodan/Censys)

```bash
# EVERY SITE HAS A FAVICON → CALCULATE ITS HASH → SEARCH SHODAN
# Origin server and CDN serve same favicon with same hash!

# CALCULATE FAVICON HASH:
curl -sL "https://target.com/favicon.ico" | python3 -c "
import sys, hashlib, base64
data = sys.stdin.buffer.read()
# Shodan uses mmh3 hash of base64-encoded favicon
import mmh3
encoded = base64.b64encode(data)
hash_val = mmh3.hash(encoded)
print(f'Shodan favicon hash: {hash_val}')
"

# SEARCH SHODAN:
shodan search "http.favicon.hash:12345678"
# Returns all servers serving the same favicon → may find origin!
```

---

## Verifying Origin IP

Once you find a candidate origin IP, verify it serves the target site:

```bash
# METHOD: FORCE HOST HEADER TO TARGET DOMAIN, DIRECT CONNECT TO ORIGIN IP:
curl -H "Host: target.com" http://ORIGIN_IP/
curl -H "Host: target.com" https://ORIGIN_IP/ --insecure

# If returns target.com content → CONFIRMED ORIGIN!

# CHECK IF ORIGIN HAS MORE SERVICES:
nmap -sV -sC -p- ORIGIN_IP

# COMPARE HTTP HEADERS (origin may be more verbose):
curl -sI -H "Host: target.com" http://ORIGIN_IP/
# → Server: Apache/2.4.41 (Ubuntu) → version exposed!
# → X-Powered-By: PHP/7.4.3 → tech stack exposed!
# (CDN would normally strip these!)
```

---

## Tools Summary

```bash
# CLOUDFLARE ORIGIN FINDER:
# Tool: CloudFail
git clone https://github.com/m0rtem/CloudFail.git
python3 cloudfail.py --target target.com

# ALL-IN-ONE ORIGIN FINDER:
# Tool: bypass-firewalls-by-DNS-history
git clone https://github.com/vincentcox/bypass-firewalls-by-DNS-history.git
python3 bypass-firewalls-by-DNS-history.py -d target.com

# SHODAN + CENSYS COMBO:
# 1. Get cert fingerprint from CDN edge:
openssl s_client -connect target.com:443 2>/dev/null | \
  openssl x509 -noout -fingerprint
# 2. Search Shodan/Censys for that cert fingerprint on non-CDN IPs
```

---

## Related Notes
- [[25 - WAF Detection]] — WAF identification
- [[27 - ASN and IP Range Discovery]] — infrastructure IP mapping
- [[07 - DNS Enumeration]] — DNS record analysis
- [[08 - Subdomain Enumeration]] — finding unprotected subdomains
