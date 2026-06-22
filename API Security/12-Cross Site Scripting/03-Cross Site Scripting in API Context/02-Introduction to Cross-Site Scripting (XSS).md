---
course: API Security
topic: Cross Site Scripting
tags: [api-security]
---

## Introduction to Cross-Site Scripting (XSS)

Cross-Site Scripting (XSS) is a type of security vulnerability typically found in web applications. It occurs when an attacker manages to inject malicious scripts into a webpage that is viewed by other users. These scripts can perform various harmful actions, such as stealing cookies, session tokens, or other sensitive information. In the context of APIs, XSS vulnerabilities can arise due to improper handling of user input, leading to potential exploitation.

### What is Cross-Site Scripting?

Cross-Site Scripting (XSS) is a client-side code injection technique where an attacker injects malicious scripts into a webpage that is viewed by other users. This can happen through various means, including:

- **Reflected XSS**: The injected script is reflected off a web server, often in response to a search query or similar operation.
- **Stored XSS**: The injected script is permanently stored on the target servers, such as in a database, and is later served to unsuspecting users.
- **DOM-based XSS**: The vulnerability exists in the way the web application's client-side JavaScript interacts with the DOM.

### Why Does XSS Matter?

XSS attacks can have severe consequences, including:

- **Data Theft**: Attackers can steal sensitive data like session cookies, authentication tokens, and personal information.
- **Account Takeover**: By stealing session tokens, attackers can gain unauthorized access to user accounts.
- **Defacement**: Attackers can modify the content of a website, leading to defacement.
- **Phishing Attacks**: Malicious scripts can redirect users to phishing sites or trick them into revealing sensitive information.

### How Does XSS Work Under the Hood?

To understand how XSS works, consider the following steps:

1. **Injection Point**: An attacker finds a place in the web application where user input is not properly sanitized or validated.
2. **Script Injection**: The attacker injects a malicious script into the application.
3. **Execution**: The injected script is executed in the victim's browser, leading to the desired malicious action.

### Real-World Examples of XSS Vulnerabilities

#### Recent CVEs and Breaches

- **CVE-2021-21972**: A stored XSS vulnerability was discovered in the WordPress plugin "WP GDPR Compliance." Attackers could inject malicious scripts into comments, leading to potential data theft.
- **CVE-2022-22965**: A reflected XSS vulnerability was found in the Atlassian Confluence application. Attackers could inject scripts into URLs, leading to unauthorized access and data theft.

### Types of XSS in API Context

In the context of APIs, XSS vulnerabilities can manifest in several ways:

1. **Reflected XSS**
2. **Stored XSS**
3. **Blind XSS**

#### Reflected XSS

Reflected XSS occurs when the malicious script is included in the URL and is reflected back to the user. This type of XSS is less common in API contexts but can still occur.

**Example Scenario:**

Consider an API endpoint `/search` that takes a `query` parameter and returns results. If the `query` parameter is not properly sanitized, an attacker can inject a malicious script.

```http
GET /search?query=<script>alert('XSS')</script>
```

The response might look like this:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "results": [
    "<script>alert('XSS')</script>"
  ]
}
```

**Detection and Prevention:**

- **Input Validation**: Ensure that all user inputs are validated and sanitized.
- **Content Security Policy (CSP)**: Implement CSP to restrict the sources of executable scripts.

#### Stored XSS

Stored XSS occurs when the malicious script is stored on the server and is later served to unsuspecting users. This type of XSS is more common in API contexts.

**Example Scenario:**

Consider an API endpoint `/register` that allows users to register and store their profile information. If the profile information is not properly sanitized, an attacker can inject a malicious script.

```http
POST /register
Content-Type: application/json

{
  "username": "attacker",
  "profile": "<script>alert('XSS')</script>"
}
```

The response might look like this:

```http
HTTP/1.1 201 Created
Location: /users/1
```

When another user views the profile, the malicious script is executed.

**Detection and Prevention:**

- **Input Validation**: Ensure that all user inputs are validated and sanitized.
- **Output Encoding**: Encode all output to prevent script execution.

#### Blind XSS

Blind XSS occurs when the attacker does not have direct feedback on whether the injection was successful. This type of XSS is more challenging to detect but can still be exploited.

**Example Scenario:**

Consider an API endpoint `/feedback` that allows users to submit feedback. If the feedback is not properly sanitized, an attacker can inject a malicious script.

```http
POST /feedback
Content-Type: application/json

{
  "message": "<script>alert('XSS')</script>"
}
```

The response might look like this:

```http
HTTP/1.1 201 Created
Location: /feedback/1
```

When the feedback is displayed to other users, the malicious script is executed.

**Detection and Prevention:**

- **Input Validation**: Ensure that all user inputs are validated and sanitized.
- **Output Encoding**: Encode all output to prevent script execution.

### How to Prevent / Defend Against XSS

#### Detection

- **Static Analysis Tools**: Use tools like SonarQube, ESLint, and Bandit to detect potential XSS vulnerabilities in your codebase.
- **Dynamic Analysis Tools**: Use tools like Burp Suite, OWASP ZAP, and Acunetix to test your application for XSS vulnerabilities.

#### Prevention

- **Input Validation**: Validate all user inputs to ensure they meet expected formats and constraints.
- **Output Encoding**: Encode all output to prevent script execution. Use libraries like `OWASP Java Encoder` or `DOMPurify` for JavaScript.
- **Content Security Policy (CSP)**: Implement CSP to restrict the sources of executable scripts. Example CSP header:

```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://trustedscripts.example.com;
```

#### Secure Coding Fixes

**Vulnerable Code:**

```javascript
app.get('/search', (req, res) => {
  const query = req.query.query;
  res.json({ results: [query] });
});
```

**Secure Code:**

```javascript
const { escape } = require('html-escaper');

app.get('/search', (req, res) => {
  const query = escape(req.query.query);
  res.json({ results: [query] });
});
```

**Vulnerable Code:**

```python
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    profile = data['profile']
    return jsonify({"username": username, "profile": profile})
```

**Secure Code:**

```python
from markupsafe import Markup

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data['username']
    profile = Markup.escape(data['profile'])
    return jsonify({"username": username, "profile": profile})
```

### Hands-On Labs

For hands-on practice with XSS in API contexts, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive modules on XSS, including API-specific scenarios.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security techniques.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates insecure coding practices.
- **WebGoat**: An interactive, gamified training application for learning web security.

These labs provide real-world scenarios and challenges to help you master the detection and prevention of XSS vulnerabilities in API contexts.

### Conclusion

Cross-Site Scripting (XSS) is a critical security vulnerability that can have severe consequences if not properly addressed. Understanding the types of XSS, their mechanisms, and how to detect and prevent them is essential for securing web applications and APIs. By implementing robust input validation, output encoding, and Content Security Policies, you can significantly reduce the risk of XSS attacks. Regularly testing your applications using static and dynamic analysis tools will help identify and mitigate potential vulnerabilities.

---
<!-- nav -->
[[01-Introduction to Cross-Site Scripting (XSS) in API Context|Introduction to Cross-Site Scripting (XSS) in API Context]] | [[API Security/12-Cross Site Scripting/03-Cross Site Scripting in API Context/00-Overview|Overview]] | [[03-Cross-Site Scripting (XSS) in API Context|Cross-Site Scripting (XSS) in API Context]]
