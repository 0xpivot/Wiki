---
course: API Security
topic: Command Injection
tags: [api-security]
---

## Command Injection

### Introduction

Command injection is a type of security vulnerability that occurs when an attacker is able to inject malicious commands into an application, which are then executed by the underlying operating system. This can lead to unauthorized access, data theft, and even complete control over the system. Understanding the mechanics of command injection, its potential impacts, and how to defend against it is crucial for securing applications that interact with the operating system.

### Background Theory

#### What is Command Injection?

Command injection occurs when an application takes untrusted input from a user and passes it to a system shell for execution. The shell interprets the input and executes the commands, potentially leading to unintended behavior. For instance, consider an application that allows users to specify a command to run on the server:

```python
import os

def run_command(user_input):
    os.system(user_input)
```

If `user_input` is not properly sanitized, an attacker can inject additional commands. For example, if the user input is `"ls; rm -rf /"`, the `os.system()` function will execute both `ls` and `rm -rf /`, which can cause significant damage.

#### How Does Command Injection Work?

The core mechanism of command injection relies on the fact that many programming languages and frameworks allow developers to execute shell commands using functions like `os.system()`, `subprocess.Popen()`, or similar. These functions pass the input directly to the shell, which then parses and executes the commands.

Consider the following Python example:

```python
import subprocess

def run_shell_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout
```

In this example, the `shell=True` argument tells `subprocess.run()` to pass the command through the shell. If `command` is not sanitized, an attacker can inject additional commands.

### Real-World Examples

#### Recent CVEs and Breaches

One notable example of a command injection vulnerability is CVE-2021-21972, which affected the Jenkins Pipeline plugin. The vulnerability allowed attackers to inject arbitrary shell commands, leading to remote code execution.

Another example is CVE-2021-32799, which affected the Apache Struts framework. An attacker could inject malicious commands via the `Content-Type` header, leading to command execution on the server.

### Detailed Mechanics

#### Example Scenario

Let's consider a web application that allows users to specify a command to run on the server. The application might have a form where users can enter a command, and the server executes it.

```html
<form action="/run-command" method="POST">
    <input type="text" name="command" placeholder="Enter command">
    <button type="submit">Run Command</button>
</form>
```

On the server side, the application might look like this:

```python
from flask import Flask, request, subprocess

app = Flask(__name__)

@app.route('/run-command', methods=['POST'])
def run_command():
    command = request.form['command']
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout
```

If an attacker submits a command like `"ls; rm -rf /"`, the server will execute both `ls` and `rm -rf /`.

### Detection and Prevention

#### How to Detect Command Injection Vulnerabilities

To detect command injection vulnerabilities, you can perform static analysis and dynamic testing:

1. **Static Analysis**: Use tools like SonarQube, Fortify, or Bandit to scan your codebase for potential command injection vulnerabilities.
2. **Dynamic Testing**: Use tools like Burp Suite, OWASP ZAP, or Metasploit to test your application for command injection vulnerabilities.

#### How to Prevent Command Injection

1. **Input Validation**: Always validate and sanitize user input. Ensure that the input does not contain any shell metacharacters or commands.
2. **Use Safe APIs**: Avoid using functions that pass commands directly to the shell. Instead, use safer alternatives like `subprocess.run()` without `shell=True`.
3. **Least Privilege Principle**: Run your application with the least privileges necessary. This limits the damage that can be done if a command injection vulnerability is exploited.

### Secure Coding Practices

#### Vulnerable Code Example

Here is an example of vulnerable code:

```python
import subprocess

def run_shell_command(command):
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout
```

#### Secure Code Example

Here is the same functionality implemented securely:

```python
import subprocess

def run_safe_command(args):
    result = subprocess.run(args, capture_output=True, text=True)
    return result.stdout

# Usage
safe_command = ["ls", "-l"]
output = run_safe_command(safe_command)
print(output)
```

### Real-World Exploits

#### Recent Attack Scenarios

One recent attack scenario involved a command injection vulnerability in a web application that allowed attackers to execute arbitrary commands on the server. The attackers used this vulnerability to gain unauthorized access to sensitive data and even take control of the server.

### Hands-On Labs

For hands-on practice with command injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on command injection.
- **OWASP Juice Shop**: Contains various vulnerabilities, including command injection.
- **DVWA (Damn Vulnerable Web Application)**: Provides a range of web application vulnerabilities, including command injection.

### Conclusion

Command injection is a serious security vulnerability that can have severe consequences. By understanding the mechanics of command injection, detecting potential vulnerabilities, and implementing secure coding practices, you can significantly reduce the risk of such attacks. Always validate and sanitize user input, use safe APIs, and follow the principle of least privilege to ensure the security of your applications.

---
<!-- nav -->
[[01-Command Injection in APIs|Command Injection in APIs]] | [[API Security/13-Command Injection/02-Command Injection/00-Overview|Overview]] | [[API Security/13-Command Injection/02-Command Injection/03-Practice Questions & Answers|Practice Questions & Answers]]
