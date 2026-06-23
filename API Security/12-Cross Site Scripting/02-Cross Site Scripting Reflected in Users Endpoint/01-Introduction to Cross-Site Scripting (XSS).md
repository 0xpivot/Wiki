---
course: API Security
topic: Cross Site Scripting
tags: [api-security]
---

## Introduction to Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability typically found in web applications where an attacker can inject malicious scripts into web pages viewed by other users. This can lead to various security issues such as stealing cookies, session tokens, and other sensitive information. XSS attacks can be categorized into three main types: **Reflected XSS**, **Stored XSS**, and **DOM-based XSS**. In this chapter, we will focus on **Reflected XSS** specifically within the context of an API endpoint that handles user data.

### What is Reflected XSS?

Reflected XSS occurs when an attacker injects malicious scripts into a web page via a query parameter, form input, or other user-controlled input. The server reflects this input back to the user without proper sanitization or validation. When the user visits the crafted URL, the injected script executes in their browser, potentially compromising their session or stealing sensitive data.

### Why Does Reflected XSS Matter?

Reflected XSS is particularly dangerous because it can be used to trick users into visiting a malicious URL. Once the user clicks on the link, the injected script runs in their browser, often leading to unauthorized actions or data theft. This type of attack is commonly seen in phishing attempts and social engineering tactics.

### How Does Reflected XSS Work Under the Hood?

To understand how Reflected XSS works, let's break down the process:

1. **User Input**: A user submits input to a web application through a form, URL parameter, or other means.
2. **Server Reflection**: The server reflects this input back to the user without proper sanitization.
3. **Script Execution**: When the user receives the reflected input, the browser interprets it as executable JavaScript, which then runs in the context of the user's session.

### Example Scenario: Reflected XSS in User API Endpoint

Consider an API endpoint `/api/users` that returns user information based on a query parameter. An attacker could craft a URL that includes malicious JavaScript, which the server reflects back to the user.

#### Background Theory

To fully grasp the mechanics of Reflected XSS, it's essential to understand the following concepts:

- **HTTP Requests and Responses**: Understanding how HTTP requests and responses work is crucial for comprehending how data is transmitted between the client and server.
- **JavaScript Execution Context**: Knowing how JavaScript executes in the browser helps in understanding the potential impact of injected scripts.
- **Input Validation and Sanitization**: Proper input validation and sanitization are key to preventing XSS attacks.

### Real-World Examples

Recent real-world examples of Reflected XSS vulnerabilities include:

- **CVE-2021-21972**: A Reflected XSS vulnerability was found in the WordPress REST API, allowing attackers to inject malicious scripts into comments.
- **CVE-2022-22965**: Another Reflected XSS vulnerability was discovered in the Atlassian Jira application, affecting user profiles.

These examples highlight the importance of securing web applications against XSS attacks.

### Step-by-Step Mechanics

Let's walk through a detailed example of how a Reflected XSS attack might occur in an API endpoint.

#### Initial Setup

Assume we have an API endpoint `/api/users` that accepts a `username` parameter and returns user information.

```http
GET /api/users?username=johndoe HTTP/1.1
Host: example.com
```

The server responds with user information:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "username": "johndoe",
    "email": "johndoe@example.com"
}
```

#### Crafting the Attack

An attacker crafts a URL with a malicious script:

```http
GET /api/users?username=<script>alert('XSS')</script> HTTP/1.1
Host: example.com
```

The server reflects the input back to the user:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
    "username": "<script>alert('XSS')</script>",
    "email": "johndoe@example.com"
}
```

When the user visits this URL, the browser executes the `<script>` tag, displaying an alert box.

### Common Pitfalls

Several common pitfalls can lead to Reflected XSS vulnerabilities:

- **Improper Input Validation**: Failing to validate user input can allow malicious scripts to be injected.
- **Insufficient Output Encoding**: Not properly encoding output can result in scripts being executed in the browser.
- **Inadequate Content Security Policy (CSP)**: Without a strong CSP, browsers may execute scripts even if they are not from trusted sources.

### How to Prevent / Defend Against Reflected XSS

#### Detection

To detect Reflected XSS vulnerabilities, you can use automated tools such as:

- **Burp Suite**: A popular tool for web application security testing.
- **OWASP ZAP**: Another widely-used tool for identifying security vulnerabilities.

#### Prevention

Preventing Reflected XSS requires a multi-layered approach:

1. **Input Validation**: Validate all user inputs to ensure they meet expected formats.
2. **Output Encoding**: Encode all outputs to prevent scripts from being executed.
3. **Content Security Policy (CSP)**: Implement a strong CSP to restrict the sources of executable scripts.

#### Secure Coding Fixes

Here’s an example of how to implement these fixes:

##### Vulnerable Code

```python
@app.route('/api/users')
def get_user():
    username = request.args.get('username', '')
    return jsonify({
        'username': username,
        'email': 'johndoe@example.com'
    })
```

##### Secure Code

```python
from flask import Flask, request, jsonify
import html

app = Flask(__name__)

@app.route('/api/users')
def get_user():
    username = request.args.get('username', '')
    encoded_username = html.escape(username)
    return jsonify({
        'username': encoded_username,
        'email': 'johndoe@example.com'
    })
```

#### Configuration Hardening

Ensure your web server and application configurations are hardened against XSS attacks:

- **Set Strict CSP Headers**: Configure your web server to set strict CSP headers.
- **Enable HTTP Headers**: Enable HTTP headers such as `X-XSS-Protection` and `Content-Security-Policy`.

### Complete Example

Let's walk through a complete example of a Reflected XSS attack and its mitigation.

#### Original Request and Response

```http
GET /api/users?username=<script>alert('XSS')</script> HTTP/1.1
Host: example.com

HTTP/1.1 200 OK
Content-Type: application/json

{
    "username": "<script>alert('XSS')</script>",
    "email": "johndoe@example.com"
}
```

#### Mitigated Request and Response

```http
GET /api/users?username=%3Cscript%3Ealert(%27XSS%27)%3C%2Fscript%3E HTTP/1.1
Host: example.com

HTTP/1.1 200 OK
Content-Type: application/json
Content-Security-Policy: default-src 'self'

{
    "username": "&lt;script&gt;alert(&#39;XSS&#39;)&lt;/script&gt;",
    "email": "johndoe@example.com"
}
```

### Hands-On Practice Labs

For hands-on practice with Reflected XSS, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive labs on various web security topics, including XSS.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that contains numerous security vulnerabilities.

### Conclusion

Reflected XSS is a critical security vulnerability that can have severe consequences if left unmitigated. By understanding the mechanics of Reflected XSS, implementing proper input validation and output encoding, and using strong security policies, you can significantly reduce the risk of such attacks. Always stay vigilant and keep your web applications secure.

---
<!-- nav -->
[[API Security/12-Cross Site Scripting/02-Cross Site Scripting Reflected in Users Endpoint/00-Overview|Overview]] | [[API Security/12-Cross Site Scripting/02-Cross Site Scripting Reflected in Users Endpoint/02-Practice Questions & Answers|Practice Questions & Answers]]
