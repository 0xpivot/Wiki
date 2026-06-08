---
tags: [vapt, oauth, beginner]
difficulty: beginner
module: "19 - OAuth"
topic: "19.11 Token Leakage via Browser History"
---

# 19.11 — Token Leakage via Browser History

## The Problem

```
BROWSER HISTORY SAVES EVERY URL VISITED:
  URL with OAuth token:
  https://app.example.com/callback?token=ACCESS_TOKEN
  
  → Saved in browser history
  → Persists even after user navigates away
  
  WHO CAN ACCESS:
  - Another user on shared computer (library, office)
  - Someone who has brief physical access to device
  - Malware reading browser history files
  - Browser sync compromise (history synced to cloud account)
  - Browser extensions with "history" permission
  - Domestic abuse / shoulder surfing
```

---

## Implicit Flow and History

```
IMPLICIT FLOW RETURNS TOKEN IN FRAGMENT:
  https://app.example.com/callback#access_token=TOKEN
  
  Fragment (#) IS included in browser history!
  Even though it's not sent to the server:
  → The full URL including fragment is in browser history
  
  TEST:
  1. Complete Implicit flow OAuth
  2. Open browser history
  3. Find the callback URL with #access_token=...
  → Token accessible from history!
  
EVEN WORSE IF APP COPIES TOKEN TO QUERY:
  Some apps do: window.history.replaceState() or redirect with token in query
  → Token now in BOTH fragment history AND query string history
```

---

## What Attackers Can Do with Historical Tokens

```
TOKEN FROM HISTORY → STILL VALID?

ACCESS TOKENS:
  Short-lived (typically 1 hour)
  → Old token from history might be expired → useless
  → BUT if token still valid → full API access!
  
HOW TO TEST:
  1. Find token in browser history URL
  2. Try using it:
  curl -H "Authorization: Bearer OLD_TOKEN" https://api.example.com/user
  → 401 = expired (good)
  → 200 = still valid (potential issue depending on age)
  
AUTH CODES:
  Short-lived (often 60 seconds to 10 minutes)
  → Usually expired by the time attacker accesses history
  → But: test if they can be used multiple times (should fail on 2nd use)
  
RESET TOKENS IN URL:
  Password reset: /reset?token=RESET_TOKEN
  These may be longer-lived (24h often)
  → Historical reset token still valid → account takeover!
```

---

## Testing

```bash
# MANUAL TEST — Check if sensitive tokens appear in URLs:
# 1. Complete OAuth flow
# 2. Open browser History (Ctrl+H in Chrome)
# 3. Find callback URL
# 4. Check if: token, code, or other sensitive params in URL

# CHECK IMPLICIT FLOW SPECIFICALLY:
# Is response_type=token used?
# After callback, is the fragment with token in history?

# CHECK FOR HISTORY-CLEANING:
# Does the app use window.history.replaceState() to clean URL?
# After landing on callback page, what URL is shown in bar?
# Is token removed?

# AUTOMATED CHECK:
# Read browser history file directly (if you have access for testing):
# Chrome Linux: ~/.config/google-chrome/Default/History (SQLite)
sqlite3 ~/.config/google-chrome/Default/History \
  "SELECT url FROM urls WHERE url LIKE '%callback%' OR url LIKE '%token%'"

# Firefox Linux: ~/.mozilla/firefox/PROFILE/places.sqlite
sqlite3 ~/.mozilla/firefox/PROFILE/places.sqlite \
  "SELECT url FROM moz_places WHERE url LIKE '%callback%'"
```

---

## URL Cleaning Technique

```javascript
// CLEAN UP SENSITIVE PARAMS FROM HISTORY:

// Option 1: replaceState (removes current URL from history entry, replaces cleanly)
// After reading token from URL:
const token = new URLSearchParams(window.location.hash.substring(1)).get('access_token');
// Store token in memory:
let accessToken = token;
// Clean URL:
window.history.replaceState({}, document.title, '/dashboard');
// → URL in bar is now clean, and the old fragment URL is REPLACED in history!

// Option 2: Redirect (server-side) after consuming code:
// Flask:
@app.route('/callback')
def callback():
    code = request.args.get('code')
    state = request.args.get('state')
    # validate state, exchange code
    session['token'] = token
    return redirect('/dashboard')  # ← replaces callback URL in history for server-rendered

// NOTE: Server-side redirect (302) creates TWO history entries:
//  1. /callback?code=...  (the callback, with code)
//  2. /dashboard          (the clean redirect target)
// → Code is still in history!
// → Better: use History API on client side to clean up
```

---

## Fix

```
DEFENSE AGAINST BROWSER HISTORY LEAKAGE:

1. DON'T USE IMPLICIT FLOW:
   → Tokens never go in URL → no history risk from tokens
   → Use Auth Code + PKCE instead
   
2. CLEAN URL IMMEDIATELY AFTER CONSUMING TOKEN:
   Client side (for SPAs handling fragments):
   window.history.replaceState({}, '', '/app');
   → Replaces the fragment URL with clean URL in history
   
3. SHORT TOKEN LIFETIME:
   → Even if stolen from history, expires quickly
   → Access tokens: 1 hour max
   → Auth codes: 10 minutes max, single-use
   
4. TOKEN BINDING (advanced):
   → Bind tokens to specific client (mTLS or DPoP)
   → Even if token stolen → unusable without the bound key
   → RFC 9449 (DPoP — Demonstration of Proof-of-Possession)
   
5. INSTRUCT USERS:
   → "Always log out on shared computers"
   → "Clear browsing data after use"
   (This doesn't fix the bug but reduces real-world impact)
   
6. SESSION-BASED APPROACH FOR SENSITIVE APPS:
   → Server sets HttpOnly cookie after OAuth
   → No token ever appears in URL at all
   → Zero history leakage risk
```

---

## Related Notes
- [[03 - Implicit Flow Vulnerabilities]] — token-in-URL root cause
- [[10 - Token Leakage via Referer Header]] — Referer-based leakage
- [[09 - Authorization Code Interception]] — code-related history leakage
- [[20 - Defense Strict Redirect URI PKCE State Validation]] — full fix
