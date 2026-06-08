---
tags: [vapt, saml, sso, beginner]
difficulty: beginner
module: "20 - SAML"
topic: "20.01 What is SAML and How SSO Works"
---

# 20.01 — What is SAML and How SSO Works

## What Is SAML?

```
SAML = Security Assertion Markup Language
Version: SAML 2.0 (current, from 2005)
Format: XML-based

PURPOSE:
  Single Sign-On (SSO) — one login, access many services
  
  Without SSO:
  User has: Gmail login, Jira login, Slack login, Salesforce login...
  → 10 different passwords, 10 different sessions
  
  With SAML SSO:
  User logs in ONCE to their company's Identity Provider (IdP)
  → Can access ALL connected apps (Service Providers) automatically!
```

---

## The Actors

```
THREE PARTIES IN SAML:

1. USER (Principal / Subject)
   The person trying to access something
   Browser is the intermediary

2. IDENTITY PROVIDER (IdP)
   WHO YOU ARE → authenticates the user
   Examples: Okta, OneLogin, Azure AD, Google Workspace, ADFS
   Holds: user credentials, attributes, group memberships
   Issues: SAML Assertions (signed XML documents proving who you are)

3. SERVICE PROVIDER (SP)
   WHAT YOU WANT TO ACCESS → the actual application
   Examples: Salesforce, Slack, AWS Console, GitHub Enterprise
   Trusts the IdP → accepts signed assertions from it
   Does NOT store user passwords!
```

---

## How SAML SSO Works

```
SP-INITIATED SSO FLOW (most common):

User → tries to access: https://app.salesforce.com/dashboard
       (not logged in)

STEP 1: SP CREATES AuthnRequest
  Salesforce (SP) creates XML request:
  <samlp:AuthnRequest
    ID="_RANDOM_ID"
    Destination="https://idp.company.com/sso/saml"
    AssertionConsumerServiceURL="https://salesforce.com/sso/callback"
    .../>
  
  Encodes it + redirects user to IdP:
  https://idp.company.com/sso/saml?SAMLRequest=BASE64_GZIP_ENCODED_XML

STEP 2: USER AUTHENTICATES WITH IDP
  User arrives at IdP login page (company's Okta/ADFS etc.)
  Enters username + password (+ MFA if configured)
  IdP validates credentials

STEP 3: IDP CREATES AND SIGNS SAML ASSERTION
  IdP creates XML assertion:
  "This user is john.doe@company.com, has role=admin, 
   assertion valid from now until +5min, signed by me (IdP)"
  
  Signs assertion with IdP's PRIVATE KEY

STEP 4: ASSERTION RETURNED TO USER'S BROWSER
  IdP creates HTML form that auto-submits:
  <form action="https://salesforce.com/sso/callback" method="POST">
    <input name="SAMLResponse" value="BASE64_ENCODED_SIGNED_ASSERTION">
    <input name="RelayState" value="ORIGINAL_URL">
  </form>
  <script>document.forms[0].submit()</script>

STEP 5: USER'S BROWSER POSTS TO SP
  Browser auto-submits → posts SAMLResponse to Salesforce

STEP 6: SP VALIDATES ASSERTION
  Salesforce receives SAMLResponse
  Decodes base64 → gets XML
  Verifies signature using IdP's PUBLIC KEY
  Checks: issuer, audience, timing, signature → ALL OK!
  
STEP 7: SP GRANTS ACCESS
  Salesforce creates local session for the user
  User arrives at dashboard!

VISUAL FLOW:
  User ──── request ────► Salesforce
  User ◄─── redirect ─── Salesforce (to IdP)
  User ──── AuthnRequest ─► IdP login page
  User ◄─── login form ── IdP
  User ──── credentials ─► IdP
  User ◄─── POST form ─── IdP (with SAMLResponse)
  User ──── SAMLResponse ► Salesforce
  User ◄─── session ───── Salesforce (logged in!)
```

---

## IdP-Initiated SSO Flow

```
ALTERNATIVE: User starts from IdP portal:

  User → logs in at company IdP portal
  Portal shows: "Available Apps" (Salesforce, Slack, AWS...)
  User clicks: "Salesforce"
  
  IdP creates assertion immediately → posts to Salesforce
  (No AuthnRequest from SP first!)
  
  SECURITY NOTE:
  IdP-initiated is LESS SECURE:
  → No AuthnRequest means SP can't verify InResponseTo
  → More vulnerable to assertion replay attacks
  → SP should validate RelayState and other anti-replay measures
```

---

## SAML vs OAuth vs OIDC

```
COMPARISON:

SAML:
  Format: XML (verbose, complex)
  Use case: Enterprise SSO (HR systems, SaaS)
  Protocol: Browser-redirects + POST bindings
  Token: XML Assertion (signed)
  Age: 2005, enterprise-focused
  
OAUTH 2.0:
  Format: JSON
  Use case: API authorization (let app access your data)
  Token: Opaque or JWT access tokens
  Age: 2012, web/mobile-focused
  
OIDC:
  Format: JSON (JWTs)
  Use case: Authentication + SSO (consumer: Google/Apple login)
  Built on: OAuth 2.0
  Token: ID token (JWT) + access token
  Age: 2014, web/mobile-focused
  
RULE OF THUMB:
  Enterprise SSO (company apps) → usually SAML
  Consumer login (Google/Facebook) → usually OIDC/OAuth
  API access delegation → usually OAuth
```

---

## Where to Find SAML in the Wild

```
LOOK FOR SAML WHEN:
  - Company uses Okta, OneLogin, Azure AD, ADFS, PingFederate, Shibboleth
  - URL contains: /saml, /sso, /Shibboleth.sso, /ADFS/
  - Response contains: SAMLResponse, SAMLRequest
  - Request has: base64 encoded XML (decode → <saml:...)
  
COMMON SAML ENDPOINTS:
  /saml/acs                           ← ACS (Assertion Consumer Service)
  /sso/saml                           ← SP-side SSO URL
  /saml/callback                      ← callback after IdP auth
  /SAML2/SSO/POST                     ← Shibboleth style
  https://idp.example.com/sso/saml    ← IdP SSO endpoint
  
HOW TO IDENTIFY IN BURP:
  Look for POST requests with SAMLResponse parameter
  Decode: base64 → gunzip (if compressed) → XML
  echo "BASE64_VALUE" | base64 -d | gunzip 2>/dev/null | xmllint --format -
```

---

## Related Notes
- [[02 - SAML Assertion Structure]] — what's inside a SAML assertion
- [[03 - XML Signature Wrapping (XSW) Attacks]] — main SAML attack
- [[09 - SAML to Account Takeover]] — full ATO chain
- [[10 - Defense — Strict Schema Validation, Signed Assertions]] — fixes
