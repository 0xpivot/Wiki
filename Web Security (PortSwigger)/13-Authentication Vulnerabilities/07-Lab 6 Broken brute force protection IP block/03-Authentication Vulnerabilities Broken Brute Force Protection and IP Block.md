---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Authentication Vulnerabilities: Broken Brute Force Protection and IP Block

### Introduction to Authentication Vulnerabilities

Authentication vulnerabilities are among the most critical issues in web security. They can allow attackers to gain unauthorized access to user accounts, leading to data breaches, financial losses, and reputational damage. One such vulnerability is the lack of effective brute force protection mechanisms, which can be exploited to guess passwords through repeated login attempts.

### Understanding Brute Force Attacks

A brute force attack is a method used by attackers to systematically guess passwords until the correct one is found. This type of attack can be highly effective against weak or commonly used passwords. The attacker typically uses automated tools to generate and test numerous password combinations against a login interface.

#### Example of a Brute Force Attack

Consider a scenario where an attacker is trying to gain access to a user's account on a web application. The attacker might use a tool like `Hydra` to automate the process of guessing passwords. Here’s an example of how Hydra might be configured:

```bash
hydra -l carlos -P /path/to/password/list.txt http://target.com/login
```

In this command:
- `-l carlos`: Specifies the username to target.
- `-P /path/to/password/list.txt`: Specifies the path to a file containing a list of potential passwords.
- `http://target.com/login`: Specifies the URL of the login page.

### Importance of Brute Force Protection

To mitigate the risk of brute force attacks, web applications must implement robust mechanisms to prevent or limit the number of login attempts. These mechanisms can include:

- **Account Lockout**: Temporarily locking an account after a certain number of failed login attempts.
- **Rate Limiting**: Limiting the frequency at which login attempts can be made from a specific IP address.
- **Captcha**: Requiring users to solve a captcha after a certain number of failed attempts.

### Detailed Analysis of the Lab Scenario

Let's analyze the scenario described in the lab to understand the vulnerability and its implications.

#### Initial Setup

The lab involves attempting to log in to an account using incorrect credentials. The steps are as follows:

1. **First Attempt**:
    - Username: `Carlos`
    - Password: Randomly generated
    - Result: Incorrect password

2. **Second Attempt**:
    - Username: `Carlos`
    - Password: Another randomly generated password
    - Result: Incorrect password

3. **Third Attempt**:
    - Username: `Carlos`
    - Password: Yet another randomly generated password
    - Result: Soft lockout message ("You have made too many incorrect login attempts. Please try again in one minute.")

#### HTTP Request and Response Analysis

Each login attempt generates an HTTP POST request to the server. Below is an example of the HTTP request and response for the first attempt:

```http
POST /login HTTP/1.1
Host: target.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 34

username=Carlos&password=randompassword
```

Response:

```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 123

<!DOCTYPE html>
<html>
<head>
<title>Login</title>
</head>
<body>
<p>Incorrect password.</p>
</body>
</html>
```

#### Vulnerability Analysis

The vulnerability in this scenario is the lack of proper brute force protection. Specifically, the application does not effectively prevent repeated login attempts, allowing an attacker to continue guessing passwords even after multiple failures.

### Detailed Explanation of the Vulnerability

#### Verbose Error Messages

One of the key issues highlighted in the lab is the presence of verbose error messages. When a user enters an incorrect password, the application returns a message indicating whether the username or password is incorrect. This information can be exploited by attackers to enumerate valid usernames in the application.

For example, if an attacker tries a series of usernames and receives a "Username not found" message for some but not others, they can deduce which usernames are valid.

#### Soft Lockout Mechanism

The application implements a soft lockout mechanism, which temporarily locks the account after a certain number of failed login attempts. However, this mechanism is not robust enough to prevent brute force attacks. Specifically, the lockout period is relatively short (one minute), and the counter does not reset upon a successful login attempt.

### Real-World Examples and Recent Breaches

Several high-profile breaches have been attributed to weak authentication mechanisms and the absence of effective brute force protection. For instance:

- **CVE-2021-26084**: A vulnerability in the WordPress REST API allowed attackers to bypass rate limiting and perform brute force attacks on user accounts.
- **Equifax Data Breach (2017)**: The breach was partly due to the absence of proper brute force protection mechanisms, allowing attackers to gain unauthorized access to sensitive data.

### How to Prevent / Defend Against Brute Force Attacks

#### Secure Coding Practices

To prevent brute force attacks, developers should implement the following secure coding practices:

1. **Use Strong Password Policies**: Enforce strong password requirements, including length, complexity, and regular updates.
2. **Implement Account Lockout**: Temporarily lock accounts after a specified number of failed login attempts.
3. **Rate Limiting**: Limit the frequency of login attempts from a specific IP address.
4. **Use Captcha**: Require users to solve a captcha after a certain number of failed attempts.

#### Example of Secure Code Implementation

Here is an example of how to implement account lockout and rate limiting in a Python Flask application:

```python
from flask import Flask, request, jsonify
from datetime import datetime, timedelta
import hashlib

app = Flask(__name__)

# In-memory storage for demonstration purposes
failed_attempts = {}
locked_accounts = {}

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    # Check if account is locked
    if username in locked_accounts:
        current_time = datetime.now()
        lockout_end_time = locked_accounts[username]
        if current_time < lockout_end_time:
            return jsonify({"message": "Account is locked. Try again later."}), 403

    # Check failed attempts
    if username in failed_attempts:
        failed_attempts[username] += 1
    else:
        failed_attempts[username] = 1

    # Simulate checking the password
    if failed_attempts[username] >= 3:
        # Lock the account for 1 minute
        locked_accounts[username] = datetime.now() + timedelta(minutes=1)
        del failed_attempts[username]
        return jsonify({"message": "Too many failed attempts. Account locked."}), 403

    # Simulate successful login
    if hash_password(password) == "hashed_password":
        del failed_attempts[username]
        return jsonify({"message": "Login successful."}), 200
    else:
        return jsonify({"message": "Incorrect password."}), 401

if __name__ == '__main__':
    app.run(debug=True)
```

#### Configuration Hardening

In addition to secure coding practices, configuration hardening is essential to prevent brute force attacks. For example, in an Nginx server, you can configure rate limiting using the `limit_req` module:

```nginx
http {
    ...
    limit_req_zone $binary_remote_addr zone=login_limit:10m rate=1r/s;

    server {
        listen 80;
        server_name example.com;

        location /login {
            limit_req zone=login_limit burst=5 nodelay;
            proxy_pass http://backend;
        }
    }
}
```

In this configuration:
- `limit_req_zone`: Defines a shared memory zone to store the number of requests per IP address.
- `limit_req`: Applies rate limiting to the `/login` endpoint, allowing a maximum of 1 request per second with a burst of 5 requests.

### Detection and Monitoring

To detect and respond to brute force attacks, organizations should implement monitoring and logging mechanisms. For example, using a tool like `fail2ban`, you can automatically block IP addresses that exhibit suspicious login behavior:

```bash
[sshd]
enabled  = true
port     = ssh
filter   = sshd
logpath  = /var/log/auth.log
maxretry = 5
bantime  = 3600
```

In this configuration:
- `enabled`: Enables the rule.
- `port`: Specifies the port to monitor (SSH in this case).
- `filter`: Specifies the filter to use (e.g., `sshd` for SSH login attempts).
- `logpath`: Specifies the log file to monitor.
- `maxretry`: Specifies the maximum number of failed login attempts before blocking the IP address.
- `bantime`: Specifies the duration for which the IP address is blocked.

### Conclusion

Effective brute force protection is crucial for maintaining the security of web applications. By implementing robust mechanisms such as account lockout, rate limiting, and captchas, organizations can significantly reduce the risk of unauthorized access. Additionally, secure coding practices and configuration hardening are essential to ensure that these mechanisms are implemented correctly and effectively.

### Hands-On Labs

To practice and reinforce the concepts learned in this chapter, consider the following hands-on labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various web security topics, including authentication vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that contains a variety of security vulnerabilities.

These labs provide practical experience in identifying and mitigating authentication vulnerabilities, helping to solidify your understanding of the concepts discussed in this chapter.

---
<!-- nav -->
[[02-Authentication Vulnerabilities Broken Brute Force Protection IP Block|Authentication Vulnerabilities Broken Brute Force Protection IP Block]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/07-Lab 6 Broken brute force protection IP block/00-Overview|Overview]] | [[04-Authentication Vulnerabilities Broken Brute Force Protection|Authentication Vulnerabilities Broken Brute Force Protection]]
