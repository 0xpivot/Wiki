---
course: Web Security
topic: Access Control Vulnerabilities
tags: [web-security]
---

## Introduction to Access Control Vulnerabilities

Access control vulnerabilities are among the most critical issues in web application security. They allow unauthorized users to perform actions that should be restricted to specific roles or privileges. One such vulnerability is the exploitation of method-based access control, which can be circumvented through clever manipulation of HTTP methods.

### What is Access Control?

Access control is the mechanism used to ensure that users and systems can only access resources and perform actions that they are authorized to do. It is a fundamental aspect of security that helps prevent unauthorized access and misuse of resources.

### Why is Access Control Important?

Access control is crucial because it helps maintain the integrity and confidentiality of data. Without proper access control, sensitive information could be accessed by unauthorized individuals, leading to data breaches and other security incidents.

### How Does Access Control Work?

Access control typically involves several components:

1. **Authentication**: Verifying the identity of a user.
2. **Authorization**: Determining what actions a user is allowed to perform based on their role or privileges.
3. **Resource Management**: Ensuring that only authorized users can access specific resources.

### Common Access Control Mechanisms

- **Role-Based Access Control (RBAC)**: Users are assigned roles, and roles are granted permissions.
- **Attribute-Based Access Control (ABAC)**: Permissions are determined based on attributes of the user, resource, and environment.
- **Discretionary Access Control (DAC)**: Owners of resources decide who can access them.
- **Mandatory Access Control (MAC)**: Access is controlled by a central authority based on security labels.

### Method-Based Access Control

Method-based access control is a type of access control that relies on the HTTP method (GET, POST, PUT, DELETE, etc.) to determine whether a user is authorized to perform an action. This approach can be vulnerable if the logic for determining authorization is flawed.

---
<!-- nav -->
[[Web Security (PortSwigger)/12-Access Control Vulnerabilities/07-Lab 6 Method based access control can be circumvented/00-Overview|Overview]] | [[02-Access Control Vulnerabilities Method-Based Access Control Can Be Circumvented|Access Control Vulnerabilities Method-Based Access Control Can Be Circumvented]]
