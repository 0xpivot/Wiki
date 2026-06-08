---
tags: [vapt, oauth, intermediate]
difficulty: intermediate
module: "19 - OAuth"
topic: "19.10 Token Leakage via Referer Header"
portswigger_labs: ["OAuth token leakage via Referer header"]
---

# 19.10 — Token Leakage via Referer Header

## The Referer Header Problem

```
REFERER HEADER:
  Browser automatically sends this on navigation:
  
  GET /resource HTTP/1.1
  Host: analytics.google.com
  Referer: https://app.example.com/page?token=ACCESS_TOKEN
  
  → Third-party site receives whatever was in your URL!
  
  SENSITIVE DATA IN URL → DANGEROUS:
  - OAuth access tokens (Implicit flow puts them in fragment, 
    but some apps then put them in URL)
  - Authorization codes (before exchange)
  - API keys, session tokens in URL
  
  If page at URL-with-token loads ANY external resource:
  → That external resource receives token in Referer!
```

---

## Implicit Flow Token in URL Fragment

```
IMPLICIT FLOW RESPONSE:
  Auth server redirects to:
  https://app.example.com/callback#access_token=TOKEN&token_type=bearer
  
  FRAGMENT (#) NOT SENT TO SERVER:
  → Server's access log does NOT see the token (fragment never sent over HTTP)
  → But: browser has it in URL bar!
  
  HOWEVER:
  JavaScript reads it: location.hash
  → Then what does the JS do with it?
  
  BAD PATTERN:
  1. JS reads token from hash
  2. JS redirects to: /dashboard?token=ACCESS_TOKEN  ← puts token in query!
  3. Dashboard page loads → Referer sent to any 3rd party with token in URL!
  
  → LEAKAGE!
```

---

## Real Leakage Scenarios

```
SCENARIO 1: Token in callback URL + analytics
  Implicit flow: /callback#access_token=TOKEN
  App JS redirects to: /app?token=TOKEN
  App loads: <script src="https://analytics.example.com/a.js">
  → Referer: https://app.example.com/app?token=TOKEN → analytics server!

SCENARIO 2: Auth code in URL + external images
  Auth code flow: /callback?code=CODE
  Callback page renders HTML with: <img src="https://cdn.images.com/logo.png">
  → Referer: https://app.example.com/callback?code=CODE → CDN!
  → CDN operator can see the code in access logs

SCENARIO 3: API token in SPA page URL
  SPA: https://app.example.com/api-docs?key=API_KEY_HERE
  User clicks link to: https://docs.example.com/
  → Referer: https://app.example.com/api-docs?key=API_KEY_HERE

SCENARIO 4: Password reset token + support chat
  /reset?token=RESET_TOKEN
  User visits, then opens support chat (chat widget loads from support.example.com)
  → Referer: /reset?token=RESET_TOKEN → support company's servers!
```

---

## Testing for Referer Token Leakage

```bash
# STEP 1: Complete OAuth flow in Burp
# Enable logging for ALL traffic

# STEP 2: After you receive the callback URL with code/token:
# Watch ALL subsequent HTTP requests in Burp Proxy History

# STEP 3: Filter HTTP History:
# Look for any request to EXTERNAL domains
# Check Referer header on each external request

# STEP 4: Look for pattern:
# Request to: analytics.example.com, cdn.example.com, etc.
# Referer: https://app.example.com/callback?code=... 
# → BUG!

# MANUALLY TEST:
# After completing OAuth:
# 1. Copy the callback URL (with code)
# 2. Check what external resources the callback page loads
# 3. Would those receive the code in Referer?

# CHECK REFERRER POLICY:
curl -s -I https://app.example.com/callback | grep -i "referrer-policy"
# Nothing? → Default browser behavior (sends full URL to same-origin,
#             origin to cross-origin in modern browsers)
# → If "no-referrer" or "strict-origin" → good!
# → If "unsafe-url" → ALL external requests get full URL!
```

---

## Referer Policy Deep Dive

```
REFERRER-POLICY HEADER VALUES:
  no-referrer            → Never send Referer (safest!)
  strict-origin          → Only send origin (not path/query) cross-origin
  strict-origin-when-cross-origin → Full URL same-origin, origin only cross-origin
  same-origin            → Only send Referer to same origin
  origin                 → Send only origin (never path/query)
  no-referrer-when-downgrade → Default: full URL same-origin, origin cross-origin, nothing HTTP
  unsafe-url             → Always send full URL including path+query (WORST!)

FOR OAUTH CALLBACKS:
  ✓ Best: no-referrer
  ✓ Good: strict-origin or strict-origin-when-cross-origin
  ✗ Bad: unsafe-url, no-referrer-when-downgrade with mixed content
  ✗ Missing: browser defaults may still send origin to cross-origin
  
  Add to callback page response:
  Referrer-Policy: no-referrer
```

---

## Fix

```
MULTI-LAYERED DEFENSE:

1. DON'T PUT TOKENS IN URL QUERY PARAMETERS:
   BAD:  /callback?token=ACCESS_TOKEN
   GOOD: Token in response body, then store in memory or HttpOnly cookie
   
2. REMOVE SENSITIVE PARAMS FROM URL IMMEDIATELY:
   After extracting code/token, redirect to clean URL:
   Python:
   @app.route('/callback')
   def callback():
       code = request.args.get('code')
       # ... exchange code for token ...
       session['access_token'] = token
       return redirect('/dashboard')  # ← no token in URL!
   
3. SET REFERRER POLICY ON SENSITIVE PAGES:
   # All responses that might have sensitive URL params:
   response.headers['Referrer-Policy'] = 'no-referrer'
   
   # Or in nginx:
   add_header Referrer-Policy "no-referrer" always;
   
   # Or in HTML meta tag:
   <meta name="referrer" content="no-referrer">

4. MINIMIZE THIRD-PARTY RESOURCES ON SENSITIVE PAGES:
   Don't load analytics/tracking scripts on:
   - OAuth callback pages
   - Password reset pages
   - Any page that might have tokens in URL
   
5. FOR IMPLICIT FLOW: MIGRATE TO PKCE
   Fragment tokens never hit server, but still visible in URL bar
   Better: auth code flow with PKCE, token never in URL
   
6. SUBRESOURCE INTEGRITY + EXTERNAL SCRIPT AUDIT:
   Know every external domain your pages load from
   Any of those can be a token leakage channel via Referer
```

---

## Related Notes
- [[03 - Implicit Flow Vulnerabilities]] — tokens in URL fragment
- [[09 - Authorization Code Interception]] — code leakage in general
- [[11 - Token Leakage via Browser History]] — another URL-based leakage
- [[20 - Defense Strict Redirect URI PKCE State Validation]] — full fix
