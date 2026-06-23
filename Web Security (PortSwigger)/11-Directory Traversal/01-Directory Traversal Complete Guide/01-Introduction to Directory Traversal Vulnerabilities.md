---
course: Web Security
topic: Directory Traversal
tags: [web-security]
---

## Introduction to Directory Traversal Vulnerabilities

Directory traversal vulnerabilities, also known as path traversal vulnerabilities, occur when an application allows users to access files or directories outside of the intended directory structure. This can happen due to improper validation of user input, leading to unauthorized access to sensitive files or directories. These vulnerabilities are particularly dangerous because they can allow attackers to read, modify, or delete critical system files, potentially leading to a complete compromise of the server.

### Root Cause: Improper Input Validation

The root cause of directory traversal vulnerabilities is often improper input validation. Applications that fail to adequately sanitize and validate user-provided input can be exploited to traverse directories and access files that should be off-limits. This is a common issue across many programming languages and frameworks, but PHP applications are frequently cited due to their widespread use and historical lack of strict input validation mechanisms.

### Sample Vulnerable Code

Let's examine the provided sample code to understand how directory traversal vulnerabilities can arise:

```php
<?php
$template = "blue.php";
if (isset($_COOKIE['template']) && !empty($_COOKIE['template'])) {
    $template = $_COOKIE['template'];
}
include($template);
?>
```

In this code snippet, the `$_COOKIE['template']` variable is used to determine which file to include. If the `template` cookie is set and not empty, its value is assigned to the `$template` variable, which is then passed to the `include()` function. This is a classic example of improper input validation, as the value of the `template` cookie is not sanitized or validated before being used.

### Identifying the Vulnerability

To identify the vulnerability, consider the following steps:

1. **Initialization**: The `$template` variable is initially set to `"blue.php"`.
2. **Conditional Check**: The code checks if the `template` cookie is set and not empty.
3. **Assignment**: If the condition is met, the value of the `template` cookie is assigned to the `$template` variable.
4. **File Inclusion**: The `include()` function is used to include the file specified by the `$template` variable.

The vulnerability lies in the fact that the `template` cookie value is directly used in the `include()` function without any validation. An attacker can manipulate the `template` cookie to include arbitrary files, leading to a directory traversal attack.

### Exploiting the Vulnerability

An attacker can exploit this vulnerability by setting the `template` cookie to a path that traverses directories. For example, setting the `template` cookie to `../../../../etc/passwd` would attempt to include the `/etc/passwd` file, which contains sensitive information about system users.

#### Example Exploit

Here’s how an attacker might craft the exploit:

1. **Set the Cookie**: Set the `template` cookie to a path that traverses directories.
2. **Trigger the Include**: Access the PHP script, causing the `include()` function to execute with the manipulated `template` value.

For instance, the attacker might send the following HTTP request:

```http
GET /vulnerable_script.php HTTP/1.1
Host: example.com
Cookie: template=../../../../etc/passwd
```

This request would cause the PHP script to include the `/etc/passwd` file, potentially revealing sensitive information.

### Real-World Examples

Directory traversal vulnerabilities have been found in numerous real-world applications. Here are some recent examples:

1. **CVE-2021-22205**: A directory traversal vulnerability was discovered in the WordPress plugin "WP File Download." Attackers could exploit this vulnerability to download arbitrary files from the server.
2. **CVE-2020-14882**: A directory traversal vulnerability was found in the "Apache Tomcat" web server. Attackers could exploit this to read sensitive files from the server.

These examples highlight the importance of proper input validation and the potential risks associated with directory traversal vulnerabilities.

### How to Prevent / Defend Against Directory Traversal

Preventing directory traversal vulnerabilities requires a combination of proper input validation, secure coding practices, and configuration hardening. Here are some key strategies:

#### Secure Coding Practices

1. **Input Validation**: Always validate and sanitize user input before using it in file operations. Ensure that the input matches a predefined pattern or whitelist.
2. **Whitelist Filenames**: Use a whitelist of allowed filenames and directories. Only allow the inclusion of files from specific, trusted locations.
3. **Canonicalization**: Normalize paths to their canonical form before using them. This helps prevent attacks that rely on encoded or obfuscated paths.

#### Example Secure Code

Here’s how the original code can be modified to include proper input validation:

```php
<?php
$template = "blue.php";
if (isset($_COOKIE['template']) && !empty($_COOKIE['template'])) {
    $allowed_templates = ['blue.php', 'red.php', 'green.php'];
    if (in_array($_COOKIE['template'], $allowed_templates)) {
        $template = $_COOKIE['template'];
    }
}
include($template);
?>
```

In this secure version, the `template` cookie value is checked against a whitelist of allowed templates before being used in the `include()` function.

#### Configuration Hardening

1. **Disable Dangerous Features**: Disable features like URL rewriting or directory listing that can expose sensitive information.
2. **Restrict Permissions**: Ensure that file permissions are set correctly to prevent unauthorized access.
3. **Use Security Headers**: Implement security headers like `X-Content-Type-Options`, `Content-Security-Policy`, and `Strict-Transport-Security` to enhance overall security.

#### Detection

Detecting directory traversal vulnerabilities can be done through various methods:

1. **Static Analysis Tools**: Use static analysis tools like SonarQube, Fortify, or Veracode to scan code for potential vulnerabilities.
2. **Dynamic Analysis Tools**: Use dynamic analysis tools like Burp Suite, OWASP ZAP, or Acunetix to test applications for runtime vulnerabilities.
3. **Manual Testing**: Perform manual testing by attempting to exploit the vulnerability using crafted inputs.

### Practice Labs

To gain practical experience with directory traversal vulnerabilities, consider the following labs:

1. **PortSwigger Web Security Academy**: Offers interactive labs that cover various web security topics, including directory traversal.
2. **OWASP Juice Shop**: A deliberately insecure web application that includes several vulnerabilities, including directory traversal.
3. **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is intentionally vulnerable, providing a controlled environment to practice exploiting and fixing vulnerabilities.

By thoroughly understanding the concepts, practicing with real-world examples, and implementing robust security measures, developers can effectively prevent directory traversal vulnerabilities and protect their applications from exploitation.

### Conclusion

Directory traversal vulnerabilities are a significant threat to web applications due to their simplicity and potential impact. By understanding the root causes, identifying vulnerabilities, and implementing proper defenses, developers can significantly reduce the risk of such attacks. Regularly testing and validating input, using secure coding practices, and hardening configurations are essential steps in maintaining the security of web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/11-Directory Traversal/01-Directory Traversal Complete Guide/00-Overview|Overview]] | [[Web Security (PortSwigger)/11-Directory Traversal/01-Directory Traversal Complete Guide/02-Introduction to Directory Traversal|Introduction to Directory Traversal]]
