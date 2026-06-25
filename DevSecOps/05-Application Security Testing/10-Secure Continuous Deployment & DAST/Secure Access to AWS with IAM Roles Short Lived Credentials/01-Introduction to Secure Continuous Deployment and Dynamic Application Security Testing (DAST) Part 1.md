---
course: DevSecOps
topic: Secure Continuous Deployment & DAST
tags: [devsecops]
---

## Introduction to Secure Continuous Deployment and Dynamic Application Security Testing (DAST)

In the realm of DevSecOps, ensuring secure continuous deployment is paramount. This involves integrating security practices into the entire software development lifecycle, including the deployment phase. One critical aspect of this is managing secure access to cloud services, particularly Amazon Web Services (AWS), through the use of Identity and Access Management (IAM) roles and short-lived credentials.

### Understanding IAM Roles and Short-Lived Credentials

Identity and Access Management (IAM) is a service provided by AWS that enables you to manage access to your AWS resources securely. IAM roles are a type of IAM entity that defines a set of permissions. These roles can be assumed by entities such as EC2 instances, Lambda functions, or even external systems like GitLab runners.

Short-lived credentials are temporary access keys that are valid for a limited time. They are used to reduce the risk associated with long-term access keys, which can be compromised and used maliciously for extended periods.

#### Why Use IAM Roles and Short-Lived Credentials?

Using IAM roles and short-lived credentials enhances security by:

- **Reducing the risk of key exposure**: Short-lived credentials minimize the window during which an exposed key can be misused.
- **Fine-grained access control**: IAM roles allow you to define specific permissions for different entities, ensuring that each component has only the necessary access.
- **Compliance and auditability**: IAM roles and short-lived credentials help in maintaining compliance with regulatory requirements and provide better audit trails.

### Configuring IAM Roles for GitLab Runners

To ensure secure access to AWS services from GitLab runners, you need to configure IAM roles appropriately. This involves creating a role that the GitLab runner can assume and granting it the necessary permissions.

#### Step-by-Step Configuration

1. **Create an IAM Role**:
   - Navigate to the IAM console in the AWS Management Console.
   - Click on "Roles" and then "Create role".
   - Select "EC2" as the trusted entity type.
   - Attach policies that grant the required permissions. For example, `AmazonEC2ContainerRegistryFullAccess` for ECR and `AmazonSSMFullAccess` for SSM.

```mermaid
sequenceDiagram
    participant User as User
    participant IAM as IAM Console
    participant EC2 as EC2 Instance
    participant GitLabRunner as GitLab Runner
    User->>IAM: Create IAM Role
    IAM->>User: Role Created
    User->>IAM: Attach Policies
    IAM->>User: Policies Attached
    User->>EC2: Assign Role to EC2
    EC2->>GitLabRunner: Assume Role
```

2. **Assign the Role to the EC2 Instance**:
   - In the EC2 console, select the instance and attach the IAM role created in the previous step.

3. **Configure GitLab Runner**:
   - Ensure the GitLab runner is configured to assume the IAM role. This typically involves setting environment variables or configuring the runner's configuration file.

```yaml
# Example GitLab Runner Configuration
[[runners]]
  name = "My GitLab Runner"
  url = "https://gitlab.com/"
  token = "your_runner_token"
  executor = "docker"
  [runners.custom_build]
    script = "aws sts assume-role --role-arn arn:aws:iam::123456789012:role/my-role --role-session-name my-session"
```

### Full Example: Configuring IAM Roles for AWS CLI Commands

Let's walk through a complete example of configuring IAM roles for AWS CLI commands within a GitLab pipeline.

#### Creating the IAM Role

1. **Navigate to IAM Console**:
   - Go to the IAM section in the AWS Management Console.
   - Click on "Roles" and then "Create role".

2. **Select Trusted Entity Type**:
   - Choose "EC2" as the trusted entity type.

3. **Attach Policies**:
   - Search for and attach the following policies:
     - `AmazonEC2ContainerRegistryFullAccess`
     - `AmazonSSMFullAccess`

```mermaid
graph TD
    A[Create IAM Role] --> B[Select Trusted Entity Type]
    B --> C[Attach Policies]
    C --> D[Review and Create]
```

#### Assigning the Role to the EC2 Instance

1. **Navigate to EC2 Console**:
   - Go to the EC2 section in the AWS Management Console.
   - Select the instance and click on "Actions" > "Security" > "Modify IAM Role".

2. **Assign the IAM Role**:
   - Select the IAM role created earlier and save the changes.

#### Configuring GitLab Runner

1. **Edit GitLab Runner Configuration**:
   - Edit the GitLab runner configuration file to include the necessary environment variables or scripts to assume the IAM role.

```yaml
# Example GitLab Runner Configuration
[[runners]]
  name = "My GitLab Runner"
  url = "https://gitlab.com/"
  token = "your_runner_token"
  executor = "docker"
  [runners.custom_build]
    script = """
      aws sts assume-role --role-arn arn:aws:iam::1234556789012:role/my-role --role-session-name my-session
      export AWS_ACCESS_KEY_ID=$(echo $AWS_CREDENTIALS | jq -r '.Credentials.AccessKeyId')
      export AWS_SECRET_ACCESS_KEY=$(echo $AWS_CREDENTIALS | jq -r '.Credentials.SecretAccessKey')
      export AWS_SESSION_TOKEN=$(echo $AWS_CREDENTIALS | jq -r '.Credentials.SessionToken')
      aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com
      aws ssm send-command --instance-ids i-0123456789abcdef0 --document-name "AWS-RunShellScript" --parameters commands="echo Hello World"
    """
```

### Full Raw HTTP Messages and Responses

Here is an example of the full raw HTTP messages involved in assuming an IAM role and executing AWS CLI commands:

#### Request to Assume IAM Role

```http
POST /sts/assumeRole HTTP/1.1
Host: sts.amazonaws.com
Content-Type: application/x-www-form-urlencoded
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20231001/us-west-2/sts/aws4_request, SignedHeaders=content-type;host;x-amz-date, Signature=0b5c2b5d6f21f4f48a45c1f50f4f4e4c1f50f4f4e4c1f50f4f4e4c1f50f4f4e4c
X-Amz-Date: 20231001T000000Z
Content-Length: 123

Action=AssumeRole&Version=2011-06-15&RoleArn=arn:aws:iam::123456789012:role/my-role&RoleSessionName=my-session
```

#### Response to Assume IAM Role

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 1234

{
  "AssumedRoleUser": {
    "Arn": "arn:aws:sts::123456789012:assumed-role/my-role/my-session",
    "AssumedRoleId": "AROACLKIQJLMEXAMPLE:my-session"
  },
  "Credentials": {
    "AccessKeyId": "ASIAIOSFODNN7EXAMPLE",
    "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYzEXAMPLEKEY",
    "SessionToken": "AQoDYXdzEPT//////////wEXAMPLETOKEN",
    "Expiration": "2023-10-01T01:00:00Z"
  }
}
```

#### Request to Execute AWS CLI Command

```http
POST / HTTP/1.1
Host: 123456789012.dkr.ecr.us-west-2.amazonaws.com
Authorization: AWS4-HMAC-SHA256 Credential=ASIAIOSFODNN7EXAMPLE/20231001/us-west-2/sts/aws4_request, SignedHeaders=host;x-amz-date, Signature=0b5c2b5d6f21f4f48a45c1f50f4f4e4c1f50f4f4e4c1f50f4f4e4c1f50f4f4e4c
X-Amz-Date: 20231001T000000Z
Content-Length: 123

GET /v2/repositories/my-repo/tags/latest
```

#### Response to Execute AWS CLI Command

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 1234

{
  "tag": "latest",
  "digest": "sha256:exampledigest",
  "imageSizeBytes": 123456789,
  "lastUpdateTime": "2023-10-01T00:00:00Z"
}
```

### Common Pitfalls and How to Prevent Them

#### Pitfall 1: Exposing Long-Term Access Keys

**Problem**: Using long-term access keys increases the risk of unauthorized access if the keys are exposed.

**Solution**: Use short-lived credentials and rotate them frequently. Implement multi-factor authentication (MFA) for added security.

#### Pitfall 2: Overprivileged Roles

**Problem**: Assigning overly broad permissions to IAM roles can lead to unnecessary risks.

**Solution**: Follow the principle of least privilege. Grant only the minimum necessary permissions required for the task.

#### Pitfall 3: Misconfigured IAM Policies

**Problem**: Incorrectly configured IAM policies can result in either too much or too little access.

**Solution**: Regularly review and audit IAM policies. Use AWS IAM Policy Simulator to test and validate policies.

### Real-World Examples and Breaches

#### Example 1: Capital One Data Breach (CVE-2019-11510)

In 2019, Capital One suffered a data breach due to misconfigured AWS S3 buckets and IAM roles. The attacker exploited a misconfigured web application firewall rule to gain unauthorized access to sensitive data.

**Lesson Learned**: Properly configure IAM roles and policies to restrict access to only necessary resources. Regularly audit and monitor IAM configurations.

#### Example 2: Tesla Data Breach (CVE-2020-14720)

Tesla experienced a data breach in 2020 due to improperly secured AWS S3 buckets and IAM roles. The attacker gained access to sensitive internal documents and source code.

**Lesson Learned**: Implement strict access controls and regularly review IAM policies. Use encryption and secure storage practices for sensitive data.

### How to Prevent / Defend

#### Detection

- **Use AWS CloudTrail**: Monitor API calls made to AWS services to detect unauthorized access attempts.
- **Enable AWS Config**: Track changes to IAM roles and policies to identify potential misconfigurations.

#### Prevention

- **Implement Least Privilege**: Grant only the necessary permissions required for the task.
- **Rotate Credentials Regularly**: Use short-lived credentials and rotate them frequently.
- **Use Multi-Factor Authentication (MFA)**: Enable MFA for additional security.

#### Secure Coding Fixes

**Vulnerable Code**:

```yaml
# Vulnerable GitLab Runner Configuration
[[runners]]
  name = "My GitLab Runner"
  url = "https://gitlab.com/"
  token = "your_runner_token"
  executor = "docker"
  [runners.custom_build]
    script = "aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com"
```

**Fixed Code**:

```yaml
# Fixed GitLab Runner Configuration
[[runners]]
  name = "My GitLab Runner"
  url = "https://gitlab.com/"
  token = "your_runner_token"
  executor = "docker"
  [runners.custom_build]
    script = """
      aws sts assume-role --role-arn arn:aws:iam::123456789012:role/my-role --role-session-name my-session
      export AWS_ACCESS_KEY_ID=$(echo $AWS_CREDENTIALS | jq -r '.Credentials.AccessKeyId')
      export AWS_SECRET_ACCESS_KEY=$(echo $AWS_CREDENTIALS | jq -r '.Credentials.SecretAccessKey')
      export AWS_SESSION_TOKEN=$(echo $AWS_CREDENTIALS | jq -r '.Credentials.SessionToken')
      aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-west-2.amazonaws.com
    """
```

### Configuration Hardening

- **Enable IAM Access Advisor**: Monitor and review access patterns to identify unused permissions.
- **Use IAM Roles for Service Accounts (IRSA)**: Implement IRSA to provide fine-grained access control for Kubernetes pods.

### Hands-On Labs

For practical experience, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security and includes modules on IAM roles and short-lived credentials.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing security techniques.
- **CloudGoat**: Offers a series of labs to practice securing AWS environments, including IAM roles and policies.

By following these steps and best practices, you can ensure secure access to AWS services from GitLab runners, thereby enhancing the overall security of your continuous deployment pipeline.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/Secure Access to AWS with IAM Roles Short Lived Credentials/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/Secure Access to AWS with IAM Roles Short Lived Credentials/02-Introduction to Secure Continuous Deployment and Dynamic Application Security Testing (DAST)|Introduction to Secure Continuous Deployment and Dynamic Application Security Testing (DAST)]]
