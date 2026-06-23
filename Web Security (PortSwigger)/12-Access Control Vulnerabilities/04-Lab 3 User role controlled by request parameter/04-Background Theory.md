---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Background Theory

Access control vulnerabilities occur when an application fails to properly restrict access to resources based on the identity and privileges of the user. These vulnerabilities can lead to unauthorized access to sensitive information, modification of critical data, and other severe consequences. One common type of access control vulnerability is when the user role is controlled by a request parameter, which can be manipulated by an attacker to gain elevated privileges.

### What is Access Control?

Access control is a security measure that ensures that users have appropriate levels of access to resources within a system. This includes both physical and digital resources. In the context of web applications, access control typically involves:

- **Authentication**: Verifying the identity of a user.
- **Authorization**: Determining what actions a user is allowed to perform based on their identity and role.

### Why is Access Control Important?

Access control is crucial because it helps prevent unauthorized access to sensitive data and functionalities. Without proper access control, an attacker could potentially:

- Gain access to confidential information.
- Modify critical data.
- Execute unauthorized actions within the application.

### How Does Access Control Work?

In a typical web application, access control is implemented through a combination of authentication mechanisms (such as username/password, tokens, etc.) and authorization rules (such as roles and permissions).

#### Authentication Mechanisms

- **Username/Password**: Users provide a username and password to authenticate themselves.
- **Tokens**: Applications often use tokens (like JWTs) to authenticate users across different requests.
- **OAuth**: A protocol for authorization and authentication that allows third-party services to access resources on behalf of a user.

#### Authorization Rules

- **Roles**: Users are assigned roles (e.g., admin, user, guest) that determine their level of access.
- **Permissions**: Specific actions that a user is allowed to perform based on their role.

### Real-World Example: CVE-2021-21972

CVE-2021-21972 is a vulnerability in the WordPress REST API where an attacker could manipulate the `context` parameter to bypass access controls and retrieve sensitive data. This demonstrates how a seemingly innocuous parameter can be exploited to gain unauthorized access.

---
<!-- nav -->
[[Web Security (PortSwigger)/12-Access Control Vulnerabilities/04-Lab 3 User role controlled by request parameter/03-Access Control Vulnerabilities|Access Control Vulnerabilities]] | [[Web Security (PortSwigger)/12-Access Control Vulnerabilities/04-Lab 3 User role controlled by request parameter/00-Overview|Overview]] | [[05-Lab Setup User Role Controlled by Request Parameter|Lab Setup User Role Controlled by Request Parameter]]
