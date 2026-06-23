---
course: API Security
topic: File Path Traversal
tags: [api-security]
---

## File Path Traversal

### Introduction

File path traversal, also known as directory traversal, is a type of web application vulnerability that allows an attacker to access restricted files and directories on the server. This vulnerability occurs when an application uses user-supplied input to build a file path without proper validation or sanitization. By manipulating the input, an attacker can traverse the file system and access sensitive information such as configuration files, passwords, and database records.

### Understanding File Path Traversal

#### What is File Path Traversal?

File path traversal is a technique used by attackers to access files that are outside the intended directory structure of a web application. This is achieved by manipulating the input parameters that are used to construct file paths. For example, consider a web application that allows users to download files from a specific directory:

```plaintext
http://example.com/download.php?file=filename.txt
```

If the `download.php` script constructs the file path using the `file` parameter without proper validation, an attacker could manipulate the input to access other files on the server. For instance:

```plaintext
http://example.com/download.php?file=../../../../etc/passwd
```

In this example, the `../../../../etc/passwd` input attempts to navigate up several directory levels and access the `/etc/passwd` file, which contains user account information.

#### Why Does File Path Traversal Matter?

File path traversal is a critical vulnerability because it can lead to unauthorized access to sensitive information. Attackers can use this vulnerability to:

- Access configuration files that may contain database credentials or other sensitive data.
- Retrieve password files or other authentication-related information.
- Gain insights into the server's file structure, which can be used to plan further attacks.
- Exfiltrate sensitive data such as database records, log files, or proprietary information.

### How File Path Traversal Works

#### Mechanics of File Path Traversal

To understand how file path traversal works, let's break down the process:

1. **Input Manipulation**: An attacker manipulates the input parameter to include special characters like `../` (dot-dot-slash) to navigate up the directory tree.
2. **Path Construction**: The application constructs the file path using the manipulated input.
3. **File Access**: The application attempts to access the constructed file path, potentially leading to unauthorized access to sensitive files.

Consider the following PHP code snippet that demonstrates a vulnerable implementation:

```php
<?php
$file = $_GET['file'];
if (file_exists($file)) {
    echo file_get_contents($file);
} else {
    echo "File not found.";
}
?>
```

In this example, the `file` parameter is directly used to construct the file path. An attacker can exploit this by providing a specially crafted input:

```plaintext
http://example.com/vulnerable.php?file=../../../../etc/passwd
```

The `../../../../etc/passwd` input navigates up several directory levels and accesses the `/etc/passwd` file.

#### Real-World Examples

File path traversal vulnerabilities have been exploited in various real-world scenarios. Here are some notable examples:

- **CVE-2021-21972**: A file path traversal vulnerability was discovered in the WordPress plugin "WP eCommerce." The plugin allowed attackers to upload malicious files and execute arbitrary code on the server.
- **CVE-2020-14882**: A file path traversal vulnerability was found in the "Apache Struts" framework. The vulnerability allowed attackers to access sensitive files and execute arbitrary commands on the server.

### Detection and Prevention

#### How to Detect File Path Traversal Vulnerabilities

Detecting file path traversal vulnerabilities requires a combination of static analysis and dynamic testing:

1. **Static Analysis**: Tools like SonarQube, Fortify, and Veracode can analyze the source code to identify potential vulnerabilities.
2. **Dynamic Testing**: Penetration testing tools like Burp Suite, OWASP ZAP, and DirBuster can simulate attacks to test for file path traversal vulnerabilities.

#### How to Prevent File Path Traversal

Preventing file path traversal requires implementing robust input validation and sanitization techniques:

1. **Input Validation**: Validate user-supplied input to ensure it conforms to expected patterns. For example, use regular expressions to match valid filenames.
2. **Whitelisting**: Use a whitelist approach to restrict the set of valid inputs. Only allow specific filenames or directories that are explicitly permitted.
3. **Canonicalization**: Normalize the input to remove any special characters or encoding that could be used to bypass validation.

Here is an example of a secure implementation using whitelisting and canonicalization:

```php
<?php
$validFiles = ['file1.txt', 'file2.txt', 'file3.txt'];
$file = $_GET['file'];

// Canonicalize the input to remove any special characters
$file = basename(realpath($file));

if (in_array($file, $validFiles)) {
    echo file_get_contents($file);
} else {
    echo "Invalid file.";
}
?>
```

In this example, the `basename` and `realpath` functions are used to canonicalize the input, ensuring that any special characters are removed. The `in_array` function checks if the input matches any of the valid filenames.

### Secure Coding Practices

#### Secure Code Example

Here is a comparison between a vulnerable and a secure implementation:

**Vulnerable Implementation:**

```php
<?php
$file = $_GET['file'];
if (file_exists($file)) {
    echo file_get_contents($file);
} else {
    echo "File not found.";
}
?>
```

**Secure Implementation:**

```php
<?php
$validFiles = ['file1.txt', 'file2.txt', 'file3.txt'];
$file = $_GET['file'];

// Canonicalize the input to remove any special characters
$file = basename(realpath($file));

if (in_array($file, $validFiles)) {
    echo file_get_contents($file);
} else {
    echo "Invalid file.";
}
?>
```

### Configuration Hardening

#### Hardening Server Configurations

Hardening server configurations can help mitigate the risk of file path traversal vulnerabilities:

1. **Limit File Permissions**: Ensure that sensitive files and directories have appropriate permissions to prevent unauthorized access.
2. **Disable Directory Listing**: Disable directory listing in web servers to prevent attackers from discovering the file structure.
3. **Use Web Application Firewalls (WAF)**: Implement WAFs to filter out malicious requests and protect against file path traversal attacks.

### Hands-On Practice

For hands-on practice with file path traversal vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice exploiting and defending against file path traversal vulnerabilities.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security vulnerabilities, including file path traversal.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for practicing penetration testing and security assessments.

### Conclusion

File path traversal is a serious vulnerability that can lead to unauthorized access to sensitive information. By understanding the mechanics of file path traversal, detecting potential vulnerabilities, and implementing secure coding practices, developers can significantly reduce the risk of exploitation. Regularly testing and hardening server configurations can further enhance the security of web applications.

---
<!-- nav -->
[[01-File Path Traversal Vulnerabilities in APIs|File Path Traversal Vulnerabilities in APIs]] | [[API Security/15-File Path Traversal/01-Background Concept API Perspective/00-Overview|Overview]] | [[API Security/15-File Path Traversal/01-Background Concept API Perspective/03-Practice Questions & Answers|Practice Questions & Answers]]
