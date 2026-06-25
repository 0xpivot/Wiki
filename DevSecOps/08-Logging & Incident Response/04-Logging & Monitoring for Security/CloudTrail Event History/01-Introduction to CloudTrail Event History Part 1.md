---
course: DevSecOps
topic: Logging & Monitoring for Security
tags: [devsecops]
---

## Introduction to CloudTrail Event History

CloudTrail is a vital service provided by Amazon Web Services (AWS) that enables you to monitor and record API calls made within your AWS environment. By logging these events, CloudTrail provides a detailed history of actions taken by users, roles, and services within your AWS account. This information is crucial for auditing, compliance, and security purposes. In this chapter, we will delve into the specifics of CloudTrail Event History, focusing on how it records and tracks various activities, particularly those related to AWS Systems Manager (SSM) commands and EC2 instances.

### Background Theory

Before diving into the specifics, let's understand the foundational concepts:

#### What is CloudTrail?

CloudTrail is a service that captures API calls made to your AWS account and delivers log files to an Amazon S3 bucket. These logs provide a comprehensive record of who performed an action, when it was done, and from which IP address. CloudTrail supports both global and regional services, allowing you to track actions across different regions.

#### Why Use CloudTrail?

1. **Auditing**: CloudTrail helps in maintaining a detailed audit trail of all actions performed in your AWS environment. This is essential for compliance with regulatory requirements such as PCI DSS, HIPAA, and GDPR.
   
2. **Security**: By monitoring API calls, you can detect unauthorized or suspicious activity. This is particularly useful in identifying potential security breaches or insider threats.

3. **Troubleshooting**: CloudTrail logs can help in diagnosing issues by providing a historical record of actions taken. This can be invaluable when trying to understand the sequence of events leading up to a problem.

4. **Compliance**: Many industries require detailed logging and auditing capabilities. CloudTrail ensures that you meet these requirements by providing a comprehensive log of all actions.

### Recording SSM Commands and EC2 Instance Actions

In the context of the lecture, we will focus on how CloudTrail records actions related to AWS Systems Manager (SSM) commands and EC2 instances.

#### AWS Systems Manager (SSM)

AWS Systems Manager (SSM) is a service that helps you manage your AWS resources efficiently. It includes features like Run Command, State Manager, Inventory, and more. One of the key functionalities of SSM is the ability to run commands on managed instances, such as EC2 instances.

#### Recording SSM Commands

When you execute an SSM command, CloudTrail records the event. This includes details such as the user who initiated the command, the target EC2 instance, and the status of the command.

```mermaid
sequenceDiagram
    participant User
    participant CloudTrail
    participant SSM
    participant EC2

    User->>SSM: Execute SSM Command
    SSM->>EC2: Send Command to EC2 Instance
    EC2-->>SSM: Command Execution Status
    SSM-->>CloudTrail: Record Event
```

### Example: Pipeline Execution of SSM Command

Let's consider a scenario where a pipeline executes an SSM command to perform an action on an EC2 instance. Here’s how the process works:

1. **Pipeline Execution**: A pipeline (e.g., CodePipeline) triggers an SSM command.
2. **Command Sent**: The SSM service sends the command to the specified EC2 instance.
3. **Event Recorded**: CloudTrail records the event, capturing details such as the user, the EC2 instance ID, and the status of the command.

#### Raw HTTP Request and Response

Here’s an example of the HTTP request and response for executing an SSM command:

```http
POST / HTTP/1.1
Host: ssm.amazonaws.com
Content-Type: application/x-amz-json-1.1
X-Amz-Target: AmazonSSM.RunCommand
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20231001/us-east-1/ssm/aws4_request, SignedHeaders=content-type;host;x-amz-date;x-amz-target, Signature=0000000000000000000000000000000000000000000000000000000000000000
X-Amz-Date: 20231001T000000Z

{
    "DocumentName": "AWS-RunShellScript",
    "InstanceIds": ["i-02573cafcfEXAMPLE"],
    "Parameters": {
        "commands": ["echo Hello World"]
    }
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/x-amz-json-1.1
x-amzn-RequestId: 12345678-1234-1234-1234-1234567890ab
Date: Mon, 01 Oct 2023 00:00:00 GMT

{
    "Command": {
        "CommandId": "d-1234567890abcdef",
        "DocumentName": "AWS-RunShellScript",
        "InstanceIds": ["i-02573cafcfEXAMPLE"],
        "Parameters": {
            "commands": ["echo Hello World"]
        },
        "Status": "InProgress"
    }
}
```

### Filtering Events in CloudTrail

CloudTrail allows you to filter events based on various criteria, such as user, event name, and access key. This is particularly useful for narrowing down specific actions or users of interest.

#### Filtering by Username

You can filter events by the username of the user who performed the action. For example, if you want to see all actions performed by a specific user, you can filter the events accordingly.

```mermaid
graph TD
    A[User] -->|Execute SSM Command| B(SSM)
    B -->|Send Command to EC2| C(EC2)
    C -->|Command Execution Status| D(SSM)
    D -->|Record Event| E(CloudTrail)
    E -->|Filter by Username| F[Filtered Events]
```

#### Filtering by Event Name

Another way to filter events is by the event name. For example, you might want to filter events related to starting a session on an EC2 instance.

```mermaid
graph TD
    A[User] -->|Start Session| B(SSM)
    B -->|Session Started| C(EC2)
    C -->|Record Event| D(CloudTrail)
    D -->|Filter by Event Name| E[Filtered Events]
```

#### Filtering by Access Key

You can also filter events by the access key of a user. This is useful for tracking all actions performed by a specific user.

```mermaid
graph TD
    A[User] -->|Use Access Key| B(SSM)
    B -->|Execute Command| C(EC2)
    C -->|Command Execution Status| D(SSM)
    D -->|Record Event| E(CloudTrail)
    E -->|Filter by Access Key| F[Filtered Events]
```

### Real-World Examples and Breaches

#### Recent CVEs and Breaches

One notable example is the AWS S3 bucket misconfiguration breach in 2019, where sensitive data was exposed due to improper permissions. CloudTrail logs would have helped in identifying the unauthorized access and the actions taken.

#### How to Prevent / Defend

To prevent such breaches and ensure the security of your AWS environment, follow these best practices:

1. **Enable CloudTrail**: Ensure that CloudTrail is enabled for all your AWS accounts and regions. This provides a comprehensive audit trail of all actions.

2. **Monitor Logs**: Regularly monitor CloudTrail logs for suspicious activity. Set up alerts for critical events such as unauthorized access attempts.

3. **IAM Policies**: Use strict IAM policies to limit access to sensitive resources. Ensure that users have the minimum necessary permissions.

4. **Multi-Factor Authentication (MFA)**: Enable MFA for all IAM users to add an extra layer of security.

5. **Secure Access Keys**: Rotate access keys regularly and ensure that they are stored securely. Avoid using access keys in scripts or code unless absolutely necessary.

#### Secure Coding Practices

Here’s an example of how to securely configure IAM policies and CloudTrail:

**Vulnerable IAM Policy**

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

**Secure IAM Policy**

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ssm:SendCommand",
                "ec2:DescribeInstances"
            ],
            "Resource": "*"
        }
    ]
}
```

**CloudTrail Configuration**

Ensure that CloudTrail is configured to deliver logs to an S3 bucket and that the bucket is encrypted and has proper access controls.

```yaml
---
Resources:
  CloudTrailBucket:
    Type: 'AWS::S3::Bucket'
    Properties:
      BucketEncryption:
        ServerSideEncryptionConfiguration:
          - ServerSideEncryptionByDefault:
              SSEAlgorithm: AES256
      PublicAccessBlockConfiguration:
        BlockPublicAcls: true
        BlockPublicPolicy: true
        IgnorePublicAcls: true
        RestrictPublicBuckets: true
  CloudTrail:
    Type: 'AWS::CloudTrail::Trail'
    Properties:
      S3BucketName: !Ref CloudTrailBucket
      IsLogging: true
```

### Hands-On Labs

To gain practical experience with CloudTrail and SSM commands, consider the following labs:

- **PortSwigger Web Security Academy**: Offers hands-on labs to practice web security techniques.
- **OWASP Juice Shop**: A deliberately insecure web app for practicing security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another web app for learning web security.
- **WebGoat**: An interactive training application for learning about web application security.

These labs provide a safe environment to experiment with CloudTrail and SSM commands, helping you understand their practical applications and potential security implications.

### Conclusion

In conclusion, CloudTrail Event History is a powerful tool for monitoring and recording actions in your AWS environment. By understanding how to use CloudTrail effectively, you can enhance the security and compliance of your AWS infrastructure. Through detailed logging, filtering, and secure coding practices, you can protect against unauthorized access and ensure that your environment remains secure.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/04-Logging & Monitoring for Security/CloudTrail Event History/00-Overview|Overview]] | [[02-Introduction to CloudTrail Event History|Introduction to CloudTrail Event History]]
