---
course: Web Security
topic: Directory Traversal
tags: [web-security]
---

## Testing for Directory Traversal Vulnerabilities

Once you have identified the input vectors, the next step is to test them for directory traversal vulnerabilities. This involves fuzzing the input vectors with common directory traversal payloads.

### Directory Traversal Payloads

Directory traversal payloads are crafted inputs designed to navigate the file system and access unauthorized files. These payloads can vary depending on the operating system (Linux, Windows) and the specific application being tested.

#### Example Payloads

Here are some common directory traversal payloads:

- `../../../../etc/passwd`
- `..\..\..\windows\system32\cmd.exe`
- `%2e%2e%2fetc%2fpasswd`
- `../etc/passwd`

These payloads attempt to navigate up the directory tree to access sensitive files such as `/etc/passwd` (Linux) or `C:\Windows\System32\cmd.exe` (Windows).

### Testing Methodology

To test for directory traversal vulnerabilities, follow these steps:

1. **Identify Input Vectors**: Map the application and identify all potential input vectors.
2. **Craft Payloads**: Create a list of directory traversal payloads based on the operating system and application specifics.
3. **Fuzz Input Vectors**: Inject the payloads into the identified input vectors and observe the application's response.
4. **Analyze Results**: Determine if the application successfully retrieves unauthorized files or executes commands.

#### Example: Testing a File Download Endpoint

Suppose we have a file download endpoint `/download?file=<filename>`. To test this endpoint for directory traversal vulnerabilities, we can inject payloads into the `file` parameter.

```http
GET /download?file=../../../../etc/passwd HTTP/1.1
Host: example.com
```

If the application is vulnerable, it might return the contents of `/etc/passwd`.

### Real-World Examples

#### CVE-2021-3520: Apache Struts Directory Traversal

In 2021, a critical vulnerability (CVE-2021-3520) was discovered in Apache Struts, a popular Java web framework. This vulnerability allowed attackers to perform directory traversal attacks and gain unauthorized access to sensitive files.

**Impact**: Attackers could exploit this vulnerability to read arbitrary files on the server, including configuration files and source code.

**Exploit Example**:

```http
POST /struts2-showcase/orders/createOrder.action HTTP/1.1
Host: vulnerable-server.com
Content-Type: application/x-www-form-urlencoded

orderBean.customerName=../../../../etc/passwd&orderBean.product=shirt&orderBean.quantity=1
```

This payload attempts to read the `/etc/passwd` file by exploiting the directory traversal vulnerability.

### How to Prevent / Defend Against Directory Traversal

Preventing directory traversal attacks requires a combination of secure coding practices, proper input validation, and configuration hardening.

#### Secure Coding Practices

1. **Validate User Input**: Ensure that all user-supplied input is validated against a whitelist of allowed characters and patterns.
2. **Use Safe Functions**: Utilize safe functions and libraries that automatically handle directory traversal risks.
3. **Canonicalize Paths**: Convert all paths to their canonical form to prevent traversal attacks.

#### Example: Secure Code Implementation

Here is an example of how to securely handle file uploads in Python:

```python
import os
from werkzeug.utils import secure_filename

def handle_file_upload(file, filename):
    # Validate the filename
    if not secure_filename(filename):
        raise ValueError("Invalid filename")

    # Define the upload directory
    upload_dir = "/path/to/upload/directory"

    # Construct the full path
    full_path = os.path.join(upload_dir, filename)

    # Canonicalize the path
    full_path = os.path.realpath(full_path)

    # Check if the path is within the upload directory
    if not full_path.startswith(upload_dir):
        raise ValueError("Path traversal detected")

    # Save the file
    file.save(full_path)
```

#### Configuration Hardening

1. **Restrict File Permissions**: Ensure that sensitive files and directories have appropriate permissions set to restrict access.
2. **Disable Directory Listing**: Disable directory listing in web servers to prevent attackers from discovering file paths.
3. **Use Web Application Firewalls (WAF)**: Implement WAF rules to detect and block directory traversal attempts.

#### Example: Nginx Configuration

Here is an example of how to configure Nginx to prevent directory traversal:

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        root /var/www/html;
        index index.html;

        # Disable directory listing
        autoindex off;

        # Restrict access to sensitive directories
        location ~* \.(htaccess|htpasswd)$ {
            deny all;
        }
    }
}
```

### Detection Tools

Several tools can help detect directory traversal vulnerabilities:

- **Burp Suite**: A comprehensive toolkit for web application security testing.
- **OWASP ZAP**: An open-source web application security scanner.
- **DirBuster**: A tool for brute-forcing directory and file names.

### Practice Labs

To practice directory traversal testing, consider using the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various web security topics, including directory traversal.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that contains numerous security vulnerabilities.

By thoroughly understanding and implementing these preventive measures, you can significantly reduce the risk of directory traversal attacks on your web applications.

---
<!-- nav -->
[[07-Mapping the Application|Mapping the Application]] | [[Web Security (PortSwigger)/11-Directory Traversal/01-Directory Traversal Complete Guide/00-Overview|Overview]] | [[Web Security (PortSwigger)/11-Directory Traversal/01-Directory Traversal Complete Guide/09-Conclusion|Conclusion]]
