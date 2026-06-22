---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Comprehensive Guide to Command Injection

### In-depth Understanding of Command Injection

Command injection is a critical security vulnerability that occurs when an application constructs a command string using untrusted input and passes it to a system shell for execution. The attacker can manipulate the input to inject additional commands, leading to unauthorized access, data theft, or even complete control over the server.

### Key Concepts

#### Shell Environment

A shell is a command-line interface that interprets and executes commands entered by the user or a script. The shell reads the input, parses it, and then executes the corresponding commands.

#### Command Execution

When a command is executed, the shell performs several steps:

1. **Tokenization**: The shell breaks the input into tokens based on whitespace and special characters.
2. **Expansion**: The shell expands variables, wildcards, and other special characters.
3. **Command Execution**: The shell executes the parsed command.

For example, consider the command `echo $PATH`. The shell tokenizes the input into `echo` and `$PATH`, expands the `$PATH` variable, and then executes the `echo` command with the expanded value.

### Common Techniques for Command Injection

Attackers use various techniques to exploit command injection vulnerabilities:

- **Semicolon (`;`)**: Used to separate multiple commands.
- **Ampersand (`&`)**: Used to run commands in the background.
- **Pipe (`|`)**: Used to redirect the output of one command to another.
- **Parentheses (`()`)**: Used to group commands.

#### Example: Multiple Commands

An attacker can inject multiple commands using semicolons:

```python
import subprocess

def list_files(user_input):
    command = f"ls {user_input}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout
```

If an attacker inputs `; echo "Hello";`, the command becomes `ls ; echo "Hello";`, which first lists files and then prints "Hello".

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
3. **Use Parameterized Commands**: When constructing commands, use parameterized methods to avoid injecting user input directly into the command string.

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
[[01-Advanced Concepts in Command Injection|Advanced Concepts in Command Injection]] | [[Web Security (PortSwigger)/10-OS Command Injection/01-Command Injection Complete Guide/00-Overview|Overview]] | [[03-Introduction to Command Injection|Introduction to Command Injection]]
