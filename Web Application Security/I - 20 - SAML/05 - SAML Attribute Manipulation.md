---
tags: [vapt, saml, intermediate]
difficulty: intermediate
module: "20 - SAML"
topic: "20.05 SAML Attribute Manipulation"
---

# 20.05 — SAML Attribute Manipulation

## What Are SAML Attributes?

```
SAML ASSERTIONS CARRY ATTRIBUTES:
  Beyond just "who you are" (NameID), IdP sends extra info:
  
  <saml:AttributeStatement>
    <saml:Attribute Name="email">
      <saml:AttributeValue>john@company.com</saml:AttributeValue>
    </saml:Attribute>
    <saml:Attribute Name="role">
      <saml:AttributeValue>user</saml:AttributeValue>
    </saml:Attribute>
    <saml:Attribute Name="groups">
      <saml:AttributeValue>employees</saml:AttributeValue>
    </saml:Attribute>
    <saml:Attribute Name="department">
      <saml:AttributeValue>engineering</saml:AttributeValue>
    </saml:Attribute>
  </saml:AttributeStatement>
  
  SP USES THESE TO:
  - Determine user's role within the SP app
  - Map to internal permissions
  - Grant access to specific resources
  
  ATTACK SURFACE:
  If attributes can be modified (signature bypass required)
  → Role escalation, unauthorized access, impersonation
```

---

## Attack Scenario

```
SETUP:
  SP uses SAML attribute "role" to determine permissions:
  role=user → regular user
  role=admin → admin access
  role=superadmin → full access
  
  ATTACK (requires signature bypass or XSW):
  Decode SAMLResponse → modify XML:
  
  ORIGINAL:
  <saml:AttributeValue>user</saml:AttributeValue>
  
  MODIFIED:
  <saml:AttributeValue>admin</saml:AttributeValue>
  
  If SP doesn't properly validate signature → escalated to admin!

COMMON ATTRIBUTES TO TARGET:
  role, roles, groups, permissions
  isAdmin, is_admin, admin
  userType, user_type, accountType
  accessLevel, level, tier
  email (for identity confusion)
  department (for data segregation bypass)
```

---

## Method 1: Direct Modification + Signature Strip

```
APPROACH: Remove signature → modify attributes → hope SP doesn't check

STEPS:
  1. Decode SAMLResponse (base64 → XML)
  2. Find and DELETE the entire <ds:Signature> element
  3. Modify NameID or attribute values
  4. Re-encode base64
  5. Submit

IF SP DOESN'T VALIDATE SIGNATURE EXISTS:
  → Accepts the assertion! → attribute manipulation works!
  
TESTING:
  In Burp, decode SAMLResponse
  Remove <ds:Signature>...</ds:Signature>
  Re-encode → forward → did it work?
  
  SAML Raider automates this:
  "Remove Signature" button → modify → send
```

---

## Method 2: XSW for Attribute Manipulation

```
XSW + ATTRIBUTE MODIFICATION:
  Signature is valid → but SP processes attacker's attributes
  
  APPROACH:
  Use XSW variant to add unsigned assertion with admin attributes
  While keeping original signed assertion (with user attributes) present
  
  IF SP processes first-found or most-specific assertion:
  → Gets attacker's admin attributes from unsigned copy!
  → But signature validation passes on original signed copy!
```

---

## Method 3: Attribute Type Confusion

```
SOME SPs USE ATTRIBUTE VALUES FOR AUTHORIZATION:
  AND THEY MIGHT COMPARE INCORRECTLY:
  
  Case 1: Case Insensitive Comparison
  "admin" vs "Admin" vs "ADMIN" vs "Admin " (trailing space)
  
  Try all variations if attribute value validation seems strict:
  <saml:AttributeValue>Admin</saml:AttributeValue>
  <saml:AttributeValue>ADMIN</saml:AttributeValue>
  <saml:AttributeValue> admin</saml:AttributeValue>  (leading space)
  
  Case 2: Array vs String Interpretation
  Some SPs check: if attributes.role == "admin"
  What if: <saml:AttributeValue>user</saml:AttributeValue>
             <saml:AttributeValue>admin</saml:AttributeValue>
  → Role attribute has TWO values! 
  → "user" AND "admin"
  → Does SP grant access if ANY value matches "admin"?
  
  Try adding a second AttributeValue with "admin":
  Original (valid, signed):
  <saml:AttributeValue>user</saml:AttributeValue>
  
  Inject (unsigned, via XSW):
  <saml:AttributeValue>user</saml:AttributeValue>
  <saml:AttributeValue>admin</saml:AttributeValue>
```

---

## Testing Attribute Manipulation

```bash
# STEP 1: IDENTIFY WHAT ATTRIBUTES SP USES:
# Look at the assertion:
echo "SAML_VALUE" | base64 -d | grep -A2 "Attribute Name"
# Note: role, groups, email attributes

# STEP 2: DETERMINE IF SIGNATURE IS VALIDATED:
# Remove signature → does SP accept?
# (Quickest test for whether any attribute manipulation is possible)

# STEP 3: TRY MODIFYING HIGH-VALUE ATTRIBUTES:
# If signature not validated OR XSW works:

# Modify via Python:
import base64, re

saml_b64 = "ORIGINAL_SAML_VALUE"
xml = base64.b64decode(saml_b64).decode()

# Change role:
xml_modified = xml.replace(
    '<saml:AttributeValue>user</saml:AttributeValue>',
    '<saml:AttributeValue>admin</saml:AttributeValue>'
)

# Re-encode:
print(base64.b64encode(xml_modified.encode()).decode())

# STEP 4: SUBMIT MODIFIED RESPONSE:
# Paste into Burp → forward → observe behavior
# → Got admin access? → Attribute manipulation vulnerability!

# STEP 5: TRY MULTIPLE ATTRIBUTE VALUES:
# Add second AttributeValue element with privileged value
# Does SP grant access based on any value?
```

---

## Fix

```
PREVENTING ATTRIBUTE MANIPULATION:

1. ALWAYS VALIDATE SIGNATURE (fundamental):
   If signature is stripped → reject!
   Attribute values ONLY trusted if assertion is properly signed

2. STRICT ATTRIBUTE SCHEMA:
   Define expected attributes and their allowed values
   Role must be in: ["user", "manager", "readonly"]
   Any other value → reject or default to lowest privilege

3. NEVER USE SAML ATTRIBUTES AS PRIMARY AUTH DECISION:
   BAD:  SP checks SAML role=admin → grants admin access
   GOOD: SP maps SAML attributes to local user record → apply local ACL
   
   Even with valid signature, IdP might issue unexpected attribute values!
   Maintain local authorization data, use SAML only for authentication

4. AUDIT ATTRIBUTE MAPPING:
   Document: which SAML attributes map to which permissions
   Ensure each mapping is validated and audited

5. USE ATTRIBUTE-LEVEL SIGNATURES (if supported):
   Some IdPs can sign individual attribute statements
   → Stronger tamper protection
```

---

## Related Notes
- [[02 - SAML Assertion Structure]] — assertion elements
- [[03 - XML Signature Wrapping (XSW) Attacks]] — how to bypass signature
- [[08 - SAML Signature Bypass (none algorithm)]] — removing signature
- [[09 - SAML to Account Takeover]] — full attack chains
- [[10 - Defense — Strict Schema Validation, Signed Assertions]] — full fix
