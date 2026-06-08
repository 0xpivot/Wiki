---
tags: [vapt, oauth, intermediate]
difficulty: intermediate
module: "19 - OAuth"
topic: "19.12 Account Linking Abuse"
portswigger_labs: ["Forced OAuth profile linking"]
---

# 19.12 — Account Linking Abuse

## What Is Account Linking?

```
ACCOUNT LINKING:
  Users can connect external OAuth provider to existing account
  
  EXAMPLE:
  You have: username/password account at shop.example.com
  You want: to also sign in with Google
  
  You go: Settings → "Link Google Account"
  → OAuth flow → Google auth → Google linked!
  → Now you can log in via Google OR username/password
  
  MULTIPLE PROVIDERS COMMON:
  "Link Google", "Link Facebook", "Link GitHub", "Link Apple"
  
  WHY DANGEROUS:
  Account linking changes who can authenticate to your account!
  If attacker can link their identity → they own your account!
```

---

## Attack 1: CSRF on Account Linking

```
PREREQUISITE: No state parameter validation on OAuth callback

ATTACK FLOW:
  1. Attacker creates own account at shop.example.com
  2. Attacker starts "Link Google" flow with their OWN Google account
  3. Attacker gets callback URL (but doesn't complete it):
     https://shop.example.com/oauth/link-callback?code=ATTACKER_CODE&state=...
  
  4. Attacker crafts CSRF page:
     <img src="https://shop.example.com/oauth/link-callback?code=ATTACKER_CODE">
     OR:
     <form action="https://shop.example.com/oauth/link-callback" ...>
  
  5. Attacker sends CSRF page to VICTIM (who is logged in)
  
  6. Victim's browser makes request to callback → victim is authenticated
     → App links ATTACKER'S Google to VICTIM'S account!
  
  7. Attacker logs in via their Google account → now in VICTIM'S account!
  
RESULT:
  - Victim's account fully compromised
  - Attacker can access even after victim changes password
  - Attacker can remove victim's Google link (or add their own password)
  
TESTING:
  1. Find account linking flow
  2. Complete OAuth up to getting callback URL with code
  3. Test if state parameter is validated (try removing it → does it still link?)
  4. If no state validation → CSRF account takeover possible!
```

---

## Attack 2: Pre-linking Before Account Creation

```
RACE: OAUTH LINK BEFORE ACCOUNT EXISTS

SOME APPS ALLOW:
  OAuth linking before the account fully exists
  OR: App creates account at first OAuth login
  
ATTACK:
  Target: victim@gmail.com has account at target app
  
  1. Attacker finds: app creates account based on OAuth provider's email
  2. Attacker also has: victim@gmail.com access? No, but...
  
  DIFFERENT SCENARIO:
  App allows "login or create account" via OAuth
  App links based on email match: OAuth email == registered email
  
  If attacker controls OAuth provider (custom OAuth server):
  They can issue tokens claiming email=victim@gmail.com
  → App matches existing account → attacker in victim's account!
  
  COMMON IN:
  Apps that trust "email_verified: false" claims
  Apps using custom/legacy OAuth providers
  Apps that merge accounts based on email without verification
```

---

## Attack 3: Sub vs Email for Account Linking

```
THE SUB CLAIM:
  OAuth providers issue a "sub" (subject) claim:
  Unique, permanent identifier for the user within that provider
  
  Google user ID: 10769150350006150715113082367
  → This number doesn't change, even if email changes
  
BAD PRACTICE — Linking by email:
  App looks up account by OAuth provider's "email" claim
  User changes Google email → App now links to wrong account!
  OR: User deletes Google, new user gets same email → auto-link!
  
GOOD PRACTICE — Link by provider sub:
  Store: oauth_links table { provider, provider_user_id (sub), app_user_id }
  → "google", "10769150350006150715113082367", → user #42
  
TESTING FOR SUB LINKAGE WEAKNESS:
  1. Link Google account → observe what's stored (sub or email?)
  2. If email-based: can changing Google email cause account confusion?
  3. If email_verified claim trusted: can unverified email cause link?
```

---

## Attack 4: Unlinking and Lockout Abuse

```
ACCOUNT LOCKOUT VIA UNLINKING:
  If app lets users unlink ALL OAuth providers and has no password:
  → Victim can be forced to lose ALL authentication methods
  
  (Less common, but worth testing)
  
UNLINKING CSRF:
  If unlinking doesn't have CSRF protection:
  → Attacker CSRFs victim into unlinking their Google account
  → Victim locked out if Google was only auth method!
  
  POST /settings/unlink-google HTTP/1.1
  (No CSRF token? → Test with CSRF attack)
```

---

## Testing Account Linking

```bash
# STEP 1: Find account linking flows:
# Look in: Settings, Profile, Security, Connected Apps pages
# Look for: "Link with Google/Facebook/GitHub", "Connected Accounts"
# Look for OAuth flows initiated from within authenticated session

# STEP 2: Start linking flow, capture callback URL in Burp:
# Note: code= and state= parameters in callback

# STEP 3: Test state validation (same as 19.06 testing):
# Try callback without state → does linking proceed?
# Try callback with wrong state → does linking proceed?

# STEP 4: Try to CSRF the linking (if state missing/weak):
# Craft HTML page:
# <img src="CALLBACK_URL?code=YOUR_CODE">
# Test in different browser session (simulating victim)
# → Did your identity get linked to the victim account?

# STEP 5: Test email-based linking:
# Create account with email A
# Link OAuth provider that claims email B
# → What happens? Does it link to email B's account?

# STEP 6: Check email_verified enforcement:
# If using custom OAuth provider in a lab:
# Issue token with email_verified=false → does app still link?
```

---

## Fix

```
SECURE ACCOUNT LINKING IMPLEMENTATION:

1. ALWAYS VALIDATE STATE PARAMETER:
   Essential for linking flows (CSRF here = account takeover!)
   state = cryptographically random, session-bound, single-use

2. REQUIRE ACTIVE SESSION FOR LINKING:
   User must be logged in to initiate linking
   Callback must verify the session is authenticated
   
3. CONFIRM BEFORE LINKING:
   "You're about to link your Google account to this profile. Continue?"
   → CSRF attacker can't bypass a confirmation that requires user action
   → Even better: require password confirmation for linking

4. LINK BY PROVIDER SUB, NOT EMAIL:
   oauth_links: { provider: "google", sub: "10769...", user_id: 42 }
   → Not affected by email changes
   → Not affected by email reuse across providers

5. REQUIRE email_verified=true:
   Only link if OAuth provider confirms email is verified
   if not id_token.email_verified:
       return error("Email not verified with OAuth provider")

6. PROTECT UNLINKING WITH CSRF TOKEN + CONFIRMATION:
   Ensure user can't accidentally or be CSRFed into unlinking

7. NOTIFY USER ON LINKING:
   Email: "A new Google account was linked to your profile"
   → Victim sees alert if attacker linked their identity
   → User can investigate and unlink
```

---

## Related Notes
- [[06 - OAuth State Parameter — CSRF in OAuth]] — state validation
- [[18 - OAuth to Account Takeover Chain]] — full ATO chain
- [[19.06 - OAuth Login CSRF]] — login-specific OAuth CSRF
- [[20 - Defense Strict Redirect URI PKCE State Validation]] — full fix
