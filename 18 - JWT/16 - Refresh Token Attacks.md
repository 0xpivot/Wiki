---
tags: [vapt, jwt, intermediate]
difficulty: intermediate
module: "18 - JWT"
topic: "18.16 Refresh Token Attacks"
---

# 18.16 — Refresh Token Attacks

## Access Token vs Refresh Token

```
TOKEN PAIR SYSTEM:
  Access Token:   Short-lived (5-15 min), used for API requests
  Refresh Token:  Long-lived (days/months), used ONLY to get new access tokens
  
FLOW:
  1. Login → server returns: access_token + refresh_token
  2. Use access_token for API calls
  3. Access token expires (15 min) → use refresh_token to get new access_token
  4. GET /auth/refresh → send refresh_token → get new access_token
  5. Repeat until refresh_token expires (logout or max lifetime)
  
WHY THIS DESIGN?
  Access token stolen → expires in 15 min → low impact
  Refresh token stolen → long-lived → MUCH higher impact
  → Keep refresh token very secure (HttpOnly cookie, not in memory)
```

---

## Refresh Token Vulnerabilities

### 1. Refresh Token Not Single-Use

```
SECURE: Each use of refresh token → NEW refresh token issued, old invalidated
  → "Rotation" — if attacker steals refresh token and uses it,
    victim's next refresh attempt fails (old token invalid)
    → Victim notices, can alert/re-login
    
VULNERABLE: Same refresh token can be used many times
  → Attacker steals refresh token
  → Silently generates new access tokens forever
  → Victim never knows!

TEST:
  1. Get refresh token from login response
  2. Use it: POST /auth/refresh → get new access token (refresh_token unchanged)
  3. Use same refresh token again
  → If you get another new access token → NOT single-use!
  → Attacker can silently maintain access indefinitely
```

### 2. Refresh Token Not Invalidated on Logout

```
TEST:
  1. Login → save refresh_token
  2. Logout (normal logout)
  3. Try to use the saved refresh_token:
     POST /auth/refresh { "refresh_token": "SAVED_TOKEN" }
  → If you get a new access_token → refresh not invalidated on logout!
  → Attacker who stole refresh_token → persists through user's logout!
```

### 3. Refresh Token Reuse Detection Bypass

```
SECURE SYSTEMS:
  If refresh token T1 is used → T2 issued, T1 invalidated
  If attacker tries T1 again → detected as TOKEN REUSE → invalidate ALL refresh tokens!
  → Both victim and attacker are logged out → forced re-login → victim notices!
  
BYPASS ATTEMPT:
  Race condition: Use T1 twice simultaneously before invalidation processes
  → Both requests succeed → two valid T2 tokens! (duplicate session)
  
TEST:
  1. Get refresh token
  2. Send two simultaneous requests using same refresh token:
     curl POST /auth/refresh (T1) &
     curl POST /auth/refresh (T1) &
  3. Do both succeed? → Race condition in refresh token rotation!
```

### 4. Refresh Token in Insecure Location

```
RISK: Refresh token stored in localStorage
  → XSS steals refresh_token → attacker has long-lived access
  → Even after access token expires, attacker refreshes indefinitely
  
  WORSE than stealing access token (which expires in 15 min)
  
TEST:
  Check localStorage: localStorage.getItem('refresh_token')
  If present → HIGH RISK!
  
SECURE: Refresh token in HttpOnly cookie
  → XSS cannot steal it
  → Only browser automatically sends on refresh endpoint
```

---

## Attack: Persistent Access via Stolen Refresh Token

```
SCENARIO:
  Attacker finds XSS → steals refresh_token from localStorage
  
  Access token expired? No problem:
  POST /auth/refresh
  Body: { "refresh_token": "STOLEN_REFRESH_TOKEN" }
  
  → New access_token returned!
  → Attacker continues accessing API indefinitely
  
PERSISTENCE SCRIPT:
  while True:
      resp = requests.post('https://target.com/auth/refresh',
          json={'refresh_token': STOLEN_REFRESH_TOKEN})
      access_token = resp.json()['access_token']
      
      # Use access_token for malicious actions
      do_evil_things(access_token)
      
      time.sleep(14 * 60)  # refresh every 14 minutes (before 15-min expiry)
```

---

## Fix

```
REFRESH TOKEN SECURITY:

  ✓ Single-use (Rotation):
    Each /refresh call → new refresh token + new access token
    Old refresh token immediately invalidated
    
  ✓ Reuse detection → invalidate ALL tokens:
    If old (already used) refresh token presented → security event!
    Invalidate entire refresh token family (all tokens for this login session)
    
  ✓ Short-ish lifetime:
    Refresh tokens: 24 hours for high-security, 30 days for normal apps
    Not indefinite!
    
  ✓ Store refresh tokens in HttpOnly cookie:
    Not localStorage! 
    Cookie: refresh_token=TOKEN; HttpOnly; Secure; SameSite=Strict; Path=/auth/refresh
    
  ✓ Bind refresh token to client:
    IP address binding (controversial) or device fingerprint
    → Token stolen and used from different IP → invalidated!
    
  ✓ Invalidate all refresh tokens on:
    - Logout
    - Password change
    - Email change
    - Suspicious activity detected
```

---

## Related Notes
- [[10 - JWT Expiry Manipulation]] — access token expiry
- [[11 - JWT Replay Attack]] — token reuse concepts
- [[13 - JWT in Cookies vs Authorization Header]] — secure token storage
- [[18 - Defense Strong Algorithms Validation Short Expiry]] — full defense
