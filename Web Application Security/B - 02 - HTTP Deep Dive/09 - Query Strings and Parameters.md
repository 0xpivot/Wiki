---
tags: [vapt, http, web, beginner]
difficulty: beginner
module: "02 - HTTP Deep Dive"
topic: "02.09 Query Strings and Parameters"
---

# 02.09 — Query Strings and Parameters

## What is it?

**Query strings** are the part of a URL after the `?` symbol. They pass parameters (key-value pairs) from client to server. **Parameters** can also appear in the POST body. Both are primary injection targets for nearly every web vulnerability class.

---

## Query String Anatomy

```
https://target.com/search?q=shoes&category=women&sort=price&page=2
                          │       │               │          │
                          q=shoes │               │          page=2
                                  category=women  sort=price

Structure:
  ?     → start of query string
  key=value  → one parameter
  &     → separator between parameters
  +     → space (alternate encoding)
  %20   → space (URL encoded)

In request:
  GET /search?q=shoes&sort=price HTTP/1.1
  Host: target.com
```

---

## Parameter Types — Where They Appear

```
1. URL QUERY STRING (GET params):
   GET /users?id=123&role=admin HTTP/1.1
   → Visible in browser URL bar, browser history, server logs, Referer header

2. POST BODY - URL encoded (HTML forms):
   POST /login HTTP/1.1
   Content-Type: application/x-www-form-urlencoded

   username=admin&password=secret&_token=csrf123

3. POST BODY - JSON:
   POST /api/users HTTP/1.1
   Content-Type: application/json

   {"username":"admin","role":"user","age":25}

4. POST BODY - Multipart (file upload + fields):
   POST /upload HTTP/1.1
   Content-Type: multipart/form-data; boundary=----boundary

   ------boundary
   Content-Disposition: form-data; name="file"; filename="avatar.png"
   ...binary data...
   ------boundary
   Content-Disposition: form-data; name="submit"
   Upload
   ------boundary--

5. PATH PARAMETERS (REST API):
   GET /api/users/123/posts/456 HTTP/1.1
   ↑ 123 = user ID (path param)  ↑ 456 = post ID (path param)
```

---

## Security Context — Parameters in VAPT

### Every Parameter is a Potential Injection Point

```
PARAMETER                         WHAT TO TRY
────────────────────────────────────────────────────────────
?id=123                  SQLi: ?id=1' OR '1'='1--
?name=shoes              XSS: ?name=<script>alert(1)</script>
?url=http://target.com   SSRF: ?url=http://169.254.169.254/
?file=report.pdf         Path traversal: ?file=../../../etc/passwd
?template=email.html     SSTI: ?template={{7*7}}
?redirect=/dashboard     Open redirect: ?redirect=https://evil.com
?cmd=list                Command injection: ?cmd=list;whoami
?format=json             XXE: ?format=xml with malicious XML body
?amount=100              Business logic: ?amount=-100 (negative)
?user=alice              IDOR: ?user=bob (horizontal priv esc)
?role=user               Mass assignment: try role=admin
```

### Hidden Parameters — Discovery

```bash
# ffuf for parameter fuzzing
ffuf -u https://target.com/api/search?FUZZ=test \
     -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt \
     -mc 200 -fc 404

# Arjun — dedicated parameter discovery tool
arjun -u https://target.com/api/search
arjun -u https://target.com/api/user --get  # GET params
arjun -u https://target.com/api/login --post --data '{"test":"1"}' # POST JSON

# Burp Suite → Target → Site map → right-click Engagement tools → Discover content
# Also: Param Miner Burp extension → automatically finds unlinked params

# x8 — fast parameter discovery
x8 -u "https://target.com/page?id=1" -w params_wordlist.txt
```

### Parameter Pollution

```
HTTP Parameter Pollution (HPP): pass same parameter multiple times.
Server and WAF may handle duplicates differently!

URL: ?id=1&id=2

PHP:    $_GET['id'] = "2"         (last wins)
ASP.NET: Request["id"] = "1,2"   (comma-joined)
Flask:   request.args.get('id') = "1"  (first wins)
Express: req.query.id = ["1","2"] (array)

ATTACK:
WAF checks first occurrence: id=safe_value
App uses last occurrence: id=malicious_value

Example:
GET /api/user?id=1&id=2' OR '1'='1--
WAF: sees id=1 (safe) → allows
App: uses last id=2' OR '1'='1-- → SQLi!

Test with Burp:
Add same parameter multiple times in Repeater
Watch response behavior
```

### Mass Assignment — JSON Parameters

```
API receives JSON body and passes it to ORM (Object-Relational Mapper).
If server uses all parameters without whitelist → you can set hidden fields!

INTENDED REQUEST:
POST /api/users HTTP/1.1
{"username":"alice","email":"alice@test.com"}

ATTACK (add admin=true or role=admin):
POST /api/users HTTP/1.1
{"username":"alice","email":"alice@test.com","isAdmin":true,"role":"admin"}

If server passes entire JSON to model.create() or model.update():
→ isAdmin field gets set!

COMMON VULNERABLE FIELDS:
  isAdmin, admin, role, verified, balance, credits
  email (if change own email to admin's)
  id (to change which record gets updated)
```

### Parameter Type Confusion

```
App expects integer:
  ?id=123          → works normally
  ?id=123.0        → treated as 123 (float → int)
  ?id=123abc       → parsed as 123 in some languages
  ?id=0x7B         → hexadecimal = 123
  ?id=[]           → array instead of scalar
  ?id[0]=123       → PHP array notation
  ?id=null         → null value
  ?id=undefined    → might crash app
  ?id=1e2          → scientific notation = 100
  ?id=true         → boolean

Each type produces different behavior!
Type confusion can bypass length checks, validations, etc.
```

---

## Hands-On: Parameter Testing

```bash
# Basic parameter injection test
curl "https://target.com/search?q=test'"
curl "https://target.com/search?q=<script>alert(1)</script>"
curl "https://target.com/search?q=../../../etc/passwd"

# Parameter pollution
curl "https://target.com/api/user?id=1&id=2"

# All injection types with ffuf
ffuf -u "https://target.com/search?q=FUZZ" \
     -w /usr/share/seclists/Fuzzing/Polyglots.txt \
     -mc 200 -ac -v

# Mass assignment test
curl -X POST https://target.com/api/register \
  -H "Content-Type: application/json" \
  -d '{"username":"attacker","password":"test","isAdmin":true,"role":"admin"}'

# Arjun parameter discovery
arjun -u https://target.com/api/search -q -o params.json

# x8 parallel parameter brute force
x8 -u "https://target.com/api/user?id=1" \
   -w /usr/share/seclists/Discovery/Web-Content/burp-parameter-names.txt \
   -t 30
```

---

## How to Fix / Secure

| Risk | Fix |
|------|-----|
| Mass assignment | Use explicit allowlist of fields, not accept-all |
| Parameter pollution | Define clear behavior for duplicate params |
| Injection via parameters | Input validation + parameterized queries |
| Hidden parameters with dangerous functions | Remove debug params in production |
| Sensitive data in GET params | Use POST body for sensitive data |

---

## Related Notes
- [[08 - URLs Anatomy]] — URL structure context
- [[10 - URL Encoding and Percent Encoding]] — encoding parameter values
- [[Module 01 - SQL Injection]] — SQL via parameters
- [[Module 02 - XSS]] — XSS via parameters
- [[Module 13 - SSRF]] — SSRF via URL parameters
- [[Module 06 - Mass Assignment]] — mass assignment vulnerabilities
