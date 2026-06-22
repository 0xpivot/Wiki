---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Access Control Vulnerabilities

### Introduction to Access Control Vulnerabilities

Access control vulnerabilities occur when an application fails to properly restrict access to resources based on user permissions. These vulnerabilities can lead to unauthorized access to sensitive data, modification of critical information, and even complete compromise of the system. One common type of access control vulnerability is when user IDs are controlled by request parameters, leading to data leakage through redirects.

### Understanding Broken Access Control

Broken access control occurs when an application does not enforce proper authorization checks. In the context of the provided lab, the vulnerability arises from the fact that the user ID is controlled by a request parameter, which can be manipulated by an attacker. When an unauthorized user tries to access another user's account, the application may redirect them to the login page but leak information about the target user in the process.

#### Example Scenario

Consider an application where the URL to view a user's profile is structured as follows:

```
https://example.com/user/profile?userId=123
```

If the `userId` parameter is not properly validated, an attacker can manipulate it to view other users' profiles. For instance, setting `userId=456` might allow the attacker to access the profile of user 456.

### Real-World Examples

Recent real-world examples of broken access control vulnerabilities include:

- **CVE-2021-21972**: A vulnerability in Microsoft Exchange Server allowed attackers to bypass authentication and access sensitive data.
- **CVE-2022-22965**: A vulnerability in VMware Workspace ONE Access and Identity Manager allowed unauthorized access to administrative functions.

These vulnerabilities highlight the importance of implementing robust access control mechanisms to prevent unauthorized access.

### Exploiting the Vulnerability

In the provided lab, the vulnerability is exploited by manipulating the `userId` parameter and observing the behavior of the application. Specifically, the lab demonstrates how an attacker can gain access to sensitive information by intercepting and modifying HTTP redirects.

#### Step-by-Step Exploitation

1. **Log in with the Provided Account**:
    - Use the credentials provided to log in to the application.
    - Observe the structure of the URLs and how the `userId` parameter is used.

2. **Identify the Vulnerable Parameter**:
    - Navigate to the user profile page and note the URL structure.
    - Identify the `userId` parameter and determine if it can be manipulated.

3. **Manipulate the `userId` Parameter**:
    - Change the `userId` parameter to a different value and observe the response.
    - Note if the application redirects to the login page but leaks information about the target user.

4. **Intercept and Modify Redirects**:
    - Use a proxy tool like Burp Suite to intercept and modify HTTP redirects.
    - Convert 302 redirects to 200 OK responses to view the leaked information.

### Detailed Example

Let's walk through a detailed example using the provided scenario.

#### Initial Setup

1. **Log in with the Provided Account**:
    - Use the credentials provided to log in to the application.
    - Observe the structure of the URLs and how the `userId` parameter is used.

```plaintext
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded

username=admin&password=password123
```

Response:

```plaintext
HTTP/1.1 302 Found
Location: /user/profile?userId=1
```

2. **Navigate to the User Profile Page**:
    - Click on the link to view the user profile.
    - Note the URL structure and the `userId` parameter.

```plaintext
GET /user/profile?userId=1 HTTP/1.1
Host: example.com
Cookie: session_id=abc123
```

Response:

```plaintext
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
    <p>Email: admin@example.com</p>
</body>
</html>
```

3. **Manipulate the `userId` Parameter**:
    - Change the `userId` parameter to a different value and observe the response.
    - Note if the application redirects to the login page but leaks information about the target user.

```plaintext
GET /user/profile?userId=2 HTTP/1.1
Host: example.com
Cookie: session_id=abc123
```

Response:

```plaintext
HTTP/1.1 302 Found
Location: /login
```

4. **Intercept and Modify Redirects**:
    - Use a proxy tool like Burp Suite to intercept and modify HTTP redirects.
    - Convert 302 redirects to 200 OK responses to view the leaked information.

```plaintext
GET /user/profile?userId=2 HTTP/1.1
Host: example.com
Cookie: session_id=abc123
```

Response:

```plaintext
HTTP/1.1 200 OK
Content-Type: text/html

<!DOCTYPE html>
<html>
<head>
    <title>User Profile</title>
</head>
<body>
    <h1>User Profile</h1>
    <p>Username: user2</p>
    <p>Email: user2@example.com</p>
</body>
</html>
```

### How to Prevent / Defend

To prevent access control vulnerabilities, several measures can be taken:

1. **Proper Authorization Checks**:
    - Ensure that all access to resources is properly authorized based on user roles and permissions.
    - Implement role-based access control (RBAC) to restrict access to sensitive data.

2. **Input Validation**:
    - Validate all input parameters to ensure they are within expected ranges and formats.
    - Use parameterized queries and prepared statements to prevent SQL injection attacks.

3. **Secure Coding Practices**:
    - Follow secure coding guidelines to avoid common vulnerabilities.
    - Use frameworks and libraries that provide built-in security features.

4. **Configuration Hardening**:
    - Harden server configurations to minimize attack surfaces.
    - Disable unnecessary services and protocols.

5. **Regular Audits and Testing**:
    - Conduct regular security audits and penetration testing to identify and mitigate vulnerabilities.
    - Use automated tools to scan for common vulnerabilities.

### Secure Code Example

Here is an example of how to implement proper authorization checks in a web application:

#### Vulnerable Code

```python
@app.route('/user/profile')
def user_profile():
    user_id = request.args.get('userId')
    user = get_user_by_id(user_id)
    return render_template('profile.html', user=user)
```

#### Secure Code

```python
@app.route('/user/profile')
@login_required
def user_profile():
    user_id = request.args.get('userId')
    current_user_id = current_user.id
    if int(user_id) != current_user_id:
        abort(403)
    user = get_user_by_id(user_id)
    return render_template('profile.html', user=user)
```

### Detection and Prevention Tools

Several tools can help detect and prevent access control vulnerabilities:

- **Burp Suite**: A comprehensive toolkit for web application security testing.
- **OWASP ZAP**: An open-source web application security scanner.
- **SonarQube**: A static code analysis tool that identifies security vulnerabilities.

### Conclusion

Access control vulnerabilities are a significant threat to web applications. By understanding the nature of these vulnerabilities and implementing proper security measures, developers can significantly reduce the risk of unauthorized access and data leakage. Regular security audits and penetration testing are essential to maintaining the security of web applications.

### Practice Labs

For hands-on practice with access control vulnerabilities, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on various web security topics, including access control.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates common web application vulnerabilities.

By engaging with these labs, you can gain practical experience in identifying and mitigating access control vulnerabilities.

---
<!-- nav -->
[[02-Access Control Vulnerabilities User ID Controlled by Request Parameter with Data Leakage in Redirect|Access Control Vulnerabilities User ID Controlled by Request Parameter with Data Leakage in Redirect]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/10-Lab 9 User ID controlled by request parameter with data leakage in redirect/00-Overview|Overview]] | [[04-Creating the Main Method|Creating the Main Method]]
