---
course: Web Security
topic: HTTP Host Header Attacks
tags: [web-security]
---

## HTTP Host Header Attacks: Password Reset Poisoning

### Background Theory

The HTTP `Host` header is a crucial component of the HTTP protocol used to specify the domain name of the server being contacted. This header is essential because it allows a single IP address to serve multiple websites (virtual hosting). However, this flexibility can also introduce security vulnerabilities, particularly when the `Host` header is not properly validated or sanitized.

### What is a Host Header Attack?

A Host Header Attack occurs when an attacker manipulates the `Host` header to trick the server into performing actions that it would not normally execute. One common form of this attack is **password reset poisoning**, where an attacker crafts a malicious link that, when clicked, resets the victim's password to a value chosen by the attacker.

### Why Does This Matter?

Password reset poisoning can lead to unauthorized access to user accounts, which can have severe consequences such as financial loss, data theft, or reputational damage. This type of attack exploits the trust users place in legitimate-looking links sent via email or other communication channels.

### How Does It Work Under the Hood?

To understand how this attack works, let's break down the steps involved:

1. **Crafting the Malicious Link**: The attacker creates a link that includes a manipulated `Host` header.
2. **Sending the Link**: The attacker sends this link to the victim through email, social media, or other means.
3. **Victim Clicks the Link**: When the victim clicks the link, their browser sends a request to the server with the manipulated `Host` header.
4. **Server Processing**: The server processes the request based on the `Host` header, potentially leading to unintended behavior such as resetting the password.

### Real-World Example: CVE-2021-21972

In 2021, a vulnerability was discovered in the WordPress plugin WPML Multilingual CMS (CVE-2021-21972). This vulnerability allowed attackers to manipulate the `Host` header to redirect users to malicious sites during the password reset process. This real-world example highlights the importance of validating and sanitizing input, especially headers like `Host`.

### Complete Code Example

Let's walk through a complete example of how this attack might occur. We'll start with the vulnerable code and then show how to fix it.

#### Vulnerable Code

Consider a simple password reset endpoint that does not validate the `Host` header:

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/reset_password', methods=['POST'])
def reset_password():
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    
    # Assume this function updates the user's password
    update_user_password(new_password)
    
    return "Password reset successful"

if __name__ == '__main__':
    app.run()
```

#### Malicious Request

An attacker could craft a request with a manipulated `Host` header:

```http
POST /reset_password HTTP/1.1
Host: evil.example.com
Content-Type: application/x-www-form-urlencoded

new_password=Peter&confirm_password=Peter
```

#### Server Response

The server would respond with:

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=utf-8

Password reset successful
```

### How to Prevent / Defend

#### Detection

To detect potential Host Header attacks, you can monitor your logs for unusual `Host` headers. Tools like Splunk or ELK Stack can help you set up alerts for suspicious activity.

#### Prevention

1. **Validate the Host Header**: Ensure that the `Host` header matches a list of valid domains.
2. **Sanitize Input**: Always sanitize and validate all input, including headers.
3. **Use Secure Coding Practices**: Implement secure coding practices to avoid common vulnerabilities.

#### Secure Code Fix

Here’s how you can modify the code to validate the `Host` header:

```python
from flask import Flask, request

app = Flask(__name__)

ALLOWED_HOSTS = ['example.com']

@app.route('/reset_password', methods=['POST'])
def reset_password():
    host_header = request.headers.get('Host')
    
    if host_header not in ALLOWED_HOSTS:
        return "Invalid Host header", 400
    
    new_password = request.form['new_password']
    confirm_password = request.form['confirm_password']
    
    # Assume this function updates the user's password
    update_user_password(new_password)
    
    return "Password reset successful"

if __name__ == '__main__':
    app.run()
```

#### Full HTTP Request and Response

**Malicious Request:**

```http
POST /reset_password HTTP/1.1
Host: evil.example.com
Content-Type: application/x-www-form-urlencoded

new_password=Peter&confirm_password=
```

**Server Response:**

```http
HTTP/1.1 400 Bad Request
Content-Type: text/html; charset=utf-8

Invalid Host header
```

### Common Pitfalls

1. **Overlooking Input Validation**: Failing to validate the `Host` header can lead to unexpected behavior.
2. **Assuming Trusted Input**: Trusting input from untrusted sources can result in security vulnerabilities.
3. **Ignoring Edge Cases**: Not considering all possible inputs can leave your application vulnerable.

### Practice Labs

For hands-on practice with HTTP Host Header attacks, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs covering different types of web security vulnerabilities, including Host Header attacks.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web hacking techniques.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for learning web security.

These labs provide a safe environment to explore and understand the mechanics of Host Header attacks and how to defend against them.

### Conclusion

Understanding and defending against HTTP Host Header attacks is crucial for maintaining the security of web applications. By validating and sanitizing input, implementing secure coding practices, and monitoring for suspicious activity, you can significantly reduce the risk of such attacks. Always stay vigilant and keep your knowledge up-to-date with the latest security practices and tools.

---
<!-- nav -->
[[Web Security (PortSwigger)/16-HTTP Host Header Attacks/02-Lab 1 Basic password reset poisoning/01-Introduction to HTTP Host Header Attacks|Introduction to HTTP Host Header Attacks]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/02-Lab 1 Basic password reset poisoning/00-Overview|Overview]] | [[Web Security (PortSwigger)/16-HTTP Host Header Attacks/02-Lab 1 Basic password reset poisoning/03-Understanding HTTP Host Header Attacks|Understanding HTTP Host Header Attacks]]
