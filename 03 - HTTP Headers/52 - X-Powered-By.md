---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.52 X-Powered-By — Tech Fingerprinting, Remove It"
---

# 03.52 — X-Powered-By

## What is it?

`X-Powered-By` is a non-standard response header that reveals the backend technology stack — PHP version, ASP.NET version, Express.js, etc. It's informational only and provides no benefit to legitimate users, but gives attackers a direct path to relevant CVEs.

---

## Common Values and What They Reveal

```
X-Powered-By: PHP/7.4.3          → exact PHP version → known CVEs!
X-Powered-By: ASP.NET            → .NET application
X-Powered-By: Express            → Node.js Express framework
X-Powered-By: Next.js            → Next.js SSR framework
X-Powered-By: Servlet/3.0 JSP/2.2  → Java Servlet container
X-Powered-By: Phusion Passenger 6.0 → Ruby/Python app server
X-Powered-By: ShieldSquare Robot Manager  → anti-bot service revealed!
```

---

## Attack: CVE Targeting from Version Information

```
1. Discover version: PHP/5.6.18

2. Search for CVEs:
   searchsploit php 5.6
   → Multiple RCE and SQLi CVEs for PHP < 7.0!
   
   NVD: https://nvd.nist.gov/vuln/search?query=php+5.6
   → CVE-2015-4642: Arb code execution in PHP 5.x

3. Test if target is vulnerable:
   Apply specific exploit for detected version.

PRACTICAL ATTACK PATH:
  Step 1: curl -sI https://target.com | grep "X-Powered-By"
  → X-Powered-By: PHP/7.2.5
  
  Step 2: searchsploit "php 7.2" → find relevant exploits
  Step 3: Test applicable CVEs
```

---

## Framework Fingerprinting Chains

```
COMBINATION ATTACK (multiple headers):
  Server: nginx/1.14.0          ← Nginx version
  X-Powered-By: PHP/7.2.5       ← PHP version
  X-AspNet-Version: 4.0.30319   ← if also ASP.NET (unusual but seen)
  Set-Cookie: PHPSESSID=...      ← PHP confirmed!
  
  RESULT: Full stack fingerprint:
    Nginx 1.14.0 + PHP 7.2.5 → specific server configs to test!

WORDPRESS FINGERPRINT:
  X-Powered-By: WP Engine
  → WordPress on WP Engine hosting → WordPress-specific exploits!
```

---

## Other Fingerprinting Headers (Similar to X-Powered-By)

```
Server: Apache/2.4.41 (Ubuntu)  → Apache version + OS
X-Generator: Drupal 9            → CMS version
X-Drupal-Cache: HIT              → Confirms Drupal
X-Varnish: 12345                 → Varnish cache
X-Cache: HIT                     → Caching layer
x-amz-request-id:                → AWS!
x-guploader-uploadid:            → Google Cloud!
```

---

## Testing

```bash
# Get full fingerprint
curl -sI https://target.com | grep -iE "server|x-powered-by|x-generator|x-aspnet|x-drupal|x-varnish"

# WhatWeb fingerprinting tool
whatweb https://target.com

# Wappalyzer browser extension (browser GUI)

# Nikto web scanner (also fingerprints)
nikto -h https://target.com

# Manual version extraction
curl -sI https://target.com | grep "X-Powered-By" | grep -oP 'PHP/[\d.]+'
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| PHP version exposed | `expose_php = Off` in php.ini |
| Express.js default header | `app.disable('x-powered-by')` in Express |
| ASP.NET version exposed | Remove in web.config |
| Any X-Powered-By | Nginx: `proxy_hide_header X-Powered-By;` |

**Nginx config to remove disclosure:**
```nginx
proxy_hide_header X-Powered-By;
proxy_hide_header X-AspNet-Version;
server_tokens off;
```

---

## Related Notes
- [[53 - Server]] — Server header version disclosure
- [[54 - X-AspNet-Version]] — ASP.NET specific fingerprinting
- [[Module 17 - Recon]] — full fingerprinting and recon techniques
