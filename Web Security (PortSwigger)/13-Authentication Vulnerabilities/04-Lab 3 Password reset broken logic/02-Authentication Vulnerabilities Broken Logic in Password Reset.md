---
course: Web Security
topic: Authentication Vulnerabilities
tags: [web-security]
---

## Authentication Vulnerabilities: Broken Logic in Password Reset

### Introduction

Authentication vulnerabilities are among the most critical issues in web security. They can lead to unauthorized access, data breaches, and other severe consequences. One common type of authentication vulnerability is broken logic in password reset mechanisms. In this section, we will delve into the details of such vulnerabilities, their implications, and how to prevent them.

### Background Theory

#### What is Authentication?

Authentication is the process of verifying the identity of a user, device, or system. It ensures that the entity attempting to access a resource is indeed who they claim to be. Common methods of authentication include:

- **Username and Password**: The most widely used method.
- **Multi-Factor Authentication (MFA)**: Combines two or more independent credentials.
- **Biometric Authentication**: Uses unique biological characteristics like fingerprints or facial recognition.

#### What is a Password Reset Mechanism?

A password reset mechanism allows users to regain access to their accounts if they forget their passwords. Typically, this involves sending a reset link or code to a registered email address or phone number.

### Broken Logic in Password Reset

Broken logic in password reset mechanisms occurs when the application fails to properly validate or enforce necessary steps during the reset process. This can lead to unauthorized access if an attacker can bypass these checks.

#### Example Scenario

Consider a scenario where a user requests a password reset. The application sends a reset link to the user’s email. However, if the application does not properly validate whether the user has clicked the reset link before allowing them to set a new password, an attacker could potentially intercept the reset link and change the password.

### Real-World Examples

#### Recent Breaches

One notable example is the breach at LinkedIn in 2012, where attackers exploited a vulnerability in the password reset mechanism. The attackers were able to reset passwords for millions of accounts, leading to widespread unauthorized access.

Another example is the breach at Yahoo in 2014, where attackers exploited a similar vulnerability in the password reset process. This resulted in the theft of personal information from over 500 million user accounts.

### Detailed Walkthrough

Let’s walk through the specific issue described in the lecture transcript and understand how to identify and fix it.

#### Code Analysis

The provided code snippet is a Python script that attempts to exploit a broken logic vulnerability in a password reset mechanism. Here is the complete code:

```python
import requests

# Define the base URL of the target application
base_url = "http://example.com"

# Define the login data
login_data = {
    "username": "admin",
    "password": "password"
}

# Send a POST request to the login endpoint
r = requests.post(base_url + "/login", data=login_data, verify=False, proxies={"http": "http://localhost:8080", "https": "http://localhost:8080"})

# Check if the login was successful
if "logout" in r.text:
    print("Login successful")
else:
    print("Login failed")
```

#### Explanation

1. **Base URL**: The `base_url` variable holds the URL of the target application.
2. **Login Data**: The `login_data` dictionary contains the username and password for the login attempt.
3. **POST Request**: The `requests.post` function sends a POST request to the `/login` endpoint with the login data.
4. **Verification**: The script checks if the response contains the string `"logout"`, which indicates a successful login.

#### Issues Identified

1. **Incorrect Endpoint**: The script initially attempted to send a request to the `/` endpoint instead of the `/login` endpoint.
2. **Missing Verification**: The script did not properly verify the login status before proceeding.

### How to Debug

To debug the script, we can use tools like Burp Suite to inspect the HTTP requests and responses. Here is a step-by-step guide:

1. **Open Burp Suite**: Ensure Burp Suite is running and configured as a proxy.
2. **Send Request**: Use the `requests.post` function to send the login request.
3. **Inspect Response**: Use Burp Suite to inspect the HTTP response and ensure the correct endpoint is being accessed.

#### HTTP Request and Response

Here is the complete HTTP request and response:

**HTTP Request:**

```http
POST /login HTTP/1.1
Host: example.com
User-Agent: python-requests/2.25.1
Accept-Encoding: gzip, deflate
Accept: */*
Connection: keep-alive
Content-Length: 26
Content-Type: application/x-www-form-urlencoded

username=admin&password=password
```

**HTTP Response:**

```http
HTTP/1.1 200 OK
Date: Tue, 01 Jan 2024 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Length: 1024
Content-Type: text/html; charset=UTF-8

<!DOCTYPE html>
<html>
<head>
<title>Login</title>
</head>
<body>
<h1>Login Successful</h1>
<a href="/logout">Logout</a>
</body>
</html>
```

### How to Prevent / Defend

#### Secure Coding Practices

1. **Validate Each Step**: Ensure that each step in the password reset process is properly validated.
2. **Use Tokens**: Implement token-based systems to ensure that only authorized users can reset passwords.
3. **Rate Limiting**: Implement rate limiting to prevent brute-force attacks on the password reset mechanism.

#### Configuration Hardening

1. **Secure Cookies**: Ensure that cookies used in the authentication process are marked as `HttpOnly` and `Secure`.
2. **Disable Auto-Complete**: Disable auto-complete on password fields to prevent accidental exposure.

#### Detection and Prevention

1. **Logging and Monitoring**: Implement logging and monitoring to detect unusual activity related to password resets.
2. **Security Testing**: Regularly perform security testing, including penetration testing, to identify and fix vulnerabilities.

#### Secure vs. Vulnerable Code

Here is the corrected version of the code:

```python
import requests

# Define the base URL of the target application
base_url = "http://example.com"

# Define the login data
login_data = {
    "username": "admin",
    "password": "password"
}

# Send a POST request to the login endpoint
r = requests.post(base_url + "/login", data=login_data, verify=False, proxies={"http": "http://localhost:8080", "https": "http://localhost:8080"})

# Check if the login was successful
if "logout" in r.text:
    print("Login successful")
else:
    print("Login failed")
```

### Conclusion

Understanding and preventing broken logic in password reset mechanisms is crucial for maintaining the security of web applications. By following secure coding practices, implementing proper validation, and using tools like Burp Suite for debugging, developers can significantly reduce the risk of such vulnerabilities.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed modules on authentication vulnerabilities.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security techniques.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for practicing web security.

By thoroughly understanding and practicing these concepts, you can become proficient in identifying and mitigating authentication vulnerabilities in web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/13-Authentication Vulnerabilities/04-Lab 3 Password reset broken logic/01-Introduction to Authentication Vulnerabilities|Introduction to Authentication Vulnerabilities]] | [[Web Security (PortSwigger)/13-Authentication Vulnerabilities/04-Lab 3 Password reset broken logic/00-Overview|Overview]] | [[03-Authentication Vulnerabilities Password Reset Broken Logic|Authentication Vulnerabilities Password Reset Broken Logic]]
