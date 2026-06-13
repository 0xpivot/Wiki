---
tags: [vapt, recon, intermediate]
difficulty: intermediate
module: "05 - Recon"
topic: "05.25 WAF Detection (wafw00f)"
---

# 05.25 — WAF Detection

## What is a WAF?

A Web Application Firewall (WAF) sits between clients and the web server, inspecting HTTP requests and blocking those that look malicious. Detecting WAF presence is critical before testing — undetected WAFs will block your payloads, produce false-negatives, and may ban your IP.

```
CLIENT → [WAF] → WEB SERVER
           ↑
   Inspects every request
   Blocks: SQLi, XSS, RCE payloads
   Returns: 403/406/429 or redirects to error page

WHY DETECT IT:
  → Know you need bypass techniques
  → Identify the WAF product (each has specific bypasses)
  → Some WAFs reveal internal IP in error pages!
  → WAF = there's something worth protecting behind it
```

---

## wafw00f (WAF Fingerprinting Tool)

```bash
# INSTALL:
pip3 install wafw00f
# OR:
git clone https://github.com/EnableSecurity/wafw00f.git

# BASIC DETECTION:
wafw00f https://target.com

# DETECT ALL MATCHING WAFV (not just first match):
wafw00f -a https://target.com

# TEST MULTIPLE TARGETS:
wafw00f -i targets.txt

# OUTPUT FORMAT:
wafw00f https://target.com -o results.json --format json
wafw00f https://target.com -o results.csv --format csv

# EXAMPLE OUTPUT:
# [*] Checking https://target.com
# [+] The site https://target.com is behind Cloudflare (Cloudflare Inc.) WAF.
# [~] Number of requests: 2

# LIST ALL SUPPORTED WAFs:
wafw00f --list

# SUPPORTED WAFs INCLUDE:
# Cloudflare, AWS WAF, Akamai, Imperva Incapsula
# F5 BIG-IP ASM, Barracuda, Citrix NetScaler
# ModSecurity, NAXSI, Sucuri, Wordfence
# Azure Application Gateway, Google Cloud Armor
# Fortinet FortiWeb, Radware AppWall, and 150+ more
```

---

## Manual WAF Detection Techniques

### HTTP Header Analysis

```bash
# CHECK HEADERS FOR WAF SIGNATURES:
curl -sI https://target.com

# CLOUDFLARE:
# CF-RAY: 7a1234567890abcd-SIN
# CF-Cache-Status: DYNAMIC
# Set-Cookie: __cfduid=...
# Server: cloudflare

# AWS WAF:
# x-amzn-requestid: xxxxxxxx
# x-amz-apigw-id: xxxxxxxx
# x-cache: Miss from cloudfront

# IMPERVA INCAPSULA:
# X-Iinfo: 8-12345-
# Set-Cookie: incap_ses_...
# Set-Cookie: visid_incap_...

# AKAMAI:
# X-Check-Cacheable: YES
# Set-Cookie: ak_bmsc=...
# AkamaiGHost header

# F5 BIG-IP:
# Set-Cookie: BIGipServer...
# Server: BigIP

# SUCURI:
# X-Sucuri-ID: 
# X-Sucuri-Cache:

# BARRACUDA:
# Set-Cookie: barra_counter_session=
# X-Powered-By: ARR/3.0 (Barracuda WAF)
```

### Trigger WAF with Malicious Payload

```bash
# SEND OBVIOUSLY MALICIOUS PAYLOAD AND ANALYZE RESPONSE:
curl -v "https://target.com/?id=1' OR '1'='1" 2>&1 | head -40

# WAF RESPONSE INDICATORS:
# 403 Forbidden (most WAFs)
# 406 Not Acceptable (ModSecurity default)
# 429 Too Many Requests (rate-limit WAF)
# Redirect to /waf-error or /blocked
# Response body contains: "Access Denied", "Blocked", "Cloudflare", "Incapsula"

# XSS PAYLOAD:
curl -v "https://target.com/?q=<script>alert(1)</script>"

# COMMON WAF ERROR PAGE SIGNATURES:
curl -s "https://target.com/?id=1 UNION SELECT 1--" | grep -iE "cloudflare|incapsula|akamai|blocked|access.denied|forbidden"

# NMAP WAF DETECTION:
nmap --script http-waf-detect target.com
nmap --script http-waf-fingerprint target.com
```

### Cookie-Based Detection

```bash
# WAF-SPECIFIC COOKIES:
curl -sI https://target.com | grep "Set-Cookie"

# CLOUDFLARE:  __cfduid, cf_clearance
# INCAPSULA:   incap_ses_*, visid_incap_*
# F5 BIG-IP:   BIGipServer*
# BARRACUDA:   barra_counter_session
# PERIMETERX:  _px, _pxhd, _pxde
# DATADOME:    datadome
# KASADA:      x-kpsdk-ct
```

---

## CDN vs WAF Detection

```
CDN (Content Delivery Network):
  Purpose: speed/availability (caches static content)
  Examples: Cloudflare CDN, AWS CloudFront, Fastly, Akamai CDN
  
WAF (Web Application Firewall):
  Purpose: security (blocks malicious requests)
  Examples: Cloudflare WAF, AWS WAF, Imperva, ModSecurity

IMPORTANT: Some products do BOTH (Cloudflare = CDN + WAF)
  → Detecting Cloudflare means both CDN AND WAF might be active!
  → Separate CDN from WAF rules (WAF rules need license/config)
```

```bash
# CLOUDFLARE SPECIFICALLY:
# Check if domain resolves to Cloudflare IPs:
dig +short target.com | while read ip; do
  whois "$ip" | grep -i "cloudflare\|APNIC" | head -1
  echo "IP: $ip"
done

# Cloudflare IP ranges:
# 103.21.244.0/22, 103.22.200.0/22, 103.31.4.0/22
# 104.16.0.0/13, 104.24.0.0/14, 108.162.192.0/18

# CHECK:
curl -sI https://target.com | grep "cf-ray"
# CF-RAY: 7abc12345-SIN → Cloudflare confirmed!
```

---

## WAF Bypass Overview (Reconnaissance Focus)

Once a WAF is identified, you can look up bypass techniques specific to it.

```
GENERAL BYPASS STRATEGIES (studied in Module 06):
  1. Encoding: URL encode, double URL encode, HTML encode, Unicode
     ' OR 1=1-- → %27%20OR%201%3D1--
     
  2. Case variation:
     UNION SELECT → uNiOn SeLeCt
     
  3. Comment insertion:
     UNION SELECT → UNION/**/SELECT → UN/**/ION SEL/**/ECT
     
  4. Alternate syntax:
     ' OR 1=1-- → ' OR 1 LIKE 1--
     
  5. HTTP header manipulation:
     X-Forwarded-For: 127.0.0.1 → may bypass IP-based WAF rules
     X-Originating-IP: 127.0.0.1
     
  6. Chunked transfer:
     Transfer-Encoding: chunked → payload split across chunks
     
  7. HTTP version tricks:
     HTTP/2 → some WAFs only inspect HTTP/1.1
     
  8. Content-Type tricks:
     application/json → WAF may not parse JSON body
     multipart/form-data → WAF may not decode properly

FOR SPECIFIC WAFS:
  → wafw00f identifies the WAF
  → Search: "bypass [WAF Name] SQLi 2024"
  → Check: https://github.com/0xInfection/Awesome-WAF
```

---

## CloudFlare Origin IP Discovery

If a site is behind Cloudflare, finding the real origin IP lets you bypass the WAF entirely.

```bash
# METHOD 1: Historical DNS (before Cloudflare was added)
# Check SecurityTrails / DNSDumpster for old A records:
curl -s "https://securitytrails.com/domain/target.com/history/a"

# METHOD 2: Certificate Transparency (crt.sh)
# Origin servers often have SSL certs with original IPs:
curl -s "https://crt.sh/?q=target.com&output=json" | \
  python3 -c "import json,sys; [print(c['name_value']) for c in json.load(sys.stdin)]" | \
  grep -oP '\d+\.\d+\.\d+\.\d+' | sort -u

# METHOD 3: MX Records (often bypass Cloudflare)
dig MX target.com
# Mail server → same IP range = origin IP!

# METHOD 4: SPF Record
dig TXT target.com | grep "spf"
# v=spf1 ip4:203.0.113.1 include:... → direct origin IP!

# METHOD 5: Subdomain not behind Cloudflare
# Often: staging.target.com, dev.target.com, mail.target.com
# Nslookup those → if not Cloudflare IPs → origin found!

# METHOD 6: Tools
# Shodan search: ssl:"target.com" org:"Hosting Provider"
# CriminalIP: https://www.criminalip.io

# VERIFY ORIGIN IP FOUND:
curl -H "Host: target.com" https://ORIGIN_IP/ -k
# If returns target.com content → origin confirmed → bypass WAF!
```

---

## Related Notes
- [[14 - Technology Fingerprinting]] — broader fingerprinting
- [[26 - CDN Detection and Origin IP Discovery]] — CDN-specific detection
- [[21 - Port Scanning with Nmap]] — infrastructure scanning
- [[Module 06 - Web Vulnerabilities]] — WAF bypass techniques in practice
