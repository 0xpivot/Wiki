---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## How to Prevent / Defend Against OS Command Injection

### Secure Coding Practices

1. **Input Validation**: Validate and sanitize all user input to ensure it does not contain malicious characters.
2. **Use Safe APIs**: Utilize safe APIs that do not rely on shell commands. For example, use `subprocess.run` in Python instead of `os.system`.

#### Vulnerable Code Example

```python
import os

cmd = input("Enter a command: ")
os.system(cmd)
```

#### Secure Code Example

```python
import subprocess

cmd = input("Enter a command: ")
subprocess.run(["echo", cmd], check=True)
```

### Configuration Hardening

1. **Disable Unnecessary Features**: Disable features that are not required, such as shell access in web applications.
2. **Least Privilege Principle**: Run the application with the least privileges necessary to perform its tasks.

### Detection and Monitoring

1. **Log Analysis**: Regularly review logs for suspicious activity, such as unexpected shell commands.
2. **IDS/IPS Systems**: Implement Intrusion Detection and Prevention Systems to monitor for command injection attempts.

### Real-World Example: CVE-2021-21972 Mitigation

For the Jenkins vulnerability (CVE-2021-21972), the mitigation involved updating to a patched version of Jenkins and ensuring that environment variables are properly validated and sanitized.

### Practice Labs

To practice and master OS Command Injection, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs specifically designed to teach and test command injection vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application that includes several command injection challenges.
- **DVWA (Damn Vulnerable Web Application)**: Provides a range of web application vulnerabilities, including command injection.

By thoroughly understanding the concepts, techniques, and defenses related to OS Command Injection, you can better protect web applications from this serious security threat.

---
<!-- nav -->
[[Web Security (PortSwigger)/10-OS Command Injection/03-Lab 2 Blind OS command injection with time delays/03-Hands-On Practice|Hands-On Practice]] | [[Web Security (PortSwigger)/10-OS Command Injection/03-Lab 2 Blind OS command injection with time delays/00-Overview|Overview]] | [[05-Implementing Time-Based OS Command Injection|Implementing Time-Based OS Command Injection]]
