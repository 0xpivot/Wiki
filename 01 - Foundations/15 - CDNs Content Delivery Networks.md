---
tags: [vapt, foundations, networking, beginner]
difficulty: beginner
module: "01 - Foundations"
topic: "01.15 CDNs — Content Delivery Networks"
---

# 01.15 — CDNs — Content Delivery Networks

## What is it?

A **CDN (Content Delivery Network)** is a globally distributed network of servers (called PoPs — Points of Presence) that caches and delivers content to users from the nearest location. This reduces latency, handles massive traffic, and provides a layer of security.

**Analogy:** Instead of everyone getting their coffee from one central warehouse, CDNs are like Starbucks — there's one near every customer, so you get served fast.

---

## How a CDN Works

```
WITHOUT CDN:
User in India ────────────────────────────────→ Origin Server in New York
             Request: 300ms round-trip

WITH CDN:
User in India ───→ [CDN Edge Node in Mumbai] ──────→ Origin Server (only for cache miss)
             Request: 20ms round-trip (served from cache)

CDN EDGE NODE LOCATIONS:
Cloudflare: 285+ cities worldwide
AWS CloudFront: 410+ PoPs
Akamai: 4000+ PoPs
Fastly: 90+ PoPs

HOW CACHING WORKS:
1. User 1 requests /logo.png from CDN edge in Mumbai
2. CDN doesn't have it → fetches from origin server → caches it
3. User 2 requests /logo.png → CDN serves from Mumbai cache (no origin hit)
4. Cache lives until TTL expires or content is purged
```

---

## CDN Security Functions

```
Modern CDNs (Cloudflare, Akamai) provide:

1. DDoS Protection
   → Absorb massive traffic volumes (Cloudflare: 100+ Tbps capacity)
   → Filter volumetric attacks before they reach origin

2. WAF (Web Application Firewall)
   → Block SQLi, XSS, etc. at CDN edge
   → Rules update automatically for known CVEs

3. Bot Detection
   → Block scrapers, credential stuffing bots
   → CAPTCHAs, JavaScript challenges

4. SSL/TLS Termination
   → CDN handles HTTPS → HTTP or HTTPS to origin
   → Manages certificates

5. Rate Limiting
   → Limit requests per IP per second
```

---

## Security Context — CDNs in VAPT

### 1. CDN Detection

```bash
# Detect CDN from response headers:
curl -sI https://target.com | grep -i "cf-ray\|x-cache\|via\|cdn\|server"

# Cloudflare:
# CF-RAY: 89abc-LHR         ← CF-RAY = Cloudflare
# Server: cloudflare

# AWS CloudFront:
# Via: 1.1 abc123.cloudfront.net
# X-Cache: Hit from cloudfront

# Akamai:
# X-Check-Cacheable: YES
# X-Akamai-Transformed: 9

# Fastly:
# X-Served-By: cache-lon4270-LON
# X-Cache: HIT
# Via: 1.1 varnish

# Tools:
wafw00f https://target.com          ← detects WAF/CDN
whatwaf --url https://target.com
```

### 2. Find the Real Origin IP — Bypass CDN

If you can find the origin server's real IP, you can bypass CDN protections (WAF, DDoS protection, rate limiting).

```bash
# Method 1: Historical DNS records (before CDN was added)
# SecurityTrails: https://securitytrails.com
# PassiveDNS: https://passivedns.mnemonic.no
# Old CDN miss → origin IP leaks

# Method 2: SSL certificate on origin
# If CDN uses "Full" mode (HTTP to origin), origin cert may differ
# shodan search: ssl:"target.com" -http.title:"cloudflare"
# censys.io: query for cert CN matching target.com

# Method 3: Email headers (SPF, MX records)
dig target.com MX +short
# If MX is not behind CDN → different IP block → same ASN as origin

# Method 4: Subdomains that might not be CDN-protected
# Direct: direct.target.com, origin.target.com
subfinder -d target.com | httpx -ip    ← resolve subdomains and show IPs
# Compare IPs to find non-CDN ones

# Method 5: Shodan + Censys search for origin
shodan search "Server: nginx http.title:\"target.com\""
# Look for matching title/content on different IPs

# Method 6: xmlrpc.php / wp-cron.php email leakage
# WordPress email headers may reveal origin IP

# Once you find origin IP — access directly:
curl -H "Host: target.com" http://ORIGIN-IP/
# ← bypasses CDN WAF entirely!
```

### 3. Cache Poisoning via CDN

CDN caches can be poisoned if cache keys don't include all relevant request parameters.

```
ATTACK: Cache Poisoning
1. Attacker sends: GET /?cb=evil HTTP/1.1
   Host: target.com
   X-Forwarded-Host: evil.com      ← CDN ignores this, app uses it

2. App generates response:
   <script src="https://evil.com/jquery.js">  ← reflected attacker host

3. CDN caches this response under key: target.com/?cb=evil

4. Innocent user visits: target.com/?cb=evil
   Gets poisoned cached response → loads evil.com JS → XSS!
```

```bash
# param-miner Burp Suite extension — finds unkeyed inputs
# Manual test:
curl "https://target.com/?cb=1" -H "X-Forwarded-Host: evil.com" -v
# Watch response for evil.com in content
```

### 4. CDN Bypass via Direct IP Access

```bash
# Test if CDN WAF rules apply when accessing origin directly:
# Find origin IP (see Method 1-6 above), then:
curl --insecure https://ORIGIN-IP/ -H "Host: target.com"
# Now send attack payload — no CDN WAF!
sqlmap -u "http://ORIGIN-IP/page?id=1" --headers="Host: target.com"
```

### 5. Cloudflare-Specific Issues

```bash
# Cloudflare IP ranges — if you know the CDN is CF, real IP is NOT in:
# 173.245.48.0/20, 103.21.244.0/22, 103.22.200.0/22 (CF ranges)

# Check if Cloudflare is in "orange cloud" (proxy) or "grey cloud" (DNS only)
dig target.com +short
# If returns 104.21.x.x or 172.67.x.x → Cloudflare proxy (IP hidden)
# If returns non-CF IP → DNS only, origin IP exposed!

# Subdomains with DNS-only (grey cloud) can reveal origin IP range
# Even if www.target.com is proxied, ftp.target.com might not be
```

---

## Hands-On: CDN Analysis Commands

```bash
# Detect CDN
curl -sI https://target.com

# Find CDN edge node location (CF-RAY: timestamp-IATA)
curl -sI https://target.com | grep CF-RAY
# CF-RAY: 89abc123-LHR → London Heathrow edge node

# Test cache HIT/MISS
curl -sI https://target.com/image.png | grep -i "x-cache\|age\|cf-cache"
# X-Cache: HIT from cloudfront  ← cached
# Age: 3600                      ← cached 1 hour ago

# Find all IPs for a domain (CDN gives different IPs each query)
for i in {1..5}; do dig +short target.com; done
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Origin IP exposed | Move origin behind CDN before going public, use firewall to block non-CDN traffic |
| Cache poisoning via unkeyed headers | Configure CDN to ignore untrusted headers or include in cache key |
| CDN WAF in report-only mode | Enable blocking mode, tune rules |
| HTTP fallback between CDN and origin | Enable "Full Strict" TLS mode — CDN to origin must also use valid cert |

---

## Related Notes
- [[14 - Load Balancers]] — CDN is a distributed load balancer
- [[17 - TLS SSL How HTTPS Works]] — CDN handles TLS
- [[Module 10 - Web Cache Poisoning]] — cache poisoning attacks
- [[Module 36 - WAF Bypass]] — bypass CDN-based WAFs
