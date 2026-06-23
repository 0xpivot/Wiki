---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Weak Password Complexity Requirements

One of the most common authentication vulnerabilities is the use of weak password complexity requirements. This occurs when the application does not enforce strong password policies, making it easier for attackers to guess or brute-force passwords.

### What Are Weak Password Complexity Requirements?

Weak password complexity requirements refer to the lack of stringent rules for creating passwords. Common issues include:

- **No Minimum Length Requirement**: Passwords can be too short, making them easy to guess.
- **No Character Diversity Requirement**: Passwords may consist of only letters or numbers, reducing their complexity.
- **No Prohibition Against Common Words**: Passwords may include common words or phrases, which are easily guessed.

### Why Are Weak Password Complexity Requirements Dangerous?

Weak password complexity requirements make it easier for attackers to guess or brute-force passwords. This can lead to unauthorized access to user accounts and potentially administrative privileges.

### How to Find Weak Password Complexity Requirements

To identify weak password complexity requirements, follow these steps:

1. **Review Password Policy Documentation**: Check if the application provides any documentation on password complexity requirements.
2. **Test Password Creation**: Attempt to create passwords with varying levels of complexity to see if the application enforces any rules.
3. **Use Automated Tools**: Utilize tools like `Burp Suite` or `OWASP ZAP` to automate the testing process.

### Example: Testing Password Complexity Requirements

Consider an application where you are testing the password creation process. You can use the following steps to identify weak password complexity requirements:

1. **Create a Short Password**:
    ```plaintext
    Username: testuser
    Password: pass
    ```
    If the application allows this password, it indicates a lack of minimum length requirement.

2. **Create a Password with Only Letters**:
    ```plaintext
    Username: testuser
    Password: abcdefgh
    ```
    If the application allows this password, it indicates a lack of character diversity requirement.

3. **Create a Password with a Common Word**:
    ```plaintext
    Username: testuser
    Password: password123
    ```
    If the application allows this password, it indicates a lack of prohibition against common words.

### Exploiting Weak Password Complexity Requirements

Once you have identified weak password complexity requirements, you can exploit them using techniques such as:

- **Brute-Force Attacks**: Use tools like `Hydra` or `John the Ripper` to attempt guessing passwords.
- **Dictionary Attacks**: Use pre-defined lists of common passwords to attempt login.

### Real-World Example: Equifax Breach

In the Equifax breach, attackers exploited a vulnerability in Apache Struts that allowed them to bypass authentication. This was possible because the application did not enforce strong password policies, making it easier for attackers to guess or brute-force passwords.

### How to Prevent / Defend Against Weak Password Complexity Requirements

To prevent weak password complexity requirements, implement the following measures:

1. **Enforce Strong Password Policies**:
    - Require a minimum length (e.g., 8 characters).
    - Require a mix of uppercase and lowercase letters, numbers, and special characters.
    - Prohibit the use of common words and phrases.

2. **Use Multi-Factor Authentication (MFA)**: Implement MFA to add an additional layer of security.

3. **Educate Users**: Provide guidance on creating strong passwords and the importance of password security.

### Secure Code Fix: Weak Password Complexity Requirements

Here is an example of how to implement strong password complexity requirements in a web application:

#### Vulnerable Code
```python
# Vulnerable code
def validate_password(password):
    return True
```

#### Secure Code
```python
import re

def validate_password(password):
    if len(password) < 8:
        return False
    if not re.search("[a-z]", password):
        return False
    if not re.search("[A-Z]", password):
        return False
    if not re.search("[0-9]", password):
        return False
    if not re.search("[!@#$%^&*()_+-=]", password):
        return False
    return True
```

### Detection and Prevention

To detect and prevent weak password complexity requirements, use the following tools and techniques:

- **Automated Scanners**: Use tools like `Burp Suite` or `OWASP ZAP` to scan for weak password policies.
- **Penetration Testing**: Conduct regular penetration tests to identify and mitigate authentication vulnerabilities.
- **Security Audits**: Perform periodic security audits to ensure compliance with strong password policies.

### Conclusion

Weak password complexity requirements are a significant authentication vulnerability that can be exploited by attackers. By implementing strong password policies and using multi-factor authentication, you can significantly reduce the risk of unauthorized access.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers modules on authentication vulnerabilities and how to test for them.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing authentication testing.
- **DVWA (Damn Vulnerable Web Application)**: Includes scenarios for testing weak password complexity requirements.

By thoroughly understanding and testing for authentication vulnerabilities, you can help ensure the security of web applications.

---

This detailed explanation covers the concept of weak password complexity requirements, their dangers, how to find and exploit them, real-world examples, and how to prevent and defend against them. The secure code fix and detection/prevention methods are also provided to ensure a comprehensive understanding of the topic.

---
<!-- nav -->
[[25-Vulnerable Transmission of Credentials|Vulnerable Transmission of Credentials]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/01-Authentication Vulnerabilities Complete Guide/00-Overview|Overview]] | [[27-Weak Password Requirements|Weak Password Requirements]]
