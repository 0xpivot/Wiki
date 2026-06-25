---
course: DevSecOps
topic: IaC and GitOps for DevSecOps
tags: [devsecops]
---

## Introduction to Infrastructure as Code (IaC) and GitOps

### What is Infrastructure as Code (IaC)?

Infrastructure as Code (IaC) is a practice where infrastructure is managed and provisioned through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools. This approach allows developers and operations teams to manage infrastructure in a consistent and repeatable manner using version control systems like Git.

### Why Use IaC?

Using IaC offers several benefits:

1. **Consistency**: Ensures that environments are consistently configured across different stages (development, testing, production).
2. **Reproducibility**: Allows for the recreation of environments at any time, which is crucial for disaster recovery and testing.
3. **Version Control**: Enables tracking changes to infrastructure configurations, making it easier to roll back to previous states if something goes wrong.
4. **Automation**: Facilitates automation of infrastructure provisioning and management, reducing manual errors and improving efficiency.

### How Does IaC Work?

In IaC, infrastructure is defined using declarative configuration files. These files describe the desired state of the infrastructure. Tools like Terraform read these configuration files and apply the necessary changes to achieve the desired state.

### Example: Terraform Configuration

Here’s an example of a simple Terraform configuration file (`main.tf`):

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_instance" "example" {
  ami           = "ami-0c94855ba95b798c7"
  instance_type = "t2.micro"

  tags = {
    Name = "example-instance"
  }
}
```

This configuration defines an AWS provider and an EC2 instance resource. Terraform will create the specified EC2 instance in the `us-west-2` region.

### GitOps

GitOps is a set of practices that extends IaC by using Git as a single source of truth for all infrastructure and application configurations. This approach leverages Git's features such as pull requests, branches, and merge strategies to manage infrastructure changes.

### Benefits of GitOps

1. **Auditability**: Every change to the infrastructure is tracked via Git commit history.
2. **Collaboration**: Multiple team members can review and approve changes through pull requests.
3. **Rollback Mechanism**: Easily roll back to previous versions if something goes wrong.
4. **Automated Deployment**: Continuous Integration/Continuous Deployment (CI/CD) pipelines can automatically deploy changes based on Git commits.

### Example: GitOps Workflow

A typical GitOps workflow involves the following steps:

1. **Define Infrastructure in Code**: Write Terraform configuration files.
2. **Commit Changes to Git**: Push the configuration files to a Git repository.
3. **Trigger CI/CD Pipeline**: A CI/CD pipeline is triggered by a Git commit.
4. **Apply Changes**: The pipeline uses Terraform to apply the changes described in the configuration files.

### Remote State Management in Terraform

Remote state management is a critical aspect of Terraform that enables multiple users and workflows to access and modify the same infrastructure state. By default, Terraform stores state information locally in a file named `terraform.tfstate`. However, for collaborative environments, remote state storage is preferred.

### Why Use Remote State?

1. **Collaboration**: Multiple users can work on the same infrastructure without conflicts.
2. **State Sharing**: Allows sharing state across different environments and teams.
3. **Backup and Recovery**: Provides a centralized location for backup and recovery of state data.

### Configuring Remote State in Terraform

To configure remote state in Terraform, you need to specify a backend configuration. Terraform supports various backends, including S3, Consul, and more. Here, we’ll focus on using S3 as the backend.

#### Step-by-Step Guide to Configure Remote State

1. **Create an S3 Bucket**:
   - Ensure the bucket is in the same region as your infrastructure.
   - Enable versioning on the bucket to maintain historical state.

2. **Configure Terraform Backend**:
   - Add a `backend` block to your Terraform configuration.

Here’s an example of a Terraform configuration file with a remote state backend:

```hcl
terraform {
  backend "s3" {
    bucket = "my-tf-state-bucket"
    key    = "path/to/state/terraform.tfstate"
    region = "us-west-2"
  }
}
```

3. **Initialize Terraform**:
   - Run `terraform init` to initialize the backend.

```bash
terraform init
```

4. **Apply Changes**:
   - Run `terraform apply` to apply the configuration and store the state in the S3 bucket.

```bash
terraform apply
```

### Full Example: Terraform Configuration with Remote State

Let’s walk through a complete example of setting up Terraform with remote state using S3.

#### Step 1: Create an S3 Bucket

First, create an S3 bucket in the AWS console or using the AWS CLI:

```bash
aws s3api create-bucket --bucket my-tf-state-bucket --region us-west-2 --create-bucket-configuration LocationConstraint=us-west-2
```

Enable versioning on the bucket:

```bash
aws s3api put-bucket-versioning --bucket my-tf-state-bucket --versioning-configuration Status=Enabled
```

#### Step 2: Define Terraform Configuration

Create a directory structure for your Terraform project:

```
my-project/
├── main.tf
└── backend.tf
```

Add the following content to `main.tf`:

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_instance" "example" {
  ami           = "ami-0c94855ba95b798c7"
  instance_type = "t2.micro"

  tags = {
    Name = "example-instance"
  }
}
```

Add the following content to `backend.tf`:

```hcl
terraform {
  backend "s3" {
    bucket = "my-tf-state-bucket"
    key    = "path/to/state/terraform.tfstate"
    region = "us-west-2"
  }
}
```

#### Step 3: Initialize Terraform

Run the following command to initialize Terraform:

```bash
terraform init -backend-config="bucket=my-tf-state-bucket" -backend-config="key=path/to/state/terraform.tfstate" -backend-config="region=us-west-2"
```

#### Step 4: Apply Changes

Run the following command to apply the configuration:

```bash
terraform apply
```

### Mermaid Diagram: Terraform Workflow with Remote State

```mermaid
graph TD
    A[Create S3 Bucket] --> B[Enable Versioning]
    B --> C[Define Terraform Configuration]
    C --> D[Initialize Terraform]
    D --> E[Apply Changes]
    E --> F[Store State in S3]
```

### Common Pitfalls and Best Practices

#### Common Pitfalls

1. **Incorrect Permissions**: Ensure that the IAM role or user has the necessary permissions to read/write to the S3 bucket.
2. **Bucket Region Mismatch**: Ensure the S3 bucket and the infrastructure are in the same region to avoid latency issues.
3. **State Locking**: Use state locking mechanisms to prevent concurrent modifications.

#### Best Practices

1. **Use Versioning**: Enable versioning on the S3 bucket to maintain historical state.
2. **Secure Access**: Use IAM roles and policies to restrict access to the S3 bucket.
3. **Regular Backups**: Regularly back up the S3 bucket to prevent data loss.

### Real-World Examples and CVEs

#### Example: CVE-2021-21277

CVE-2021-21277 is a vulnerability in Terraform that allows unauthorized access to remote state storage. This vulnerability highlights the importance of securing remote state storage.

#### Secure Configuration Example

Here’s how to secure the S3 bucket used for remote state storage:

1. **IAM Policy**:
   - Create an IAM policy that grants read/write access to the S3 bucket.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject",
                "s3:PutObject",
                "s3:DeleteObject",
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::my-tf-state-bucket",
                "arn:aws:s3:::my-tf-state-b_ucket/*"
            ]
        }
    ]
}
```

2. **Attach Policy to IAM Role/User**:
   - Attach the policy to the IAM role or user used by Terraform.

### How to Prevent / Defend

#### Detection

1. **Monitor S3 Bucket Access**: Use AWS CloudTrail to monitor access to the S3 bucket.
2. **Audit Logs**: Regularly audit logs to detect unauthorized access attempts.

#### Prevention

1. **IAM Policies**: Use strict IAM policies to limit access to the S3 bucket.
2. **Encryption**: Enable server-side encryption on the S3 bucket to protect data at rest.

#### Secure-Coding Fixes

Compare the insecure and secure configurations:

**Insecure Configuration**:

```hcl
terraform {
  backend "s3" {
    bucket = "my-tf-state-bucket"
    key    = "path/to/state/terraform.tfstate"
    region = "us-west-2"
  }
}
```

**Secure Configuration**:

```hcl
terraform {
  backend "s3" {
    bucket = "my-tf-state-bucket"
    key    = "path/to/state/terraform.tfstate"
    region = "us-west-2"
    encrypt = true
  }
}
```

### Complete Example: Full HTTP Request and Response

When initializing Terraform with remote state, the following HTTP request and response might occur:

**HTTP Request**:

```http
PUT /my-tf-state-bucket/path/to/state/terraform.tfstate?versionId=1234567890abcdef1234567890abcdef HTTP/1.1
Host: my-tf-state-bucket.s3.amazonaws.com
Content-Length: 1234
Content-Type: application/octet-stream
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20230401/us-west-2/s3/aws4_request, SignedHeaders=content-type;host;x-amz-content-sha256;x-amz-date, Signature=0b5d6d7c9e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5

---
<!-- nav -->
[[02-Introduction to Infrastructure as Code (IaC) and GitOps Part 2|Introduction to Infrastructure as Code (IaC) and GitOps Part 2]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/02-IaC and GitOps for DevSecOps/Configure Remote State for Terraform/00-Overview|Overview]] | [[04-Introduction to Infrastructure as Code (IaC) and GitOps|Introduction to Infrastructure as Code (IaC) and GitOps]]
