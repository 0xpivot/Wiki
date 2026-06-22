---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## SSH Key Pairs and Instance Creation

When creating an instance in a cloud environment such as AWS, Azure, or Google Cloud, one of the critical steps is assigning an SSH key pair to the instance. This key pair allows you to securely log in to the server using SSH (Secure Shell).

### What is an SSH Key Pair?

An SSH key pair consists of two parts: a private key and a public key. The private key is kept secret and should never be shared, while the public key can be freely distributed. When you attempt to log in to a server, the server uses the public key to verify your identity based on the private key.

### Why Use SSH Key Pairs?

Using SSH key pairs provides several advantages over traditional password-based authentication:

1. **Security**: SSH keys are more secure than passwords because they are longer and more complex.
2. **Automation**: SSH keys can be used in scripts and automation tools, making it easier to manage large numbers of servers.
3. **Non-repudiation**: SSH keys provide a level of non-repudiation, meaning that once a key is used, it can be traced back to the specific user or system.

### Creating an SSH Key Pair

To create an SSH key pair, you can use the `ssh-keygen` command-line tool. Here’s an example of how to generate an RSA key pair:

```bash
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

This command generates a 4096-bit RSA key pair and associates it with your email address. The output will look something like this:

```plaintext
Generating public/private rsa key pair.
Enter file in which to save the key (/home/user/.ssh/id_rsa): 
Enter passphrase (empty for no passphrase): 
Enter same passphrase again: 
Your identification has been saved in /home/user/.ssh/id_rsa.
Your public key has been saved in /home/user/.ssh/id_rsa.pub.
The key fingerprint is:
SHA256:xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx your_email@example.com
The key's randomart image is:
+---[RSA 4096]----+
|                 |
|                 |
|                 |
|                 |
|                 |
|                 |
|                 |
|                 |
|                 |
+----[SHA256]-----+
```

### Adding SSH Key to Cloud Provider

Once you have generated the SSH key pair, you need to add the public key to your cloud provider. For example, in AWS, you would go to the EC2 dashboard and add the public key to the list of key pairs.

### SSH Key Management Pitfalls

One common pitfall is losing access to the private key. If you lose the private key, you will no longer be able to log in to the server. To mitigate this risk, you should:

1. **Backup the Private Key**: Store the private key in a secure location, such as a password manager or a hardware security module.
2. **Use Multiple Keys**: Consider using multiple SSH keys for different environments or purposes.

### How to Prevent / Defend

#### Detection

Regularly check the list of authorized keys on your servers to ensure that no unauthorized keys have been added.

#### Prevention

1. **Use Strong Passphrases**: Protect your private key with a strong passphrase.
2. **Limit Access**: Restrict access to the private key to only those who need it.
3. **Audit Logs**: Enable and monitor audit logs to detect unauthorized access attempts.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/11-Integrating Terraform into CICD Pipeline/06-Real-World Examples and Recent Breaches|Real-World Examples and Recent Breaches]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/11-Integrating Terraform into CICD Pipeline/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/11-Integrating Terraform into CICD Pipeline/08-Practice Questions & Answers|Practice Questions & Answers]]
