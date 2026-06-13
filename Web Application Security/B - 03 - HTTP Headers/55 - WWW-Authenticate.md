---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.55 WWW-Authenticate — Auth Challenge"
---

# 03.55 — WWW-Authenticate

## What is it?

`WWW-Authenticate` is a response header sent with a `401 Unauthorized` response that tells the client how to authenticate. It specifies the authentication scheme and challenge parameters. It reveals what authentication mechanisms the server supports and can leak information like realm names and authentication server URLs.

---

## Format

```
WWW-Authenticate: Basic realm="Admin Panel"
WWW-Authenticate: Bearer realm="API", error="invalid_token"
WWW-Authenticate: Digest realm="secure", nonce="abc123", algorithm=MD5
WWW-Authenticate: Negotiate   → Kerberos/NTLM
WWW-Authenticate: NTLM        → Windows NTLM challenge

MULTIPLE SCHEMES (server supports all):
  WWW-Authenticate: Basic realm="example"
  WWW-Authenticate: Bearer realm="api"
```

---

## Attack 1: Realm Information Leakage

```
WWW-Authenticate: Basic realm="Internal Admin Panel - Dev Env"

REVEALS:
  - Authentication type: Basic (base64, trivially reversible!)
  - Context: "Internal Admin Panel" → high-value target!
  - Environment: "Dev Env" → might have weaker security!

WWW-Authenticate: Bearer realm="https://auth.internal.corp/oauth/token"

REVEALS:
  - OAuth token endpoint: auth.internal.corp → internal hostname!
  - Can target OAuth server directly for SSRF or token theft!
```

---

## Attack 2: Basic Auth Brute Force

```
SEEING: WWW-Authenticate: Basic realm="Admin"

IMMEDIATE ATTACK — brute force Basic auth:
  hydra -l admin -P /usr/share/wordlists/rockyou.txt \
    target.com http-get /admin

  OR in Burp Intruder:
  Authorization: Basic <payload>
  Payload: base64(admin:FUZZ)

CREDENTIALS OVER HTTP:
  If Basic auth endpoint is on HTTP (not HTTPS):
  → Credentials transmitted in cleartext!
  → Any network observer can see them!
```

---

## Attack 3: NTLM Authentication Relay

```
SEEING: WWW-Authenticate: NTLM or Negotiate

ATTACK (internal network):
  1. Set up Responder to capture NTLM hashes:
     responder -I eth0
  
  2. Trick target into authenticating to attacker:
     → NTLM hash captured!
  
  3. Relay or crack:
     Crack: hashcat -m 5600 ntlm_hash.txt rockyou.txt
     Relay: ntlmrelayx.py -t target.com

ALSO:
  NTLM authentication reveals domain information in challenge!
  ntlmrecon to extract: NetBIOS name, DNS name, domain name, etc.
```

---

## Attack 4: OAuth Token Endpoint Discovery

```
WWW-Authenticate: Bearer realm="https://oauth.target.com", 
                  error="invalid_token",
                  error_description="Token has expired"

REVEALS:
  - OAuth endpoint: https://oauth.target.com
  - Token is expired (not invalid!) → try refresh token flow!
  - May be able to enumerate OAuth server directly!
```

---

## Testing

```bash
# Trigger 401 to see WWW-Authenticate:
curl -sI https://target.com/api/admin

# Look for realm and scheme:
curl -sI https://target.com/api | grep -i "www-authenticate"

# Brute force Basic auth:
hydra -L users.txt -P /usr/share/wordlists/rockyou.txt \
  -f target.com https-get /admin

# Test with curl:
curl -u admin:password https://target.com/admin
curl -u admin: https://target.com/admin  # empty password test

# Check for NTLM:
curl -sI https://target.com/api | grep -i "ntlm\|negotiate"
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Basic auth (reversible encoding) | Use modern auth (OAuth, JWT, session-based) |
| Realm reveals sensitive info | Use generic realm names |
| NTLM auth on web | Prefer modern auth; restrict NTLM to internal only |
| OAuth endpoint in WWW-Authenticate | Use error codes only, not full URLs |

---

## Related Notes
- [[18 - Authorization]] — Authorization request header
- [[02.13 - HTTP Authentication Schemes]] — all auth schemes
- [[Module 05 - Authentication Bypass]] — authentication attacks
