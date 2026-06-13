---
tags: [vapt, authentication, beginner]
difficulty: beginner
module: "16 - Authentication"
topic: "16.24 Username/Password in URL"
---

# 16.24 — Username/Password in URL

## The Problem: Credentials in GET Parameters

```
HAPPENS WHEN:
  Login form uses GET instead of POST:
  GET /login?username=admin&password=secret123 HTTP/1.1
  
  OR:
  API designed with credentials in URL:
  GET /api/data?api_key=MY_SECRET_KEY
  GET /api/user?token=MY_JWT_TOKEN
  
WHY THIS IS BAD:
  URLs end up in MANY places automatically:
  1. Browser history (history.json, addressbar autocomplete)
  2. Server access logs (every request URL is logged!)
  3. Reverse proxy / CDN logs (Nginx, CloudFront, Fastly)
  4. Referer header → external pages see the URL!
  5. Screenshot tools / screen sharing
  6. Bookmarks (user bookmarks the login URL with password!)
  7. Browser cache
  8. Network monitoring / SIEM tools
```

---

## Where Credentials Leak From URLs

```
SCENARIO 1: SERVER LOGS
  Nginx access log:
  2024-01-15 10:23:45 GET /login?username=admin&password=Admin123! HTTP/1.1

  → Any developer with log access can see the password!
  → Log aggregation tools (Splunk, ELK) index this!
  → Backup of logs = credential backup!
  
SCENARIO 2: REFERER HEADER
  User logs in via:
  GET /login?username=alice&password=Secret1! HTTP/1.1
  
  Login redirects to /dashboard which loads an analytics script:
  GET https://analytics.example.com/track.js HTTP/1.1
  Referer: https://myapp.com/login?username=alice&password=Secret1!
  
  → Third-party analytics server gets the password in Referer!

SCENARIO 3: BROWSER HISTORY
  If user on shared computer → anyone can check browser history
  → Full login URL with credentials visible

SCENARIO 4: CURL / SCRIPTS
  Developer tests API:
  curl https://api.example.com/data?api_key=SECRET123
  → Shell history stores this command!
  history | grep api_key  → credentials exposed!
```

---

## Testing

```bash
# CHECK IF LOGIN USES GET:
curl -v "https://target.com/login" -d "username=test&password=test"
# Or intercept in Burp and check if login is a GET request

# CHECK FOR CREDENTIALS IN URL OF ANY ENDPOINT:
# In Burp → HTTP History → filter by "Params: present"
# Look for: token=, api_key=, password=, secret=, auth=, key= in URLs

# CHECK API DOCUMENTATION:
# Does API guide say: GET /api?api_key=YOUR_KEY
# → Report this pattern even if not immediately exploitable

# TEST REFERER LEAKAGE:
# Visit the page that has credentials in URL
# Click a link to an external site (or load external resource)
# In Burp, check Referer header of outbound requests
# → Does it contain the credential-bearing URL?
```

---

## Fix

```
DEFENSES:
  ✓ Use POST for login forms (method="POST" not method="GET")
  
  ✓ Use Authorization header instead of URL for APIs:
    WRONG: GET /api/data?api_key=SECRET
    RIGHT: GET /api/data
           Authorization: Bearer SECRET
           OR: X-API-Key: SECRET
           
  ✓ For OAuth tokens: use Authorization: Bearer, not ?access_token=
    OAuth spec says URL parameter is SHOULD NOT (discouraged)
    
  ✓ If token MUST be in URL (e.g., email links):
    - Make it single-use
    - Short expiry
    - Redirect to clean URL after consumption (remove token from URL)
    
  ✓ Configure logging to redact sensitive parameters:
    Nginx: log_format with $arg_username but NOT $arg_password
    
  ✓ Set Referrer-Policy: no-referrer header on pages with sensitive URLs
```

---

## Related Notes
- [[07 - Forgot Password Token Predictability]] — tokens in URLs (reset links)
- [[21 - Magic Link Vulnerabilities]] — Referer leakage via URLs
- [[28 - Defense Rate Limiting Lockout MFA]] — defense guide
