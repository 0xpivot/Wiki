---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## File Upload Vulnerabilities and Polyglot Web Shells

### Introduction to File Upload Vulnerabilities

File upload vulnerabilities occur when a web application allows users to upload files without proper validation or sanitization. This can lead to various security issues, including remote code execution (RCE), cross-site scripting (XSS), and directory traversal attacks. One particularly dangerous form of file upload vulnerability is the ability to upload a polyglot file—a file that can be interpreted in multiple ways depending on the context in which it is used.

### What is a Polyglot File?

A polyglot file is a file that can be interpreted in different ways based on the context in which it is used. For example, a polyglot file might appear to be an image file (like a `.jpg` or `.png`) but also contain executable code (like PHP). This dual nature makes polyglot files a powerful tool for attackers to bypass file type restrictions and execute arbitrary code on a server.

#### Why Polyglot Files Matter

Polyglot files are significant because they can circumvent typical file upload filters. Many web applications restrict uploads to specific file types, such as images, to prevent malicious code from being uploaded. However, if an attacker can craft a file that looks like an image but contains executable code, they can bypass these restrictions and potentially gain control of the server.

### Creating a Polyglot File Using `exiftool`

To demonstrate how to create a polyglot file, we will use a command-line tool called `exiftool`. This tool is commonly available in Kali Linux and can be used to embed executable code within the metadata of an image file.

#### Background on `exiftool`

`exiftool` is a versatile command-line utility that can read, write, and manipulate metadata in various file formats, including images. By embedding executable code within the metadata of an image file, we can create a polyglot file that appears to be an image but also contains malicious code.

#### Step-by-Step Guide to Creating a Polyglot File

1. **Open Terminal**: Open a terminal window in Kali Linux.
2. **Prepare the Image**: Download an image file, such as `CAD.jpg`.
3. **Embed Malicious Code**: Use `exiftool` to embed a PHP web shell within the metadata of the image.

Here is the command to achieve this:

```bash
exiftool -Comment='<?php echo file_get_contents("/home/carlos/secret"); ?>' CAD.jpg -o polygott.php
```

This command does the following:
- `-Comment`: Specifies the metadata field where the malicious code will be embedded.
- `'<?php echo file_get_contents("/home/carlos/secret"); ?>'`: The PHP code to be embedded. This code reads and outputs the contents of the `/home/carlos/secret` file.
- `CAD.jpg`: The input image file.
- `-o polygott.php`: The output file name.

### Understanding the Polyglot File

When the server inspects the `polygott.php` file, it sees it as a valid image file due to its extension and metadata. However, when the file is accessed as a PHP script, the embedded code is executed.

#### Example of the Polyglot File

Let's break down the process with a more detailed example:

1. **Download an Image**:
   ```bash
   wget https://example.com/CAD.jpg
   ```

2. **Embed Malicious Code**:
   ```bash
   exiftool -Comment='<?php echo file_get_contents("/home/carlos/secret"); ?>' CAD.jpg -o polygott.php
   ```

3. **Verify the Output**:
   After running the command, you should see the output:
   ```
   1 image files created
   ```

4. **Inspect the Result**:
   The `polygott.php` file now contains both the image data and the embedded PHP code.

### Real-World Examples and Recent Breaches

Polyglot files have been used in several real-world attacks. For instance, in the breach of a popular blogging platform in 2021, attackers used polyglot files to bypass file upload restrictions and execute arbitrary code on the server. This led to the exposure of sensitive user data and the compromise of the platform's infrastructure.

### How to Prevent / Defend Against Polyglot File Attacks

#### Detection

1. **Signature-Based Detection**: Use antivirus software and intrusion detection systems (IDS) that can identify known patterns of polyglot files.
2. **Behavioral Analysis**: Monitor server logs and network traffic for unusual behavior indicative of polyglot file exploitation.

#### Prevention

1. **Strict File Validation**: Implement strict file validation mechanisms to ensure that only allowed file types are uploaded.
2. **Content-Type Checking**: Verify the MIME type of uploaded files to ensure they match the expected type.
3. **Metadata Inspection**: Use tools like `exiftool` to inspect the metadata of uploaded files for suspicious content.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of the code:

**Vulnerable Code**:
```php
<?php
$target_dir = "uploads/";
$target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);
move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file);
?>
```

**Secure Code**:
```php
<?php
$target_dir = "uploads/";
$target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);
$allowed_types = ['image/jpeg', 'image/png'];
$file_type = $_FILES["fileToUpload"]["type"];

if (in_array($file_type, $allowed_types)) {
    move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file);
} else {
    echo "Invalid file type.";
}
?>
```

### Configuration Hardening

1. **Disable Executable Content**: Ensure that the web server is configured to disallow the execution of scripts from user-uploaded directories.
2. **Use Content Security Policies (CSP)**: Implement CSP to restrict the sources from which scripts can be loaded.

### Hands-On Practice Labs

For hands-on practice with file upload vulnerabilities and polyglot files, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various web security topics, including file upload vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

These labs provide a safe environment to explore and understand the intricacies of file upload vulnerabilities and how to defend against them.

### Conclusion

File upload vulnerabilities, especially those involving polyglot files, pose a significant threat to web applications. By understanding the mechanics of these vulnerabilities and implementing robust detection and prevention strategies, developers can significantly reduce the risk of such attacks. Always stay vigilant and keep your systems up-to-date with the latest security practices.

---
<!-- nav -->
[[03-Exfiltrating the Secret File|Exfiltrating the Secret File]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/07-Lab 6 Remote code execution via polyglot web shell upload/00-Overview|Overview]] | [[05-File Upload Vulnerabilities and Remote Code Execution via Polyglot Web Shells|File Upload Vulnerabilities and Remote Code Execution via Polyglot Web Shells]]
