---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to AWS EC2 Instances and AMIs

### What is an EC2 Instance?

Amazon Elastic Compute Cloud (EC2) is a web service that provides resizable compute capacity in the cloud. At its core, an EC2 instance is a virtual server provided by Amazon Web Services (AWS). Each EC2 instance is defined by a specific hardware configuration (such as CPU, memory, storage, and networking capacity) and runs a guest operating system (OS) of your choice.

### What is an AMI?

An Amazon Machine Image (AMI) is a template used to launch an EC2 instance. An AMI contains the following components:

- **A template for the root volume** (the volume that is attached to the instance at launch)
- **Launch permissions** that control which AWS accounts can use the AMI to launch instances
- **Block device mappings** that specify the volumes to attach to the instance when it is launched

Each AMI has a unique identifier called the **AMI ID**, which starts with `ami-` followed by a unique alphanumeric string. This ID is crucial because it specifies the exact image to be used when launching an EC2 instance.

### Why Use AMIs?

AMIs provide a consistent and repeatable way to launch EC2 instances. They allow you to configure your environment once and then reuse that configuration whenever you need to launch new instances. This is particularly useful in DevOps environments where consistency and automation are key.

### AMI IDs Across Regions

One important aspect to consider is that AMI IDs can vary across different AWS regions. This means that the same AMI might have a different ID in different regions. For example, the AMI ID for the latest Amazon Linux 2 image in the US East (N. Virginia) region (`us-east-1`) might be `ami-0c94855ba95c71c99`, whereas in the EU West (London) region (`eu-west-2`), it could be `ami-0b45f77d65d7f30d7`.

### Dynamic Nature of AMI IDs

Another critical point is that AMI IDs can change over time. When a new version of an AMI is released, the ID changes. This means that if you hardcode an AMI ID in your infrastructure-as-code (IaC) scripts, you might encounter issues if the ID changes and you are using an outdated ID.

### Hardcoding vs. Dynamic Retrieval

Hardcoding an AMI ID can lead to maintenance issues and potential failures if the ID changes. Instead, it is recommended to dynamically retrieve the AMI ID from AWS programmatically. This ensures that you always use the most up-to-date and correct AMI ID.

### Using Terraform to Dynamically Retrieve AMI IDs

Terraform is an infrastructure-as-code tool that allows you to define and provision your infrastructure using declarative configuration files. One of the powerful features of Terraform is its ability to dynamically retrieve data from AWS.

#### Data Sources in Terraform

In Terraform, you can use data sources to query information from AWS. A data source is similar to a resource, but instead of creating something, it retrieves information about something that already exists.

To dynamically retrieve the AMI ID for the latest Amazon Linux 2 image, you would use the `aws_ami` data source. Here’s how you can do it:

```hcl
data "aws_ami" "latest_amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  filters     = [
    {
      name   = "name"
      values = ["amzn2-ami-hvm*"]
    }
  ]
}
```

This configuration does the following:

- **most_recent**: Set to `true` to ensure you get the most recent AMI.
- **owners**: Specifies the owner of the AMI. In this case, `"amazon"` refers to the official Amazon Linux AMIs.
- **filters**: Allows you to filter the AMIs based on specific criteria. Here, we are filtering for AMIs whose name starts with `amzn2-ami-hvm*`.

### Using the Retrieved AMI ID

Once you have retrieved the AMI ID, you can use it to launch an EC2 instance. Here’s an example of how to launch an EC2 instance using the retrieved AMI ID:

```hcl
resource "aws_instance" "example" {
  ami           = data.aws_ami.latest_amazon_linux.id
  instance_type = "t2.micro"

  tags = {
    Name = "example-instance"
  }
}
```

### Full Example with Terraform

Here is a complete example of a Terraform configuration that dynamically retrieves the latest Amazon Linux 2 AMI and launches an EC2 instance:

```hcl
provider "aws" {
  region = "us-east-1"
}

data "aws_ami" "latest_amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  filters     = [
    {
      name   = "name"
      values = ["amzn2-ami-hvm*"]
    }
  ]
}

resource "aws_instance" "example" {
  ami           = data.aws_ami.latest_amazon_linux.id
  instance_type = "t2.micro"

  tags = {
    Name = "example-instance"
  }
}
```

### How to Prevent / Defend Against AMI ID Issues

#### Detection

To detect if you are using an outdated AMI ID, you can periodically check the AMI IDs in your IaC configurations against the latest AMI IDs available in AWS. This can be done manually or through automated scripts.

#### Prevention

1. **Use Data Sources**: Always use data sources in Terraform to dynamically retrieve the latest AMI IDs.
2. **Automated Checks**: Implement automated checks to ensure that your IaC configurations are using the most up-to-date AMI IDs.
3. **Version Control**: Keep your IaC configurations in version control and review changes to ensure that AMI IDs are being updated correctly.

### Real-World Examples

#### Recent CVEs and Breaches

While AMI ID issues are not typically associated with CVEs or breaches, they can lead to operational issues if not managed properly. For example, if you are using an outdated AMI ID, you might miss out on important security patches and updates.

#### Real-World Scenarios

Consider a scenario where a company is using an outdated AMI ID for their production environment. If a new security patch is released and the AMI ID changes, the company might continue to use the old AMI ID, leading to potential security vulnerabilities.

### Conclusion

Using dynamic retrieval of AMI IDs is a best practice in DevOps and cloud infrastructure management. It ensures that you always use the most up-to-date and correct AMI IDs, reducing the risk of operational issues and ensuring that your infrastructure is secure and up-to-date.

### Practice Labs

For hands-on experience with AWS EC2 instances and AMIs, consider the following labs:

- **PortSwigger Web Security Academy**: While primarily focused on web security, this platform offers a comprehensive learning experience that includes cloud security concepts.
- **OWASP Juice Shop**: A deliberately insecure web application for security training. It can be deployed on AWS EC2 instances using AMIs.
- **CloudGoat**: A series of labs designed to help you learn AWS security best practices. It covers various aspects of AWS, including EC2 and AMIs.

These labs provide practical, real-world scenarios to reinforce your understanding of AWS EC2 instances and AMIs.

---
<!-- nav -->
[[02-Introduction to AWS EC2 Instance Configuration|Introduction to AWS EC2 Instance Configuration]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/13-Creating AWS EC2 Instance Configuration/00-Overview|Overview]] | [[04-Introduction to AWS EC2 Instances and Key Pairs|Introduction to AWS EC2 Instances and Key Pairs]]
