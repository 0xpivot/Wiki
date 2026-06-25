---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Automating VPC and Subnet Creation

### What is a VPC?

A Virtual Private Cloud (VPC) is a virtual network dedicated to your AWS account. It is logically isolated from other virtual networks in the AWS Cloud. A VPC enables you to have complete control over your virtual networking environment, including selection of IP address range, creation of subnets, and configuration of route tables and network gateways.

### Why Automate VPC and Subnet Creation?

Automating the creation of VPCs and subnets ensures consistency and reduces the risk of manual errors. It also allows you to quickly spin up new environments for testing or production purposes.

### Creating a VPC Using boto3

Here’s an example of how to create a VPC using `boto3`:

```python
import boto3

# Create an EC2 client
ec2 = boto3.client('ec2')

# Create a VPC
vpc_response = ec2.create_vpc(CidrBlock='10.0.0.0/16')
vpc_id = vpc_response['Vpc']['VpcId']

print(f"Created VPC with ID: {vpc_id}")
```

### Creating Subnets Within a VPC

Once the VPC is created, you can create subnets within it:

```python
# Create a subnet
subnet_response = ec2.create_subnet(
    CidrBlock='10.0.1.0/24',
    VpcId=vpc_id,
    AvailabilityZone='us-west-2a'
)
subnet_id = subnet_response['Subnet']['SubnetId']

print(f"Created Subnet with ID: {subnet_id}")
```

### Common Pitfalls and How to Avoid Them

1. **CIDR Block Overlap**: Ensure that the CIDR blocks for your VPC and subnets do not overlap. Overlapping CIDR blocks can cause routing conflicts.
2. **Availability Zone Selection**: Choose availability zones wisely. Ensure that the availability zones you select are appropriate for your use case.
3. **Network ACLs and Security Groups**: Configure Network ACLs and Security Groups to control traffic flow within your VPC.

### How to Prevent / Defend

1. **Use IAM Roles**: Use IAM roles to grant permissions to your VPC and subnet creation scripts. This ensures that the scripts run with the minimum necessary privileges.
2. **Enable VPC Flow Logs**: Enable VPC flow logs to monitor traffic within your VPC. This helps in detecting unauthorized access and troubleshooting network issues.
3. **Regular Audits**: Regularly audit your VPC configurations to ensure that they comply with your organization's security policies.

---
<!-- nav -->
[[01-Introduction to Python Automation for DevOps Use Cases|Introduction to Python Automation for DevOps Use Cases]] | [[DevOps/DevOps Bootcamp/03-Python & Scripting/13-Python Automation for DevOps Use Cases/00-Overview|Overview]] | [[03-Comparing boto3 with Terraform|Comparing boto3 with Terraform]]
