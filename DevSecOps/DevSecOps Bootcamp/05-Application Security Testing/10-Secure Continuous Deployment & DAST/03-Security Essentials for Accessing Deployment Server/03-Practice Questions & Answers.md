---
course: DevSecOps
topic: Secure Continuous Deployment & DAST
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Why is having SSH port 22 open to the entire internet considered a security risk?**

Having SSH port 22 open to the entire internet is considered a significant security risk because it exposes the server to potential brute force attacks, unauthorized access attempts, and other malicious activities. Even though SSH requires a private key for authentication, leaving the port open to the world increases the attack surface, making it easier for attackers to attempt unauthorized access. By limiting access to only whitelisted IP addresses, you significantly reduce the likelihood of such attacks.

**Q2. How can you configure SSH access to only allow connections from specific IP addresses?**

To configure SSH access to only allow connections from specific IP addresses, you can modify the firewall rules associated with the EC2 instance. For example, using AWS Security Groups, you can specify inbound rules that only allow traffic on port 22 from certain IP addresses. Here’s an example configuration:

```plaintext
Inbound Rule:
Type: SSH
Protocol: TCP
Port Range: 22
Source: <whitelisted IP address>
```

This ensures that only the specified IP addresses can connect to the SSH port, enhancing security by reducing the number of potential attack vectors.

**Q3. Explain why relying solely on SSH access for server management is less secure compared to using AWS CLI.**

Relying solely on SSH access for server management is less secure compared to using AWS CLI because SSH bypasses the AWS authentication mechanisms. When you SSH directly into an EC2 instance, you are essentially creating a backdoor that AWS cannot monitor or control. This means that AWS may not be aware of the actions performed via SSH, leading to potential security gaps.

Using AWS CLI, on the other hand, involves authenticating with AWS using IAM credentials and then making API calls to manage resources. This approach provides better visibility and control over actions performed on AWS resources, as all operations are logged and can be audited. Additionally, AWS CLI leverages temporary access tokens, which are more secure than static private keys used in SSH.

**Q4. How can you completely block SSH access to an EC2 instance while still being able to manage it securely?**

To completely block SSH access to an EC2 instance while still being able to manage it securely, you can follow these steps:

1. **Close Port 22**: Modify the Security Group associated with the EC2 instance to remove the inbound rule for SSH (port 22). This will prevent any external SSH connections.

2. **Use AWS CLI**: Use the AWS Command Line Interface (CLI) to manage the EC2 instance. The AWS CLI allows you to perform actions like starting/stopping instances, managing volumes, and executing commands on the instance using AWS APIs.

3. **Set Up IAM Policies**: Ensure that IAM users have appropriate policies attached that grant them the necessary permissions to manage the EC2 instance via the AWS CLI. This includes permissions to start/stop instances, execute commands, and manage other related resources.

By closing port 22 and using the AWS CLI, you eliminate the risk associated with direct SSH access while maintaining full control over the instance through secure and monitored channels.

**Q5. What are the benefits of using AWS CLI for managing EC2 instances compared to traditional SSH access?**

Using AWS CLI for managing EC2 instances offers several benefits over traditional SSH access:

1. **Enhanced Security**: The AWS CLI uses IAM credentials and temporary access tokens, which are more secure than static private keys used in SSH. This reduces the risk of key exposure and unauthorized access.

2. **Better Auditing and Logging**: All actions performed via the AWS CLI are logged and can be audited, providing better visibility into who did what and when. This is crucial for compliance and forensic analysis.

3. **Integrated with AWS Services**: The AWS CLI integrates seamlessly with other AWS services, allowing you to manage resources consistently across the board. This includes managing EC2 instances, RDS databases, S3 buckets, and more.

4. **Automation and Scripting**: The AWS CLI supports automation and scripting, enabling you to write scripts to automate repetitive tasks, such as starting/stopping instances, deploying applications, and managing configurations.

5. **Reduced Attack Surface**: By eliminating direct SSH access, you reduce the attack surface of your EC2 instances, making them less vulnerable to external threats.

For example, consider a recent breach where an attacker gained unauthorized access to an EC2 instance via SSH. If the instance had been managed exclusively via the AWS CLI, the attack vector would have been significantly reduced, potentially preventing the breach altogether.

---
<!-- nav -->
[[02-Secure Continuous Deployment & DAST Security Essentials for Accessing Deployment Server|Secure Continuous Deployment & DAST Security Essentials for Accessing Deployment Server]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/03-Security Essentials for Accessing Deployment Server/00-Overview|Overview]]
