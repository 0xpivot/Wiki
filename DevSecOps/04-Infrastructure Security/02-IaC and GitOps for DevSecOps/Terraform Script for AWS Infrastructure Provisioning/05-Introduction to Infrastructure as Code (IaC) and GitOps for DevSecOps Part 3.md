---
course: DevSecOps
topic: IaC and GitOps for DevSecOps
tags: [devsecops]
---

## Introduction to Infrastructure as Code (IaC) and GitOps for DevSecOps

### What is Infrastructure as Code (IaC)?

Infrastructure as Code (IaC) is a practice of managing and provisioning computer data centers through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools. This approach allows for automation, consistency, and version control in the management of infrastructure, which includes servers, storage, networking, and security policies.

#### Why Use IaC?

- **Consistency**: IaC ensures that environments are consistent across development, testing, and production stages.
- **Automation**: Automates the deployment and management of infrastructure, reducing manual errors and increasing efficiency.
- **Version Control**: Allows tracking of changes to infrastructure configurations, making it easier to revert to previous states if something goes wrong.
- **Reproducibility**: Ensures that the same environment can be recreated multiple times, which is crucial for testing and disaster recovery.

### What is GitOps?

GitOps is an operational framework that uses Git as a single source of truth for all infrastructure and application configurations. It extends the principles of IaC by incorporating continuous integration and continuous delivery (CI/CD) practices to manage infrastructure and applications.

#### Why Use GitOps?

- **Centralized Management**: All infrastructure and application configurations are stored in a Git repository, providing a centralized and auditable source of truth.
- **Automated Deployment**: Changes to the Git repository trigger automated deployment pipelines, ensuring that the live environment is always in sync with the desired state.
- **Rollback Mechanism**: Since all changes are version-controlled, rolling back to a previous state is straightforward and reliable.
- **Collaboration**: Multiple team members can collaborate on infrastructure and application configurations, with Git’s robust branching and merging capabilities.

### Example: Terraform Script for AWS Infrastructure Provisioning

Let's dive into a practical example using Terraform, a popular IaC tool, to provision AWS infrastructure.

#### Terraform Configuration

Terraform uses `.tf` files to define infrastructure resources. Here’s a basic example of a Terraform script to create an EC2 instance:

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.micro"

  tags = {
    Name = "example-instance"
  }
}
```

This script defines an AWS provider and an EC2 instance resource. The `instance_type` is set to `t2.micro`, which is a small instance type.

#### Scaling Instances

Depending on the requirements, you might need to scale the instance types. For example, if the `t2.micro` instance is not sufficient, you can change it to a larger instance type like `t2.medium`.

```hcl
resource "aws_instance" "example" {
  ami           = "ami-0c55b159cbfafe1f0"
  instance_type = "t2.medium"

  tags = {
    Name = "example-instance"
  }
}
```

By changing the `instance_type`, you can easily scale the instance size. This is one of the key benefits of IaC: you can make changes to the infrastructure configuration and apply them consistently across environments.

#### SSH Access and Tool Installation

When creating instances, you often need to SSH into them and install necessary tools. In the given context, we need to install Docker and the AWS CLI on the app server and GitLab Runner server.

##### App Server Setup

First, SSH into the app server and install Docker and the AWS CLI:

```sh
ssh -i path/to/key.pem ec2-user@<app-server-ip>
sudo yum update -y
sudo amazon-linux-extras install docker
sudo service docker start
sudo usermod -a -G docker ec2-user
sudo yum install -y awscli
```

##### GitLab Runner Server Setup

Similarly, SSH into the GitLab Runner server and install Docker, the AWS CLI, and the GitLab Runner:

```sh
ssh -i path/to/key.pem ec2-user@<gitlab-runner-ip>
sudo yum update -y
sudo amazon-linux-extras install docker
sudo service docker start
sudo usermod -a -G docker ec2-user
sudo yum install -y awscli
curl -L https://packages.gitlab.com/install/repositories/runner/gitlab-runner/script.rpm.sh | sudo bash
sudo yum install -y gitlab-runner
sudo gitlab-runner register --non-interactive \
  --url "https://gitlab.example.com/" \
  --registration-token "your-registration-token" \
  --executor "docker" \
  --description "my-runner" \
  --tag-list "docker,aws" \
  --run-untagged="true" \
  --locked="false"
```

### Mermaid Diagrams

To visualize the setup process, we can use a sequence diagram:

```mermaid
sequenceDiagram
  participant User
  participant AppServer
  participant GitLabRunnerServer
  User->>AppServer: SSH into App Server
  AppServer-->>User: Install Docker and AWS CLI
  User->>GitLabRunnerServer: SSH into GitLab Runner Server
  GitLabRunnerServer-->>User: Install Docker, AWS CLI, and GitLab Runner
  GitLabRunnerServer-->>User: Register GitLab Runner
```

### Real-World Examples and CVEs

#### Recent Breaches and CVEs

One notable breach involving misconfigured infrastructure is the Capital One data breach in 2019 (CVE-2019-11017). The breach occurred due to a misconfigured firewall rule, allowing unauthorized access to sensitive data. This highlights the importance of proper configuration management and regular audits.

#### Secure Coding Practices

To prevent such vulnerabilities, ensure that your infrastructure configurations are properly secured. For example, use IAM roles with least privilege and enable encryption for sensitive data.

### How to Prevent / Defend

#### Detection

Regularly audit your infrastructure configurations using tools like Terraform’s `terraform plan` to review proposed changes before applying them. Additionally, use security scanning tools like Trivy to check for vulnerabilities in your infrastructure.

#### Prevention

- **Use Least Privilege**: Ensure that IAM roles and permissions are configured with the minimum necessary privileges.
- **Enable Encryption**: Enable encryption for sensitive data at rest and in transit.
- **Regular Audits**: Conduct regular audits of your infrastructure configurations to identify and mitigate potential vulnerabilities.

#### Secure-Coding Fixes

Here’s an example of a vulnerable configuration and its secure counterpart:

**Vulnerable Configuration:**

```hcl
resource "aws_s3_bucket" "example" {
  bucket = "example-bucket"
  acl    = "public-read"
}
```

**Secure Configuration:**

```hcl
resource "aws_s3_bucket" "example" {
  bucket = "example-bucket"
  acl    = "private"
  server_side_encryption_configuration {
    rule {
      apply_server_side_encryption_by_default {
        sse_algorithm = "AES256"
      }
    }
  }
}
```

### Complete Example: Full HTTP Request and Response

When configuring an IAM policy, you might need to make API calls to AWS. Here’s an example of a full HTTP request and response:

**HTTP Request:**

```http
POST / HTTP/1.1
Host: iam.amazonaws.com
Content-Type: application/x-amz-json-1.1
X-Amz-Target: CreatePolicy
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20150101/us-east-1/iam/aws4_request, SignedHeaders=content-type;host;x-amz-date;x-amz-target, Signature=7f8da690eaa69f65b620e8950f20e0d35f737f8f6c70f2e4e2d905b1f1f2d5e1
X-Amz-Date: 20150101T000000Z

{
  "PolicyName": "ExamplePolicy",
  "PolicyDocument": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Action\":\"s3:*\",\"Resource\":\"*\"}]}"
}
```

**HTTP Response:**

```http
HTTP/1.1 200 OK
Content-Type: application/x-amz-json-1.1
x-amzn-RequestId: 52343cbb-ff1a-11df-80eb-1f104f111111
x-amz-id-2: 1234567890123456789012345678901234567890123456789012345678901234
Date: Thu, 01 Jan 2015 00:00:00 GMT
Content-Length: 123

{
  "Policy": {
    "PolicyName": "ExamplePolicy",
    "Arn": "arn:aws:iam::123456789012:policy/ExamplePolicy"
  }
}
```

### Practice Labs

For hands-on experience with IaC and GitOps, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but includes sections on IaC and GitOps.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: Another web application for security training.
- **WebGoat**: An interactive web application security training tool.

These labs provide practical experience in setting up and securing infrastructure using IaC and GitOps principles.

### Conclusion

In conclusion, Infrastructure as Code and GitOps are powerful practices that enhance the management and security of infrastructure. By automating and version-controlling infrastructure configurations, you can achieve consistency, reproducibility, and efficient deployment. Regular audits and secure coding practices are essential to prevent vulnerabilities and ensure the security of your infrastructure.

---
<!-- nav -->
[[04-Introduction to Infrastructure as Code (IaC) and GitOps for DevSecOps Part 2|Introduction to Infrastructure as Code (IaC) and GitOps for DevSecOps Part 2]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/02-IaC and GitOps for DevSecOps/Terraform Script for AWS Infrastructure Provisioning/00-Overview|Overview]] | [[06-Introduction to Infrastructure as Code (IaC) and GitOps for DevSecOps Part 4|Introduction to Infrastructure as Code (IaC) and GitOps for DevSecOps Part 4]]
