---
course: Web Security
topic: OS Command Injection
tags: [web-security]
---

## Blacklist vs. Whitelist Validation

### Blacklist Validation

Blacklist validation involves identifying and blocking known malicious inputs. However, this approach is generally ineffective because attackers can often find ways to bypass the blacklist.

#### Example of Blacklist Bypass

Consider a Python function that attempts to block certain characters:

```python
def validate_input(user_input):
    forbidden_chars = [';', '&', '|']
    for char in forbidden_chars:
        if char in user_input:
            raise ValueError("Invalid input")
    return user_input
```

An attacker could bypass this by using URL encoding or other obfuscation techniques. For example, the character `&` can be encoded as `%26`, which would pass the validation check but still be interpreted as a command separator by the shell.

### Whitelist Validation

Whitelist validation involves allowing only a predefined set of safe inputs. This approach is much more robust because it explicitly defines what is allowed, making it harder for attackers to inject malicious commands.

#### Example of Whitelist Validation

Here’s an example of a Python function that uses whitelist validation to ensure that only alphanumeric characters are accepted:

```python
import re

def validate_input(user_input):
    if not re.match(r'^[a-zA-Z0-9]*$', user_input):
        raise ValueError("Invalid input")
    return user_input
```

This function uses a regular expression to check if the input consists solely of alphanumeric characters. Any input that does not match this pattern will be rejected.

### How to Prevent / Defend Against OS Command Injection

#### Secure Coding Practices

1. **Avoid Direct OS Command Execution**: Whenever possible, use built-in library functions instead of executing OS commands directly. For example, use `os.path.join()` instead of constructing file paths manually.

2. **Input Validation**: Always validate and sanitize user input. Use whitelisting to restrict input to a known safe set of characters.

3. **Least Privilege Principle**: Run applications with the least privileges necessary. This limits the potential damage if an attacker gains control.

#### Detection and Mitigation

1. **Static Code Analysis**: Use tools like SonarQube or Fortify to scan your codebase for potential command injection vulnerabilities.

2. **Dynamic Analysis**: Employ dynamic analysis tools like Burp Suite or OWASP ZAP to test your application for runtime vulnerabilities.

3. **Logging and Monitoring**: Implement logging and monitoring to detect unusual activity that might indicate an injection attempt.

### Real-World Example: CVE-2020-14882

CVE-2020-14882 is a command injection vulnerability found in the Apache Struts framework. An attacker could inject malicious commands through the `Content-Type` header, leading to remote code execution. This highlights the importance of thorough input validation and the use of secure coding practices.

---
<!-- nav -->
[[07-Background Theory|Background Theory]] | [[Web Security (PortSwigger)/10-OS Command Injection/01-Command Injection Complete Guide/00-Overview|Overview]] | [[09-Crafting Command Injection Payloads|Crafting Command Injection Payloads]]
