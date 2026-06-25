---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to DigitalOcean Droplets and AWS EC2 Instances

In the realm of cloud computing, DigitalOcean Droplets and AWS EC2 (Elastic Compute Cloud) instances are two of the most popular services used for deploying and managing virtual servers. Both platforms offer scalable and flexible solutions for hosting applications, but they differ in terms of pricing, ease of use, and feature sets. This chapter will delve into the details of configuring and connecting to these virtual servers, focusing on the SSH (Secure Shell) protocol and the importance of proper security practices.

### Overview of DigitalOcean Droplets and AWS EC2 Instances

**DigitalOcean Droplets** are virtual servers provided by DigitalOcean, a cloud infrastructure provider. They are designed to be simple and easy to use, making them ideal for developers and small teams. Each Droplet comes with a pre-configured operating system and can be scaled up or down based on resource requirements.

**AWS EC2 Instances**, on the other hand, are part of Amazon Web Services (AWS), one of the largest cloud providers. EC2 offers a wide range of instance types, each optimized for different workloads, such as compute-intensive tasks, memory-intensive tasks, and storage-intensive tasks. AWS also provides extensive management tools and integrates seamlessly with other AWS services.

### Configuring Hostnames and Users

When setting up a web application, it is essential to configure the hostname and the user account that will be used to manage the server. This configuration is crucial for ensuring smooth communication between the client and the server.

#### Setting Up Hostnames

For a web application, the hostname typically corresponds to the domain name of the application. For example, if your application is hosted at `app.com`, you would configure the hostname accordingly. In the context of this discussion, we will assume the hostname is `app.com`.

To configure the hostname, you can use the `/etc/hosts` file on Unix-based systems. This file maps hostnames to IP addresses. Here is an example of how to modify the `/etc/hosts` file:

```plaintext
127.0.0.1   localhost
192.168.1.10 app.com
```

In this example, `192.168.1.10` is the IP address of the server, and `app.com` is the hostname.

#### Configuring User Accounts

When working with cloud servers, it is important to configure the user accounts that will be used to manage the server. Typically, cloud providers like AWS and DigitalOcean provide a default user account that can be used for initial setup.

For AWS EC2 instances, the default user account is often named `ec2-user`. This user account does not have root privileges, which is a good security practice. To switch to the root user, you can use the `sudo` command.

Here is an example of how to log in to an EC2 instance using the `ec2-user` account:

```bash
ssh -i /path/to/private_key.pem ec2-user@ip_address_or_dns_name
```

In this command:
- `-i` specifies the path to the private key file.
- `ec2-user` is the username.
- `ip_address_or_dns_name` is the IP address or DNS name of the server.

### Configuring SSH Keys

SSH keys are used to authenticate users when logging into remote servers. Proper configuration of SSH keys is crucial for maintaining the security of your server.

#### Creating and Using SSH Keys

When creating an EC2 instance, you are prompted to create or select an existing SSH key pair. The private key is downloaded to your local machine, and the public key is stored on the server. This key pair is used for authentication when connecting to the server via SSH.

Here is an example of how to create an SSH key pair:

```bash
ssh-keygen -t rsa -b 4096 -f /path/to/private_key.pem
```

This command generates a new RSA key pair with a key size of 4096 bits. The private key is saved in `/path/to/private_key.pem`, and the public key is saved in `/path/to/private_key.pem.pub`.

#### Modifying SSH Key Permissions

It is important to ensure that the private key file has the correct permissions to prevent unauthorized access. The private key file should be readable only by the owner.

Here is an example of how to modify the permissions of the private key file:

```bash
chmod 400 /path/to/private_key.pem
```

This command sets the permissions of the private key file to `400`, which means the file is readable only by the owner.

### Connecting to the Server

Once the hostname and user account are configured, and the SSH keys are set up, you can connect to the server using the `ssh` command.

Here is an example of how to connect to an EC2 instance:

```bash
ssh -i /path/to/private_key.pem ec2-user@ip_address_or_dns_name
```

Upon successful connection, you will be logged in as the `ec2-user` account.

### Security Considerations

Proper security practices are essential when managing cloud servers. Here are some key considerations:

#### SSH Key Security

- **Key Management**: Ensure that the private key is stored securely and is not shared with unauthorized parties.
- **Key Rotation**: Regularly rotate SSH keys to minimize the risk of key compromise.
- **Key Revocation**: Immediately revoke compromised keys and update the server's authorized_keys file.

#### User Account Security

- **Non-root Access**: Avoid logging in as the root user. Instead, use a non-root user account and elevate privileges using `sudo`.
- **Password Policy**: Implement strong password policies and enforce regular password changes.

#### Network Security

- **Firewall Rules**: Configure firewall rules to restrict access to the server. Only allow necessary ports and protocols.
- **Security Groups**: Use security groups to control inbound and outbound traffic to the server.

### Real-World Examples and Recent Breaches

Recent breaches and vulnerabilities have highlighted the importance of proper security practices. For example, the 2021 SolarWinds breach involved the compromise of SSH keys, leading to widespread access to sensitive systems.

#### Example: SolarWinds Breach

The SolarWinds breach involved the compromise of SSH keys, allowing attackers to gain unauthorized access to customer networks. This breach underscores the importance of proper key management and regular key rotation.

### How to Prevent / Defend

#### Secure SSH Configuration

- **Use Strong Keys**: Generate strong SSH keys with a key size of at least 4096 bits.
- **Set Correct Permissions**: Ensure that the private key file has the correct permissions (`chmod 400`).
- **Use SSH Agent**: Use an SSH agent to manage SSH keys securely.

#### Secure User Accounts

- **Non-root Access**: Use a non-root user account and elevate privileges using `sudo`.
- **Strong Passwords**: Implement strong password policies and enforce regular password changes.

#### Secure Network Configuration

- **Firewall Rules**: Configure firewall rules to restrict access to the server.
- **Security Groups**: Use security groups to control inbound and outbound traffic to the server.

### Conclusion

Configuring and managing cloud servers, such as DigitalOcean Droplets and AWS EC2 instances, requires careful attention to security practices. By properly configuring hostnames, user accounts, and SSH keys, and implementing robust security measures, you can ensure the security and reliability of your cloud infrastructure.

### Practice Labs

For hands-on experience with configuring and securing cloud servers, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs for learning web security concepts.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is vulnerable to many types of attacks.
- **WebGoat**: An interactive training application designed to teach web application security lessons.

These labs provide practical experience in configuring and securing cloud servers, helping you to master the skills needed for effective DevOps practices.

---
<!-- nav -->
[[01-Introduction to Digital Ocean Droplets and AWS EC2 Instances|Introduction to Digital Ocean Droplets and AWS EC2 Instances]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/11-Comparing Digital Ocean Droplets with AWS EC2 Instances/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/11-Comparing Digital Ocean Droplets with AWS EC2 Instances/03-Practice Questions & Answers|Practice Questions & Answers]]
