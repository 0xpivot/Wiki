---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## Introduction to Compliance as Code

Compliance as Code is a DevSecOps practice that automates the enforcement of compliance requirements through code. In the context of AWS, this means using tools like AWS Config to define and enforce compliance rules across your infrastructure. AWS Config Rules allow you to continuously monitor your AWS resources against defined rules, ensuring that your environment adheres to specific policies and regulations.

### What is AWS Config?

AWS Config is a service that provides you with an inventory of your AWS resources, their relationships, and historical changes. It helps you maintain compliance with internal policies and external regulations by continuously auditing your resources against predefined rules.

#### Key Features of AWS Config
- **Inventory Management**: Tracks all AWS resources and their configurations.
- **Configuration History**: Maintains a history of changes to your resources.
- **Compliance Rules**: Allows you to define custom rules to check compliance.
- **Notifications**: Sends alerts when resources violate compliance rules.

### Why Use AWS Config Rules?

Using AWS Config Rules is essential for maintaining a secure and compliant environment. It helps you:

- **Automate Compliance Checks**: Continuously monitor resources against compliance rules.
- **Detect Non-Compliant Resources**: Identify and remediate issues promptly.
- **Maintain Audit Trails**: Keep a record of all changes and compliance statuses.
- **Ensure Regulatory Compliance**: Meet industry-specific regulations and standards.

### How AWS Config Rules Work

AWS Config Rules work by evaluating your resources against predefined rules. These rules can be built-in or custom-defined. When a rule is violated, AWS Config generates a notification, allowing you to take corrective action.

#### Example Scenario

In the given scenario, we have two AWS Config Rules:
1. **Restricted Security Group**: Ensures that security groups are configured securely.
2. **CloudTrail Enabled**: Ensures that CloudTrail logging is enabled.

Let's break down each rule and understand how they work.

### Restricted Security Group Rule

The Restricted Security Group rule checks whether security groups are configured securely. Specifically, it looks for security groups that allow unrestricted access to certain ports, such as SSH (port 22).

#### Rule Definition

Here is an example of how you might define this rule in AWS Config:

```json
{
  "ConfigRuleName": "restricted-security-group",
  "Description": "Checks if security groups allow unrestricted access to SSH port.",
  "Scope": {
    "ComplianceResourceTypes": [
      "AWS::EC2::SecurityGroup"
    ]
  },
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "SECURITY_GROUP_UNRESTRICTED_INBOUND_TRAFFIC"
  }
}
```

#### How It Works

1. **Evaluation**: AWS Config evaluates all security groups in your account.
2. **Check**: It checks if any security group allows inbound traffic on port 22 from `0.0.0.0/0` (all IP addresses).
3. **Notification**: If a security group violates the rule, AWS Config generates a notification.

#### Real-World Example

Consider a recent breach where an attacker gained unauthorized access to an SSH server due to an open security group rule. This could have been prevented by enforcing the Restricted Security Group rule.

### CloudTrail Enabled Rule

The CloudTrail Enabled rule ensures that CloudTrail logging is enabled in your AWS account. CloudTrail logs API calls made within your account, providing a valuable audit trail.

#### Rule Definition

Here is an example of how you might define this rule in AWS Config:

```json
{
  "ConfigRuleName": "cloudtrail-enabled",
  "Description": "Checks if CloudTrail logging is enabled.",
  "Scope": {},
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "CLOUDTRAIL_ENABLED"
  }
}
```

#### How It Works

1. **Evaluation**: AWS Config evaluates the CloudTrail settings in your account.
2. **Check**: It checks if CloudTrail logging is enabled.
3. **Notification**: If CloudTrail logging is disabled, AWS Config generates a notification.

#### Real-World Example

In a recent data breach, an organization was unable to trace the actions of an attacker due to missing CloudTrail logs. Enforcing the CloudTrail Enabled rule would have ensured that logs were available for investigation.

### Checking Compliance Status

To check the compliance status of your rules, you can use the AWS Management Console or the AWS CLI.

#### Using the AWS Management Console

1. **Navigate to AWS Config**.
2. **Select Compliance**.
3. **View the Compliance Dashboard**.

#### Using the AWS CLI

You can use the following commands to check compliance status:

```sh
aws configservice describe-compliance-by-config-rule --config-rules restricted-security-group cloudtrail-enabled
```

This command returns the compliance status of the specified rules.

### Detailed Example: Restricted Security Group

Let's dive deeper into the Restricted Security Group rule and see how it works in practice.

#### Scenario Setup

Assume you have two EC2 instances running in your account, both using the same security group. The security group allows inbound traffic on port 22 from all IP addresses (`0.0.0.0/0`).

#### Security Group Configuration

Here is an example of the security group configuration:

```json
{
  "GroupId": "sg-12345678",
  "IpPermissions": [
    {
      "IpProtocol": "tcp",
      "FromPort": 22,
      "ToPort": 22,
      "IpRanges": [
        {
          "CidrIp": "0.0.0.0/0"
        }
      ]
    }
  ]
}
```

#### Compliance Check

When AWS Config evaluates this security group, it checks if the rule is violated. In this case, the rule is violated because the security group allows unrestricted access to port 22.

#### Notification

AWS Config generates a notification indicating that the security group is non-compliant. You can view this notification in the AWS Management Console or via the AWS CLI.

### How to Prevent / Defend

#### Secure Configuration

To prevent the security group from being non-compliant, you should restrict access to port 22. Here is an example of a secure configuration:

```json
{
  "GroupId": "sg-12345678",
  "IpPermissions": [
    {
      "IpProtocol": "tcp",
      "FromPort": 22,
      "ToPort": 22,
      "IpRanges": [
        {
          "CidrIp": "192.168.1.0/24"
        }
      ]
    }
  ]
}
```

#### Secure Coding Fix

Here is a comparison of the insecure and secure configurations:

**Insecure Configuration**

```json
{
  "GroupId": "sg-12345678",
  "IpPermissions": [
    {
      "IpProtocol": "tcp",
      "FromPort": 22,
      "ToPort": 22,
      "IpRanges": [
        {
          "CidrIp": "0.0.0.0/0"
        }
      ]
    }
  ]
}
```

**Secure Configuration**

```json
{
  "GroupId": "sg-12345678",
  "IpPermissions": [
    {
      "IpProtocol": "tcp",
      "FromPort": 22,
      "ToPort": 22,
      "IpRanges": [
        {
          "CidrIp": "192.168.1.0/24"
        }
      ]
    }
  ]
}
```

#### Hardening

To further harden your security group configuration, consider the following best practices:

- **Limit Access**: Restrict access to necessary IP ranges.
- **Use Security Groups**: Utilize security groups to control access to resources.
- **Enable Logging**: Ensure CloudTrail logging is enabled to maintain an audit trail.

### Conclusion

By using AWS Config Rules, you can automate the enforcement of compliance requirements, ensuring that your AWS environment remains secure and compliant. Understanding how these rules work and how to configure them properly is crucial for maintaining a secure infrastructure.

### Practice Labs

For hands-on experience with AWS Config Rules, consider the following labs:

- **CloudGoat**: A cloud security training platform that includes exercises on AWS Config Rules.
- **flaws.cloud**: A cloud security training platform that covers various AWS security services, including AWS Config.

These labs provide practical experience in setting up and managing AWS Config Rules, helping you gain mastery over this important DevSecOps practice.

---
<!-- nav -->
[[05-Introduction to Compliance as Code Part 4|Introduction to Compliance as Code Part 4]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Setting up AWS Config Rules/00-Overview|Overview]] | [[07-Introduction to Compliance as Code Part 6|Introduction to Compliance as Code Part 6]]
