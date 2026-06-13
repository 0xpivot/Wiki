---
tags: [vapt, http-headers, web, beginner]
difficulty: beginner
module: "03 - HTTP Headers"
topic: "03.35 X-Content-Type-Options: nosniff — MIME Sniffing Prevention"
---

# 03.35 — X-Content-Type-Options

## What is it?

`X-Content-Type-Options: nosniff` is a response header that tells browsers NOT to guess (sniff) the content type of a response — they must use exactly what the `Content-Type` header says. Without it, browsers might execute a text file as JavaScript or render a download as HTML, enabling XSS attacks.

---

## What is MIME Sniffing?

```
WITHOUT nosniff:
  Server sends:
    Content-Type: text/plain
    Body: <script>alert(1)</script>
  
  Browser thinks: "Hmm, this looks like HTML/JavaScript..."
  → Browser renders it as HTML!
  → XSS executes!

WITH nosniff:
  Server sends:
    Content-Type: text/plain
    X-Content-Type-Options: nosniff
    Body: <script>alert(1)</script>
  
  Browser: "Server said text/plain, and I must trust that"
  → Renders as plain text → no XSS!
```

---

## Attack: MIME Sniffing for XSS

```
SCENARIO: File upload allows text files.
  User uploads: exploit.txt containing <script>alert(1)</script>
  
  Server serves it as:
    Content-Type: text/plain
    (no X-Content-Type-Options)
  
  When another user views the file:
    URL: https://target.com/uploads/exploit.txt
    Browser sniffs → "this looks like HTML" → executes!
    → XSS!

FIX:
    Content-Type: text/plain
    X-Content-Type-Options: nosniff
    → Browser won't sniff → no XSS from text file!
```

---

## Attack: JavaScript MIME Confusion

```
Browser blocking scripts from wrong MIME type (modern browsers):
  <script src="/api/data.json"></script>  → blocked (JSON, not JS)
  
WITHOUT nosniff on the JSON endpoint:
  If JSON response starts with JS-looking content → browser might execute it!

PRACTICAL BYPASS SCENARIO:
  Target has CSP: script-src 'self'
  But JSON API endpoint at /api/user.json returns:
  {"data":"..."}
  
  WITHOUT nosniff → attacker might craft /api/user.json?callback=alert(1)
  to return JS-looking content → sniffed as script → CSP bypass!
```

---

## CSS MIME Sniffing

```
WITHOUT nosniff:
  Upload malicious CSS (with XSS via IE's expression() feature — legacy)
  
  Content-Type: text/plain (should not execute)
  Browser sniffs as CSS → executes expressions in IE!
  
MODERN RELEVANCE:
  Less critical now, but nosniff prevents cross-origin CSS injection
  in some contexts.
```

---

## Checking and Testing

```bash
# Check if nosniff is set
curl -sI https://target.com | grep -i "x-content-type-options"
# Missing → MIME sniffing possible!

# Check for all static file endpoints
for path in / /upload/ /static/ /media/ /files/; do
  echo -n "$path: "
  curl -sI https://target.com$path | grep -i "x-content-type-options" || echo "MISSING"
done

# Test MIME sniffing (requires browser):
# Upload a text file with HTML content
# Access it and check if browser renders HTML or shows text
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| MIME sniffing XSS via uploaded files | Add `X-Content-Type-Options: nosniff` globally |
| JSON endpoint sniffed as script | Set correct Content-Type AND nosniff |
| CSP bypass via MIME sniffing | nosniff + strict Content-Type enforcement |

**One-line fix** (Nginx):
```nginx
add_header X-Content-Type-Options "nosniff" always;
```

---

## Related Notes
- [[34 - Content-Security-Policy]] — CSP and MIME sniffing interaction
- [[02.14 - MIME Types and Content-Type]] — MIME type reference
- [[Module 08 - File Upload]] — file upload security
- [[Module 02 - XSS]] — XSS via MIME sniffing
