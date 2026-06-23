---
course: API Security
topic: OWASP API TOP 10
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain what mass assignment is in the context of API security.**

Mass assignment refers to a vulnerability where an API accepts and processes data from a client without properly filtering or validating the input against a whitelist of allowed properties. This allows an attacker to potentially modify sensitive properties that were not intended to be exposed or modified. For instance, an attacker could manipulate a request to set a `has_admin_role` property to `true`, thereby elevating their privileges.

**Q2. How can an attacker exploit a mass assignment vulnerability?**

To exploit a mass assignment vulnerability, an attacker needs to identify the properties that can be manipulated. This can often be achieved by reviewing the API documentation or using tools like Postman to explore the API endpoints. Once identified, the attacker constructs a request that includes additional properties, such as setting `has_admin_role` to `true`. If the API does not filter these properties correctly, the attacker's request will be processed, leading to unauthorized privilege escalation or data tampering.

**Q3. Describe a real-world example of a mass assignment vulnerability and its impact.**

A notable example of a mass assignment vulnerability occurred in the Ruby on Rails framework, which was exploited in various web applications. One such case involved the popular job board site Indeed.com. Attackers exploited a mass assignment vulnerability to gain unauthorized access to user accounts and potentially modify sensitive data. This incident highlights the critical need for proper validation and filtering of input data to prevent such vulnerabilities.

**Q4. How can developers mitigate the risk of mass assignment vulnerabilities in their APIs?**

Developers can mitigate the risk of mass assignment vulnerabilities by implementing strict input validation and filtering mechanisms. Specifically:

1. **Whitelist Filtering**: Ensure that only a predefined set of properties can be updated via API requests. Any additional properties should be ignored.
   
2. **Parameter Sanitization**: Use sanitization techniques to ensure that input data conforms to expected formats and values.

3. **Role-Based Access Control (RBAC)**: Implement RBAC to restrict which properties can be updated based on the user’s role and permissions.

4. **Automated Testing**: Regularly test APIs using automated tools to detect potential mass assignment vulnerabilities.

Here is an example of how to implement whitelist filtering in Python using Flask:

```python
from flask import Flask, request, jsonify

app = Flask(__name__)

# Whitelist of allowed properties
allowed_properties = {'username', 'email', 'real_name'}

@app.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    filtered_data = {k: v for k, v in data.items() if k in allowed_properties}
    # Process filtered_data
    return jsonify(filtered_data)

if __name__ == '__main__':
    app.run(debug=True)
```

**Q5. What are some common sensitive properties that attackers might target in a mass assignment attack?**

Attackers often target sensitive properties that can grant elevated privileges or control over the system. Common examples include:

1. **Permission-related properties**: Properties like `is_admin`, `has_admin_role`, or `is_superuser`.
2. **Process-dependent properties**: Properties that should only be set internally after certain verifications, such as `payment_status` or `verified_email`.
3. **Internal properties**: Properties that should only be managed by the application itself, such as `created_at` or `updated_at`.

By manipulating these properties, attackers can gain unauthorized access, modify critical data, or bypass security mechanisms.

---
<!-- nav -->
[[05-Understanding Mass Assignment Vulnerability|Understanding Mass Assignment Vulnerability]] | [[API Security/05-OWASP API TOP 10/07-API6 Mass Assignment/00-Overview|Overview]]
