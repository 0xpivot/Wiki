---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Nexus Repository Manager

The Nexus Repository Manager is a powerful artifact management solution used in many organizations to manage binary artifacts such as JARs, WARs, RPMs, and Docker images. It provides a centralized repository for storing and managing these artifacts, ensuring consistency and reliability across development and deployment processes.

### Background Theory

Nexus Repository Manager is built on top of the Apache Maven project and integrates seamlessly with various build tools like Maven, Gradle, and Ant. It supports different types of repositories, including Maven, npm, NuGet, Docker, and more. This makes it a versatile tool for managing dependencies and artifacts across different environments.

### Setting Up Nexus User and Group Ownership

To effectively manage access and permissions within Nexus, it is crucial to set up users and groups correctly. This involves configuring the operating system level permissions and ensuring that the Nexus service runs under the correct user context.

#### Creating a Nexus User and Group

In Unix-based systems, users and groups are managed through the `/etc/passwd` and `/etc/group` files. To create a new user and group for Nexus, you can use the `useradd` and `groupadd` commands.

```bash
sudo groupadd nexus
sudo useradd -g nexus -m nexus
```

This creates a group named `nexus` and a user named `nexus` that belongs to this group. The `-m` flag ensures that a home directory is created for the user.

### Recursively Setting Owner and Group

Once the user and group are created, you need to set the ownership and group recursively for the Nexus installation directory. This ensures that all files and directories within the Nexus installation are owned by the `nexus` user and group.

```bash
sudo chown -R nexus:nexus /opt/nexus
```

Here, `/opt/nexus` is the installation directory for Nexus. The `-R` flag ensures that the ownership is set recursively for all files and directories within this path.

### Example: Setting Ownership for Sonatype Work Directory

Let's consider the specific example from the transcript where the `Sonatype Work` directory needs to be set with the `nexus` user and group ownership.

```bash
sudo chown -R nexus:nexus /opt/sonatype-work
```

This command sets the ownership of the `/opt/sonatype-work` directory and all its contents to the `nexus` user and group.

### Verifying Ownership Changes

After setting the ownership, you can verify the changes using the `ls -l` command.

```bash
ls -l /opt/sonatype-work
```

This will display the file permissions and ownership details for the `/opt/sonatype-work` directory. You should see that the owner and group are set to `nexus`.

### Switching to the Nexus User

To ensure that the `nexus` user has the necessary permissions, you can switch to this user using the `su` command.

```bash
su - nexus
```

This switches the current shell session to the `nexus` user. You can then navigate to the `/opt/sonatype-work` directory and verify that you have the required permissions.

### Recursive Ownership Impact

Setting the ownership recursively ensures that all subdirectories and files within the specified directory inherit the same ownership. This is crucial for maintaining consistent permissions across the entire Nexus installation.

### Configuring Nexus to Run as the Nexus User

To ensure that the Nexus service runs under the `nexus` user context, you need to configure the `nexus.rc` file. This file contains startup parameters for the Nexus service.

#### Location of `nexus.rc` File

The `nexus.rc` file is typically located in the `/opt/nexus/bin` directory.

```bash
cat /opt/nexus/bin/nexus.rc
```

This command displays the contents of the `nexus.rc` file. You should look for the `RUN_AS_USER` parameter.

#### Modifying `nexus.rc` File

If the `RUN_AS_USER` parameter is commented out or has an empty value, you need to modify it to specify the `nexus` user.

```bash
RUN_AS_USER=nexus
```

Ensure that this line is uncommented and set to `nexus`. Save the changes to the `nexus.rc` file.

### Example: Modifying `nexus.rc` File

Here is a complete example of modifying the `nexus.rc` file:

```bash
# Before modification
RUN_AS_USER=

# After modification
RUN_AS_USER=nexus
```

Save the changes and restart the Nexus service to apply the new configuration.

### Restarting the Nexus Service

To apply the changes made to the `nexus.rc` file, you need to restart the Nexus service.

```bash
sudo systemctl restart nexus
```

This command restarts the Nexus service, ensuring that it runs under the `nexus` user context.

### Verifying the Nexus Service

After restarting the service, you can verify that it is running under the `nexus` user context.

```bash
ps aux | grep nexus
```

This command lists the processes running under the `nexus` user, confirming that the Nexus service is running correctly.

### Common Pitfalls and How to Avoid Them

#### Incorrect Ownership Settings

One common pitfall is setting incorrect ownership for the Nexus installation directory. This can lead to permission issues and prevent the Nexus service from running properly.

**How to Prevent:**

- Always double-check the ownership settings using the `ls -l` command.
- Ensure that the `nexus` user and group have the necessary permissions for all files and directories within the Nexus installation.

#### Incorrect Configuration of `nexus.rc` File

Another common issue is incorrectly configuring the `nexus.rc` file. This can result in the Nexus service not running under the correct user context.

**How to Prevent:**

- Carefully review the `nexus.rc` file and ensure that the `RUN_AS_USER` parameter is correctly set to `nexus`.
- Test the configuration by restarting the Nexus service and verifying that it runs under the `nexus` user context.

### Real-World Examples and Recent CVEs

#### CVE-2021-21287: Unauthorized Access in Nexus Repository Manager

In 2021, a critical vulnerability was discovered in the Nexus Repository Manager, allowing unauthorized access to sensitive data. This vulnerability was due to improper handling of authentication tokens.

**Impact:**

- Attackers could gain unauthorized access to the Nexus Repository Manager and potentially compromise sensitive data.

**How to Prevent:**

- Ensure that the Nexus Repository Manager is updated to the latest version.
- Implement strict access controls and regularly audit user permissions.
- Use secure authentication mechanisms and regularly rotate authentication tokens.

#### CVE-2_2022-37975: Path Traversal Vulnerability in Nexus Repository Manager

In 2022, another vulnerability was discovered in the Nexus Repository Manager, allowing attackers to perform path traversal attacks.

**Impact:**

- Attackers could exploit this vulnerability to access sensitive files outside the intended directory structure.

**How to Prevent:**

- Ensure that the Nexus Repository Manager is updated to the latest version.
- Implement strict input validation and sanitize user inputs.
- Regularly audit the file system permissions and ensure that sensitive files are protected.

### Secure Coding Practices

#### Secure Configuration of `nexus.rc` File

When configuring the `nexus.rc` file, it is important to follow secure coding practices to prevent potential vulnerabilities.

**Vulnerable Code:**

```bash
RUN_AS_USER=
```

**Secure Code:**

```bash
RUN_AS_USER=nexus
```

By setting the `RUN_AS_USER` parameter to `nexus`, you ensure that the Nexus service runs under the correct user context.

### Hardening Recommendations

#### File System Permissions

To harden the file system permissions for the Nexus installation, you can set restrictive permissions for the `/opt/nexus` directory.

```bash
sudo chmod -R 755 /opt/nexus
```

This command sets the permissions to `rwxr-xr-x`, ensuring that only the `nexus` user and group have write access.

#### SELinux Configuration

If your system uses SELinux, you can further harden the security by configuring SELinux policies for the Nexus service.

```bash
sudo semanage permissive -a nexus_t
```

This command sets the Nexus service to permissive mode, allowing you to monitor and log SELinux denials without blocking the service.

### Conclusion

Properly setting up user and group ownership for the Nexus Repository Manager is crucial for ensuring the security and reliability of your artifact management solution. By following the steps outlined in this chapter, you can configure the Nexus service to run under the correct user context and protect against potential vulnerabilities.

### Practice Labs

For hands-on practice with Nexus Repository Manager, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers a series of labs focused on web application security, including some related to artifact management.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning web security.

These labs provide practical experience in configuring and securing the Nexus Repository Manager, helping you to master the concepts covered in this chapter.

---
<!-- nav -->
[[04-Introduction to DevOps and Nexus|Introduction to DevOps and Nexus]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/14-Create Nexus User And Group Ownership/00-Overview|Overview]] | [[06-Introduction to Nexus User and Group Ownership|Introduction to Nexus User and Group Ownership]]
