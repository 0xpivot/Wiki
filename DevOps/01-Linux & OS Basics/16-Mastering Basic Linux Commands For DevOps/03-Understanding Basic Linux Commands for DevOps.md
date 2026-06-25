---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Understanding Basic Linux Commands for DevOps

### Introduction to Basic Linux Commands

In the realm of DevOps, proficiency with basic Linux commands is essential. These commands form the backbone of many operations, from managing files and directories to executing scripts and monitoring system performance. This section delves into some fundamental concepts and commands, providing a comprehensive understanding of their usage and importance.

### The Tilde Character (`~`)

The tilde character (`~`) is a special symbol in Linux that represents the home directory of the current user. This shorthand is incredibly useful for navigating and referencing files within your home directory without having to type out the full path.

#### What is the Home Directory?

The home directory is a specific directory in the filesystem that belongs to a particular user. Each user has their own home directory, typically located under `/home/username`. For instance, if your username is `nano`, your home directory would be `/home/nano`.

#### Why Use the Tilde?

Using the tilde simplifies navigation and file management. Instead of typing out the full path to your home directory, you can simply use `~`. This makes commands more concise and easier to remember.

#### Example Usage

To navigate to your home directory using the tilde:

```bash
cd ~
```

This command changes the current working directory to your home directory.

### The Dollar Sign (`$`) and Root User (`#`)

The prompt in a terminal session often includes a dollar sign (`$`) or a pound sign (`#`). These symbols indicate the current user's privileges and provide context about the environment in which commands are being executed.

#### Regular User Prompt (`$`)

When you log in as a regular user, the terminal prompt typically ends with a dollar sign (`$`). This signifies that you are working with standard user permissions, which are limited compared to those of a superuser (root).

#### Superuser Prompt (`#`)

If you log in as the root user or switch to root using commands like `sudo` or `su`, the prompt changes to a pound sign (`#`). This indicates that you have elevated privileges and can perform administrative tasks that require higher permissions.

#### Importance of Different Prompts

Different prompts help avoid confusion, especially when working on multiple machines simultaneously. By visually distinguishing between regular and root user sessions, you can ensure that you are executing commands with the appropriate level of privilege.

#### Example Usage

Here’s an example of switching to the root user and back to a regular user:

```bash
# Switch to root user
sudo su

# Now the prompt changes to '#'
# Perform administrative tasks

# Switch back to regular user
exit

# Now the prompt changes back to '$'
```

### Writing Commands for the Computer to Execute

In a Linux terminal, you interact with the system by writing commands that the computer executes. These commands can range from simple file operations to complex script executions. Understanding how to write and interpret these commands is crucial for effective DevOps work.

#### Creating a Folder Using Commands

Instead of using a graphical interface to create a folder, you can use the `mkdir` command in the terminal. This command creates a new directory.

#### Example Usage

To create a new directory named `myfolder` in your current working directory:

```bash
mkdir myfolder
```

To verify that the directory was created, you can list the contents of the current directory:

```bash
ls
```

### Common Pitfalls and How to Avoid Them

#### Misusing Privileges

One common pitfall is misusing root privileges. Executing commands as root can lead to unintended consequences, such as accidentally deleting critical system files. Always ensure you understand the implications of running commands with elevated privileges.

#### How to Prevent / Defend

To mitigate risks associated with root access, follow these best practices:

1. **Use `sudo` for Administrative Tasks**: Instead of logging in as root, use `sudo` to run individual commands with elevated privileges. This limits the exposure of root access.

2. **Regularly Audit Permissions**: Periodically review and audit file and directory permissions to ensure they are set correctly. Use tools like `chmod` and `chown` to manage permissions.

3. **Limit Root Access**: Restrict root login via SSH and other remote access methods. Use `sudo` to grant temporary elevated privileges to users who need them.

#### Example Secure Configuration

Here’s an example of setting up a secure SSH configuration to limit root access:

```bash
# Edit the SSH configuration file
sudo nano /etc/ssh/sshd_config

# Add or modify the following line to disable root login
PermitRootLogin no

# Restart the SSH service to apply changes
sudo systemctl restart sshd
```

### Real-World Examples and Recent Breaches

#### CVE-2021-44228 (Log4Shell)

The Log4Shell vulnerability (CVE-2021-44228) is a critical security flaw in the Apache Log4j library. This vulnerability allows attackers to execute arbitrary code on affected systems, leading to potential data breaches and system compromises.

#### Impact and Prevention

To prevent such vulnerabilities, ensure that all software dependencies are kept up-to-date. Regularly scan your systems for known vulnerabilities using tools like `nmap` and `OpenVAS`.

#### Example Scan Using `nmap`

```bash
# Perform a vulnerability scan using nmap
sudo nmap -sV --script vuln <target_ip>
```

### Hands-On Practice Labs

For hands-on practice with Linux commands and DevOps fundamentals, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn web security concepts.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web app for learning security.

These labs provide practical experience in applying the concepts learned in this chapter.

### Conclusion

Mastering basic Linux commands is a foundational skill for any DevOps professional. Understanding the significance of symbols like the tilde and dollar sign, and knowing how to write and execute commands effectively, can greatly enhance your ability to manage and maintain systems. By following best practices and regularly auditing your configurations, you can ensure a secure and efficient DevOps workflow.

---
<!-- nav -->
[[02-Introduction to Terminal Windows and Command Line Interface (CLI)|Introduction to Terminal Windows and Command Line Interface (CLI)]] | [[DevOps/DevOps Bootcamp/01-Linux & OS Basics/16-Mastering Basic Linux Commands For DevOps/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/01-Linux & OS Basics/16-Mastering Basic Linux Commands For DevOps/04-Practice Questions & Answers|Practice Questions & Answers]]
