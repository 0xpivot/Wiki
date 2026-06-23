---
course: API Security
topic: File Path Traversal
tags: [api-security]
---

## File Path Traversal Vulnerabilities in APIs

### Introduction

File path traversal vulnerabilities occur when user-supplied input is used to access files on a server in an unsafe manner. This type of vulnerability can allow attackers to read or write arbitrary files on the server, potentially leading to unauthorized access to sensitive information or even remote code execution. In the context of APIs, these vulnerabilities often arise due to improper validation or sanitization of user input used to construct file paths.

### Background Concepts

#### What is File Path Traversal?

File path traversal, also known as directory traversal, is a type of web application vulnerability that allows an attacker to access restricted files and directories on a web server. This is achieved by manipulating the input parameters that are used to reference files. By using special characters like `../` (dot-dot-slash), an attacker can navigate up the directory tree and access files outside of the intended directory.

#### Why Does It Matter?

File path traversal vulnerabilities can lead to severe security issues:

- **Unauthorized Access**: Attackers can access sensitive files such as configuration files, database backups, or source code.
- **Data Leakage**: Confidential information can be leaked, leading to privacy violations and potential legal consequences.
- **Remote Code Execution**: In some cases, attackers can execute arbitrary code on the server by accessing and modifying specific files.

### How Does It Work?

#### User-Controlled Input

In many web applications, user input is used to construct file paths. For example, consider an API endpoint that serves files based on a user-provided filename:

```http
GET /api/files?filename=example.txt
```

If the server constructs the file path using the provided filename without proper validation, an attacker can manipulate the input to traverse directories:

```http
GET /api/files?filename=../../../../etc/passwd
```

This request attempts to access the `/etc/passwd` file, which contains user account information on Unix-based systems.

#### Example Scenario

Let's consider a simple API endpoint that reads a file based on a user-provided filename:

```python
import os

def read_file(filename):
    file_path = os.path.join("/var/www/html", filename)
    with open(file_path, "r") as f:
        return f.read()

# Example usage
print(read_file("example.txt"))
```

If an attacker provides a malicious filename, they can bypass the intended directory and access other files on the server:

```python
# Malicious input
print(read_file("../../etc/passwd"))
```

### Real-World Examples

#### Recent CVEs and Breaches

Several high-profile breaches have been attributed to file path traversal vulnerabilities:

- **CVE-2021-3129**: A vulnerability in the Apache Struts framework allowed attackers to execute arbitrary commands by exploiting a file path traversal flaw.
- **CVE-2020-13952**: A vulnerability in the Jenkins CI/CD platform allowed attackers to read arbitrary files by manipulating the `scriptPath` parameter.

These examples highlight the severity of file path traversal vulnerabilities and the importance of securing APIs against such attacks.

### Detection and Prevention

#### How to Detect

To detect file path traversal vulnerabilities, you can perform the following steps:

1. **Static Analysis**: Use static analysis tools to scan your codebase for potential vulnerabilities.
2. **Dynamic Analysis**: Perform dynamic analysis by testing your API endpoints with various input values to see if they can be exploited.
3. **Automated Scanning**: Use automated scanning tools like Burp Suite, OWASP ZAP, or commercial solutions to identify potential vulnerabilities.

#### How to Prevent

To prevent file path traversal vulnerabilities, follow these best practices:

1. **Input Validation**: Validate and sanitize all user inputs that are used to construct file paths.
2. **Whitelist Filenames**: Use a whitelist approach to restrict the filenames that can be accessed.
3. **Canonicalize Paths**: Use functions that canonicalize paths to ensure that relative paths are resolved correctly.
4. **Use Safe Libraries**: Utilize libraries that handle file path construction securely.

### Secure Coding Practices

#### Vulnerable Code Example

Consider the following vulnerable code snippet:

```python
import os

def read_file_vulnerable(filename):
    file_path = os.path.join("/var/www/html", filename)
    with open(file_path, "r") as f:
        return f.read()

# Example usage
print(read_file_vulnerable("example.txt"))
```

An attacker can exploit this function by providing a malicious filename:

```python
print(read_file_vulnerable("../../etc/passwd"))
```

#### Secure Code Example

To secure the code, validate the input and use a whitelist approach:

```python
import os

def read_file_secure(filename):
    allowed_files = ["example.txt", "anotherfile.txt"]
    if filename not in allowed_files:
        raise ValueError("Invalid filename")
    file_path = os.path.join("/var/www/html", filename)
    with open(file_path, "r") as f:
        return f.read()

# Example usage
print(read_file_secure("example.txt"))
```

### Configuration Hardening

#### Secure Configuration Example

Ensure that your server configurations are hardened to prevent unauthorized access:

```nginx
server {
    listen 80;
    server_name example.com;

    location /api/files {
        root /var/www/html;
        internal;  # Restrict access to internal requests only
    }
}
```

### Hands-On Practice

For hands-on practice with file path traversal vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice detecting and preventing file path traversal vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including file path traversal.

### Conclusion

File path traversal vulnerabilities are a serious threat to the security of web applications and APIs. By understanding the underlying mechanisms and implementing robust security measures, developers can significantly reduce the risk of such vulnerabilities. Always validate and sanitize user inputs, use whitelisting techniques, and ensure that your server configurations are hardened to prevent unauthorized access.

---
<!-- nav -->
[[API Security/15-File Path Traversal/01-Background Concept API Perspective/00-Overview|Overview]] | [[API Security/15-File Path Traversal/01-Background Concept API Perspective/02-File Path Traversal|File Path Traversal]]
