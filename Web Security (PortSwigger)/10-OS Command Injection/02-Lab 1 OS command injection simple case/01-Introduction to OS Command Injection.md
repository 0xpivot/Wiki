---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Introduction to OS Command Injection

### What is OS Command Injection?

OS Command Injection is a type of vulnerability that occurs when an application constructs and executes a system command using input provided by an attacker. If the input is not properly sanitized, an attacker can inject malicious commands that can be executed by the operating system. This can lead to unauthorized access, data theft, or even complete control of the server.

### Why Does OS Command Injection Matter?

Command injection vulnerabilities are critical because they allow attackers to bypass application logic and execute arbitrary commands on the underlying operating system. This can result in severe consequences such as:

- **Data Theft**: Accessing sensitive files or databases.
- **System Compromise**: Gaining administrative privileges on the server.
- **Denial of Service**: Disrupting the normal operation of the system.
- **Malware Installation**: Installing malware or backdoors for future attacks.

### How Does OS Command Injection Work?

The core mechanism of OS Command Injection involves the execution of system commands through functions like `exec()`, `system()`, `shell_exec()`, etc., in various programming languages. These functions take a string as input and execute it as a command on the operating system.

Consider the following PHP code snippet:

```php
<?php
$product_id = $_GET['product_id'];
$store_id = $_GET['store_id'];

$command = "stock_check $product_id $store_id";
$output = shell_exec($command);
echo "<pre>$output</pre>";
?>
```

In this example, the `$product_id` and `$store_id` variables are taken directly from the user input (`$_GET`). If these inputs are not sanitized, an attacker can inject additional commands.

### Real-World Example: CVE-2021-3186

A notable real-world example of OS Command Injection is CVE-2021-3186, which affected the Jenkins Continuous Integration server. The vulnerability allowed attackers to execute arbitrary commands on the Jenkins server by manipulating certain parameters in the Jenkins API.

#### Impact

- **Unauthorized Access**: Attackers could gain access to the Jenkins server and execute commands.
- **Data Theft**: Sensitive information stored on the server could be accessed.
- **System Compromise**: Full control of the server could be achieved.

#### Exploit Details

The vulnerability was due to improper validation of user input in the Jenkins API. An attacker could craft a malicious request to inject commands, leading to remote code execution.

### Understanding the Lab Environment

In the lab environment described, the application uses user-supplied input to construct and execute a shell command. The goal is to exploit this vulnerability to execute the `whoami` command, which reveals the name of the current user.

### Setting Up the Lab

To access the lab, follow these steps:

1. Visit the URL: [PortSwigger Web Security Academy](https://portswigger.net/web-security).
2. Sign up for an account if you haven't already.
3. Log in to your account.
4. Navigate to the Academy section.
5. Select the learning path for command injection.
6. Choose the lab titled "OS Command Injection Simple Case."

### Using Burp Suite

Burp Suite is a powerful toolkit for web application security testing. We will use it to intercept and modify HTTP requests to exploit the vulnerability.

1. Open Burp Suite Community Edition.
2. Click "OK" and then "Next."
3. Close the initial setup window and start Burp Suite.

### Analyzing the Vulnerability

The lab contains an OS command injection vulnerability in the product stock checker. The application takes user-supplied `product_id` and `store_id` parameters and constructs a shell command using these inputs.

#### Example Request

Let's consider a typical request to the stock checker:

```http
GET /stock-check?product_id=123&store_id=456 HTTP/1.1
Host: vulnerable-app.com
User-Agent: Mozilla/5.0
Accept: */*
```

The server constructs and executes a command like:

```bash
stock_check 123 456
```

If the inputs are not sanitized, an attacker can inject additional commands.

### Exploiting the Vulnerability

To exploit the vulnerability, we need to inject a command that will be executed alongside the original command. One common approach is to use semicolons (`;`) to separate commands.

#### Injecting the `whoami` Command

We can modify the `product_id` parameter to include the `whoami` command:

```http
GET /stock-check?product_id=123;whoami&store_id=456 HTTP/1.1
Host: vulnerable-app.com
User-Agent: Mozilla/5.0
Accept: */*
```

This results in the following command being executed:

```bash
stock_check 123; whoami 456
```

The `whoami` command will be executed, revealing the name of the current user.

### Intercepting and Modifying Requests

Using Burp Suite, we can intercept and modify the HTTP request to exploit the vulnerability.

1. Configure your browser to use Burp Suite as a proxy.
2. Send the request to the stock checker.
3. In Burp Suite, go to the "Proxy" tab and intercept the request.
4. Modify the `product_id` parameter to include the `whoami` command.
5. Forward the modified request to the server.

#### Expected Response

The server should return the output of the `whoami` command along with the original command output.

```http
HTTP/1.1 200 OK
Date: Mon, 01 Jan 2024 00:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html
Content-Length: 20

current_user_name
```

### Common Pitfalls and Detection

#### Common Mistakes

- **Improper Input Validation**: Not validating or sanitizing user input.
- **Use of Unsafe Functions**: Using functions like `system()` or `shell_exec()` without proper precautions.
- **Lack of Contextual Awareness**: Not considering the context in which user input is used.

#### Detection Techniques

- **Static Analysis Tools**: Tools like SonarQube, Fortify, and Veracode can identify potential command injection vulnerabilities.
- **Dynamic Analysis Tools**: Tools like Burp Suite, OWASP ZAP, and Metasploit can help detect and exploit command injection vulnerabilities during runtime.
- **Manual Code Review**: Carefully reviewing code for unsafe function usage and lack of input validation.

### How to Prevent / Defend Against OS Command Injection

#### Secure Coding Practices

- **Input Validation**: Validate and sanitize all user inputs to ensure they do not contain malicious characters.
- **Avoid Unsafe Functions**: Use safer alternatives to functions like `system()` or `shell_exec()`.
- **Whitelisting**: Use whitelisting to restrict the set of valid inputs.

#### Example: Secure Code Implementation

Here is a comparison between insecure and secure code implementations:

**Insecure Code**

```php
<?php
$product_id = $_GET['product_id'];
$store_id = $_GET['store_id'];

$command = "stock_check $product_id $store_id";
$output = shell_exec($command);
echo "<pre>$output</pre>";
?>
```

**Secure Code**

```php
<?php
$product_id = filter_var($_GET['product_id'], FILTER_SANITIZE_NUMBER_INT);
$store_id = filter_var($_GET['store_id'], FILTER_SANITIZE_NUMBER_INT);

if (!ctype_digit($product_id) || !ctype_digit($store_id)) {
    die("Invalid input");
}

$command = "stock_check $product_id $store_id";
$output = shell_exec($command);
echo "<pre>$output</pre>";
?>
```

#### Configuration Hardening

- **Disable Unnecessary Features**: Disable features that are not required, such as shell access.
- **Least Privilege Principle**: Run the application with the least privilege necessary to perform its tasks.

#### Monitoring and Logging

- **Real-Time Monitoring**: Implement real-time monitoring to detect unusual activity.
- **Logging**: Maintain detailed logs of all system commands executed by the application.

### Conclusion

OS Command Injection is a serious vulnerability that can lead to significant security risks. By understanding the mechanisms behind this vulnerability and implementing secure coding practices, you can effectively prevent and defend against such attacks.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on different types of command injection vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

By working through these labs, you can gain practical experience in identifying and exploiting OS Command Injection vulnerabilities, as well as implementing effective defenses.

---
<!-- nav -->
[[Web Security (PortSwigger)/10-OS Command Injection/02-Lab 1 OS command injection simple case/00-Overview|Overview]] | [[02-OS Command Injection|OS Command Injection]]
