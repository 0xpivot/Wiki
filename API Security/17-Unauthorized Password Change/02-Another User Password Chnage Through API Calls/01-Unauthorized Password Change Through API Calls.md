---
course: API Security
topic: Unauthorized Password Change
tags: [api-security]
---

## Unauthorized Password Change Through API Calls

### Introduction

In the realm of API security, unauthorized access and manipulation of sensitive data, such as user passwords, are critical vulnerabilities. This section delves into the scenario where an attacker attempts to change another user's password through API calls, which is unauthorized and poses significant risks to the system's integrity and user privacy.

### Background Theory

APIs (Application Programming Interfaces) are the backbone of modern web applications, enabling communication between different software components. They allow developers to interact with services and databases programmatically. However, APIs can also introduce security risks if not properly secured. One such risk is unauthorized access to sensitive operations, like changing user passwords.

#### What is an API?

An API is a set of rules and protocols for building and interacting with software applications. It defines the methods and data formats that software components can use to communicate with each other. In the context of web applications, APIs often expose endpoints that can be accessed via HTTP requests.

#### Why is API Security Important?

API security is crucial because APIs often handle sensitive data and provide access to core functionalities of an application. If an API is not properly secured, attackers can exploit vulnerabilities to gain unauthorized access, manipulate data, or perform malicious actions.

### Scenario: Unauthorized Password Change

Let's consider a scenario where an attacker tries to change another user's password through API calls. This scenario highlights the importance of proper authentication and authorization mechanisms in API design.

#### Step-by-Step Mechanics

1. **User Registration**:
    - An attacker creates a new user account to gain access to the system.
    - The attacker provides necessary details such as username, password, and email address.

2. **Authentication**:
    - The attacker logs in to obtain an authentication token.
    - This token is used to authenticate subsequent API requests.

3. **Unauthorized Access**:
    - The attacker uses the obtained token to make unauthorized API calls to change another user's password.

### Detailed Example

Let's walk through the detailed steps and code involved in this scenario.

#### User Registration

The attacker first registers a new user account. Here is an example of the registration process:

```http
POST /users/register HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "username": "offensive_hunter",
  "password": "offensive_hunter_7",
  "email": "offensive_hunter_007@gmail.com"
}
```

Upon successful registration, the server responds with a confirmation message:

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "message": "User registered successfully."
}
```

#### Authentication

Next, the attacker logs in to obtain an authentication token. Here is the login request:

```http
POST /auth/login HTTP/1.1
Host: example.com
Content-Type: application/json

{
  "username": "offensive_hunter",
  "password": "offensive_hunter_7"
}
```

Upon successful login, the server responds with an authentication token:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### Unauthorized Access

With the obtained token, the attacker attempts to change another user's password. Here is an example of the unauthorized API call:

```http
PUT /users/{userId}/change-password HTTP/1.1
Host: example.com
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Content-Type: application/json

{
  "new_password": "new_secret_password"
}
```

If the API does not properly validate the user's permissions, the attacker might succeed in changing the password.

### Mermaid Diagrams

To visualize the flow of the attack, we can use a sequence diagram:

```mermaid
sequenceDiagram
  participant Attacker
  participant Server
  participant Database
  
  Attacker->>Server: POST /users/register
  Server-->>Attacker: 201 Created
  Attacker->>Server: POST /auth/login
  Server-->>Attacker: 200 OK (Token)
  Attacker->>Server: PUT /users/{userId}/change-password
  Server-->>Database: Update Password
  Database-->>Server: Success
  Server-->>Attacker: 200 OK
```

### Real-World Examples

Recent breaches and vulnerabilities related to unauthorized access through APIs include:

- **CVE-2021-21972**: A vulnerability in the WordPress REST API allowed unauthorized users to modify posts and pages.
- **CVE-2020-14182**: A vulnerability in the Shopify API allowed unauthorized access to customer data.

These examples highlight the importance of robust authentication and authorization mechanisms in API design.

### How to Prevent / Defend

#### Detection

To detect unauthorized access attempts, implement logging and monitoring mechanisms. Log all API requests and analyze them for suspicious activity. Use tools like Splunk or ELK Stack for centralized logging and analysis.

#### Prevention

1. **Strong Authentication Mechanisms**:
    - Use multi-factor authentication (MFA) to enhance security.
    - Implement OAuth 2.0 and OpenID Connect for secure authentication.

2. **Proper Authorization**:
    - Ensure that each API endpoint checks the user's permissions before allowing access.
    - Use role-based access control (RBAC) to restrict access based on user roles.

3. **Secure Token Management**:
    - Use JWT (JSON Web Tokens) with proper validation and expiration policies.
    - Implement token revocation mechanisms to invalidate compromised tokens.

4. **Input Validation**:
    - Validate all input parameters to prevent injection attacks.
    - Use parameterized queries to prevent SQL injection.

5. **Secure Coding Practices**:
    - Follow secure coding guidelines to avoid common vulnerabilities.
    - Use static code analysis tools like SonarQube to identify security issues.

#### Secure Code Fix

Here is an example of a vulnerable API endpoint and its secure counterpart:

**Vulnerable Code**:

```python
@app.route('/users/<int:user_id>/change-password', methods=['PUT'])
def change_password(user_id):
    new_password = request.json['new_password']
    # Vulnerable: No permission check
    update_password(user_id, new_password)
    return jsonify({"message": "Password changed successfully"})
```

**Secure Code**:

```python
@app.route('/users/<int:user_id>/change-password', methods=['PUT'])
@jwt_required()
def change_password(user_id):
    current_user = get_jwt_identity()
    if current_user != user_id:
        return jsonify({"error": "Unauthorized"}), 403
    
    new_password = request.json['new_password']
    # Secure: Permission check implemented
    update_password(user_id, new_password)
    return jsonify({"message": "Password changed successfully"})
```

### Conclusion

Unauthorized access to sensitive operations through APIs is a serious security concern. By implementing strong authentication, proper authorization, and secure coding practices, organizations can significantly reduce the risk of such attacks. Regularly auditing and testing APIs for vulnerabilities is essential to maintaining a secure environment.

### Hands-On Labs

For practical experience with API security, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive modules on API security, including unauthorized access scenarios.
- **OWASP Juice Shop**: A deliberately insecure web app for practicing various security techniques, including API exploitation.
- **DVWA (Damn Vulnerable Web Application)**: Provides a range of web application vulnerabilities, including those related to APIs.

By engaging with these labs, you can gain hands-on experience in identifying and mitigating API security risks.

---
<!-- nav -->
[[API Security/17-Unauthorized Password Change/02-Another User Password Chnage Through API Calls/00-Overview|Overview]] | [[02-Understanding Unauthorized Password Change Through API Calls|Understanding Unauthorized Password Change Through API Calls]]
