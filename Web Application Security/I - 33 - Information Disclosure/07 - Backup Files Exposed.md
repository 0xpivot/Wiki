---
tags: [vapt, information-disclosure, reconnaissance, backups, beginner]
difficulty: beginner
module: "33 - Information Disclosure"
topic: "33.07 Backup Files Exposed (.bak, .old, .swp)"
---

# 07 - Backup Files Exposed (.bak, .old, .swp)

## Introduction

In the lifecycle of web application development and maintenance, developers and system administrators frequently edit files directly on production servers or create quick, ad-hoc backups before applying patches. This seemingly harmless operational habit is the root cause of Backup File Exposure—a critical subset of Information Disclosure. 

When backup files, editor swap files, or compressed archives are left within the web root, they bypass application-level routing and execution contexts. For example, a web server is configured to execute `.php` files but will serve `.php.bak` or `.php.swp` as plain text. If an attacker discovers these artifacts, they instantly gain access to the raw source code, hardcoded credentials, API keys, database connection strings, and the underlying business logic of the application.

This vulnerability exists at the intersection of poor operational security (OpSec) and misconfigured web server MIME types.

## The Anatomy of a Backup Leak

When a client requests a resource, the web server evaluates the file extension against its configured handlers. Handlers dictate whether a file should be executed (e.g., passed to PHP-FPM or an ASP.NET engine) or served directly to the client as a static asset.

Because custom backup extensions (`.bak`, `.old`, `~`) do not map to executable handlers, the server falls back to its default behavior: serving the file as `application/octet-stream` or `text/plain`.

### ASCII Diagram: Backup File Discovery Architecture

```text
+---------------------+                                       +-----------------------+
|                     |     1. GET /config.php.bak HTTP/1.1   |                       |
|  Attacker /         |  -----------------------------------> |  Web Server (Apache)  |
|  Fuzzer (ffuf)      |                                       |  (Document Root)      |
|                     |     2. 200 OK                         |  - index.php          |
|  Wordlist:          |        Content-Type: text/plain       |  - config.php         |
|  - .bak             |  <----------------------------------- |  - config.php.bak     |
|  - .old             |                                       +-----------------------+
|  - .swp             |        [Source Code Returned]                    |
+---------------------+        <?php                                     |
         |                     $db_pass = "SuperSecret123!";             |
         |                     ...                                       |
         v                                                               |
+---------------------+                                                  |
|                     |     3. Extracts Database Credentials             |
|  Exploitation       |  <-----------------------------------------------+
|  Phase              |
+---------------------+
```

## Common Backup Artifacts and their Signatures

Backup files originate from a variety of sources. Understanding the origin is crucial for tailoring wordlists and discovery techniques.

### 1. Text Editor Artifacts
Many command-line text editors automatically create temporary or backup files to prevent data loss in the event of a crash.

*   **Vim Swap Files (`.swp`, `.swo`, `.swn`):**
    When editing `config.php`, Vim creates a hidden binary swap file named `.config.php.swp`. If Vim crashes or the session is killed, this file remains.
    *Signature:* Vim swap files are binary but start with a known magic byte sequence, often `b0VIM 3.0`.
    *Recovery:* An attacker can download the file and run `vim -r .config.php.swp` locally to reconstruct the unedited file.
*   **Nano Backups (`.save`):**
    If a nano session is abruptly terminated (e.g., SIGHUP), it saves the buffer to `filename.save`.
*   **Emacs Backups (`~`):**
    Emacs appends a tilde (`~`) to the original filename to create a backup, resulting in files like `config.php~`.

### 2. Manual Developer Backups
System administrators often create manual copies before updating critical configuration files. These follow predictable naming patterns.

*   **Extensions:** `.bak`, `.old`, `.orig`, `.test`, `.dev`, `.txt`, `_backup`, `-copy`
*   **Examples:** `database.yml.bak`, `settings.py.old`, `wp-config.php.txt`

### 3. Archive Formats
Occasionally, entire directories are zipped up as a backup. If left in a publicly accessible directory, it results in massive source code disclosure.

*   **Extensions:** `.zip`, `.tar.gz`, `.tgz`, `.7z`, `.rar`, `.bz2`
*   **Examples:** `backup.zip`, `html.tar.gz`, `source.zip`, `site.rar`

## Automated Discovery Techniques

Discovering exposed backups requires aggressive directory and file fuzzing using tools like `ffuf`, `feroxbuster`, or `gobuster`. 

### Advanced Fuzzing with Ffuf

Standard fuzzing might only look for directories. To find backup files, you must use extension fuzzing or specific backup wordlists.

```bash
# Fuzzing a specific file (e.g., config.php) for backup extensions
ffuf -u http://target.com/config.phpFUZZ -w /usr/share/wordlists/SecLists/Discovery/Web-Content/burp-parameter-names.txt -mc 200

# Using specialized SecLists wordlists
ffuf -u http://target.com/FUZZ -w /usr/share/wordlists/SecLists/Discovery/Web-Content/backupfiles.txt -mc 200

# Appending extensions to a known wordlist
ffuf -u http://target.com/FUZZ -w common.txt -e .bak,.old,.swp,.txt,~ -mc 200
```

### Writing Custom Wordlist Generation Scripts

Sometimes, fuzzing tools miss edge cases. A custom script can generate tailored permutations based on known files.

```python
import sys

def generate_permutations(filename):
    extensions = ['.bak', '.old', '.txt', '~', '.orig', '.1', '.save']
    prefixes = ['.', '_', 'copy_of_']
    
    # Base permutations
    for ext in extensions:
        print(f"{filename}{ext}")
        print(f"{filename.split('.')[0]}{ext}")
        
    # Vim specific
    print(f".{filename}.swp")
    print(f".{filename}.swo")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        generate_permutations(sys.argv[1])
```

## Impact Analysis

The impact of exposed backup files is universally severe, often leading to total system compromise. 
1.  **Source Code Disclosure:** Exposes proprietary algorithms, hidden parameters, and hardcoded API endpoints.
2.  **Credential Leakage:** Configuration files (like `wp-config.php`, `.env`, `web.config`) contain database credentials, AWS IAM keys, and third-party API tokens.
3.  **Vulnerability Mapping:** With the source code in hand, attackers can perform white-box code reviews to discover SQL Injection (`[[01 - SQL Injection]]`), Cross-Site Scripting (`[[01 - Cross Site Scripting XSS]]`), or Insecure Direct Object References (`[[01 - IDOR]]`).

## Remediation and Prevention

Preventing backup file exposure requires defense-in-depth strategies spanning web server configuration, developer training, and CI/CD pipeline controls.

### 1. Web Server Blacklisting
Configure the web server to explicitly deny access to known backup extensions, hidden files, and source code repositories (like `.git`).

**Apache (`.htaccess` or `httpd.conf`):**
```apache
<FilesMatch "\.(bak|config|sql|fla|md|sw[op]|save|~)$">
    Require all denied
</FilesMatch>

# Block access to hidden files (e.g., .env, .config.php.swp)
<FilesMatch "^\.">
    Require all denied
</FilesMatch>
```

**Nginx (`nginx.conf`):**
```nginx
# Deny access to hidden files (starts with a dot)
location ~ /\. {
    deny all;
    access_log off;
    log_not_found off;
}

# Deny access to backup and archive files
location ~* \.(bak|old|orig|txt|swp|swo|save|~)$ {
    deny all;
}
```

### 2. Operational Security (OpSec)
*   **Never edit files in production:** All changes should go through a structured version control system (Git) and automated deployment pipelines (CI/CD).
*   **Use ephemeral containers:** Implementing Docker/Kubernetes ensures that the environment is immutable. If a file needs to be patched, a new image is built and deployed. Temporary files never persist.

### 3. Pipeline Scanning
Integrate tools like `trufflehog` or `gitleaks` into the CI/CD pipeline to catch `.env` files or backups before they are deployed to the web root. Ensure the `.gitignore` file strictly prohibits the addition of `*.bak` or `*.swp` files to the repository.

## Chaining Opportunities

Finding an exposed backup file is rarely the end of the attack chain. It acts as an enabler for significantly more critical vulnerabilities.

*   **[[10 - Source Code Disclosure]]:** Exposed backups directly map to source code disclosure, allowing for white-box analysis.
*   **[[01 - SQL Injection]]:** Uncovering backend database queries inside a `.bak` file enables an attacker to craft perfect SQLi payloads without needing to rely on blind error-guessing.
*   **[[01 - Server-Side Request Forgery SSRF]]:** Discovering internal API endpoints and expected JSON payloads inside source code backups simplifies SSRF exploitation.
*   **[[01 - Remote Code Execution]]:** If an attacker leaks the application's secret signing keys (e.g., JWT secrets or Django `SECRET_KEY`), they may be able to forge serialized objects leading to RCE.

## Related Notes
*   [[01 - Introduction to Information Disclosure]]
*   [[08 - Version Disclosure]]
*   [[04 - Directory Traversal]]
*   [[03 - Sensitive Data Exposure]]
*   [[06 - Source Code Management (Git) Disclosure]]

---
*End of Note*
