---
tags: [interview, web-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Web Security"
topic: "QnA - Web Module 12"
---

# Web QnA - Module 12 - Directory Traversal and File Uploads

## Custom ASCII Diagram

```text
    [Attacker]
        |
        |  1. Uploads malicious file (shell.php.jpg)
        |     Bypasses extension filter via Null Byte (%00)
        v
    [Web Server] -- Directory Traversal: ../../../var/www/uploads/
        |
        |  2. File stored on disk with executable permissions
        v
    [Local File System]
        |  /var/www/html/images/shell.php
        |
        |  3. Attacker requests /images/shell.php?cmd=whoami
        v
    [RCE Execution Context] -> returns "www-data"
```

## Real-World Attack Scenario

You are on a Red Team engagement assessing an enterprise Content Management System (CMS). The CMS has a feature allowing administrators to upload custom profile pictures. The application employs strict client-side and server-side validation: it checks the `Content-Type` header, verifies the magic bytes of the file, and restricts extensions to `.jpg` and `.png`.

However, during your analysis, you observe that the "filename" parameter in the multipart form-data is directly concatenated into the file path used for storage without proper sanitization. You craft a malicious PHP payload, give it valid JPEG magic bytes at the beginning, and name the file `../../../var/www/html/shell.php`.

The server-side validation passes because the magic bytes match a JPEG. But when the application saves the file, the directory traversal payload in the filename forces the OS to write the file directly into the web root `/var/www/html/` instead of the isolated `/uploads/` directory. By requesting the newly created `shell.php`, you achieve full Remote Code Execution (RCE) on the web server, completely circumventing the intended file upload restrictions.

## Chaining Opportunities

1. **File Upload + Directory Traversal:** Storing uploaded files outside of intended, non-executable directories (e.g., moving a web shell into the `htdocs` or `www` root).
2. **File Upload + XSS (Stored):** Uploading an SVG file containing malicious `<script>` tags. When a victim views the image directly, the browser executes the payload.
3. **Directory Traversal + LFI to RCE:** Using directory traversal to read sensitive log files, then poisoning those logs via User-Agent manipulation to execute injected PHP code.
4. **File Upload + XXE:** Uploading malicious DOCX or SVG files that contain XML External Entity payloads, leading to internal SSRF or local file read upon server-side parsing.
5. **Path Traversal + Local Privilege Escalation:** Overwriting sensitive system files (e.g., SSH authorized_keys) if the web server is running with overly permissive privileges.

## Related Notes

- [[02 - Input Validation and Sanitization]]
- [[07 - Local File Inclusion LFI]]
- [[10 - Remote Code Execution RCE]]
- [[14 - Bypassing Antivirus and EDR]]
- [[19 - Secure Coding Practices in PHP]]

---

## Formal Technical Questions

### Q1: Explain the difference between Local File Inclusion (LFI) and Directory (Path) Traversal.

**Answer:**
While both vulnerabilities involve manipulating file paths, their impacts and mechanisms differ significantly:
- **Directory Traversal (Path Traversal):** This vulnerability allows an attacker to read arbitrary files on the server that is running the application. The application simply reads the contents of the file and returns it in the HTTP response. It does not execute the file. The goal is data exfiltration (e.g., reading `/etc/passwd` or application source code).
- **Local File Inclusion (LFI):** This vulnerability occurs when an application includes a file as part of its execution context (e.g., using `include()`, `require()` in PHP). If an attacker can control the file path, the server will not just read the file, but will parse and execute its contents. This allows attackers to achieve Remote Code Execution (RCE) by including files containing malicious code (like poisoned logs or uploaded shells).

### Q2: What are "Magic Bytes" (File Signatures), and why is relying on them insufficient for securing file uploads?

**Answer:**
"Magic Bytes" are the first few bytes of a file that identify its true content type, regardless of its extension. For example, a JPEG file always starts with `FF D8 FF E0`.

Relying solely on magic byte validation is insufficient because an attacker can easily spoof them. An attacker can create a valid PHP script and simply prepend the magic bytes of a JPEG (`\xFF\xD8\xFF\xE0`) to the beginning of the file. 

If the server validates the file based on these magic bytes, it will incorrectly classify the malicious PHP script as a safe image and allow the upload. If this file is later accessed and executed by the web server (e.g., if the extension was not properly stripped or if chained with an LFI), the server will execute the PHP code that follows the magic bytes, leading to system compromise.

---

## Scenario-Based Questions

### Q3: You are on a Red Team engagement. You find a file upload mechanism that strictly validates the file extension against a whitelist (e.g., only `.jpg`, `.png`). How would you attempt to bypass this whitelist to upload a web shell?

**Answer:**
Bypassing strict extension whitelists requires finding discrepancies in how the application, the web server, or the operating system parses file extensions. I would attempt the following techniques:

1. **Null Byte Injection (`%00`):** In older C-based backends, a null byte terminates a string. Uploading `shell.php%00.jpg` might pass the `.jpg` check, but the OS writes it as `shell.php`.
2. **Double Extensions:** If the web server (like Apache) is misconfigured, it might execute files based on the first recognized extension. Uploading `shell.php.jpg` might result in execution if the server processes the `.php` directive.
3. **Alternate Executable Extensions:** The whitelist might miss obscure executable extensions. For PHP, I would try `.php3`, `.php4`, `.php5`, `.phtml`, `.phar`, or `.inc`.
4. **Overwriting Configuration Files:** If directory traversal is possible, I would upload a `.htaccess` file (for Apache) or `web.config` (for IIS) to alter the directory's configuration. For example, a custom `.htaccess` could instruct the server to execute `.jpg` files as PHP.
5. **Path Overlap:** Exploiting URL encoding or trailing characters like `shell.php.` or `shell.php ` (with a trailing space). Windows OS often strips trailing dots and spaces during file creation.

### Q4: During an assessment, you discover a directory traversal vulnerability that allows you to read files: `GET /download?file=../../../etc/passwd`. However, the server implements a regex filter that strips `../` from the input. How do you bypass this?

**Answer:**
If the application uses a simplistic, non-recursive filter to strip `../`, there are several bypass techniques:

1. **Nested Traversal Sequences:** I would use `....//` or `..././`. When the filter strips the `../`, the remaining characters collapse to form a new, valid `../` sequence. For example, `....//etc/passwd` becomes `../../etc/passwd` after one pass of the filter.
2. **URL Encoding:** The WAF or filter might execute before the application decodes the input. I would URL encode the sequence: `%2e%2e%2f` (for `../`).
3. **Double URL Encoding:** If the application decodes input twice, I can bypass filters that only decode once. `../` becomes `%252e%252e%252f`.
4. **Unicode/UTF-8 Encoding:** Using overlong UTF-8 encodings or Unicode representations like `..%c0%af` or `..%ef%bc%8f`.
5. **Absolute Paths:** Bypassing traversal entirely by providing the direct absolute path, such as `/etc/passwd`, assuming the application code appends the input to a base directory but fails to restrict absolute paths.

---

## Deep-Dive Defensive Questions

### Q5: As an Application Security Architect, outline a comprehensive, defense-in-depth strategy for handling user-uploaded files securely.

**Answer:**
A defense-in-depth strategy for file uploads must ensure that even if one control fails, others prevent exploitation.

1. **Storage Isolation:** Never store uploaded files in the web root. Store them in an isolated directory, on a separate partition, or ideally, in a cloud storage bucket (like AWS S3) that lacks execution capabilities.
2. **Filename Randomization:** Never trust the user-provided filename. Rename all uploaded files to a randomly generated string (e.g., UUID) to prevent directory traversal and file overwriting attacks.
3. **Strict Whitelisting:** Implement strict server-side validation for both file extensions and Content-Type headers against a hardcoded whitelist of allowed types.
4. **Content Validation and Stripping:** Do not rely solely on magic bytes. Use libraries to actively parse and strip metadata from images (e.g., EXIF data which can house payloads). For critical applications, re-encode images to completely sanitize them.
5. **Disable Execution:** Configure the web server to explicitly deny the execution of scripts in the upload directory. For example, in Apache, disable the PHP engine using `.htaccess` (`php_flag engine off`), or remove executable permissions at the OS level.
6. **Malware Scanning:** Integrate an asynchronous backend process to scan all uploaded files with Anti-Virus or sandboxing solutions before making them available to users.

### Q6: What is a "File Upload Race Condition," and how can it lead to RCE even in systems with robust post-upload malware scanning?

**Answer:**
A File Upload Race Condition occurs when an application temporarily stores an uploaded file on the filesystem before completing its validation, moving, or scanning processes.

In this scenario, the application might save the malicious file (e.g., `shell.php`) to a temporary directory accessible via the web server. It then initiates an Anti-Virus scan or an extension check. If the check fails, the application deletes the file. 

However, there is a small time window (the "race window") between the file being written to disk and it being deleted. An attacker can exploit this by continuously uploading the malicious file while simultaneously sending automated HTTP requests to execute it. If the execution request hits the server exactly during that split-second race window, the web shell executes before the server can delete it, resulting in full Remote Code Execution.

To defend against this, files must be uploaded to memory or a completely inaccessible quarantine directory, and only moved to a web-accessible location *after* all validation and scanning processes have successfully completed.
