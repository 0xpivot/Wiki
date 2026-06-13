---
tags: [vapt, recon, beginner]
difficulty: beginner
module: "05 - Recon"
topic: "05.29 Directory and File Bruteforcing (ffuf, gobuster, feroxbuster)"
---

# 05.29 — Directory and File Bruteforcing

## What is it?

Web servers often have pages, directories, and files that aren't linked from the UI — admin panels, backup files, API endpoints, config files, debug pages. Directory and file bruteforcing requests thousands of common paths to discover these hidden resources.

```
WHAT YOU FIND:
  /admin/           → admin panel
  /backup.zip       → full site backup!
  /api/v2/          → undocumented API version
  /.env             → environment variables (credentials!)
  /config.php.bak   → backup of PHP config
  /phpinfo.php      → PHP info page
  /debug/           → debug endpoints
  /console          → server console (CRITICAL!)
  /actuator/        → Spring Boot actuator (health, env, beans...)
  /.git/            → git repository exposed!
```

---

## ffuf (Fastest Web Fuzzer)

```bash
# INSTALL:
go install -v github.com/ffuf/ffuf/v2@latest

# BASIC DIRECTORY SCAN:
ffuf -u https://target.com/FUZZ \
  -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt

# DIRECTORY + EXTENSIONS:
ffuf -u https://target.com/FUZZ \
  -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-words.txt \
  -e .php,.html,.txt,.bak,.backup,.old,.zip,.tar.gz,.sql,.json,.xml

# FILTER OPTIONS:
ffuf -u https://target.com/FUZZ \
  -w wordlist.txt \
  -mc 200,301,302,401,403  # show only these status codes
  -fc 404                   # filter out 404s
  -fs 1234                  # filter responses of size 1234
  -fw 10                    # filter responses with 10 words
  -fl 5                     # filter responses with 5 lines
  -fr "Not Found"           # filter responses matching regex

# RECURSIVE SCAN (follow discovered dirs):
ffuf -u https://target.com/FUZZ \
  -w wordlist.txt \
  -recursion \
  -recursion-depth 2 \
  -e .php,.html,.txt

# RATE LIMITING (be nice / avoid detection):
ffuf -u https://target.com/FUZZ \
  -w wordlist.txt \
  -rate 100              # 100 requests/second max

# OUTPUT TO FILE:
ffuf -u https://target.com/FUZZ \
  -w wordlist.txt \
  -o results.json -of json   # json, ejson, html, md, csv, all

# MULTI-TARGET (scan several directories at once):
ffuf -u https://target.com/admin/FUZZ \
  -w wordlist.txt \
  -mc 200,301

# CUSTOM HEADERS (authenticated scan):
ffuf -u https://target.com/FUZZ \
  -w wordlist.txt \
  -H "Cookie: session=ABCDEF" \
  -H "Authorization: Bearer TOKEN"

# POST DATA FUZZING:
ffuf -u https://target.com/login \
  -w usernames.txt \
  -X POST \
  -d "username=FUZZ&password=Password123" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -fc 403
```

---

## gobuster (dir, file, vhost)

```bash
# INSTALL:
go install -v github.com/OJ/gobuster/v3@latest

# BASIC DIR SCAN:
gobuster dir \
  -u https://target.com \
  -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt

# WITH EXTENSIONS:
gobuster dir \
  -u https://target.com \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
  -x php,html,txt,bak,old,zip

# STATUS CODES TO SHOW:
gobuster dir \
  -u https://target.com \
  -w wordlist.txt \
  -s "200,204,301,302,307,401,403"

# THREADS AND TIMEOUT:
gobuster dir \
  -u https://target.com \
  -w wordlist.txt \
  -t 50 \
  --timeout 5s

# FOLLOW REDIRECTS:
gobuster dir -u https://target.com -w wordlist.txt -r

# AUTHENTICATED:
gobuster dir \
  -u https://target.com \
  -w wordlist.txt \
  -c "session=ABCDEF"        # cookie
  -H "Authorization: Bearer TOKEN"

# NO TLS VERIFY:
gobuster dir -u https://target.com -w wordlist.txt -k

# OUTPUT:
gobuster dir -u https://target.com -w wordlist.txt -o gobuster.txt

# FILE SCAN (specific file names, not dirs):
gobuster dir \
  -u https://target.com \
  -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-small-files.txt
```

---

## feroxbuster (Recursive, Fast)

```bash
# INSTALL:
cargo install feroxbuster
# OR:
apt install feroxbuster

# BASIC SCAN (recursive by default!):
feroxbuster -u https://target.com

# WITH WORDLIST:
feroxbuster -u https://target.com \
  -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-directories.txt

# WITH EXTENSIONS:
feroxbuster -u https://target.com \
  -w wordlist.txt \
  -x php,html,txt,bak

# SET RECURSION DEPTH:
feroxbuster -u https://target.com -d 3   # max 3 levels deep

# FILTER:
feroxbuster -u https://target.com \
  -C 404 \        # filter 404s
  --filter-size 1234

# THREADS:
feroxbuster -u https://target.com -t 100

# OUTPUT:
feroxbuster -u https://target.com -o ferox-results.txt

# STEALTH (low and slow):
feroxbuster -u https://target.com -L 5  # 5 requests/second

# AUTO-TUNE (adapts to server responses):
feroxbuster -u https://target.com --auto-tune
```

---

## Wordlist Selection Strategy

```bash
# SMALL (quick, for CTF/initial check):
/usr/share/wordlists/seclists/Discovery/Web-Content/common.txt          # ~4500 words
/usr/share/wordlists/seclists/Discovery/Web-Content/quickhits.txt       # known sensitive paths

# MEDIUM (balance of speed/coverage):
/usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-directories.txt  # ~30k
/usr/share/wordlists/seclists/Discovery/Web-Content/raft-medium-words.txt        # ~56k

# LARGE (comprehensive):
/usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt             # ~220k
/usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-words.txt # ~119k

# PLATFORM-SPECIFIC WORDLISTS:
/usr/share/wordlists/seclists/Discovery/Web-Content/CMS/wordpress.fuzz.txt
/usr/share/wordlists/seclists/Discovery/Web-Content/CMS/drupal.txt
/usr/share/wordlists/seclists/Discovery/Web-Content/spring-boot.txt   # Spring actuators
/usr/share/wordlists/seclists/Discovery/Web-Content/api/api-endpoints.txt

# HIGH-VALUE SENSITIVE FILES (always check!):
/usr/share/wordlists/seclists/Discovery/Web-Content/quickhits.txt
# Contains: .env, .git, phpinfo.php, wp-config.php, .htpasswd, etc.
```

---

## Context-Specific Scanning

```bash
# WORDPRESS:
gobuster dir -u https://target.com \
  -w /usr/share/wordlists/seclists/Discovery/Web-Content/CMS/wordpress.fuzz.txt \
  -x php

# SPRING BOOT ACTUATORS:
ffuf -u https://target.com/FUZZ \
  -w /usr/share/wordlists/seclists/Discovery/Web-Content/spring-boot.txt \
  -mc 200
# /actuator → all actuators listed!
# /actuator/env → environment variables (credentials!)
# /actuator/heapdump → JVM heap dump (contains secrets!)
# /actuator/mappings → all URL mappings

# LARAVEL:
ffuf -u https://target.com/FUZZ \
  -w /usr/share/wordlists/seclists/Discovery/Web-Content/laravel.txt

# API ENDPOINTS:
ffuf -u https://target.com/api/FUZZ \
  -w /usr/share/wordlists/seclists/Discovery/Web-Content/api/api-endpoints.txt
  
# ADMIN PANEL HUNTING:
ffuf -u https://target.com/FUZZ \
  -w /usr/share/wordlists/seclists/Discovery/Web-Content/AdminPanels.fuzz.txt \
  -mc 200,301,302,401,403
```

---

## Interpreting Results

```
STATUS CODE MEANING:
  200 → EXISTS + ACCESSIBLE → test it!
  301/302 → REDIRECT → follow it!
  401 → EXISTS but requires authentication → try bypass!
  403 → EXISTS but forbidden → try bypass! (X-Forwarded-For, path variations)
  404 → Does not exist (usually)
  500 → Server error → probe further, may indicate injection point

403 BYPASS ATTEMPTS:
  # Try path variations:
  curl https://target.com/admin
  curl https://target.com/admin/
  curl https://target.com/admin/.
  curl https://target.com/%2fadmin
  curl https://target.com/admin%20
  
  # Try different HTTP methods:
  curl -X POST https://target.com/admin
  curl -X OPTIONS https://target.com/admin
  
  # Try headers:
  curl -H "X-Original-URL: /admin" https://target.com/
  curl -H "X-Rewrite-URL: /admin" https://target.com/
  curl -H "X-Forwarded-For: 127.0.0.1" https://target.com/admin
```

---

## Related Notes
- [[30 - Parameter Discovery]] — finding hidden parameters
- [[15 - robots.txt and sitemap.xml]] — known paths to check
- [[19 - Source Code Leakage]] — specific sensitive files
- [[28 - Virtual Host Enumeration]] — vhost-level discovery
