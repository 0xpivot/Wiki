---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Understanding Access Control Vulnerabilities

Access control vulnerabilities occur when an application fails to properly restrict access to sensitive resources or functionalities based on user roles or permissions. This can lead to unauthorized users gaining access to administrative panels, modifying critical data, or performing actions that should be restricted to specific roles. In this section, we will delve into the details of such vulnerabilities, focusing on unprotected admin functionality and how to exploit and defend against them.

### Background Theory

Access control is a fundamental aspect of web application security. It ensures that users can only access resources and perform actions that are appropriate for their roles within the system. Typically, this involves:

- **Authentication**: Verifying the identity of a user.
- **Authorization**: Determining what actions a user is allowed to perform based on their authenticated role.

When these mechanisms fail, attackers can exploit the vulnerabilities to gain unauthorized access to sensitive areas of the application.

### Example Scenario: Unprotected Admin Functionality

Consider a web application that has an administrative panel accessible via a specific URL, such as `https://example.com/admin`. If proper access controls are not implemented, an attacker might be able to access this panel simply by navigating to the URL.

#### Real-World Example: CVE-2021-21972

In 2021, a vulnerability was discovered in the Jenkins Continuous Integration server (CVE-2021-21972). This vulnerability allowed unauthenticated users to access the Jenkins Script Console, which is typically reserved for administrators. By exploiting this vulnerability, attackers could execute arbitrary Groovy scripts, leading to remote code execution and potential compromise of the entire system.

### Exploiting Unprotected Admin Functionality

To demonstrate how an unprotected admin functionality can be exploited, let's walk through a step-by-step process using Python and the `requests` library.

#### Step 1: Identify the Admin Panel URL

The first step is to identify the URL of the admin panel. In our example, the admin panel is located at `https://example.com/admin`.

#### Step 2: Perform a GET Request

We will use Python's `requests` library to send a GET request to the admin panel URL. Here is the complete code:

```python
import requests

# Define the admin panel URL
admin_panel_url = "https://example.com/admin"

# Send a GET request to the admin panel
response = requests.get(admin_panel_url, verify=False)

# Print the response status code and content
print(f"Status Code: {response.status_code}")
print(f"Response Content:\n{response.text}")
```

#### Explanation of the Code

- **`requests.get()`**: Sends a GET request to the specified URL.
- **`verify=False`**: Disables SSL certificate verification. This is often necessary when dealing with self-signed certificates or testing environments.
- **`response.status_code`**: Retrieves the HTTP status code of the response.
- **`response.text`**: Retrieves the content of the response.

#### Full HTTP Request and Response

Here is the full HTTP request and response:

```http
GET /admin HTTP/1.1
Host: example.com
User-Agent: python-requests/2.25.1
Accept-Encoding: gzip, deflate
Connection: keep-alive
```

```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Type: text/html; charset=UTF-8
Content-Length: 1234
Connection: close

<!DOCTYPE html>
<html>
<head>
    <title>Admin Panel</title>
</head>
<body>
    <h1>Welcome to the Admin Panel</h1>
    <!-- Admin panel content -->
</body>
</html>
```

### Pitfalls and Common Mistakes

- **Disabling SSL Verification**: While disabling SSL verification (`verify=False`) is sometimes necessary for testing, it should never be used in production environments as it exposes the application to man-in-the-middle attacks.
- **Hardcoding URLs**: Hardcoding URLs in scripts can make them brittle and difficult to maintain. Consider using environment variables or configuration files to manage URLs dynamically.

### How to Prevent / Defend Against Unprotected Admin Functionality

#### Detection

- **Logging and Monitoring**: Implement logging and monitoring to detect unauthorized access attempts to sensitive areas of the application.
- **Security Scanning Tools**: Use automated security scanning tools like Burp Suite, OWASP ZAP, or commercial solutions to identify access control vulnerabilities.

#### Prevention

- **Role-Based Access Control (RBAC)**: Ensure that access to sensitive areas is restricted based on user roles. Only authenticated users with the appropriate role should be able to access the admin panel.
- **Session Management**: Implement strong session management practices to prevent session hijacking and ensure that sessions are securely terminated after a period of inactivity.
- **Input Validation and Sanitization**: Validate and sanitize all inputs to prevent injection attacks and other forms of exploitation.

#### Secure Coding Fixes

Here is an example of how to implement RBAC in a Flask application:

```python
from flask import Flask, redirect, url_for, request, session

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Sample user database
users = {
    'admin': {'password': 'admin_password', 'role': 'admin'},
    'user': {'password': 'user_password', 'role': 'user'}
}

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if username in users and users[username]['password'] == password:
        session['username'] = username
        return redirect(url_for('dashboard'))
    else:
        return 'Invalid credentials'

@app.route('/dashboard')
def dashboard():
    if 'username' in session and users[session['username']]['role'] == 'admin':
        return 'Welcome to the Admin Dashboard'
    else:
        return 'Unauthorized access'

if __name__ == '__main__':
    app.run(debug=True)
```

#### Vulnerable vs. Fixed Code

**Vulnerable Code:**

```python
@app.route('/dashboard')
def dashboard():
    return 'Welcome to the Admin Dashboard'
```

**Fixed Code:**

```python
@app.route('/dashboard')
def dashboard():
    if 'username' in session and users[session['username']]['role'] == 'admin':
        return 'Welcome to the Admin Dashboard'
    else:
        return 'Unauthorized access'
```

### Configuration Hardening

- **Disable Directory Listing**: Ensure that directory listing is disabled to prevent unauthorized access to sensitive files.
- **Secure Configuration Files**: Store configuration files outside the web root and ensure they are not accessible via HTTP.

### Hands-On Labs

For hands-on practice with access control vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a series of labs focused on web security, including access control vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for learning about web security.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

By thoroughly understanding and practicing the concepts covered in this section, you will be better equipped to identify, exploit, and defend against access control vulnerabilities in web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/12-Access Control Vulnerabilities/02-Lab 1 Unprotected admin functionality/03-Access Control Vulnerabilities|Access Control Vulnerabilities]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/02-Lab 1 Unprotected admin functionality/00-Overview|Overview]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/02-Lab 1 Unprotected admin functionality/05-Practice Questions & Answers|Practice Questions & Answers]]
