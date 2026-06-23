---
course: API Security
topic: Mass Assignment Attack
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain what mass assignment is and why it poses a security risk in APIs.**

Mass assignment occurs when an API allows an attacker to set multiple attributes of an object in a single request. This can pose a significant security risk because it might allow an attacker to modify sensitive fields that should not be accessible or modifiable by the user. For example, an attacker might be able to change a user’s role from 'user' to 'admin', thereby gaining unauthorized access to administrative functions.

**Q2. How can you identify potential mass assignment vulnerabilities in an API?**

To identify potential mass assignment vulnerabilities, you should look for endpoints that accept multiple parameters in a single request. Specifically, check if the API allows setting sensitive attributes such as roles, permissions, or other critical data. Testing involves sending crafted requests with additional parameters to see if the API accepts and processes them. For instance, if a user registration endpoint accepts a `username` and `password`, you might test whether it also accepts an `isAdmin` parameter.

**Q3. Describe how an attacker could exploit a mass assignment vulnerability in a password reset functionality.**

An attacker could exploit a mass assignment vulnerability in a password reset functionality by manipulating the request parameters. For example, if the password reset endpoint accepts both the new password and the old password, an attacker might attempt to omit the old password parameter and include additional parameters that could modify other attributes, such as user roles. If the API does not properly validate or sanitize these inputs, the attacker could potentially elevate their privileges or perform other unauthorized actions.

**Q4. How would you mitigate mass assignment vulnerabilities in an API?**

Mitigating mass assignment vulnerabilities involves several strategies:

1. **Whitelist Attributes**: Explicitly define which attributes can be updated through each endpoint. Only allow the specified attributes to be modified.
   
2. **Parameter Validation**: Ensure that all incoming parameters are validated against expected values and types. Reject any unexpected or malformed parameters.

3. **Role-Based Access Control (RBAC)**: Implement RBAC to ensure that only authorized users can modify certain attributes. For example, only administrators should be able to change user roles.

4. **Input Sanitization**: Sanitize all user inputs to prevent injection attacks and ensure that only valid data is processed.

Here is an example of whitelisting attributes in a Python Flask application:

```python
from flask import Flask, request

app = Flask(__name__)

@app.route('/update_user/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    allowed_fields = ['username', 'email']
    data = {k: v for k, v in request.json.items() if k in allowed_fields}
    # Update the user with the sanitized data
    return f"User {user_id} updated with {data}", 200

if __name__ == '__main__':
    app.run(debug=True)
```

**Q5. Provide a recent real-world example of a mass assignment vulnerability and explain how it was exploited.**

One notable example is the mass assignment vulnerability found in the popular Ruby on Rails framework. In 2012, a vulnerability was discovered where an attacker could exploit the `create` action in a controller to assign arbitrary attributes, including sensitive ones like `admin`. The attacker could send a POST request to create a new user and include an `admin` parameter set to `true`.

For example, the following payload could be used:

```json
{
  "user": {
    "username": "attacker",
    "email": "attacker@example.com",
    "admin": true
  }
}
```

If the application did not properly restrict which attributes could be assigned, the attacker could gain administrative privileges. This vulnerability led to widespread concern and prompted many developers to implement stricter controls around mass assignment.

**Q6. How can you test for mass assignment vulnerabilities in an API?**

Testing for mass assignment vulnerabilities involves the following steps:

1. **Identify Endpoints**: Identify all endpoints that accept multiple parameters, especially those related to user management, such as registration, profile updates, and password resets.

2. **Craft Malicious Requests**: Craft requests that include additional parameters that should not be modifiable by the user. For example, include an `isAdmin` parameter in a user registration request.

3. **Monitor Responses**: Monitor the responses to see if the API accepts and processes the additional parameters. If the API modifies the attributes as intended by the malicious request, it indicates a mass assignment vulnerability.

4. **Automate Testing**: Use automated tools like Burp Suite, OWASP ZAP, or custom scripts to automate the testing process and systematically test all endpoints.

By following these steps, you can effectively identify and mitigate mass assignment vulnerabilities in your API.

---
<!-- nav -->
[[04-Understanding Mass Assignment Vulnerability|Understanding Mass Assignment Vulnerability]] | [[API Security/10-Mass Assignment Attack/04-Mass Assignment Preparation/00-Overview|Overview]]
