---
course: API Security
topic: OWASP API TOP 10
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain what broken function level authorization is and provide an example.**

Broken function level authorization occurs when an API allows non-administrative users to access administrative functions without proper authorization. For instance, if an authenticated user can access an admin-specific API endpoint by simply changing the URL from `/users/myinfo` to `/admin/allinfo`, this indicates a vulnerability. This can happen due to insufficient or missing authorization checks on the server side.

**Q2. How can an attacker exploit broken function level authorization?**

An attacker can exploit broken function level authorization by sending legitimate-looking API requests to endpoints that they should not have access to. For example, an attacker might change the URL path from `/users/info` to `/admin/allinfo` or modify parameters like `isAdmin=false` to `isAdmin=true`. If the server does not properly validate the user’s role before processing the request, the attacker could gain unauthorized access to sensitive data or functionalities.

**Q3. Describe a recent real-world example of broken function level authorization.**

A notable example is the GitHub API vulnerability disclosed in 2020 (CVE-2020-14769). The issue allowed authenticated users to access sensitive information by manipulating the API endpoint URLs. Specifically, users could access private repositories and sensitive data by altering the API requests to include paths intended for administrative access. This demonstrates how predictable and structured API endpoints can be exploited if proper authorization checks are not implemented.

**Q4. How can developers prevent broken function level authorization in their APIs?**

To prevent broken function level authorization, developers should implement robust authorization checks for every API endpoint. This includes:

1. **Role-Based Access Control (RBAC):** Ensure that each API endpoint verifies the user’s role before processing the request.
2. **Parameter Validation:** Validate all input parameters to ensure they match the expected roles and permissions.
3. **Endpoint Hardening:** Use unpredictable endpoint names and avoid exposing administrative functions under easily guessable paths.
4. **Regular Audits:** Conduct regular security audits and penetration testing to identify and fix any vulnerabilities.

Here is a simple code snippet demonstrating RBAC in Python:

```python
def handle_request(user_role, endpoint):
    if user_role == 'admin' and endpoint.startswith('/admin'):
        # Process admin-specific logic
        return "Admin endpoint accessed"
    elif user_role == 'user' and endpoint.startswith('/user'):
        # Process user-specific logic
        return "User endpoint accessed"
    else:
        raise PermissionError("Unauthorized access attempt")

# Example usage
try:
    print(handle_request('user', '/admin/allinfo'))
except PermissionError as e:
    print(e)
```

**Q5. What are the steps to test for broken function level authorization in an API?**

Testing for broken function level authorization involves several steps:

1. **Identify User Roles and Permissions:** Understand the different roles and their associated permissions within the application.
2. **Map API Endpoints:** Document all available API endpoints and their intended access levels.
3. **Perform Role Switching Tests:** Test each endpoint by simulating different user roles to ensure that unauthorized access attempts are blocked.
4. **Check Parameter Manipulation:** Test endpoints by modifying parameters such as `isAdmin` to see if the server enforces proper authorization.
5. **Use Automated Tools:** Utilize security tools like Burp Suite or OWASP ZAP to automate the process of detecting unauthorized access.

By following these steps, developers can ensure that their APIs are secure against broken function level authorization attacks.

---
<!-- nav -->
[[03-Understanding Broken Function Level Authorization|Understanding Broken Function Level Authorization]] | [[API Security/05-OWASP API TOP 10/06-API5 Broken Function Level Authorization/00-Overview|Overview]]
