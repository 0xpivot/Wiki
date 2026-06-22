---
course: API Security
topic: BFLA Issues
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain the concept of broken functional level authorization in the context of API security.**

Broken functional level authorization occurs when an application fails to properly enforce access controls, allowing unauthorized users to perform actions that should be restricted to specific roles. In the context of API security, this can mean that an attacker can manipulate API endpoints to perform actions such as modifying user roles or accessing sensitive data without proper authentication or authorization checks.

**Q2. How would you exploit a broken functional level authorization vulnerability to escalate privileges in an API?**

To exploit a broken functional level authorization vulnerability, follow these steps:

1. Identify an endpoint that allows modification of user roles, such as PUT /users/{id}.
2. Use the endpoint to modify your user role to an administrative role by changing the role ID to the ID corresponding to an admin role.
3. Verify the change by querying the user information endpoint, such as GET /users/{id}, to ensure the role has been updated.

For example, if the role ID for an admin is `1`, you could construct a request like this:

```json
PUT /users/2 HTTP/1.1
Host: target.example.com
Content-Type: application/json

{
    "role_id": 1
}
```

After sending this request, you should verify the role change by fetching the user details:

```http
GET /users/2 HTTP/1.1
Host: target.example.com
```

If the response shows the role ID as `1`, the privilege escalation was successful.

**Q3. How would you exploit a broken functional level authorization vulnerability to manipulate grades in a student portal API?**

To exploit a broken functional level authorization vulnerability to manipulate grades in a student portal API, follow these steps:

1. Identify an endpoint that allows modification of grades, such as PUT /grades/{id}.
2. Use the endpoint to modify the grades of a specific student by changing the grade value.
3. Verify the change by querying the grade information endpoint, such as GET /grades/{id}, to ensure the grade has been updated.

For example, if the grade ID is `13` and the student ID is `3`, you could construct a request like this:

```json
PUT /grades/13 HTTP/1.1
Host: target.example.com
Content-Type: application/json

{
    "student_id": 3,
    "grade": 100
}
```

After sending this request, you should verify the grade change by fetching the grade details:

```http
GET /grades/13 HTTP/1.1
Host: target.example.com
```

If the response shows the grade as `100`, the manipulation was successful.

**Q4. What recent real-world examples or CVEs highlight the risks of broken functional level authorization in APIs?**

One notable example is the 2020 breach of the University of California, San Diego (UCSD), where attackers exploited vulnerabilities in the university’s online systems to access and modify student records. Although the specifics were not widely disclosed, it is likely that broken functional level authorization played a role in the breach. Attackers might have manipulated API endpoints to escalate their privileges and gain unauthorized access to sensitive data.

Another example is CVE-2021-3014, which affected the Jenkins CI/CD platform. This vulnerability allowed attackers to bypass authorization checks and execute arbitrary commands on the server. While this particular CVE involved command execution rather than direct API manipulation, it highlights the broader risk of insufficient access control mechanisms in software systems.

**Q5. How can you prevent broken functional level authorization vulnerabilities in API design and implementation?**

To prevent broken functional level authorization vulnerabilities in API design and implementation, consider the following best practices:

1. **Role-Based Access Control (RBAC):** Implement RBAC to ensure that users can only perform actions appropriate to their roles. For example, a regular user should not be able to update another user's role to admin.

2. **Least Privilege Principle:** Ensure that users and services have the minimum set of permissions necessary to perform their tasks. Avoid granting unnecessary privileges that could be exploited.

3. **Input Validation:** Validate all input parameters to ensure they conform to expected values and formats. This can help prevent unauthorized modifications to sensitive fields like role IDs or grade values.

4. **Logging and Monitoring:** Implement comprehensive logging and monitoring to detect and respond to suspicious activities. Logs should capture details of API requests, including user identities and actions performed.

5. **Regular Audits and Penetration Testing:** Conduct regular security audits and penetration testing to identify and remediate vulnerabilities before they can be exploited. Automated tools can help in identifying common issues related to broken functional level authorization.

By adhering to these principles, you can significantly reduce the risk of broken functional level authorization vulnerabilities in your API implementations.

---
<!-- nav -->
[[04-Broken Authentication Demonstration|Broken Authentication Demonstration]] | [[API Security/07-BFLA Issues/02-Broken Authentication Demonstration/00-Overview|Overview]]
