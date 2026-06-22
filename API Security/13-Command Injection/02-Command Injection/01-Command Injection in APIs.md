---
course: API Security
topic: Command Injection
tags: [api-security]
---

## Command Injection in APIs

### Introduction to Command Injection

Command injection is a type of security vulnerability that occurs when an attacker can inject malicious commands into a program through user input. This can happen in various contexts, including web applications, APIs, and command-line interfaces. In the context of APIs, command injection vulnerabilities can arise when an application takes user input and uses it to execute shell commands without proper sanitization or validation.

The primary goal of an attacker exploiting a command injection vulnerability is to execute arbitrary commands on the server, which can lead to unauthorized access, data theft, or even complete control over the server. Understanding how command injection works and how to prevent it is crucial for securing your APIs.

### Background Theory

#### What is Command Injection?

Command injection occurs when an application constructs a command string using untrusted input and then executes that command. The attacker can manipulate the input to inject additional commands or alter the intended command structure. This can result in the execution of unintended commands, leading to security breaches.

For example, consider an API endpoint that retrieves system uptime information by executing a shell command:

```python
import subprocess

def get_uptime(input):
    command = f"uptime {input}"
    return subprocess.check_output(command, shell=True)

# Example usage
print(get_uptime(""))
```

If the `input` parameter is not properly sanitized, an attacker could inject a malicious command. For instance, setting `input` to `"; ls"` would result in the following command being executed:

```sh
uptime "; ls"
```

This would first run the `uptime` command and then list the contents of the current directory (`ls`). This demonstrates how an attacker can chain commands to perform unintended actions.

### Real-World Examples

#### Recent CVEs and Breaches

One notable example of a command injection vulnerability is CVE-2021-3186, which affected the Jenkins Continuous Integration server. This vulnerability allowed attackers to execute arbitrary commands on the server by manipulating environment variables passed to a plugin. The exploitation of this vulnerability led to several high-profile breaches, highlighting the severity of command injection attacks.

Another example is CVE-2020-14882, which affected the Apache Struts framework. This vulnerability allowed attackers to inject malicious commands through the `Content-Type` header, leading to remote code execution. These examples underscore the importance of securing APIs against command injection attacks.

### How Command Injection Works

#### Execution Context

To understand how command injection works, it's essential to consider the execution context. When an application constructs a command string and executes it using a shell, the shell interprets the command string and performs the specified actions. If the command string includes user input, the shell can interpret parts of the input as additional commands or arguments.

For instance, consider the following Python code snippet:

```python
import subprocess

def execute_command(user_input):
    command = f"echo {user_input}"
    return subprocess.check_output(command, shell=True)

# Example usage
print(execute_command("Hello; ls"))
```

In this example, the `user_input` parameter is used to construct the command string. If the user input is `"Hello; ls"`, the constructed command becomes:

```sh
echo Hello; ls
```

When this command is executed, the shell first runs `echo Hello` and then runs `ls`. This demonstrates how an attacker can inject additional commands by manipulating the input.

### Common Pitfalls

#### Improper Input Validation

One of the most common pitfalls in command injection vulnerabilities is improper input validation. Applications often assume that user input is safe and do not perform adequate checks before using it to construct command strings. This assumption can lead to severe security issues.

For example, consider the following Node.js code snippet:

```javascript
const { exec } = require('child_process');

function getSystemInfo(input) {
    const command = `uptime ${input}`;
    exec(command, (error, stdout, stderr) => {
        console.log(stdout);
    });
}

// Example usage
getSystemInfo("; ls");
```

In this example, the `input` parameter is used to construct the command string. If the `input` parameter is set to `"; ls"`, the constructed command becomes:

```sh
uptime "; ls"
```

When this command is executed, the shell first runs `uptime` and then runs `ls`. This demonstrates how improper input validation can lead to command injection vulnerabilities.

### Detection and Prevention

#### How to Detect Command Injection Vulnerabilities

Detecting command injection vulnerabilities requires a combination of static analysis and dynamic testing. Static analysis tools can identify potential vulnerabilities by analyzing the code for patterns that may lead to command injection. Dynamic testing involves simulating attacks to see if the application is vulnerable to command injection.

For example, using a static analysis tool like SonarQube can help identify instances where user input is used to construct command strings without proper validation. Additionally, using a dynamic testing tool like Burp Suite can help simulate attacks and verify if the application is vulnerable to command injection.

#### How to Prevent Command Injection Vulnerabilities

Preventing command injection vulnerabilities involves several best practices:

1. **Input Validation**: Always validate and sanitize user input before using it to construct command strings. Ensure that the input does not contain characters that can be interpreted as command delimiters or special characters.

2. **Use Safe APIs**: Instead of using shell commands, use safer APIs that do not involve executing shell commands. For example, in Python, use the `subprocess.run()` function with the `shell=False` parameter to avoid shell interpretation.

3. **Least Privilege Principle**: Run the application with the least privileges necessary. This limits the damage that can be caused by a successful command injection attack.

4. **Security Testing**: Regularly perform security testing, including static analysis and dynamic testing, to identify and mitigate command injection vulnerabilities.

### Secure Coding Practices

#### Example of Vulnerable Code

Consider the following vulnerable Python code snippet:

```python
import subprocess

def get_uptime(input):
    command = f"uptime {input}"
    return subprocess.check_output(command, shell=True)

# Example usage
print(get_uptime("; ls"))
```

In this example, the `input` parameter is used to construct the command string. If the `input` parameter is set to `"; ls"`, the constructed command becomes:

```sh
uptime "; ls"
```

When this command is executed, the shell first runs `uptime` and then runs `ls`.

#### Example of Secure Code

To secure the above code, we can use the `subprocess.run()` function with the `shell=False` parameter to avoid shell interpretation. Here is the secure version of the code:

```python
import subprocess

def get_uptime(input):
    command = ["uptime", input]
    return subprocess.run(command, capture_output=True, text=True).stdout

# Example usage
print(get_uptime("; ls"))
```

In this secure version, the `input` parameter is passed as a separate argument to the `uptime` command, preventing the shell from interpreting it as additional commands.

### Configuration Hardening

#### Secure Configuration Examples

To further harden the configuration, ensure that the application runs with the least privileges necessary. For example, in a Docker container, use a non-root user to run the application:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

USER 1000

CMD ["python", "app.py"]
```

In this Dockerfile, the `USER 1000` directive ensures that the application runs as a non-root user, limiting the damage that can be caused by a successful command injection attack.

### Hands-On Labs

#### Recommended Labs

To practice and reinforce your understanding of command injection vulnerabilities in APIs, consider the following hands-on labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on command injection vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application that includes command injection challenges.
- **DVWA (Damn Vulnerable Web Application)**: Provides a variety of web application vulnerabilities, including command injection.

These labs provide practical experience in identifying and mitigating command injection vulnerabilities, helping you to better secure your APIs.

### Conclusion

Command injection is a serious security vulnerability that can lead to unauthorized access and control over the server. By understanding how command injection works, detecting and preventing vulnerabilities, and practicing secure coding and configuration, you can significantly reduce the risk of command injection attacks in your APIs.

---
<!-- nav -->
[[API Security/13-Command Injection/02-Command Injection/00-Overview|Overview]] | [[API Security/13-Command Injection/02-Command Injection/02-Command Injection|Command Injection]]
