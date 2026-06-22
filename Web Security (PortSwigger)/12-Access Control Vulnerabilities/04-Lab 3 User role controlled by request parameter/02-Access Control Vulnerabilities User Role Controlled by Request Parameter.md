---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Access Control Vulnerabilities: User Role Controlled by Request Parameter

### Introduction to Access Control

Access control is a fundamental aspect of web application security. It ensures that users can only perform actions and access resources that they are authorized to use. This is typically achieved through mechanisms such as authentication, authorization, and session management. One common vulnerability in access control is when user roles are controlled by request parameters, which can be manipulated by attackers to gain unauthorized privileges.

### Understanding Cookies and Sessions

Cookies are small pieces of data stored on the client-side (usually in the browser) that are sent back to the server with each request. They are often used to maintain session state between requests. There are two main types of cookies:

1. **Session Cookies**: These are temporary cookies that are deleted when the browser is closed. They are commonly used to store session identifiers.
2. **Persistent Cookies**: These remain on the client's device even after the browser is closed and can be used to remember user preferences or to keep the user logged in across sessions.

In the context of the lecture, we encounter two types of cookies:

- **Admin Cookie**: This cookie indicates whether the user has administrative privileges.
- **Session Cookie**: This cookie identifies the user's session.

#### Example of Cookies in Action

Consider the following HTTP response from a server:

```http
HTTP/1.1 200 OK
Set-Cookie: sessionId=abc123; Path=/; HttpOnly
Set-Cookie: isAdmin=false; Path=/; Secure

<!DOCTYPE html>
<html>
<head>
    <title>User Account</title>
</head>
<body>
    <h1>Welcome, User!</h1>
    <p>Your session ID is: abc123</p>
    <p>You are not an admin.</p>
</body>
</html>
```

Here, the `sessionId` cookie is used to track the user's session, and the `isAdmin` cookie indicates that the user does not have administrative privileges.

### Manipulating Cookies for Privilege Escalation

The lecture highlights a scenario where the `isAdmin` cookie is set to `false`. An attacker might attempt to manipulate this cookie to gain administrative privileges. This is possible if the server does not properly validate the cookie value or if the cookie is not securely transmitted.

#### Steps to Exploit the Vulnerability

1. **Intercept the Request**: Use a tool like Burp Suite to intercept and modify HTTP requests.
2. **Modify the Cookie**: Change the `isAdmin` cookie value from `false` to `true`.
3. **Send the Modified Request**: Send the modified request to the server to see if the server accepts the new value.

Let's walk through this process using Burp Suite.

#### Using Burp Suite to Intercept and Modify Requests

1. **Open Burp Suite**: Start Burp Suite and configure your browser to use Burp as a proxy.
2. **Log In to the Application**: Log in to the application using the provided credentials.
3. **Intercept the Login Request**: In Burp Suite, navigate to the "Proxy" tab and enable interception.
4. **Highlight Useful Requests**: Highlight the login request and any subsequent requests that set cookies.

Here is an example of the login request:

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 26

username=admin&password=password123
```

After logging in, the server responds with cookies:

```http
HTTP/1.1 200 OK
Set-Cookie: sessionId=abc123; Path=/; HttpOnly
Set-Cookie: isAdmin=false; Path=/; Secure

<!DOCTYPE html>
<html>
<head>
    <title>User Account</title>
</head>
<body>
    <h1>Welcome, User!</h1>
    <p>Your session ID is: abc123</p>
    <p>You are not an admin.</p>
</body>
</html>
```

#### Modifying the `isAdmin` Cookie

To exploit the vulnerability, we need to modify the `isAdmin` cookie and send the request again.

1. **Navigate to Repeater**: In Burp Suite, go to the "Repeater" tab.
2. **Send the My Account Request**: Send the request to the "My Account" page.
3. **Modify the Cookie**: Change the `isAdmin` cookie value to `true`.

Here is the modified request:

```http
GET /my-account HTTP/1.1
Host: example.com
Cookie: sessionId=abc123; isAdmin=true
```

If the server does not properly validate the `isAdmin` cookie, it may accept the modified value and grant administrative privileges to the user.

### Real-World Examples of Access Control Vulnerabilities

Access control vulnerabilities have been exploited in numerous real-world scenarios. Here are a few recent examples:

1. **CVE-2021-21972**: A vulnerability in the Jenkins Continuous Integration server allowed attackers to bypass access controls and execute arbitrary code. This was due to improper validation of user roles.
2. **CVE-2020-14882**: A vulnerability in the WordPress REST API allowed unauthenticated users to perform actions reserved for administrators. This was due to insufficient access control checks.

### How to Prevent / Defend Against Access Control Vulnerabilities

#### Detection

To detect access control vulnerabilities, you can use automated tools and manual testing techniques:

1. **Automated Tools**: Use tools like Burp Suite, OWASP ZAP, and Nessus to scan for vulnerabilities.
2. **Manual Testing**: Perform manual testing to verify that access controls are properly enforced.

#### Prevention

To prevent access control vulnerabilities, follow these best practices:

1. **Proper Authentication and Authorization**: Ensure that user roles are properly authenticated and authorized.
2. **Server-Side Validation**: Always validate user input on the server-side, not just on the client-side.
3. **Use Secure Cookies**: Set cookies with the `HttpOnly` and `Secure` flags to prevent JavaScript access and ensure transmission over HTTPS.
4. **Role-Based Access Control (RBAC)**: Implement RBAC to manage user permissions based on roles.

#### Secure Coding Practices

Here is an example of insecure and secure code for handling user roles:

**Insecure Code**

```python
# Insecure code
def check_admin_role(request):
    admin_cookie = request.cookies.get('isAdmin')
    if admin_cookie == 'true':
        return True
    return False
```

**Secure Code**

```python
# Secure code
def check_admin_role(user_id):
    # Fetch user role from database
    user_role = get_user_role_from_db(user_id)
    if user_role == 'admin':
        return True
    return False
```

In the secure code, the user role is fetched from the database rather than relying on a client-side cookie.

### Configuration Hardening

To harden your application against access control vulnerabilities, consider the following configurations:

1. **Web Server Configuration**: Configure your web server to enforce secure cookies and restrict access to sensitive resources.
2. **Application Configuration**: Configure your application to enforce strict access controls and validate user roles on the server-side.

#### Example Configuration

Here is an example of configuring a web server to enforce secure cookies:

```nginx
server {
    listen 443 ssl;
    server_name example.com;

    ssl_certificate /etc/nginx/ssl/example.crt;
    ssl_certificate_key /etc/nginx/ssl/example.key;

    location / {
        add_header Set-Cookie "sessionId=$cookie_value; Path=/; HttpOnly; Secure";
        add_header Set-Cookie "isAdmin=$role_value; Path=/; Secure";
    }
}
```

### Conclusion

Access control vulnerabilities, particularly those involving user roles controlled by request parameters, can lead to serious security issues. By understanding the underlying mechanisms and implementing proper security measures, you can protect your applications from such vulnerabilities.

### Practice Labs

For hands-on practice with access control vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various web security topics, including access control.
- **OWASP Juice Shop**: A deliberately insecure web application designed for security training.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

By engaging with these labs, you can gain practical experience in identifying and mitigating access control vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/12-Access Control Vulnerabilities/04-Lab 3 User role controlled by request parameter/01-Introduction to Access Control Vulnerabilities|Introduction to Access Control Vulnerabilities]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/04-Lab 3 User role controlled by request parameter/00-Overview|Overview]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/04-Lab 3 User role controlled by request parameter/03-Access Control Vulnerabilities|Access Control Vulnerabilities]]
