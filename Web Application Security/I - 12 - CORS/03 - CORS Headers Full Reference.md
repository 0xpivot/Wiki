---
tags: [vapt, cors, beginner]
difficulty: beginner
module: "12 - CORS"
topic: "12.03 CORS Headers — Full Reference"
---

# 12.03 — CORS Headers: Full Reference

## Request Headers (Browser → Server)

### Origin
```http
Origin: https://app.example.com

PURPOSE: Identifies where the request comes from
WHEN SENT: ALL cross-origin requests + same-site requests with credentials
NOTE: Browser sets this — cannot be spoofed by JavaScript
      (curl/Postman CAN spoof it — CORS is browser enforcement only!)
MISSING WHEN: Same-origin requests (browser omits it)
              Programmatic requests in some edge cases
```

### Access-Control-Request-Method (Preflight only)
```http
Access-Control-Request-Method: DELETE

PURPOSE: Asks "will you allow this method?"
WHEN SENT: Only in preflight OPTIONS request
EXAMPLE: JS does fetch('/data', {method: 'DELETE'})
         → Browser preflights with ACRM: DELETE first
```

### Access-Control-Request-Headers (Preflight only)
```http
Access-Control-Request-Headers: Authorization, Content-Type, X-Custom-Header

PURPOSE: Asks "will you allow these headers?"
WHEN SENT: Only in preflight OPTIONS request
NOTE: Lowercase, comma-separated
```

---

## Response Headers (Server → Browser)

### Access-Control-Allow-Origin (ACAO)
```http
# Specific origin:
Access-Control-Allow-Origin: https://app.example.com

# Wildcard (no credentials!):
Access-Control-Allow-Origin: *

# null:
Access-Control-Allow-Origin: null

PURPOSE: Tells browser which origins can read this response
RULES:
  - Only ONE value allowed (not a list!)
  - If allowing multiple origins: reflect dynamically based on Origin header
  - * cannot be used with Access-Control-Allow-Credentials: true
  
SECURE PATTERN:
  const allowedOrigins = ['https://app.example.com', 'https://admin.example.com'];
  if (allowedOrigins.includes(request.headers.origin)) {
    response.setHeader('Access-Control-Allow-Origin', request.headers.origin);
  }

INSECURE PATTERN (reflected blindly):
  response.setHeader('Access-Control-Allow-Origin', request.headers.origin);
  // ANY origin gets access!
```

### Access-Control-Allow-Credentials (ACAC)
```http
Access-Control-Allow-Credentials: true

PURPOSE: Allows cookies, HTTP auth, and TLS client certificates in response
RULES:
  - If true: ACAO cannot be * (browsers reject the combination)
  - If true: frontend fetch must use: credentials: 'include'
  - If false or absent: cookies not sent, JS can't read credentialed data

SECURITY NOTE:
  ACAO: * + ACAC: true = browser rejects (but check with null origin!)
  ACAO: reflected-origin + ACAC: true = CRITICAL VULNERABILITY!
```

### Access-Control-Allow-Methods
```http
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS

PURPOSE: In preflight response — which methods are allowed
DEFAULT: Only simple methods (GET, POST, HEAD) if not specified
NOTE: Wildcard * allowed here in Chrome 97+ (not all browsers)
```

### Access-Control-Allow-Headers
```http
Access-Control-Allow-Headers: Authorization, Content-Type, X-Requested-With

PURPOSE: In preflight response — which request headers are allowed
DEFAULT: Only safe headers if not specified
WILDCARD: Access-Control-Allow-Headers: * (allowed in some browsers)
```

### Access-Control-Expose-Headers
```http
Access-Control-Expose-Headers: X-Custom-Header, X-Request-ID

PURPOSE: Which RESPONSE headers JS can access
DEFAULT: Only "safe" headers: Cache-Control, Content-Language, 
         Content-Length, Content-Type, Expires, Last-Modified, Pragma
NOTE: Custom headers in response are hidden from JS unless listed here
```

### Access-Control-Max-Age
```http
Access-Control-Max-Age: 86400

PURPOSE: Cache preflight response for this many seconds
BENEFIT: Avoids repeated preflight OPTIONS requests
LIMITS: Chrome max = 7200, Firefox max = 86400
```

---

## Complete Header Interaction Table

```
SCENARIO                                ATTACK POSSIBLE?
─────────────────────────────────────────────────────────────────
ACAO: * + no ACAC                       No (no creds in req/res)
ACAO: * + ACAC: true                    No (browser rejects!)
ACAO: reflected + no ACAC              Limited (no creds readable)
ACAO: reflected + ACAC: true            YES → CRITICAL!
ACAO: null + ACAC: true                 YES via sandboxed iframe!
ACAO: specific-origin + ACAC: true      Only if that origin is compromised
ACAO: *.trusted.com + ACAC: true        YES if subdomain taken over!
No CORS headers at all                  No (JS can't read response)
```

---

## Quick Reference: Safe vs Unsafe Patterns

```http
# SAFE: Specific whitelist + credentials
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Credentials: true
Vary: Origin

# SAFE: Public API, no credentials
Access-Control-Allow-Origin: *

# UNSAFE: Reflected origin + credentials
Access-Control-Allow-Origin: [whatever Origin header said]
Access-Control-Allow-Credentials: true

# UNSAFE: Null + credentials
Access-Control-Allow-Origin: null
Access-Control-Allow-Credentials: true

# IMPORTANT: Always include Vary: Origin when dynamically setting ACAO
# This prevents caching issues when different origins get different ACAO values
```

---

## Related Notes
- [[01 - What is CORS and Why It Exists]] — CORS overview
- [[02 - Simple vs Preflight Requests]] — when headers apply
- [[04 - Origin Reflection Misconfiguration]] — exploiting reflected ACAO
- [[05 - Null Origin Misconfiguration]] — exploiting null ACAO
