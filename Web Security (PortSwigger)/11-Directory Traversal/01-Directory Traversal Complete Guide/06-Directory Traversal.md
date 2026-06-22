---
course: Web Security
topic: Directory Traversal
tags: [web-security]
---

## Directory Traversal

### What is Directory Traversal?

Directory Traversal, also known as Path Traversal, is a type of web application vulnerability that allows an attacker to access files and directories that are stored outside the web root directory. This can lead to unauthorized access to sensitive information such as configuration files, source code, and other critical data. The attacker achieves this by manipulating the input parameters used to reference files.

### Why Does Directory Traversal Matter?

Directory Traversal vulnerabilities can have severe consequences, including:

- **Data Exposure**: Attackers can gain access to sensitive data like passwords, private keys, and other confidential information.
- **System Compromise**: Access to system files can allow attackers to execute arbitrary commands, leading to a full system compromise.
- **Denial of Service**: By accessing certain files, attackers might cause the application to crash or behave unexpectedly, resulting in a denial of service.

### How Does Directory Traversal Work?

The core mechanism of Directory Traversal involves manipulating the input parameters that reference files. Typically, these parameters are passed through the URL or form inputs. The goal is to trick the application into reading files from unintended locations.

#### Absolute Path Exploitation

One straightforward method is to use the absolute path of the desired file. For instance, consider a web application that reads a file based on user input:

```plaintext
http://example.com/download?file=../etc/passwd
```

Here, `../` is used to navigate up one directory level. If the application does not properly sanitize the input, it may read the `/etc/passwd` file, which contains user account information.

### Non-Recursive Stripping of Traversal Sequences

Another common scenario is when the application attempts to strip out traversal sequences (`../`) but does so non-recursively. This means that if the traversal sequence is repeated multiple times, the application might not completely remove it.

For example, consider the following payload:

```plaintext
http://example.com/download?file=../../../../etc/passwd
```

If the application only removes the first occurrence of `../`, the remaining traversal sequences will still be processed, leading to unauthorized access.

### URL Encoding and Double Encoding

To bypass simple input validation mechanisms, attackers often use URL encoding. For instance, `../` can be encoded as `%2e%2e%2f`.

```plaintext
http://example.com/download?file=%2e%2e%2f%2e%2e%2fetc%2fpasswd
```

Double encoding involves encoding the already encoded string again. For example, `%2e%2e%2f` can be further encoded as `%252e%252e%252f`.

```plaintext
http://example.com/download?file=%252e%252e%252f%25252e%25252e%25252fetc%252fpasswd
```

This technique can sometimes bypass more sophisticated validation mechanisms.

### Specific Path Requirements

In some cases, the application requires the input parameter to start with a specific path. For example, the parameter might need to start with `/var/www/images/`.

```plaintext
http://example.com/download?file=/var/www/images/../../etc/passwd
```

By including the required path, the attacker can still exploit the vulnerability.

### File Extension Requirements

Some applications enforce specific file extensions. To bypass this, attackers can use the null byte (`\x00`), which is often interpreted as the end of a string.

```plaintext
http://example.com/download?file=../../etc/passwd%00.jpg
```

Here, `%00` represents the null byte, effectively truncating the filename at `passwd`.

### Real-World Examples

#### CVE-2021-21972

In 2021, a directory traversal vulnerability was discovered in the popular WordPress plugin "WP eCommerce." The vulnerability allowed attackers to access sensitive files by manipulating the `file` parameter in the URL.

```plaintext
http://example.com/wp-content/plugins/wp-e-commerce/wpsc-templates/download.php?file=../../../../wp-config.php
```

This led to the exposure of database credentials and other sensitive information.

#### CVE-2022-22965

Another notable example is the directory traversal vulnerability found in the "Joomla!" CMS. The vulnerability allowed attackers to read arbitrary files by manipulating the `tmpl` parameter.

```plaintext
http://example.com/index.php?option=com_content&view=article&id=1&tmpl=component&print=1&layout=default&Itemid=101&format=raw&task=download&file=../../../../etc/passwd
```

This resulted in unauthorized access to system files and potential system compromise.

### Detection and Prevention

#### How to Detect Directory Traversal Vulnerabilities

1. **Static Analysis**: Use tools like SonarQube, Fortify, or Veracode to scan the codebase for insecure file handling practices.
2. **Dynamic Analysis**: Employ penetration testing tools like Burp Suite, OWASP ZAP, or DirBuster to test the application for directory traversal vulnerabilities.
3. **Logging and Monitoring**: Implement logging and monitoring to detect unusual file access patterns that might indicate an exploitation attempt.

#### How to Prevent Directory Traversal Vulnerabilities

1. **Input Validation**: Ensure that all user-supplied input is validated against a whitelist of allowed characters and paths.
2. **Canonicalization**: Normalize all paths to their canonical form before processing them. This helps in preventing attacks that rely on different representations of the same path.
3. **Least Privilege Principle**: Run the web server and application with the least privileges necessary. Avoid running them as root or administrator.
4. **Filesystem Permissions**: Restrict filesystem permissions to ensure that the application cannot access sensitive files outside its designated directory.

### Secure Coding Practices

#### Vulnerable Code Example

```php
<?php
$file = $_GET['file'];
readfile("/var/www/html/uploads/$file");
?>
```

#### Secure Code Example

```php
<?php
$allowed_extensions = ['jpg', 'png', 'gif'];
$file = basename($_GET['file']);
$ext = pathinfo($file, PATHINFO_EXTENSION);

if (!in_array($ext, $allowed_extensions)) {
    die("Invalid file extension.");
}

$safe_file = "/var/www/html/uploads/" . $file;
readfile($safe_file);
?>
```

### Configuration Hardening

#### Web Server Configuration

Ensure that the web server is configured to restrict access to sensitive directories. For example, in Apache, you can use the `<Directory>` directive to set permissions.

```apache
<Directory /var/www/html>
    Options Indexes FollowSymLinks MultiViews
    AllowOverride None
    Order allow,deny
    Allow from all
</Directory>

<Directory /etc>
    Order deny,allow
    Deny from all
</Directory>
```

### Hands-On Labs

To practice and understand directory traversal vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive module on directory traversal with interactive challenges.
- **OWASP Juice Shop**: A deliberately vulnerable web application that includes directory traversal vulnerabilities among other issues.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is intentionally vulnerable, including directory traversal.

### Conclusion

Directory Traversal is a serious web security issue that can lead to significant data exposure and system compromise. Understanding the mechanisms behind this vulnerability, detecting it, and implementing robust preventive measures are crucial for securing web applications. By following secure coding practices and configuring systems appropriately, developers can mitigate the risks associated with directory traversal attacks.

---
<!-- nav -->
[[05-Directory Traversal Vulnerability|Directory Traversal Vulnerability]] | [[Web Security (PortSwigger)/11-Directory Traversal/01-Directory Traversal Complete Guide/00-Overview|Overview]] | [[07-Mapping the Application|Mapping the Application]]
