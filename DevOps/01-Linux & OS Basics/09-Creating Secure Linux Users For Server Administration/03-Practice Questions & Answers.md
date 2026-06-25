---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Why is it important to avoid running services with root privileges?**

Running services with root privileges poses significant security risks. If a service running with root privileges is compromised, the attacker gains full control over the system, leading to potential data breaches, unauthorized access, and system damage. By creating a dedicated user for each service with minimal necessary permissions, the attack surface is reduced, enhancing overall system security.

**Q2. How would you create a new Linux user and grant it sudo privileges?**

To create a new Linux user and grant it sudo privileges, follow these steps:

1. Create the user:
   ```bash
   sudo adduser nana
   ```
2. Set a password for the user:
   ```bash
   sudo passwd nana
   ```
3. Add the user to the sudo group:
   ```bash
   sudo usermod -aG sudo nana
   ```

This process creates a new user named `nana` and adds them to the `sudo` group, allowing them to execute commands with elevated privileges.

**Q3. Explain how to configure SSH access for a newly created user.**

Configuring SSH access for a newly created user involves the following steps:

1. Switch to the new user:
   ```bash
   su - nana
   ```
2. Create the `.ssh` directory in the user’s home directory:
   ```bash
   mkdir ~/.ssh
   chmod 700 ~/.ssh
   ```
3. Create the `authorized_keys` file and add the public SSH key:
   ```bash
   echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... user@hostname" > ~/.ssh/authorized_keys
   chmod 600 ~/.ssh/authorized_keys
   ```

Replace `"ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC... user@hostname"` with your actual public SSH key.

4. Test SSH login:
   ```bash
   ssh nana@your_server_ip
   ```

This setup ensures that the user can securely log in via SSH using their public key.

**Q4. What are the benefits of creating a dedicated user for each application?**

Creating a dedicated user for each application offers several benefits:

1. **Isolation**: Each application runs under its own user, limiting the scope of potential damage if the application is compromised.
2. **Minimal Privileges**: The user can be granted only the necessary permissions, reducing the risk of unauthorized actions.
3. **Auditability**: Actions performed by the user can be tracked and audited, making it easier to monitor and manage application activities.
4. **Compliance**: Many security standards and best practices recommend isolating applications to enhance security and compliance.

For example, the recent breach of SolarWinds (CVE-2020-1014) highlighted the importance of isolating software components to prevent widespread compromise.

**Q5. How would you switch between users on a Linux server?**

Switching between users on a Linux server can be done using the `su` command. Here’s how:

1. To switch to another user:
   ```bash
   su - username
   ```
   Replace `username` with the desired user’s name. You may be prompted to enter the password for the target user.

2. To return to the original user:
   ```bash
   exit
   ```

Using `su -` ensures that the environment variables are set according to the target user, providing a fully functional session as that user.

**Q6. What is the significance of the `$` and `#` signs in the terminal prompt?**

The `$` and `#` signs in the terminal prompt signify different user types:

- `$`: Represents a regular user prompt. When you see this symbol, you are logged in as a non-root user.
- `#`: Represents a root user prompt. When you see this symbol, you are logged in as the root user or executing commands with elevated privileges using `sudo`.

These symbols help distinguish between user levels and remind users of their current privileges, aiding in security awareness and preventing accidental misuse of elevated privileges.

**Q7. How would you ensure that a newly created user has the necessary permissions to perform administrative tasks without full root access?**

To ensure a newly created user has the necessary permissions to perform administrative tasks without full root access, follow these steps:

1. Create the user and add them to the sudo group:
   ```bash
   sudo adduser nana
   sudo usermod -aG sudo nana
   ```

2. Configure sudoers file to specify allowed commands:
   ```bash
   sudo visudo
   ```
   Add a line like:
   ```bash
   nana ALL=(ALL) NOPASSWD: /path/to/command
   ```
   This allows the user `nana` to run `/path/to/command` without needing a password.

By carefully configuring sudo permissions, you can grant users the ability to perform specific administrative tasks without granting full root access, enhancing security and control.

---
<!-- nav -->
[[02-Creating Secure Linux Users for Server Administration|Creating Secure Linux Users for Server Administration]] | [[DevOps/DevOps Bootcamp/01-Linux & OS Basics/09-Creating Secure Linux Users For Server Administration/00-Overview|Overview]]
