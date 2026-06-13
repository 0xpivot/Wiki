---
tags: [vapt, injection, intermediate]
difficulty: intermediate
module: "10 - Injection Attacks"
topic: "10.03 XML Injection"
---

# 10.03 — XML Injection

## What is XML Injection?

XML Injection occurs when user input is embedded into an XML document without proper encoding. Attackers can break the XML structure, inject new elements, or manipulate existing ones.

```
VULNERABLE XML BUILDING:
  <user>
    <name>USER_INPUT</name>
    <role>guest</role>
  </user>

INJECT: </name><role>admin</role><name>john
RESULT:
  <user>
    <name></name><role>admin</role><name>john</name>
    <role>guest</role>
  </user>

→ Parser reads role = admin (first occurrence wins or app uses first!)
→ Privilege escalation via XML injection!
```

---

## XML Special Characters

```
< = &lt;    (less-than — closes XML tags)
> = &gt;    (greater-than)
& = &amp;   (ampersand — starts entity reference)
' = &apos;  (apostrophe — attribute delimiter)
" = &quot;  (quote — attribute delimiter)

IF NOT ENCODED IN USER INPUT → XML injection possible!
```

---

## XML Injection Attack Scenarios

### Breaking XML Structure

```xml
<!-- ORIGINAL: -->
<order>
  <item>USER_INPUT</item>
  <price>10.00</price>
</order>

<!-- INJECT: laptop</item><price>0.01</price><item>laptop -->
<!-- RESULT: -->
<order>
  <item>laptop</item><price>0.01</price><item>laptop</item>
  <price>10.00</price>
</order>
<!-- → Price changed to 0.01! Business logic bypass! -->
```

### Role Escalation

```xml
<!-- ORIGINAL: -->
<user>
  <username>USER_INPUT</username>
  <role>user</role>
</user>

<!-- INJECT: john</username><role>admin</role><username>john -->
<!-- RESULT: -->
<user>
  <username>john</username><role>admin</role><username>john</username>
  <role>user</role>
</user>
<!-- → If app reads first <role> → gets "admin"! -->
```

### Comment Injection

```xml
<!-- INJECT: test--><!--<secret> (close comment, open new comment) -->
<!-- Or: --%><inject>
<!-- → Can hide legitimate XML content inside injected comment! -->
```

---

## Testing XML Injection

```bash
# STEP 1: INJECT SINGLE ANGLE BRACKET:
?name=test<
# XML error? → possible injection!

# STEP 2: INJECT AMPERSAND:
?name=test&
# Error: "XML entity reference not well-formed"? → vulnerable

# STEP 3: INJECT XML CLOSE TAG:
?name=test</name>
# Error or unexpected behavior? → injectable

# STEP 4: TRY STRUCTURE BREAK:
?name=</item><price>0.01</price><item>test

# STEP 5: CHECK WITH XML VALIDATORS:
# If app processes XML and reflects it back → try full injection
```

---

## SOAP Injection (XML Injection in Web Services)

```xml
<!-- SOAP REQUEST: -->
POST /service HTTP/1.1
Content-Type: text/xml

<soap:Envelope xmlns:soap="...">
  <soap:Body>
    <login>
      <username>USER_INPUT</username>
      <password>PASS_INPUT</password>
    </login>
  </soap:Body>
</soap:Envelope>

<!-- INJECT IN USERNAME: -->
admin</username><password>ignored</password><!--

<!-- RESULT: -->
<username>admin</username><password>ignored</password><!--</username>
<password>PASS_INPUT</password>
<!-- The app may read: username=admin, password=ignored (injected) -->
<!-- while real password is in a comment! -->
```

---

## Defense

```
PROTECTION:
  1. XML encode all user input:
     < → &lt;  > → &gt;  & → &amp;  ' → &apos;  " → &quot;
  
  2. Use DOM API to build XML (not string concatenation!):
     // Java (safe):
     Element nameEl = doc.createElement("name");
     nameEl.setTextContent(userInput);  ← textContent auto-escapes!
     
     // Python (safe):
     from lxml import etree
     root = etree.Element("user")
     name = etree.SubElement(root, "name")
     name.text = user_input  ← auto-escaped!
  
  3. Validate XML structure after building
  4. Use schema validation (XSD) to enforce allowed structure
```

---

## Related Notes
- [[02 - XPath Injection]] — XPath queries on XML
- [[Module 14 - XXE]] — XML External Entity attacks (more dangerous!)
- [[10 - CRLF Injection]] — header injection
