---
course: DevSecOps
topic: Logging & Monitoring for Security
tags: [devsecops]
---

## CloudTrail Event History

### Introduction to CloudTrail

CloudTrail is a vital component of AWS's logging and monitoring infrastructure designed to help organizations maintain compliance, troubleshoot issues, and audit activity within their AWS environment. CloudTrail captures API calls made to AWS services, including calls from the AWS Management Console, AWS SDKs, command-line tools, and other AWS services. This comprehensive logging mechanism provides a detailed record of actions taken within an AWS account, enabling administrators to track changes, identify unauthorized access, and respond to security incidents effectively.

### Understanding IAM Events in CloudTrail

IAM (Identity and Access Management) is a core AWS service responsible for managing access to AWS resources securely. CloudTrail logs various IAM-related events, such as user management, role creation, and access control changes. These events provide critical insights into how identities and permissions are managed within an AWS account.

#### Example IAM Events

Let's explore some typical IAM events logged by CloudTrail:

- **User Creation**: When a new IAM user is created, CloudTrail logs the `CreateUser` event.
- **Role Creation**: When a new IAM role is created, CloudTrail logs the `CreateRole` event.
- **Policy Attachment**: When an IAM policy is attached to a user or role, CloudTrail logs the `AttachUserPolicy` or `AttachRolePolicy` event.
- **Access Key Management**: When an access key is created or deleted, CloudTrail logs the `CreateAccessKey` and `DeleteAccessKey` events.

These events are crucial for maintaining an audit trail of identity and access management activities within an AWS account.

### Event Source and Billing Information

In addition to IAM events, CloudTrail also logs events related to the AWS billing console. For instance, when credits are added to an AWS billing account, CloudTrail records the `AddCreditToAccount` event. This ensures that financial transactions are also tracked and audited.

#### Example Billing Event

```json
{
    "eventVersion": "1.08",
    "userIdentity": {
        "type": "IAMUser",
        "principalId": "AIDAJDPLRKLG7UEXAMPLE",
        "arn": "arn:aws:iam::123456789012:user/admin",
        "accountId": "123456789012",
        "accessKeyId": "AKIAIOSFODNN7EXAMPLE",
        "userName": "admin"
    },
    "eventTime": "2023-10-01T12:34:56Z",
    "eventSource": "billing.amazonaws.com",
    "eventName": "AddCreditToAccount",
    "awsRegion": "us-east-1",
    "sourceIPAddress": "192.0.2.0",
    "userAgent": "AWSConsole [en_US]",
    "requestParameters": {
        "amount": 1000,
        "currencyCode": "USD"
    },
    "responseElements": null,
    "requestID": "12345678-1234-1234-1234-123456789012",
    "eventID": "12345678-1234-1234-1234-123456789012",
    "readOnly": false,
    "resources": [],
    "sharedEventID": "",
    "eventType": "AwsApiCall",
    "managementEvent": true,
    "recipientAccountId": "123456777777"
}
```

This event shows that a user named `admin` added $1000 in credits to their AWS billing account using the AWS Management Console.

### Filtering CloudTrail Events

When dealing with large volumes of CloudTrail events, filtering becomes essential. CloudTrail allows users to filter events based on various criteria, such as event name, username, and more. This feature helps administrators focus on specific types of events, making it easier to identify and investigate security-relevant activities.

#### Example Filter Configuration

To filter events by username, you can use the following configuration:

```json
{
    "Filters": [
        {
            "FieldName": "Username",
            "Values": ["GitLab"]
        }
    ]
}
```

This filter will return all events performed by the user `GitLab`.

### Detailed Event Analysis

Let's dive deeper into a specific event to understand its components and implications. Consider the following event:

```json
{
    "eventVersion": "1.08",
    "userIdentity": {
        "type": "IAMUser",
        "principalId": "AIDAJDPLRKLG7UEXAMPLE",
        "arn": "arn:aws:iam::123456789012:user/GitLab",
        "accountId": "123456789012",
        "accessKeyId": "AKIAIOSFODNN7EXAMPLE",
        "userName": "GitLab"
    },
    "eventTime": "2023-10-01T12:34:56Z",
    "eventSource": "ssm.amazonaws.com",
    "eventName": "SendCommand",
    "awsRegion": "eu-west-3",
    "sourceIPAddress": "192.0.2.0",
    "userAgent": "aws-cli/2.0.0 Python/3.7.3 Linux/4.15.0-104-generic botocore/2.0.0",
    "requestParameters": {
        "DocumentName": "AWS-RunShellScript",
        "InstanceIds": ["i-0abcdef1234567890"],
        "Comment": "Run script on instance",
        "Parameters": {
            "commands": ["echo Hello World"]
        }
    },
    "responseElements": null,
    "requestID": "12345678-1234-1234-1234-123456789012",
    "eventID": "12345678-1234-1234-1234-123456789012",
    "readOnly": false,
    "resources": [
        {
            "ARN": "arn:aws:ssm:eu-west-3:123456789012:document/AWS-RunShellScript",
            "accountId": "111122223333",
            "type": "AWS::SSM::Document"
        },
        {
            "ARN": "arn:aws:ec2:eu-west-3:123456789012:instance/i-0abcdef1234567890",
            "accountId": "123456789012",
            "type": "AWS::EC2::Instance"
        }
    ],
    "sharedEventID": "",
    "eventType": "AwsApiCall",
    "managementEvent": true,
    "recipientAccountId": "123456789012"
}
```

This event shows that the `GitLab` user executed a `SendCommand` action using the AWS Systems Manager (SSM) service. The command ran a simple shell script on an EC2 instance.

### How to Prevent / Defend

#### Detection

To detect unauthorized or suspicious activities, you can set up CloudWatch Alarms and Lambda functions to trigger alerts based on specific CloudTrail events. For example, you can create an alarm to notify you whenever a new IAM user is created.

```yaml
Resources:
  CloudTrailAlarm:
    Type: 'AWS::CloudWatch::Alarm'
    Properties:
      AlarmName: 'NewIAMUserCreationAlarm'
      ComparisonOperator: GreaterThanThreshold
      EvaluationPeriods: 1
      MetricName: 'NumberOfAPIEvents'
      Namespace: 'AWS/CloudTrail'
      Period: 300
      Statistic: Sum
      Threshold: 0
      Dimensions:
        - Name: 'EventName'
          Value: 'CreateUser'
      AlarmActions:
        - !Ref SNSNotificationTopic
```

#### Prevention

To prevent unauthorized access and ensure secure configurations, implement the following best practices:

1. **Least Privilege Principle**: Ensure that IAM users and roles have only the minimum permissions necessary to perform their tasks.
2. **Multi-Factor Authentication (MFA)**: Enable MFA for all IAM users to add an extra layer of security.
3. **Regular Audits**: Conduct regular audits of IAM policies and access keys to identify and remediate potential security risks.

#### Secure Coding Fixes

Here’s an example of how to securely configure IAM policies:

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
                "s3:GetObject",
                "s3:PutObject"
            ],
            "Resource": "arn:aws:s3:::my-bucket/*"
        }
    ]
}
```

The secure policy restricts access to specific S3 actions and resources, adhering to the least privilege principle.

### Real-World Examples and Breaches

Recent breaches have highlighted the importance of robust logging and monitoring practices. For example, the Capital One breach in 2019 involved unauthorized access to sensitive customer data. Proper implementation of CloudTrail and regular audits could have helped detect and mitigate such unauthorized access attempts earlier.

### Hands-On Labs

For practical experience with CloudTrail and IAM, consider the following labs:

- **PortSwigger Web Security Academy**: Offers modules on AWS security, including CloudTrail and IAM.
- **OWASP Juice Shop**: Provides a vulnerable web application that can be used to practice securing IAM configurations and monitoring with CloudTrail.
- **DVWA (Damn Vulnerable Web Application)**: Useful for practicing web application security, including integration with AWS services like CloudTrail.

By thoroughly understanding and implementing these concepts, you can significantly enhance the security posture of your AWS environment.

---
<!-- nav -->
[[03-CloudTrail Event History Part 1|CloudTrail Event History Part 1]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/04-Logging & Monitoring for Security/CloudTrail Event History/00-Overview|Overview]] | [[05-CloudTrail Event History|CloudTrail Event History]]
