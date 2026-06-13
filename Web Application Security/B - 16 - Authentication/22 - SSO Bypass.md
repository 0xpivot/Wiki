---
tags: [vapt, authentication, saml, oauth, intermediate]
difficulty: intermediate
module: "16 - Authentication"
topic: "16.22 SSO Bypass (SAML, OAuth)"
portswigger_labs: ["SAML authentication bypass"]
---

# 16.22 — SSO Bypass (SAML, OAuth)

## What Is SSO?

```
SINGLE SIGN-ON (SSO):
  Login once → access multiple applications
  
  ENTERPRISE EXAMPLE:
  Login to corporate IdP (Okta, Azure AD) 
  → Access Gmail, Salesforce, Jira without re-entering credentials
  
  CONSUMER EXAMPLE:
  Login with Google/Facebook → access many websites
  
TECHNOLOGIES:
  SAML 2.0:   XML-based (enterprise/B2B)
  OAuth 2.0 / OIDC: JSON/JWT-based (consumer/API)
  
WHERE TO ATTACK:
  The assertion/token validation step
  If you can forge or tamper the identity assertion → bypass auth!
```

---

## SAML Vulnerabilities

```
SAML FLOW:
  1. User accesses Service Provider (SP): app.example.com
  2. SP redirects to Identity Provider (IdP): okta.com/saml
  3. User authenticates at IdP
  4. IdP sends SAML Assertion (signed XML) to SP via browser POST
  5. SP validates assertion signature → logs user in

THE SAML ASSERTION (XML):
  <saml:Assertion ...>
    <saml:AttributeStatement>
      <saml:Attribute Name="email">
        <saml:AttributeValue>user@example.com</saml:AttributeValue>
      </saml:Attribute>
      <saml:Attribute Name="role">
        <saml:AttributeValue>user</saml:AttributeValue>
      </saml:Attribute>
    </saml:AttributeStatement>
    <ds:Signature> ... CRYPTOGRAPHIC SIGNATURE ... </ds:Signature>
  </saml:Assertion>

ATTACK SURFACE:
  Can we modify the XML without breaking the signature?
```

---

## SAML Attack 1: XML Signature Wrapping (XSW)

```
CONCEPT:
  SAML assertion is signed, but WHERE in the XML does the SP check?
  
  If SP checks: "is there a valid signature somewhere in this XML?"
  → Attacker can ADD a new (malicious) assertion AND keep the valid signature!
  
  The SP sees: valid signature exists → user authenticated!
  But processes: the NEW malicious content (not what was signed)!

ATTACK:
  Original (legitimate, signed):
  <Response>
    <SignedAssertion ID="abc">
      <email>alice@company.com</email>
      <Signature>VALID_SIG_OVER_abc</Signature>
    </SignedAssertion>
  </Response>
  
  Modified (XSW attack):
  <Response>
    <SignedAssertion ID="abc">      ← attacker copies legitimate signed one
      <email>alice@company.com</email>   (still has valid signature)
      <Signature>VALID_SIG_OVER_abc</Signature>
    </SignedAssertion>
    <Assertion ID="xyz">           ← NEW assertion, NOT signed!
      <email>admin@company.com</email>  ← attacker's target!
    </Assertion>
  </Response>
  
  If SP uses the unsigned "xyz" assertion for auth → attacker = admin!

TOOL: SAML Raider (Burp extension)
  Intercepts SAML → auto-generates XSW variants → test each
```

---

## SAML Attack 2: Comment Injection

```
VULNERABILITY (CVE-2017-11427 and family):
  Some parsers ignore XML comments
  
  Assertion signed for: alice@company.com
  
  ATTACK: Inject comment to confuse parser:
  <email>alice@company.com<!--attacker@evil.com--></email>
  
  SAML library signs: "alice@company.com<!--attacker@evil.com-->"
  But app extracts username by stripping comments:
  → Uses: "alice@company.com" + "attacker@evil.com"?
  
  Depends on which parsing library → affects: OneLogin, SimpleSAMLphp, Duo
  
ANOTHER VARIANT:
  user@company.com<!---->admin@company.com
  → Signing library sees: "user@company.com<!---->admin@company.com"
  → App sees: "user@company.comadmin@company.com"? Or splits on <!---->?
  → Some parsers: just "admin@company.com"!
```

---

## SAML Attack 3: Signature Stripping

```
IF SP DOESN'T VERIFY SIGNATURE EXISTS:
  Remove the <ds:Signature> element entirely
  Modify the assertion content at will
  → Does the SP still accept it? If yes → no signature verification!
  
TEST:
  1. Capture SAML POST (base64 + URL decode → XML)
  2. Remove entire <ds:Signature>...</ds:Signature> block
  3. Change email/role to admin
  4. Re-encode (base64 → URL encode)
  5. Replay → if you're logged in as admin → no signature check!
```

---

## Testing SAML with Burp + SAML Raider

```
1. Install Burp extension: SAML Raider

2. Intercept SAML POST:
   POST /saml/consume
   SAMLResponse=PD94bWwg...  ← base64 encoded XML
   
3. SAML Raider → Decode → Shows XML

4. Test attacks:
   a) SAML Raider → "Remove Signature" → resend
   b) SAML Raider → "XSW Attacks" → try all 8 XSW variants
   c) Manually edit email/role → re-sign or send unsigned
   
5. Check if any variant grants elevated access
```

---

## OAuth SSO Bypass

```
COMMON OAUTH BYPASS: Not verifying email ownership
  
  FLOW:
  Google OAuth → sends email: "hacker@gmail.com"
  App trusts email → logs in as whoever has that email in their system
  
  ATTACK:
  What if attacker creates Google account with email admin@company.com?
  Some apps TRUST the email from OAuth without verifying domain ownership!
  → Login with crafted Google account → access company internal app!
  
ANOTHER BYPASS: Unverified email field
  Some OAuth providers return both email and email_verified
  If app uses email but doesn't check email_verified=true:
  → Sign up with unverified email → force email on OAuth payload → bypass!
  
TEST:
  1. Check what fields the app uses from OAuth response
  2. Can you influence any of those fields?
  3. Does app verify email_verified is true?
```

---

## Fix

```
SAML DEFENSE:
  ✓ Validate signature using the correct signing certificate
  ✓ Verify signature covers the entire assertion (not just part)
  ✓ Use strict XML parsing (reject comments, DTD, namespaced elements)
  ✓ Validate assertion audience, expiry, and conditions
  ✓ Use battle-tested SAML libraries (not custom implementations!)
  ✓ Test with SAML Raider yourself!
  
OAUTH DEFENSE:
  ✓ Verify email_verified = true before trusting email
  ✓ Link accounts by provider ID (not email!)
    Google returns a stable sub field → use that, not email
  ✓ Verify state parameter (anti-CSRF)
  ✓ Validate client_id matches your application
```

---

## Related Notes
- [[20 - OAuth Login CSRF]] — CSRF via OAuth flow
- [[Module: JWT]] — JWT token attacks (OIDC uses JWTs)
- [[Module: SAML]] — deeper SAML exploitation module
- [[Module: OAuth]] — full OAuth attack surface
