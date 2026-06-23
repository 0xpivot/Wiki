---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Optional Attributes for Launching an EC2 Instance

### Subnet ID

#### What is a Subnet ID?

A subnet is a range of IP addresses within a VPC. The subnet ID identifies a specific subnet within the VPC. By specifying the subnet ID, you can control which subnet the EC2 instance is launched into.

#### Why is Subnet ID Important?

Specifying the subnet ID ensures that the EC2 instance is launched into the correct subnet within your VPC. This is important for network segmentation and security purposes.

#### How to Specify Subnet ID

You can specify the subnet ID in the EC2 instance configuration. For example, in a Terraform configuration file:

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c94855ba95b798c7"
  instance_type = var.instance_type
  subnet_id     = "subnet-0123456789abcdef0"
}
```

In this example, the `subnet_id` attribute is set to a specific subnet ID, ensuring that the EC2 instance is launched into the correct subnet.

### Security Group ID

#### What is a Security Group ID?

A security group is a virtual firewall that controls inbound and outbound traffic to your EC2 instance. The security group ID identifies a specific security group within the VPC. By specifying the security group ID, you can control the network access to the EC2 instance.

#### Why is Security Group ID Important?

Specifying the security group ID ensures that the EC2 instance is assigned the correct security group, which controls the network access to the instance. This is important for security purposes.

#### How to Specify Security Group ID

You can specify the security group ID in the EC2 instance configuration. For example, in a Terraform configuration file:

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c94855ba95b798c7"
  instance_type = var.instance_type
  subnet_id     = "subnet--0123456789abcdef0"
  vpc_security_group_ids = ["sg-0123456789abcdef0"]
}
```

In this example, the `vpc_security_group_ids` attribute is set to a specific security group ID, ensuring that the EC2 instance is assigned the correct security group.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/13-Creating AWS EC2 Instance Configuration/13-Hands-On Labs|Hands-On Labs]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/13-Creating AWS EC2 Instance Configuration/00-Overview|Overview]] | [[15-Required Attributes for Launching an EC2 Instance|Required Attributes for Launching an EC2 Instance]]
