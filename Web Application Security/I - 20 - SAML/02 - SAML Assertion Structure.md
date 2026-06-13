---
tags: [vapt, saml, beginner]
difficulty: beginner
module: "20 - SAML"
topic: "20.02 SAML Assertion Structure"
---

# 20.02 — SAML Assertion Structure

## The SAMLResponse

```
WHAT YOU SEE IN BURP:
  POST /saml/acs HTTP/1.1
  Host: app.example.com
  Content-Type: application/x-www-form-urlencoded
  
  SAMLResponse=PHNhbWxwOlJlc3BvbnNlIHhtbG5z...&RelayState=/dashboard

  SAMLResponse value = base64 encoded XML

DECODE IT:
  echo "PHNhbWxwOlJlc3BvbnNlIHhtbG5z..." | base64 -d
  
  (May also be gzip-compressed for HTTP-Redirect binding:)
  echo "SAMLREQUEST_VALUE" | base64 -d | gunzip
  
  OR use a SAML decoder:
  burp extension: SAML Raider
  online: samltool.com (only use with non-sensitive test data!)
```

---

## Full SAML Response Structure

```xml
<!-- OUTER WRAPPER: samlp:Response (from the IdP) -->
<samlp:Response 
    xmlns:samlp="urn:oasis:names:tc:SAML:2.0:protocol"
    xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
    ID="_response_unique_id_here"
    Version="2.0"
    IssueInstant="2024-01-15T12:00:00Z"
    Destination="https://app.example.com/saml/acs"     ← WHERE SP expects it
    InResponseTo="_authnrequest_id">                   ← Ties to AuthnRequest
    
  <!-- Who sent this response -->
  <saml:Issuer>https://idp.company.com</saml:Issuer>
  
  <!-- Signature on the RESPONSE level (optional — some sign only assertion) -->
  <ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
    <ds:SignedInfo>
      <ds:Reference URI="#_response_unique_id_here">
        <!-- What was signed -->
      </ds:Reference>
    </ds:SignedInfo>
    <ds:SignatureValue>BASE64_SIGNATURE_HERE</ds:SignatureValue>
    <ds:KeyInfo>
      <!-- Public key that can verify this signature -->
      <ds:X509Certificate>CERT_BASE64</ds:X509Certificate>
    </ds:KeyInfo>
  </ds:Signature>
  
  <!-- Status: did auth succeed? -->
  <samlp:Status>
    <samlp:StatusCode Value="urn:oasis:names:tc:SAML:2.0:status:Success"/>
  </samlp:Status>

  <!-- THE ASSERTION — the actual identity claim -->
  <saml:Assertion 
      xmlns:saml="urn:oasis:names:tc:SAML:2.0:assertion"
      ID="_assertion_unique_id"
      Version="2.0"
      IssueInstant="2024-01-15T12:00:00Z">
      
    <saml:Issuer>https://idp.company.com</saml:Issuer>
    
    <!-- Signature on just the ASSERTION (most common) -->
    <ds:Signature xmlns:ds="http://www.w3.org/2000/09/xmldsig#">
      <ds:SignedInfo>
        <ds:Reference URI="#_assertion_unique_id">...</ds:Reference>
      </ds:SignedInfo>
      <ds:SignatureValue>BASE64_ASSERTION_SIGNATURE</ds:SignatureValue>
    </ds:Signature>
    
    <!-- SUBJECT: who is this assertion about? -->
    <saml:Subject>
      <saml:NameID Format="urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress">
        john.doe@company.com    ← THE USERNAME! (attack surface!)
      </saml:NameID>
      <saml:SubjectConfirmation Method="urn:oasis:names:tc:SAML:2.0:cm:bearer">
        <saml:SubjectConfirmationData 
            NotOnOrAfter="2024-01-15T12:05:00Z"   ← assertion expiry!
            Recipient="https://app.example.com/saml/acs"
            InResponseTo="_authnrequest_id"/>
      </saml:SubjectConfirmation>
    </saml:Subject>
    
    <!-- CONDITIONS: when/where this assertion is valid -->
    <saml:Conditions 
        NotBefore="2024-01-15T11:59:55Z"    ← not valid before
        NotOnOrAfter="2024-01-15T12:05:00Z">  ← expires in 5 minutes
      <saml:AudienceRestriction>
        <saml:Audience>https://app.example.com</saml:Audience>  ← FOR THIS SP ONLY!
      </saml:AudienceRestriction>
    </saml:Conditions>
    
    <!-- AUTHNSTATEMENT: how/when user was authenticated -->
    <saml:AuthnStatement AuthnInstant="2024-01-15T12:00:00Z">
      <saml:AuthnContext>
        <saml:AuthnContextClassRef>
          urn:oasis:names:tc:SAML:2.0:ac:classes:PasswordProtectedTransport
        </saml:AuthnContextClassRef>
      </saml:AuthnContext>
    </saml:AuthnStatement>
    
    <!-- ATTRIBUTES: additional user attributes -->
    <saml:AttributeStatement>
      <saml:Attribute Name="email">
        <saml:AttributeValue>john.doe@company.com</saml:AttributeValue>
      </saml:Attribute>
      <saml:Attribute Name="role">
        <saml:AttributeValue>user</saml:AttributeValue>  ← ATTACK SURFACE!
      </saml:Attribute>
      <saml:Attribute Name="groups">
        <saml:AttributeValue>employees</saml:AttributeValue>
        <saml:AttributeValue>salesforce-users</saml:AttributeValue>
      </saml:Attribute>
    </saml:AttributeStatement>
    
  </saml:Assertion>
</samlp:Response>
```

---

## Key Attack Surfaces

```
ELEMENTS TO TARGET IN SAML ATTACKS:

1. NameID (username/identity):
   <saml:NameID>john.doe@company.com</saml:NameID>
   → Can you change this to admin@company.com?
   → If signature wrapping works → claim any identity!

2. Attributes (roles/permissions):
   <saml:AttributeValue>user</saml:AttributeValue>
   → Can you change "user" to "admin"?
   → Privilege escalation!

3. Signature:
   The signature PROTECTS the assertion
   → XSW attacks try to BYPASS it (keep valid sig, add unsigned copy)
   → alg=none tries to REMOVE it (note 08)

4. Conditions (timing):
   NotOnOrAfter="2024-01-15T12:05:00Z"
   → Can you replay assertion after it expires? (if server doesn't check)

5. Audience:
   <saml:Audience>https://app.example.com</saml:Audience>
   → Does SP validate it matches themselves?
   → If not: assertion for SP-A can be used at SP-B!

6. InResponseTo:
   Ties response to original AuthnRequest
   → If not checked: assertion replay / CSRF-like attack
```

---

## How to Decode SAML in Practice

```bash
# DECODE SAMLResponse FROM BURP:
# Copy the SAMLResponse value (URL-decoded already by Burp)

# Decode base64:
echo "BASE64_VALUE_HERE" | base64 -d > saml_response.xml
xmllint --format saml_response.xml  # pretty-print XML

# If HTTP-Redirect binding (GET request, usually compressed):
echo "BASE64_VALUE" | base64 -d | python3 -c "
import sys, zlib
data = sys.stdin.buffer.read()
try:
    print(zlib.decompress(data, -15).decode())  # raw deflate
except:
    print(data.decode())
"

# USING SAML RAIDER (Burp Extension):
# Install: Burp → Extensions → BApp Store → SAML Raider
# Automatically detects and decodes SAML in requests/responses
# Provides GUI to modify and re-sign assertions

# USING PYTHON:
import base64
import xml.dom.minidom

saml_b64 = "BASE64_VALUE"
xml_data = base64.b64decode(saml_b64).decode()
dom = xml.dom.minidom.parseString(xml_data)
print(dom.toprettyxml())
```

---

## Related Notes
- [[01 - What is SAML and How SSO Works]] — SAML overview
- [[03 - XML Signature Wrapping (XSW) Attacks]] — attacking the signature
- [[05 - SAML Attribute Manipulation]] — modifying attributes
- [[10 - Defense — Strict Schema Validation, Signed Assertions]] — fixes
