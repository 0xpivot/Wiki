---
tags: [vapt, authentication, intermediate]
difficulty: intermediate
module: "16 - Authentication"
topic: "16.10 Account Lockout Bypass"
portswigger_labs: ["Broken brute-force protection, IP block", "Broken brute-force protection, multiple credentials per request"]
---

# 16.10 — Account Lockout Bypass

## How Account Lockout Works

```
BASIC LOCKOUT:
  Failed attempt counter per account
  After N failures (e.g., 5) → account locked for T minutes
  
GOAL OF LOCKOUT:
  Prevent brute force by making it too slow to be practical
  
BYPASS GOAL:
  Reset the counter, change IP, or exploit implementation flaws
  to keep attempting without triggering the lockout
```

---

## Bypass Techniques

### 1. IP Address Rotation

```
MECHANISM:
  Some apps lock based on SOURCE IP, not account
  Or: IP-based rate limit separate from account lockout

BYPASS:
  Rotate IP address between requests
  - Rotate proxies (Burp → SOCKS proxy list)
  - Use X-Forwarded-For header spoofing (if app trusts it!)
  - TOR exit nodes (slow but anonymized)
  - Cloud IPs (AWS, GCP, Azure — rotate instances)

X-FORWARDED-FOR BYPASS:
  If server trusts X-Forwarded-For to identify "real IP":
  Add header with a fresh IP per request:
  
  Request 1: X-Forwarded-For: 1.1.1.1
  Request 2: X-Forwarded-For: 1.1.1.2
  Request 3: X-Forwarded-For: 1.1.1.3
  ...
  → Each request looks like a different client!
  
  BURP INTRUDER TRICK:
  Payload 1: §password§ = password list
  Payload 2: §xff§ = list of IPs
  Use "Pitchfork" to rotate both
  
  OR: Add X-Forwarded-For with unique IP per request using
  macros or Burp extension "IP Rotate"
```

### 2. Counter Reset via Successful Login

```
MECHANISM:
  Most implementations reset the failure counter on successful login!
  
BYPASS:
  Try: wrongpass1, wrongpass2, wrongpass3, wrongpass4
  Then: CORRECT OWN PASSWORD (resets counter!)
  Then: wrongpass5, wrongpass6, wrongpass7, wrongpass8
  Then: CORRECT OWN PASSWORD again
  ...
  
  Pattern: [N-1 guesses] [own correct password] repeat
  
  If lockout is at 5:
  4 wrong attempts → 1 correct (own account) → counter resets → 4 more wrong → ...
  
  IMPORTANT: This requires knowing OWN password
  Works if: Attacker is logged in (testing own lockout bypass)
            OR: App allows cross-account reset of counter somehow
```

### 3. Multiple Credentials Per Request

```
SOME APIs ACCEPT ARRAYS OF PASSWORDS:
  
  NORMAL:
  {"username": "admin", "password": "test"}
  
  ARRAY BYPASS:
  {"username": "admin", "password": ["password1","password2","password3",...,"password100"]}
  
  → Server may check ALL of them with a single failed counter increment!
  
  Test this by sending array syntax and see if:
  a) Server returns error about format
  b) Server accepts it and tries each
  c) Server treats it as a single (weird) password
  
  ALSO TEST:
  username as array: {"username": ["admin","administrator"], "password": "test"}
```

### 4. Case Sensitivity

```
IF LOCKOUT IS CASE-SENSITIVE ON USERNAME:
  admin locked? → try Admin, ADMIN, AdMiN
  → Different capitalization = different "account" in some systems
  
  Most apps normalize username to lowercase, but test it!
```

### 5. Null Byte Bypass

```
SOME OLDER SYSTEMS:
  Add null byte to username:
  admin%00
  admin%20 (URL-encoded space)
  
  → May be treated as different username by lockout mechanism
  → But same user by the actual auth check
```

---

## Testing Lockout Exists

```bash
# STEP 1: TEST IF LOCKOUT EXISTS:
for i in {1..20}; do
    code=$(curl -s -o /dev/null -w "%{http_code}" \
      -X POST https://target.com/login \
      -d "username=admin&password=wrongpass$i")
    echo "Attempt $i: HTTP $code"
done
# → After N attempts: response changes (403, redirect to lockout page, etc.)

# STEP 2: CHECK WHAT TRIGGERS LOCKOUT:
# Is it per-account? (lock admin → can still login as other user?)
# Is it per-IP? (same account from different IP works?)
# Is it per-session? (clear cookies to reset?)

# STEP 3: TEST RESET MECHANISM:
# Does the counter reset after T minutes? How long?
# Does it reset after a successful login?
```

---

## Fix

```
LAYERED DEFENSE (both are needed!):
  
  1. PER-ACCOUNT LOCKOUT:
     - Lock after 5-10 failed attempts
     - Progressive delay (exponential backoff)
     - Lockout for 15-30 min (NOT permanent — DoS risk!)
     
  2. RATE LIMITING BY IP:
     - Limit to N attempts per minute per IP
     - Can still be bypassed by IP rotation, but raises cost
     
  3. NEVER TRUST X-Forwarded-For FOR SECURITY DECISIONS:
     Only use it for logging, not for rate limit identity
     
  4. MFA:
     Even if lockout bypassed → second factor required
     
  5. CAPTCHA:
     After first few failures → require CAPTCHA
     → Automation defeated even without IP lockout
```

---

## Related Notes
- [[02 - Password Brute Force]] — what lockout defends against
- [[04 - Password Spraying]] — bypasses lockout by spreading across accounts
- [[28 - Defense Rate Limiting Lockout MFA]] — full defense guide
