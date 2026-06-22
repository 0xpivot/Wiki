---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Access Control Vulnerabilities: Method-Based Access Control Can Be Circumvented

### Background Theory

Access control is a fundamental aspect of web application security. It ensures that users have appropriate permissions to access resources and perform actions within the application. Access control mechanisms can be broadly categorized into two types:

1. **Role-Based Access Control (RBAC)**: Users are assigned roles, and these roles determine their access rights.
2. **Attribute-Based Access Control (ABAC)**: Access decisions are made based on attributes such as user identity, resource properties, and environmental conditions.

In the context of web applications, method-based access control refers to the enforcement of access rules based on the HTTP methods used (e.g., GET, POST, PUT, DELETE). This approach relies on the assumption that certain methods are inherently more secure than others. However, this assumption can be flawed, leading to vulnerabilities.

### Understanding the Scenario

Let's delve into the scenario described in the lecture transcript. We are dealing with a web application that allows administrative actions such as upgrading or downgrading user roles. These actions are performed via HTTP POST requests to specific endpoints.

#### Key Concepts

- **HTTP Methods**: Different HTTP methods (GET, POST, PUT, DELETE) are used to perform various operations on resources. In this case, the POST method is used to modify user roles.
- **Endpoints**: Specific URLs within the application that handle particular actions. For example, `/admin/roles` is the endpoint used to manage user roles.
- **Burp Suite**: A popular tool used for web application security testing. It includes features like the built-in browser and the HTTP History tab, which help in intercepting and analyzing HTTP requests.

### Analyzing the Request

The lecture describes logging into the admin account and performing an action to upgrade a user's role. Let's break down the HTTP request involved in this process.

#### HTTP Request Analysis

```http
POST /admin/roles HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 25

username=Carlos&action=upgrade
```

- **Method**: `POST`
- **Endpoint**: `/admin/roles`
- **Headers**:
  - `Host`: Specifies the target server.
  - `Content-Type`: Indicates the format of the data being sent (`application/x-www-form-urlencoded`).
  - `Content-Length`: Specifies the length of the body in bytes.
- **Body**: Contains the parameters `username` and `action`.

### Exploiting Method-Based Access Control

The vulnerability arises from the fact that the application relies solely on the HTTP method (POST) to enforce access control. An attacker can potentially bypass this control by crafting malicious requests that mimic legitimate ones.

#### Real-World Example: CVE-2021-21972

CVE-2021-21972 is a real-world example where a similar vulnerability was exploited in a web application. The application allowed unauthorized users to perform administrative actions by manipulating HTTP requests.

### Steps to Exploit

1. **Intercept the Request**: Use Burp Suite to intercept the HTTP request sent when upgrading a user's role.
2. **Analyze the Request**: Understand the structure of the request, including the method, endpoint, and parameters.
3. **Craft Malicious Requests**: Create new requests that mimic the original but are sent from a non-administrative account.

#### Example Exploit

```http
POST /admin/roles HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 25

username=attacker&action=upgrade
```

By sending this request, an attacker can attempt to upgrade their own role or manipulate other users' roles.

### How to Prevent / Defend

To prevent method-based access control vulnerabilities, several measures can be implemented:

1. **Role-Based Access Control (RBAC)**: Ensure that access controls are enforced based on user roles rather than just HTTP methods.
2. **Input Validation**: Validate all input parameters to ensure they conform to expected formats and values.
3. **Authorization Checks**: Implement robust authorization checks to verify that the user making the request has the necessary privileges.
4. **Logging and Monitoring**: Maintain detailed logs of access attempts and monitor for suspicious activity.

#### Secure Coding Fixes

Here’s an example of how to implement secure coding practices to prevent such vulnerabilities:

```python
# Vulnerable Code
@app.route('/admin/roles', methods=['POST'])
def upgrade_user():
    username = request.form['username']
    action = request.form['action']
    if action == 'upgrade':
        # Upgrade user logic
        pass
    elif action == 'downgrade':
        # Downgrade user logic
        pass
    return "Action completed"

# Secure Code
@app.route('/admin/roles', methods=['POST'])
def upgrade_user_secure():
    username = request.form['username']
    action = request.form['action']
    
    # Check if the current user is an admin
    if not current_user.is_admin:
        return "Unauthorized", 403
    
    if action == 'upgrade':
        # Upgrade user logic
        pass
    elif action == 'downgrade':
        # Downgrade user logic
        pass
    return "Action completed"
```

### Detection and Prevention

Detection of method-based access control vulnerabilities can be achieved through:

- **Automated Scanning Tools**: Use tools like Burp Suite, OWASP ZAP, and Nessus to scan for vulnerabilities.
- **Penetration Testing**: Conduct regular penetration tests to identify and mitigate potential vulnerabilities.
- **Security Audits**: Perform periodic security audits to ensure compliance with best practices.

### Conclusion

Method-based access control can be easily circumvented if not properly implemented. By understanding the underlying principles and implementing robust security measures, developers can significantly reduce the risk of such vulnerabilities. Always validate inputs, enforce proper authorization, and maintain comprehensive logging and monitoring systems to detect and respond to suspicious activities.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers numerous labs on access control vulnerabilities.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing various security techniques.
- **DVWA (Damn Vulnerable Web Application)**: A deliberately insecure web application for learning about web application security.

These labs provide practical experience in identifying and mitigating access control vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/12-Access Control Vulnerabilities/07-Lab 6 Method based access control can be circumvented/01-Introduction to Access Control Vulnerabilities|Introduction to Access Control Vulnerabilities]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/07-Lab 6 Method based access control can be circumvented/00-Overview|Overview]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/07-Lab 6 Method based access control can be circumvented/03-Access Control Vulnerabilities|Access Control Vulnerabilities]]
