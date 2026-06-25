---
course: DevSecOps
topic: Secure IaC Pipeline for EKS Provisioning
tags: [devsecops]
---

## Introduction to Secure Infrastructure as Code (IaC) Pipeline for EKS Provisioning

In the realm of DevSecOps, ensuring the security of your infrastructure as code (IaC) pipeline is paramount. This chapter will delve into the specifics of securing an IaC pipeline for Amazon Elastic Kubernetes Service (EKS) provisioning using Terraform. We'll cover the necessary configurations, potential vulnerabilities, and best practices to ensure your pipeline remains secure.

### Background Theory

Infrastructure as Code (IaC) is the practice of managing and provisioning computing resources through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools. Terraform is a popular IaC tool that allows you to define and provision your infrastructure using declarative configuration files.

Amazon Elastic Kubernetes Service (EKS) is a managed service that makes it easy to run Kubernetes on AWS without needing expertise in Kubernetes orchestration or the need to operate your own Kubernetes control plane. EKS supports open-source Kubernetes applications and is compatible with all Kubernetes tools.

### Static Credentials in Terraform

In the initial setup of your Terraform project, you might have used static credentials such as access keys and secret access keys from an AWS user. These credentials were necessary when executing Terraform locally. However, in a CI/CD pipeline, it's crucial to avoid using static credentials due to the inherent risks associated with their exposure.

#### Example of Static Credentials

```terraform
provider "aws" {
  region     = "us-west-2"
  access_key = "AKIAIOSFODNN7EXAMPLE"
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}
```

#### Risks of Static Credentials

Using static credentials poses several risks:

1. **Exposure**: If the credentials are stored in a version-controlled repository, they can be exposed to unauthorized users.
2. **Longevity**: Static credentials remain valid until manually revoked, increasing the window of opportunity for misuse.
3. **Auditability**: It's difficult to track who used the credentials and when, making auditing challenging.

### Dynamic Credentials in CI/CD Pipelines

To mitigate these risks, dynamic credentials should be used in CI/CD pipelines. This approach ensures that credentials are generated and used on-demand, reducing the risk of exposure and misuse.

#### Example of Dynamic Credentials in GitLab CI/CD

In GitLab CI/CD, you can use the `before_script` section to set up dynamic credentials for the GitLab runner role. Here’s how you can configure it:

```yaml
stages:
  - deploy

deploy:
  stage: deploy
  script:
    - terraform init
    - terraform apply -auto-approve
  before_script:
    - export AWS_ACCESS_KEY_ID=$(aws sts assume-role --role-arn arn:aws:iam::123456789012:role/GitLabRunnerRole --role-session-name GitLabSession --query 'Credentials.AccessKeyId' --output text)
    - export AWS_SECRET_ACCESS_KEY=$(aws sts assume-role --role-arn arn:aws:iam::123456789012:role/GitLabRunnerRole --role-session-name GitLabSession --query 'Credentials.SecretAccessKey' --output text)
    - export AWS_SESSION_TOKEN=$(aws sts assume-role --role-arn arn:aws:iam::123456789012:role/GitLabRunnerRole --role-session-name GitLabSession --query 'Credentials.SessionToken' --output text)
```

#### Explanation of the Script

- **`export AWS_ACCESS_KEY_ID`**: Sets the `AWS_ACCESS_KEY_ID` environment variable using the `aws sts assume-role` command.
- **`export AWS_SECRET_ACCESS_KEY`**: Sets the `AWS_SECRET_ACCESS_KEY` environment variable similarly.
- **`export AWS_SESSION_TOKEN`**: Sets the `AWS_SESSION_TOKEN` environment variable, which is required for temporary credentials.

### Removing Static Credentials from Terraform Configuration

Once you've set up dynamic credentials, you can remove the static credentials from your Terraform configuration files. This ensures that your Terraform project does not contain any hardcoded sensitive information.

#### Updated Terraform Configuration

```terraform
provider "aws" {
  region = "us-west-2"
}
```

### Setting Default Values for Variables

If you still need to set default values for certain variables, you can do so within your Terraform configuration. However, it's important to ensure that these values are not committed to the repository.

#### Example of Default Values

```terraform
variable "aws_access_key_id" {
  default = ""
}

variable "aws_secret_access_key" {
  default = ""
}
```

### Using Environment Variables in CI/CD Pipelines

Instead of committing the Terraform variables file (`TFVars`) to the repository, you can set the values as environment variables in the CI/CD pipeline settings. This approach ensures that sensitive information is not stored in the repository.

#### Example of Setting Environment Variables in GitLab CI/CD

In GitLab CI/CD, you can set environment variables in the project settings:

1. Navigate to **Settings > CI/CD**.
2. Scroll down to the **Variables** section.
3. Add the following variables:
   - `AWS_ACCESS_KEY_ID`
   - `AWS_SECRET_ACCESS_KEY`
   - `AWS_SESSION_TOKEN`

These variables will be available to your pipeline jobs without being stored in the repository.

### Pitfalls and Common Mistakes

1. **Hardcoding Credentials**: Avoid hardcoding credentials in your Terraform configuration files or committing them to the repository.
2. **Improper Role Permissions**: Ensure that the roles used in your CI/CD pipeline have the minimum necessary permissions.
3. **Lack of Auditing**: Implement logging and monitoring to track the usage of credentials and detect any unauthorized access.

### How to Prevent / Defend

#### Detection

- **Logging and Monitoring**: Enable CloudTrail and configure CloudWatch Logs to monitor API calls and detect any suspicious activity.
- **IAM Access Advisor**: Use IAM Access Advisor to understand which services and actions are being accessed by your roles.

#### Prevention

- **Least Privilege Principle**: Assign roles with the least privilege necessary to perform their tasks.
- **Temporary Credentials**: Use temporary credentials with limited duration to reduce the risk of exposure.

#### Secure Coding Fixes

##### Vulnerable Code

```terraform
provider "aws" {
  region     = "us-west-2"
  access_key = "AKIAIOSFODNN7EXAMPLE"
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}
```

##### Fixed Code

```terraform
provider "aws" {
  region = "us-west-2"
}
```

#### Configuration Hardening

- **IAM Policies**: Define strict IAM policies to limit the actions that can be performed by the roles used in your CI/CD pipeline.
- **Environment Variables**: Use environment variables in your CI/CD pipeline settings to manage sensitive information securely.

### Real-World Examples

#### Recent Breaches

- **Example 1**: In 2021, a company experienced a breach due to hardcoded AWS credentials in their Terraform configuration files. The attackers gained access to their AWS account and launched a series of attacks.
- **Example 2**: Another company suffered a data leak when their Terraform variables file containing sensitive information was accidentally committed to their public GitHub repository.

### Conclusion

Securing your IaC pipeline for EKS provisioning using Terraform requires careful management of credentials and adherence to best practices. By using dynamic credentials, removing static credentials from your configuration files, and setting environment variables in your CI/CD pipeline, you can significantly reduce the risk of exposure and misuse. Always ensure that your pipeline is audited and monitored to detect any unauthorized access.

### Practice Labs

For hands-on experience with securing IaC pipelines for EKS provisioning, consider the following labs:

- **PortSwigger Web Security Academy**: Offers modules on securing IaC pipelines and managing credentials.
- **OWASP Juice Shop**: Provides a vulnerable application to practice securing IaC pipelines.
- **CloudGoat**: A lab environment for practicing cloud security, including IaC pipelines.

By following these guidelines and practicing with real-world scenarios, you can ensure that your IaC pipeline remains secure and resilient against potential threats.

---
<!-- nav -->
[[04-Introduction to Secure IaC Pipeline for EKS Provisioning|Introduction to Secure IaC Pipeline for EKS Provisioning]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/03-Secure IaC Pipeline for EKS Provisioning/Terraform Configuration for EKS provisioning/00-Overview|Overview]] | [[06-Introduction to Secure Infrastructure as Code (IaC) Pipeline for EKS Provisioning|Introduction to Secure Infrastructure as Code (IaC) Pipeline for EKS Provisioning]]
