---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Terraform and AWS Resource Creation

In this section, we delve into the process of creating AWS resources using Terraform, a powerful infrastructure-as-code (IaC) tool. We will cover the basics of Terraform, the specifics of AWS resource creation, and provide detailed examples and explanations to ensure a comprehensive understanding.

### What is Terraform?

Terraform is an open-source IaC tool developed by HashiCorp. It allows you to define and provision infrastructure in a declarative manner using a high-level configuration language called HCL (HashiCorp Configuration Language). Terraform supports a wide range of cloud providers, including AWS, Azure, Google Cloud Platform, and many others.

#### Why Use Terraform?

1. **Consistency**: Terraform ensures that your infrastructure is consistent across different environments (development, testing, production).
2. **Version Control**: You can store your Terraform configurations in version control systems like Git, making it easy to track changes and collaborate with team members.
3. **Automation**: Terraform automates the provisioning and management of infrastructure, reducing the risk of human error.
4. **Multi-Cloud Support**: Terraform supports multiple cloud providers, allowing you to manage infrastructure across different clouds seamlessly.

### AWS Resources and Terraform

In this section, we focus on creating two specific AWS resources: a Virtual Private Cloud (VPC) and a Subnet within that VPC. These resources form the foundational components of most AWS-based applications.

#### What is a VPC?

A Virtual Private Cloud (VPC) is a logically isolated virtual network within AWS. It allows you to launch AWS resources into a virtual network that you define. A VPC provides you with complete control over the IP address range, subnets, routing tables, and gateways.

#### What is a Subnet?

A subnet is a range of IP addresses in a VPC. It is used to segment the VPC into smaller networks. Each subnet is associated with a specific Availability Zone (AZ) and can be public (accessible from the internet) or private (not accessible from the internet).

### Defining Resources in Terraform

To create a VPC and a Subnet using Terraform, you need to define these resources in a `.tf` file. Let's start by defining the VPC and Subnet in a Terraform configuration file.

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_vpc" "example" {
  cidr_block = "10.0.0.0/16"

  tags = {
    Name = "example-vpc"
  }
}

resource "aws_subnet" "example" {
  vpc_id     = aws_vpc.example.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "us-west-2a"

  tags = {
    Name = "example-subnet"
  }
}
```

### Explanation of the Configuration

1. **Provider Block**:
   - The `provider` block specifies the AWS provider and the region where the resources will be created. In this example, we are using the `us-west-2` region.

2. **VPC Resource**:
   - The `aws_vpc` resource defines a VPC with a CIDR block of `10.0.0.0/16`. The `tags` block adds a tag to the VPC for easier identification.

3. **Subnet Resource**:
   - The `aws_subnet` resource defines a subnet within the previously created VPC. The `vpc_id` attribute references the VPC ID, ensuring that the subnet is created within the correct VPC. The `cidr_block` attribute defines the CIDR block for the subnet, and the `availability_zone` attribute specifies the AZ where the subnet will be located. The `tags` block adds a tag to the subnet for easier identification.

### Applying the Configuration

Once the configuration is defined, you can apply it using the `terraform apply` command. This command calculates the necessary steps to achieve the desired state and prompts you to confirm the changes.

```sh
terraform init
terraform apply
```

### Understanding the Output

When you run `terraform apply`, Terraform will display a list of actions it plans to take to achieve the desired state. Here is an example output:

```plaintext
Terraform will perform the following actions:

  # aws_subnet.example will be created
  + resource "aws_subnet" "example" {
      + arn                         = (known after apply)
      + assign_ipv6_address_on_creation = false
      + availability_zone           = "us-west-2a"
      + availability_zone_id        = (known after apply)
      + cidr_block                  = "10.0.1.0/24"
      + id                          = (known after apply)
      + ipv6_cidr_block             = (known after apply)
      + map_public_ip_on_launch     = false
      + owner_id                    = (known after apply)
      + tags                        = {
          + "Name" = "example-subnet"
        }
      + vpc_id                      = (known after apply)
    }

  # aws_vpc.example will be created
  + resource "aws_vpc" "example" {
      + arn                         = (known after apply)
      + cidr_block                  = "1 0.0.0.0/16"
      + default_network_acl_id      = (known after apply)
      + default_route_table_id      = (known after apply)
      + default_security_group_id   = (known after apply)
      + dhcp_options_id             = (known after apply)
      + enable_dns_hostnames        = (known after apply)
      + enable_dns_support          = (known after apply)
      + id                          = (known after apply)
      + instance_tenancy            = (known after apply)
      + main_route_table_id         = (known after apply)
      + owner_id                    = (known after apply)
      + tags                        = {
          + "Name" = "example-vpc"
        }
    }

Plan: 2 to add, 0 to change, 0 to destroy.

Do you want to perform these actions?
  Terraform will perform the actions described above.
  Only 'yes' will be accepted to approve.

  Enter a value: yes
```

### Understanding the Attributes

In the output, you can see the attributes of the VPC and Subnet resources. Some attributes are set by you (e.g., `cidr_block`, `availability_zone`), while others are set by AWS (e.g., `id`, `arn`). The `+` symbol indicates that these resources will be created.

### Referencing Attributes

One of the key features of Terraform is the ability to reference attributes of one resource in another. For example, you can reference the `id` of the VPC in the Subnet definition to ensure that the Subnet is created within the correct VPC.

```hcl
resource "aws_subnet" "example" {
  vpc_id     = aws_vpc.example.id
  cidr_block = "10.0.1.0/24"
  availability_zone = "us-west-2a"

  tags = {
    Name = "example-subnet"
  }
}
```

### Summary of Resources

After applying the configuration, Terraform will create two resources: a VPC and a Subnet. The VPC will have a CIDR block of `10.0.0.0/16`, and the Subnet will have a CIDR block of `10.0.1.0/24` and be located in the `us-west-2a` AZ.

### How to Prevent / Defend

#### Detection

To detect unauthorized changes to your infrastructure, you can use AWS CloudTrail, which logs API calls made to your AWS account. By monitoring CloudTrail logs, you can identify any unauthorized changes to your VPC and Subnet configurations.

#### Prevention

1. **IAM Policies**: Ensure that IAM policies are properly configured to restrict access to sensitive resources. Use least privilege principles to limit permissions to only what is necessary.
   
2. **Terraform State Locking**: Enable state locking in Terraform to prevent concurrent modifications to the state file. This helps avoid conflicts when multiple users are working on the same infrastructure.

3. **Secure Code Practices**: Follow secure coding practices when writing Terraform configurations. Avoid hardcoding sensitive information such as access keys and secret keys. Use environment variables or AWS Secrets Manager to securely store and retrieve sensitive data.

4. **Regular Audits**: Regularly audit your Terraform configurations and infrastructure to ensure compliance with security policies and best practices.

### Real-World Example: CVE-2021-3539

CVE-2021-3539 is a critical vulnerability in AWS Elastic Load Balancing (ELB) that could allow an attacker to bypass security controls and gain unauthorized access to resources. This vulnerability highlights the importance of securing your infrastructure and regularly auditing your configurations.

#### Impact

An attacker could exploit this vulnerability to bypass security groups and access resources that should be protected. This could lead to unauthorized access to sensitive data and services.

#### Mitigation

1. **Update to Latest Version**: Ensure that you are using the latest version of AWS ELB to mitigate the vulnerability.
2. **Security Groups**: Configure security groups to restrict access to only necessary resources and ports.
3. **Network ACLs**: Use Network ACLs to further restrict traffic to your VPC and Subnets.

### Conclusion

In this section, we covered the basics of creating AWS resources using Terraform. We defined a VPC and a Subnet, explained the configuration, and demonstrated how to apply the configuration. We also discussed how to prevent and defend against potential vulnerabilities and provided real-world examples to illustrate the importance of secure infrastructure management.

### Practice Labs

For hands-on practice with Terraform and AWS, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on web application security, including some that involve setting up and securing infrastructure.
- **OWASP Juice Shop**: A deliberately insecure web application for security training. While it focuses more on web app security, it can be deployed using Terraform and AWS.
- **Terraform Official Documentation**: Provides numerous examples and tutorials for setting up various AWS resources using Terraform.

By following these labs and practicing with real-world scenarios, you can gain a deeper understanding of how to effectively manage and secure your infrastructure using Terraform and AWS.

---
<!-- nav -->
[[06-Introduction to Terraform Providers and Resources|Introduction to Terraform Providers and Resources]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/06-Creating AWS Resources Using Terraform Provider/00-Overview|Overview]] | [[08-Introduction to Terraform and AWS Resource Management|Introduction to Terraform and AWS Resource Management]]
