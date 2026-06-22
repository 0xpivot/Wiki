---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Practical Examples and Scenarios

### Real-World Scenarios

Let's explore some practical scenarios where command injection can occur and how to mitigate these risks.

#### Scenario 1: File Upload with Command Injection

Consider a web application that allows users to upload files and processes them using a system command. If the filename is not properly sanitized, an attacker can inject a malicious command.

```python
import os

def process_file(filename):
    # Dangerous: Directly using user input in a system command
    os.system(f"cat {filename}")
```

To mitigate this, sanitize the filename and use a safer method to execute the command:

```python
import os

def process_file(filename):
    # Sanitize the filename
    sanitized_filename = os.path.basename(filename)
    
    # Use subprocess.run with a list to avoid shell injection
    result = subprocess.run(["cat", sanitized_filename], capture_output=True, text=True)
    return result.stdout
```

#### Scenario 2: Environment Variable Injection

Consider a script that uses an environment variable to construct a command. If the environment variable is not properly sanitized, an attacker can inject a malicious command.

```bash
export CMD="malicious_command"
script.sh
```

To mitigate this, validate and sanitize the environment variable before using it:

```bash
export CMD="safe_command"
script.sh
```

#### Scenario 3: API Endpoint with Command Injection

Consider an API endpoint that accepts a command parameter and executes it. If the command is not properly sanitized, an attacker can inject a malicious command.

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/execute', methods=['POST'])
def execute():
    command = request.form['command']
    # Dangerous: Directly using user input in a system command
    os.system(command)
    return "Command executed"

if __name__ == '__main__':
    app.run()
```

To mitigate this, sanitize the command and use a safer method to execute it:

```python
from flask import Flask, request
import subprocess

app = Flask(__name__)

@app.route('/execute', methods=['POST'])
def execute():
    command = request.form['command']
    # Sanitize the command
    sanitized_command = command.replace(";", "").replace("&", "")
    
    # Use subprocess.run with a list to avoid shell injection
    result = subprocess.run(sanitized_command.split(), capture_output=True, text=True)
    return result.stdout

if __name__ == '__main__':
    app.run()
```

### Real-World Examples

Several high-profile breaches have been caused by command injection vulnerabilities:

- **CVE-2-21972**: A command injection vulnerability was found in the Jenkins plugin `git-client`. An attacker could inject malicious commands through the `GIT_SSH` environment variable.
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
[[17-OS Command Injection|OS Command Injection]] | [[Web Security (PortSwigger)/10-OS Command Injection/01-Command Injection Complete Guide/00-Overview|Overview]] | [[19-Preventing and Defending Against Command Injection|Preventing and Defending Against Command Injection]]
