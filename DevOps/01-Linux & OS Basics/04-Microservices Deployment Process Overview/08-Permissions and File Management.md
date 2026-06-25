---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Permissions and File Management

### Understanding File Permissions

In Unix-based systems, file permissions determine who can access a file and what kind of access they have. There are three types of permissions:

1. **Read (r)**: Allows viewing the contents of a file.
2. **Write (w)**: Allows modifying the contents of a file.
3. **Execute (x)**: Allows executing the file as a program.

These permissions can be set for three categories of users:

1. **Owner**: The user who owns the file.
2. **Group**: Users who belong to the same group as the file.
3. **Others**: All other users on the system.

#### Setting File Permissions

To set file permissions, you can use the `chmod` command. For example, to give the owner read and write permissions, you would use:

```bash
chmod 600 filename
```

Here, `600` means:
- `6` for the owner (read + write)
- `0` for the group (no permissions)
- `0` for others (no permissions)

Alternatively, you can use symbolic notation:

```bash
chmod u=rw,g=,o= filename
```

This sets the owner to have read and write permissions (`rw`), the group to have no permissions (`=`), and others to have no permissions (`=`).

### Example: Setting Permissions for a Configuration File

Suppose you have a configuration file named `config.yaml` located in the `/downloads` directory. You want to ensure that only the owner can read and write to this file, while others have no permissions.

First, navigate to the directory containing the file:

```bash
cd /downloads
```

Then, set the appropriate permissions:

```bash
chmod 600 config.yaml
```

To verify the permissions, use the `ls -l` command:

```bash
ls -l config.yaml
```

The output should look like this:

```
-rw------- 1 username groupname date time config.yaml
```

Here, `-rw-------` indicates that the owner has read and write permissions, while the group and others have no permissions.

### Pitfalls and Best Practices

1. **Overly Permissive Permissions**: Avoid setting overly permissive permissions, such as `777`, which allows everyone to read, write, and execute the file. This can lead to security vulnerabilities.
2. **Regular Audits**: Regularly audit file permissions to ensure they align with your security policies. Tools like `find` can help identify files with specific permissions:

    ```bash
    find /path/to/directory -type f -perm 600
    ```

3. **Secure Coding Practices**: Always validate and sanitize input when handling files. Ensure that sensitive data is stored securely and that permissions are set appropriately.

### How to Prevent / Defend

1. **Use Least Privilege Principle**: Set permissions based on the principle of least privilege. Only grant the minimum necessary permissions required for a task.
2. **Audit and Monitor**: Regularly audit file permissions and monitor for unauthorized changes using tools like `auditd`.
3. **Automate Permission Management**: Use automation tools like Ansible or Puppet to manage file permissions consistently across your environment.

---
<!-- nav -->
[[08-Namespace Management in Microservices|Namespace Management in Microservices]] | [[DevOps/DevOps Bootcamp/01-Linux & OS Basics/04-Microservices Deployment Process Overview/00-Overview|Overview]] | [[10-Service Ports in Microservices|Service Ports in Microservices]]
