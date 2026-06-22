---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## How to Prevent / Defend

### Detection

To detect method-based access control vulnerabilities, you can use automated tools and manual testing techniques:

- **Automated Tools**: Tools like Burp Suite, OWASP ZAP, and WAPT can help identify unexpected behavior when different HTTP methods are used.
- **Manual Testing**: Manually test endpoints by sending requests with different HTTP methods and observing the responses.

### Prevention

To prevent method-based access control vulnerabilities, follow these best practices:

1. **Validate HTTP Methods**: Ensure that the application validates the HTTP method used in requests and only allows the expected methods.
2. **Use Role-Based Access Control (RBAC)**: Implement RBAC to ensure that users can only perform actions based on their roles and privileges.
3. **Audit Logs**: Maintain detailed audit logs to track access attempts and detect suspicious activity.
4. **Input Validation**: Validate all input parameters to ensure they meet the expected criteria.

### Secure Coding Fixes

Here is an example of how to implement secure coding practices to prevent method-based access control vulnerabilities:

#### Vulnerable Code

```python
@app.route('/promote', methods=['PUT'])
def promote_user():
    username = request.json['username']
    role = request.json['role']
    # Promote user logic
    return jsonify({"message": f"User '{username}' promoted to {role} successfully."})
```

#### Secure Code

```python
@app.route('/promote', methods=['PUT'])
def promote_user():
    if request.method != 'PUT':
        abort(405)
    username = request.json['username']
    role = request.json['role']
    # Promote user logic
    return jsonify({"message": f"User '{username}' promoted to {role} successfully."})
```

### Configuration Hardening

Ensure that your web server and application configurations are hardened to prevent unauthorized access:

- **Web Server Configuration**: Configure your web server to restrict access to sensitive endpoints.
- **Application Configuration**: Configure your application to enforce strict access control policies.

### Mitigations

Implement the following mitigations to further protect against method-based access control vulnerabilities:

- **Rate Limiting**: Implement rate limiting to prevent brute-force attacks.
- **Captcha**: Use CAPTCHA to prevent automated attacks.
- **Two-Factor Authentication (2FA)**: Implement 2FA to add an additional layer of security.

---
<!-- nav -->
[[04-Analyzing the Vulnerability|Analyzing the Vulnerability]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/07-Lab 6 Method based access control can be circumvented/00-Overview|Overview]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/07-Lab 6 Method based access control can be circumvented/06-Practice Labs|Practice Labs]]
