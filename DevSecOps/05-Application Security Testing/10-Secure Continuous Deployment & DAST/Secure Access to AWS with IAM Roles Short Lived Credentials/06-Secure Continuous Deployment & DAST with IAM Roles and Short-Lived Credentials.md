---
course: DevSecOps
topic: Secure Continuous Deployment & DAST
tags: [devsecops]
---

## Secure Continuous Deployment & DAST with IAM Roles and Short-Lived Credentials

### Background Theory

In the realm of DevSecOps, ensuring secure continuous deployment is paramount. One critical aspect of this is managing access to cloud resources securely. In the context of AWS, Identity and Access Management (IAM) roles play a crucial role in granting temporary, limited access to resources. This approach helps mitigate the risks associated with long-term static credentials and ensures that only the necessary permissions are granted for specific tasks.

### IAM Roles and Permissions

An IAM role is an entity that defines a set of permissions. Unlike users, roles are not associated with specific individuals but are instead assumed by entities such as EC2 instances, Lambda functions, or even external identities. When an EC2 instance assumes an IAM role, it gains the permissions defined by that role.

#### Why Use IAM Roles?

Using IAM roles provides several benefits:

1. **Least Privilege Principle**: IAM roles allow you to grant only the necessary permissions required for a task, adhering to the principle of least privilege.
2. **Temporary Credentials**: IAM roles can provide temporary credentials, reducing the risk associated with long-lived static credentials.
3. **Centralized Management**: IAM roles can be centrally managed, making it easier to update permissions across multiple resources.

### Associating IAM Roles with EC2 Instances

To associate an IAM role with an EC2 instance, you can specify the role during instance creation or attach it later using the AWS Management Console, CLI, or SDKs.

#### Example: Attaching an IAM Role to an EC2 Instance

```bash
aws ec2 run-instances --image-id ami-0c94855ba95c71c99 --count 1 --instance-type t2.micro --key-name MyKeyPair --security-group-ids sg-0123456789abcdef0 --iam-instance-profile Name=my-iam-role
```

This command creates an EC2 instance and attaches the `my-iam-role` IAM role to it.

### Permissions for Deployment

When deploying applications to EC2 instances, the IAM role associated with the EC2 instance should have the necessary permissions to perform the deployment actions. These actions might include:

- Deploying to other EC2 instances.
- Accessing Amazon Elastic Container Registry (ECR).
- Performing other necessary actions within the pipeline deployment process.

#### Example IAM Policy for Deployment

Here is an example IAM policy that grants permissions to deploy to EC2 instances and access ECR:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:RunInstances",
                "ec2:TerminateInstances"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage"
            ],
            "Resource": "*"
        }
    ]
}
```

### Using IAM Roles in GitLab CI/CD Pipelines

In a GitLab CI/CD pipeline, the GitLab Runner runs jobs on an EC2 instance. By associating an IAM role with the EC2 instance, the GitLab Runner inherits the permissions from the IAM role. This setup allows the GitLab Runner to make authenticated AWS API requests using the role credentials stored in the EC2 instance metadata.

#### Example: GitLab CI/CD Pipeline Configuration

Here is an example `.gitlab-ci.yml` configuration that uses the IAM role credentials to execute AWS SSM and ECR commands:

```yaml
stages:
  - build
  - deploy

build_job:
  stage: build
  script:
    - echo "Building the application..."
    - aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com
    - docker build -t my-app .
    - docker tag my-app:latest $AWS_ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/my-app:latest
    - docker push $AWS_ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com/my-app:latest

deploy_job:
  stage: deploy
  script:
    - echo "Deploying the application..."
    - aws ssm send-command --instance-ids i-0123456789abcdef0 --document-name "AWS-RunShellScript" --parameters '{"commands":["echo Hello World"]}'
```

### Avoiding Static Credentials in CI/CD Settings

By using IAM roles, you avoid the need to manage AWS IAM credentials within the GitLab CI/CD pipeline. This reduces the risk of exposing sensitive credentials and simplifies the management of permissions.

#### Vulnerable Pattern vs. Secure Pattern

**Vulnerable Pattern:**

```yaml
deploy_job:
  stage: deploy
  script:
    - echo "Deploying the application..."
    - export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
    - export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
    - aws ssm send-command --instance-ids i-0123456789abcdef0 --document-name "AWS-RunShellScript" --parameters '{"commands":["echo Hello World"]}'
```

**Secure Pattern:**

```yaml
deploy_job:
  stage: deploy
  script:
    - echo "Deploying the application..."
    - aws ssm send-command --instance-ids i-0123456789abcdef0 --document-name "AWS-RunShellScript" --parameters '{"commands":["echo Hello World"]}'
```

### How to Prevent / Defend

#### Detection

To detect misconfigurations or unauthorized access, you can use AWS CloudTrail and AWS Config:

- **CloudTrail**: Logs API calls made to your AWS account, including those made by the IAM role.
- **Config**: Tracks changes to your AWS resources and can alert you to unauthorized changes.

#### Prevention

- **Least Privilege**: Ensure that IAM roles have only the minimum necessary permissions.
- **Rotation**: Regularly rotate IAM roles and their associated policies.
- **Monitoring**: Set up monitoring and alerts for unusual activity.

#### Secure Coding Fixes

Ensure that your CI/CD pipelines do not hardcode any AWS credentials. Instead, rely on IAM roles and temporary credentials.

### Real-World Examples

#### Recent Breaches

One notable breach involved the exposure of AWS credentials due to insecure storage practices. By using IAM roles and short-lived credentials, such breaches can be significantly mitigated.

#### CVEs

CVE-2021-44228 (Log4j vulnerability) highlighted the importance of securing access to cloud resources. Using IAM roles and short-lived credentials can help prevent unauthorized access even if a vulnerability is exploited.

### Mermaid Diagrams

#### IAM Role Architecture

```mermaid
graph TD
    A[GitLab CI/CD Pipeline] --> B[EC2 Instance]
    B --> C[IAM Role]
    C --> D[AWS API Requests]
    D --> E[EC2 Instances]
    D --> F[Amazon ECR]
```

#### Sequence Diagram

```mermaid
sequenceDiagram
    participant GitLabCI as GitLab CI/CD Pipeline
    participant EC2Instance as EC2 Instance
    participant IAMRole as IAM Role
    participant AWSService as AWS Service

    GitLabCI->>EC2Instance: Execute Job
    EC2Instance->>IAMRole: Assume Role
    IAMRole->>AWSService: Make API Request
    AWSService-->>IAMRole: Respond
    IAMRole-->>EC2Instance: Return Response
    EC2Instance-->>GitLabCI: Job Complete
```

### Practice Labs

For hands-on practice with secure continuous deployment and IAM roles, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but includes modules on secure CI/CD pipelines.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing and secure coding practices.
- **DVWA (Damn Vulnerable Web Application)**: Another web application for learning security concepts, including secure deployment practices.

These labs provide practical experience in setting up and securing CI/CD pipelines, including the use of IAM roles and short-lived credentials.

### Conclusion

By leveraging IAM roles and short-lived credentials, you can significantly enhance the security of your continuous deployment processes. This approach ensures that only the necessary permissions are granted and reduces the risk of exposing sensitive credentials. Through careful planning, implementation, and regular monitoring, you can maintain a robust and secure DevSecOps environment.

---
<!-- nav -->
[[05-Secure Continuous Deployment & DAST with IAM Roles and Short-Lived Credentials Part 1|Secure Continuous Deployment & DAST with IAM Roles and Short-Lived Credentials Part 1]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/Secure Access to AWS with IAM Roles Short Lived Credentials/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/Secure Access to AWS with IAM Roles Short Lived Credentials/07-Secure Continuous Deployment & Dynamic Application Security Testing (DAST)|Secure Continuous Deployment & Dynamic Application Security Testing (DAST)]]
