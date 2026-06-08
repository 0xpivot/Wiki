---
tags: [vapt, oauth, intermediate]
difficulty: intermediate
module: "19 - OAuth"
topic: "19.14 Token Replay Attack"
---

# 19.14 — Token Replay Attack

## What Is a Token Replay Attack?

```
TOKEN REPLAY:
  Tokens are bearer credentials — like cash:
  "Whoever holds it, can spend it"
  
  If attacker obtains a valid token:
  → Use it over and over until it expires
  → Impersonates the legitimate user
  
  "Replaying" = using the same token multiple times, possibly after theft
  
UNLIKE TRADITIONAL SESSIONS:
  Sessions: Server can invalidate server-side at any time
  JWT/OAuth tokens: Stateless — server can't track individual tokens
  → Once issued, token is valid until expiry
  → No built-in revocation (without extra infrastructure)
```

---

## Token Theft Scenarios for Replay

```
WHERE TOKENS ARE STOLEN:
  1. XSS — script reads localStorage / session storage
  2. Log file exposure — token in access logs
  3. Referer header — see note 10
  4. Browser history — see note 11
  5. Insecure storage — file system, hardcoded
  6. Man-in-the-middle — HTTP (not HTTPS), SSL stripping
  7. Network sniffing — open WiFi
  
ONCE STOLEN:
  Attacker uses:
  curl -H "Authorization: Bearer STOLEN_TOKEN" https://api.example.com/user
  → Full access until token expires!
  
DURATION OF RISK:
  1-hour token: 1 hour of access after theft
  24-hour token: 24 hours
  No expiry: Permanent access!
```

---

## Testing for Replay Issues

```bash
# TEST 1: CAN TOKEN BE REUSED INDEFINITELY?
# Use the access token multiple times:
for i in {1..5}; do
  curl -s -H "Authorization: Bearer ACCESS_TOKEN" https://api.example.com/user
  echo "---"
done
# → All 5 return 200? Normal (tokens are typically multi-use)
# → But: how long does it stay valid?

# TEST 2: IS THE TOKEN SHORT-LIVED ENOUGH?
# Note the issued-at time (iat) and expiry (exp) in the JWT:
python3 -c "
import base64, json
token = 'ACCESS_TOKEN'
payload = token.split('.')[1]
payload += '=' * (4 - len(payload) % 4)
data = json.loads(base64.b64decode(payload))
import datetime
print('Issued:', datetime.datetime.fromtimestamp(data['iat']))
print('Expires:', datetime.datetime.fromtimestamp(data['exp']))
print('Lifetime:', data['exp'] - data['iat'], 'seconds')
"
# → More than 3600 seconds (1 hour) → long-lived, note this

# TEST 3: IS TOKEN VALID AFTER LOGOUT?
# 1. Get token, log out
# 2. Use saved token:
curl -H "Authorization: Bearer TOKEN_FROM_BEFORE_LOGOUT" https://api.example.com/user
# → 200? Token not invalidated on logout → BUG!

# TEST 4: IS TOKEN VALID AFTER PASSWORD CHANGE?
# 1. Get token, change password
# 2. Use old token:
curl -H "Authorization: Bearer OLD_TOKEN" https://api.example.com/user
# → 200? Token persists through password change → BUG!

# TEST 5: IS TOKEN VALID AFTER ROLE CHANGE?
# 1. Get token as regular user
# 2. Admin revokes your access / changes your role
# 3. Use old token:
curl -H "Authorization: Bearer OLD_TOKEN" https://api.example.com/admin
# → Still admin access? Token not reflecting current role → BUG!
```

---

## Stateless Tokens and Revocation Problem

```
THE FUNDAMENTAL TENSION:
  Stateless JWT benefit: No database lookup per request → fast!
  Stateless JWT problem: Can't revoke without state!
  
  "There's no such thing as a revocable stateless token"
  
COMMON WORKAROUNDS:

  1. SHORT EXPIRY (simplest):
     1-hour tokens → stolen token usable for max 1 hour
     Trade-off: users re-authenticate more often
     
  2. TOKEN BLOCKLIST (selective revocation):
     On logout: add jti (JWT ID) to Redis blocklist
     On each request: check if jti is in blocklist
     Trade-off: Now you have state! → defeats "stateless" benefit
     But: only store tokens that need revocation (small set)
     
  3. REFRESH TOKEN ROTATION:
     Short-lived access tokens (15 min)
     Long-lived refresh tokens (single-use, rotate on each use)
     On logout: invalidate refresh token → user can't renew
     Trade-off: Access token still valid for 15 min after logout
     
  4. TOKEN BINDING (future-proof but complex):
     Token bound to client certificate or key → can't be replayed elsewhere
     DPoP (RFC 9449) adds proof-of-possession
```

---

## Real-World Impact Examples

```
SCENARIO 1: API Key in Test Script
  Developer tests API: stores token in test.sh
  Token has no expiry
  test.sh committed to GitHub
  Attacker finds it → permanent API access

SCENARIO 2: Leaked Token from Log
  Access log: GET /callback?token=eyJ... → exported to analytics
  Analytics team sees token
  Token valid for 24 hours → access window

SCENARIO 3: Post-Logout Token
  Employee quits, logs out of company app
  OAuth access token still valid for 60 min
  Ex-employee uses saved token → accesses company data
  
SCENARIO 4: Mobile App Token Theft via Backup
  Android backup enabled: copies app data including stored token
  Backup restored on attacker's device
  Token works → account accessed
```

---

## Fix

```
DEFENSE IN DEPTH AGAINST TOKEN REPLAY:

1. SHORT ACCESS TOKEN LIFETIME:
   # Recommended: 15-60 minutes max
   # PyJWT:
   payload = {
       'sub': user.id,
       'iat': int(time.time()),
       'exp': int(time.time()) + 3600,  # 1 hour max
   }

2. TOKEN REVOCATION LIST (for logout/critical events):
   # Redis-based blocklist:
   import redis
   r = redis.Redis()
   
   # On logout:
   def logout(token_jti, token_exp):
       ttl = token_exp - int(time.time())  # expire from blocklist when token expires
       r.setex(f"blocklist:{token_jti}", ttl, "1")
   
   # On each request:
   def verify_token(token):
       payload = decode_jwt(token)
       if r.exists(f"blocklist:{payload['jti']}"):
           raise Exception("Token revoked!")
       return payload

3. INVALIDATE ON SECURITY EVENTS:
   - Password change → invalidate all tokens
   - Role change → invalidate all tokens (or use short expiry so it auto-refreshes)
   - Account locked → blocklist all active tokens

4. JTI (JWT ID) FOR ALL TOKENS:
   # Each token gets unique ID:
   import uuid
   payload['jti'] = str(uuid.uuid4())

5. HTTPS EVERYWHERE:
   → Prevents network-level token theft

6. SECURE STORAGE:
   → Never in localStorage (XSS risk)
   → Memory (most secure, lost on tab close)
   → HttpOnly Secure cookie (immune to XSS reads)
```

---

## Related Notes
- [[18 - JWT — Refresh Token Attacks]] — refresh token replay
- [[16 - Refresh Token Attacks]] — refresh token specific
- [[10 - Token Leakage via Referer Header]] — how tokens are stolen
- [[20 - Defense Strict Redirect URI PKCE State Validation]] — full fix
