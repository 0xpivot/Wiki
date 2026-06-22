---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## OS Command Injection

### What is OS Command Injection?

OS Command Injection is a type of security vulnerability that occurs when an application executes operating system commands that include input provided by users. This vulnerability allows attackers to inject malicious commands into the application, potentially leading to unauthorized access, data theft, or even complete control over the system.

#### Why Does OS Command Injection Matter?

Command injection vulnerabilities can have severe consequences. An attacker can leverage these vulnerabilities to execute arbitrary commands on the server, bypass authentication mechanisms, and gain unauthorized access to sensitive information. This can lead to significant financial losses, reputational damage, and legal repercussions for the affected organization.

#### How Does OS Command Injection Work?

When an application constructs and executes a command using user-supplied input without proper sanitization or validation, it becomes susceptible to command injection attacks. The attacker can manipulate the input to inject additional commands or modify existing ones, leading to unintended behavior.

### Example Scenario: Ping Command Injection

Consider a web application that allows users to ping an IP address and displays the result. The application might construct a command like `ping <user_input>` and execute it. If the user input is not properly validated, an attacker can inject additional commands.

#### Normal Use Case

Let's look at a normal use case where Alice pings an IP address:

```python
import subprocess

def ping_ip(ip_address):
    command = f"ping {ip_address}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

# Example usage
output = ping_ip("127.0.0.1")
print(output)
```

In this scenario, Alice enters `127.0.0.1` as the IP address. The application constructs the command `ping 127.0.0.1` and executes it. The output is then displayed to Alice.

#### Attack Scenario

Now, let's consider an attack scenario where an attacker injects additional commands:

```python
import subprocess

def ping_ip(ip_address):
    command = f"ping {ip_address}"
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

# Example usage with injection
output = ping_ip("127.0.0.1; cat /etc/passwd")
print(output)
```

In this case, the attacker inputs `127.0.0.1; cat /etc/passwd`. The application constructs the command `ping 127.0.0.1; cat /etc/passwd` and executes it. The output includes both the result of the `ping` command and the contents of the `/etc/passwd` file.

### Real-World Examples

#### Recent CVEs and Breaches

One notable example of a command injection vulnerability is CVE-2021-3129, which affected the Jenkins CI/CD platform. The vulnerability allowed attackers to inject arbitrary commands through the `JENKINS_HOME` environment variable, leading to remote code execution.

Another example is CVE-2020-14882, which affected the Apache Struts framework. This vulnerability allowed attackers to inject commands through the `Content-Type` header, leading to remote code execution.

### How to Detect Command Injection Vulnerabilities

Detecting command injection vulnerabilities requires a combination of static analysis, dynamic analysis, and manual testing.

#### Static Analysis

Static analysis tools can identify potential command injection vulnerabilities by scanning the codebase for patterns that involve executing user-supplied input. Tools like SonarQube, Fortify, and Veracode can help identify such issues.

#### Dynamic Analysis

Dynamic analysis involves testing the application with various inputs to see if it behaves as expected. Tools like Burp Suite, OWASP ZAP, and Metasploit can be used to simulate attacks and detect vulnerabilities.

#### Manual Testing

Manual testing involves manually crafting inputs to test the application's behavior. This can be done using tools like curl, Postman, or even a simple Python script.

### How to Prevent / Defend Against Command Injection

#### Secure Coding Practices

To prevent command injection vulnerabilities, follow these secure coding practices:

1. **Input Validation**: Validate all user-supplied input to ensure it meets the expected format and constraints.
2. **Use Safe APIs**: Use safe APIs that do not allow direct execution of user-supplied input. For example, use `subprocess.run()` without `shell=True`.
3. **Whitelist Input**: Use whitelisting to restrict input to a predefined set of acceptable values.
4. **Escape User Input**: Escape user-supplied input to prevent it from being interpreted as part of the command.

#### Example of Secure Code

Here is an example of secure code that prevents command injection:

```python
import subprocess

def ping_ip(ip_address):
    if not ip_address.isnumeric():
        raise ValueError("Invalid IP address")
    
    command = ["ping", "-c", "1", ip_address]
    result = subprocess.run(command, capture_output=True, text=True)
    return result.stdout

# Example usage
output = ping_ip("127.0.0.1")
print(output)
```

In this example, the `ping_ip` function validates the input and uses a list of arguments instead of a string to construct the command. This prevents the injection of additional commands.

#### Configuration Hardening

Hardening the application's configuration can also help prevent command injection vulnerabilities. Ensure that the application runs with the least privileges necessary and that unnecessary services are disabled.

#### Detection and Monitoring

Implement logging and monitoring to detect and respond to potential command injection attempts. Use intrusion detection systems (IDS) and security information and event management (SIEM) tools to monitor for suspicious activity.

### Practice Labs

To practice and understand command injection vulnerabilities, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on command injection.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web application vulnerabilities.

### Conclusion

OS Command Injection is a serious security vulnerability that can have severe consequences. By understanding how it works, detecting it, and implementing secure coding practices, you can prevent and defend against such attacks. Always validate and sanitize user input, use safe APIs, and implement configuration hardening to ensure the security of your applications.

---
<!-- nav -->
[[16-OS Command Injection Vulnerability|OS Command Injection Vulnerability]] | [[Web Security (PortSwigger)/10-OS Command Injection/01-Command Injection Complete Guide/00-Overview|Overview]] | [[18-Practical Examples and Scenarios|Practical Examples and Scenarios]]
