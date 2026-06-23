---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Route Tables in AWS VPC

In the context of deploying Docker containers on AWS EC2 using Terraform, understanding the role of route tables within an Amazon Virtual Private Cloud (VPC) is crucial. A route table is a component of the VPC that determines where network traffic from your instances is directed. Each subnet in a VPC is associated with a route table, which defines the routes for the traffic leaving the subnet.

### What is a Route Table?

A route table contains a set of rules, known as routes, that are used to determine where network traffic from your instances should be directed. Each route specifies a destination CIDR block and a target, such as an internet gateway, a virtual private gateway, or another subnet within the VPC.

#### Why Route Tables Matter

Route tables are essential for controlling the flow of traffic within and out of your VPC. They ensure that traffic is routed correctly, whether it is destined for the internet, another VPC, or even another subnet within the same VPC. Without properly configured route tables, your instances may not be able to communicate with other resources as intended.

### Default Route Table

When you create a VPC, AWS automatically creates a default route table. This default route table is associated with all subnets in the VPC unless you explicitly associate them with a custom route table. The default route table typically includes a route to the internet gateway, allowing instances in the VPC to access the internet.

#### Example of Default Route Table

Consider a VPC with a default route table:

```plaintext
Destination | Target
-------------|-------
0.0.0.0/0   | igw-12345678
```

Here, `0.0.0.0/0` is the CIDR block representing all IP addresses, and `igw-12345678` is the ID of the internet gateway. This route directs all traffic to the internet gateway.

### Custom Route Tables

While the default route table is useful, you often need to create custom route tables to meet specific requirements. For instance, you might want to isolate certain subnets from the internet or route traffic to a different VPC.

#### Creating a Custom Route Table

To create a custom route table, you can use the AWS Management Console, AWS CLI, or Terraform. Here’s how you can create a custom route table using Terraform:

```hcl
resource "aws_route_table" "custom" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
}
```

This Terraform configuration creates a custom route table (`aws_route_table.custom`) and associates it with the specified VPC (`aws_vpc.main`). The route directs all traffic (`0.0.0.0/0`) to the internet gateway (`aws_internet_gateway.main`).

### Subnet Associations

Once you have created a custom route table, you need to associate it with the appropriate subnets. By default, subnets are associated with the default route table, but you can change this association to use your custom route table.

#### Associating Subnets with Route Tables

To associate a subnet with a custom route table, you can use the following Terraform configuration:

```hcl
resource "aws_route_table_association" "subnet_association" {
  subnet_id      = aws_subnet.main.id
  route_table_id = aws_route_table.custom.id
}
```

This configuration associates the specified subnet (`aws_subnet.main`) with the custom route table (`aws_route_table.custom`).

### Example Scenario

Let’s consider a scenario where you have a VPC with two subnets: one public subnet that needs internet access and one private subnet that does not. You would create two custom route tables: one for the public subnet and one for the private subnet.

#### Public Subnet Route Table

For the public subnet, you would create a route table with a route to the internet gateway:

```hcl
resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }
}

resource "aws_route_table_association" "public_subnet_association" {
  subnet_id      = aws_subnet.public.id
  route_table_id = aws_route_table.public.id
}
```

#### Private Subnet Route Table

For the private subnet, you would create a route table without a route to the internet gateway:

```hcl
resource "aws_route_table" "private" {
  vpc_id = aws_v_ pc.main.id
}

resource "aws_route_table_association" "private_subnet_association" {
  subnet_id      = aws_subnet.private.id
  route_table_id = aws_route_table.private.id
}
```

### Pitfalls and Best Practices

#### Common Mistakes

1. **Incorrect Route Configuration**: Misconfiguring routes can lead to traffic being directed to unintended destinations. Always double-check your route configurations.
2. **Default Route Table Association**: Forgetting to associate subnets with custom route tables can result in unexpected behavior. Ensure that all subnets are associated with the correct route table.
3. **Security Considerations**: Exposing subnets to the internet unnecessarily can increase the risk of security vulnerabilities. Use security groups and network ACLs to control access.

#### How to Prevent / Defend

1. **Regular Audits**: Regularly audit your route tables to ensure they are configured correctly. Use tools like AWS Config to monitor changes.
2. **Least Privilege Principle**: Apply the least privilege principle by limiting internet access to only those subnets that require it.
3. **Security Groups and Network ACLs**: Use security groups and network ACLs to control inbound and outbound traffic to your subnets.

### Real-World Examples

#### Recent Breaches

One notable breach involving misconfigured route tables occurred in 2021 when a company inadvertently exposed sensitive data due to incorrect routing. The company had configured a route table to direct traffic to an internet gateway, but failed to restrict access properly, leading to unauthorized access.

#### Secure Configuration Example

To prevent such issues, ensure that your route tables are configured securely. Here’s an example of a secure configuration:

```hcl
resource "aws_route_table" "secure" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name = "Secure Route Table"
  }
}

resource "aws_route_table_association" "secure_subnet_association" {
  subnet_id      = aws_subnet.secure.id
  route_table_id = aws_route_table.secure.id
}
```

### Conclusion

Understanding and configuring route tables correctly is essential for managing network traffic within your VPC. By creating custom route tables and associating them with the appropriate subnets, you can control the flow of traffic and ensure that your instances are accessible as needed. Always follow best practices to prevent security vulnerabilities and regularly audit your configurations.

### Practice Labs

For hands-on practice with route tables and Terraform, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a module on AWS networking and security, including route tables.
- **CloudGoat**: Provides scenarios for securing AWS infrastructure, including route table configurations.
- **AWS Official Workshops**: Includes detailed labs on setting up and configuring VPCs and route tables.

By completing these labs, you can gain practical experience in deploying Docker containers on AWS EC2 using Terraform and managing route tables effectively.

---
<!-- nav -->
[[01-Introduction to Deploying Docker Containers on AWS EC2 with Terraform|Introduction to Deploying Docker Containers on AWS EC2 with Terraform]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/08-Deploying Docker Containers on AWS EC2 with Terraform/00-Overview|Overview]] | [[03-Introduction to Security Groups in AWS EC2|Introduction to Security Groups in AWS EC2]]
