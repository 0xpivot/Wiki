---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the main components of the Nexus UI and their functions.**

Nexus UI is organized into several key components:

- **Repositories**: This is the central part where you manage different types of repositories such as Maven, npm, Docker, etc. Each repository type supports specific package formats and allows you to store and manage artifacts.

- **Security**: Here you handle user management, including creating new users, assigning roles and permissions, and integrating with LDAP or Active Directory for centralized authentication and authorization.

- **Blob Stores**: Blob stores are the physical storage locations for the artifacts within Nexus. They allow you to manage storage space and perform operations like backups and restores.

- **Cleanup Policies**: Cleanup policies help automate the removal of old or unused artifacts from repositories to prevent the system from becoming cluttered and inefficient.

**Q2. How would you configure a new repository in Nexus?**

To configure a new repository in Nexus, follow these steps:

1. Log in to the Nexus UI with administrative privileges.
2. Navigate to the "Repositories" section under the "Server" tab.
3. Click on "Create repository".
4. Select the type of repository you want to create (e.g., Maven, Docker, npm).
5. Fill in the required details such as repository name, format, and storage configuration.
6. Configure additional settings like remote URLs if you need to proxy external repositories.
7. Save the repository configuration.

For example, to create a Maven hosted repository:

```plaintext
Name: my-maven-repo
Format: maven2
Storage: Default Storage
```

**Q3. Why is it important to set up cleanup policies in Nexus?**

Cleanup policies are crucial for maintaining the efficiency and performance of Nexus. Over time, repositories can accumulate numerous artifacts, including outdated versions and duplicates. Without proper cleanup, this can lead to:

- Increased storage usage.
- Slower performance due to the overhead of managing large numbers of artifacts.
- Potential issues with disk space and backup processes.

By setting up automated cleanup policies, you can ensure that only necessary artifacts remain in the repository, improving overall system performance and reducing maintenance overhead.

**Q4. How can you integrate LDAP with Nexus for user management?**

Integrating LDAP with Nexus involves configuring the LDAP settings to authenticate and authorize users against an existing LDAP directory. Here’s how you can do it:

1. Log in to Nexus with administrative privileges.
2. Go to the "Security" section under the "System" tab.
3. Click on "LDAP Configuration".
4. Enter the LDAP server details such as the server URL, base DN, and bind credentials.
5. Define the user and group search filters.
6. Map LDAP attributes to Nexus roles and permissions.
7. Test the LDAP connection to ensure it is configured correctly.
8. Save the configuration.

For example, to configure LDAP:

```plaintext
LDAP Server URL: ldap://ldap.example.com:389
Base DN: dc=example,dc=com
Bind DN: cn=admin,dc=example,dc=com
Bind Password: your-bind-password
User Search Base: ou=users,dc=example,dc=com
Group Search Base: ou=groups,dc=example,dc=com
```

**Q5. What are blob stores in Nexus and how do they function?**

Blob stores in Nexus are the underlying storage mechanisms used to store artifacts. They function as follows:

- **Storage Location**: Blob stores define where the actual artifact data is stored on disk.
- **Management**: You can manage blob stores to control storage allocation, perform backups, and restore data.
- **Configuration**: Blob stores can be configured to use different storage strategies, such as on-disk or cloud-based storage solutions.

For example, to create a new blob store:

1. Log in to Nexus with administrative privileges.
2. Go to the "Blob Stores" section under the "Server" tab.
3. Click on "Create blob store".
4. Choose the type of blob store (e.g., file, S3).
5. Configure the storage location and any additional settings.
6. Save the blob store configuration.

**Q6. Describe the process of creating a cleanup policy in Nexus.**

Creating a cleanup policy in Nexus involves defining rules for removing artifacts that meet certain criteria. Here’s how you can create a cleanup policy:

1. Log in to Nexus with administrative privileges.
2. Go to the "Cleanup Policies" section under the "Server" tab.
3. Click on "Create cleanup policy".
4. Name the policy and select the repository it will apply to.
5. Define the criteria for the cleanup policy, such as removing artifacts older than a certain date or those that haven’t been accessed in a specified period.
6. Schedule the policy to run at regular intervals (e.g., daily, weekly).
7. Save the cleanup policy.

For example, to create a cleanup policy:

```plaintext
Policy Name: Old Artifacts Cleanup
Repository: my-maven-repo
Criteria: Remove artifacts older than 30 days
Schedule: Run every Sunday at midnight
```

**Q7. How does Nexus handle user permissions and roles?**

In Nexus, user permissions and roles are managed through the Security section:

- **Roles**: Roles define a set of permissions that can be assigned to users or groups. For example, a "Developer" role might have read-only access to repositories, while an "Admin" role might have full access.
- **Permissions**: Permissions specify what actions a user or role can perform, such as deploying artifacts, managing repositories, or accessing the UI.
- **User Management**: Users can be created and assigned roles directly in Nexus or integrated via LDAP/AD for centralized management.

For example, to assign a role to a user:

1. Log in to Nexus with administrative privileges.
2. Go to the "Users" section under the "Security" tab.
3. Create or edit a user.
4. Assign roles to the user.
5. Save the user configuration.

**Q8. What recent real-world examples demonstrate the importance of proper Nexus administration?**

Recent breaches and vulnerabilities highlight the importance of proper Nexus administration:

- **CVE-2021-2109** involved a vulnerability in Nexus Repository Manager that allowed unauthorized access to sensitive data. Proper configuration of security settings and timely updates could mitigate such risks.
- **Data Leaks**: Inadequate cleanup policies and improper user management led to data leaks in several organizations. Regularly applying cleanup policies and ensuring strict access controls can prevent such incidents.

These examples underscore the need for robust administration practices to secure and maintain Nexus effectively.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/04-Nexus UI Tour And Administration Basics/01-Introduction to Nexus Repository Manager|Introduction to Nexus Repository Manager]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/04-Nexus UI Tour And Administration Basics/00-Overview|Overview]]
