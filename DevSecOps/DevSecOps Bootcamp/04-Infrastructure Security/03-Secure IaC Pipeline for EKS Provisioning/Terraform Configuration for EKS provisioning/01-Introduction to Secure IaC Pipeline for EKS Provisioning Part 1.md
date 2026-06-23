---
course: DevSecOps
topic: Secure IaC Pipeline for EKS Provisioning
tags: [devsecops]
---

## Introduction to Secure IaC Pipeline for EKS Provisioning

In the realm of DevSecOps, Infrastructure as Code (IaC) plays a pivotal role in automating the deployment and management of infrastructure. One of the most popular tools for IaC is Terraform, which allows you to define your infrastructure using declarative configuration files. In this chapter, we will delve into the process of setting up a secure IaC pipeline for provisioning an Amazon Elastic Kubernetes Service (EKS) cluster using Terraform.

### Background Theory

#### What is Infrastructure as Code (IaC)?

Infrastructure as Code (IaC) is the practice of managing and provisioning computer data centers through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools. This approach allows for automation, consistency, and version control in infrastructure management.

#### Why Use IaC?

Using IaC offers several benefits:

- **Consistency**: Ensures that environments are consistently deployed and configured.
- **Automation**: Reduces manual errors and speeds up deployment processes.
- **Version Control**: Allows tracking changes to infrastructure configurations.
- **Reproducibility**: Makes it easier to replicate environments across different stages (development, testing, production).

#### What is Terraform?

Terraform is an open-source tool for building, changing, and combining infrastructure safely and efficiently. It can manage a wide range of cloud services and on-premises infrastructure, and it uses a high-level configuration language called HCL (HashiCorp Configuration Language).

### Setting Up the EKS Cluster with Terraform

To set up an EKS cluster using Terraform, you need to define the necessary resources in Terraform configuration files. These files describe the desired state of your infrastructure, and Terraform will ensure that the actual state matches the desired state.

#### Step-by-Step Process

1. **Define the Resources**:
   - Create a `main.tf` file to define the EKS cluster and related resources.
   - Define the AWS provider and specify the region.
   - Define the EKS cluster resource, including the VPC, subnets, and node groups.

2. **Initialize Terraform**:
   - Run `terraform init` to initialize the Terraform working directory.
   - This command downloads the necessary providers and modules.

3. **Plan the Changes**:
   - Run `terraform plan` to preview the changes that will be applied.
   - Review the output to ensure that the changes align with your expectations.

4. **Apply the Changes**:
   - Run `terraform apply` to apply the changes and create the EKS cluster.
   - Confirm the changes by typing `yes`.

5. **Push the Changes to the Repository**:
   - Commit the changes to the local Git repository.
   - Push the changes to the remote repository to trigger the pipeline.

### Example Terraform Configuration

Here is an example of a `main.tf` file for provisioning an EKS cluster:

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_eks_cluster" "example" {
  name     = "example-cluster"
  role_arn = aws_iam_role.example.arn

  vpc_config {
    subnet_ids = [aws_subnet.example.id]
  }
}

resource "aws_iam_role" "example" {
  name = "example-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      },
    ]
  })
}
```

### Handling Credentials in the Pipeline

When provisioning resources using Terraform, it is crucial to handle credentials securely. In the given scenario, the pipeline failed due to a lack of valid credentials for accessing the S3 bucket backend.

#### What Happened?

The error message indicates that there were no valid credential sources found for the S3 bucket backend. This means that Terraform could not access the S3 bucket to store or retrieve the state.

#### How to Fix It

To resolve this issue, you need to pass AWS credentials to the init job where the `terraform init` command gets executed. This can be done by configuring the pipeline to inject the necessary environment variables.

### Example Pipeline Configuration

Here is an example of a `.gitlab-ci.yml` file that configures the pipeline to inject AWS credentials:

```yaml
stages:
  - init
  - deploy

init_job:
  stage: init
  script:
    - echo "Initializing Terraform..."
    - terraform init
  before_script:
    - apt-get update && apt-get install -y awscli
    - aws sts get-caller-identity
  environment:
    name: development
    url: http://localhost:8080

deploy_job:
  stage: deploy
  script:
    - echo "Deploying EKS cluster..."
    - terraform apply -auto-approve
  dependencies:
    - init_job
  environment:
    name: development
    url: http://localhost:8080
```

### Full HTTP Request and Response

Here is an example of a full HTTP request and response for the `aws sts get-caller-identity` command:

```http
POST / HTTP/1.1
Host: sts.amazonaws.com
Content-Type: application/x-www-form-urlencoded
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20150101/us-east-1/sts/aws4_request, SignedHeaders=host;x-amz-date, Signature=fe5f356c9512bb22cde96b057f5226cf966f7d7e2ff97c00fc7c594f6c9c478b
X-Amz-Date: 20150101T120000Z
Content-Length: 123

Action=GetCallerIdentity&Version=2011-06-15

HTTP/1.1 200 OK
Content-Type: application/xml
Content-Length: 1234
Date: Thu, 01 Jan 2015 12:00:00 GMT

<?xml version="1.0"?>
<GetCallerIdentityResponse xmlns="https://sts.amazonaws.com/doc/2011-06-15/">
  <GetCallerIdentityResult>
    <Arn>arn:aws:iam::123456789012:user/example-user</Arn>
    <UserId>AIDA12345678901234567</UserId>
    <Account>123456789012</Account>
  </GetCallerIdentityResult>
  <ResponseMetadata>
    <RequestId>12345678-1234-1234-1234-123456789012</RequestId>
  </ResponseMetadata>
</GetCallerIdentityResponse>
```

### Mermaid Diagrams

Here is a mermaid diagram illustrating the pipeline flow:

```mermaid
graph TD
  A[Commit Changes] --> B[Push to Remote Repository]
  B --> C[Trigger Pipeline]
  C --> D[Init Job]
  D --> E[Deploy Job]
  E --> F[Deploy EKS Cluster]
```

### Common Pitfalls and How to Avoid Them

#### Pitfall: Missing Credentials

One common pitfall is forgetting to pass the necessary credentials to the pipeline jobs. This can lead to errors like the one described earlier.

#### How to Avoid It

Ensure that the pipeline configuration includes steps to inject the required environment variables. This can be done using the `before_script` section in the `.gitlab-ci.yml` file.

### Real-World Examples

#### Recent Breaches and CVEs

One recent breach involving misconfigured IaC pipelines was the Capital One data breach in 2019. The breach occurred due to a misconfigured web application firewall rule, which exposed sensitive customer data. This highlights the importance of securing IaC pipelines and ensuring that credentials are handled securely.

### How to Prevent / Defend

#### Detection

- **Monitor Logs**: Regularly monitor logs for unauthorized access attempts.
- **Use Security Tools**: Utilize security tools like AWS CloudTrail to track API calls and detect suspicious activity.

#### Prevention

- **Secure Credentials**: Ensure that credentials are stored securely and are not hardcoded in configuration files.
- **Least Privilege Principle**: Follow the least privilege principle by granting minimal permissions necessary for the pipeline to function.

#### Secure Coding Fixes

Here is an example of a vulnerable configuration and the corresponding secure configuration:

**Vulnerable Configuration**:

```yaml
init_job:
  stage: init
  script:
    - echo "Initializing Terraform..."
    - terraform init
  before_script:
    - apt-get update && apt-get install -y awscli
    - aws sts get-caller-identity
```

**Secure Configuration**:

```yaml
init_job:
  stage: init
  script:
    - echo "Initializing Terraform..."
    - terraform init
  before_script:
    - apt-get update && apt-get install -y awscli
    - aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
    - aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
    - aws sts get-caller-identity
```

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.
- **WebGoat**: An interactive, gamified training application for learning about web application security.

### Conclusion

In this chapter, we covered the process of setting up a secure IaC pipeline for provisioning an EKS cluster using Terraform. We discussed the importance of handling credentials securely and provided examples of how to configure the pipeline to inject the necessary environment variables. By following these best practices, you can ensure that your IaC pipeline is secure and reliable.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/03-Secure IaC Pipeline for EKS Provisioning/Terraform Configuration for EKS provisioning/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/03-Secure IaC Pipeline for EKS Provisioning/Terraform Configuration for EKS provisioning/02-Introduction to Secure IaC Pipeline for EKS Provisioning Part 2|Introduction to Secure IaC Pipeline for EKS Provisioning Part 2]]
