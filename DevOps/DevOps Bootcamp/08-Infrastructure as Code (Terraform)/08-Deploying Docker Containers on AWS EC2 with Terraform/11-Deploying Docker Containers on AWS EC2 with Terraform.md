---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Deploying Docker Containers on AWS EC2 with Terraform

### Introduction to IP Address Management in AWS EC2

When deploying Docker containers on AWS EC2 instances using Terraform, managing IP addresses is crucial for ensuring security and accessibility. This section will delve into the concepts of IP address management, CIDR blocks, and how to configure them securely within Terraform.

#### What is an IP Address?

An IP (Internet Protocol) address is a unique identifier assigned to devices connected to a computer network. It allows devices to communicate with each other over the internet. There are two versions of IP addresses: IPv4 and IPv6. IPv4 addresses are 32-bit numbers, typically represented in dotted decimal notation (e.g., `192.168.1.1`), while IPv6 addresses are 128-bit numbers, often written in colon-separated hexadecimal notation (e.g., `2001:0db8:85a3:0000:0000:8a2e:0370:7334`).

#### CIDR Blocks

CIDR (Classless Inter-Domain Routing) blocks are used to represent a range of IP addresses. A CIDR block consists of an IP address followed by a slash and a number indicating the number of bits used for the network prefix. For example, `192.168.1.0/24` represents a range of IP addresses from `192.168.1.0` to `192.168.1.255`.

In the context of AWS EC2, CIDR blocks are used to define the IP address ranges for subnets and security groups. For instance, if you want to allow a specific range of IP addresses to access your EC2 instance via SSH, you would define a CIDR block in your security group rules.

### Configuring Security Groups with CIDR Blocks

Security groups in AWS EC2 act as virtual firewalls that control inbound and outbound traffic to your instances. They are stateful, meaning that if you allow incoming traffic on a certain port, the corresponding outgoing traffic is automatically allowed.

#### Example: Allowing SSH Access from Specific IP Addresses

Let's consider a scenario where you want to allow SSH access to your EC2 instance from a specific set of IP addresses. You can achieve this by configuring a security group rule with a CIDR block.

```hcl
resource "aws_security_group" "ssh_access" {
  name        = "ssh_access"
  description = "Allow SSH access from specific IP addresses"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["192.168.1.1/32", "192.168.1.2/32"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

In this example, the security group `ssh_access` allows inbound TCP traffic on port 22 (SSH) from the IP addresses `192.168.1.1` and `192.168.1.2`. The egress rule allows all outbound traffic.

### Handling Dynamic IP Addresses

If your IP address is dynamic, meaning it changes frequently, hardcoding it in your Terraform configuration is not practical. Instead, you can use variables to dynamically reference the IP address.

#### Example: Using Variables for Dynamic IP Addresses

```hcl
variable "my_ip" {
  description = "The IP address to allow SSH access from"
  type        = string
}

resource "aws_security_group" "ssh_access" {
  name        = "ssh_access"
  description = "Allow SSH access from specific IP addresses"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${var.my_ip}/32"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

In this example, the `my_ip` variable is used to specify the IP address. You can pass the value of `my_ip` when applying the Terraform configuration:

```sh
terraform apply -var="my_ip=192.168.1.1"
```

### Real-World Examples and Recent Breaches

#### Example: CVE-2021-20225

CVE-2021-20225 is a vulnerability in the AWS SDK for Java that could allow unauthorized access to EC2 instances due to improper validation of IP addresses in security group rules. This highlights the importance of properly configuring security groups and validating IP addresses.

#### Example: Breach at Capital One

In 2019, Capital One suffered a data breach where an attacker exploited misconfigured security group rules in AWS, allowing unauthorized access to sensitive data. This underscores the critical nature of securing IP addresses and network access.

### How to Prevent / Defend

#### Detection

To detect unauthorized access attempts, you can enable VPC Flow Logs and CloudTrail logging in AWS. VPC Flow Logs capture information about the IP traffic going to and from network interfaces in your VPC. CloudTrail logs provide detailed records of API calls made within your AWS account.

#### Prevention

1. **Use Strong Security Group Rules**: Ensure that security group rules are as restrictive as possible, allowing only necessary IP addresses and ports.
2. **Enable Network ACLs**: Network ACLs provide an additional layer of security by filtering traffic at the subnet level.
3. **Regularly Audit Security Group Rules**: Periodically review and update security group rules to ensure they remain secure and up-to-date.
4. **Use IAM Roles**: Instead of hardcoding credentials, use IAM roles to grant permissions to EC2 instances.

#### Secure Coding Fixes

Here is an example of a vulnerable security group configuration and its secure counterpart:

**Vulnerable Configuration**

```hcl
resource "aws_security_group" "ssh_access" {
  name        = "ssh_access"
  description = "Allow SSH access from any IP address"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   =  0
    to_port     =  0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

**Secure Configuration**

```hcl
variable "my_ip" {
  description = "The IP address to allow SSH access from"
  type        = string
}

resource "aws_security_group" "ssh_access" {
  name        = "ssh_access"
  description = "Allow SSH access from specific IP addresses"

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["${var.my_ip}/32"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
```

### Hands-On Labs

For hands-on practice with deploying Docker containers on AWS EC2 using Terraform, consider the following resources:

- **PortSwigger Web Security Academy**: Offers a comprehensive course on web application security, including sections on infrastructure security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training purposes.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.
- **WebGoat**: An interactive, gamified training application for learning about web application security.

These labs provide practical experience in configuring and securing AWS EC2 instances and Terraform configurations.

### Conclusion

Proper management of IP addresses and CIDR blocks is essential for securing AWS EC2 instances deployed with Terraform. By understanding the principles behind IP addresses, CIDR blocks, and security group rules, you can effectively configure your infrastructure to be both accessible and secure. Regular auditing and updates to your security configurations will help mitigate risks and prevent unauthorized access.

---
<!-- nav -->
[[10-Creating an Internet Gateway in the VPC|Creating an Internet Gateway in the VPC]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/08-Deploying Docker Containers on AWS EC2 with Terraform/00-Overview|Overview]] | [[12-Security Groups in AWS EC2|Security Groups in AWS EC2]]
