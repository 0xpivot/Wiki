---
course: API Security
topic: BFLA Issues
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain what is meant by "broken function level authorization" in the context of API security.**

Broken function level authorization refers to a situation where unauthorized users can access administrative or sensitive functions through APIs. This typically occurs when proper access controls are not enforced, allowing non-privileged users to perform actions they should not be permitted to do, such as accessing administrative functions or modifying data.

**Q2. How can you identify if administrative functions are exposed as APIs without proper authorization?**

To identify if administrative functions are exposed as APIs without proper authorization, you can follow these steps:

1. **Review API Endpoints**: Check the documentation and test the API endpoints to see if any administrative functions are accessible.
2. **Test with Non-Privileged User**: Attempt to access these endpoints using credentials of a non-administrative user to see if they can still access administrative functionalities.
3. **Manipulate HTTP Verbs and Parameters**: Try changing the HTTP verbs (GET, POST, DELETE) and parameters to see if unauthorized actions can be performed.

For example, if an endpoint like `/api/v1/users` returns detailed user information, testing with a non-admin user should not return any results or should return only limited information.

**Q3. Provide an example of how to exploit a broken function level authorization vulnerability.**

Suppose you discover an API endpoint `/api/v1/users` which returns detailed user information. To exploit a potential broken function level authorization vulnerability, you can:

1. **Access the Endpoint**: Use a non-administrative user token to make a GET request to `/api/v1/users`.
2. **Check Response**: If the response contains detailed information about all users, it indicates a lack of proper authorization.
3. **Manipulate HTTP Methods**: Change the HTTP method to DELETE and attempt to delete a user record. For example, sending a DELETE request to `/api/v1/users/{userId}` might succeed if the authorization is broken.

Here’s a sample payload using `curl`:

```bash
curl -X DELETE \
     -H "Authorization: Bearer <non-admin-user-token>" \
     http://example.com/api/v1/users/12345
```

If this request succeeds, it demonstrates a broken function level authorization issue.

**Q4. What recent real-world examples or CVEs highlight issues related to broken function level authorization?**

One notable example is the 2021 incident involving a popular cloud storage service, where unauthorized users could access sensitive administrative functions due to improper authorization controls. In this case, attackers were able to manipulate API endpoints to gain elevated privileges and access confidential data.

Another example is CVE-2021-27653, which affected a widely used open-source project management tool. The vulnerability allowed authenticated users to bypass intended access restrictions and execute administrative functions, leading to potential data exposure and manipulation.

These incidents underscore the importance of implementing robust access control mechanisms and regularly auditing API endpoints for unauthorized access.

**Q5. How can developers prevent broken function level authorization vulnerabilities in their APIs?**

Developers can prevent broken function level authorization vulnerabilities by following these best practices:

1. **Implement Role-Based Access Control (RBAC)**: Ensure that API endpoints are protected by role-based access control, where users are granted permissions based on their roles.
2. **Use Authorization Headers**: Require authentication tokens in every request and validate them against the user's role before granting access to resources.
3. **Limit Scope of Permissions**: Grant the minimum necessary permissions required for a user to perform their tasks, avoiding overly broad access rights.
4. **Regular Audits and Testing**: Conduct regular security audits and penetration testing to identify and fix potential vulnerabilities.
5. **Documentation and Training**: Maintain clear documentation of API endpoints and their access requirements, and provide training to developers on secure coding practices.

By adhering to these guidelines, developers can significantly reduce the risk of broken function level authorization vulnerabilities in their APIs.

---
<!-- nav -->
[[01-Broken Function Level Authorization (BFLA)|Broken Function Level Authorization (BFLA)]] | [[API Security/07-BFLA Issues/01-BFLA Background Concept/00-Overview|Overview]]
