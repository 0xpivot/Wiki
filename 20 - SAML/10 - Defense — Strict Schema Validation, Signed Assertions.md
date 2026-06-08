---
tags: [vapt, saml, defense]
difficulty: intermediate
module: "20 - SAML"
topic: "20.10 Defense — Strict Schema Validation, Signed Assertions"
---

# 20.10 — Defense: Strict Schema Validation, Signed Assertions

## SAML Security Checklist

```
SIGNATURE VALIDATION:
  □ wantAssertionsSigned = True (require signed assertions)
  □ wantMessagesSigned = True (require signed response)
  □ IdP certificate pre-configured at SP (not from assertion KeyInfo)
  □ Algorithm allowlist: RSA-SHA256 minimum, reject SHA1/MD5
  □ Reject unsigned assertions (no signature = reject)
  □ Validate signature BEFORE processing any content

IDENTITY & ASSERTION CONTENT:
  □ Validate issuer (iss) matches expected IdP entity ID
  □ Validate audience matches this SP's entity ID
  □ Validate NotOnOrAfter (reject expired assertions)
  □ Validate NotBefore (reject future assertions, allow ±5min clock skew)
  □ Track assertion IDs (prevent replay)
  □ Validate InResponseTo (for SP-initiated flows)

XML PROCESSING SECURITY:
  □ Disable XXE: DOCTYPE declarations blocked in parser
  □ Remove XML comments before parsing (prevent comment injection)
  □ Strict schema validation before processing
  □ Reject multiple assertions unless all signed and expected
  □ Use signed element ID to locate assertion (not XPath on first found)

ACCOUNT MATCHING:
  □ Map SAML identity to local account securely
  □ Reject unknown users (or provision with least privilege)
  □ Don't use just email for matching if email can change
  □ Verify email_verified claim if used for matching

ENDPOINT SECURITY:
  □ ACS URL pre-registered, not taken from AuthnRequest
  □ HTTPS required for all SAML endpoints
  □ No caching of SAML responses/assertions
  □ Referrer-Policy: no-referrer on ACS endpoint

LIBRARY:
  □ Using maintained SAML library (not custom implementation)
  □ Library version is recent/patched
  □ Configured securely (not default "permissive" settings)
```

---

## python3-saml Secure Configuration

```python
# pip install python3-saml

from onelogin.saml2.auth import OneLogin_Saml2_Auth
from onelogin.saml2.settings import OneLogin_Saml2_Settings
import defusedxml  # automatically used by python3-saml

# settings.json or Python dict:
SAML_SETTINGS = {
    # SP (this application):
    "sp": {
        "entityId": "https://myapp.example.com/saml/metadata",
        "assertionConsumerService": {
            "url": "https://myapp.example.com/saml/acs",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST"
        },
        "singleLogoutService": {
            "url": "https://myapp.example.com/saml/sls",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        },
        "NameIDFormat": "urn:oasis:names:tc:SAML:1.1:nameid-format:emailAddress",
        "x509cert": "",  # SP cert for encryption (optional)
        "privateKey": ""
    },
    
    # IdP (the identity provider):
    "idp": {
        "entityId": "https://idp.example.com",
        "singleSignOnService": {
            "url": "https://idp.example.com/sso/saml",
            "binding": "urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect"
        },
        # PRE-REGISTERED CERTIFICATE — never trust assertion KeyInfo!
        "x509cert": "MIIC...IdP_CERT_HERE...==",
    },
    
    # SECURITY — these are the critical settings:
    "security": {
        # Require signatures:
        "authnRequestsSigned": True,        # sign our AuthnRequests
        "logoutRequestSigned": True,
        "logoutResponseSigned": True,
        "wantMessagesSigned": True,          # ← REQUIRE signed Response
        "wantAssertionsSigned": True,        # ← REQUIRE signed Assertion
        "wantAssertionsEncrypted": False,    # optional but recommended
        "signMetadata": True,
        
        # Algorithm:
        "signatureAlgorithm": "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256",
        "digestAlgorithm": "http://www.w3.org/2001/04/xmlenc#sha256",
        
        # Replay prevention:
        "rejectDeprecatedAlgorithm": True,  # reject SHA1
        "relaxDestinationValidation": False, # strict destination check
        "destinationStrictlyMatches": True,
    }
}

# ACS endpoint:
from flask import request, session, redirect

@app.route('/saml/acs', methods=['POST'])
def saml_acs():
    req = {
        'https': 'on' if request.scheme == 'https' else 'off',
        'http_host': request.host,
        'script_name': request.path,
        'get_data': request.args.copy(),
        'post_data': request.form.copy()
    }
    
    auth = OneLogin_Saml2_Auth(req, custom_base_path=SAML_SETTINGS_PATH)
    auth.process_response()
    
    errors = auth.get_errors()
    if errors:
        return f"SAML Error: {errors}", 400
    
    if not auth.is_authenticated():
        return "Authentication failed", 401
    
    # Get validated attributes:
    user_id = auth.get_nameid()
    attributes = auth.get_attributes()
    
    # Map to local account:
    session['user'] = get_or_create_user(user_id, attributes)
    
    relay_state = request.form.get('RelayState', '/')
    return redirect(relay_state)
```

---

## Assertion Replay Prevention

```python
import redis
from datetime import datetime, timezone

r = redis.Redis()

def check_and_mark_assertion(assertion_id, not_on_or_after):
    """
    Returns True if assertion is new (not seen before).
    Returns False if assertion ID was already used (replay!).
    """
    key = f"saml_assertion:{assertion_id}"
    
    # Atomic check-and-set (prevents race conditions):
    result = r.setnx(key, "used")  # SET if Not eXists
    
    if not result:
        # Key already existed → this assertion was already used!
        return False
    
    # Calculate TTL: expire the key when assertion would have expired anyway
    now = datetime.now(timezone.utc)
    ttl = max(int((not_on_or_after - now).total_seconds()) + 300, 60)
    r.expire(key, ttl)
    
    return True  # New assertion, OK to proceed

# In ACS handler:
if not check_and_mark_assertion(assertion.id, assertion.not_on_or_after):
    return "Assertion already used!", 400
```

---

## XXE Prevention in XML Parsing

```python
# ALWAYS use defusedxml for SAML XML processing:
import defusedxml.ElementTree as ET

# OR: lxml with security options:
from lxml import etree

def safe_parse_xml(xml_string):
    if b'<!DOCTYPE' in xml_string or b'<!ENTITY' in xml_string:
        raise ValueError("DOCTYPE/ENTITY not allowed in SAML")
    
    parser = etree.XMLParser(
        no_network=True,          # no external resource fetching
        resolve_entities=False,   # don't resolve &entities;
        load_dtd=False,           # don't load DTD
        dtd_validation=False,
    )
    return etree.fromstring(xml_string, parser=parser)

# ALSO: Strip comments before processing:
def strip_xml_comments(xml_string):
    from lxml import etree
    parser = etree.XMLParser(remove_comments=True)
    tree = etree.fromstring(xml_string, parser=parser)
    return etree.tostring(tree)
```

---

## Secure Account Provisioning

```python
def get_or_create_user(name_id, saml_attributes):
    """Map SAML identity to local user safely"""
    
    # Use provider + NameID as unique identifier (not email!)
    idp_entity_id = "https://idp.company.com"
    
    user = db.query(
        "SELECT * FROM saml_users WHERE idp_entity_id = ? AND name_id = ?",
        [idp_entity_id, name_id]
    ).fetchone()
    
    if not user:
        # First login: provision new user with minimum privileges
        email = saml_attributes.get('email', [name_id])[0]
        role = 'user'  # NEVER: take role from SAML attributes directly!
        # Or: map from known group membership:
        groups = saml_attributes.get('groups', [])
        if 'admins' in groups:
            role = 'admin'  # only from trusted SAML group claim
        
        user = db.execute(
            "INSERT INTO saml_users (idp_entity_id, name_id, email, role) VALUES (?,?,?,?)",
            [idp_entity_id, name_id, email, role]
        )
    
    return user

# NOTE: Map SAML role/group claims to LOCAL roles
# Don't blindly trust arbitrary SAML attribute values for privilege escalation!
```

---

## Testing Your SAML Implementation

```bash
# CHECK CONFIGURATION:
# Test 1: Is signature required?
# Decode SAMLResponse → remove signature → submit
# → Should return 400/error, not login!

# Test 2: Is audience validated?
# Decode → change <saml:Audience>OTHER_SP</saml:Audience> → submit
# → Should reject (audience mismatch)

# Test 3: Is expiry validated?
# Wait 10 minutes, replay old assertion
# → Should reject (expired)

# Test 4: Is replay tracked?
# Use same assertion twice immediately
# → Second attempt should reject

# Test 5: Is XXE blocked?
# Prepend DOCTYPE to SAMLResponse XML
# → Should reject

# Test 6: Is comment injection safe?
# Modify NameID to: admin<!--comment-->@company.com
# → Should not log in as admin

# AUTOMATED SCANNING:
# SAML Raider in Burp → run all XSW variants
# → All should fail (rejected by SP)
```

---

## Related Notes
- [[01 - What is SAML and How SSO Works]] — SAML overview
- [[03 - XML Signature Wrapping (XSW) Attacks]] — XSW attacks
- [[04 - SAML Replay Attack]] — replay prevention
- [[07 - SAML External Entity (SAML + XXE)]] — XXE prevention
- [[09 - SAML to Account Takeover]] — full attack chains
