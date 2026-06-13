---
tags: [vapt, file-upload, defense, advanced]
difficulty: advanced
module: "22 - File Upload"
topic: "22.15 Defense — Extension Allowlists, Content Validation, Separate Storage"
---

# 22.15 — Defense: Extension Allowlists, Content Validation, Separate Storage

## What is it?
Securing file upload functionality is notoriously difficult because attackers only need to find a single flaw in the validation logic to achieve Remote Code Execution (RCE). A robust defense cannot rely on a single check (like a blocklist). Instead, it requires a **defense-in-depth** architecture.

The gold standard for file upload defense involves three mandatory pillars:
1. **Extension Allowlists:** Explicitly defining what is allowed and rejecting everything else.
2. **Content Validation:** Re-processing the file to strip payloads and verify it matches its extension.
3. **Separate Storage:** Storing the files in an environment where execution is mathematically impossible (like an S3 bucket or a sandboxed, non-executable filesystem).

Think of it like a high-security prison. You don't just check someone's ID at the door (Allowlist). You also put them through a metal detector and X-ray scanner (Content Validation). Finally, you put them in a locked cell where they cannot touch the control panels (Separate Storage).

## ASCII Diagram
```text
[User Uploads File] ──> "shell.php.jpg"
       │
       ▼
+---------------------------------------------------+
| 1. EXTENSION ALLOWLIST                            |
|    Extract true suffix: ".jpg"                    |
|    Is in ['.jpg', '.png']? YES -> Proceed         |
+---------------------------------------------------+
       │
       ▼
+---------------------------------------------------+
| 2. CONTENT VALIDATION                             |
|    Load into Image Library (e.g., Pillow/Imagick) |
|    Does it parse as a real image? YES             |
|    Strip EXIF/Metadata & Re-encode -> Safe Image  |
+---------------------------------------------------+
       │
       ▼
+---------------------------------------------------+
| 3. SECURE STORAGE & RENAMING                      |
|    Discard "shell.php.jpg"                        |
|    Generate UUID: "550e8400-e29b-41d4-a716.jpg"   |
|    Save to isolated AWS S3 Bucket or CDN          |
+---------------------------------------------------+
       │
       ▼
[Attacker defeated. File is safe, harmless, and non-executable.]
```

## Core Defense 1: Extension Allowlists
Never use a blocklist (e.g., `if ext == '.php' return false`). Attackers will bypass it using `.phtml`, `.php5`, or null bytes. You must use a strict allowlist.

**Rules for Allowlists:**
- Extract the extension carefully. Always take the *very last* string after the final dot.
- Convert it to lowercase to prevent `.PhP` bypasses.
- Match it strictly against a hardcoded list of allowed extensions.

**Python Example:**
```python
import os

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf'}

def is_extension_safe(filename):
    # os.path.splitext correctly handles multiple dots, returning the last one
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError("File type strictly prohibited.")
    return ext
```

## Core Defense 2: Content Validation (Re-encoding)
Validating the `Content-Type` header or checking the "Magic Bytes" is not enough, as attackers can easily spoof both (Polyglot files). The only secure way to validate content, especially for images, is to **re-encode** the file.

When you pass an image through a rendering library and save it as a new image, the library discards the raw bytes and generates a fresh image. Any PHP code hidden in the metadata or appended to the file is completely destroyed.

**Python Example (using Pillow):**
```python
from PIL import Image
import io

def sanitize_image(raw_bytes):
    try:
        # Load the image using Pillow
        img = Image.open(io.BytesIO(raw_bytes))
        img.verify() # Verify it's structurally an image
        
        # Re-open and strip it of all metadata/injections by saving to a new buffer
        img = Image.open(io.BytesIO(raw_bytes))
        
        # Convert to RGB to strip alpha channels if not needed
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')
            
        safe_buffer = io.BytesIO()
        img.save(safe_buffer, format='JPEG') # Force save as strict JPEG
        return safe_buffer.getvalue()
    except Exception as e:
        raise ValueError("Image content validation failed. Malicious file detected.")
```

## Core Defense 3: Separate Storage & Execution Prevention
Even if your validation fails, you can prevent RCE by ensuring the environment where the file is stored has no capability to execute scripts.

**Rules for Storage:**
1. **Never use user-provided filenames.** Generate a UUID. This prevents Path Traversal (`../`) and Overwriting files.
2. **Store outside the Web Root.** Do not store files in `/var/www/html/uploads/`. Store them in `/var/app_data/uploads/` and use a script to fetch and stream them to the user, OR use a cloud provider like Amazon S3.
3. **Strip Execution Permissions.** If you must use a local web server directory, configure the web server to forcefully block execution.

**Nginx Configuration (Disable Execution):**
```nginx
location ^~ /uploads/ {
    # If any PHP file somehow gets here, deny access
    location ~ \.php$ {
        deny all;
    }
    
    # Force the browser to NOT MIME-sniff the file (prevents XSS)
    add_header X-Content-Type-Options "nosniff";
    
    # Optional: Force download instead of inline rendering for dangerous types
    # add_header Content-Disposition "attachment";
}
```

## Summary Checklist for Secure File Uploads
- [ ] Is an **Allowlist** used for file extensions?
- [ ] Is the `Content-Type` header completely ignored?
- [ ] Are file contents strictly validated or re-encoded (e.g., Image sanitization)?
- [ ] Are user-supplied filenames discarded and replaced with random UUIDs?
- [ ] Are files stored in a non-executable directory, cloud bucket, or external CDN?
- [ ] Are files served with `X-Content-Type-Options: nosniff` headers?
- [ ] Is there a strict file size limit implemented to prevent DoS attacks?

## Related Notes
- [[01 - What Makes File Upload Dangerous]]
- [[02 - Unrestricted File Upload — Webshell Upload]]
- [[07 - File Upload + Path Traversal]]
- [[12 - Image Upload Magic Bytes Bypass]]
