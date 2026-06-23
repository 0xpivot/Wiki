---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Introduction to Command Injection

Command injection is a type of security vulnerability that occurs when an attacker is able to inject arbitrary commands into a system through a vulnerable application. This allows the attacker to execute commands on the underlying operating system with the privileges of the application. Understanding command injection is crucial for developers and security professionals as it can lead to severe consequences such as data theft, system compromise, and unauthorized access.

### What is Command Injection?

Command injection is a technique used by attackers to execute arbitrary commands on a target system. This is achieved by exploiting a vulnerability in the application that allows user input to be interpreted as part of a shell command. The vulnerability typically arises due to improper validation or sanitization of user input.

#### Example Scenario

Consider a web application that allows users to specify a filename to download. The application might construct a shell command to retrieve the file using the `cat` command:

```python
filename = request.GET['filename']
os.system(f"cat {filename}")
```

If an attacker can control the `filename` parameter, they could inject additional commands. For instance, setting `filename` to `; rm -rf /` would result in the following command being executed:

```bash
cat ; rm -rf /
```

This would delete all files on the system, demonstrating the severity of command injection vulnerabilities.

### Types of Command Injection Vulnerabilities

There are several types of command injection vulnerabilities, each with its own characteristics and potential impacts:

1. **Shell Command Injection**: This occurs when user input is directly included in a shell command. The most common form is when the application constructs a command string and passes it to a function like `system()` or `exec()`.

2. **Environment Variable Injection**: This type of injection involves manipulating environment variables to influence the behavior of a command. For example, setting an environment variable that is used in a command can alter its execution.

3. **Argument Injection**: This happens when user input is passed as arguments to a command. If the arguments are not properly sanitized, an attacker can inject additional arguments or commands.

### Conditions for Command Injection Vulnerability

For a page to be vulnerable to command injection, certain conditions must be met:

1. **User Input**: The application must accept user input that is then used in constructing a shell command.
2. **Improper Validation**: User input must not be properly validated or sanitized before being included in the command.
3. **Execution Context**: The command must be executed in a context where the user input can be interpreted as part of the command.

### Commonality of Command Injection Vulnerabilities

Command injection vulnerabilities are relatively common, especially in applications that interact with the underlying operating system. According to recent statistics, command injection vulnerabilities account for a significant portion of reported security issues. Real-world examples include:

- **CVE-2021-21972**: A command injection vulnerability in the Jenkins plugin for GitLab integration allowed attackers to execute arbitrary commands on the Jenkins server.
- **CVE-2020-14882**: A command injection vulnerability in the Apache Struts framework allowed attackers to execute arbitrary commands on the server.

### Finding Command Injection Vulnerabilities

To identify command injection vulnerabilities, both white-box and black-box approaches can be used.

#### White-Box Testing

White-box testing involves examining the application's source code to identify potential vulnerabilities. Key areas to focus on include:

- **Functions that Execute Shell Commands**: Look for functions like `system()`, `exec()`, `shell_exec()`, etc.
- **User Input Handling**: Check how user input is handled and whether it is properly validated or sanitized before being included in a command.
- **Environment Variables**: Verify that environment variables are not influenced by user input in a way that could alter command execution.

#### Black-Box Testing

Black-box testing involves interacting with the application without access to the source code. Techniques include:

- **Fuzzing**: Send various inputs to the application to see if any cause unexpected behavior.
- **Error Messages**: Look for error messages that reveal information about the underlying command structure.
- **Time-Based Attacks**: Inject commands that cause delays to confirm successful injection.

### Exploiting Command Injection Vulnerabilities

Once a command injection vulnerability is identified, an attacker can exploit it to achieve their goals. Common exploitation techniques include:

- **Executing Arbitrary Commands**: Inject commands to perform actions such as deleting files, creating new files, or executing other programs.
- **Privilege Escalation**: If the application runs with elevated privileges, an attacker can use command injection to gain those same privileges.
- **Data Exfiltration**: Use command injection to read sensitive files or exfiltrate data.

#### Example Exploitation

Consider the previous example where the application constructs a command using user input:

```python
filename = request.GET['filename']
os.system(f"cat {filename}")
```

An attacker could set `filename` to `; id` to execute the `id` command, which displays the current user's identity:

```bash
cat ; id
```

The output would reveal the user ID and group ID of the process executing the command, potentially leading to further exploitation.

### Preventing and Mitigating Command Injection Attacks

Preventing command injection requires a combination of proper coding practices, input validation, and secure configurations.

#### Secure Coding Practices

1. **Avoid Using Shell Commands**: Whenever possible, avoid using shell commands and instead use built-in functions or libraries that do not involve shell execution.
2. **Sanitize User Input**: Validate and sanitize user input to ensure it does not contain malicious characters or sequences.
3. **Use Safe Functions**: Use safe functions that do not interpret user input as part of a command. For example, use `subprocess.run()` with the `shell=False` parameter.

#### Input Validation

Input validation is crucial to prevent command injection. Ensure that user input is checked against a whitelist of allowed characters and patterns. For example:

```python
import re

def validate_filename(filename):
    # Allow only alphanumeric characters and underscores
    if re.match(r'^[a-zA-Z0-9_]+$', filename):
        return True
    return False

filename = request.GET['filename']
if validate_filename(filename):
    os.system(f"cat {filename}")
else:
    print("Invalid filename")
```

#### Secure Configuration

Secure configurations can help mitigate the impact of command injection vulnerabilities:

1. **Least Privilege Principle**: Run the application with the least privilege necessary to perform its tasks.
2. **Filesystem Permissions**: Set appropriate permissions on files and directories to restrict access.
3. **Environment Variables**: Ensure that environment variables are not influenced by user input.

### Detection and Prevention

Detecting and preventing command injection requires a multi-layered approach:

1. **Static Analysis Tools**: Use static analysis tools to scan the application's source code for potential vulnerabilities.
2. **Dynamic Analysis Tools**: Employ dynamic analysis tools to test the application for runtime vulnerabilities.
3. **Security Policies**: Implement security policies that enforce secure coding practices and regular security audits.

#### Secure Code Example

Here is an example of secure code that avoids command injection:

```python
import subprocess

filename = request.GET['filename']
if validate_filename(filename):
    try:
        result = subprocess.run(['cat', filename], capture_output=True, text=True)
        print(result.stdout)
    except Exception as e:
        print(f"Error: {e}")
else:
    print("Invalid filename")
```

In this example, `subprocess.run()` is used with `shell=False` to prevent shell interpretation of the command.

### Conclusion

Command injection is a serious security vulnerability that can have severe consequences. By understanding the technical details, identifying vulnerabilities, and implementing secure coding practices, developers and security professionals can effectively prevent and mitigate these attacks.

### Practice Labs

For hands-on practice with command injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on command injection and other web security topics.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that contains numerous security vulnerabilities for educational purposes.

These labs provide practical experience in identifying and exploiting command injection vulnerabilities, as well as learning how to defend against them.

---

This comprehensive guide covers the essential aspects of command injection, providing deep insights into its technical details, real-world examples, and practical steps to prevent and mitigate such vulnerabilities.

---
<!-- nav -->
[[02-Comprehensive Guide to Command Injection|Comprehensive Guide to Command Injection]] | [[Web Security (PortSwigger)/10-OS Command Injection/01-Command Injection Complete Guide/00-Overview|Overview]] | [[04-Introduction to OS Command Injection|Introduction to OS Command Injection]]
