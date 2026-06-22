---
course: API Security
topic: Cross Site Scripting
tags: [api-security]
---

## Introduction to Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a common web security vulnerability that allows an attacker to inject malicious scripts into web pages viewed by other users. This can lead to various attacks, including session hijacking, defacement, and phishing. XSS vulnerabilities can occur in different parts of a web application, including API endpoints. In this chapter, we will focus on a specific type of XSS vulnerability called Content-Type Cross-Site Scripting (CT-XSS) in API endpoints.

### What is Content-Type Cross-Site Scripting?

Content-Type Cross-Site Scripting (CT-XSS) occurs when an API endpoint returns data with an incorrect `Content-Type` header, leading to the browser interpreting the response in an unintended way. Typically, APIs return data in formats like JSON or XML, which are not meant to be interpreted as HTML. However, if the `Content-Type` is set to `text/plain` or `text/html`, the browser may interpret the response as HTML, potentially executing any embedded scripts.

### Why Does CT-XSS Matter?

CT-XSS matters because it can allow attackers to inject malicious scripts into responses that are intended to be plain text or JSON. This can lead to various security issues, such as:

- **Session Hijacking**: An attacker could steal session cookies or tokens.
- **Defacement**: An attacker could change the appearance of the page.
- **Phishing**: An attacker could trick users into entering sensitive information.

### How Does CT-XSS Work?

To understand how CT-XSS works, let's break down the process:

1. **User Interaction**: A user interacts with an application, such as registering a new account.
2. **API Request**: The application sends an API request to the server.
3. **Server Response**: The server responds with data, often in JSON format.
4. **Incorrect Content-Type**: If the server sets the `Content-Type` to `text/plain` or `text/html`, the browser interprets the response as HTML.
5. **Script Execution**: If the response contains script tags (`<script>`), the browser executes them, leading to potential security issues.

### Example Scenario

Let's consider the scenario described in the lecture transcript:

- **User Registration**: A user tries to register a new account with the username `Vakass7`.
- **API Request**: The application sends an API request to the server to check if the username is available.
- **Server Response**: The server responds with a JSON object indicating whether the username is available.
- **Incorrect Content-Type**: Instead of setting the `Content-Type` to `application/json`, the server sets it to `text/plain`.

Here is a detailed breakdown of the interaction:

#### Step-by-Step Mechanics

1. **Initial Request**:
    ```http
    POST /api/register HTTP/1.1
    Host: example.com
    Content-Type: application/json
    {
        "username": "Vakass7",
        "password": "password123"
    }
    ```

2. **Server Response**:
    ```http
    HTTP/1.1 200 OK
    Content-Type: application/json
    {
        "status": "success",
        "message": "User registered successfully"
    }
    ```

3. **Incorrect Content-Type**:
    ```http
    HTTP/1.1 200 OK
    Content-Type: text/plain
    <script>alert('XSS');</script>
    ```

In this case, the server incorrectly sets the `Content-Type` to `text/plain`, causing the browser to interpret the response as HTML and execute the `<script>` tag.

### Real-World Examples

Recent real-world examples of CT-XSS include:

- **CVE-2021-3116**: A vulnerability in the WordPress REST API allowed attackers to inject scripts into responses due to incorrect `Content-Type` settings.
- **CVE-2022-22965**: A vulnerability in the Jenkins API allowed attackers to inject scripts into responses due to incorrect `Content-Type` settings.

These examples highlight the importance of correctly setting `Content-Type` headers to prevent CT-XSS.

### How to Prevent / Defend Against CT-XSS

#### Detection

To detect CT-XSS vulnerabilities, you can:

1. **Static Analysis**: Use tools like SonarQube, ESLint, or Bandit to scan your code for potential issues.
2. **Dynamic Analysis**: Use tools like Burp Suite, OWASP ZAP, or Acunetix to test your API endpoints for vulnerabilities.
3. **Manual Testing**: Manually test your API endpoints by changing the `Content-Type` header and checking if the response is interpreted as HTML.

#### Prevention

To prevent CT-XSS, you should:

1. **Set Correct Content-Type Headers**: Always set the `Content-Type` header to match the actual content type of the response. For example, if you are returning JSON, set `Content-Type` to `application/json`.
2. **Validate User Input**: Ensure that user input is properly validated and sanitized to prevent injection of malicious scripts.
3. **Use Content Security Policy (CSP)**: Implement a Content Security Policy (CSP) to restrict the sources of executable scripts.

#### Secure Coding Fixes

Here is an example of a vulnerable code snippet and its secure counterpart:

**Vulnerable Code**:
```python
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/register', methods=['POST'])
def register():
    username = request.json['username']
    # Check if username is available
    if check_username_available(username):
        return jsonify({"status": "success", "message": "User registered successfully"})
    else:
        return "<script>alert('Username already exists');</script>", 200, {'Content-Type': 'text/plain'}

if __name__ == '__main__':
    app.run()
```

**Secure Code**:
```python
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/api/register', methods=['POST'])
def register():
    username = request.json['username']
    # Check if username is available
    if check_username_available(username):
        return jsonify({"status": "success", "message": "User registered successfully"})
    else:
        return jsonify({"status": "error", "message": "Username already exists"}), 200, {'Content-Type': 'application/json'}

if __name__ == '__main__':
    app.run()
```

### Configuration Hardening

To further harden your API against CT-XSS, you can:

1. **Implement CSP**: Add a Content Security Policy (CSP) to your web application to restrict the sources of executable scripts.
2. **Use HTTP Strict Transport Security (HSTS)**: Ensure that all communication with your API is encrypted using HTTPS.
3. **Enable CORS Policies**: Configure Cross-Origin Resource Sharing (CORS) policies to restrict which domains can make requests to your API.

### Conclusion

Content-Type Cross-Site Scripting (CT-XSS) is a serious vulnerability that can lead to various security issues. By understanding how CT-XSS works, detecting potential vulnerabilities, and implementing proper defenses, you can protect your API endpoints from these attacks. Always ensure that `Content-Type` headers are set correctly, validate user input, and implement additional security measures like CSP and HSTS.

### Practice Labs

For hands-on practice with CT-XSS, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various web security topics, including XSS.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates common web application vulnerabilities.

By completing these labs, you can gain practical experience in identifying and preventing CT-XSS vulnerabilities.

---
<!-- nav -->
[[API Security/12-Cross Site Scripting/01-Content Type Cross Scripting in API Endpoints/00-Overview|Overview]] | [[02-Content Type Cross-Site Scripting in API Endpoints|Content Type Cross-Site Scripting in API Endpoints]]
