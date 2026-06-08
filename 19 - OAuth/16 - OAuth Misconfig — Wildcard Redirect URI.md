---
tags: [vapt, oauth, intermediate]
difficulty: intermediate
module: "19 - OAuth"
topic: "19.16 OAuth Misconfig — Wildcard Redirect URI"
---

# 19.16 — OAuth Misconfig: Wildcard Redirect URI

## What Is a Wildcard Redirect URI?

```
SOME AUTH SERVERS ALLOW WILDCARD REGISTRATION:
  Instead of: https://app.example.com/callback (exact)
  Allow:      https://*.example.com/*           (wildcard!)
  
  Developer thinks: "This is convenient for our subdomains!"
  Security reality: ANY subdomain + ANY path on example.com can receive codes!
  
  OTHER LOOSELY VALIDATED PATTERNS:
  Prefix match: https://app.example.com/* → any path allowed
  Domain-only:  https://app.example.com   → any path allowed
  Regex:        Bad regex with unescaped dots → bypass via lookalike
  URL-decoded:  https://app.example.com%2Fevil.com → path traversal
```

---

## Attack: Exploiting Wildcard/Prefix Match

```
SCENARIO:
  Registered: https://*.example.com/*
  (All subdomains, all paths)
  
ATTACK:
  Attacker controls (or can inject into): 
  https://evil.example.com OR
  https://user-uploads.example.com (user content)
  
  Craft auth request:
  https://auth.example.com/oauth/authorize?
    client_id=CLIENT_ID&
    redirect_uri=https://evil.example.com/steal&   ← wildcard matches!
    response_type=code&
    scope=email
    
  Auth server: Does evil.example.com match *.example.com? YES!
  → Sends code to attacker's subdomain!
  
FINDING VULNERABLE SUBDOMAINS:
  - subdomain takeover opportunities (dangling DNS)
  - user-content subdomains: user.example.com, uploads.example.com
  - staging/dev subdomains: staging.example.com (less protected)
  - CGI/open redirect on any subdomain of example.com
```

---

## Testing Wildcard Misconfiguration

```bash
# STEP 1: IDENTIFY THE REGISTERED REDIRECT URI:
# From the auth request in Burp:
# redirect_uri=https://app.example.com/callback
# Base domain: example.com

# STEP 2: TEST VARIATIONS:

# Variation 1: Extra path
--data-urlencode "redirect_uri=https://app.example.com/callback/extra"
# 302 to that path? → path wildcard!

# Variation 2: Different path
--data-urlencode "redirect_uri=https://app.example.com/attacker"
# Accepted? → domain-only match!

# Variation 3: Subdomain
--data-urlencode "redirect_uri=https://evil.app.example.com/callback"
# Accepted? → subdomain wildcard!

# Variation 4: Different subdomain entirely
--data-urlencode "redirect_uri=https://evil.example.com/callback"
# Accepted? → domain wildcard (very loose)!

# Variation 5: Different port
--data-urlencode "redirect_uri=https://app.example.com:8080/callback"

# Variation 6: Different protocol
--data-urlencode "redirect_uri=http://app.example.com/callback"

# HOW TO KNOW IF IT WORKED:
# If redirect_uri accepted: auth server redirects to that URI
# In the location header after auth:
curl -s -D - "https://auth.example.com/oauth/authorize?..." 2>&1 | grep -i location
```

---

## Chained Attack: Wildcard + Subdomain Takeover

```
MOST POWERFUL COMBINATION:

SUBDOMAIN TAKEOVER:
  CNAME: dev.example.com → old-resource.s3.amazonaws.com
  Old S3 bucket: deleted (CNAME dangling)
  Attacker: creates S3 bucket with same name → controls dev.example.com!

COMBINED WITH WILDCARD REDIRECT:
  Registered: https://*.example.com/*
  → dev.example.com now controlled by attacker!
  
  Craft: redirect_uri=https://dev.example.com/steal
  Auth server accepts (wildcard)
  Victim clicks attacker's link → authenticates → code sent to dev.example.com
  → Attacker's server receives code!
  
FINDING SUBDOMAIN TAKEOVER CANDIDATES:
  # Check CNAMEs that point to unclaimed services:
  dig CNAME dev.example.com → points to some-bucket.s3.amazonaws.com
  curl https://some-bucket.s3.amazonaws.com → "NoSuchBucket" error
  → TAKEOVER POSSIBLE!
  
  Tools: subjack, can-i-take-over-xyz project
```

---

## Regex Bypass in Redirect URI Validation

```
COMMON REGEX MISTAKE:
  Developer writes: ^https://app\.example\.com/callback$
  
  Wait — dot (.) in domain not escaped!
  Actually matches: https://appXexample.com/callback
  Where X is ANY character (dot is "any char" in regex)
  
  ATTACK:
  Register domain: appaexample.com (or use existing)
  redirect_uri=https://appaexample.com/callback → passes regex!
  
  ANOTHER COMMON MISTAKE:
  Regex: /https:\/\/app\.example\.com\/.*/
  → Matches: https://app.example.com.evil.com/anything
  
  Because: regex matches if "app.example.com/" appears ANYWHERE in URL!
  Must anchor with ^ and $ AND be applied to the full URL
  
TESTING:
  If auth server uses regex, try:
  - appaexample.com (dot as any char)
  - app.example.com.evil.com (regex match without anchoring)
  - app.example.com@evil.com (URL parser vs regex disagreement)
```

---

## URL Parsing Discrepancies

```
ATTACK SURFACE: PARSER CONFUSION
  Auth server validates using one URL parser
  Browser navigates using browser's URL parser
  → If they disagree → bypass!
  
EXAMPLES:
  redirect_uri=https://app.example.com\@evil.com
  
  Some parsers: host = app.example.com, auth = no auth
  Others: host = evil.com, auth = app.example.com
  → Validated against example.com, but browser goes to evil.com!
  
  redirect_uri=https://app.example.com/callback#@evil.com
  → Fragment after # → some validators ignore → browser includes
  
  redirect_uri=https://app.example.com%2F@evil.com
  → %2F decoded as / → changes meaning after validation
```

---

## Fix

```
STRICT REDIRECT URI VALIDATION:

1. EXACT STRING MATCH (strongest):
   registered_uris = ["https://app.example.com/callback"]
   
   # Python:
   def validate_redirect_uri(requested_uri, registered_uris):
       # Normalize both URIs (lowercase scheme+host, decode %xx)
       normalized = normalize_uri(requested_uri)
       return normalized in [normalize_uri(u) for u in registered_uris]

2. NO WILDCARDS IN REGISTERED URIS:
   ✗ https://*.example.com/*
   ✓ https://app.example.com/oauth/callback  (exact path!)

3. MULTIPLE EXACT URIS FOR MULTIPLE ENVIRONMENTS:
   Register separately for dev, staging, prod:
   - https://localhost:3000/callback        (dev)
   - https://staging.example.com/callback  (staging)
   - https://app.example.com/callback      (production)

4. NORMALIZE BEFORE COMPARISON:
   Parse URL → extract scheme, host, port, path, query
   Normalize: lowercase scheme+host, resolve ../, URL decode
   Compare normalized form

5. REJECT MISMATCHES EXPLICITLY:
   Don't silently use registered URI when mismatch detected
   Log mismatch attempts as potential attacks

6. PERIODIC REVIEW:
   Audit registered redirect URIs for each client
   Remove old/unused URIs
   Flag wildcard registrations for immediate removal
```

---

## Related Notes
- [[07 - Redirect URI Manipulation]] — testing redirect_uri validation
- [[08 - Open Redirect in Redirect URI]] — combining with open redirects
- [[17 - OAuth Misconfig — Lack of State Validation]] — related misconfiguration
- [[20 - Defense Strict Redirect URI PKCE State Validation]] — full fix
