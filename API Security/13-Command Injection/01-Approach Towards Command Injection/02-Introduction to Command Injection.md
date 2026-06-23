---
course: API Security
topic: Command Injection
tags: [api-security]
---

## Introduction to Command Injection

Command injection is a type of security vulnerability that occurs when an attacker is able to inject malicious commands into an application, which are then executed by the operating system. This can lead to unauthorized access, data theft, or even complete control of the system. Understanding command injection is crucial for securing APIs and web applications.

### What is Command Injection?

Command injection happens when an application takes input from an untrusted source and uses it to construct a command that is executed by the operating system. The input can come from various sources such as user input, URL parameters, cookies, or other external inputs. If the application does not properly validate or sanitize this input, an attacker can inject malicious commands that will be executed with the privileges of the application.

#### Example Scenario

Consider an application that allows users to search for files on the server. The application constructs a shell command using the user input and executes it. An attacker could manipulate the input to inject additional commands, leading to unauthorized actions.

```mermaid
sequenceDiagram
    participant User
    participant Application
    participant OS
    User->>Application: Search for "file.txt; rm -rf /"
    Application->>OS: Execute "ls file.txt; rm -rf /"
    OS-->>Application: Result of command execution
```

### How Does Command Injection Work?

The core mechanism of command injection involves the following steps:

1. **Input Collection**: The application collects input from an untrusted source.
2. **Command Construction**: The input is used to construct a command string.
3. **Command Execution**: The constructed command is executed by the operating system.
4. **Privilege Escalation**: If the command is malicious, it can execute with the privileges of the application, potentially leading to severe consequences.

#### Example Code

Here is a simple example of a vulnerable Python script that constructs and executes a shell command based on user input:

```python
import subprocess

def search_file(user_input):
    command = f"ls {user_input}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

# Vulnerable usage
user_input = "file.txt; rm -rf /"
print(search_file(user_input))
```

In this example, the `subprocess.run` function is used with `shell=True`, which allows the command to be executed through the shell. An attacker can inject a semicolon (`;`) to append additional commands, leading to potential damage.

### Real-World Examples

Command injection vulnerabilities have been found in numerous real-world applications. Here are some recent examples:

1. **CVE-2021-39211**: A command injection vulnerability was discovered in the `nginx` web server. The vulnerability allowed attackers to execute arbitrary commands by manipulating the `Host` header in HTTP requests.

2. **CVE-2022-22965**: A command injection vulnerability was found in the `Apache Struts` framework. Attackers could exploit this vulnerability to execute arbitrary commands on the server.

### Detection and Prevention

Detecting and preventing command injection requires a combination of static analysis, dynamic testing, and proper coding practices.

#### Static Analysis

Static analysis tools can help identify potential command injection vulnerabilities by analyzing the code for unsafe command execution patterns. Tools like SonarQube, Fortify, and Veracode can be used for this purpose.

#### Dynamic Testing

Dynamic testing involves simulating attacks against the application to check for vulnerabilities. Tools like Burp Suite, OWASP ZAP, and Metasploit can be used to test for command injection.

#### Secure Coding Practices

To prevent command injection, follow these secure coding practices:

1. **Avoid Using Shell Commands**: Avoid using shell commands whenever possible. Instead, use built-in functions or libraries that do not involve shell execution.
2. **Sanitize Input**: Validate and sanitize all user input to ensure it does not contain malicious characters or commands.
3. **Use Safe Libraries**: Use libraries and frameworks that provide safe methods for executing commands, such as `subprocess.run` without `shell=True`.

### Secure Code Example

Here is an example of a secure Python script that avoids using shell commands:

```python
import os

def search_file(user_input):
    try:
        # Sanitize input to remove dangerous characters
        sanitized_input = os.path.basename(user_input)
        if os.path.exists(sanitized_input):
            return f"File exists: {sanitized_input}"
        else:
            return f"File does not exist: {sanitized_input}"
    except Exception as e:
        return f"Error: {str(e)}"

# Secure usage
user_input = "file.txt; rm -rf /"
print(search_file(user_input))
```

In this example, the `os.path.basename` function is used to sanitize the input, ensuring that it does not contain directory traversal or command injection attempts.

### How to Prevent / Defend Against Command Injection

#### Detection

1. **Static Analysis**: Use static analysis tools to scan your codebase for potential command injection vulnerabilities.
2. **Dynamic Testing**: Use dynamic testing tools to simulate attacks and identify vulnerabilities.

#### Prevention

1. **Avoid Shell Commands**: Avoid using shell commands whenever possible. Use built-in functions or libraries that do not involve shell execution.
2. **Sanitize Input**: Validate and sanitize all user input to ensure it does not contain malicious characters or commands.
3. **Use Safe Libraries**: Use libraries and frameworks that provide safe methods for executing commands.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of the code:

**Vulnerable Code**

```python
import subprocess

def search_file(user_input):
    command = f"ls {user_input}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

# Vulnerable usage
user_input = "file.txt; rm -rf /"
print(search_file(user_input))
```

**Secure Code**

```python
import os

def search_file(user_input):
    try:
        # Sanitize input to remove dangerous characters
        sanitized_input = os.path.basename(user_input)
        if os.path.exists(sanitized_input):
            return f"File exists: {sanitized_input}"
        else:
            return f"File does not exist: {sanitized_input}"
    except Exception as e:
        return f"Error: {str(e)}"

# Secure usage
user_input = "file.txt; rm -rf /"
print(search_file(user_input))
```

### Conclusion

Command injection is a serious security vulnerability that can lead to significant damage if not properly addressed. By understanding the mechanisms behind command injection, detecting potential vulnerabilities, and implementing secure coding practices, developers can significantly reduce the risk of such attacks.

### Practice Labs

For hands-on practice with command injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on command injection.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security exploits, including command injection.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for practicing penetration testing and security assessments.

By engaging with these labs, you can gain practical experience in identifying and mitigating command injection vulnerabilities.

---
<!-- nav -->
[[01-Command Injection Overview|Command Injection Overview]] | [[API Security/13-Command Injection/01-Approach Towards Command Injection/00-Overview|Overview]] | [[03-Command Injection in APIs|Command Injection in APIs]]
