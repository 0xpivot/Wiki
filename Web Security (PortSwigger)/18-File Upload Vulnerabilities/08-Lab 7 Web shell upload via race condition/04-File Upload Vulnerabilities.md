---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## File Upload Vulnerabilities

### Introduction

File upload vulnerabilities occur when a web application allows users to upload files to the server without proper validation or sanitization. This can lead to various security issues, including remote code execution, denial of service, and data leakage. In this section, we will explore one specific type of file upload vulnerability: a web shell upload via a race condition.

### Background Theory

#### What is a File Upload Vulnerability?

A file upload vulnerability arises when a web application allows users to upload files to the server, but does not properly validate the file type, size, or content. This can allow attackers to upload malicious files, such as web shells, which can be executed on the server to gain unauthorized access.

#### Why Does It Matter?

File upload vulnerabilities can have severe consequences, including:

- **Remote Code Execution**: Attackers can upload and execute arbitrary code on the server.
- **Data Leakage**: Attackers can upload scripts that exfiltrate sensitive data from the server.
- **Denial of Service**: Attackers can upload large files or scripts that consume server resources, leading to a denial of service.

### Race Condition Vulnerability

#### What is a Race Condition?

A race condition occurs when the outcome of a process depends on the sequence or timing of uncontrollable events. In the context of file uploads, a race condition can occur if the server checks the file type after moving the file to a temporary location, but before executing the final validation steps.

#### How Does It Work?

Consider the following scenario:

1. An attacker uploads a PHP file (`test.php`) containing a web shell.
2. The server temporarily moves the file to a temporary directory.
3. The server performs a virus scan and file type check.
4. If the file type check fails, the server deletes the file.

If the attacker can manipulate the timing of these operations, they can exploit the race condition to bypass the file type check and execute the web shell.

### Example Scenario

Let's walk through the example provided in the lecture transcript.

#### Step-by-Step Mechanics

1. **Create the Web Shell**:
    - Create a PHP file named `test.php` with the following content:
      ```php
      <?php
      echo file_get_contents('/home/carlos/secret');
      ?>
      ```

2. **Upload the File**:
    - Attempt to upload the `test.php` file using the web interface.
    - The server responds with an error message: "Sorry, only JPEG or PNG files are allowed."

3. **Inspect the Request**:
    - Use a proxy tool like Burp Suite to inspect the HTTP request.
    - The request includes the file name `test.php` and the content of the PHP script.

4. **Analyze the Response**:
    - The server returns a `403 Forbidden` status code, indicating that the file type is not allowed.

5. **White Box Approach**:
    - Ask the developers for access to the codebase.
    - Review the code responsible for the upload functionality.

#### Code Analysis

The code snippet responsible for the upload functionality might look like this:

```php
<?php
$target_dir = "uploads/";
$target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);
$uploadOk = 1;
$imageFileType = strtolower(pathinfo($target_file, PATHINFO_EXTENSION));

// Check if file is a actual image or fake image
if (isset($_POST["submit"])) {
    $check = getimagesize($_FILES["fileToUpload"]["tmp_name"]);
    if ($check !== false) {
        echo "File is an image - " . $check["mime"] . ".";
        $uploadOk = 1;
    } else {
        echo "File is not an image.";
        $uploadOk = 0;
    }
}

// Check file size
if ($_FILES["fileToUpload"]["size"] > 500000) {
    echo "Sorry, your file is too large.";
    $uploadOk = 0;
}

// Allow certain file formats
if ($imageFileType != "jpg" && $imageFileType != "png") {
    echo "Sorry, only JPG, PNG files are allowed.";
    $uploadOk = 0;
}

// Check if $uploadOk is set to 0 by an error
if ($uploadOk == 0) {
    echo "Sorry, your file was not uploaded.";
} else {
    if (move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file)) {
        echo "The file ". htmlspecialchars(basename($_FILES["fileToUpload"]["name"])). " has been uploaded.";
    } else {
        echo "Sorry, there was an error uploading your file.";
    }
}
?>
```

### Race Condition Exploit

#### How to Exploit

1. **Timing Manipulation**:
    - The attacker can manipulate the timing of the upload process to exploit the race condition.
    - By rapidly uploading the file and triggering the final validation steps, the attacker can bypass the file type check.

2. **Race Condition Sequence**:
    - The attacker uploads the `test.php` file.
    - The server temporarily moves the file to a temporary directory.
    - Before the final validation steps are performed, the attacker triggers the execution of the web shell.

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2021-21972**: A race condition vulnerability in the WordPress plugin "WP File Download" allowed attackers to upload and execute arbitrary files.
- **CVE-2020-14882**: A race condition vulnerability in the Joomla component "com_media" allowed attackers to upload and execute arbitrary files.

### How to Prevent / Defend

#### Detection

- **Static Analysis**: Use static analysis tools to identify potential race conditions in the codebase.
- **Dynamic Analysis**: Use dynamic analysis tools to monitor the upload process and detect suspicious behavior.

#### Prevention

- **Strict Validation**: Implement strict validation of file types, sizes, and content.
- **Temporary Directory**: Use a temporary directory that is not accessible from the web.
- **File Type Checking**: Perform file type checking before moving the file to the final destination.
- **Content Scanning**: Use content scanning tools to detect and block malicious files.

#### Secure Coding Fixes

##### Vulnerable Code

```php
<?php
$target_dir = "uploads/";
$target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);
$uploadOk = 1;
$imageFileType = strtolower(pathinfo($target_file, PATHINFO_EXTENSION));

// Check if file is a actual image or fake image
if (isset($_POST["submit"])) {
    $check = getimagesize($_FILES["fileToUpload"]["tmp_name"]);
    if ($check !== false) {
        echo "File is an image - " . $check["mime"] . ".";
        $uploadOk = 1;
    } else {
        echo "File is not an image.";
        $uploadOk = 0;
    }
}

// Check file size
if ($_FILES["fileToUpload"]["size"] > 2000000) {
    echo "Sorry, your file is too large.";
    $uploadOk = 0;
}

// Allow certain file formats
if ($imageFileType != "jpg" && $imageFileType != "png") {
    echo "Sorry, only JPG, PNG files are allowed.";
    $uploadOk = 0;
}

// Check if $uploadOk is set to 0 by an error
if ($uploadOk == 0) {
    echo "Sorry, your file was not uploaded.";
} else {
    if (move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file)) {
        echo "The file ". htmlspecialchars(basename($_FILES["fileToUpload"]["name"])). " has been uploaded.";
    } else {
        echo "Sorry, there was an error uploading your file.";
    }
}
?>
```

##### Secure Code

```php
<?php
$target_dir = "uploads/";
$target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);
$uploadOk = 1;
$imageFileType = strtolower(pathinfo($target_file, PATHINFO_EXTENSION));

// Check if file is a actual image or fake image
if (isset($_POST["submit"])) {
    $check = getimagesize($_FILES["fileToUpload"]["tmp_name"]);
    if ($check !== false) {
        echo "File is an image - " . $check["mime"] . ".";
        $uploadOk = 1;
    } else {
        echo "File is not an image.";
        $uploadOk = 0;
    }
}

// Check file size
if ($_FILES["fileToUpload"]["size"] > 2000000) {
    echo "Sorry, your file is too large.";
    $uploadOk = 0;
}

// Allow certain file formats
if ($imageFileType != "jpg" && $imageFileType != "png") {
    echo "Sorry, only JPG, PNG files are allowed.";
    $uploadOk = 0;
}

// Check if $uploadOk is set to 0 by an error
if ($uploadOk == 0) {
    echo "Sorry, your file was not uploaded.";
} else {
    // Move the file to a temporary directory
    $temp_file = tempnam(sys_get_temp_dir(), 'upload_');
    if (move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $temp_file)) {
        // Perform additional checks on the temporary file
        if (is_image($temp_file)) {
            // Move the file to the final destination
            if (rename($temp_file, $target_file)) {
                echo "The file ". htmlspecialchars(basename($_FILES["fileToUpload"]["name"])). " has been uploaded.";
            } else {
                echo "Sorry, there was an error uploading your file.";
            }
        } else {
            echo "File is not an image.";
            unlink($temp_file);
        }
    } else {
        echo "Sorry, there was an error uploading your file.";
    }
}
?>
```

### Configuration Hardening

#### Secure Configuration

- **Disable Directory Listing**: Ensure that directory listing is disabled to prevent attackers from browsing the upload directory.
- **Restrict Permissions**: Set appropriate file permissions to prevent unauthorized access to uploaded files.
- **Use Content Security Policies**: Implement content security policies to restrict the sources of executable content.

### Practice Labs

For hands-on practice with file upload vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive lab on file upload vulnerabilities.
- **OWASP Juice Shop**: Provides a real-world web application with various security vulnerabilities, including file upload vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: Contains a variety of web application vulnerabilities, including file upload vulnerabilities.
- **WebGoat**: Offers a series of lessons on web application security, including file upload vulnerabilities.

By thoroughly understanding the mechanics of file upload vulnerabilities and implementing robust defenses, you can significantly reduce the risk of exploitation.

---
<!-- nav -->
[[03-File Upload Vulnerabilities and Race Conditions|File Upload Vulnerabilities and Race Conditions]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/08-Lab 7 Web shell upload via race condition/00-Overview|Overview]] | [[05-Understanding File Upload Vulnerabilities|Understanding File Upload Vulnerabilities]]
