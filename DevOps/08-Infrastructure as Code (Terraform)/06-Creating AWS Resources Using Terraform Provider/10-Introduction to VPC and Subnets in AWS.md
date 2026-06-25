---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to VPC and Subnets in AWS

In the context of AWS, a Virtual Private Cloud (VPC) is a logically isolated section of the AWS Cloud where you can launch AWS resources in a virtual network that you define. A VPC allows you to have complete control over the virtual networking environment for your AWS resources, including the IP address range, subnets, routing tables, and gateways.

### What is a VPC?

A VPC is a virtual network dedicated to your AWS account. It is logically isolated from other virtual networks in the AWS Cloud. You can launch your AWS resources, such as EC2 instances, into your VPC. By default, the instances launched into your VPC have network connectivity only within the VPC; they cannot communicate with the internet unless you explicitly enable that connectivity.

#### Key Components of a VPC

- **CIDR Block**: A VPC is defined by a unique range of IP addresses, specified as a Classless Inter-Domain Routing (CIDR) block. For example, `10.0.0.0/16` defines a range of IP addresses from `10.0.0.0` to `10.0.255.255`.
- **Subnets**: Subnets are segments of the VPC's IP address range. Each subnet is associated with a specific Availability Zone (AZ) and can contain one or more EC2 instances.
- **Internet Gateway**: An Internet Gateway provides a target for the route to the internet. It enables communication between instances in a VPC and the internet.
- **Route Tables**: Route tables determine where network traffic from your subnet is directed. Each subnet is associated with a route table.
- **Network Access Control Lists (ACLs)**: Network ACLs act as a firewall for controlling traffic in and out of your subnets.
- **Security Groups**: Security groups act as a virtual firewall for your EC2 instances, controlling inbound and outbound traffic at the instance level.

### What is a Subnet?

A subnet is a range of IP addresses in a VPC. Each subnet is associated with a specific Availability Zone (AZ). Subnets allow you to segment your VPC into smaller, more manageable parts, each with its own set of rules and configurations.

#### Key Characteristics of Subnets

- **IP Address Range**: Each subnet is assigned a portion of the VPC's CIDR block. For example, a VPC with a CIDR block of `10.0.0.0/16` might have a subnet with a CIDR block of `10.0.1.0/24`.
- **Availability Zone**: Each subnet is associated with a specific AZ. This allows you to distribute your instances across multiple AZs for high availability.
- **Route Table**: Each subnet is associated with a route table that determines where network traffic is directed.
- **Network ACLs**: Each subnet can have its own network ACLs to control inbound and outbound traffic.

### Why Subnets Matter

Subnets are crucial for several reasons:

- **Isolation**: Subnets allow you to isolate different parts of your network, improving security and reducing the risk of lateral movement.
- **Scalability**: Subnets make it easier to scale your infrastructure by allowing you to add more instances or services in specific AZs.
- **Performance**: By distributing your instances across multiple AZs, you can improve performance and reduce latency.

### How Subnets Work Under the Hood

When you create a subnet, AWS allocates a portion of the VPC's IP address range to that subnet. The subnet is then associated with a specific AZ, and you can launch instances into that subnet. The instances in the subnet share the same network configuration, including route tables and network ACLs.

#### Example: Creating a VPC and Subnets

Let's walk through an example of creating a VPC and subnets using the AWS Management Console.

1. **Create a VPC**:
    - Go to the VPC dashboard in the AWS Management Console.
    - Click on "Start VPC Wizard".
    - Choose "VPC with Public and Private Subnets".
    - Enter a name for your VPC and select the region.
    - Specify the CIDR block for your VPC (e.g., `10.0.0.0/16`).
    - Specify the CIDR blocks for your public and private subnets (e.g., `10.0.1.0/24` and `10.0.2.0/24`).
    - Click "Create VPC".

2. **Launch Instances**:
    - Once your VPC and subnets are created, you can launch instances into them.
    - Go to the EC2 dashboard and click on "Launch Instance".
    - Select an AMI and configure the instance details.
    - In the "Configure Instance Details" step, select the VPC and subnet where you want to launch the instance.
    - Complete the remaining steps to launch the instance.

### Pitfalls and Common Mistakes

- **Incorrect IP Address Ranges**: Ensure that the IP address ranges for your subnets are within the VPC's CIDR block and do not overlap with other subnets.
- **Insufficient Subnets**: Having too few subnets can limit your ability to scale and isolate your network.
- **Improper Route Table Configuration**: Incorrectly configured route tables can lead to network connectivity issues.
- **Security Group Misconfiguration**: Improperly configured security groups can expose your instances to unnecessary risks.

### How to Prevent / Defend

- **Validate IP Address Ranges**: Before creating subnets, validate that the IP address ranges are within the VPC's CIDR block and do not overlap with other subnets.
- **Use Network ACLs**: Configure network ACLs to control inbound and outbound traffic at the subnet level.
- **Secure Security Groups**: Configure security groups to allow only necessary inbound and outbound traffic.
- **Monitor Network Traffic**: Use AWS CloudTrail and VPC Flow Logs to monitor network traffic and detect any unauthorized activity.

### Real-World Examples

- **CVE-2021-20225**: This vulnerability in AWS VPC allowed attackers to bypass network isolation and gain unauthorized access to resources in other subnets. To prevent this, ensure that your network ACLs and security groups are properly configured.
- **AWS Outage in 2021**: An outage in AWS affected multiple regions due to misconfigured route tables. To prevent this, regularly review and test your route tables to ensure they are correctly configured.

---
<!-- nav -->
[[09-Introduction to Terraform and Idempotency|Introduction to Terraform and Idempotency]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/06-Creating AWS Resources Using Terraform Provider/00-Overview|Overview]] | [[11-Creating AWS Resources Using Terraform Provider|Creating AWS Resources Using Terraform Provider]]
