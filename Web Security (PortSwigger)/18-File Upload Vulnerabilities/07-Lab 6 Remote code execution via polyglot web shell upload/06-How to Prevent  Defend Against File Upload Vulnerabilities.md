---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## How to Prevent / Defend Against File Upload Vulnerabilities

### Detection

To detect file upload vulnerabilities, you can use static analysis tools to scan the codebase for insecure file upload functions. Additionally, you can use dynamic analysis tools to test the application for vulnerabilities.

### Prevention

To prevent file upload vulnerabilities, you should implement the following measures:

1. **Validate File Types:** Ensure that only allowed file types can be uploaded. Use a whitelist approach to specify allowed file types.
2. **Sanitize File Contents:** Validate the contents of the file to ensure that it does not contain executable code.
3. **Use Content Disposition Headers:** Set appropriate content disposition headers to prevent the browser from executing the file.
4. **Store Files Outside the Web Root:** Store uploaded files outside the web root directory to prevent direct access via a web browser.
5. **Use Secure File Names:** Use secure file naming conventions to prevent path traversal attacks.

### Secure Coding Fixes

Here is an example of a secure file upload function in PHP:

```php
<?php
$allowedTypes = ['image/jpeg', 'image/png'];
$targetDir = '/path/to/upload/directory';
$targetFile = $targetDir . basename($_FILES["file"]["name"]);

// Check if file is a valid image
$imageFileType = strtolower(pathinfo($targetFile, PATHINFO_EXTENSION));
if (!in_array($imageFileType, $allowedTypes)) {
    die("Invalid file type.");
}

// Move the uploaded file to the target directory
if (move_uploaded_file($_FILES["file"]["tmp_name"], $targetFile)) {
    echo "The file ". htmlspecialchars(basename($_FILES["file"]["name"])). " has been uploaded.";
} else {
    echo "Sorry, there was an error uploading your file.";
}
?>
```

### Configuration Hardening

Ensure that the web server configuration is hardened to prevent file upload vulnerabilities. For example, in Apache, you can set the following directives in the `.htaccess` file:

```apache
<FilesMatch "\.(php|php5)$">
    Order Deny,Allow
    Deny from all
</FilesMatch>
```

This will deny access to PHP files in the specified directory.

---
<!-- nav -->
[[05-File Upload Vulnerabilities and Remote Code Execution via Polyglot Web Shells|File Upload Vulnerabilities and Remote Code Execution via Polyglot Web Shells]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/07-Lab 6 Remote code execution via polyglot web shell upload/00-Overview|Overview]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/07-Lab 6 Remote code execution via polyglot web shell upload/07-Practice Labs|Practice Labs]]
