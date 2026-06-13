---
tags: [vapt, cors, defense, beginner]
difficulty: beginner
module: "12 - CORS"
topic: "12.12 Defense — Strict Origin Whitelisting"
---

# 12.12 — Defense: Strict Origin Whitelisting

## The Core Rule

```
NEVER:
  ✗ Reflect the Origin header blindly
  ✗ Trust: null origin (for credentialed requests)
  ✗ Use weak regex (endsWith, includes, without anchors)
  ✗ Use Access-Control-Allow-Origin: * with credentials
  ✗ Trust HTTP subdomains from an HTTPS site
  ✗ Trust all subdomains without individual vetting

ALWAYS:
  ✓ Maintain an explicit allowlist of approved origins
  ✓ Validate origin exactly (case-sensitive, full URL with protocol)
  ✓ Add Vary: Origin when dynamically setting ACAO
  ✓ Keep credentials off public APIs (use * without ACAC)
  ✓ Log and alert on unexpected origin values
```

---

## Correct Implementation by Language

### Node.js / Express

```javascript
const allowedOrigins = [
  'https://app.example.com',
  'https://admin.example.com',
];

app.use((req, res, next) => {
  const origin = req.headers.origin;
  
  if (origin && allowedOrigins.includes(origin)) {
    res.setHeader('Access-Control-Allow-Origin', origin);
    res.setHeader('Access-Control-Allow-Credentials', 'true');
    res.setHeader('Vary', 'Origin');
  }
  
  if (req.method === 'OPTIONS') {
    res.setHeader('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE');
    res.setHeader('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    res.setHeader('Access-Control-Max-Age', '86400');
    return res.status(204).end();
  }
  
  next();
});

// USING cors npm PACKAGE:
const cors = require('cors');
app.use(cors({
  origin: allowedOrigins,  // pass the array — cors handles the check!
  credentials: true,
}));
```

### Python / Flask

```python
from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)

ALLOWED_ORIGINS = {
    'https://app.example.com',
    'https://admin.example.com',
}

# Using flask-cors:
CORS(app, origins=list(ALLOWED_ORIGINS), supports_credentials=True)

# OR manual:
@app.after_request
def add_cors_headers(response):
    origin = request.headers.get('Origin', '')
    if origin in ALLOWED_ORIGINS:
        response.headers['Access-Control-Allow-Origin'] = origin
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        response.headers['Vary'] = 'Origin'
    return response
```

### Django

```python
# settings.py:
INSTALLED_APPS = [
    ...
    'corsheaders',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',  # MUST be before CommonMiddleware!
    'django.middleware.common.CommonMiddleware',
    ...
]

# Strict whitelist:
CORS_ALLOWED_ORIGINS = [
    "https://app.example.com",
    "https://admin.example.com",
]

CORS_ALLOW_CREDENTIALS = True

# DON'T USE (allows all):
# CORS_ALLOW_ALL_ORIGINS = True
```

### PHP

```php
$allowed_origins = [
    'https://app.example.com',
    'https://admin.example.com',
];

$origin = $_SERVER['HTTP_ORIGIN'] ?? '';

if (in_array($origin, $allowed_origins, true)) {
    header("Access-Control-Allow-Origin: $origin");
    header("Access-Control-Allow-Credentials: true");
    header("Vary: Origin");
}

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    header("Access-Control-Allow-Methods: GET, POST, PUT, DELETE");
    header("Access-Control-Allow-Headers: Content-Type, Authorization");
    header("Access-Control-Max-Age: 86400");
    http_response_code(204);
    exit;
}
```

---

## Public API vs Authenticated API

```
PUBLIC API (no auth, public data):
  Access-Control-Allow-Origin: *
  (no Access-Control-Allow-Credentials)
  → Any origin can read response → fine for public data!

AUTHENTICATED API (cookies/sessions):
  Use strict origin whitelist + ACAC: true
  Never use * with credentials
  
MIXED API (some public, some private):
  Apply whitelist to private endpoints
  Apply * only to genuinely public endpoints
```

---

## The Vary: Origin Header

```
WHY IT MATTERS:
  If ACAO changes based on Origin header (dynamic whitelist),
  and the response is cached by CDN/proxy:
  
  Request from app.example.com → cached with ACAO: https://app.example.com
  Request from attacker.com    → CDN serves cached response!
                                  ACAO: https://app.example.com
                                  (wrong, but attacker's browser ignores this)
  
  OR:
  Request from attacker.com    → cached with ACAO: (none)
  Request from app.example.com → CDN serves cached "no CORS" response!
                                  App breaks!

FIX:
  Add: Vary: Origin
  → CDN caches separate responses per Origin value
  → No cache poisoning!
  → Always add this when ACAO is set dynamically!

ALTERNATIVE:
  Cache-Control: no-store, private  → prevent caching of private API responses
```

---

## Security Test Checklist for Developers

```
BEFORE DEPLOYING CORS CONFIG:
  [ ] Are all allowed origins explicitly listed?
  [ ] Is the origin comparison exact (not substring/regex)?
  [ ] Is the protocol checked (https:// not http://)?
  [ ] Are no untrusted subdomains in the allowlist?
  [ ] Is null origin NOT in the allowlist (for credentialed endpoints)?
  [ ] Is Vary: Origin set on dynamic ACAO responses?
  [ ] Is Access-Control-Allow-Origin: * NOT combined with ACAC: true?
  [ ] Are OPTIONS preflight responses correctly configured?
  [ ] Is the CORS config consistent across all environments (dev/staging/prod)?
  [ ] Are any old CORS headers from dev config removed?

TEST WITH:
  curl -H "Origin: https://evil.com" [endpoint] | grep access-control
  curl -H "Origin: null" [endpoint] | grep access-control
  curl -H "Origin: http://[yourapp.com]" [endpoint] | grep access-control
  (HTTP version of your allowed origin should NOT be trusted by HTTPS site)
```

---

## Common Mistakes Summary

```
MISTAKE                             FIX
──────────────────────────────────────────────────────────────────────
Blindly reflecting Origin header   → Whitelist check before reflecting
Trusting null origin               → Never whitelist null
Trusting HTTP origins from HTTPS   → Require https:// in whitelist
Using endsWith('.domain.com')      → Exact match from explicit list
Using * with credentials           → Use explicit origin whitelist
Not setting Vary: Origin           → Always set Vary: Origin on dynamic ACAO
Allowing subdomains without vetting → List only the specific needed origins
Dev config (CORS: *) in production → Different config per environment
Trusting all subdomains            → List each needed subdomain explicitly
```

---

## Related Notes
- [[01 - What is CORS and Why It Exists]] — CORS fundamentals
- [[04 - Origin Reflection Misconfiguration]] — what goes wrong
- [[05 - Null Origin Misconfiguration]] — null origin attack
- [[06 - Wildcard with Credentials]] — wildcard misuse
- [[07 - Subdomain Trust]] — subdomain attacks
- [[08 - Regex Bypass]] — regex weaknesses
