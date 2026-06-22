---
course: API Security
topic: File Path Traversal
tags: [api-security]
---

## Introduction to File Path Traversal

File Path Traversal, also known as Directory Traversal, is a type of web application vulnerability that allows attackers to access restricted files and directories on a server. This vulnerability occurs when an application uses user-supplied input to construct a file path without proper validation or sanitization. Attackers can manipulate the input to traverse the directory structure and access sensitive files such as configuration files, source code, or other critical data.

### Why Does File Path Traversal Matter?

Understanding and preventing File Path Traversal is crucial because it can lead to unauthorized access to sensitive information, which can result in data breaches, loss of intellectual property, and potential legal ramifications. This vulnerability is particularly dangerous in environments where sensitive data is stored on the same server as the web application.

### How Does File Path Traversal Work?

In a typical scenario, a web application might allow users to download files from a specific directory. The application constructs the file path using user input, such as a filename or a directory name. If the application does not properly validate or sanitize this input, an attacker can manipulate it to traverse the directory structure and access files outside the intended directory.

For example, consider an API endpoint that allows users to download files based on a provided filename:

```http
GET /api/download?filename=example.txt
```

If the application constructs the file path using the `filename` parameter without proper validation, an attacker can manipulate the input to access other files on the server. For instance:

```http
GET /api/download?filename=../../../../etc/passwd
```

This request attempts to access the `/etc/passwd` file, which contains user account information on Unix-based systems.

### Real-World Examples

#### CVE-2021-21972: Apache Struts Path Traversal Vulnerability

Apache Struts is a popular Java framework used for building web applications. In 2021, a vulnerability (CVE-2021-21972) was discovered in Apache Struts that allowed attackers to exploit File Path Traversal. The vulnerability was present in the `Content-Type` header, which could be manipulated to access arbitrary files on the server.

**Impact**: This vulnerability could lead to unauthorized access to sensitive files, potentially exposing confidential data.

**Example Exploit**:

```http
POST /struts2-showcase/orders/createOrder.action HTTP/1.1
Host: target.example.com
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="../../../../etc/passwd"
Content-Type: application/octet-stream

<file content>
```

In this example, the attacker uses the `Content-Disposition` header to specify a filename that traverses the directory structure and accesses the `/etc/passwd` file.

### Background Theory

To understand File Path Traversal, it is essential to grasp the basics of file paths and directory structures. In most operating systems, file paths are represented using forward slashes (`/`) or backslashes (`\`). These paths can be absolute (starting from the root directory) or relative (starting from the current working directory).

#### Absolute Paths

An absolute path starts from the root directory and specifies the complete path to a file or directory. For example:

- On Unix-based systems: `/var/log/syslog`
- On Windows systems: `C:\Windows\System32\cmd.exe`

#### Relative Paths

A relative path is specified relative to the current working directory. For example:

- `../logs/syslog`: Moves up one directory level and then accesses the `syslog` file in the `logs` directory.
- `./config/settings.ini`: Accesses the `settings.ini` file in the current directory.

### Common Pitfalls

When developing web applications, developers often overlook the importance of validating and sanitizing user input. Here are some common pitfalls that can lead to File Path Traversal vulnerabilities:

1. **Insufficient Input Validation**: Failing to validate user input against a whitelist of allowed characters and patterns.
2. **Improper Sanitization**: Not properly sanitizing user input to remove or encode special characters that can be used to manipulate file paths.
3. **Absolute Path Construction**: Constructing file paths using absolute paths without proper validation, allowing attackers to traverse the directory structure.
4. **Relative Path Construction**: Using relative paths without ensuring that the current working directory is set to a safe location.

### Demonstrating File Path Traversal

Let's demonstrate how File Path Traversal can occur in an API. Consider an API endpoint that allows users to download files based on a provided filename:

```http
GET /api/download?filename=example.txt
```

The backend code might look something like this:

```python
import os

def download_file(filename):
    file_path = os.path.join("/app/files", filename)
    if os.path.exists(file_path):
        return open(file_path, "rb").read()
    else:
        return "File not found"

# Example usage
print(download_file("example.txt"))
```

In this example, the `download_file` function constructs the file path using the `os.path.join` method, which combines the base directory (`/app/files`) with the user-provided filename. However, if the user provides a filename that includes directory traversal sequences, the function will attempt to access files outside the intended directory.

#### Exploiting the Vulnerability

An attacker can exploit this vulnerability by providing a filename that includes directory traversal sequences:

```http
GET /api/download?filename=../../../../etc/passwd
```

This request attempts to access the `/etc/passwd` file, which contains user account information on Unix-based systems.

### How to Prevent / Defend Against File Path Traversal

Preventing File Path Traversal requires a combination of input validation, sanitization, and proper handling of file paths. Here are some best practices to defend against this vulnerability:

1. **Input Validation**: Validate user input against a whitelist of allowed characters and patterns. Ensure that filenames do not contain directory traversal sequences.
2. **Sanitization**: Sanitize user input to remove or encode special characters that can be used to manipulate file paths.
3. **Use Whitelisting**: Use a whitelist of allowed filenames or directories to restrict access to specific files or directories.
4. **Canonicalize Paths**: Canonicalize file paths to ensure that they are resolved correctly and do not contain directory traversal sequences.
5. **Limit Permissions**: Limit the permissions of the web application to only the necessary files and directories. Avoid running the application with elevated privileges.

#### Secure Code Example

Here is an example of secure code that validates and sanitizes user input to prevent File Path Traversal:

```python
import os
import re

def download_file(filename):
    # Validate filename against a whitelist of allowed characters
    if not re.match(r'^[a-zA-Z0-9._-]+$', filename):
        return "Invalid filename"

    # Sanitize filename to remove or encode special characters
    sanitized_filename = re.sub(r'[^\w.-]', '', filename)

    # Construct the file path using the sanitized filename
    file_path = os.path.join("/app/files", sanitized_filename)

    # Canonicalize the file path to ensure it is resolved correctly
    canonicalized_path = os.path.realpath(file_path)

    # Check if the canonicalized path is within the allowed directory
    if not canonicalized_path.startswith("/app/files"):
        return "Access denied"

    # Check if the file exists and return its contents
    if os.path.exists(canonicalized_path):
        return open(canonicalized_path, "rb").read()
    else:
        return "File not found"

# Example usage
print(download_file("example.txt"))
```

In this example, the `download_file` function first validates the filename against a whitelist of allowed characters. It then sanitizes the filename to remove or encode special characters. The function constructs the file path using the sanitized filename and canonicalizes it to ensure it is resolved correctly. Finally, the function checks if the canonicalized path is within the allowed directory before attempting to access the file.

### Detection and Prevention Tools

Several tools and techniques can help detect and prevent File Path Traversal vulnerabilities:

1. **Static Analysis Tools**: Static analysis tools can scan source code for potential vulnerabilities, including File Path Traversal. Examples include SonarQube, Fortify, and Veracode.
2. **Dynamic Analysis Tools**: Dynamic analysis tools can test web applications for vulnerabilities by simulating attacks. Examples include Burp Suite, OWASP ZAP, and Acunetix.
3. **Web Application Firewalls (WAF)**: WAFs can help protect web applications by filtering out malicious requests. Examples include ModSecurity, AWS WAF, and Cloudflare WAF.
4. **Secure Coding Practices**: Following secure coding practices, such as input validation, sanitization, and proper handling of file paths, can help prevent File Path Traversal vulnerabilities.

### Practice Labs

To gain hands-on experience with File Path Traversal, consider the following practice labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various web security topics, including File Path Traversal.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates common web application vulnerabilities.
- **WebGoat**: An interactive training application designed to teach web application security lessons.

These labs provide a controlled environment to practice identifying and exploiting File Path Traversal vulnerabilities, as well as learning how to defend against them.

### Conclusion

File Path Traversal is a serious web application vulnerability that can lead to unauthorized access to sensitive files and data. Understanding how this vulnerability works, its real-world implications, and how to prevent it is crucial for securing web applications. By following best practices, using secure coding techniques, and leveraging detection and prevention tools, developers can effectively mitigate the risk of File Path Traversal vulnerabilities.

---
<!-- nav -->
[[API Security/15-File Path Traversal/02-Path Traversal Demonstration/00-Overview|Overview]] | [[API Security/15-File Path Traversal/02-Path Traversal Demonstration/02-File Path Traversal|File Path Traversal]]
