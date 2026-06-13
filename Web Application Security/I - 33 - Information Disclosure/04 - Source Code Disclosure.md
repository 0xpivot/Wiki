---
tags: [vapt, information-disclosure, lfi, configuration, intermediate]
difficulty: intermediate
module: "33 - Information Disclosure"
topic: "33.04 Source Code Disclosure"
---

# Source Code Disclosure

## 1. Executive Summary and Definition

Source Code Disclosure is a critical vulnerability that occurs when a web application or its underlying infrastructure inadvertently exposes its backend source code to end users. Unlike client-side source code (HTML, CSS, JavaScript) which is designed to be downloaded and rendered by the browser, server-side source code (PHP, Python, Java, C#, Ruby, Go) contains the core business logic, database queries, proprietary algorithms, and often hardcoded sensitive information such as credentials or API keys. When an attacker gains access to this code, the security posture of the application shifts from "black box" to "white box," exponentially increasing the likelihood of identifying and exploiting further, more severe vulnerabilities.

This disclosure typically stems from misconfigurations in the web server, improper handling of backup or temporary files, unhandled exceptions that dump stack traces with code snippets, or secondary vulnerabilities like Local File Inclusion (LFI) or Path Traversal. 

Understanding the root cause of source code disclosure requires a deep dive into the mechanics of how web servers process requests and differentiate between static assets (which are served directly) and dynamic scripts (which are executed, and only their output is served).

## 2. Root Causes and Technical Deep Dive

### 2.1 Web Server Handler Misconfigurations

Web servers like Apache and Nginx rely on specific configurations to determine how to handle incoming requests for various file types. For dynamic languages like PHP, Python, or Ruby, the web server must be configured to pass the file to an interpreter (e.g., PHP-FPM, uWSGI, Passenger) rather than serving its contents as plain text.

#### Apache HTTP Server Misconfigurations
In Apache, handlers or `AddType` directives map file extensions to processing modules. If these mappings are lost due to a configuration error or an override in a `.htaccess` file, Apache will fall back to its default behavior: serving the file as `text/plain`.

```apache
# Incorrect or missing mapping
# If the following line is commented out or missing, .php files are served as text.
# AddType application/x-httpd-php .php
```

Another common scenario involves multiple file extensions. If an attacker uploads a file named `shell.php.jpg`, and the web server is configured with a flawed regex or evaluates extensions from right-to-left improperly, it might bypass upload filters but still be executed—or conversely, legitimate code files might be served as plain text.

#### Nginx Misconfigurations
Nginx uses `location` blocks to match URI patterns and proxy requests to backend application servers via FastCGI, uWSGI, or proxy_pass. If a location block is misconfigured, or if it lacks the proper `fastcgi_pass` directive for certain extensions, Nginx will simply read the file from the document root and transmit it to the client.

```nginx
# Vulnerable Configuration
server {
    listen 80;
    server_name example.com;
    root /var/www/html;

    # The following block correctly executes .php files
    location ~ \.php$ {
        fastcgi_pass unix:/var/run/php/php7.4-fpm.sock;
        include fastcgi_params;
        fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;
    }

    # However, .inc or .phps files are not handled!
    # If the application uses database.inc to store credentials, requesting
    # https://example.com/database.inc will download the file as plaintext.
}
```

### 2.2 Backup, Temporary, and Uncompressed Files

Text editors and IDEs frequently create temporary or backup files while a developer is editing code on a live server (a practice that violates deployment best practices but remains extremely common).
- **Vim Swap Files:** Vim creates `.swp`, `.swo`, and `.swn` files. If a developer edits `config.php`, vim creates `.config.php.swp`.
- **Emacs and Nano Backups:** These editors often append a tilde (`~`) or `.save` to the filename (e.g., `config.php~` or `config.php.save`).
- **Legacy Backups:** Developers manually backing up files before making changes often create files like `index.php.bak`, `index.php.old`, `index.php.2023`, `index.txt`, or `Copy of index.php`.

Because the web server is strictly configured to execute `.php` files, it will not recognize `.bak` or `~` as executable scripts. It will therefore serve them as static files, resulting in a full source code disclosure.

### 2.3 Local File Inclusion (LFI) and Path Traversal

Source code disclosure is often the direct result of an LFI vulnerability. In languages like PHP, the `include()`, `require()`, or `file_get_contents()` functions might take user-controlled input. While attackers typically use LFI to read `/etc/passwd`, they can also use it to read application source code.

For PHP specifically, attackers use PHP wrappers to extract source code. If they simply include a PHP file via LFI, the file will be executed by the server, and only the output will be returned. By using the `php://filter` wrapper and base64 encoding the stream, the file contents are treated as a string and returned without execution.

**Payload Example:**
```http
GET /index.php?page=php://filter/convert.base64-encode/resource=login.php HTTP/1.1
Host: target.com
```
The server returns a base64 string. When decoded, this string contains the exact, unexecuted PHP source code of `login.php`.

### 2.4 Diagnostic and Debugging Endpoints

Development frameworks provide robust debugging tools that, if left enabled in production, can expose source code.
- **Werkzeug/Flask Debugger:** Exposes an interactive console and displays highly detailed stack traces that include snippets of the Python source code surrounding the exception.
- **Spring Boot Actuators:** The `/actuator/env` or `/actuator/heapdump` endpoints can expose configurations and memory contents, which often include application source code or raw configurations.
- **Node.js/Express:** Unhandled promise rejections or misconfigured error middleware can dump stack traces to the HTTP response.

## 3. Visual Attack Flow Diagram

```ascii
+-------------------+                                      +-------------------------+
|                   |   1. Requests backup file            |                         |
|   Attacker        |------------------------------------->|      Web Server         |
|   (Web Browser/   |   GET /config.php.bak HTTP/1.1       |  (Apache / Nginx)       |
|    Burp Suite)    |                                      |                         |
|                   |<-------------------------------------|                         |
+-------------------+   2. Returns application/x-trash     +-------------------------+
        |                  (Unexecuted PHP source code)                 |
        |                                                               |
        |                                                               |
        v                                                               v
+-------------------+                                      +-------------------------+
|                   |   3. Extracts DB Credentials         |                         |
|   Local Analysis  |      from config.php.bak             |   Backend Database      |
|                   |------------------------------------->|   (MySQL/PostgreSQL)    |
|                   |   4. Connects to DB remotely         |                         |
+-------------------+   using stolen credentials           +-------------------------+
```

## 4. Exploitation and Tooling

### 4.1 Reconnaissance and Discovery
Attackers use automated directory brute-forcing tools to hunt for backup extensions and temporary files.

**Using ffuf to find backup extensions:**
```bash
ffuf -w /path/to/wordlist/raft-small-words.txt -u http://target.com/FUZZ.php.bak
ffuf -w /path/to/wordlist/raft-small-words.txt -u http://target.com/FUZZ.php~
```

**Common Extensions to Fuzz:**
- `.bak`, `.old`, `.save`, `.txt`, `.tmp`, `.swp`, `~`
- `.zip`, `.tar.gz`, `.rar` (often developers zip the webroot as a backup: `www.zip`, `html.tar.gz`, `backup.zip`)

### 4.2 Exploiting PHP Wrappers via LFI
Once an LFI is confirmed, attackers use automated scripts to dump the entire source code repository file by file. Tools like `LFISuite` or custom Python scripts will iteratively request:
```
?page=php://filter/read=convert.base64-encode/resource=index.php
?page=php://filter/read=convert.base64-encode/resource=includes/db.php
?page=php://filter/read=convert.base64-encode/resource=classes/User.php
```

### 4.3 Exploiting Development Frameworks
If a Flask application is in debug mode and throws an exception, an attacker can access the interactive debugger at `/console`. While a PIN is usually required, the attacker can use arbitrary file read vulnerabilities to calculate the Werkzeug PIN (which relies on predictable system variables like MAC address and machine-id) and execute arbitrary code or read further source files.

## 5. Impact and Risk Assessment

The impact of source code disclosure cannot be overstated. It effectively eliminates the effort required for an attacker to understand the application's architecture. 

1. **Exposure of Hardcoded Secrets:** Code often contains hardcoded API keys (AWS, Stripe, SendGrid), database credentials, internal IP addresses, and encryption salts/keys.
2. **Identification of Logic Flaws:** Attackers can analyze the source code for complex business logic vulnerabilities that are nearly impossible to find via black-box testing (e.g., race conditions, complex IDORs, precise parameter manipulation).
3. **Discovery of Hidden Endpoints:** Source code reveals unlisted administrative endpoints, deprecated APIs, and undocumented parameters.
4. **Bypass of Security Controls:** By reading the exact implementation of input validation, WAF filters, or anti-CSRF token generation, attackers can craft precise payloads to bypass these defenses.

## 6. Remediation and Prevention Strategies

### 6.1 Strict Web Server Configuration
Ensure that the web server correctly denies access to non-essential file extensions.
**Apache (`.htaccess` or `httpd.conf`):**
```apache
<FilesMatch "\.(bak|config|sql|fla|md|ini|log|sh|inc|swp|dist)|~|^\.">
    Order allow,deny
    Deny from all
    Satisfy All
</FilesMatch>
```

**Nginx (`nginx.conf`):**
```nginx
# Deny access to backup extensions & hidden files
location ~* (\.bak|\.config|\.sql|\.fla|\.md|\.ini|\.log|\.sh|\.inc|\.swp|\.dist)|~|^\. {
    deny all;
    access_log off;
    log_not_found off;
}
```

### 6.2 Secure Deployment Practices
- **Never edit files on production:** Eliminate the use of Vim, Nano, or Emacs directly on the web server. Use proper CI/CD pipelines (e.g., GitHub Actions, Jenkins) to deploy code.
- **Clean up artifacts:** Ensure deployment scripts delete temporary files, build artifacts, and hidden directories (like `.git` or `.svn`) before moving the code to the document root.
- **Move logic outside the webroot:** Web applications should only expose a single entry point (e.g., `index.php` or `app.js`) to the webroot (`/var/www/html/public`). All libraries, configurations, and core logic should reside one directory level up (`/var/www/html/src`), completely inaccessible directly via HTTP.

### 6.3 Disable Debug Modes
Ensure that framework debug modes are strictly disabled in production environments.
- **Django:** `DEBUG = False`
- **Flask:** `app.run(debug=False)`
- **Express.js:** Set `NODE_ENV=production`

## 7. Chaining Opportunities

- **Source Code Disclosure -> SQL Injection:** By reading the source code, an attacker might find a database query that uses unsafe string concatenation instead of parameterized queries. They can then exploit this SQLi with exact knowledge of the database schema.
- **Source Code Disclosure -> Remote Code Execution (RCE):** Discovering an insecure use of `eval()`, `exec()`, or insecure deserialization in the code allows the attacker to achieve RCE.
- **Source Code Disclosure -> Privilege Escalation:** Hardcoded JWT secrets or password salts found in the source code can be used to forge administrative tokens or crack password hashes.

## 8. Related Notes

- [[01 - Local File Inclusion (LFI)]]
- [[05 - .git Directory Exposed]]
- [[06 - .env File Exposed]]
- [[08 - Hardcoded Credentials]]
- [[02 - Path Traversal]]
