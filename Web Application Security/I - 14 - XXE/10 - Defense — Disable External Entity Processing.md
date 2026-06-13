---
tags: [vapt, xxe, defense, beginner]
difficulty: beginner
module: "14 - XXE"
topic: "14.10 Defense — Disable External Entity Processing"
---

# 14.10 — Defense: Disable External Entity Processing

## The Core Fix

```
THE ROOT CAUSE:
  XML parsers enable external entity processing by default.
  User-controlled XML is parsed without disabling this.
  
THE FIX:
  Disable external entity processing in the XML parser!
  This is a parser-level configuration — not input validation!
  
  You CANNOT fix XXE by filtering input (too many bypass techniques).
  You MUST configure the parser to disable external entities.
```

---

## Java

```java
// JAVA XML PARSERS HAVE MANY WAYS TO CONFIGURE:

// DocumentBuilderFactory:
DocumentBuilderFactory dbf = DocumentBuilderFactory.newInstance();
dbf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
dbf.setFeature("http://xml.org/sax/features/external-general-entities", false);
dbf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);
dbf.setFeature("http://apache.org/xml/features/nonvalidating/load-external-dtd", false);
dbf.setXIncludeAware(false);
dbf.setExpandEntityReferences(false);
DocumentBuilder db = dbf.newDocumentBuilder();

// SAXParserFactory:
SAXParserFactory spf = SAXParserFactory.newInstance();
spf.setFeature("http://apache.org/xml/features/disallow-doctype-decl", true);
spf.setFeature("http://xml.org/sax/features/external-general-entities", false);
spf.setFeature("http://xml.org/sax/features/external-parameter-entities", false);

// XMLInputFactory (StAX):
XMLInputFactory xif = XMLInputFactory.newInstance();
xif.setProperty(XMLInputFactory.IS_SUPPORTING_EXTERNAL_ENTITIES, false);
xif.setProperty(XMLInputFactory.SUPPORT_DTD, false);

// BEST PRACTICE IN JAVA:
// Use "disallow-doctype-decl" → completely rejects any DOCTYPE declaration
// This is the most secure option if you don't need DOCTYPE at all
```

---

## Python

```python
# PYTHON — DIFFERENT LIBRARIES:

# lxml (most popular — SECURE BY DEFAULT for external entities):
from lxml import etree

parser = etree.XMLParser(
    resolve_entities=False,   # disable external entity resolution
    no_network=True,          # disable network access
    load_dtd=False,           # don't load external DTDs
)
tree = etree.parse(xml_input, parser)

# defusedxml (easiest secure option — drop-in replacement):
pip install defusedxml

import defusedxml.ElementTree as ET
# Just use defusedxml instead of xml.etree.ElementTree
# Automatically safe against XXE, entity expansion bombs, etc.
tree = ET.parse('file.xml')

# xml.etree.ElementTree (Python standard library):
# Not secure against all XXE attacks by default
# Best: use defusedxml instead!

# xmltodict:
import defusedxml.xmltodict as xmltodict  # use defusedxml version!
data = xmltodict.parse(xml_string)
```

---

## PHP

```php
// PHP — libxml:
// Disable external entities:
libxml_disable_entity_loader(true);  // Deprecated in PHP 8.0 (now default behavior)

// For PHP < 8.0:
$dom = new DOMDocument();
libxml_disable_entity_loader(true);
$dom->loadXML($xml, LIBXML_NONET | LIBXML_NOENT);

// SimpleXML — disable external entities:
libxml_disable_entity_loader(true);
$xml = simplexml_load_string($xmlContent, 'SimpleXMLElement', LIBXML_NOENT | LIBXML_NONET);

// PHP 8.0+: external entity loading disabled by default
// Still use LIBXML_NOENT | LIBXML_NONET flags for defense-in-depth

// ALSO: Use a schema validator:
$dom->schemaValidate('schema.xsd');
// If schema doesn't allow DOCTYPE → extra protection
```

---

## Node.js

```javascript
// libxmljs (vulnerable by default — configure it!):
const libxmljs = require('libxmljs');

// UNSAFE (default):
const doc = libxmljs.parseXml(xmlString);

// SAFE:
const doc = libxmljs.parseXml(xmlString, {
  nonet: true,      // no network access
  noent: true,      // don't expand entities (safer)
  dtdattr: false,   // don't use DTD attributes
  dtdload: false,   // don't load external DTDs
  dtdvalid: false,  // don't validate against DTD
});

// xml2js (generally safe — doesn't process DOCTYPE by default):
const xml2js = require('xml2js');
xml2js.parseString(xmlString, (err, result) => { /* ... */ });

// RECOMMENDED: Use xml2js or sax (not libxmljs) for user input!
```

---

## .NET (C#)

```csharp
// XmlDocument — disable DTD:
XmlDocument xmlDoc = new XmlDocument();
xmlDoc.XmlResolver = null;  // prevents external entity resolution!
xmlDoc.LoadXml(xmlString);

// XmlReader — most secure:
XmlReaderSettings settings = new XmlReaderSettings();
settings.DtdProcessing = DtdProcessing.Prohibit;  // blocks DOCTYPE entirely
settings.XmlResolver = null;                       // no external resources
XmlReader reader = XmlReader.Create(new StringReader(xmlString), settings);

// .NET 4.5.2+: XmlDocument defaults to safe settings
// But still explicitly set XmlResolver = null for defense-in-depth
```

---

## Additional Mitigations

```
LAYERED DEFENSE STRATEGY:

1. DISABLE EXTERNAL ENTITIES (primary fix):
   Configure parser → done

2. USE ALLOWLIST FOR XML SCHEMAS:
   Validate parsed XML against a strict schema (XSD)
   Schema should not allow DOCTYPE
   Even if entities were enabled, schema rejects unexpected structure

3. USE SAFER FORMATS:
   JSON instead of XML where possible
   No entity references in JSON

4. LEAST PRIVILEGE:
   App process should not have read access to /etc/passwd, shadow, etc.
   Use separate user with minimal filesystem permissions

5. WAF AS SUPPLEMENTARY (not primary):
   Block <!DOCTYPE, SYSTEM, file:// as an extra layer
   NOT a replacement for parser-level fix!

6. DISABLE XINCLUDE:
   Also disable XInclude processing if not needed:
   // Java lxml: no_network=True covers XInclude over HTTP
   // Java: xmlParser.setFeature("http://apache.org/xml/features/xinclude/fixup-base-uris", false)

7. SANDBOX THE XML PARSER:
   Run parser in a container/sandbox with no network and minimal filesystem
   Even if XXE fires, it can't reach anything!
```

---

## Quick Fix Summary Table

```
LANGUAGE    LIBRARY              FIX
────────────────────────────────────────────────────────────────────────
Java        DocumentBuilderFactory  setFeature(disallow-doctype-decl, true)
Java        SAXParser               setFeature(external-general-entities, false)
Python      lxml                    XMLParser(resolve_entities=False, no_network=True)
Python      any                     Use defusedxml (drop-in replacement)
PHP         DOMDocument             libxml_disable_entity_loader(true) [PHP <8]
PHP         PHP 8+                  Safe by default, add LIBXML_NONET flag
Node.js     libxmljs                {nonet: true, noent: true, dtdload: false}
Node.js     xml2js                  Safe by default
.NET        XmlDocument             XmlResolver = null
.NET        XmlReader               DtdProcessing = DtdProcessing.Prohibit
Ruby        Nokogiri                Safe by default (since 1.5.4)
```

---

## Related Notes
- [[01 - What is XXE]] — fundamentals
- [[03 - Classic XXE File Read]] — what this defense prevents
- [[07 - XXE via XInclude]] — XInclude also needs to be disabled
- [[09 - XXE WAF Bypass]] — why WAF alone is insufficient
