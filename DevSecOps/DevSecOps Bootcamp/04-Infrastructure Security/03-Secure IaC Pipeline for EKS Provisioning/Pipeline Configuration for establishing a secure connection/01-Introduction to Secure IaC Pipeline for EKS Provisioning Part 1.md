---
course: DevSecOps
topic: Secure IaC Pipeline for EKS Provisioning
tags: [devsecops]
---

## Introduction to Secure IaC Pipeline for EKS Provisioning

In the realm of DevSecOps, Infrastructure as Code (IaC) plays a pivotal role in automating the provisioning and management of infrastructure. One of the key challenges in this process is ensuring that the pipeline is secure, especially when dealing with sensitive resources like Amazon Elastic Kubernetes Service (EKS). This chapter will delve into the intricacies of setting up a secure IaC pipeline for EKS provisioning, focusing on the integration between GitLab CI/CD and AWS.

### Background Theory

Infrastructure as Code (IaC) is the practice of managing and provisioning computer data centers through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools. This approach allows for automation, consistency, and version control in infrastructure management. In the context of EKS, IaC can be used to define and manage Kubernetes clusters and their associated resources.

GitLab CI/CD is a powerful tool for continuous integration and continuous delivery (CI/CD). It integrates seamlessly with GitLab's version control system, allowing developers to automate the testing and deployment of applications. When combined with AWS services, GitLab CI/CD can be used to provision and manage EKS clusters securely.

### Key Concepts

#### AWS Roles and Trust Relationships

AWS Identity and Access Management (IAM) roles are a fundamental component of securing access to AWS resources. A role is an IAM entity that defines a set of permissions. Unlike users, roles are not associated with specific individuals; instead, they are assumed by entities that need temporary access to AWS resources.

A trust relationship is established between an AWS service and an IAM role. This relationship specifies which entities can assume the role and under what conditions. For example, when GitLab CI/CD assumes an AWS role, it establishes a trust relationship with AWS, indicating that GitLab is authorized to perform certain actions on behalf of the AWS account.

#### GitLab CI/CD Integration with AWS

To integrate GitLab CI/CD with AWS, several steps are required:

1. **Create an IAM Role**: Define an IAM role in AWS that has the necessary permissions to manage EKS resources.
2. **Establish Trust Relationship**: Configure the IAM role to trust GitLab CI/CD.
3. **Configure GitLab CI/CD**: Set up GitLab CI/CD to assume the IAM role and use the temporary credentials to interact with AWS.

### Detailed Steps for Secure IaC Pipeline

#### Step 1: Create an IAM Role in AWS

First, create an IAM role in AWS that has the necessary permissions to manage EKS resources. This role should be tailored to the specific actions required by GitLab CI/CD.

```yaml
# Example IAM Policy for EKS Management
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "eks:*",
                "ec2:*",
                "iam:PassRole",
                "iam:GetRole",
                "iam:ListRoles",
                "iam:ListInstanceProfiles",
                "iam:ListAttachedRolePolicies",
                "iam:ListRolePolicies",
                "iam:ListPolicyVersions",
                "iam:ListPolicies",
                "iam:ListEntitiesForPolicy",
                "iam:ListRoleTags",
                "iam:TagRole",
                "iam:UntagRole"
            ],
            "Resource": "*"
        }
    ]
}
```

#### Step 2: Establish Trust Relationship

Next, establish a trust relationship between the IAM role and GitLab CI/CD. This involves configuring the IAM role to allow GitLab CI/CD to assume the role.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        },
        {
            "Effect": "Allow",
            "Principal": {
                "AWS": "arn:aws:iam::123456789012:root"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```

In this example, `arn:aws:iam::123456789012:root` should be replaced with the ARN of the GitLab CI/CD service principal.

#### Step 3: Configure GitLab CI/CD

Finally, configure GitLab CI/CD to assume the IAM role and use the temporary credentials to interact with AWS. This involves setting up environment variables in GitLab CI/CD to store the necessary credentials.

```yaml
# .gitlab-ci.yml
stages:
  - deploy

deploy:
  stage: deploy
  script:
    - aws sts assume-role --role-arn arn:aws:iam::123456789012:role/GitLabCI --role-session-name GitLabSession
    - export AWS_ACCESS_KEY_ID=$(echo $AWS_CREDENTIALS | jq -r '.Credentials.AccessKeyId')
    - export AWS_SECRET_ACCESS_KEY=$(echo $AWS_CREDENTIALS | jq -r '.Credentials.SecretAccessKey')
    - export AWS_SESSION_TOKEN=$(echo $AWS_CREDENTIALS | jq -r '.Credentials.SessionToken')
    - kubectl apply -f ./kubernetes/deployment.yaml
```

### Mermaid Diagrams

#### Trust Relationship Diagram

```mermaid
graph TD
    A[GitLab CI/CD] -->|Assume Role| B[IAM Role]
    B -->|Temporary Credentials| C[AWS Services]
```

#### Pipeline Flow Diagram

```mermaid
graph TD
    A[Commit to Feature Branch] --> B[Rerun Pipeline]
    B --> C[Switch to Feature Branch]
    C --> D[Run Pipeline Manually]
    D --> E[Check Logs]
    E --> F[Validate Assume Role Request]
    F --> G[Use Temporary Credentials]
    G --> H[Execute Command]
```

### Real-World Examples

#### Recent Breaches and CVEs

One notable breach involving misconfigured IAM roles occurred in 2021, where an attacker gained unauthorized access to AWS resources due to a misconfigured trust relationship. This highlights the importance of properly securing IAM roles and trust relationships.

### Pitfalls and Common Mistakes

#### Misconfigured IAM Policies

One common mistake is creating overly permissive IAM policies. This can lead to unnecessary exposure of sensitive resources. To avoid this, ensure that IAM policies are least privilege, granting only the minimum permissions required.

#### Hardcoding Credentials

Another common pitfall is hardcoding AWS credentials directly into scripts or configuration files. This can lead to credential leaks and unauthorized access. Instead, use environment variables or AWS Secrets Manager to securely manage credentials.

### How to Prevent / Defend

#### Detection

To detect misconfigurations, use AWS Config and AWS Trusted Advisor. These tools can help identify and remediate issues with IAM roles and trust relationships.

#### Prevention

1. **Least Privilege Principle**: Ensure that IAM policies grant only the minimum permissions required.
2. **Environment Variables**: Use environment variables to store AWS credentials securely.
3. **Regular Audits**: Conduct regular audits of IAM roles and trust relationships to identify and remediate issues.

#### Secure Coding Fixes

##### Vulnerable Code

```yaml
# Vulnerable .gitlab-ci.yml
stages:
  - deploy

deploy:
  stage: deploy
  script:
    - aws sts assume-role --role-arn arn:aws:iam::123456789012:role/GitLabCI --role-session-name GitLabSession
    - export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
    - export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
    - kubectl apply -f ./kubernetes/deployment.yaml
```

##### Fixed Code

```yaml
# Fixed .gitlab-ci.yml
stages:
  - deploy

deploy:
  stage: deploy
  script:
    - aws sts assume-role --role-arn arn:aws:iam::123456789012:role/GitLabCI --role-session-name GitLabSession
    - export AWS_ACCESS_KEY_ID=$(echo $AWS_CREDENTIALS | jq -r '.Credentials.AccessKeyId')
    - export AWS_SECRET_ACCESS_KEY=$(echo $AWS_CREDENTIALS | jq -r '.Credentials.SecretAccessKey')
    - export AWS_SESSION_TOKEN=$(echo $AWS_CREDENTIALS | jq -r '.Credentials.SessionToken')
    - kubectl apply -f ./kubernetes/deployment.yaml
```

### Hands-On Labs

For practical experience with setting up a secure IaC pipeline for EKS provisioning, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but includes modules on secure coding practices.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **CloudGoat**: A series of labs designed to teach cloud security concepts, including IAM roles and trust relationships.

By following these detailed steps and best practices, you can ensure that your IaC pipeline for EKS provisioning is secure and robust.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/03-Secure IaC Pipeline for EKS Provisioning/Pipeline Configuration for establishing a secure connection/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/03-Secure IaC Pipeline for EKS Provisioning/Pipeline Configuration for establishing a secure connection/02-Introduction to Secure IaC Pipeline for EKS Provisioning Part 2|Introduction to Secure IaC Pipeline for EKS Provisioning Part 2]]
