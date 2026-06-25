---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain why creating a custom VPC is considered a best practice in Terraform deployments.**

Creating a custom VPC is considered a best practice in Terraform deployments for several reasons:

1. **Isolation**: By creating a custom VPC, you ensure that your resources are isolated from the default VPC. This isolation helps prevent conflicts with other services or resources that might exist in the default VPC.
   
2. **Control**: A custom VPC allows you to have full control over the network configuration, including subnets, route tables, and security groups. This level of control ensures that your infrastructure is tailored to your specific requirements.

3. **Scalability**: When deploying multiple servers or services, having a custom VPC allows you to scale your infrastructure more efficiently. You can create multiple subnets and configure them according to your needs, such as separating public and private subnets.

4. **Cleanup**: If you no longer need the resources, you can easily delete the entire VPC and all its components without affecting the default VPC. This makes cleanup and management easier.

**Q2. How would you configure a route table in Terraform to enable internet connectivity for a VPC?**

To configure a route table in Terraform to enable internet connectivity for a VPC, you would follow these steps:

1. **Create an Internet Gateway**: Define a resource for the internet gateway and associate it with the VPC.

```hcl
resource "aws_internet_gateway" "my_app_igw" {
  vpc_id = aws_vpc.my_app_vpc.id
  tags = {
    Name = "my_app_igw"
  }
}
```

2. **Create a Route Table**: Define a resource for the route table and associate it with the VPC.

```hcl
resource "aws_route_table" "my_app_rtb" {
  vpc_id = aws_vpc.my_app_vpc.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.my_app_igw.id
  }
  tags = {
    Name = "my_app_rtb"
  }
}
```

3. **Associate the Route Table with a Subnet**: Define a resource to associate the route table with a subnet.

```hcl
resource "aws_route_table_association" "my_app_rta" {
  subnet_id = aws_subnet.my_app_subnet.id
  route_table_id = aws_route_table.my_app_rtb.id
}
```

By following these steps, you ensure that the VPC is properly connected to the internet via the route table and internet gateway.

**Q3. Why is it important to define security groups in Terraform for EC2 instances?**

Defining security groups in Terraform for EC2 instances is important for several reasons:

1. **Network Isolation**: Security groups act as a virtual firewall for your EC2 instances, controlling inbound and outbound traffic. This helps isolate your instances from unauthorized access and ensures that only necessary traffic is allowed.

2. **Consistency**: Using Terraform to manage security groups ensures that the configurations are consistent across all environments (development, staging, production). This reduces the risk of misconfigurations and security vulnerabilities.

3. **Automation**: By defining security groups in Terraform, you automate the creation and management of these groups. This eliminates manual errors and ensures that security policies are applied consistently.

4. **Scalability**: When deploying multiple EC2 instances, security groups can be reused across instances, making it easier to manage large-scale deployments. This scalability is crucial for maintaining security as the number of instances grows.

Here is an example of how to define a security group in Terraform:

```hcl
resource "aws_security_group" "my_app_sg" {
  name        = "my_app_sg"
  description = "Allow SSH and HTTP access"
  vpc_id      = aws_vpc.my_app_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 8080
    to_port     = .8080
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

**Q4. How would you modify the Terraform configuration to use the default security group instead of creating a new one?**

To modify the Terraform configuration to use the default security group instead of creating a new one, you would follow these steps:

1. **Define the Default Security Group**: Use the `aws_default_security_group` resource type to reference the default security group associated with the VPC.

```hcl
resource "aws_default_security_group" "default_sg" {
  vpc_id = aws_vpc.my_app_vpc.id

  ingress {
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = [var.my_ip]
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

2. **Remove the Custom Security Group**: Remove the custom security group resource from your Terraform configuration.

By using the default security group, you leverage the built-in security group that AWS creates for each VPC, reducing the need to manage additional resources.

**Q5. What recent real-world examples demonstrate the importance of proper network configuration in cloud environments?**

Recent real-world examples highlight the importance of proper network configuration in cloud environments:

1. **Capital One Data Breach (2019)**: In this breach, an attacker exploited misconfigured web applications and security groups to gain unauthorized access to sensitive data. Proper network segmentation and strict security group rules could have mitigated the attack.

2. **Twitter Hack (2020)**: The hack involved unauthorized access to Twitter employees' accounts, leading to the posting of fraudulent tweets. Misconfigured IAM roles and lack of proper network isolation contributed to the breach.

3. **SolarWinds Supply Chain Attack (2020)**: This sophisticated attack involved the compromise of SolarWinds software, which was then used to infiltrate numerous organizations. Proper network segmentation and strict security policies could have limited the spread of the attack.

These examples underscore the critical importance of proper network configuration, including the use of VPCs, subnets, route tables, and security groups, to ensure robust security in cloud environments.

---
<!-- nav -->
[[16-Virtual Private Cloud (VPC)|Virtual Private Cloud (VPC)]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/08-Deploying Docker Containers on AWS EC2 with Terraform/00-Overview|Overview]]
