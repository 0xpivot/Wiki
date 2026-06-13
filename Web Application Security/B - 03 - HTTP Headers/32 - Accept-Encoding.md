---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.32 Accept-Encoding — BREACH Attack"
---

# 03.32 — Accept-Encoding

## What is it?

`Accept-Encoding` tells the server which compression algorithms the client supports. The server compresses the response body to save bandwidth. The BREACH attack exploits HTTP compression to recover secrets from encrypted (HTTPS) responses by observing compressed response sizes.

---

## Common Values

```
Accept-Encoding: gzip          → gzip compression
Accept-Encoding: deflate       → deflate compression
Accept-Encoding: br            → Brotli (newer, better compression)
Accept-Encoding: gzip, deflate, br  → browser default (accept all)
Accept-Encoding: identity      → no compression
```

---

## Attack: BREACH (Browser Reconnaissance and Exfiltration via Adaptive Compression of Hypertext)

```
PRECONDITIONS (all required):
  1. HTTP compression enabled (gzip/deflate in response)
  2. Secret reflected in response body (CSRF token, API key in page source)
  3. Attacker can make requests on victim's behalf (MITM or CSRF + observe size)

HOW COMPRESSION LEAKS SECRETS:
  Compression replaces repeated patterns with shorter codes.
  If secret is in page AND attacker-controlled text is also in page:
  
  Response body:
    "...csrf-token=ABCDEF... <attacker-controlled search query>"
  
  ATTACK:
    Make victim request: ?q=csrf-token=A  → observe compressed size
    Make victim request: ?q=csrf-token=B  → observe compressed size
    ...
    If ?q=csrf-token=AB gives smaller size → first two chars are "AB"!
    
  Why? "csrf-token=AB" matches start of real secret → better compression!
  → Attacker recovers secret one character at a time!

REAL-WORLD EXAMPLE:
  Target URL: https://bank.com/account?search=<ATTACKER-CONTROLLED>
  Page always contains: <input name="csrf" value="SECRETTOKEN">
  
  Attacker guesses each character of SECRETTOKEN by comparing sizes.
```

---

## BREACH vs CRIME

```
CRIME (2012):
  Exploited TLS/SSL compression (not HTTP body compression)
  Fixed: TLS compression disabled in all modern TLS implementations

BREACH (2013):
  Exploits HTTP-level compression (Content-Encoding: gzip)
  Still relevant! Not fully fixed everywhere.
  
  KEY DIFFERENCE: BREACH attacks the gzip-compressed response BODY.
  TLS encryption doesn't help — size is observable even when encrypted!
```

---

## Testing for BREACH Vulnerability

```bash
# 1. Check if compression is enabled:
curl -sI -H "Accept-Encoding: gzip" https://target.com/ | grep -i "content-encoding"
# Content-Encoding: gzip → compression enabled

# 2. Check if secrets are in compressed response:
curl -H "Accept-Encoding: gzip" https://target.com/dashboard | gunzip | grep -i "csrf\|token\|secret"

# 3. Check if attacker-controlled data is reflected in same page as secrets:
curl -H "Accept-Encoding: gzip" "https://target.com/?search=test" | gunzip | grep "test"

# All three true → BREACH conditions met!

# Tools:
# breachattack.com → BREACH attack toolkit
# Burp Suite → Observe response size for different inputs
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Secret + user-input in compressed response | Mask CSRF tokens (XOR with random value per request) |
| HTTP compression of secret pages | Disable compression for pages with secrets in body |
| BREACH attack surface | Separate user-controlled content from secrets; add length-hiding padding |

---

## Related Notes
- [[02.15 - Transfer-Encoding]] — BREACH vs CRIME comparison
- [[02.03 - HTTP Versions]] — CRIME against TLS compression
- [[Module 07 - CSRF]] — CSRF token masking as BREACH mitigation
