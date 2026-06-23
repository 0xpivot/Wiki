---
course: DevSecOps
topic: IaC and GitOps for DevSecOps
tags: [devsecops]
---

## Adding Automated Security Scans to Terraform Infrastructure Code

One of the key practices in DevSecOps is integrating security into the CI/CD pipeline. This includes adding automated security scans to the infrastructure code to ensure that the infrastructure is secure and compliant.

### Basic Syntax Validation

Before diving into security scans, it's important to ensure that the Terraform code is syntactically correct and structurally sound. This involves checking for basic integrity, such as loading modules, ensuring that variables are correctly named and referenced, and validating the basic syntax of the Terraform script files.

#### Example: Basic Syntax Validation

```terraform
# main.tf
provider "aws" {
  region = "us-west-2"
}

resource "aws_instance" "example" {
  ami           = "ami-0c94855ba95b79819"
  instance_type = "t2.micro"

  tags = {
    Name = "example-instance"
  }
}
```

To validate the syntax of the Terraform script, you can use the `terraform validate` command:

```sh
terraform validate
```

This command checks for syntax errors and configuration problems, ensuring that the overall structure of the code is correct.

### Shallow Scan Limitations

While basic syntax validation is important, it is a shallow scan that only checks for syntax and structural correctness. It does not check for security misconfigurations, which can lead to significant security risks.

#### Real-World Example: CVE-2021-21277

CVE-2021-21277 is a security vulnerability in AWS IAM policies that allows unauthorized access to sensitive resources. This vulnerability could have been detected by a deeper security scan, highlighting the importance of incorporating security scans into the CI/CD pipeline.

### Adding TFSEC for Security Scanning

To address the limitations of basic syntax validation, you can add a security scanning tool like TFSEC to your CI/CD pipeline. TFSEC is a static analysis tool specifically designed for scanning Terraform scripts for misconfigurations, including security misconfigurations.

#### Installing TFSEC

TFSEC can be installed via Docker, making it easy to integrate into CI/CD pipelines. You can find the TFSEC Docker image on Docker Hub.

```sh
docker pull hadolint/tfsec
```

#### Running TFSEC

To run TFSEC, you can use the following command:

```sh
docker run --rm -v $(pwd):/src hadolint/tfsec /src
```

This command executes TFSEC on the current directory, which contains the Terraform scripts that it should scan.

### Allowing for Failure

When integrating TFSEC into the CI/CD pipeline, it's important to allow for failure. This means that the pipeline should continue even if TFSEC detects security issues, providing additional confidence that the Terraform script or code doesn't have any critical issues.

#### Example: CI/CD Pipeline with TFSEC

Here is an example of a CI/CD pipeline that integrates TFSEC:

```yaml
name: Terraform CI/CD Pipeline

on:
  push:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v2

    - name: Install Terraform
      run: |
        wget https://releases.hashicorp.com/terraform/0.14.8/terraform_0.14.8_linux_amd64.zip
        unzip terraform_0.14.8_linux_amd64.zip
        sudo mv terraform /usr/local/bin/

    - name: Validate Terraform
      run: terraform validate

    - name: Run TFSEC
      run: docker run --rm -v $(pwd):/src hadolint/tfsec /src
      continue-on-error: true
```

This pipeline includes steps to checkout the code, install Terraform, validate the Terraform code, and run TFSEC. The `continue-on-error: true` flag ensures that the pipeline continues even if TFSEC detects security issues.

### How to Prevent / Defend

To prevent security misconfigurations in Terraform scripts, it's important to follow best practices and use secure coding techniques. Here are some key strategies:

#### Secure Coding Practices

- **Use Least Privilege Principle**: Ensure that IAM roles and policies grant only the minimum necessary permissions.
- **Avoid Hardcoding Secrets**: Use environment variables or secrets management tools like AWS Secrets Manager or HashiCorp Vault.
- **Validate Inputs**: Use input validation to ensure that user-provided inputs are safe and valid.

#### Example: Secure vs Vulnerable Code

Here is an example of a vulnerable Terraform script and its secure counterpart:

**Vulnerable Code**

```terraform
resource "aws_s3_bucket" "example" {
  bucket = "my-bucket"
  acl    = "public-read"
}
```

**Secure Code**

```terraform
resource "aws_s3_bucket" "example" {
  bucket = "my-bucket"
  acl    = "private"
}
```

The vulnerable code sets the ACL to `public-read`, which allows anyone to read the contents of the bucket. The secure code sets the ACL to `private`, which restricts access to the bucket.

### Detection and Prevention

To detect and prevent security misconfigurations, you can use tools like TFSEC and integrate them into your CI/CD pipeline. Additionally, you can use other security tools like Trivy, tfsec, or Checkov to further enhance your security posture.

#### Example: Using Trivy

Trivy is a vulnerability scanner that can be used to scan container images and dependencies for known vulnerabilities. Here is an example of how to use Trivy in a CI/CD pipeline:

```yaml
name: Container Image Security Scan

on:
  push:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v2

    - name: Build Docker image
      run: docker build -t my-image .

    - name: Run Trivy
      run: trivy image my-image
```

This pipeline includes steps to checkout the code, build a Docker image, and run Trivy to scan the image for known vulnerabilities.

### Conclusion

Integrating security into IaC and GitOps is crucial for maintaining a secure and compliant environment. By adding automated security scans to the infrastructure code, you can detect and mitigate potential security vulnerabilities. Tools like TFSEC, Trivy, and Checkov can help you achieve this goal, ensuring that your infrastructure is secure and compliant.

### Practice Labs

For hands-on experience with IaC and GitOps for DevSecOps, consider the following labs:

- **Terraform Security Lab**: Use the Terraform Security Lab provided by HashiCorp to practice securing Terraform scripts.
- **GitOps Lab**: Use the GitOps Lab provided by FluxCD to practice implementing GitOps workflows.
- **DevSecOps Lab**: Use the DevSecOps Lab provided by OWASP to practice integrating security into CI/CD pipelines.

These labs will provide you with practical experience in implementing IaC and GitOps for DevSecOps, helping you to master these essential skills.

---
<!-- nav -->
[[05-Introduction to IaC and GitOps for DevSecOps|Introduction to IaC and GitOps for DevSecOps]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/02-IaC and GitOps for DevSecOps/Add Automated Security Scan to TF Infrastructure Code/00-Overview|Overview]] | [[07-Infrastructure as Code (IaC) and GitOps for DevSecOps|Infrastructure as Code (IaC) and GitOps for DevSecOps]]
