---
tags: [vapt, saml, advanced]
difficulty: advanced
module: "20 - SAML"
topic: "20.09 SAML to Account Takeover"
---

# 20.09 — SAML to Account Takeover

## Overview: ATO via SAML

```
SAML ATO CHAINS:

Chain A: Signature Not Validated → Any Identity
  Remove signature → change NameID → admin@company.com → ATO!

Chain B: XSW Attack → Claim Any Identity
  Forge unsigned assertion + keep valid signed → SP processes forged → ATO!

Chain C: Comment Injection → Confuse Identity
  Inject XML comment in NameID → parser confusion → target identity!

Chain D: Assertion Replay → Impersonate Past User
  Capture old assertion → replay → session as victim!

Chain E: SAML + Open Redirect → Assertion Theft
  Phish victim → capture their assertion → replay it!

Chain F: Email-Based Account Linking Confusion
  SAML email ≠ internal account email? → account confusion → ATO!
```

---

## Chain A: Signature Not Validated (Simplest)

```
REQUIREMENTS:
  SP does not validate SAML signature (or can be bypassed)

FULL ATTACK:
  1. Initiate SAML login to SP
  2. Get a valid SAMLResponse (for your own attacker account)
  3. Decode: base64 → XML
  4. Delete <ds:Signature> element
  5. Change NameID: attacker@evil.com → victim@company.com
     (Or: change role attribute: user → admin)
  6. Re-encode: XML → base64
  7. Submit modified SAMLResponse to /saml/acs
  
  → SP processes without signature → logged in as victim!

IMPACT:
  Full account takeover of ANY user in the SP
  (Even users who never logged in via SAML!)
  → SP might match by email to existing local accounts

TEST VERIFICATION:
  After login: visit /profile or /whoami
  → Shows victim's account? → ATO confirmed!
  
SEVERITY: CRITICAL
```

---

## Chain B: XSW for Identity Takeover

```
REQUIREMENTS:
  SP vulnerable to XML Signature Wrapping
  SP processes first/outermost assertion (not the signed one)

FULL ATTACK:
  1. Log in as attacker → capture SAMLResponse
  2. Decode → XML
  3. Add UNSIGNED assertion BEFORE the signed one:
  
  <!-- INJECTED: unsigned, admin identity -->
  <saml:Assertion ID="_forged">
    <saml:NameID>admin@company.com</saml:NameID>
    <saml:Attribute Name="role">
      <saml:AttributeValue>admin</saml:AttributeValue>
    </saml:Attribute>
    ... (copy conditions, audience from original) ...
  </saml:Assertion>
  
  <!-- ORIGINAL: signed, attacker identity -->
  <saml:Assertion ID="_legit">
    <ds:Signature>VALID_SIGNATURE_FOR_LEGIT</ds:Signature>
    <saml:NameID>attacker@evil.com</saml:NameID>
  </saml:Assertion>

  4. Signature validation: checks _legit → VALID!
  5. SP identity extraction: reads _forged (first found) → admin@company.com!
  6. Logged in as admin!

SAML RAIDER AUTOMATION:
  XSW tab → XSW1 → modify NameID in injected assertion → Apply → Send
```

---

## Chain C: Forging Identity via Signed Certificate Substitution

```
REQUIREMENTS:
  SP trusts any certificate provided in assertion's KeyInfo
  (Instead of pre-configured IdP cert)

FULL ATTACK:
  1. Generate RSA key pair:
     openssl genrsa -out attacker.pem 2048
     openssl req -x509 -new -key attacker.pem -out attacker.crt -days 365 -subj "/CN=attacker"
  
  2. Craft completely forged assertion:
  <saml:Assertion ...>
    <saml:NameID>admin@company.com</saml:NameID>
    ...
  </saml:Assertion>
  
  3. Sign with attacker's private key (using xmlsec1 or Python)
  
  4. Embed attacker's certificate in assertion:
  <ds:KeyInfo>
    <ds:X509Certificate>ATTACKER_CERT_BASE64</ds:X509Certificate>
  </ds:KeyInfo>
  
  5. Submit → SP uses attacker's cert → verifies signature → "valid"!
  → Logged in as admin!
```

---

## Chain D: Account Takeover via SAML Replay

```
SETUP:
  Attacker obtains victim's SAML assertion
  (via XSS, log exposure, Referer header, MITM on non-HTTPS)

ATTACK:
  1. Capture valid SAMLResponse for victim
  2. Submit it immediately (before NotOnOrAfter):
  POST /saml/acs
  SAMLResponse=VICTIM_ASSERTION
  
  3. SP processes → creates session as victim → ATO!
  
  TIME WINDOW: usually 5 minutes (NotOnOrAfter)
  But if replay not tracked → can be reused until expiry

HOW TO OBTAIN VICTIM ASSERTION:
  - XSS on the SP that captures SAMLResponse POST body
  - Intercept traffic on HTTP (if SP doesn't enforce HTTPS)
  - Social engineering: trick victim into submitting assertion to attacker's page
    (attacker sets up fake SP endpoint, sends victim auth link)
```

---

## Chain E: SP-Initiated Flow Hijacking

```
ATTACK ON MULTI-PARTY SAML:
  Target has: Company internal apps using SAML via Okta IdP
  Attacker goal: access internal Jira (SP)
  
  IF: Attacker can phish victim to click a specially crafted SAML auth link
  AND: Victim authenticates with IdP (Okta)
  AND: Assertion is sent to URL attacker controls (open redirect / misconfig)
  → Attacker receives victim's assertion → replays to Jira!
  
FULL CHAIN:
  1. Craft SAML AuthnRequest with ACS URL changed to attacker's site
     (Some IdPs accept ACS URLs not pre-registered — misconfiguration!)
  2. Phish victim to click the link
  3. Victim authenticates with Okta
  4. Okta sends assertion to ATTACKER's URL
  5. Attacker receives SAMLResponse in attacker server logs
  6. Attacker replays to real Jira ACS endpoint
  7. Jira: valid signature from Okta → creates session → ATO!
  
  REQUIREMENT:
  IdP must NOT validate that ACS URL is pre-registered
  → Legacy SAML implementations sometimes allowed this!
```

---

## Writing the Full Report

```
TITLE: Account Takeover via SAML Signature Bypass

SEVERITY: Critical

SUMMARY:
  The application's SAML Single Sign-On implementation fails to validate
  the cryptographic signature on SAML assertions. An attacker can forge
  a SAML assertion claiming any user identity, bypassing authentication
  entirely and gaining access to any account.

STEPS TO REPRODUCE:
  1. Navigate to [login page] and select "Login with SSO"
  2. Intercept the SAMLResponse in Burp Suite
  3. Decode the base64 SAMLResponse
  4. Remove the <ds:Signature> element
  5. Change the NameID value to victim@company.com
  6. Re-encode and forward the modified request
  7. Observe: browser is now logged in as victim@company.com

IMPACT:
  Full account takeover of any user account in the application.
  No user interaction or victim credentials required.
  This includes administrator accounts.

PROOF OF CONCEPT:
  [Screenshots showing account before and after]
  [Burp logs]

REMEDIATION:
  1. Require signature validation: wantAssertionsSigned = True
  2. Configure SP with pre-registered IdP certificate
  3. Verify signature before processing any assertion content
  See note 20.10 for full remediation checklist.
```

---

## Related Notes
- [[03 - XML Signature Wrapping (XSW) Attacks]] — XSW details
- [[08 - SAML Signature Bypass (none algorithm)]] — signature bypass details
- [[04 - SAML Replay Attack]] — assertion replay
- [[10 - Defense — Strict Schema Validation, Signed Assertions]] — full fix
