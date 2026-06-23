---
course: Web Security
topic: Directory Traversal
tags: [web-security]
---

## Introduction to Directory Traversal

Directory traversal, also known as path traversal, is a type of web application vulnerability that allows an attacker to access restricted files and directories on a web server. This vulnerability occurs due to improper input validation and handling of user-supplied input in web applications. By manipulating the input, an attacker can traverse the directory structure of the server and gain unauthorized access to sensitive information such as configuration files, source code, and even execute arbitrary commands.

### Background Theory

To understand directory traversal, let's first look at how web servers handle file requests. When a user requests a file from a web server, the server maps the requested URL to a physical file on the server's filesystem. For example, a request for `http://example.com/path/to/file.txt` might map to `/var/www/html/path/to/file.txt` on the server.

However, if the web application does not properly validate the input, an attacker can manipulate the URL to traverse the directory structure. For instance, an attacker might request `http://example.com/../../etc/passwd`, which would map to `/var/www/html/../../etc/passwd`. This request bypasses the intended directory structure and accesses the `/etc/passwd` file, which contains sensitive system information.

### Impact of Directory Traversal

The impact of directory traversal vulnerabilities can be severe:

- **Access to Sensitive Files**: Attackers can read configuration files, source code, and other sensitive data stored on the server.
- **Remote Code Execution**: In some cases, attackers can upload and execute malicious scripts, leading to full control over the server.
- **Data Leakage**: Unauthorized access to sensitive data can lead to data breaches and compliance violations.

### Recent Real-World Examples

#### CVE-2021-3520

In 2021, a directory traversal vulnerability was discovered in the popular web application framework Django. The vulnerability allowed attackers to access arbitrary files on the server by manipulating the `upload_to` parameter in file uploads. This could lead to exposure of sensitive files and potential remote code execution.

```python
# Vulnerable code snippet
def handle_upload(request):
    uploaded_file = request.FILES['file']
    filename = uploaded_file.name
    with open(f'/path/to/uploads/{filename}', 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
```

#### CVE-2022-22965

Another notable example is the directory traversal vulnerability found in the Apache Log4j library. Although primarily known for its remote code execution capabilities, the vulnerability also allowed attackers to read arbitrary files on the server, leading to significant data leakage.

### How to Find Directory Traversal Vulnerabilities

Finding directory traversal vulnerabilities typically involves testing the application for improper input validation and handling. Here are some steps to identify these vulnerabilities:

1. **Identify File Access Points**: Look for parts of the application where files are accessed based on user input, such as file download endpoints or image display functions.
2. **Test Input Validation**: Manipulate the input to see if the application allows traversal of the directory structure. Common techniques include using `../` sequences or null byte (`%00`) injection.
3. **Check for Sensitive Files**: Attempt to access sensitive files such as `/etc/passwd`, `/etc/shadow`, or configuration files.

### Example Exploitation

Let's consider an example where a web application allows users to view images stored on the server. The application uses the following code to serve images:

```python
# Vulnerable code snippet
def serve_image(request, image_name):
    image_path = os.path.join('/path/to/images', image_name)
    return send_file(image_path)
```

An attacker can exploit this by requesting `http://example.com/images/../../etc/passwd`, which would map to `/path/to/images/../../etc/passwd`.

### Detection and Prevention

#### Detection

To detect directory traversal vulnerabilities, you can use automated tools such as:

- **Burp Suite**: A popular web application security testing tool that includes features for detecting directory traversal vulnerabilities.
- **OWASP ZAP**: Another widely used tool for identifying security issues in web applications.

#### Prevention

Preventing directory traversal vulnerabilities involves proper input validation and sanitization. Here are some best practices:

1. **Validate User Input**: Ensure that user-supplied input does not contain directory traversal sequences such as `../`.
2. **Use Whitelisting**: Restrict file access to a predefined set of safe directories and filenames.
3. **Canonicalize Paths**: Normalize paths to their absolute form to prevent traversal attacks.

### Secure Coding Fixes

Here is an example of how to securely handle file access in Python:

```python
import os
from flask import send_file

# Secure code snippet
def serve_image(request, image_name):
    base_dir = '/path/to/images'
    safe_image_name = os.path.basename(image_name)
    image_path = os.path.join(base_dir, safe_image_name)
    if not os.path.commonprefix([image_path, base_dir]) == base_dir:
        raise ValueError("Invalid path")
    return send_file(image_path)
```

### Configuration Hardening

Hardening the web server configuration can also help mitigate directory traversal vulnerabilities. For example, in Apache, you can configure the `mod_security` module to block suspicious requests:

```apache
<IfModule mod_security.c>
    SecRule ARGS "@rx \.\./" "deny,status:403"
</IfModule>
```

### Conclusion

Directory traversal is a serious web application vulnerability that can lead to significant security risks. By understanding the underlying mechanisms, recognizing recent real-world examples, and implementing robust detection and prevention strategies, you can effectively protect your web applications from these threats.

### Practice Labs

For hands-on practice with directory traversal vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn and test directory traversal vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing various web security concepts, including directory traversal.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities, including directory traversal.

By engaging with these labs, you can gain practical experience in identifying and mitigating directory traversal vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/11-Directory Traversal/01-Directory Traversal Complete Guide/01-Introduction to Directory Traversal Vulnerabilities|Introduction to Directory Traversal Vulnerabilities]] | [[Web Security (PortSwigger)/11-Directory Traversal/01-Directory Traversal Complete Guide/00-Overview|Overview]] | [[03-What is Directory Traversal|What is Directory Traversal]]
