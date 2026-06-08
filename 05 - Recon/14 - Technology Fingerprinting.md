---
tags: [vapt, recon, beginner]
difficulty: beginner
module: "05 - Recon"
topic: "05.14 Technology Fingerprinting (Wappalyzer, WhatWeb)"
---

# 05.14 — Technology Fingerprinting

## What is it?

Technology fingerprinting identifies what software, frameworks, and libraries a web application uses — without source code access. Knowing the exact stack immediately points you toward relevant CVEs, default configurations, and platform-specific attack vectors.

---

## Why Fingerprinting Matters

```
KNOWN TECH → TARGETED ATTACKS:

WordPress 5.6.0 detected:
  → searchsploit wordpress 5.6
  → CVE-2021-29447: XXE in media library
  → Immediate critical finding!

Apache 2.4.49 detected:
  → CVE-2021-41773: Path traversal + RCE
  → curl https://target.com/cgi-bin/.%2e/.%2e/bin/sh
  → Immediate check!

Joomla 3.7.0:
  → CVE-2017-8917: SQLi in com_fields
  
PHP/5.x:
  → Many historical RCE CVEs
  → Laravel debug mode? → RCE via deserialization
  
jQuery 1.x:
  → Multiple XSS CVEs via older plugins
```

---

## Wappalyzer

```
BROWSER EXTENSION: Free, works on any site you visit
  Install → browse target → click icon → see tech stack

CLI VERSION:
  npm install -g wappalyzer
  wappalyzer https://target.com --pretty

API:
  curl "https://api.wappalyzer.com/v2/lookup/?urls=https://target.com" \
    -H "x-api-key: YOUR_KEY"

DETECTS FROM:
  HTTP headers (Server, X-Powered-By, X-Generator)
  HTML patterns (meta tags, comments, script names)
  JavaScript variables and objects
  Cookie names (PHPSESSID → PHP, JSESSIONID → Java)
  File paths (/wp-content → WordPress)
  Response body patterns
```

---

## WhatWeb

```bash
# Basic scan:
whatweb https://target.com

# Aggressive scan (more requests):
whatweb -a 3 https://target.com

# Quiet mode (just technologies):
whatweb -q https://target.com

# Scan multiple targets:
whatweb -i targets.txt -a 3 -o results.csv --log-csv

# Output formats:
whatweb https://target.com --log-xml results.xml
whatweb https://target.com --log-json results.json

EXAMPLE OUTPUT:
whatweb target.com
https://target.com [200 OK] 
  Apache[2.4.41], 
  Bootstrap[4.5.2], 
  HTTPServer[Ubuntu Linux][Apache/2.4.41 (Ubuntu)], 
  IP[203.0.113.1], 
  JQuery[3.5.1], 
  PHP[7.4.3], 
  WordPress[5.8.3], 
  X-Powered-By[PHP/7.4.3]
→ IMMEDIATE FINDINGS: Apache 2.4.41, PHP 7.4.3, WordPress 5.8.3!
```

---

## Manual Fingerprinting from HTTP Headers

```bash
# Full header fingerprinting:
curl -sI https://target.com

LOOK FOR:
  Server: Apache/2.4.41 (Ubuntu)     → Apache version + OS!
  X-Powered-By: PHP/7.4.3            → PHP version!
  X-Generator: Drupal 9 (drupal.org) → Drupal CMS!
  X-Drupal-Cache: HIT                → Drupal confirmed
  Set-Cookie: PHPSESSID=             → PHP session
  Set-Cookie: JSESSIONID=            → Java/Tomcat
  Set-Cookie: connect.sid=           → Express.js (Node)
  Set-Cookie: __utma=                → Google Analytics
  Set-Cookie: wp_settings=           → WordPress
  Via: 1.1 varnish                   → Varnish cache
  X-Cache: HIT from varnish          → Varnish confirmed
  CF-RAY:                            → Cloudflare!
  X-Amz-Cf-Id:                       → AWS CloudFront!
  X-Azure-Ref:                       → Azure Front Door!
```

---

## CMS Detection

```bash
# WORDPRESS:
curl -s https://target.com | grep -i "wp-content\|wp-includes\|wordpress"
curl -s https://target.com/wp-login.php -o /dev/null -w "%{http_code}"  # 200 = WP!
curl -s https://target.com/wp-json/wp/v2/users  # user enumeration!

# DRUPAL:
curl -s https://target.com | grep -i "drupal\|/sites/default\|drupalSettings"
curl -s https://target.com/CHANGELOG.txt | head -5  # version!

# JOOMLA:
curl -s https://target.com | grep -i "joomla"
curl -s https://target.com/administrator/  # admin panel

# MAGENTO:
curl -s https://target.com | grep -i "magento\|skin/frontend\|mage"

# SHOPIFY:
curl -sI https://target.com | grep -i "x-shopify\|myshopify"

# TOOL: CMSeek (CMS detection and exploitation):
cmseek -u https://target.com
```

---

## WAF Detection

```bash
# WAFW00F (WAF fingerprinting):
wafw00f https://target.com

# Manual detection:
# Send malicious payload → see how server responds:
curl -A "sqlmap" https://target.com/  # known scanner UA → WAF blocks?
curl "https://target.com/?id=1' OR '1'='1" -sI  # SQLi payload → WAF response?

# WAF fingerprints:
# Cloudflare: "cf-ray" header, error page "Cloudflare"
# AWS WAF: x-amzn-requestid header
# Imperva: "_imp_apg_r_" cookie
# F5 BIG-IP: "bigipserver" cookie
# ModSecurity: X-Request-ID or "Mod_Security" in error
# Akamai: "akamai-grn" header
```

---

## Related Notes
- [[25 - WAF Detection]] — WAF-specific fingerprinting
- [[53 - Server header]] — server version disclosure
- [[52 - X-Powered-By]] — framework fingerprinting
- [[Module 17 - Recon]] — broader recon context
