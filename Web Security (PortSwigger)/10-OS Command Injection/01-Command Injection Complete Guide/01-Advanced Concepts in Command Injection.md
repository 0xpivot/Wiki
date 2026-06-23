---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Advanced Concepts in Command Injection

### Advanced Techniques for Exploitation

While basic command injection involves injecting simple commands, advanced techniques can allow attackers to perform more sophisticated attacks. These techniques often involve chaining commands, using environment variables, and exploiting specific shell features.

#### Chaining Commands

Attackers can chain multiple commands together using semicolons (`;`) or ampersands (`&`). This allows them to execute a series of commands in sequence or in parallel.

```bash
command1; command2; command3
```

or

```bash
command1 & command2 & command3
```

#### Using Environment Variables

Environment variables can be manipulated to inject commands. For example, if a script uses an environment variable to construct a command, an attacker can set the variable to include malicious commands.

```bash
export CMD="malicious_command"
script.sh
```

#### Exploiting Shell Features

Some shells have features that can be exploited for command injection. For example, the `$(...)` syntax in Bash can be used to execute commands and substitute their output.

```bash
command=$(malicious_command)
```

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
[[Web Security (PortSwigger)/10-OS Command Injection/01-Command Injection Complete Guide/00-Overview|Overview]] | [[02-Comprehensive Guide to Command Injection|Comprehensive Guide to Command Injection]]
