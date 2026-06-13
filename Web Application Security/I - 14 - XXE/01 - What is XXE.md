---
tags: [vapt, xxe, beginner]
difficulty: beginner
module: "14 - XXE"
topic: "14.01 What is XXE?"
portswigger_labs: ["Exploiting XXE using external entities to retrieve files"]
---

# 14.01 — What is XXE?

## Core Concept

```
XXE = XML External Entity Injection

XML has a feature called "entities" — like variables that expand to values.
External entities can reference files or URLs.
If an app parses XML and allows external entities,
an attacker can read local files or make server-side requests!

SIMPLE EXAMPLE:
  Normal XML entity (internal):
  <!DOCTYPE root [<!ENTITY name "World">]>
  <greeting>Hello &name;!</greeting>
  → Renders as: Hello World!

  External entity (XXE):
  <!DOCTYPE root [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>
  <greeting>Hello &xxe;!</greeting>
  → Entity reads /etc/passwd → renders as its content!
  → Attacker gets /etc/passwd in the response!
```

---

## Why XXE Happens

```
XML PARSERS SUPPORT EXTERNAL ENTITIES BY DEFAULT (in most languages):
  Java (SAXParser, DocumentBuilder, XMLReader)
  Python (xml.etree, lxml, xmltodict)
  PHP (SimpleXML, DOMDocument)
  .NET (XmlDocument, XmlReader)
  Node.js (libxmljs, xml2js in some configs)
  
  These parsers were designed before SSRF was a known threat.
  External entities were added for legitimate XML linking.
  But they're dangerous when user-controlled XML is parsed!
  
  FIX: Disable external entity processing (see note 14.10)
```

---

## What XXE Can Do

```
XXE CAN:
  ✓ Read local files (etc/passwd, ssh keys, config files, source code)
  ✓ SSRF — make the server fetch internal URLs (see note 14.08)
  ✓ Port scanning via SSRF
  ✓ Data exfiltration via out-of-band DNS/HTTP
  ✓ Denial of Service (Billion Laughs / XML bomb)
  ✓ Path to RCE (if reading source code reveals other vulnerabilities)
  ✓ Cloud metadata theft (SSRF to 169.254.169.254)

XXE CANNOT:
  ✗ Execute code directly
  ✗ Write files (standard XXE)
  ✗ Work if XML parser has external entities disabled
```

---

## Where XXE Appears

```
XXE REQUIRES XML PARSING OF USER INPUT:

DIRECT XML ENDPOINTS:
  ✓ SOAP web services (Content-Type: text/xml)
  ✓ REST APIs accepting application/xml
  ✓ XML configuration uploads
  ✓ XML import features

FILE UPLOADS (XML-based formats):
  ✓ SVG files (SVG is XML!)
  ✓ DOCX files (ZIP containing XML)
  ✓ XLSX files (ZIP containing XML)
  ✓ PDF with embedded XML metadata
  ✓ RSS/Atom feeds
  ✓ GPX files (GPS data)
  ✓ XML-based config files

HIDDEN XML PROCESSING:
  ✓ Content-Type: application/json → change to application/xml
    (some apps accept both!)
  ✓ Sitemap.xml, robots.txt parsers
  ✓ OpenDocument format (ODF)
```

---

## ASCII Diagram: XXE Attack Flow

```
ATTACKER                APP SERVER              LOCAL FILES
   │                        │                       │
   │  POST /api/parse        │                       │
   │  Content-Type: text/xml │                       │
   │  <!DOCTYPE foo [        │                       │
   │    <!ENTITY xxe         │                       │
   │      SYSTEM             │                       │
   │      "file:///etc/passwd│                       │
   │  ">]>                   │                       │
   │  <data>&xxe;</data>     │                       │
   │─────────────────────────→                       │
   │                         │  Read /etc/passwd     │
   │                         │───────────────────────→
   │                         │  Contents returned    │
   │                         │←──────────────────────
   │  Response contains      │                       │
   │  /etc/passwd content!   │                       │
   │←────────────────────────│                       │
```

---

## XXE vs SSRF vs Command Injection

```
XXE:
  Reads local files or makes server-side requests
  Needs XML parsing of attacker-controlled input
  No direct code execution (usually)
  
SSRF:
  Makes server-side requests to any URL
  Needs URL parameter in app functionality
  
COMMAND INJECTION:
  Executes OS commands
  Needs system() / exec() style call with user input
  Direct RCE
  
XXE CAN LEAD TO SSRF (chain):
  XXE with http:// SYSTEM URL → SSRF!
  This is covered in note 14.08.
```

---

## Related Notes
- [[02 - XML Basics and DTD]] — understanding XML structure
- [[03 - Classic XXE File Read]] — stealing /etc/passwd
- [[06 - Blind XXE OOB]] — when response doesn't echo entity
- [[08 - XXE to SSRF]] — using XXE for SSRF attacks
- [[10 - Defense Disable External Entity Processing]] — how to fix
