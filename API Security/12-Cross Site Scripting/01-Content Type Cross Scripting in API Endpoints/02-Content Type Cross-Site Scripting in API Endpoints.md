---
course: API Security
topic: Cross Site Scripting
tags: [api-security]
---

## Content Type Cross-Site Scripting in API Endpoints

### Background Theory

Cross-Site Scripting (XSS) is a type of security vulnerability typically found in web applications where an attacker can inject malicious scripts into web pages viewed by other users. This can lead to unauthorized access to sensitive data, session hijacking, and other malicious activities. In the context of APIs, XSS vulnerabilities can occur when user input is improperly validated and then included in the response sent back to the client.

Content-Type Cross-Site Scripting (CT-XSS) is a specific variant of XSS that exploits the `Content-Type` header in HTTP responses. This vulnerability arises when an application does not properly validate or sanitize the `Content-Type` header, allowing an attacker to manipulate the response to execute arbitrary JavaScript code.

### How CT-XSS Works

When an API endpoint returns a response with a `Content-Type` header set to `text/html`, browsers interpret the response as HTML. If the response contains user-supplied data that is not properly sanitized, an attacker can inject malicious scripts that will be executed by the browser.

#### Example Scenario

Consider an API endpoint that returns a user profile:

```http
GET /api/user/profile HTTP/1.1
Host: example.com
```

The server responds with the following:

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8

<html>
<body>
<h1>User Profile</h1>
<p>Name: {{user.name}}</p>
</body>
</html>
```

If the `{{user.name}}` variable is not properly sanitized, an attacker could supply a name like `<script>alert('XSS')</script>`. The response would look like this:

```http
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8

<html>
<body>
<h1>User Profile</h1>
<p>Name: <script>alert('XSS')</script></p>
</body>
</html>
```

When this response is rendered by the browser, the script will execute, potentially compromising the user's session.

### Real-World Examples

Recent real-world examples of CT-XSS vulnerabilities include:

- **CVE-2021-33203**: A CT-XSS vulnerability was discovered in the WordPress REST API. An attacker could inject malicious scripts into the `Content-Type` header, leading to unauthorized access and potential data theft.
- **CVE-2022-22965**: Another CT-XSS vulnerability was found in the Drupal CMS. The issue allowed attackers to inject scripts into the `Content-Type` header, which could be executed by the browser.

These examples highlight the importance of proper validation and sanitization of user inputs, especially in the context of API endpoints.

### How to Prevent / Defend

#### Detection

To detect CT-XSS vulnerabilities, you can use automated tools such as:

- **OWASP ZAP**: A free and open-source tool that can scan for various types of vulnerabilities, including XSS.
- **Burp Suite**: A comprehensive toolkit for web application security testing that includes features for detecting XSS vulnerabilities.

#### Prevention

To prevent CT-XSS vulnerabilities, follow these best practices:

1. **Validate and Sanitize Input**: Ensure that all user inputs are properly validated and sanitized before being included in the response. Use libraries like `DOMPurify` for HTML sanitization.

2. **Set Strict Content-Type Headers**: Always set the `Content-Type` header to a strict value that matches the actual content type of the response. For example, if the response is JSON, set the `Content-Type` to `application/json`.

3. **Use Content Security Policy (CSP)**: Implement a Content Security Policy to restrict the sources from which scripts can be loaded. This can help mitigate the impact of XSS attacks.

4. **Secure Coding Practices**: Follow secure coding practices such as input validation, output encoding, and least privilege principles.

#### Secure Code Fix

Here is an example of how to fix a vulnerable API endpoint using proper sanitization and setting the correct `Content-Type` header:

**Vulnerable Code:**

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    user_name = request.args.get('name')
    return f'<html><body><h1>User Profile</h1><p>Name: {user_name}</p></body></html>', 200, {'Content-Type': 'text/html'}

if __name__ == '__main__':
    app.run()
```

**Fixed Code:**

```python
from flask import Flask, request, jsonify
import html

app = Flask(__name__)

@app.route('/api/user/profile', methods=['GET'])
def get_user_profile():
    user_name = request.args.get('name')
    sanitized_name = html.escape(user_name)
    return f'<html><body><h1>User Profile</h1><p>Name: {sanitized_name}</p></body></html>', 200, {'Content-Type': 'text/html'}

if __name__ == '__main__':
    app.run()
```

In the fixed code, we use `html.escape` to sanitize the user input, preventing any malicious scripts from being executed.

### Hands-On Practice

To gain practical experience with CT-XSS vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice identifying and exploiting XSS vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including XSS.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities, including XSS.

By working through these labs, you can gain a deeper understanding of how to identify and mitigate CT-XSS vulnerabilities in real-world scenarios.

### Conclusion

Content-Type Cross-Site Scripting is a serious vulnerability that can compromise the security of web applications and APIs. By understanding the mechanisms behind CT-XSS, validating and sanitizing user inputs, and implementing proper security measures, you can effectively prevent and defend against these attacks. Regularly testing your applications with automated tools and practicing with hands-on labs will further enhance your ability to identify and mitigate CT-XSS vulnerabilities.

---
<!-- nav -->
[[API Security/12-Cross Site Scripting/01-Content Type Cross Scripting in API Endpoints/01-Introduction to Cross-Site Scripting (XSS)|Introduction to Cross-Site Scripting (XSS)]] | [[API Security/12-Cross Site Scripting/01-Content Type Cross Scripting in API Endpoints/00-Overview|Overview]] | [[API Security/12-Cross Site Scripting/01-Content Type Cross Scripting in API Endpoints/03-Practice Questions & Answers|Practice Questions & Answers]]
