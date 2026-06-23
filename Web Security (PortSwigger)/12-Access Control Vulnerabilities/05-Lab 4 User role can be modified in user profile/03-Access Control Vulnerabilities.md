---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Access Control Vulnerabilities

### Introduction to Access Control

Access control is a fundamental aspect of web application security. It ensures that users have appropriate permissions to access resources and perform actions within the application. Access control vulnerabilities occur when an application fails to properly restrict access to certain functionalities or data based on user roles and permissions. These vulnerabilities can lead to unauthorized access, privilege escalation, and data breaches.

### Understanding the Scenario

In the provided scenario, we are dealing with a web application where users can modify their profiles. Specifically, the user role can be modified through the user profile settings. This is a critical area where access control vulnerabilities can arise.

#### Logging In

The first step in the scenario involves logging into the application using the credentials provided. The login process typically involves sending a POST request to the `/login` endpoint with the username and password as parameters.

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

username=admin&password=Peter
```

Upon successful authentication, the server responds with a session ID, which is used to maintain the user's session across subsequent requests.

```http
HTTP/1.1 200 OK
Set-Cookie: session_id=abc123; Path=/; HttpOnly
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>Dashboard</title>
</head>
<body>
    <h1>Welcome, admin!</h1>
</body>
</html>
```

### Identifying the Vulnerability

The next step is to identify where the broken access control vulnerability lies. In this case, the vulnerability is related to the user profile settings. Specifically, the user can modify their role through the profile settings.

#### Analyzing the Profile Request

When accessing the user profile, the application sends a GET request to the `/profile` endpoint with the `id` parameter set to the user's username.

```http
GET /profile?id=admin HTTP/1.1
Host: example.com
Cookie: session_id=abc123
```

The response from the server contains the user's profile information, including the role.

```http
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>User Profile</title>
</head>
<body>
    <h1>User Profile</h1>
    <p>Username: admin</p>
    <p>Role: admin</p>
</body>
</html>
```

### Exploiting the Vulnerability

To exploit the vulnerability, an attacker can manipulate the `id` parameter to access and modify the profile of any user, including administrative accounts. This allows the attacker to escalate privileges and gain unauthorized access to sensitive functionalities.

#### Crafting the Exploit

Using a tool like Burp Suite, the attacker can intercept and modify the profile request to change the `id` parameter to a different user's username.

```http
GET /profile?id=admin HTTP/1.1
Host: example.com
Cookie: session_id=abc123
```

By changing the `id` parameter to a different user's username, the attacker can access and modify the profile of that user.

```http
GET /profile?id=user1 HTTP/1.1
Host: example.com
Cookie: session_id=abc123
```

### Real-World Examples

Access control vulnerabilities have been exploited in numerous real-world scenarios. One notable example is the Equifax breach in 2017, where attackers exploited a vulnerability in the Apache Struts framework to gain unauthorized access to sensitive data. Another example is the Capital One breach in 2019, where an attacker exploited a misconfigured web application firewall to access sensitive customer data.

### How to Prevent / Defend

#### Detection

To detect access control vulnerabilities, organizations should implement comprehensive security testing practices, including:

1. **Static Application Security Testing (SAST)**: Analyze the source code for potential security issues.
2. **Dynamic Application Security Testing (DAST)**: Simulate attacks on the running application to identify vulnerabilities.
3. **Penetration Testing**: Engage ethical hackers to test the application's defenses.

#### Prevention

To prevent access control vulnerabilities, organizations should follow these best practices:

1. **Role-Based Access Control (RBAC)**: Implement RBAC to ensure that users have appropriate permissions based on their roles.
2. **Least Privilege Principle**: Grant users the minimum level of access necessary to perform their tasks.
3. **Input Validation**: Validate all input parameters to prevent manipulation.
4. **Session Management**: Use secure session management techniques to prevent session hijacking and replay attacks.

#### Secure Coding Fixes

Here is an example of how to securely handle user roles in a web application:

**Vulnerable Code**

```python
@app.route('/profile', methods=['GET'])
def profile():
    user_id = request.args.get('id')
    user = User.query.filter_by(username=user_id).first()
    return render_template('profile.html', user=user)
```

**Secure Code**

```python
@app.route('/profile', methods=['GET'])
@login_required
def profile():
    user_id = request.args.get('id')
    if current_user.role != 'admin' and current_user.username != user_id:
        abort(403)
    user = User.query.filter_by(username=user_id).first()
    return render_template('profile.html', user=user)
```

### Configuration Hardening

To further harden the application against access control vulnerabilities, organizations should configure the following:

1. **Web Server Configuration**: Ensure that the web server is configured to enforce strict access controls.
2. **Application Configuration**: Configure the application to enforce least privilege and role-based access control.
3. **Database Configuration**: Configure the database to enforce strict access controls and limit the privileges of application users.

### Hands-On Labs

To practice identifying and exploiting access control vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a series of labs on access control vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates common web application vulnerabilities.

### Conclusion

Access control vulnerabilities are a significant threat to web applications. By understanding the underlying mechanisms and implementing robust security measures, organizations can effectively mitigate these risks. Regular security testing, secure coding practices, and configuration hardening are essential steps in ensuring the security of web applications.

---
<!-- nav -->
[[02-Access Control Vulnerabilities Modifying User Roles|Access Control Vulnerabilities Modifying User Roles]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/05-Lab 4 User role can be modified in user profile/00-Overview|Overview]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/05-Lab 4 User role can be modified in user profile/04-Practice Questions & Answers|Practice Questions & Answers]]
