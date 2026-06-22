---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Logging In and Switching Users in Linux

In Linux, managing users and permissions is a fundamental aspect of system administration. This section covers how to log in as different users, switch between users, and manage user groups.

### Logging In as a Different User

To log in as a different user, you can use the `su` (substitute user) command. This command allows you to switch to another user account, either temporarily or permanently, depending on your needs.

#### Syntax and Usage

The basic syntax for the `su` command is:

```sh
su [options] [username]
```

If you do not specify a username, `su` defaults to logging in as the `root` user, which is the superuser with full administrative privileges.

#### Example: Switching to Another User

Let's say you want to switch from the current user to the `Tom` user. You would use the following command:

```sh
su - Tom
```

Here, the `-` option tells `su` to start a login shell for the specified user, meaning it will set up the environment as if the user had logged in directly.

#### Example: Switching to Root User

To switch to the root user, you would simply run:

```sh
su -
```

This will prompt you for the root user's password. Once authenticated, you will be logged in as the root user.

### Switching Back to Original User

After performing tasks as another user, you might want to switch back to your original user. This can be done by simply typing `exit` in the terminal:

```sh
exit
```

This command logs you out of the current user session and returns you to the previous user session.

### Creating and Managing Groups

Groups in Linux are used to organize users and manage permissions collectively. Instead of assigning permissions to individual users, you can assign them to a group, making management more efficient.

#### Creating a Group

To create a new group, you can use the `groupadd` command. Here’s an example of creating a group named `DevOps`:

```sh
sudo groupadd DevOps
```

This command creates a new group named `DevOps`. Note that you need to have administrative privileges to execute this command, hence the use of `sudo`.

#### Verifying Group Creation

To verify that the group has been created successfully, you can check the `/etc/group` file, which contains the list of all groups on the system:

```sh
cat /etc/group
```

You should see an entry for the `DevOps` group at the end of the output, similar to this:

```
DevOps:x:1001:
```

Here, `1001` is the group ID assigned to the `DevOps` group.

### Adding Users to Groups

Once a group is created, you can add users to it using the `usermod` command. For example, to add the user `Tom` to the `DevOps` group, you would run:

```sh
sudo usermod -aG DevOps Tom
```

The `-aG` options tell `usermod` to append the user to the specified group(s).

### Managing User Accounts

Creating and managing user accounts is another critical task in Linux system administration.

#### Creating a New User

To create a new user, you can use the `useradd` command. For example, to create a new user named `Alice`, you would run:

```sh
sudo useradd Alice
```

By default, this command creates a user with a home directory and a default shell. To set a password for the new user, you would use the `passwd` command:

```sh
sudo passwd Alice
```

This will prompt you to enter and confirm a password for the `Alice` user.

### Secure Coding Practices

When managing users and groups, it is crucial to follow secure coding practices to prevent unauthorized access and ensure system integrity.

#### Avoiding Hardcoded Passwords

Never hardcode passwords in scripts or configurations. Always use secure methods to handle authentication, such as using environment variables or secure vaults.

#### Example: Vulnerable Code

Consider the following insecure script that hardcodes a password:

```sh
#!/bin/sh
echo "password123" | sudo -S su -
```

This script is highly insecure because it exposes the root password in plain text.

#### Secure Code Fix

A secure alternative would be to use `sudo` with proper permissions configured in the `/etc/sudoers` file, ensuring that the user has the necessary privileges without exposing the password:

```sh
#!/bin/sh
sudo su -
```

Ensure that the user has the appropriate `sudo` permissions configured in `/etc/sudoers`:

```sh
Alice ALL=(ALL) NOPASSWD: /bin/su -
```

### Real-World Examples and CVEs

#### CVE-2021-44228 (Log4Shell)

The Log4Shell vulnerability (CVE-2021-44228) affected many systems due to improper handling of user input. This highlights the importance of secure coding practices and the need to validate and sanitize user inputs.

#### Example: Secure Input Handling

To prevent such vulnerabilities, always validate and sanitize user inputs. For example, when creating a new user, ensure that the username does not contain malicious characters:

```sh
#!/bin/sh
# Validate username
if ! echo "$1" | grep -qE '^[a-zA-Z0-9_-]+$'; then
    echo "Invalid username"
    exit 1
fi

# Create user
sudo useradd "$1"
```

### How to Prevent / Defend

#### Detection

Regularly audit user accounts and permissions using tools like `lastlog` and `who`.

```sh
lastlog
```

#### Prevention

1. **Use Strong Password Policies**: Enforce strong password policies using `pam_cracklib` or `pam_pwquality`.
   
   ```sh
   sudo authconfig --enablecracklib --cracklib-dict=/usr/share/cracklib/pw_dict --update
   ```

2. **Limit Sudo Privileges**: Configure `/etc/sudoers` to limit sudo privileges to specific commands and users.

   ```sh
   Alice ALL=(ALL) NOPASSWD: /bin/useradd, /bin/passwd
   ```

3. **Audit Logs**: Enable auditing to track user activities.

   ```sh
   sudo auditctl -w /etc/passwd -p wa -k passwd_changes
   ```

### Hands-On Labs

For practical experience in managing users and permissions, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

These labs provide a safe environment to practice and learn about user management and security in Linux systems.

### Conclusion

Managing users and permissions in Linux is a critical aspect of system administration. By understanding how to log in as different users, switch between users, and manage groups, you can effectively control access and permissions on your system. Following secure coding practices and regularly auditing user accounts and permissions can help prevent unauthorized access and ensure system integrity.

---
<!-- nav -->
[[07-Linux Users Permissions and Management|Linux Users Permissions and Management]] | [[DevOps/DevOps Bootcamp/01-Linux & OS Basics/14-Linux Users Permissions And Management/00-Overview|Overview]] | [[09-User Management in Linux|User Management in Linux]]
