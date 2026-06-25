---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Core Concepts in Linux Users and Permissions

### Introduction to Linux Users and Permissions

In this section, we delve into one of the most fundamental aspects of Linux and other operating systems: users and their permissions. Understanding these concepts is crucial for managing a Linux system effectively, ensuring security, and maintaining proper access control.

### Categories of Users in Linux

There are three primary categories of users in a Linux system:

1. **Root User**
2. **Regular or Standard Users**
3. **Service Users**

#### Root User

The root user, also known as the superuser, is a special type of user with unrestricted access and permissions to the entire system. This user can perform any administrative task and access any file or directory. The root user is essential for system administration but should be used cautiously due to the high level of privilege.

**Why is the root user important?**

The root user is necessary for performing critical system operations such as installing software, modifying system configurations, and managing other users and groups. Without the root user, many administrative tasks would be impossible.

**How does the root user work?**

When logged in as the root user, you have full control over the system. You can execute any command, modify any file, and change any configuration. However, this level of access comes with significant risks. Any mistake made while logged in as root can potentially damage the system or compromise security.

**Example of using the root user:**

To perform an administrative task, you might need to switch to the root user using the `su` command:

```sh
$ su -
Password:
```

After entering the root password, you will be logged in as the root user.

**Real-world example:**

CVE-2021-4034, also known as "Dirty Pipe," is a vulnerability that allows a non-root user to escalate privileges to root. This highlights the importance of securing the root account and limiting its usage to avoid potential exploits.

**How to Prevent / Defend:**

- **Limit root usage:** Avoid logging in as root unless absolutely necessary. Use `sudo` for executing specific commands with elevated privileges.
- **Secure the root password:** Ensure the root password is strong and changed regularly.
- **Audit root activity:** Monitor and log all activities performed by the root user to detect any unauthorized actions.

#### Regular or Standard Users

Regular or standard users are the typical users created to log in to the system. Each user has their own dedicated space, usually located in the `/home` directory, with a folder named after the user.

**Why are regular users important?**

Regular users provide a way to manage individual access to the system. Each user can have their own set of permissions and access levels, ensuring that sensitive operations are restricted to authorized users.

**How do regular users work?**

Each regular user has a unique username and password. Upon logging in, the user gains access to their home directory and any files or directories they have permission to access. Users can perform various tasks within their permissions, such as creating files, running applications, and accessing shared resources.

**Example of creating a regular user:**

To create a new user, you can use the `adduser` command:

```sh
$ sudo adduser john
```

This command will prompt you to enter details such as the user's password, full name, and other information.

**Real-world example:**

In the Equifax data breach of 2017, attackers exploited a vulnerability in the Apache Struts framework to gain access to the system. They then used a regular user account to move laterally through the network, highlighting the importance of properly managing user permissions and access controls.

**How to Prevent / Defend:**

- **Use strong passwords:** Ensure that all user accounts have strong, unique passwords.
- **Implement multi-factor authentication (MFA):** Add an extra layer of security by requiring users to provide additional verification methods.
- **Limit user permissions:** Assign the minimum necessary permissions to each user based on their role and responsibilities.

#### Service Users

Service users are relevant primarily on Linux server distributions. These users are typically created to run specific services such as database servers, web application servers, and other daemons. Service users often have limited permissions and are isolated from regular user accounts.

**Why are service users important?**

Service users help isolate the execution of services from regular user accounts, reducing the risk of privilege escalation and improving overall system security.

**How do service users work?**

Service users are created with specific permissions and are often assigned to run particular services. For example, a MySQL database server might run as a service user named `mysql`. This ensures that the service runs with the least necessary privileges and does not interfere with other user accounts.

**Example of creating a service user:**

To create a service user, you can use the `useradd` command:

```sh
$ sudo useradd -r mysql
```

The `-r` flag indicates that this is a system user, which is appropriate for service users.

**Real-world example:**

In the case of the Heartbleed vulnerability (CVE-2014-0160), attackers could exploit OpenSSL to steal sensitive information from memory. By isolating services using service users, the impact of such vulnerabilities can be minimized.

**How to Prevent / Defend:**

- **Isolate service users:** Ensure that each service runs as a dedicated service user with minimal permissions.
- **Monitor service user activity:** Regularly audit the activities of service users to detect any unusual behavior.
- **Update and patch services:** Keep all services up to date with the latest security patches to mitigate known vulnerabilities.

### Managing Users and Groups

In addition to creating users, managing groups is also essential for organizing permissions and access control.

#### Creating and Managing Groups

Groups allow you to assign permissions to a collection of users, making it easier to manage access control.

**Why are groups important?**

Groups simplify the management of permissions by allowing you to assign permissions to a group rather than individual users. This reduces the complexity of managing permissions and ensures consistency across multiple users.

**How do groups work?**

Groups are collections of users that share common permissions. When a user is added to a group, they inherit the permissions associated with that group.

**Example of creating a group:**

To create a new group, you can use the `groupadd` command:

```sh
$ sudo groupadd developers
```

To add a user to a group, you can use the `usermod` command:

```sh
$ sudo usermod -aG developers john
```

**Real-world example:**

In the Capital One data breach of 2019, attackers exploited a misconfigured web application firewall to gain access to the system. Proper management of user groups and permissions could have helped contain the damage.

**How to Prevent / Defend:**

- **Use groups for permission management:** Organize users into groups based on their roles and responsibilities.
- **Regularly review group memberships:** Ensure that users are only members of the groups necessary for their job functions.
- **Audit group permissions:** Regularly review and update group permissions to ensure they remain appropriate and secure.

### File and Directory Permissions

Understanding file and directory permissions is crucial for managing access control on a Linux system.

#### File and Directory Permissions

File and directory permissions determine who can read, write, or execute files and directories.

**Why are file and directory permissions important?**

File and directory permissions control access to system resources, ensuring that only authorized users can perform certain actions. This helps maintain system integrity and security.

**How do file and directory permissions work?**

Permissions are assigned to three categories of users: the owner, the group, and others. Each category can have read (`r`), write (`w`), and execute (`x`) permissions.

**Example of setting file permissions:**

To set permissions for a file, you can use the `chmod` command:

```sh
$ chmod 755 /path/to/file
```

This sets the permissions to `rwxr-xr-x`, meaning the owner has read, write, and execute permissions, while the group and others have read and execute permissions.

**Real-world example:**

In the WannaCry ransomware attack of 2017, attackers exploited a vulnerability in the Windows SMB protocol to spread the malware. Proper management of file and directory permissions could have helped limit the spread of the attack.

**How to Prevent / Defend:**

- **Set appropriate permissions:** Ensure that files and directories have the correct permissions based on their intended use.
- **Regularly review permissions:** Periodically review and update file and directory permissions to ensure they remain secure.
- **Use access control lists (ACLs):** For more granular control, consider using ACLs to define permissions for specific users and groups.

### Conclusion

Understanding and managing users and permissions in Linux is essential for maintaining system security and integrity. By properly configuring users, groups, and file permissions, you can ensure that only authorized users have access to system resources and that sensitive operations are restricted to those with the necessary privileges.

### Practice Labs

For hands-on practice with Linux users and permissions, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises on web application security, including topics related to user management and permissions.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing security testing and management techniques.
- **DVWA (Damn Vulnerable Web Application)**: Another vulnerable web application for learning security concepts and practices.

These labs provide practical experience in managing users and permissions in a controlled environment, helping you apply the concepts learned in this chapter.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/01-Linux & OS Basics/14-Linux Users Permissions And Management/00-Overview|Overview]] | [[02-Introduction to Linux User Management|Introduction to Linux User Management]]
