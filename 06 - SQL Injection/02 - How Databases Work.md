---
tags: [vapt, sqli, beginner]
difficulty: beginner
module: "06 - SQL Injection"
topic: "06.02 How Databases Work (SELECT, INSERT, UPDATE, DELETE)"
---

# 06.02 — How Databases Work

## What is a Database?

A database is an organized collection of data stored in tables. Each table has columns (fields) and rows (records). SQL (Structured Query Language) is the language used to interact with relational databases.

```
DATABASE: myapp_db
│
├── TABLE: users
│   ┌────┬──────────┬──────────────────┬────────────┐
│   │ id │ username │ password         │ is_admin   │
│   ├────┼──────────┼──────────────────┼────────────┤
│   │ 1  │ admin    │ 5f4dcc3b5aa765d6 │ 1          │
│   │ 2  │ alice    │ 2b003f9b1a1d4c3e │ 0          │
│   │ 3  │ bob      │ 7f3d8a2b9c1e5f4a │ 0          │
│   └────┴──────────┴──────────────────┴────────────┘
│
└── TABLE: orders
    ┌────┬─────────┬───────────┬────────────┐
    │ id │ user_id │ product   │ price      │
    ├────┼─────────┼───────────┼────────────┤
    │ 1  │ 2       │ Widget    │ 9.99       │
    │ 2  │ 3       │ Gadget    │ 24.99      │
    └────┴─────────┴───────────┴────────────┘
```

---

## Core SQL Commands

### SELECT — Read Data

```sql
-- Get all columns from all rows:
SELECT * FROM users;

-- Get specific columns:
SELECT username, password FROM users;

-- Filter with WHERE:
SELECT * FROM users WHERE id = 1;
SELECT * FROM users WHERE username = 'admin';

-- Multiple conditions:
SELECT * FROM users WHERE username = 'admin' AND password = 'secret';
SELECT * FROM users WHERE id = 1 OR id = 2;

-- Sort results:
SELECT * FROM users ORDER BY id ASC;
SELECT * FROM users ORDER BY id DESC;

-- Limit results:
SELECT * FROM users LIMIT 1;
SELECT * FROM users LIMIT 5 OFFSET 10;   -- rows 11-15

-- Join two tables:
SELECT users.username, orders.product
FROM users
JOIN orders ON users.id = orders.user_id;

-- Count rows:
SELECT COUNT(*) FROM users;

-- Aggregate:
SELECT username, COUNT(*) FROM orders GROUP BY user_id;
```

### INSERT — Add Data

```sql
-- Insert one row:
INSERT INTO users (username, password, is_admin)
VALUES ('charlie', 'hash123', 0);

-- Insert via SQLi (second-order):
-- If username='charlie' is stored and later used in:
-- SELECT * FROM users WHERE username = 'charlie'
-- AND you stored username = "charlie' OR '1'='1"
-- → SECOND ORDER SQLi!
```

### UPDATE — Modify Data

```sql
-- Update specific row:
UPDATE users SET password = 'newhash' WHERE id = 1;

-- Update multiple rows:
UPDATE users SET is_admin = 1 WHERE username = 'alice';

-- DANGEROUS (no WHERE = affects ALL rows!):
UPDATE users SET password = 'hacked';
```

### DELETE — Remove Data

```sql
-- Delete specific row:
DELETE FROM users WHERE id = 3;

-- DANGEROUS (no WHERE = deletes ALL rows!):
DELETE FROM users;
-- This is what happens if attacker uses ; DROP TABLE users--!
```

---

## SQL Comments (Critical for Injection)

```sql
-- Single-line comment (MySQL, MSSQL, PostgreSQL):
SELECT * FROM users WHERE id = 1 -- rest is ignored

# Single-line comment (MySQL only):
SELECT * FROM users WHERE id = 1 # rest is ignored

/* Multi-line comment (all databases): */
SELECT * FROM users WHERE id = 1 /* this is ignored */ AND 1=1

/* USED IN INJECTION TO IGNORE REMAINING QUERY:
   Original:  SELECT * FROM users WHERE id = 1 AND active = 1
   Injected:  SELECT * FROM users WHERE id = 1 OR 1=1-- AND active = 1
                                                            ↑ commented out!
*/
```

---

## String Concatenation in SQL

```sql
-- MySQL:
SELECT CONCAT(username, ':', password) FROM users;

-- PostgreSQL:
SELECT username || ':' || password FROM users;

-- MSSQL:
SELECT username + ':' + password FROM users;

-- Oracle:
SELECT username || ':' || password FROM users;

-- USEFUL IN UNION INJECTION:
-- UNION SELECT CONCAT(username,':',password) FROM users--
```

---

## Information Schema (Database Metadata)

Every database has a special database/schema containing metadata about all other databases, tables, and columns. This is gold for SQL injection!

```sql
-- MySQL: list all databases:
SELECT schema_name FROM information_schema.schemata;

-- MySQL: list all tables in current database:
SELECT table_name FROM information_schema.tables
WHERE table_schema = database();

-- MySQL: list all columns in a table:
SELECT column_name FROM information_schema.columns
WHERE table_name = 'users';

-- MySQL: current database name:
SELECT database();

-- MySQL: current user:
SELECT user();

-- MySQL: version:
SELECT version();

-- PostgreSQL equivalents:
SELECT datname FROM pg_database;
SELECT tablename FROM pg_tables WHERE schemaname='public';
SELECT column_name FROM information_schema.columns WHERE table_name='users';
SELECT current_database();
SELECT current_user;
SELECT version();

-- MSSQL equivalents:
SELECT name FROM sys.databases;
SELECT name FROM sys.tables;
SELECT name FROM sys.columns WHERE object_id = OBJECT_ID('users');
SELECT DB_NAME();
SELECT SYSTEM_USER;
SELECT @@VERSION;
```

---

## Database-Specific Syntax Cheat Sheet

```sql
-- STRING COMPARISON:
MySQL/PostgreSQL: WHERE username = 'admin'
MSSQL:           WHERE username = 'admin'
Oracle:          WHERE username = 'admin'

-- LIMIT / TOP:
MySQL/PostgreSQL: SELECT * FROM users LIMIT 1
MSSQL:           SELECT TOP 1 * FROM users
Oracle:          SELECT * FROM users WHERE ROWNUM = 1

-- STRING FUNCTIONS:
MySQL:      SUBSTRING('hello', 1, 1)   → 'h'
PostgreSQL: SUBSTRING('hello', 1, 1)   → 'h'
MSSQL:      SUBSTRING('hello', 1, 1)   → 'h'
Oracle:     SUBSTR('hello', 1, 1)      → 'h'

-- STRING LENGTH:
MySQL:      LENGTH('hello')    → 5
MSSQL:      LEN('hello')       → 5
Oracle:     LENGTH('hello')    → 5

-- ASCII VALUE:
MySQL/MSSQL:   ASCII('a')     → 97
PostgreSQL:    ASCII('a')     → 97
Oracle:        ASCII('a')     → 97

-- SLEEP / DELAY (time-based):
MySQL:      SELECT SLEEP(5)
MSSQL:      WAITFOR DELAY '0:0:5'
PostgreSQL: SELECT pg_sleep(5)
Oracle:     dbms_pipe.receive_message('a',5)

-- CONCAT:
MySQL:      CONCAT(a, b, c)
PostgreSQL: a || b || c
MSSQL:      a + b + c
Oracle:     a || b || c
```

---

## How Web Applications Use Databases

```
TYPICAL FLOW (login form):

1. User enters: username=admin&password=secret

2. PHP code:
   $sql = "SELECT * FROM users WHERE username='" . $username . 
          "' AND password='" . md5($password) . "'";

3. SQL executed:
   SELECT * FROM users WHERE username='admin' AND password='5ebe2294...'

4. If rows returned → user authenticated!

INJECTION OPPORTUNITY:
   Username: admin'--
   SQL becomes:
   SELECT * FROM users WHERE username='admin'-- AND password='anything'
                                               ↑ password check commented out!
   → Returns admin user without knowing password!
```

---

## Related Notes
- [[01 - What is SQL Injection]] — SQLi introduction
- [[03 - Error-Based SQLi]] — exploiting error messages
- [[04 - Union-Based SQLi]] — UNION SELECT exploitation
- [[15 - MySQL Specific Payloads]] — MySQL-specific commands
- [[16 - PostgreSQL Specific Payloads]] — PostgreSQL commands
