---
course: API Security
topic: Broken Object Level Authorization issues
tags: [api-security]
---

## Practice Questions & Answers

**Q1. Explain what Broken Object Level Authorization (BOLA) is and provide an example from the lecture.**

Broken Object Level Authorization (BOLA) occurs when an application fails to properly restrict access to resources based on the authenticated user's permissions. In the lecture, the demonstration showed accessing user data through the `dump user DB` endpoint without proper authorization. The endpoint returned sensitive information like usernames and admin status without verifying the user's permission to view such data.

**Q2. How can you identify potential BOLA vulnerabilities in an API?**

To identify potential BOLA vulnerabilities, you should:

1. **Review Endpoints**: Look for endpoints that return sensitive data or perform critical actions.
2. **Check Authentication Mechanisms**: Ensure that the authentication mechanism (like JWT tokens) is correctly implemented and validated.
3. **Test Access Controls**: Test whether unauthorized users can access data or perform actions intended for specific roles.
4. **Inspect Headers and Bodies**: Check if sensitive information is being passed in headers or request bodies without proper validation.

For example, in the lecture, the `dump user DB` endpoint was accessible without proper authorization, indicating a BOLA vulnerability.

**Q3. How would you exploit a BOLA vulnerability in an API?**

To exploit a BOLA vulnerability, follow these steps:

1. **Identify Sensitive Endpoints**: Find endpoints that return sensitive data or perform critical actions.
2. **Obtain Authentication Tokens**: Acquire valid authentication tokens, possibly by logging in with known credentials.
3. **Access Unauthorized Data**: Use the obtained tokens to access data or perform actions that should be restricted.

For instance, in the lecture, the `dump user DB` endpoint could be accessed with a valid token to retrieve sensitive user information.

**Q4. How would you fix a BOLA vulnerability in an API?**

To fix a BOLA vulnerability, ensure that:

1. **Proper Authorization Checks**: Implement checks to verify that the authenticated user has the necessary permissions to access specific resources.
2. **Role-Based Access Control (RBAC)**: Use RBAC to restrict access based on user roles.
3. **Audit Logs**: Maintain audit logs to track who accessed what data and when.

For example, in the `dump user DB` endpoint, you should add logic to check if the authenticated user has the permission to view the database contents.

**Q5. Reference a recent real-world example of a BOLA vulnerability and explain how it was exploited.**

A notable example is the **CVE-2021-21972** vulnerability in Microsoft Exchange Server. This vulnerability allowed attackers to bypass authorization controls and gain unauthorized access to sensitive data. Attackers exploited this by sending specially crafted requests to the server, which allowed them to access and modify data without proper authorization.

In this case, the lack of proper authorization checks led to a BOLA vulnerability, allowing unauthorized access to sensitive information.

**Q6. How can you test for BOLA vulnerabilities using automated tools?**

Automated tools like **OWASP ZAP**, **Burp Suite**, and **Nessus** can help identify BOLA vulnerabilities:

1. **OWASP ZAP**: Use ZAP to scan the API and identify endpoints that might be vulnerable to BOLA. ZAP can detect if sensitive data is being returned without proper authorization.
2. **Burp Suite**: Burp Suite can be used to intercept and modify requests to test if unauthorized access is possible. You can use the Intruder tool to automate testing of different user roles and permissions.
3. **Nessus**: Nessus can be configured to scan for common vulnerabilities, including BOLA, by checking for misconfigured access controls and unauthorized data exposure.

By leveraging these tools, you can systematically test for BOLA vulnerabilities and ensure that your API is secure.

---
<!-- nav -->
[[API Security/06-Broken Object Level Authorization issues/04-BOLA Demonstration/02-Introduction to Broken Object-Level Authorization (BOLA)|Introduction to Broken Object-Level Authorization (BOLA)]] | [[API Security/06-Broken Object Level Authorization issues/04-BOLA Demonstration/00-Overview|Overview]]
