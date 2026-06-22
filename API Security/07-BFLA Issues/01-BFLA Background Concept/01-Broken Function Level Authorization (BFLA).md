---
course: API Security
topic: BFLA Issues
tags: [api-security]
---

## Broken Function Level Authorization (BFLA)

### Introduction

Broken Function Level Authorization (BFLA) is a critical security issue that arises when an application fails to properly restrict access to sensitive functions based on user roles or permissions. This vulnerability allows unauthorized users to perform actions that should be restricted to specific roles, such as administrators. In this section, we will delve into the details of BFLA, including its causes, impacts, and methods to identify and mitigate it.

### Understanding BFLA

#### What is BFLA?

Broken Function Level Authorization occurs when an application does not enforce proper access controls on its functions. This means that users with lower privileges can access and execute functions intended for higher-privileged users, such as administrators. This can lead to severe security breaches, including data theft, unauthorized modifications, and even system compromise.

#### Why Does BFLA Matter?

BFLA is significant because it undermines the fundamental principle of least privilege, which states that users should have the minimum level of access necessary to perform their tasks. When BFLA is present, users can bypass these restrictions and gain access to sensitive operations, leading to potential security incidents.

### Identifying BFLA

#### Administrative Functions Exposed as APIs

One common scenario where BFLA can occur is when administrative functions are exposed as APIs. These functions might include operations like creating, deleting, or modifying user accounts, managing system configurations, or performing other high-privilege actions. If these functions are accessible via API endpoints without proper authorization checks, non-privileged users can exploit them.

##### Example: Exposed User Management API

Consider an API endpoint `/api/v1/users` that allows users to manage user accounts. If this endpoint is accessible without proper authorization checks, a non-administrative user might be able to perform actions like:

- **GET** `/api/v1/users`: Retrieve a list of all users.
- **POST** `/api/v1/users`: Create a new user account.
- **DELETE** `/api/v1/users/{id}`: Delete a user account.

If these actions are not properly restricted, a non-administrative user could potentially access and modify sensitive user data.

```http
GET /api/v1/users HTTP/1.1
Host: example.com
Authorization: Bearer <token>

HTTP/1.1 200 OK
Content-Type: application/json

[
    {
        "id": 1,
        "username": "admin",
        "email": "admin@example.com"
    },
    {
        "id": 2,
        "username": "user1",
        "email": "user1@example.com"
    }
]
```

```http
POST /api/v1/users HTTP/1.1
Host: example.com
Authorization: Bearer <token>
Content-Type: application/json

{
    "username": "newuser",
    "email": "newuser@example.com",
    "password": "securepassword"
}

HTTP/1.1 201 Created
Location: /api/v1/users/3
```

```http
DELETE /api/v1/users/2 HTTP/1.1
Host: example.com
Authorization: Bearer <token>

HTTP/1.1 204 No Content
```

### Methods to Identify BFLA

#### URL Manipulation

One way to identify BFLA is by manipulating URLs and HTTP verbs to see if unauthorized access is possible. For example, changing the HTTP method from `GET` to `POST` or `DELETE` can reveal whether the application enforces proper authorization.

##### Example: Changing HTTP Method

Suppose an API endpoint `/api/v1/users/{id}` is designed to retrieve user information using `GET`. If a non-administrative user can change the HTTP method to `DELETE`, they might be able to delete a user account.

```http
GET /api/v1/users/2 HTTP/1.1
Host: example.com
Authorization: Bearer <token>

HTTP/1.1 200 OK
Content-Type: application/json

{
    "id": 2,
    "username": "user1",
    "email": "user1@example.com"
}
```

```http
DELETE /api/v1/users/2 HTTP/1.1
Host: example.com
Authorization: Bearer <token>

HTTP/1.1 204 No Content
```

### Real-World Examples

#### Recent CVEs and Breaches

Several recent CVEs and breaches highlight the severity of BFLA issues. For instance, CVE-2021-3129, a vulnerability in the Jenkins CI/CD platform, allowed attackers to execute arbitrary code due to improper authorization checks. Similarly, the Capital One breach in 2019 was partly due to misconfigured access controls, allowing unauthorized access to sensitive data.

### How to Prevent / Defend Against BFLA

#### Detection

To detect BFLA, organizations should conduct thorough security assessments, including:

- **Penetration Testing**: Simulate attacks to identify unauthorized access points.
- **Code Reviews**: Manually review code to ensure proper authorization checks are in place.
- **Automated Scanning**: Use tools like Burp Suite, OWASP ZAP, or commercial scanners to identify potential vulnerabilities.

#### Prevention

To prevent BFLA, follow these best practices:

- **Role-Based Access Control (RBAC)**: Implement RBAC to ensure users have only the permissions necessary to perform their tasks.
- **Least Privilege Principle**: Assign the minimum set of permissions required for each role.
- **Authorization Checks**: Ensure that every API endpoint performs proper authorization checks before executing any action.

##### Secure Coding Practices

Here is an example of how to implement proper authorization checks in a Python Flask application:

```python
from flask import Flask, request, jsonify
from functools import wraps

app = Flask(__name__)

# Sample user roles
users = {
    'admin': {'role': 'admin'},
    'user1': {'role': 'user'}
}

def check_auth(username, password):
    return username in users and users[username]['password'] == password

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return jsonify({'message': 'Authentication failed'}), 401
        return f(*args, **kwargs)
    return decorated

@app.route('/api/v1/users', methods=['GET'])
@requires_auth
def get_users():
    user_role = users[request.authorization.username]['role']
    if user_role != 'admin':
        return jsonify({'message': 'Unauthorized access'}), 403
    return jsonify(users)

@app.route('/api/v1/users/<int:user_id>', methods=['DELETE'])
@requires_auth
def delete_user(user_id):
    user_role = users[request.authorization.username]['role']
    if user_role != 'admin':
        return jsonify({'message': 'Unauthorized access'}), 403
    del users[user_id]
    return jsonify({'message': 'User deleted'})

if __name__ == '__main__':
    app.run(debug=True)
```

### Conclusion

Broken Function Level Authorization is a serious security issue that can lead to significant breaches if not properly addressed. By understanding the causes and impacts of BFLA, and implementing robust detection and prevention strategies, organizations can significantly reduce the risk of unauthorized access to sensitive functions.

### Practice Labs

For hands-on experience with identifying and mitigating BFLA, consider the following practice labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice identifying and exploiting BFLA vulnerabilities.
- **OWASP Juice Shop**: A deliberately insecure web application that includes various security vulnerabilities, including BFLA.
- **DVWA (Damn Vulnerable Web Application)**: Provides a range of web application vulnerabilities, including BFLA, for educational purposes.

By engaging with these labs, you can gain practical experience in detecting and preventing BFLA issues in real-world applications.

---
<!-- nav -->
[[API Security/07-BFLA Issues/01-BFLA Background Concept/00-Overview|Overview]] | [[API Security/07-BFLA Issues/01-BFLA Background Concept/02-Practice Questions & Answers|Practice Questions & Answers]]
