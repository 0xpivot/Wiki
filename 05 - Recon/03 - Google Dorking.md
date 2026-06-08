---
tags: [vapt, recon, osint, beginner]
difficulty: beginner
module: "05 - Recon"
topic: "05.03 Google Dorking"
---

# 05.03 — Google Dorking

## What is it?

Google dorking uses advanced Google search operators to find specific types of information that targets expose publicly. Named after "Johnny Long" who popularized it, dorks can find exposed credentials, admin panels, vulnerable files, database files, and sensitive configuration — all indexed by Google.

---

## Core Google Search Operators

```
OPERATOR          FUNCTION                        EXAMPLE
──────────────────────────────────────────────────────────────────
site:             Limit to specific domain        site:target.com
inurl:            String in URL                  inurl:admin
intitle:          String in page title           intitle:"index of"
intext:           String in page body            intext:"password"
filetype:         Specific file extension        filetype:pdf
ext:              Extension (same as filetype)   ext:sql
-                 Exclude results               site:target.com -www
*                 Wildcard                        site:*.target.com
"exact phrase"    Exact phrase match             "password" "target.com"
OR                Either term                    site:target.com OR site:sub.target.com
cache:            Google's cached copy           cache:target.com
link:             Links to URL                   link:target.com
related:          Related sites                  related:target.com
```

---

## Essential Dorks for VAPT

```
ADMIN AND LOGIN PANELS:
  site:target.com intitle:"admin" inurl:admin
  site:target.com intitle:"login" inurl:login
  site:target.com inturl:"/admin/"
  site:target.com inurl:"adminpanel"
  site:target.com inurl:"wp-admin"  ← WordPress admin

SENSITIVE FILES:
  site:target.com ext:sql
  site:target.com ext:xlsx "password"
  site:target.com ext:txt "password"
  site:target.com ext:log
  site:target.com ext:bak  ← backup files!
  site:target.com ext:env  ← environment config!
  site:target.com ext:conf
  site:target.com ext:config

DATABASE FILES:
  site:target.com ext:sql "INSERT INTO"
  site:target.com ext:mdb  ← Microsoft Access DB
  site:target.com filetype:csv "password"

DIRECTORY LISTINGS:
  site:target.com intitle:"index of"
  site:target.com intitle:"directory listing"
  site:target.com intitle:"parent directory"

CONFIGURATION AND ENV:
  site:target.com inurl:".env"
  site:target.com intitle:"phpinfo()"
  site:target.com inurl:"phpinfo.php"
  site:target.com inurl:"server-status"  ← Apache status
  site:target.com inurl:"server-info"

EXPOSED API KEYS AND CREDENTIALS:
  site:github.com "target.com" "api_key"
  site:github.com "target.com" "password"
  site:pastebin.com "target.com"
  site:gist.github.com "target.com" "secret"

DOCUMENT LEAKAGE:
  site:target.com filetype:pdf
  site:target.com filetype:doc "confidential"
  site:target.com filetype:ppt
  site:target.com ext:xlsx

ERROR MESSAGES (reveal internals):
  site:target.com "SQL syntax"
  site:target.com "Warning: mysql_"
  site:target.com "ORA-01" ← Oracle error
  site:target.com "Stack trace" "Exception"
  site:target.com "Fatal error"

CAMERA/IOT (out of scope usually but educational):
  inurl:"/view.shtml"
  intitle:"webcam" inurl:view.shtml
```

---

## Google Hacking Database (GHDB)

```
GHDB: https://www.exploit-db.com/google-hacking-database

Community-maintained database of thousands of dorks organized by category:
  - Footholds (login panels)
  - Files containing usernames
  - Sensitive directories
  - Error messages
  - Files containing passwords
  - Sensitive online shopping info
  - Web server detection

SEARCH BY CATEGORY:
  All footholds: https://www.exploit-db.com/ghdb?type=2&s=target

USEFUL CATEGORIES:
  Type 2: Footholds (admin panels, login pages)
  Type 3: Sensitive directories (git, svn, backup)
  Type 5: Files containing usernames
  Type 6: Files containing passwords
  Type 7: Sensitive online shopping info (payment data)
```

---

## Automated Dorking Tools

```bash
# GOOGLER (CLI Google search):
googler -n 10 "site:target.com filetype:pdf"

# DORKS-EYE (automated dork checking):
python3 dorks-eye.py -d target.com -w dorks.txt

# GITLEAKS + GITHUB SEARCH (for code):
trufflehog github --repo https://github.com/target-org/repo

# PAGODO (GHDB dorks automation):
python3 pagodo.py -g google_dorks.txt -d target.com -l 50

# SHODAN CLI (different search engine):
shodan search "hostname:target.com"
shodan search "ssl.cert.subject.CN:target.com"

# BING DORKS (Bing often indexes more than Google):
# bing.com: site:target.com filetype:pdf
# ip:192.168.1.1 → search by IP on Bing!
```

---

## Dorking for Specific Technologies

```
WORDPRESS:
  site:target.com inurl:"wp-content"
  site:target.com inurl:"wp-admin"
  site:target.com inurl:"xmlrpc.php"
  site:target.com "WordPress" + filetype:txt

APACHE / NGINX:
  site:target.com intitle:"Apache HTTP Server"
  site:target.com intitle:"Welcome to nginx"

JENKINS:
  site:target.com intitle:"Dashboard [Jenkins]"

JIRA:
  site:target.com intitle:"Jira" inurl:jira

ELASTIC/KIBANA:
  site:target.com intitle:"Kibana"
  intitle:"Kibana" inurl:5601  ← default port!

GRAFANA:
  site:target.com intitle:"Grafana"

PHPMYADMIN:
  site:target.com intitle:"phpMyAdmin"
  site:target.com inurl:phpmyadmin
```

---

## Legal Note

```
Google dorking itself is LEGAL (using public search engine).
ACCESSING indexed sensitive files requires authorization!

IF you find a sensitive exposed file:
  - Do NOT download or use the data
  - Document the dork and URL
  - Report to client (responsible disclosure)
  
Example boundary:
  LEGAL: Search for "site:target.com ext:sql" → see URL in results
  MAY BE ILLEGAL: Click on .sql backup file, view contents
  (Depends on authorization and intent)
```

---

## Related Notes
- [[02 - OSINT]] — broader OSINT context
- [[04 - Shodan]] — another powerful search tool
- [[11 - GitHub Dorking for Secrets]] — code repository dorking
