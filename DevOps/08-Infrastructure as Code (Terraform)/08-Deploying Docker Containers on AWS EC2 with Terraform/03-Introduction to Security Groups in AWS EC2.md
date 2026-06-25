---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Security Groups in AWS EC2

Security groups act as virtual firewalls for your Amazon Elastic Compute Cloud (EC2) instances, controlling inbound and outbound traffic. They are essential for securing your instances by allowing or denying traffic based on predefined rules. Understanding how to configure these rules is crucial for maintaining the security and accessibility of your EC2 instances.

### What Are Security Groups?

A security group is a virtual firewall that controls the traffic for your EC2 instances. Each security group is associated with a set of rules that define which traffic is allowed to reach the instances. These rules specify the following:

- **Protocol**: The type of traffic (TCP, UDP, ICMP).
- **Port Range**: The range of ports that the traffic can use.
- **Source/Destination**: The IP addresses or other security groups that are allowed to send/receive traffic.

### Why Use Security Groups?

Security groups provide a layer of security by controlling the traffic that reaches your instances. By defining specific rules, you can ensure that only authorized traffic is allowed to access your instances. This helps in preventing unauthorized access and potential attacks.

### How Security Groups Work

When you launch an EC2 instance, you associate it with one or more security groups. Each security group has a set of rules that define the traffic that is allowed to reach the instance. The rules are evaluated in the order they are listed, and the first matching rule determines whether the traffic is allowed or denied.

### Example of a Security Group Rule

Let's consider a simple example where we allow SSH traffic to an EC2 instance. The rule would look like this:

- **Protocol**: TCP
- **Port Range**: 22
- **Source**: Any IP address (0.0.0.0/0)

This rule allows any IP address to send TCP traffic to port 22 on the instance.

### Configuring Security Groups Using Terraform

Terraform is an infrastructure as code (IaC) tool that allows you to define and manage your infrastructure using declarative configuration files. You can use Terraform to define and manage security groups for your EC2 instances.

#### Terraform Configuration for Security Groups

Here is an example of how to define a security group using Terraform:

```hcl
resource "aws_security_group" "example" {
  name        = "example"
  description = "Allow SSH access"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

In this example, we define a security group named `example` that allows SSH traffic (port 22) from any IP address (`0.0.0.0/0`). The `egress` block defines the outbound traffic rules, allowing all outbound traffic.

### Detailed Explanation of Security Group Rules

#### Ingress Rules

Ingress rules control the inbound traffic to your EC2 instances. Here are the key components of an ingress rule:

- **from_port**: The starting port number of the range.
- **to_port**: The ending port number of the range.
- **protocol**: The protocol used (TCP, UDP, ICMP).
- **cidr_blocks**: The list of CIDR blocks that are allowed to send traffic to the specified port range.

#### Egress Rules

Egress rules control the outbound traffic from your EC2 instances. Similar to ingress rules, egress rules have the following components:

- **from_port**: The starting port number of the range.
- **to_port**: The ending port number of the range.
- **protocol**: The protocol used (TCP, UDP, ICMP).
- **cidr_blocks**: The list of CIDR blocks that are allowed to receive traffic from the specified port range.

### Real-World Examples and Breaches

#### Example: CVE-2021-21547

CVE-2021-21547 is a critical vulnerability in the AWS SDK for Java, which could allow an attacker to bypass security group rules and gain unauthorized access to EC2 instances. This vulnerability highlights the importance of properly configuring security groups and keeping your software up to date.

#### Example: SSH Brute Force Attacks

SSH brute force attacks are a common method used by attackers to gain unauthorized access to EC2 instances. By attempting to guess the SSH password, attackers can bypass weak security group rules that allow SSH traffic from any IP address.

### How to Prevent / Defend

#### Detection

To detect unauthorized access attempts, you can enable AWS CloudTrail and monitor the logs for suspicious activity. Additionally, you can use AWS GuardDuty to automatically detect and respond to threats.

#### Prevention

To prevent unauthorized access, you should:

1. **Limit Access**: Restrict the source IP addresses that are allowed to access your instances. Instead of allowing traffic from any IP address (`0.0.0.0/0`), limit it to specific IP addresses or ranges.
2. **Use Strong Passwords**: Ensure that your SSH passwords are strong and complex. Consider using SSH keys instead of passwords for added security.
3. **Enable Two-Factor Authentication**: Enable two-factor authentication (2FA) for SSH access to further secure your instances.
4. **Keep Software Up to Date**: Regularly update your software and apply security patches to protect against known vulnerabilities.

#### Secure Coding Fixes

Here is an example of how to configure a security group with limited access:

```hcl
resource "aws_security_group" "secure_example" {
  name        = "secure_example"
  description = "Allow SSH access from specific IP"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["192.168.1.1/32"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

In this example, we restrict SSH access to a specific IP address (`192.168.1.1/32`).

### Common Pitfalls

#### Allowing Traffic from Any IP Address

One common pitfall is allowing traffic from any IP address (`0.0.0.0/0`). This can expose your instances to unauthorized access and potential attacks. Always limit the source IP addresses that are allowed to access your instances.

#### Not Keeping Software Up to Date

Another common pitfall is not keeping your software up to date. This can leave your instances vulnerable to known vulnerabilities and attacks. Always apply security patches and updates regularly.

### Conclusion

Security groups are a crucial component of securing your EC2 instances. By properly configuring security group rules, you can control the traffic that reaches your instances and prevent unauthorized access. Using tools like Terraform, you can define and manage your security groups in a declarative manner, ensuring consistency and security.

### Practice Labs

For hands-on practice with deploying Docker containers on AWS EC2 with Terraform, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web security, including deploying and securing Docker containers.
- **OWASP Juice Shop**: A deliberately insecure web application that you can use to practice deploying and securing Docker containers.
- **AWS Official Workshops**: Provides guided workshops and labs that cover deploying and managing EC2 instances with Terraform.

By completing these labs, you can gain practical experience in deploying and securing Docker containers on AWS EC2 using Terraform.

---
<!-- nav -->
[[02-Introduction to Route Tables in AWS VPC|Introduction to Route Tables in AWS VPC]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/08-Deploying Docker Containers on AWS EC2 with Terraform/00-Overview|Overview]] | [[04-Introduction to Terraform and AWS EC2 Deployment|Introduction to Terraform and AWS EC2 Deployment]]
