---
course: DevSecOps
topic: Secure Continuous Deployment & DAST
tags: [devsecops]
---

## Secure Continuous Deployment & DAST with IAM Roles and Short-Lived Credentials

### Background Theory

In the context of DevSecOps, continuous deployment (CD) and dynamic application security testing (DAST) are critical components that ensure applications are deployed securely and tested for vulnerabilities dynamically. One of the key challenges in this process is managing secure access to cloud resources, such as Amazon Web Services (AWS), using Identity and Access Management (IAM) roles and short-lived credentials.

IAM roles provide a way to grant permissions to entities (like EC2 instances) without embedding long-term credentials in the environment. Short-lived credentials further enhance security by limiting the time window during which these credentials can be used, reducing the risk of exposure.

### Understanding IAM Roles

**What are IAM Roles?**

IAM roles are a type of AWS identity that you can use to delegate permissions to other AWS services. Instead of creating an IAM user and assigning permissions to that user, you create an IAM role and assign permissions to the role. Then, you attach the role to an entity, such as an EC2 instance, Lambda function, or ECS task.

**Why Use IAM Roles?**

Using IAM roles enhances security by:

- **Reducing the risk of credential exposure**: IAM roles eliminate the need to store long-term credentials in your environment.
- **Fine-grained access control**: IAM roles allow you to define specific permissions for different services and actions.
- **Dynamic assignment**: IAM roles can be dynamically assigned to entities at runtime, making them ideal for ephemeral environments like CI/CD pipelines.

### Short-Lived Credentials

**What are Short-Lived Credentials?**

Short-lived credentials are temporary access keys and secret keys that are valid for a limited period, typically a few hours. They are generated using AWS Security Token Service (STS) and are used to perform actions on behalf of an IAM role.

**Why Use Short-Lived Credentials?**

Using short-lived credentials enhances security by:

- **Limiting exposure time**: If credentials are compromised, they are only useful for a short period.
- **Reducing the attack surface**: Short-lived credentials reduce the window of opportunity for attackers to exploit stolen credentials.
- **Auditability**: Short-lived credentials can be easily audited and revoked if necessary.

### Example Scenario

Consider a scenario where you have a GitLab CI/CD pipeline that deploys images to an Amazon Elastic Container Registry (ECR). The pipeline runs on a shared runner, but the deployment job needs to be executed on a GitLab runner that has AWS credentials.

#### Step-by-Step Mechanics

1. **Assign IAM Role to EC2 Instance**: Assign an IAM role to the EC2 instance where the GitLab runner is running. This role should have permissions to interact with AWS services, such as ECR.

2. **Use Short-Lived Credentials**: Generate short-lived credentials using STS and use them to authenticate with AWS services.

3. **Configure GitLab CI/CD Pipeline**: Ensure that the deployment job is scheduled on the GitLab runner with AWS access.

### Detailed Configuration

#### Assigning IAM Role to EC2 Instance

To assign an IAM role to an EC2 instance, follow these steps:

1. **Create an IAM Role**: Create an IAM role with the necessary permissions. For example, if you need to push images to ECR, the role should have `AmazonEC2ContainerRegistryPowerUser` permissions.

```yaml
# IAM Role Policy Example
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",
                "ecr:PutImage"
            ],
            "Resource": "*"
        }
    ]
}
```

2. **Attach IAM Role to EC2 Instance**: Attach the IAM role to the EC2 instance where the GitLab runner is running.

```bash
# Attach IAM Role to EC2 Instance
aws ec2 associate-iam-instance-profile --instance-id i-0123456789abcdef0 --iam-instance-profile Name=MyInstanceProfile
```

#### Generating Short-Lived Credentials

To generate short-lived credentials, use the AWS Security Token Service (STS).

```bash
# Generate Short-Lived Credentials
aws sts assume-role --role-arn arn:aws:iam::123456789012:role/MyRole --role-session-name MySessionName
```

The output will include temporary access keys and secret keys.

```json
{
    "Credentials": {
        "AccessKeyId": "ASIAIOSFODNN7EXAMPLE",
        "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "SessionToken": "AQoDYXdzEJr...EXAMPLETOKEN",
        "Expiration": "2023-10-10T12:34:56Z"
    },
    "AssumedRoleUser": {
        "AssumedRoleId": "AROACLKIQJLMEXAMPLE:MySessionName",
        "Arn": "arn:aws:sts::123456789012:assumed-role/MyRole/MySessionName"
    }
}
```

#### Configuring GitLab CI/CD Pipeline

To configure the GitLab CI/CD pipeline, modify the `.gitlab-ci.yml` file to ensure the deployment job is scheduled on the GitLab runner with AWS access.

```yaml
# .gitlab-ci.yml
stages:
  - build
  - deploy

build_job:
  stage: build
  script:
    - echo "Building the application..."

deploy_job:
  stage: deploy
  script:
    - aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com
    - docker tag my-image:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/my-image:latest
    - docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/my-image:latest
  tags:
    - gitlab-runner-with-aws-access
```

### Pitfalls and Common Mistakes

1. **Hardcoding Credentials**: Avoid hardcoding AWS credentials in your CI/CD pipeline. Use IAM roles and short-lived credentials instead.
2. **Incorrect Permissions**: Ensure that the IAM role has the correct permissions to perform the required actions.
3. **Expired Credentials**: Ensure that short-lived credentials are refreshed before they expire.

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2021-44228 (Log4Shell)**: This vulnerability allowed attackers to execute arbitrary code on servers running Apache Log4j. While not directly related to IAM roles, it highlights the importance of securing access to cloud resources.
- **Capital One Data Breach (2019)**: This breach exposed sensitive data due to misconfigured IAM roles. Properly configuring IAM roles and using short-lived credentials could have mitigated this risk.

### How to Prevent / Defend

#### Detection

- **Monitor IAM Role Usage**: Use AWS CloudTrail to monitor IAM role usage and detect any unauthorized access.
- **Audit Logs**: Regularly audit logs to identify any suspicious activity.

#### Prevention

- **Least Privilege Principle**: Assign IAM roles with the minimum necessary permissions.
- **Use Short-Lived Credentials**: Generate short-lived credentials using STS to limit the exposure time.

#### Secure Coding Fixes

##### Vulnerable Code

```yaml
# Vulnerable .gitlab-ci.yml
deploy_job:
  stage: deploy
  script:
    - aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com
    - docker tag my-image:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/my-image:latest
    - docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/my-image:latest
  tags:
    - gitlab-runner-with-hardcoded-credentials
```

##### Fixed Code

```yaml
# Fixed .gitlab-ci.yml
deploy_job:
  stage: deploy
  script:
    - aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com
    - docker tag my-image:latest 123456789012.dkr.ecr.us-west-2.amazonaws.com/my-image:latest
    - docker push 123456789012.dkr.ecr.us-west-2.amazonaws.com/my-image:latest
  tags:
    - gitlab-runner-with-aws-access
```

### Hardening

- **Enable MFA**: Enable Multi-Factor Authentication (MFA) for IAM users to add an extra layer of security.
- **Use IAM Policies**: Define and enforce IAM policies to restrict access to specific resources and actions.

### Mermaid Diagrams

#### IAM Role Assignment

```mermaid
graph TD
A[GitLab Runner] --> B[EC2 Instance]
B --> C[IAM Role]
C --> D[AWS Services]
```

#### Short-Lived Credentials Generation

```mermaid
sequenceDiagram
participant GitLabRunner
participant STS
participant AWS
GitLabRunner->>STS: Request Temporary Credentials
STS-->>GitLabRunner: Provide Temporary Credentials
GitLabRunner->>AWS: Authenticate with Temporary Credentials
```

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security and includes modules on IAM roles and short-lived credentials.
- **CloudGoat**: Provides a series of labs to learn about cloud security, including IAM roles and short-lived credentials.
- **Pacu**: A penetration testing framework for AWS that includes modules for testing IAM roles and short-lived credentials.

By following these detailed steps and best practices, you can ensure that your continuous deployment and DAST processes are secure and efficient.

---
<!-- nav -->
[[04-Secure Continuous Deployment & DAST with AWS IAM Roles for Short-Lived Credentials|Secure Continuous Deployment & DAST with AWS IAM Roles for Short-Lived Credentials]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/Secure Access to AWS with IAM Roles Short Lived Credentials/00-Overview|Overview]] | [[06-Secure Continuous Deployment & DAST with IAM Roles and Short-Lived Credentials|Secure Continuous Deployment & DAST with IAM Roles and Short-Lived Credentials]]
