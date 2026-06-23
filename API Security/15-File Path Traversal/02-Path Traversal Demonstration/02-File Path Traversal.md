---
course: API Security
topic: File Path Traversal
tags: [api-security]
---

## File Path Traversal

### Introduction

File Path Traversal, also known as Directory Traversal, is a type of web application vulnerability that allows an attacker to access files and directories that are stored outside the web root directory. This can lead to unauthorized access to sensitive information such as configuration files, source code, and even system files like `/etc/passwd` or `/etc/shadow`. The vulnerability arises due to improper input validation and sanitization of user-supplied input used to reference files.

### Understanding the Vulnerability

#### What is File Path Traversal?

File Path Traversal occurs when an application uses untrusted input to construct a file path without proper validation. An attacker can manipulate the input to traverse the file system hierarchy and access arbitrary files. This can be achieved using special characters such as `../`, `%2E%2E%2F`, or other URL-encoded sequences.

#### Why Does It Matter?

The primary concern with File Path Traversal is the potential exposure of sensitive data. Attackers can exploit this vulnerability to gain access to critical system files, which may contain passwords, private keys, or other confidential information. This can lead to further attacks such as privilege escalation or denial of service.

### How It Works Under the Hood

#### Example Scenario

Consider a web application that allows users to download files from a specific directory. The application constructs the file path based on user input:

```python
def download_file(filename):
    file_path = f"/var/www/uploads/{filename}"
    with open(file_path, 'rb') as file:
        return file.read()
```

If an attacker provides a specially crafted filename such as `../../../../etc/passwd`, the application will attempt to read the `/etc/passwd` file instead of a file within the intended directory.

#### URL Encoding

Attackers often use URL encoding to bypass simple input validation checks. For example, `../` can be encoded as `%2E%2E%2F`.

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2021-3184**: A File Path Traversal vulnerability was found in the Apache Struts framework. Attackers could exploit this to read arbitrary files on the server.
- **CVE-2022-22965**: A vulnerability in the Log4j library allowed attackers to execute arbitrary code and potentially read sensitive files through File Path Traversal.

### Detailed Exploit Example

#### Step-by-Step Mechanics

Let's walk through a detailed example of how an attacker might exploit a File Path Traversal vulnerability.

1. **Identify the Vulnerable Endpoint**:
   The attacker identifies an endpoint that accepts user input to reference a file, such as `/download?file=example.txt`.

2. **Craft the Malicious Input**:
   The attacker crafts a malicious input to traverse the file system. For instance, `../../../../etc/passwd`.

3. **Send the Request**:
   The attacker sends the following HTTP request:

   ```http
   GET /download?file=../../../../etc/passwd HTTP/1.1
   Host: vulnerable.example.com
   ```

4. **Receive the Response**:
   If the application is vulnerable, it will respond with the contents of the `/etc/passwd` file:

   ```http
   HTTP/1.1 200 OK
   Content-Type: text/plain
   Content-Length: 1024

   root:x:0:0:root:/root:/bin/bash
   daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
   bin:x:2:2:bin:/bin:/usr/sbin/nologin
   ...
   ```

### Common Pitfalls and Mistakes

#### Improper Input Validation

One of the most common mistakes is failing to properly validate and sanitize user input. Applications should ensure that input does not contain characters or sequences that can be used to traverse the file system.

#### Lack of Proper Error Handling

Applications often fail to handle errors gracefully. If an invalid file path is provided, the application should return a generic error message rather than revealing sensitive information.

### How to Prevent / Defend

#### Detection

To detect File Path Traversal vulnerabilities, you can use automated tools such as static analysis tools (e.g., SonarQube, Fortify) and dynamic analysis tools (e.g., Burp Suite, OWASP ZAP).

#### Prevention

1. **Input Validation**:
   Validate and sanitize all user-supplied input to ensure it does not contain characters or sequences that can be used to traverse the file system.

2. **Whitelist Filenames**:
   Use a whitelist of allowed filenames and directories. Only allow access to files within a predefined set of directories.

3. **Use Safe Libraries**:
   Utilize libraries and frameworks that provide safe methods for handling file paths. For example, in Python, use the `pathlib` module.

4. **Error Handling**:
   Implement proper error handling to avoid revealing sensitive information. Return generic error messages when an invalid file path is provided.

#### Secure Coding Fixes

Here is an example of how to securely handle file paths in Python:

```python
from pathlib import Path

def download_file(filename):
    base_dir = Path("/var/www/uploads")
    file_path = base_dir / filename
    if file_path.is_relative_to(base_dir):
        with open(file_path, 'rb') as file:
            return file.read()
    else:
        raise ValueError("Invalid file path")
```

#### Configuration Hardening

Ensure that your web server and application server configurations are hardened to prevent unauthorized access. For example, in Nginx, you can configure the `autoindex` directive to disable directory listing:

```nginx
server {
    listen 80;
    server_name example.com;

    location /uploads/ {
        autoindex off;
        alias /var/www/uploads/;
    }
}
```

### Complete Example with Request, Response, and Result

#### Vulnerable Code

```python
def download_file(filename):
    file_path = f"/var/www/uploads/{filename}"
    with open(file_path, 'rb') as file:
        return file.read()
```

#### HTTP Request

```http
GET /download?file=../../../../etc/passwd HTTP/1.1
Host: vulnerable.example.com
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Content-Type: text/plain
Content-Length: 1024

root:x:0:0:root:/root:/bin/bash
daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
bin:x:2:2:bin:/bin:/usr/sbin/nologin
...
```

#### Secure Code

```python
from pathlib import Path

def download_file(filename):
    base_dir = Path("/var/www/uploads")
    file_path = base_dir / filename
    if file_path.is_relative_to(base_dir):
        with open(file_path, 'rb') as file:
            return file.read()
    else:
        raise ValueError("Invalid file path")
```

#### HTTP Request

```http
GET /download?file=../../../../etc/passwd HTTP/1.1
Host: secure.example.com
```

#### HTTP Response

```http
HTTP/1.1 400 Bad Request
Content-Type: text/plain
Content-Length: 20

Invalid file path
```

### Practice Labs

For hands-on practice with File Path Traversal, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice exploiting and defending against File Path Traversal.
- **OWASP Juice Shop**: A deliberately insecure web application for learning about various security vulnerabilities, including File Path Traversal.
- **DVWA (Damn Vulnerable Web Application)**: Provides a variety of web application vulnerabilities, including File Path Traversal, for educational purposes.

### Conclusion

File Path Traversal is a serious vulnerability that can lead to unauthorized access to sensitive information. By understanding the mechanics of the vulnerability, recognizing common pitfalls, and implementing robust preventive measures, you can significantly reduce the risk of exploitation. Always ensure that user input is properly validated and sanitized, and use secure coding practices to protect your applications from File Path Traversal attacks.

---
<!-- nav -->
[[01-Introduction to File Path Traversal|Introduction to File Path Traversal]] | [[API Security/15-File Path Traversal/02-Path Traversal Demonstration/00-Overview|Overview]] | [[API Security/15-File Path Traversal/02-Path Traversal Demonstration/03-Practice Questions & Answers|Practice Questions & Answers]]
