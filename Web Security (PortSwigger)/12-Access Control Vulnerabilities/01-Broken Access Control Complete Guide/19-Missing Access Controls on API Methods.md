---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Missing Access Controls on API Methods

### What are APIs?

APIs (Application Programming Interfaces) are sets of protocols and tools for building software applications. They allow different software components to communicate with each other and exchange data.

### Why Are APIs Vulnerable?

APIs are often exposed to the internet and can be accessed by both legitimate and malicious actors. If proper access controls are not implemented, attackers can exploit the API to perform unauthorized actions.

### Example: Missing Access Controls on POST, PUT, DELETE Methods

Consider an API endpoint that allows users to create, update, and delete resources. The API might have endpoints like `/api/resource`, `/api/resource/{id}`, etc. If the API does not properly enforce access controls on these methods, an attacker could perform unauthorized actions.

For example, the following API endpoint might be vulnerable:

```http
POST /api/resource
Content-Type: application/json

{
    "name": "New Resource",
    "description": "This is a new resource"
}
```

If the API does not check whether the user is authorized to create a new resource, an attacker could exploit this to create unauthorized resources.

### Real-World Example: CVE-2021-3427

In 2021, a vulnerability was discovered in a popular API management platform where access controls were not properly enforced on certain API methods. An attacker could exploit this to create, update, or delete resources without proper authorization.

### How to Exploit

To exploit this vulnerability, an attacker would send a request to the API endpoint without proper authorization. For example:

```http
POST /api/resource
Content-Type: application/json

{
    "name": "Unauthorized Resource",
    "description": "This is an unauthorized resource"
}
```

### How to Prevent / Defend

#### Detection

Automated tools like Burp Suite or OWASP ZAP can help detect missing access controls on API methods by analyzing API requests and observing changes in the application's behavior.

#### Prevention

1. **Implement Access Controls**: Ensure that access controls are implemented on all API methods and enforced on the server side.
2. **Use Role-Based Access Control (RBAC)**: Implement RBAC to ensure that users can only access resources appropriate to their roles.
3. **Secure Coding Practices**: Ensure that all input parameters are validated and sanitized.

#### Secure Code Fix

**Vulnerable Code:**

```python
@app.route('/api/resource', methods=['POST'])
def create_resource():
    data = request.get_json()
    # Create resource
    return jsonify({"message": "Resource created"})
```

**Fixed Code:**

```python
@app.route('/api/resource', methods=['POST'])
@jwt_required()
def create_resource():
    current_user = get_jwt_identity()
    if current_user['role'] == 'admin':
        data = request.get_json()
        # Create resource
        return jsonify({"message": "Resource created"})
    else:
        return jsonify({"message": "Access Denied"}), 403
```

### Summary

Missing access controls on API methods is a common vulnerability that can be exploited to perform unauthorized actions. Proper validation and enforcement of access control mechanisms can prevent such attacks.

---

---
<!-- nav -->
[[18-Manipulating Metadata JSON Web Tokens and Cookies|Manipulating Metadata JSON Web Tokens and Cookies]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/01-Broken Access Control Complete Guide/00-Overview|Overview]] | [[20-Principle of Least Privilege|Principle of Least Privilege]]
