---
course: Web Security
topic: Directory Traversal
tags: [web-security]
---

## What is Directory Traversal?

Directory traversal, also known as path traversal, is a type of web security vulnerability that allows attackers to access files and directories that are stored outside the web root directory. This vulnerability occurs due to improper input validation and handling of user-supplied input in web applications. Essentially, an attacker can manipulate the input to traverse the directory structure of the server and gain unauthorized access to sensitive files such as configuration files, source code, or even system binaries.

### Why Does Directory Traversal Matter?

Directory traversal attacks can lead to severe consequences, including data theft, loss of confidentiality, and potential system compromise. By accessing sensitive files, an attacker can extract valuable information, such as database credentials, encryption keys, or intellectual property. Furthermore, gaining access to system binaries can allow an attacker to execute arbitrary commands on the server, leading to a full system takeover.

### How Does Directory Traversal Work Under the Hood?

To understand directory traversal, let's break down the process:

1. **User Input**: A web application typically accepts user input through various means, such as form fields, URL parameters, or API endpoints.
2. **File Access**: The application uses this input to construct a file path and attempt to read or write to a specific file.
3. **Improper Validation**: If the input is not properly validated, an attacker can inject special characters or sequences to manipulate the file path.
4. **Traversal**: By using special sequences like `../` (which moves up one directory level), the attacker can navigate outside the intended directory and access files that should be restricted.

### Real-World Example: CVE-2021-21972

A notable real-world example of a directory traversal vulnerability is CVE-2021-21972, which affected the Apache Struts framework. This vulnerability allowed attackers to bypass the intended directory restrictions and access arbitrary files on the server. The exploitation involved manipulating the `Content-Disposition` header in an HTTP request to trick the application into reading files outside the web root directory.

```http
POST /struts2-showcase/fileupload!execute.action HTTP/1.1
Host: target.example.com
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="../../etc/passwd"

<file contents>
```

In this example, the attacker used the `../../` sequence to move up two directory levels and access the `/etc/passwd` file, which contains user account information.

### Common Mistakes and Pitfalls

One of the most common mistakes that lead to directory traversal vulnerabilities is improper input validation. Developers often assume that user input will always be safe and fail to implement robust validation mechanisms. Additionally, relying solely on client-side validation is insufficient, as attackers can easily bypass it.

Another pitfall is the use of relative paths without proper sanitization. For instance, consider the following PHP code snippet:

```php
<?php
$filename = $_GET['file'];
if (file_exists($filename)) {
    echo file_get_contents($filename);
}
?>
```

In this example, the `$filename` variable is directly taken from the user input and used in the `file_get_contents()` function. An attacker can manipulate the `file` parameter to perform directory traversal, such as `file=../../../../etc/passwd`.

### How to Prevent / Defend Against Directory Traversal

#### Detection

Detecting directory traversal vulnerabilities requires a combination of static analysis and dynamic testing. Static analysis tools can identify insecure coding patterns, while dynamic testing involves simulating attacks to see if the application is vulnerable.

#### Prevention

Preventing directory traversal involves several key strategies:

1. **Input Validation**: Always validate and sanitize user input to ensure it does not contain malicious sequences. Use whitelisting to allow only specific, safe characters.
2. **Absolute Paths**: Use absolute paths instead of relative paths to avoid directory traversal. Ensure that the application operates within a predefined directory structure.
3. **Least Privilege Principle**: Run the web application with the least privileges necessary. Avoid running the application as a privileged user, such as root or administrator.
4. **Security Headers**: Implement security headers like `X-Content-Type-Options` and `Content-Security-Policy` to mitigate potential exploitation vectors.

#### Secure Coding Fixes

Let's compare the vulnerable code with a secure version:

**Vulnerable Code:**

```php
<?php
$filename = $_GET['file'];
if (file_exists($filename)) {
    echo file_get_contents($filename);
}
?>
```

**Secure Code:**

```php
<?php
$baseDir = '/var/www/html/uploads/';
$filename = basename($_GET['file']);
$fullPath = $baseDir . $filename;

if (file_exists($fullPath)) {
    echo file_get_contents($fullPath);
}
?>
```

In the secure version, the `basename()` function ensures that only the filename is used, preventing directory traversal. The `fullPath` is constructed by concatenating the base directory with the sanitized filename.

### Hands-On Lab Exercises

To practice and solidify your understanding of directory traversal, consider the following hands-on lab exercises:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various web security topics, including directory traversal.
- **OWASP Juice Shop**: A deliberately insecure web application that includes directory traversal vulnerabilities for educational purposes.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application with intentional vulnerabilities, including directory traversal, for learning and testing.

These labs provide a controlled environment to test and exploit directory traversal vulnerabilities, helping you gain practical experience in identifying and mitigating such issues.

### Conclusion

Directory traversal is a critical web security vulnerability that can lead to significant data breaches and system compromises. By understanding the underlying mechanics, recognizing common mistakes, and implementing robust prevention measures, you can effectively defend against directory traversal attacks. Stay vigilant and continue to learn about the latest security practices to protect your applications and systems.

---
<!-- nav -->
[[Web Security (PortSwigger)/11-Directory Traversal/01-Directory Traversal Complete Guide/02-Introduction to Directory Traversal|Introduction to Directory Traversal]] | [[Web Security (PortSwigger)/11-Directory Traversal/01-Directory Traversal Complete Guide/00-Overview|Overview]] | [[04-Directory Traversal Vulnerabilities|Directory Traversal Vulnerabilities]]
