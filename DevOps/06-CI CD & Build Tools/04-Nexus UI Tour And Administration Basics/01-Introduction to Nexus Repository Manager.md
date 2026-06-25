---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Nexus Repository Manager

The Nexus Repository Manager is a powerful tool used in DevOps environments to manage artifacts such as libraries, binaries, and dependencies. It provides a centralized repository management system that helps teams efficiently store, retrieve, and manage their software components. In this chapter, we will delve deep into the Nexus UI, covering its main concepts, administration basics, and security features.

### Main Concepts in Nexus UI

Upon deploying Nexus, you will be greeted with a welcome page that lists all supported repository formats. These formats include Maven, npm, NuGet, Docker, and more. The support for these formats is crucial because different development environments and tools require specific artifact types.

#### Supported Repository Formats

Nexus supports a wide range of repository formats, catering to various programming languages and package managers:

- **Maven**: Used for Java projects.
- **npm**: Node Package Manager for JavaScript projects.
- **NuGet**: Used for .NET projects.
- **Docker**: For container images.
- **PyPI**: Python Package Index for Python projects.

These formats ensure that developers can manage their dependencies in a consistent and reliable manner across different ecosystems.

### Default User and Authentication

When you deploy Nexus, a default user is created with administrative privileges. This user is typically named `admin` and comes with a default password. It is essential to change this password immediately after deployment to enhance security.

```mermaid
sequenceDiagram
    participant User
    participant Nexus
    User->>Nexus: Access Nexus UI
    Nexus-->>User: Display Welcome Page
    User->>Nexus: Login with Default Credentials
    Nexus-->>User: Authenticate User
```

#### Changing the Default Password

To change the default password, follow these steps:

1. Log in to Nexus using the default credentials (`admin`/`password`).
2. Navigate to the **Security** section.
3. Click on **Users**.
4. Locate the `admin` user and click on **Edit**.
5. Change the password and save the changes.

```mermaid
flowchart TD
    A[Log in with Default Credentials] --> B[Navigate to Security Section]
    B --> C[Click on Users]
    C --> D[Locate Admin User]
    D --> E[Edit User Profile]
    E --> F[Change Password]
    F --> G[Save Changes]
```

### Creating Additional Users

In a large organization, it is common to have multiple users accessing Nexus. To manage these users effectively, you can create additional accounts with varying levels of access.

#### Creating a New User

To create a new user, follow these steps:

1. Log in to Nexus as an admin.
2. Navigate to the **Security** section.
3. Click on **Users**.
4. Click on **Create User**.
5. Fill in the required details such as username, email, and password.
6. Assign roles and permissions as needed.
7. Save the user.

```mermaid
flowchart TD
    A[Log in as Admin] --> B[Navigate to Security Section]
    B --> C[Click on Users]
    C --> D[Click on Create User]
    D --> E[Fill in User Details]
    E --> F[Assign Roles and Permissions]
    F --> G[Save User]
```

### LDAP Integration

For organizations with many users, integrating Nexus with an LDAP server can streamline user management. LDAP (Lightweight Directory Access Protocol) is a protocol used to maintain distributed directory information services.

#### Configuring LDAP Integration

To configure LDAP integration, follow these steps:

1. Log in to Nexus as an admin.
2. Navigate to the **Security** section.
3. Click on **LDAP Configuration**.
4. Enter the necessary details such as the LDAP server URL, base DN, and bind credentials.
5. Test the connection to ensure it is working correctly.
6. Save the configuration.

```mermaid
flowchart TD
    A[Log in as Admin] --> B[Navigate to Security Section]
    B --> C[Click on LDAP Configuration]
    C --> D[Enter LDAP Server Details]
    D --> E[Test Connection]
    E --> F[Save Configuration]
```

### Repository Management

Repositories are the core concept in Nexus. They are used to store and manage artifacts such as libraries, binaries, and dependencies. There are several types of repositories, including hosted, proxy, and group repositories.

#### Types of Repositories

- **Hosted Repositories**: Used to store internal artifacts.
- **Proxy Repositories**: Used to cache external artifacts.
- **Group Repositories**: Combine multiple repositories into a single view.

#### Creating a Hosted Repository

To create a hosted repository, follow these steps:

1. Log in to Nexus as an admin.
2. Navigate to the **Repository** section.
3. Click on **Create Repository**.
4. Select the type of repository (e.g., Maven hosted).
5. Configure the repository settings such as name, storage location, and component layout.
6. Save the repository.

```mermaid
flowchart TD
    A[Log in as Admin] --> B[Navigate to Repository Section]
    B --> C[Click on Create Repository]
    C --> D[Select Repository Type]
    D --> E[Configure Repository Settings]
    E --> F[Save Repository]
```

### Security Features

Security is paramount in managing repositories. Nexus provides several security features to protect your artifacts and ensure compliance.

#### Role-Based Access Control (RBAC)

RBAC allows you to define roles and assign them to users. Each role can have specific permissions, ensuring that users only have access to the resources they need.

#### Example of RBAC Configuration

To configure RBAC, follow these steps:

1. Log in to Nexus as an admin.
2. Navigate to the **Security** section.
3. Click on **Roles**.
4. Create a new role and assign permissions.
5. Assign the role to a user.

```mermaid
flowchart TD
    A[Log in as Admin] --> B[Navigate to Security Section]
    B --> C[Click on Roles]
    C --> D[Create New Role]
    D --> E[Assign Permissions]
    E --> F[Assign Role to User]
```

### Recent Real-World Examples

Recent breaches and vulnerabilities have highlighted the importance of securing repository managers like Nexus. For instance, the CVE-2021-21277 vulnerability in Nexus Repository Manager allowed unauthorized access to sensitive data.

#### CVE-2021-21277

This vulnerability was due to improper validation of user input, allowing attackers to bypass authentication mechanisms. To mitigate this, ensure that you are using the latest version of Nexus and apply all security patches.

### How to Prevent / Defend

#### Detection

Regularly monitor logs and audit trails to detect any unauthorized access attempts. Use tools like Splunk or ELK Stack to analyze logs and identify suspicious activities.

#### Prevention

- **Use Strong Authentication Mechanisms**: Implement multi-factor authentication (MFA) to enhance security.
- **Limit User Privileges**: Ensure that users only have the minimum necessary privileges.
- **Regularly Update and Patch**: Keep Nexus up-to-date with the latest security patches.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of a configuration file:

**Vulnerable Configuration:**
```yaml
security:
  authentication:
    enabled: true
    method: basic
```

**Secure Configuration:**
```yaml
security:
  authentication:
    enabled: true
    method: multi-factor
```

### Complete Example: Full HTTP Request and Response

Here is a complete example of a full HTTP request and response when creating a new user in Nexus:

**HTTP Request:**
```http
POST /service/rest/v1/security/users HTTP/1.1
Host: nexus.example.com
Authorization: Basic YWRtaW46cGFzc3dvcmQ=
Content-Type: application/json

{
  "userId": "newuser",
  "firstName": "New",
  "lastName": "User",
  "emailAddress": "newuser@example.com",
  "status": "active"
}
```

**HTTP Response:**
```http
HTTP/1.1 201 Created
Date: Mon, 01 Jan 2024 12:00:00 GMT
Content-Type: application/json

{
  "userId": "newuser",
  "firstName": "New",
  "lastName": "User",
  "emailAddress": "newuser@example.com",
  "status": "active"
}
```

### Hands-On Labs

To practice and reinforce your understanding of Nexus UI and administration basics, consider the following labs:

- **PortSwigger Web Security Academy**: Offers hands-on labs for web application security.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another resource for practicing web application security.

By thoroughly understanding and implementing the concepts covered in this chapter, you will be well-equipped to manage and secure your Nexus Repository Manager effectively.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/04-Nexus UI Tour And Administration Basics/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/04-Nexus UI Tour And Administration Basics/02-Practice Questions & Answers|Practice Questions & Answers]]
