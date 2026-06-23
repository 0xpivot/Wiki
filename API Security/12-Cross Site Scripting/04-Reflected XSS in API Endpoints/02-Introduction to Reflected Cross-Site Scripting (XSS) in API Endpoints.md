---
course: API Security
topic: Cross Site Scripting
tags: [api-security]
---

## Introduction to Reflected Cross-Site Scripting (XSS) in API Endpoints

Cross-Site Scripting (XSS) is a type of security vulnerability that allows attackers to inject malicious scripts into web pages viewed by other users. There are several types of XSS, including Stored XSS, DOM-based XSS, and Reflected XSS. In this chapter, we will focus on Reflected XSS specifically within API endpoints. This type of XSS occurs when an attacker injects malicious data into a request that is then immediately reflected back in the response.

### What is Reflected XSS?

Reflected XSS happens when an attacker injects malicious data into a request that is then immediately reflected back in the response. Unlike Stored XSS, where the malicious script is permanently stored on the server and served to multiple users, Reflected XSS requires the victim to click on a malicious link or submit a form containing the injected script.

#### How Reflected XSS Works

1. **Injection Point**: An attacker finds a place in the application where user input is reflected back in the response, such as a search query parameter or a URL path.
2. **Malicious Input**: The attacker crafts a malicious input, typically a JavaScript snippet, and includes it in the request.
3. **Reflection**: The server processes the request and reflects the malicious input back in the response.
4. **Execution**: When the victim visits the crafted URL or submits the form, the browser executes the malicious script, potentially compromising the user's session or stealing sensitive information.

### Example Scenario

Consider an API endpoint `/api/users` that accepts a `username` parameter and returns an XML response containing the username:

```http
GET /api/users?username=test HTTP/1.1
Host: example.com
```

The server responds with:

```xml
<?xml version="1.0"?>
<response>
    <username>test</username>
</response>
```

Now, if an attacker injects a malicious script into the `username` parameter:

```http
GET /api/users?username=<script>alert('XSS')</script> HTTP/1.1
Host: example.com
```

The server might respond with:

```xml
<?xml version="1.0"?>
<response>
    <username><script>alert('XSS')</script></username>
</response>
```

If this response is rendered in a browser, the script will execute, triggering an alert box.

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2021-21972**: A Reflected XSS vulnerability was found in the WordPress REST API. Attackers could inject malicious scripts into certain API endpoints, leading to potential session hijacking.
- **CVE-2022-22965**: A Reflected XSS vulnerability was discovered in the Atlassian Jira Service Desk. Attackers could inject malicious scripts into the `summary` field of issues, which would be executed when viewed by other users.

### Background Theory

To understand Reflected XSS in API endpoints, it's essential to grasp the underlying principles of HTTP requests and responses, as well as the role of user input in these interactions.

#### HTTP Requests and Responses

HTTP (Hypertext Transfer Protocol) is the foundation of data communication on the World Wide Web. An HTTP request consists of a method (e.g., GET, POST), a URL, and optional headers and a body. The server processes the request and sends an HTTP response, which includes status codes, headers, and a body.

#### User Input in API Endpoints

API endpoints often accept user input through query parameters, form data, or request bodies. This input is used to filter, sort, or modify the data returned in the response. If this input is not properly sanitized or validated, it can lead to vulnerabilities like Reflected XSS.

### Detection and Prevention

#### How to Detect Reflected XSS

Detecting Reflected XSS involves testing API endpoints for susceptibility to injection attacks. This can be done manually or using automated tools.

##### Manual Testing

1. **Identify Injection Points**: Look for places where user input is reflected back in the response, such as query parameters or URL paths.
2. **Craft Malicious Input**: Inject a simple script tag, such as `<script>alert('XSS')</script>`, into the identified injection points.
3. **Observe Response**: Check if the injected script is reflected back in the response and if it executes when rendered in a browser.

##### Automated Tools

Tools like Burp Suite, OWASP ZAP, and Acunetix can automate the process of detecting Reflected XSS by injecting various payloads into API endpoints and analyzing the responses.

#### How to Prevent Reflected XSS

Preventing Reflected XSS involves sanitizing and validating user input, encoding output, and implementing security headers.

##### Sanitize and Validate User Input

1. **Input Validation**: Ensure that user input conforms to expected formats and lengths. For example, validate that usernames contain only alphanumeric characters and underscores.
2. **Sanitization**: Remove or escape any characters that could be used to inject malicious scripts. Libraries like HTML Purifier can help with this.

##### Encode Output

1. **Output Encoding**: Encode user input before reflecting it in the response. Use context-aware encoding techniques, such as HTML entity encoding for HTML contexts and URL encoding for URL contexts.
2. **Content Security Policy (CSP)**: Implement a Content Security Policy to restrict the sources from which scripts can be loaded. This can help mitigate the impact of Reflected XSS.

##### Secure Coding Practices

1. **Use Frameworks and Libraries**: Leverage frameworks and libraries that provide built-in protections against XSS. For example, Django and Ruby on Rails automatically escape user input in templates.
2. **Avoid Directly Embedding User Input**: Avoid directly embedding user input into HTML, JavaScript, or CSS. Instead, use safe methods provided by the framework or library.

### Complete Example

Let's walk through a complete example of a Reflected XSS vulnerability in an API endpoint and how to fix it.

#### Vulnerable Code

Consider an API endpoint `/api/users` that accepts a `username` parameter and returns an XML response containing the username:

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/api/users')
def get_users():
    username = request.args.get('username', '')
    return f'''
<?xml version="1.0"?>
<response>
    <username>{username}</username>
</response>
'''

if __name__ == '__main__':
    app.run(debug=True)
```

#### Exploitation

An attacker can inject a malicious script into the `username` parameter:

```http
GET /api/users?username=<script>alert('XSS')</script> HTTP/1.1
Host: example.com
```

The server responds with:

```xml
<?xml version="1.0"?>
<response>
    <username><script>alert('XSS')</script></username>
</response>
```

When this response is rendered in a browser, the script executes, triggering an alert box.

#### Fixed Code

To fix the vulnerability, we need to encode the `username` before reflecting it in the response:

```python
from flask import Flask, request
import html

app = Flask(__name__)

@app.route('/api/users')
def get_users():
    username = request.args.get('username', '')
    encoded_username = html.escape(username)
    return f'''
<?xml version="1.0"?>
<response>
    <username>{encoded_username}</username>
</response>
'''

if __name__ == '__main__':
    app.run(debug=True)
```

Now, if an attacker injects a malicious script:

```http
GET /api/users?username=<script>alert('XSS')</script> HTTP/1.1
Host: example.com
```

The server responds with:

```xml
<?xml version="1.0"?>
<response>
    <username>&lt;script&gt;alert('XSS')&lt;/script&gt;</username>
</response>
```

The script is properly escaped and does not execute when rendered in a browser.

### Mermaid Diagrams

#### Request-Response Flow

```mermaid
sequenceDiagram
    participant Browser
    participant Server
    Browser->>Server: GET /api/users?username=<script>alert('XSS')</script>
    Server-->>Browser: <?xml version="1.0"?><response><username>&lt;script&gt;alert('XSS')&lt;/script&gt;</username></response>
    Browser->>Browser: Renders response safely
```

### Common Pitfalls

#### Incorrect Encoding

One common pitfall is using incorrect encoding methods. For example, using `html.escape` for HTML contexts but not for other contexts like JavaScript or CSS can leave the application vulnerable.

#### Lack of Input Validation

Failing to validate user input can allow attackers to inject malicious scripts. Always ensure that user input conforms to expected formats and lengths.

### Hands-On Labs

For hands-on practice with Reflected XSS in API endpoints, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various types of XSS, including Reflected XSS.
- **OWASP Juice Shop**: Provides a vulnerable web application with multiple XSS vulnerabilities, including Reflected XSS.
- **DVWA (Damn Vulnerable Web Application)**: Includes a variety of web application vulnerabilities, including Reflected XSS.

These labs provide real-world scenarios and challenges to help you master the detection and prevention of Reflected XSS in API endpoints.

### Conclusion

Reflected XSS in API endpoints is a serious security vulnerability that can compromise user sessions and steal sensitive information. By understanding the underlying principles, detecting and preventing the vulnerability, and practicing with real-world examples, you can ensure the security of your applications. Always sanitize and validate user input, encode output, and implement security headers to protect against Reflected XSS.

---
<!-- nav -->
[[API Security/12-Cross Site Scripting/04-Reflected XSS in API Endpoints/01-Introduction to Cross-Site Scripting (XSS)|Introduction to Cross-Site Scripting (XSS)]] | [[API Security/12-Cross Site Scripting/04-Reflected XSS in API Endpoints/00-Overview|Overview]] | [[API Security/12-Cross Site Scripting/04-Reflected XSS in API Endpoints/03-Practice Questions & Answers|Practice Questions & Answers]]
