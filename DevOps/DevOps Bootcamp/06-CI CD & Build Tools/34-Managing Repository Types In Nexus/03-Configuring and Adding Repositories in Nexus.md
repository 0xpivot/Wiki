---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Configuring and Adding Repositories in Nexus

### Repository Types

Nexus supports several types of repositories, each with its own characteristics:

1. **Proxy Repositories**: Act as a cache for remote repositories. They fetch artifacts from remote sources and store them locally for faster access.
2. **Hosted Repositories**: Store artifacts generated within your organization. These repositories are typically used for internal builds and deployments.
3. **Group Repositories**: Combine multiple repositories into a single logical unit. This allows developers to access multiple repositories through a single URL.

### Configuring Repositories

To configure repositories in Nexus, follow these steps:

1. **Log in to Nexus**: Access the Nexus Repository Manager interface.
2. **Navigate to Repositories**: Go to the "Repositories" section.
3. **Create a New Repository**:
    - Click on "Add repository".
    - Select the type of repository (e.g., Maven proxy, Maven hosted).
    - Configure the settings for the repository, such as the name, remote URL (for proxy repositories), and storage location.

Here is an example of creating a Maven proxy repository:

```mermaid
sequenceDiagram
    participant User
    participant Nexus
    User->>Nexus: Log in to Nexus
    Nexus-->>User: Welcome to Nexus
    User->>Nexus: Navigate to Repositories
    Nexus-->>User: Repositories page loaded
    User->>Nexus: Add repository
    Nexus-->>User: Select repository type
    User->>Nexus: Choose Maven proxy
    Nexus-->>User: Configure settings
    User->>Nexus: Enter repository name
    User->>Nexus: Enter remote URL
    User->>Nexus: Save repository
```

### Creating a Group Repository

A group repository combines multiple repositories into a single logical unit. Here’s how to create one:

1. **Log in to Nexus**.
2. **Navigate to Repositories**.
3. **Add a new repository**.
4. **Select Group**.
5. **Configure the group repository**:
    - Enter a name for the group.
    - Add the repositories you want to include in the group.
    - Set the order of the repositories (this determines the priority when resolving artifacts).

Here is an example of creating a group repository:

```mermaid
sequenceDiagram
    participant User
    participant Nexus
    User->>Nexus: Log in to Nexus
    Nexus-->>User: Welcome to Nexus
    User->>Nexus: Navigate to Repositories
    Nexus-->>User: Repositories page loaded
    User->>Nexus: Add repository
    Nexus-->>User: Select repository type
    User->>Nexus: Choose Group
    Nexus-->>User: Configure settings
    User->>Nexus: Enter group name
    User->>Nexus: Add repositories to group
    User->>N
```

### Full Example of Creating a Group Repository

Let's walk through a complete example of creating a group repository that includes a Maven proxy repository and a Maven hosted repository.

#### Step 1: Create a Maven Proxy Repository

1. **Log in to Nexus**.
2. **Navigate to Repositories**.
3. **Add a new repository**.
4. **Select Maven proxy**.
5. **Configure the settings**:
    - Name: `maven-proxy`
    - Remote URL: `https://repo.maven.apache.org/maven2/`
    - Save the repository.

#### Step 2: Create a Maven Hosted Repository

1. **Log in to Nexus**.
2. **Navigate to Repositories**.
3. **Add a new repository**.
4. **Select Maven hosted**.
5. **Configure the settings**:
    - Name: `maven-hosted`
    - Save the repository.

#### Step 3: Create a Group Repository

1. **Log in to Nexus**.
2. **Navigate to Repositories**.
3. **Add a new repository**.
4. **Select Group**.
5. **Configure the settings**:
    - Name: `maven-group`
    - Add repositories: `maven-proxy`, `maven-hosted`
    - Set the order of the repositories (e.g., `maven-proxy` first, then `maven-hosted`).
    - Save the repository.

### Full HTTP Request and Response Example

When a developer accesses the group repository, the request and response look like this:

#### HTTP Request

```http
GET /nexus/content/groups/maven-group/com/example/library/1.0/library-1.0.jar HTTP/1.1
Host: nexus.example.com
Accept: application/json
Authorization: Basic dXNlcm5hbWU6cGFzc3dvcmQ=
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Mon, 01 Jan 2024 12:00:00 GMT
Content-Type: application/octet-stream
Content-Length: 12345
Last-Modified: Fri, 30 Dec 2023 12:00:00 GMT

[Binary data]
```

### How to Prevent / Defend

#### Detection

To ensure the integrity and security of your Nexus repositories, you should:

1. **Monitor Access Logs**: Regularly review access logs to detect unauthorized access attempts.
2. **Use Auditing Tools**: Implement auditing tools to track changes and access patterns.
3. **Set Up Alerts**: Configure alerts for suspicious activities, such as repeated failed login attempts.

#### Prevention

1. **Secure Authentication**: Ensure that all access to Nexus is authenticated using strong credentials.
2. **Role-Based Access Control (RBAC)**: Implement RBAC to restrict access based on user roles.
3. **Regular Updates**: Keep Nexus and all plugins up to date to protect against vulnerabilities.

#### Secure Coding Fixes

Here is an example of a vulnerable configuration and a secure configuration:

##### Vulnerable Configuration

```json
{
  "name": "maven-proxy",
  "type": "proxy",
  "remoteUrl": "https://repo.maven.apache.org/maven2/",
  "authentication": {
    "type": "none"
  }
}
```

##### Secure Configuration

```json
{
  "name": "maven-proxy",
  "type": "proxy",
  "remoteUrl": "https://repo.maven.apache.org/maven2/",
  "authentication": {
    "type": "basic",
    "username": "secure-user",
    "password": "secure-password"
  }
}
```

### Real-World Examples

#### Recent CVEs and Breaches

One notable breach involving repository managers was the **CVE-2021-21296**, which affected Nexus Repository Manager 3. This vulnerability allowed attackers to execute arbitrary code on the server. To mitigate such risks, it is crucial to keep Nexus updated and apply security patches promptly.

### Hands-On Labs

For practical experience with managing repositories in Nexus, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive course on web security, including sections on managing repositories.
- **OWASP Juice Shop**: A deliberately insecure web application for security training, which can be used to practice securing repositories.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for security training, useful for practicing repository management.

These labs provide real-world scenarios and challenges to help you master the skills needed to effectively manage repositories in Nexus.

### Conclusion

Managing repositories in Nexus is a critical aspect of DevOps workflows. By configuring and grouping repositories, you can simplify access for developers and improve overall performance. Understanding the different types of repositories and how to secure them is essential for maintaining a robust and secure environment.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/34-Managing Repository Types In Nexus/02-Introduction to Nexus Repository Manager|Introduction to Nexus Repository Manager]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/34-Managing Repository Types In Nexus/00-Overview|Overview]] | [[04-Managing Repository Types in Nexus|Managing Repository Types in Nexus]]
