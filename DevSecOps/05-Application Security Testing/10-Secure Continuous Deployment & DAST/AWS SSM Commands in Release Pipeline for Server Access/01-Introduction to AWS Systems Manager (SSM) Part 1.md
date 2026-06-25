---
course: DevSecOps
topic: Secure Continuous Deployment & DAST
tags: [devsecops]
---

## Introduction to AWS Systems Manager (SSM)

AWS Systems Manager (SSM) is a powerful tool that helps you manage your Amazon EC2 instances at scale. It provides a suite of capabilities that enable you to automate tasks, maintain compliance, and troubleshoot issues across your fleet of instances. One of the key features of SSM is the ability to run commands on your instances using the `aws ssm send-command` command. This allows you to execute shell scripts or commands remotely, making it easier to perform maintenance tasks, deploy updates, or troubleshoot issues.

### Instance Identification in SSM

In SSM, you can identify instances using various methods:

- **Instance ID**: A unique identifier assigned to each EC2 instance.
- **Target**: Can be the name of the instance or a key-value pair tag associated with the instance.

For example, if you have an instance with the ID `i-0123456789abcdef0`, you can specify it directly in the command. Alternatively, if you have tagged your instances with a specific tag, such as `Environment=Production`, you can use this tag to target multiple instances at once.

### Document Name

The document name specifies the type of command you want to execute. In the context of SSM, a document is essentially a template that defines the actions to be performed. For example, the document `AWS-RunShellScript` is used to run shell scripts on your instances.

### Parameters

Parameters are the actual commands or shell scripts that you want to execute on the instances. These can range from simple commands like `echo "Hello World"` to complex shell scripts that perform various operations.

### Example Command

Here is an example of how you might use the `aws ssm send-command` command to execute a shell script on an instance:

```bash
aws ssm send-command \
    --instance-ids i-0123456789abcdef0 \
    --document-name "AWS-RunShellScript" \
    --parameters '{"commands":["echo \"Hello World\""]}' \
    --comment "Test command"
```

### Authentication and Authorization

When using the AWS CLI, the commands are authenticated using the access keys defined as environment variables. These keys are typically associated with a specific user, such as a GitLab user in this case. The authentication process ensures that the user is who they claim to be.

However, authentication alone is not enough. Once the user is authenticated, AWS checks whether the user is authorized to perform the requested action. This is done through IAM policies and roles. For example, if you are trying to access the Elastic Container Registry (ECR) or the Systems Manager (SSM) service, the user must have the appropriate permissions.

### IAM Policies and Roles

IAM policies define the permissions that are granted to users, groups, or roles. For example, to allow a user to execute commands using SSM, you would need to attach a policy that grants the necessary permissions. Here is an example of an IAM policy that allows a user to execute commands using SSM:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ssm:SendCommand",
                "ssm:GetCommandInvocation"
            ],
            "Resource": "*"
        }
    ]
}
```

This policy allows the user to send commands and get command invocations using SSM.

### Secure Continuous Deployment

Continuous deployment is a practice where code changes are automatically deployed to production after passing through a series of automated tests. In a DevSecOps environment, it is crucial to ensure that the deployment process is secure. This includes ensuring that the commands being executed on the instances are secure and that the users executing these commands are properly authenticated and authorized.

### Real-World Examples

#### CVE-2021-20225

CVE-2021-20225 is a vulnerability in AWS SSM that allows unauthorized access to instances. This vulnerability arises due to misconfigured IAM policies that grant excessive permissions to users. To prevent this, it is important to follow the principle of least privilege and ensure that IAM policies are tightly controlled.

#### Breach Example: Capital One Data Breach

The Capital One data breach in 2019 was caused by a misconfigured web application firewall (WAF) that allowed an attacker to access sensitive data. While this breach did not involve SSM directly, it highlights the importance of securing all aspects of your infrastructure, including the tools used for deployment and management.

### How to Prevent / Defend

#### Detection

To detect unauthorized access or misuse of SSM, you can use AWS CloudTrail to log all API calls made to SSM. This allows you to monitor and audit the usage of SSM and identify any suspicious activity.

#### Prevention

To prevent unauthorized access, ensure that IAM policies are tightly controlled and follow the principle of least privilege. Only grant the minimum permissions required to perform the necessary tasks.

#### Secure Coding Fixes

Here is an example of a vulnerable IAM policy and its secure counterpart:

**Vulnerable Policy:**

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "*",
            "Resource": "*"
        }
    ]
}
```

**Secure Policy:**

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ssm:SendCommand",
                "ssm:GetCommandInvocation"
            ],
            "Resource": "*"
        }
    ]
}
```

### Complete Example

Here is a complete example of how you might use SSM to execute a shell script on an instance, including the full HTTP request and response:

#### Full HTTP Request

```http
POST / HTTP/1.1
Host: ssm.us-west-2.amazonaws.com
Content-Type: application/x-amz-json-1.1
X-Amz-Target: AmazonSSM.SendCommand
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20230401/us-west-2/ssm/aws4_request, SignedHeaders=content-type;host;x-amz-date;x-amz-target, Signature=0b5d4c5f2c60b78a4f020a5d9b2d7b5c0b5d4c5f2c60b78a4f020a5d9b2d7b5c
X-Amz-Date: 20230401T000000Z

{
    "DocumentName": "AWS-RunShellScript",
    "InstanceIds": ["i-0123456789abcdef0"],
    "Parameters": {
        "commands": ["echo \"Hello World\""]
    },
    "Comment": "Test command"
}
```

#### Full HTTP Response

```http
HTTP/1.1 200 OK
Content-Type: application/x-amz-json-1.1
Content-Length: 157
Date: Mon, 01 Apr 2023 00:00:00 GMT

{
    "Command": {
        "CommandId": "d-1234567890abcdef0",
        "DocumentName": "AWS-RunShellScript",
        "InstanceIds": ["i-0123456789abcdef0"],
        "Parameters": {
            "commands": ["echo \"Hello World\""]
        },
        "Comment": "Test command"
    }
}
```

### Mermaid Diagrams

#### Sequence Diagram

```mermaid
sequenceDiagram
    participant User
    participant GitLab
    participant AWSCLI
    participant SSM
    participant EC2Instance

    User->>GitLab: Trigger deployment
    GitLab->>AWSCLI: Execute command
    AWSCLI->>SSM: Send command
    SSM->>EC2Instance: Execute command
    EC2Instance-->>SSM: Return result
    SSM-->>AWSCLI: Return result
    AWSCLI-->>GitLab: Return result
    GitLab-->>User: Deployment complete
```

### Hands-On Labs

For hands-on practice with AWS SSM and secure continuous deployment, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web security and secure coding practices.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **CloudGoat**: A set of labs designed to help you understand and mitigate common cloud security issues.

These labs provide practical experience in securing your deployment pipeline and managing your instances securely.

### Conclusion

In conclusion, using AWS SSM to execute commands on your instances is a powerful tool that can greatly enhance your DevSecOps practices. By understanding the concepts of instance identification, document names, parameters, and authentication and authorization, you can effectively manage your instances and ensure that your deployment process is secure. Always follow best practices for secure coding and regularly review and update your IAM policies to ensure that your infrastructure remains secure.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/AWS SSM Commands in Release Pipeline for Server Access/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/AWS SSM Commands in Release Pipeline for Server Access/02-Introduction to AWS Systems Manager (SSM)|Introduction to AWS Systems Manager (SSM)]]
