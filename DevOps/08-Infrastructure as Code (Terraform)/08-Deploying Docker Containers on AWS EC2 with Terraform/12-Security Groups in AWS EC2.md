---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Security Groups in AWS EC2

### Introduction to Security Groups

Security groups in AWS EC2 are virtual firewalls that control inbound and outbound traffic to your instances. They are stateful, meaning that if you allow incoming traffic on a specific port, the corresponding outgoing traffic is automatically allowed. Security groups are essential for securing your EC2 instances by controlling access based on IP addresses, protocols, and ports.

#### Why Security Groups Matter

Security groups provide a layer of security by allowing you to specify which traffic is allowed to reach your instances. Without proper security group configurations, your instances could be exposed to unauthorized access, leading to potential security breaches. For example, the Heartbleed bug (CVE-2014-0160) exploited a flaw in OpenSSL, which could have been mitigated by properly configuring security groups to restrict access to sensitive services.

### Creating a Security Group

To create a security group using Terraform, you first need to define the resource in your Terraform configuration file. Here’s an example of how to create a security group:

```hcl
resource "aws_security_group" "example" {
  name        = "example-sg"
  description = "Example security group"
  vpc_id      = aws_vpc.example.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["<your-ip-address>/32"]
  }

  ingress {
    from_port   = 8080
    to_port     = 8080
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

In this example:
- `name` specifies the name of the security group.
- `description` provides a description for the security group.
- `vpc_id` specifies the VPC ID where the security group will be created.
- `ingress` defines the inbound rules.
- `egress` defines the outbound rules.

### Inbound Rules

Inbound rules control the traffic that can enter your EC2 instances. In the example above, we have two inbound rules:
1. **SSH Access**: Allows SSH traffic on port 22 from a specific IP address (`<your-ip-address>`).
2. **Custom TCP Access**: Allows TCP traffic on port 8080 from all sources (`0.0.0.0/0`).

#### SSH Access

SSH (Secure Shell) is a cryptographic network protocol for operating network services securely. Allowing SSH access from a specific IP address ensures that only authorized users can connect to your instance via SSH.

#### Custom TCP Access

Allowing TCP traffic on port 8080 from all sources (`0.0.0.0/0`) means that any device can send TCP traffic to your instance on this port. This is useful for services like web applications, but it also increases the risk of unauthorized access.

### Outbound Rules

Outbound rules control the traffic that can leave your EC2 instances. In the example above, we have one outbound rule:
- **All Traffic**: Allows all traffic to leave the instance to any destination (`0.0.0.0/0`).

### Using Default Security Group

Instead of creating a new security group, you can use the default security group provided by AWS. This is useful when you want to simplify your configuration and avoid managing additional resources.

To use the default security group in Terraform, you can modify the resource definition as follows:

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  vpc_security_group_ids = [aws_default_security_group.default.id]
}
```

In this example:
- `vpc_security_group_ids` specifies the security group IDs to associate with the instance.
- `aws_default_security_group.default.id` refers to the default security group.

### Security Group Diagram

Here’s a mermaid diagram illustrating the security group configuration:

```mermaid
graph TD
  A[EC2 Instance] -->|SSH (22)| B[Your IP Address]
  A -->|TCP (8080)| C[All Sources]
  A -->|All Traffic| D[All Destinations]
```

### Pitfalls and Best Practices

#### Pitfall: Exposing SSH to the World

Exposing SSH to the world by allowing access from `0.0.0.0/0` is a significant security risk. An attacker could brute-force the SSH credentials, leading to unauthorized access.

**How to Prevent / Defend**

- **Restrict SSH Access**: Limit SSH access to specific IP addresses or ranges.
- **Use Key-Based Authentication**: Instead of password-based authentication, use key-based authentication to secure SSH access.
- **Monitor SSH Logs**: Regularly monitor SSH logs for suspicious activity.

#### Pitfall: Allowing Unnecessary Traffic

Allowing all traffic to leave the instance (`0.0.0.0/0`) can expose your instance to potential attacks. For example, if an attacker gains access to your instance, they can use it to launch attacks on other systems.

**How to Prevent / Defend**

- **Limit Outbound Traffic**: Restrict outbound traffic to only the necessary destinations.
- **Use Network ACLs**: Configure Network ACLs to further restrict traffic at the subnet level.
- **Regular Audits**: Perform regular audits of your security group configurations to ensure they are up-to-date and secure.

### Real-World Example: Heartbleed Bug (CVE-2014-0160)

The Heartbleed bug was a serious vulnerability in the popular OpenSSL cryptographic software library. It allowed attackers to steal information protected by SSL/TLS encryption, such as passwords, private keys, and sensitive data.

**How to Prevent / Defend**

- **Update OpenSSL**: Ensure that your OpenSSL installation is up-to-date and patched against known vulnerabilities.
- **Use Security Groups**: Configure security groups to restrict access to sensitive services.
- **Monitor Logs**: Regularly monitor logs for signs of unauthorized access or suspicious activity.

### Conclusion

Security groups are a crucial component of securing your EC2 instances. By properly configuring inbound and outbound rules, you can control access to your instances and mitigate potential security risks. Always follow best practices and regularly audit your configurations to ensure they remain secure.

### Practice Labs

For hands-on practice with deploying Docker containers on AWS EC2 with Terraform, consider the following labs:
- **PortSwigger Web Security Academy**: Offers comprehensive training on web security, including deploying and securing Docker containers.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for learning web security.
- **WebGoat**: A deliberately insecure Java web application designed to teach web application security lessons.

These labs provide practical experience in deploying and securing Docker containers on AWS EC2 using Terraform.

---
<!-- nav -->
[[11-Deploying Docker Containers on AWS EC2 with Terraform|Deploying Docker Containers on AWS EC2 with Terraform]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/08-Deploying Docker Containers on AWS EC2 with Terraform/00-Overview|Overview]] | [[13-Understanding Route Tables in AWS VPC|Understanding Route Tables in AWS VPC]]
