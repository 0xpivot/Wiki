---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Introduction to Authentication Vulnerabilities

Authentication vulnerabilities are among the most critical security issues in web applications. They allow attackers to impersonate legitimate users, gain unauthorized access to sensitive data, and perform actions that should be restricted. One common type of authentication vulnerability is a broken password reset mechanism. In this section, we will delve into the details of such vulnerabilities, focusing on the specific scenario described in the lab: "Password Reset, Broken Logic."

### What is a Broken Password Reset Mechanism?

A broken password reset mechanism occurs when the process designed to help users regain access to their accounts through a forgotten password is flawed. These flaws can range from logical errors in the implementation to insufficient validation checks, making it possible for attackers to bypass intended security measures.

#### Why Does It Matter?

Broken password reset mechanisms are significant because they can lead to unauthorized access to user accounts. Once an attacker gains access, they can perform various malicious activities, such as stealing personal information, conducting financial fraud, or spreading malware. This can result in severe consequences for both the individual users and the organization hosting the application.

### How Does It Work Under the Hood?

To understand how a broken password reset mechanism works, let's break down the typical steps involved in a secure password reset process:

1. **Request Password Reset**: The user initiates a password reset request by providing their username or email address.
2. **Validation Check**: The system verifies the provided information to ensure it belongs to a valid user.
3. **Token Generation**: A unique token is generated and sent to the user via email or another secure channel.
4. **Reset Page Access**: The user clicks on the link containing the token, which directs them to a password reset page.
5. **Password Change**: The user enters a new password, which is then validated and stored securely.

In a broken password reset mechanism, one or more of these steps may be compromised, allowing an attacker to bypass the intended security controls.

### Real-World Examples

Recent real-world examples of broken password reset mechanisms include:

- **CVE-2021-3116**: A vulnerability in the WordPress plugin "User Registration" allowed attackers to reset passwords without proper validation.
- **CVE-2020-14882**: A flaw in the Joomla CMS allowed unauthorized password resets due to insufficient input validation.

These vulnerabilities highlight the importance of thorough testing and validation in the password reset process.

### Lab Setup

The lab we are working on is titled "Password Reset, Broken Logic." To access the lab, follow these steps:

1. Visit [PortSwigger Web Security Academy](https://portswigger.net/web-security).
2. Sign up for an account if you haven't already.
3. Navigate to the "Academy" section.
4. Search for "authentication labs."
5. Select lab number three titled "Password Reset, Broken Logic."

### Understanding the Lab Scenario

In this lab, you are tasked with exploiting a broken password reset functionality to reset Carlos' password and gain access to his account. The key steps involve:

1. Identifying the vulnerability in the password reset process.
2. Exploiting the vulnerability to reset Carlos' password.
3. Logging in with the newly set password to access Carlos' account.

### Detailed Steps to Exploit the Vulnerability

#### Step 1: Identify the Vulnerability

To identify the vulnerability, you need to analyze the password reset process. Let's assume the following steps are involved:

1. **Request Password Reset**: The user submits their username or email address.
2. **Validation Check**: The system checks if the provided information matches a valid user.
3. **Token Generation**: A unique token is generated and sent to the user.
4. **Reset Page Access**: The user clicks on the link containing the token to access the password reset page.
5. **Password Change**: The user sets a new password.

However, in this lab, the validation check might be flawed, allowing an attacker to bypass it.

#### Step 2: Exploit the Vulnerability

To exploit the vulnerability, you need to manipulate the request to bypass the validation check. Here’s a detailed breakdown:

1. **Intercept the Request**: Use Burp Suite to intercept the request sent when initiating a password reset.
2. **Analyze the Request**: Examine the request to identify any parameters that might be vulnerable to manipulation.
3. **Manipulate the Request**: Modify the request to bypass the validation check. For example, if the validation check is based on a simple string comparison, you might be able to bypass it by using a different format or value.

Here is an example of how the request might look:

```http
POST /reset-password HTTP/1.1
Host: vulnerable-app.com
Content-Type: application/x-www-form-urlencoded

username=carlos&email=carlos@example.com
```

By manipulating the `email` parameter, you might be able to bypass the validation check.

#### Step 3: Reset the Password

Once you have successfully bypassed the validation check, you can proceed to reset the password. Here’s how the request might look:

```http
POST /reset-password HTTP/1.1
Host: vulnerable-app.com
Content-Type: application/x-www-form-urlencoded

token=generated-token&new_password=newpassword123
```

After submitting this request, the password for Carlos' account will be reset.

#### Step 4: Log In with the New Password

Finally, log in to Carlos' account using the newly set password. Here’s how the login request might look:

```http
POST /login HTTP/1.1
Host: vulnerable-app.com
Content-Type: application/x-www-form-urlencoded

username=carlos&password=newpassword123
```

Upon successful login, you will be redirected to Carlos' account page.

### Common Pitfalls and Mistakes

When dealing with broken password reset mechanisms, there are several common pitfalls and mistakes to avoid:

1. **Insufficient Validation**: Ensure that all inputs are thoroughly validated to prevent bypassing the validation check.
2. **Weak Tokens**: Use strong, unique tokens that cannot be easily guessed or manipulated.
3. **Improper Token Management**: Ensure that tokens are properly managed and expire after a short period to prevent reuse.

### How to Prevent / Defend Against Broken Password Reset Mechanisms

To prevent and defend against broken password reset mechanisms, follow these best practices:

#### Secure Coding Practices

1. **Input Validation**: Validate all inputs to ensure they match the expected format and content.
2. **Strong Tokens**: Generate strong, unique tokens that are difficult to guess or manipulate.
3. **Token Expiry**: Set a short expiration time for tokens to prevent reuse.

#### Example of Secure Code

Here is an example of secure code for handling password reset requests:

```python
import secrets
import hashlib
from datetime import datetime, timedelta

def generate_reset_token(user_id):
    token = secrets.token_urlsafe(16)
    expiry_time = datetime.now() + timedelta(minutes=15)
    store_token(user_id, token, expiry_time)
    return token

def validate_reset_token(user_id, token):
    stored_token, expiry_time = retrieve_token(user_id)
    if stored_token == token and expiry_time > datetime.now():
        return True
    return False

def reset_password(user_id, new_password):
    if validate_reset_token(user_id, token):
        hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
        update_password(user_id, hashed_password)
        invalidate_token(user_id)
```

#### Configuration Hardening

1. **Secure Email Transmission**: Ensure that emails containing reset links are transmitted securely using TLS.
2. **Rate Limiting**: Implement rate limiting to prevent brute-force attacks on the password reset functionality.
3. **Logging and Monitoring**: Enable logging and monitoring to detect and respond to suspicious activity.

#### Detection and Mitigation

1. **Automated Testing**: Use automated tools like Burp Suite to test for vulnerabilities in the password reset process.
2. **Penetration Testing**: Conduct regular penetration testing to identify and mitigate potential vulnerabilities.
3. **Security Audits**: Perform regular security audits to ensure compliance with best practices and standards.

### Conclusion

Understanding and addressing broken password reset mechanisms is crucial for maintaining the security of web applications. By following best practices and implementing secure coding techniques, you can significantly reduce the risk of unauthorized access and protect user accounts from exploitation.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs to practice identifying and exploiting broken password reset mechanisms.
- **OWASP Juice Shop**: Provides a simulated web application with numerous security vulnerabilities, including broken password reset mechanisms.
- **DVWA (Damn Vulnerable Web Application)**: Another popular platform for practicing web security skills, including password reset vulnerabilities.

By engaging in these labs, you can gain practical experience and reinforce your understanding of authentication vulnerabilities and how to defend against them.

---
<!-- nav -->
[[Web Security (PortSwigger)/13-Authentication Vulnerabilities/04-Lab 3 Password reset broken logic/00-Overview|Overview]] | [[02-Authentication Vulnerabilities Broken Logic in Password Reset|Authentication Vulnerabilities Broken Logic in Password Reset]]
