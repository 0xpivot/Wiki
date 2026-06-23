---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Configuring Application Deployment Environment on EC2 Server

In the context of Continuous Delivery (CD) pipelines, configuring the application deployment environment on an Amazon EC2 server is a critical step. This process involves setting up the necessary infrastructure and ensuring that the environment is ready to receive and deploy the application. One aspect of this setup is handling user authentication and access control, which is often referred to as "login."

### Understanding User Authentication in CD Pipelines

User authentication is the process of verifying the identity of a user who wants to access a system or perform certain actions. In the context of deploying applications on an EC2 server, this typically means ensuring that the deployment scripts or tools have the necessary credentials to log in to the server and execute commands.

#### Why User Authentication Matters

User authentication is crucial because it ensures that only authorized users can access the server and deploy applications. Without proper authentication, unauthorized individuals could gain access to the server and potentially compromise the security of the application and the underlying infrastructure.

#### How User Authentication Works

User authentication usually involves a combination of username and password, but more secure methods include:

- **Public Key Authentication**: Using SSH keys to authenticate users.
- **Multi-Factor Authentication (MFA)**: Requiring additional verification steps, such as a time-based one-time password (TOTP).

### Handling Login in CD Pipelines

In the given context, the login process is already taken care of, meaning that the necessary authentication mechanisms are in place. However, it is still an option to handle login within the CD pipeline itself. This flexibility allows for different deployment strategies and security requirements.

#### Example: Using SSH Keys for Authentication

One common method for handling login in CD pipelines is using SSH keys. Here’s how you can set up SSH key-based authentication for your EC2 instance:

1. **Generate SSH Key Pair**:
    ```bash
    ssh-keygen -t rsa -b 2048 -f ~/.ssh/id_rsa_ec2
    ```

2. **Copy Public Key to EC2 Instance**:
    ```bash
    ssh-copy-id -i ~/.ssh/id_rsa_ec2.pub ec2-user@your-ec2-instance-ip
    ```

3. **Configure SSH Configuration**:
    Create a `~/.ssh/config` file to specify the key for the EC2 instance:
    ```plaintext
    Host your-ec2-instance-ip
        IdentityFile ~/.ssh/id_rsa_ec2
    ```

4. **Deploy Application Using SSH**:
    You can now use SSH to deploy your application:
    ```bash
    ssh ec2-user@your-ec2-instance-ip 'cd /path/to/app && git pull'
    ```

### Real-World Examples and Recent Breaches

Recent breaches have highlighted the importance of robust authentication mechanisms. For example, the SolarWinds breach (CVE-2020-1014) involved attackers gaining access to systems through compromised credentials. This underscores the need for strong authentication practices, including multi-factor authentication and regular key rotation.

### Pitfalls and Common Mistakes

1. **Hardcoding Credentials**: Avoid hardcoding credentials in your deployment scripts. This can lead to exposure if the script is committed to a public repository.
2. **Weak Passwords**: Ensure that passwords used for authentication are strong and complex. Weak passwords can be easily guessed or cracked.
3. **Insufficient Logging**: Lack of proper logging can make it difficult to trace unauthorized access attempts. Ensure that authentication events are logged and monitored.

### How to Prevent / Defend

#### Secure Coding Practices

1. **Use Environment Variables**: Store sensitive information like passwords and API keys in environment variables rather than hardcoding them.
    ```bash
    export SSH_KEY="your-ssh-key"
    ```

2. **Secure Secrets Management**: Use tools like HashiCorp Vault or AWS Secrets Manager to manage and securely store secrets.

#### Secure Configuration Hardening

1. **Disable Root Login**: Disable root login via SSH to prevent direct access to the root account.
    ```plaintext
    # /etc/ssh/sshd_config
    PermitRootLogin no
    ```

2. **Enable Multi-Factor Authentication**: Enable MFA for all users accessing the EC2 instance.
    ```plaintext
    # /etc/pam.d/sshd
    auth required pam_google_authenticator.so
    ```

#### Detection and Monitoring

1. **Audit Logs**: Enable audit logs to track authentication attempts and other security-related events.
    ```plaintext
    # /etc/audit/audit.rules
    -w /var/log/auth.log -p wa -k auth-log
    ```

2. **Security Information and Event Management (SIEM)**: Use SIEM tools to monitor and analyze security events in real-time.

### Complete Example: Full SSH Request and Response

Here’s a complete example of an SSH request and response:

```plaintext
ssh ec2-user@your-ec2-instance-ip 'cd /path/to/app && git pull'
```

Response:
```plaintext
Welcome to Ubuntu 20.04 LTS (GNU/Linux 5.4.0-1039-aws x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

Last login: Mon Jan  1 00:00:00 2023 from 192.168.1.1
ec2-user@your-ec2-instance-ip:~$ cd /path/to/app && git pull
remote: Enumerating objects: 5, done.
remote: Counting objects: 100% (5/5), done.
remote: Compressing objects: 100% (3/3), done.
Unpacking objects: 100% (5/5), done.
From https://github.com/your-repo
   1234567..89abcde  master     -> origin/master
Updating 1234567..89abcde
Fast-forward
 README.md | 2 +-
 1 file changed, 1 insertion(+), 1 deletion(-)
```

### Practice Labs

For hands-on practice with configuring application deployment environments on EC2 servers, consider the following labs:

- **CloudGoat**: A cloud security training platform that includes exercises on securing EC2 instances.
- **AWS Official Workshops**: AWS provides various workshops and labs that cover the setup and configuration of EC2 instances, including authentication and access control.

By thoroughly understanding and implementing these concepts, you can ensure that your CD pipeline is secure and efficient, reducing the risk of unauthorized access and potential breaches.

---
<!-- nav -->
[[02-Configuring Application Deployment Environment on EC2 Server Part 2|Configuring Application Deployment Environment on EC2 Server Part 2]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Configure Application Deployment Environment on EC2 Server/00-Overview|Overview]] | [[04-Configuring Application Deployment Environment on EC2 Server|Configuring Application Deployment Environment on EC2 Server]]
