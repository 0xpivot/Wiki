---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Detailed Example: Vulnerable vs. Secure Code

### Vulnerable Code Example

Consider the following PHP code snippet that constructs a command using user input:

```php
<?php
$user_input = $_GET['cmd'];
$command = "ls " . $user_input;
exec($command, $output);
print_r($output);
?>
```

In this example, an attacker could inject a malicious command by setting the `cmd` parameter to something like `; rm -rf /`.

### Secure Code Example

To secure this code, we can use a whitelist to validate the input and avoid direct command execution:

```php
<?php
function validate_input($input) {
    $allowed_commands = ['dir', 'ls', 'pwd'];
    if (!in_array($input, $allowed_commands)) {
        throw new Exception("Invalid command");
    }
    return $input;
}

try {
    $user_input = validate_input($_GET['cmd']);
    $command = "ls " . escapeshellarg($user_input);
    exec($command, $output);
    print_r($output);
} catch (Exception $e) {
    echo "Error: " . $e->getMessage();
}
?>
```

In this secure version, we validate the input against a list of allowed commands and use `escapeshellarg()` to safely escape the input.

### How to Prevent / Defend Against OS Command Injection

#### Secure Coding Practices

1. **Use Built-In Functions**: Instead of executing OS commands directly, use built-in functions that are designed to handle specific tasks securely. For example, use `os.path.join()` for file path manipulation.

2. **Input Validation**: Always validate and sanitize user input. Use whitelisting to restrict input to a known safe set of characters.

3. **Least Privilege Principle**: Run applications with the least privileges necessary. This limits the potential damage if an attacker gains control.

#### Detection and Mitigation

1. **Static Code Analysis**: Use tools like SonarQube or Fortify to scan your codebase for potential command injection vulnerabilities.

2.. **Dynamic Analysis**: Employ dynamic analysis tools like Burp Suite or OWASP ZAP to test your application for runtime vulnerabilities.

3. **Logging and Monitoring**: Implement logging and monitoring to detect unusual activity that might indicate an injection attempt.

### Real-World Example: CVE-2020-14882

CVE-2020-14882 is a command injection vulnerability found in the Apache Struts framework. An attacker could inject malicious commands through the `Content-Type` header, leading to remote code execution. This highlights the importance of thorough input validation and the use of secure coding practices.

### Practice Labs

For hands-on practice with OS Command Injection, consider the following resources:

- **PortSwigger Web Security Academy**: Offers a comprehensive module on OS Command Injection, including interactive labs and detailed explanations.
- **OWASP Juice Shop**: A deliberately insecure web application that includes various security vulnerabilities, including OS Command Injection.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application that can be used to practice exploiting and defending against OS Command Injection.

By thoroughly understanding the concepts, practicing with real-world examples, and implementing secure coding practices, you can effectively prevent and mitigate OS Command Injection vulnerabilities in your applications.

### Conclusion

OS Command Injection is a serious security vulnerability that can have severe consequences if not properly addressed. By avoiding direct OS command execution, validating and sanitizing user input, and following secure coding practices, you can significantly reduce the risk of such vulnerabilities. Regularly testing your applications with static and dynamic analysis tools, and implementing robust logging and monitoring, can help detect and mitigate these issues before they can be exploited.

---
<!-- nav -->
[[09-Crafting Command Injection Payloads|Crafting Command Injection Payloads]] | [[Web Security (PortSwigger)/10-OS Command Injection/01-Command Injection Complete Guide/00-Overview|Overview]] | [[11-Detailed Mechanics of Command Injection|Detailed Mechanics of Command Injection]]
