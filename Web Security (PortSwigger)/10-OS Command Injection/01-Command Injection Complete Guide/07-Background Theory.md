---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Background Theory

### Understanding Operating Systems and Shells

Before diving deeper into command injection, it's important to understand the basics of operating systems and shells. An operating system (OS) is a collection of software that manages computer hardware resources and provides common services for computer programs. A shell is a program that interprets and executes commands entered by the user or a script.

#### Types of Shells

There are several types of shells commonly used in different operating systems:

- **Bash (Bourne Again SHell)**: The default shell in many Linux distributions.
- **Zsh (Z Shell)**: An enhanced version of Bash with additional features.
- **Csh (C Shell)**: A shell that uses C-like syntax.
- **Fish (Friendly Interactive SHell)**: A user-friendly shell designed for ease of use.

Each shell has its own set of commands and syntax, but they all share the ability to execute system commands.

### Command Execution in Programming Languages

Programming languages often provide mechanisms to execute system commands. Here are some common ways to execute commands in popular programming languages:

#### Python

Python provides the `subprocess` module for executing system commands:

```python
import subprocess

# Execute a command and capture the output
result = subprocess.run(["ls", "-l"], capture_output=True, text=True)
print(result.stdout)
```

#### Node.js

Node.js provides the `child_process` module for executing system commands:

```javascript
const { exec } = require('child_process');

exec('ls -l', (error, stdout, stderr) => {
  if (error) {
    console.error(`Error: ${error.message}`);
    return;
  }
  if (stderr) {
    console.error(`Stderr: ${stderr}`);
    return;
  }
  console.log(`Stdout: ${stdout}`);
});
```

#### Java

Java provides the `Runtime` class for executing system commands:

```java
import java.io.BufferedReader;
import java.io.InputStreamReader;

public class Main {
    public static void main(String[] args) throws Exception {
        Process p = Runtime.getRuntime().exec("ls -l");
        BufferedReader in = new BufferedReader(new InputStreamReader(p.getInputStream()));
        String line;
        while ((line = in.readLine()) != null) {
            System.out.println(line);
        }
        in.close();
    }
}
```

### Command Injection Mechanics

Command injection vulnerabilities occur when an application constructs a command string using untrusted input and passes it to a system shell for execution. The attacker can manipulate the input to inject additional commands.

#### Example: Unsanitized User Input

Consider the following Python code that constructs a command using user input:

```python
import subprocess

def list_files(user_input):
    command = f"ls {user_input}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout
```

If an attacker inputs `; rm -rf /`, the command becomes `ls ; rm -rf /`, which first lists files and then attempts to delete all files on the server.

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
[[06-Advanced Topics in Command Injection|Advanced Topics in Command Injection]] | [[Web Security (PortSwigger)/10-OS Command Injection/01-Command Injection Complete Guide/00-Overview|Overview]] | [[08-Blacklist vs. Whitelist Validation|Blacklist vs. Whitelist Validation]]
