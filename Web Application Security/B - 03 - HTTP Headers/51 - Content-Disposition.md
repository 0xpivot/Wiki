---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.51 Content-Disposition — Filename Injection, Download vs Inline"
---

# 03.51 — Content-Disposition

## What is it?

`Content-Disposition` controls whether the browser renders content inline (displays it) or downloads it as a file attachment. It also sets the suggested filename. Attackers can exploit it to force downloads of malicious files, inject characters into suggested filenames, or exploit filename injection vulnerabilities.

---

## Values

```
Content-Disposition: inline
  → Browser displays in window (default for HTML, images, PDFs)

Content-Disposition: attachment
  → Browser downloads the file (no specified name)

Content-Disposition: attachment; filename="document.pdf"
  → Browser downloads and suggests "document.pdf" as filename

Content-Disposition: attachment; filename*=UTF-8''%E2%80%8Bfile.exe
  → RFC 5987 encoded filename (allows Unicode)
```

---

## Attack 1: Filename Injection (Path Traversal in Filename)

```
SCENARIO: App generates download link with user-supplied filename.
  GET /download?file=report.pdf
  
  Response:
  Content-Disposition: attachment; filename="report.pdf"

ATTACK:
  GET /download?file=../../../etc/passwd
  
  Response:
  Content-Disposition: attachment; filename="../../../etc/passwd"
  
  SOME OLDER BROWSERS: might try to write to relative path!
  → Path traversal to write files in different directory!
  
  MODERN IMPACT: Even if browser doesn't follow path, the server
  might have read the file at that path → file disclosure!
```

---

## Attack 2: Missing attachment → XSS via Inline Display

```
SCENARIO: Upload endpoint for user files.
  User uploads HTML file → served inline!
  
  Server:
    Content-Disposition: inline     ← or no Content-Disposition
    Content-Type: text/html
    Body: <script>alert(1)</script>
  
  → XSS when victim views the "uploaded file"!

FIX:
  For ALL user-uploaded files:
    Content-Disposition: attachment; filename="user_upload.txt"
    X-Content-Type-Options: nosniff
  → Browser downloads instead of rendering → no XSS!
```

---

## Attack 3: Overriding attachment with inline (Firefox/IE)

```
LEGACY ATTACK:
  Server sets: Content-Disposition: attachment; filename="safe.txt"
  Content-Type: text/html
  
  Some old browsers rendered HTML despite attachment directive!
  → XSS possible from downloads in old browsers.
  
  MODERN: Not an issue in current browsers with nosniff.
```

---

## Attack 4: Filename Injection → Double Extension

```
SCENARIO: Server reflects user-supplied filename.
  GET /download?name=report.pdf

ATTACK:
  GET /download?name=malware.pdf.exe
  
  Response:
  Content-Disposition: attachment; filename="malware.pdf.exe"
  
  Windows hides .exe extension → user sees "malware.pdf"
  → Social engineering to execute malware!
```

---

## Testing

```bash
# Check Content-Disposition on uploads and downloads:
curl -sI https://target.com/download/file.pdf | grep -i "content-disposition"
curl -sI https://target.com/uploads/user-file.html | grep -i "content-disposition"

# Test filename injection:
curl -sI "https://target.com/download?file=../etc/passwd" | grep -i "content-disposition"

# Test if HTML files are served inline:
# Upload HTML file → access URL → does browser render it or download?

# Check for missing attachment on user-uploaded files:
curl -sI https://target.com/uploads/test.html \
  -H "Cookie: session=legit" | grep -i "disposition"
# Missing → render → potential XSS!
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| User uploads served inline | Always use `attachment` for user content |
| Filename from user input | Sanitize filename; strip path separators |
| Double extension social engineering | Validate and normalize file extensions |

---

## Related Notes
- [[35 - X-Content-Type-Options]] — nosniff prevents rendering wrong type
- [[Module 08 - File Upload]] — file upload security guide
- [[Module 02 - XSS]] — XSS via inline file serving
