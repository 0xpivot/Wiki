---
course: DevSecOps
topic: Secure IaC Pipeline for EKS Provisioning
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Why is it important to configure a remote state storage for Terraform state in a pipeline-based workflow?**

The importance of configuring a remote state storage for Terraform state in a pipeline-based workflow lies in ensuring consistency and reliability across multiple executions. When the state is stored remotely, such as in an S3 bucket, it ensures that all pipeline runs have access to the most recent state information. This prevents issues arising from local state inconsistencies and allows multiple developers or automated processes to safely manage infrastructure without conflicts. Additionally, remote state storage enhances collaboration and auditability, as everyone works with the same, centralized state data.

**Q2. How would you configure an S3 bucket as a remote state storage for a Terraform project in an AWS environment?**

To configure an S3 bucket as a remote state storage for a Terraform project in an AWS environment, follow these steps:

1. **Create an S3 Bucket**: Ensure the bucket name is unique and accessible from your AWS region.
2. **Configure the Backend**: In your `main.tf` file, add the backend configuration pointing to the S3 bucket:

```hcl
terraform {
  backend "s3" {
    bucket = "<unique-bucket-name>"
    key    = "infra/state.tfstate"
    region = "<aws-region>"
  }
}
```

3. **Initialize Terraform**: Run `terraform init` to initialize the backend configuration.

4. **Ensure IAM Permissions**: Make sure the IAM role or user running the Terraform commands has permissions to read/write to the S3 bucket.

**Q3. Explain how to set up a GitLab pipeline to execute Terraform commands and provision an EKS cluster on AWS.**

Setting up a GitLab pipeline to execute Terraform commands and provision an EKS cluster on AWS involves several steps:

1. **Define Pipeline Stages**: Typically, you'll have stages like `init`, `build`, and `deploy`.

2. **Init Stage**: Initialize Terraform and download necessary providers.

```yaml
stages:
  - init
  - build
  - deploy

init:
  stage: init
  image: hashicorp/terraform:latest
  script:
    - terraform init
  artifacts:
    paths:
      - .terraform/
```

3. **Build Stage**: Plan the infrastructure changes.

```yaml
build:
  stage: build
  image: hashicorp/terraform:latest
  before_script:
    - pip3 install awscli --upgrade --user
    - aws sts get-caller-identity
  script:
    - terraform plan -out=plan.out
  artifacts:
    paths:
      - plan.out
```

4. **Deploy Stage**: Apply the planned changes.

```yaml
deploy:
  stage: deploy
  image: hashicorp/terraform:latest
  before_script:
    - pip3 install awscli --upgrade --user
    - aws sts get-caller-identity
  script:
    - terraform apply plan.out
```

5. **Environment Variables**: Set necessary environment variables like AWS credentials in GitLab CI/CD settings.

**Q4. What are the advantages and disadvantages of using a specific tag for Docker images in a CI/CD pipeline?**

Advantages of using a specific tag for Docker images in a CI/CD pipeline include:

- **Predictability**: Using a specific tag ensures that the exact same version of the image is used every time, reducing the risk of unexpected behavior due to changes in the image.
- **Reproducibility**: Specific tags allow for precise replication of builds and deployments, which is crucial for debugging and auditing purposes.
- **Control**: Developers have control over when to upgrade to a newer version of the image, allowing for proper testing and validation before deployment.

Disadvantages include:

- **Maintenance Overhead**: Regularly updating the tag to the latest version requires ongoing maintenance to ensure that the pipeline uses the most recent and secure versions of the image.
- **Potential Security Risks**: If the specific tag is not updated frequently, it might miss critical security patches and updates.

**Q5. How would you handle AWS credentials in a GitLab pipeline to avoid hardcoding them in the Terraform configuration files?**

To handle AWS credentials in a GitLab pipeline without hardcoding them in Terraform configuration files, follow these steps:

1. **Use Environment Variables**: Store AWS credentials as environment variables in GitLab CI/CD settings.

```yaml
variables:
  AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID
  AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY
```

2. **Set Environment Variables in Pipeline**: Use these environment variables in the pipeline jobs to authenticate with AWS.

```yaml
before_script:
  - pip3 install awscli --upgrade --user
  - aws sts get-caller-identity
```

3. **Remove Static Credentials from Terraform**: Remove any hardcoded credentials from the Terraform configuration files.

```hcl
provider "aws" {
  region = "<aws-region>"
}
```

By using environment variables, you ensure that sensitive credentials are not exposed in the source code and are securely managed within the GitLab CI/CD environment.

---
<!-- nav -->
[[16-Terraform Configuration for EKS Provisioning|Terraform Configuration for EKS Provisioning]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/03-Secure IaC Pipeline for EKS Provisioning/Terraform Configuration for EKS provisioning/00-Overview|Overview]]
