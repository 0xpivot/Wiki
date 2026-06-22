---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Detailed Mechanics of Command Injection

### Understanding the Shell Environment

To fully grasp command injection, it's essential to understand the shell environment and how commands are executed. A shell is a command-line interface that interprets and executes commands entered by the user or a script. The shell reads the input, parses it, and then executes the corresponding commands.

#### Shell Parsing

When a command is executed, the shell performs several steps:

1. **Tokenization**: The shell breaks the input into tokens based on whitespace and special characters.
2. **Expansion**: The shell expands variables, wildcards, and other special characters.
3. **Command Execution**: The shell executes the parsed command.

For example, consider the command `echo $PATH`. The shell tokenizes the input into `echo` and `$PATH`, expands the `$PATH` variable, and then executes the `echo` command with the expanded value.

### Command Injection in Different Contexts

Command injection vulnerabilities can occur in various contexts within web applications. Here are some common scenarios:

#### Form Inputs

Web forms often accept user input and pass it to backend scripts for processing. If the input is not properly sanitized, an attacker can inject malicious commands.

#### URL Parameters

URL parameters can also be used to inject commands. For example, consider a URL like `http://example.com/script.php?cmd=ls`. If the `cmd` parameter is not sanitized, an attacker can inject a malicious command.

#### API Endpoints

API endpoints that accept user input can also be vulnerable to command injection. For example, consider an endpoint that accepts a command parameter and executes it.

### Real-World Examples

Several high-profile breaches have been caused by command injection vulnerabilities:

- **CVE-2021-21972**: A command injection vulnerability was found in the Jenkins plugin `git-client`. An attacker could inject malicious commands through the `GIT_SSH` environment variable.
- **CVE-2020-14882**: A command injection vulnerability in the `docker-compose` tool allowed attackers to execute arbitrary commands on the host system.

These examples highlight the importance of securing applications against command injection attacks.

### Detection and Prevention

Detecting and preventing command injection requires a multi-faceted approach:

1. **Input Validation**: Ensure that user input is properly validated and sanitized.
2. **Secure Coding Practices**: Avoid using system shells for executing commands whenever possible.
3. **Security Tools**: Use static analysis tools to identify potential command injection vulnerabilities.

### Secure Coding Practices

To prevent command injection, follow these best practices:

1. **Avoid Using System Shells**: Instead of using system shells, use language-specific APIs that handle command execution securely.
2. **Sanitize Input**: Validate and sanitize user input to ensure it does not contain malicious characters.
3.. **Use Parameterized Commands**: When constructing commands, use parameterized methods to avoid injecting user input directly into the command string.

#### Example: Secure Code

Here’s how you can modify the previous example to prevent command injection:

```python
import subprocess

def list_files(user_input):
    # Sanitize user input
    sanitized_input = user_input.replace(";", "").replace("&", "")
    
    # Use subprocess.run with a list to avoid shell injection
    command = ["ls", sanitized_input]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout
```

In this example, we sanitize the user input by removing potentially dangerous characters and use a list to pass the command to `subprocess.run`, which avoids the use of the shell.

### Detection Tools

Several tools can help detect command injection vulnerabilities:

- **Static Analysis Tools**: Tools like SonarQube and Fortify can analyze code for potential command injection vulnerabilities.
- **Dynamic Analysis Tools**: Tools like Burp Suite and OWASP ZAP can simulate attacks and detect vulnerabilities during runtime.

### Hands-On Labs

To practice detecting and preventing command injection vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on command injection.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application with numerous security vulnerabilities.

### Conclusion

Command injection is a serious security vulnerability that can lead to significant damage if not properly addressed. By understanding the mechanics of command injection, validating and sanitizing user input, and using secure coding practices, developers can significantly reduce the risk of such vulnerabilities. Regularly testing and auditing code with security tools is essential to maintaining the security of web applications.

---
<!-- nav -->
[[10-Detailed Example Vulnerable vs. Secure Code|Detailed Example Vulnerable vs. Secure Code]] | [[Web Security (PortSwigger)/10-OS Command Injection/01-Command Injection Complete Guide/00-Overview|Overview]] | [[12-Exploiting Command Injection|Exploiting Command Injection]]
