---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Infrastructure as Code (IaC)

### What is Infrastructure as Code?

Infrastructure as Code (IaC) is a practice of managing and provisioning computer data centers through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools. This approach allows developers and operations teams to manage infrastructure in a consistent and repeatable manner using code, which can be version-controlled, tested, and deployed automatically.

### Why Use Infrastructure as Code?

The primary benefits of IaC include:

1. **Consistency**: Ensures that environments are consistently configured across different stages (development, testing, production).
2. **Reproducibility**: Allows for the recreation of environments from scratch, ensuring that the setup is exactly the same every time.
3. **Version Control**: Enables tracking changes to infrastructure configurations, similar to how code is versioned.
4. **Automation**: Facilitates automation of infrastructure management tasks, reducing manual errors and increasing efficiency.
5. **Collaboration**: Improves collaboration among team members by providing a shared, documented view of the infrastructure.

### How Does Infrastructure as Code Work?

In IaC, infrastructure is defined using declarative configuration files. These files describe the desired state of the infrastructure, and tools like Terraform, Ansible, or CloudFormation apply these definitions to create and manage the actual infrastructure.

#### Example: Terraform Configuration

Terraform is a popular IaC tool that uses a simple, declarative language called HCL (HashiCorp Configuration Language). Here’s an example of a basic Terraform configuration file (`main.tf`) that creates an AWS S3 bucket:

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_s3_bucket" "example" {
  bucket = "my-example-bucket"
  acl    = "private"
}
```

This configuration defines an AWS provider and an S3 bucket resource. When `terraform apply` is run, Terraform will create the specified S3 bucket in the `us-west-2` region.

### Best Practices for Infrastructure as Code

One of the key best practices in IaC is to ensure that all changes to the infrastructure are made through the configuration files. This means avoiding direct manipulation of the infrastructure outside of the IaC tool.

#### Direct vs. Indirect Changes

**Direct Changes**: Making changes directly to the infrastructure bypasses the IaC tool and can lead to inconsistencies and drift between the desired state and the actual state. For example, manually creating an S3 bucket in the AWS console without updating the Terraform configuration file can cause issues when the configuration is reapplied.

**Indirect Changes**: All changes should be made through the configuration files and applied using the IaC tool. This ensures that the infrastructure remains consistent and can be easily reproduced.

### Using Terraform Apply

Terraform provides a command-line interface to manage infrastructure. The `terraform apply` command is used to apply the changes described in the configuration files.

#### Example: Applying Changes with Terraform

Consider the following scenario where we want to update the ACL of an existing S3 bucket from `private` to `public-read`.

1. **Update the Configuration File**:
   Modify the `main.tf` file to change the ACL of the S3 bucket:

   ```hcl
   provider "aws" {
     region = "us-west-2"
   }

   resource "aws_s3_bucket" "example" {
     bucket = "my-example-bucket"
     acl    = "public-read"
   }
   ```

2. **Run `terraform plan`**:
   Before applying the changes, it's a good practice to run `terraform plan` to see the proposed changes:

   ```sh
   terraform plan
   ```

   This command will output the changes that will be made, allowing you to review them before proceeding.

3. **Apply the Changes**:
   Once you have reviewed the changes, you can apply them using `terraform apply`:

   ```sh
   terraform apply
   ```

   Terraform will prompt you to confirm the changes. After confirmation, it will apply the changes to the infrastructure.

### Real-World Examples and CVEs

#### Example: AWS S3 Bucket Misconfiguration

A common issue in cloud environments is misconfigured S3 buckets, leading to unauthorized access. In 2019, a major breach occurred due to misconfigured S3 buckets, exposing sensitive data.

**Vulnerable Configuration**:
```hcl
resource "aws_s3_bucket" "example" {
  bucket = "my-sensitive-data"
  acl    = "public-read"
}
```

**Secure Configuration**:
```hcl
resource "aws_s3_bucket" "example" {
  bucket = "my-sensitive-data"
  acl    = "private"
}
```

By using IaC, such misconfigurations can be detected and prevented through automated checks and reviews.

### How to Prevent / Defend

#### Detection

1. **Automated Scanning Tools**: Use tools like AWS Trusted Advisor, AWS Security Hub, or third-party scanners like Aqua Security or Twistlock to detect misconfigurations.
2. **Continuous Integration/Continuous Deployment (CI/CD)**: Integrate IaC validation into your CI/CD pipeline to automatically check for misconfigurations before deployment.

#### Prevention

1. **Code Reviews**: Regularly review IaC code to ensure compliance with security policies.
2. **Policy Enforcement**: Use tools like Terraform modules or custom scripts to enforce security policies and prevent misconfigurations.
3. **Least Privilege Principle**: Ensure that resources are configured with the least privileges necessary to perform their function.

### Complete Example: Full Terraform Workflow

#### Initial Setup

1. **Initialize Terraform**:
   ```sh
   terraform init
   ```

2. **Plan the Changes**:
   ```sh
   terraform plan
   ```

3. **Apply the Changes**:
   ```sh
   terraform apply
   ```

#### Full HTTP Request and Response

When Terraform interacts with AWS, it sends HTTP requests to the AWS API. Here’s an example of a request and response for creating an S3 bucket:

**Request**:
```http
POST / HTTP/1.1
Host: s3.amazonaws.com
Content-Type: application/x-www-form-urlencoded
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20150101/us-west-2/s3/aws4_request, SignedHeaders=host;x-amz-content-sha256;x-amz-date, Signature=fe5f356c9d09c9b55d1985a4fc70b7c5389b8e47ddc2d7d11b74a0fd28e5c9b4
X-Amz-Date: 20150101T000000Z
X-Amz-Content-Sha256: e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
Content-Length: 123

Action=CreateBucket&Bucket=my-example-bucket&Acl=private
```

**Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/xml
Date: Thu, 01 Jan 2015 00:00:00 GMT
Server: AmazonS3
Content-Length: 0
```

### Common Pitfalls and Mistakes

1. **Manual Changes**: Avoid making manual changes to the infrastructure outside of the IaC tool.
2. **Configuration Drift**: Ensure that the actual infrastructure matches the desired state defined in the configuration files.
3. **Security Misconfigurations**: Regularly review and validate configurations to prevent security vulnerabilities.

### Conclusion

Using Terraform and other IaC tools to manage infrastructure changes through configuration files ensures consistency, reproducibility, and security. By following best practices and using automated tools, you can effectively manage and secure your infrastructure.

### Practice Labs

For hands-on experience with Terraform and AWS, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web security, including some that involve setting up and securing infrastructure.
- **AWS Official Workshops**: Provides guided workshops on various AWS services, including Terraform integration.
- **CloudGoat**: A cloud security training platform that includes exercises on securing AWS infrastructure using IaC tools.

These labs provide practical experience in managing and securing infrastructure using IaC principles and tools.

---
<!-- nav -->
[[01-Introduction to AWS Resource Tagging with Terraform|Introduction to AWS Resource Tagging with Terraform]] | [[DevOps/DevOps Bootcamp/08-Infrastructure as Code (Terraform)/13-Naming AWS Resources Using Tags With Terraform/00-Overview|Overview]] | [[03-Naming AWS Resources Using Tags With Terraform|Naming AWS Resources Using Tags With Terraform]]
