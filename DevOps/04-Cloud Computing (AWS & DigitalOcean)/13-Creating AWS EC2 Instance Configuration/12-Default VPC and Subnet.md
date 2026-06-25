---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Default VPC and Subnet

If you do not specify the subnet ID and security group ID, the EC2 instance will be launched into a default VPC and one of the subnets within that VPC. This can lead to unexpected behavior and security risks.

### Example of Default VPC Behavior

If you do not specify the subnet ID and security group ID, the EC2 instance will be launched into a default VPC and one of the subnets within that VPC. This can lead to unexpected behavior and security risks.

#### How to Detect Default VPC Behavior

You can detect whether an EC2 instance is launched into a default VPC by checking the VPC ID and subnet ID of the instance. For example, using the AWS CLI:

```sh
aws ec2 describe-instances --instance-ids i-0123456789abcdef0
```

This command returns the details of the specified EC2 instance, including the VPC ID and subnet ID.

#### How to Prevent Default VPC Behavior

To prevent the EC2 instance from being launched into a default VPC, you should always specify the subnet ID and security group ID in the instance configuration. This ensures that the instance is launched into the correct VPC and subnet, and is assigned the correct security group.

### Real-World Example: CVE-2021-20225

CVE-2021-20225 is a vulnerability in AWS EC2 instances that allows unauthorized access to the instance metadata service. This vulnerability can be exploited if the EC2 instance is launched into a default VPC and does not have proper network isolation.

#### How to Detect CVE-2021-20225

You can detect whether an EC2 instance is vulnerable to CVE-2021-20225 by checking the security group rules and network isolation settings of the instance. For example, using the AWS CLI:

```sh
aws ec2 describe-security-groups --group-ids sg-0123456789abcdef0
```

This command returns the details of the specified security group, including the ingress and egress rules.

#### How to Prevent CVE-2021-20225

To prevent the EC2 instance from being vulnerable to CVE-2021-20225, you should ensure that the instance is launched into a non-default VPC and subnet, and is assigned a security group with proper network isolation settings. For example, in a Terraform configuration file:

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c94855ba95b798c7"
  instance_type = var.instance_type
  subnet_id     = "subnet-0123456789abcdef0"
  vpc_security_group_ids = ["sg-0123456789abcdef0"]
}
```

In this example, the `subnet_id` and `vpc_security_group_ids` attributes are set to specific values, ensuring that the EC2 instance is launched into the correct VPC and subnet, and is assigned the correct security group.

---
<!-- nav -->
[[11-Creating AWS EC2 Instance Configuration|Creating AWS EC2 Instance Configuration]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/13-Creating AWS EC2 Instance Configuration/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/13-Creating AWS EC2 Instance Configuration/13-Hands-On Labs|Hands-On Labs]]
