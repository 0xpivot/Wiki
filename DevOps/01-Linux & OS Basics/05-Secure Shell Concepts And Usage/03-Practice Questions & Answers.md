---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the purpose of SSH and why it is considered secure.**

SSH, or Secure Shell, is a protocol used for securely accessing and managing remote servers. Its primary purpose includes enabling secure command-line access, file transfers, and executing commands on remote servers. SSH is considered secure because it uses encryption to protect data transmitted between the client and the server, ensuring that unauthorized parties cannot intercept or tamper with the communication. Additionally, SSH supports strong authentication methods, such as username/password and public/private key pairs, which further enhance security.

**Q2. Describe the difference between username/password authentication and SSH key-based authentication.**

Username/password authentication requires users to provide a username and password to authenticate themselves with the remote server. This method is less secure because passwords can be intercepted or guessed. On the other hand, SSH key-based authentication uses a pair of keys: a public key and a private key. The public key is stored on the server, while the private key remains on the client's machine. When a client attempts to connect, the server verifies the client's identity using the private key, making this method more secure as it eliminates the risk of password interception.

**Q3. How can you set up SSH key-based authentication for a user on a remote server?**

To set up SSH key-based authentication, follow these steps:

1. Generate an SSH key pair on the client machine using the `ssh-keygen` command.
2. Copy the public key (`id_rsa.pub`) to the remote server. This can be done manually or using the `ssh-copy-id` command.
3. Append the public key to the `~/.ssh/authorized_keys` file on the remote server.
4. Ensure the `~/.ssh` directory and the `authorized_keys` file have the correct permissions (`700` for the directory and `600` for the file).

Example commands:

```bash
# Generate SSH key pair
ssh-keygen -t rsa -b 4096

# Copy public key to remote server
ssh-copy-id user@remote-server-ip

# Verify permissions
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys
```

**Q4. What is the significance of the SSH port number 22, and how can it be secured using a firewall?**

Port 22 is the default port for SSH communication. To secure SSH using a firewall, you can restrict access to this port by configuring firewall rules to allow traffic only from trusted IP addresses. This helps prevent unauthorized access attempts and reduces the risk of brute-force attacks.

Example firewall rule using `iptables`:

```bash
# Allow SSH access only from a specific IP address
sudo iptables -A INPUT -p tcp --dport 22 -s trusted_ip_address -j ACCEPT

# Block all other incoming SSH connections
sudo iptables -A INPUT -p tcp --dport 22 -j DROP
```

**Q5. How can you use SCP to securely transfer files between a local and a remote server?**

SCP (Secure Copy) is a command-line utility that allows you to securely transfer files between a local and a remote server using SSH. Here’s how to use SCP:

1. To copy a file from the local machine to the remote server:
   ```bash
   scp /path/to/local/file user@remote-server-ip:/path/to/destination/
   ```

2. To copy a file from the remote server to the local machine:
   ```bash
   scp user@remote-server-ip:/path/to/remote/file /path/to/local/destination/
   ```

For example, to copy a file named `test.sh` from the local machine to the remote server:

```bash
scp /home/user/test.sh user@remote-server-ip:/home/user/
```

**Q6. What are the benefits of using SSH keys over traditional username/password authentication?**

Using SSH keys provides several benefits over traditional username/password authentication:

1. **Enhanced Security**: SSH keys are more secure as they eliminate the risk of password interception and guessing attacks.
2. **Convenience**: SSH keys allow for automated login and script execution without requiring manual password entry.
3. **Flexibility**: SSH keys can be used for various purposes, such as allowing automated processes (e.g., Jenkins) to access remote servers securely.
4. **Stronger Authentication**: SSH keys support stronger cryptographic algorithms compared to password-based authentication, providing better protection against unauthorized access.

**Q7. How can you ensure that SSH connections are only allowed from specific IP addresses?**

To ensure that SSH connections are only allowed from specific IP addresses, you can configure the firewall to restrict access to port 22. This can be done using tools like `iptables` or `ufw`.

Example using `ufw`:

```bash
# Allow SSH access from a specific IP address
sudo ufw allow from trusted_ip_address to any port 22

# Deny all other SSH access
sudo ufw deny 22
```

This configuration ensures that only the specified IP address can establish an SSH connection, enhancing security by blocking unauthorized access attempts.

---
<!-- nav -->
[[02-Secure Shell Concepts and Usage|Secure Shell Concepts and Usage]] | [[DevOps/DevOps Bootcamp/01-Linux & OS Basics/05-Secure Shell Concepts And Usage/00-Overview|Overview]]
