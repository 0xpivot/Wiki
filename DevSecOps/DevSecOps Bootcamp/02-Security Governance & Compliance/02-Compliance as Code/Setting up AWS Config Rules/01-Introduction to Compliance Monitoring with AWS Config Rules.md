---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## Introduction to Compliance Monitoring with AWS Config Rules

Compliance monitoring is a critical aspect of DevSecOps, ensuring that your infrastructure adheres to regulatory requirements and internal policies. AWS Config is a service that enables you to assess, audit, and manage the configurations of your AWS resources. By using AWS Config rules, you can automate the process of checking whether your resources comply with specific rules and standards.

### Why Use AWS Config Rules?

AWS Config rules help you maintain compliance by continuously monitoring your resources against predefined rules. This ensures that your infrastructure remains compliant with regulatory requirements such as GDPR, HIPAA, and PCI-DSS. Additionally, AWS Config rules can help you enforce internal policies, such as tagging conventions and resource naming standards.

### How AWS Config Works

AWS Config works by collecting configuration details of your AWS resources and storing them in a central repository. These details include metadata about the resources, their relationships, and their configurations. AWS Config can then evaluate these details against predefined rules to determine compliance.

#### Key Components of AWS Config

- **Configuration Items**: Detailed records of the configuration settings of your AWS resources.
- **Configuration Recorder**: A component that records the configuration items of your resources.
- **Aggregator**: A component that aggregates configuration data from multiple accounts and regions.
- **Rules**: Predefined conditions that AWS Config evaluates against the configuration items.

### Setting Up AWS Config Rules

To set up AWS Config rules, you need to configure several components, including the configuration recorder, data governance, and delivery method.

#### Configuration Recorder

The configuration recorder is responsible for recording the configuration items of your resources. You can configure the frequency of these recordings, which can be either continuous or scheduled.

```mermaid
sequenceDiagram
    participant User
    participant AWS_Config_Recorder
    participant AWS_Resource
    User->>AWS_Config_Recorder: Configure Recording Frequency
    AWS_Config_Recorder->>AWS_Resource: Record Configuration
    AWS_Resource-->>AWS_Config_Recorder: Send Configuration Data
```

**Continuous Recording vs. Scheduled Recording**

- **Continuous Recording**: AWS Config continuously records the configuration items of your resources. This is useful for real-time monitoring but may generate more data.
- **Scheduled Recording**: AWS Config records the configuration items at specified intervals (e.g., daily). This is useful for reducing the amount of data generated.

#### Data Governance

Data governance ensures that AWS Config has the necessary permissions to track changes to your AWS resources. This involves creating an IAM role with the required permissions.

```mermaid
sequenceDiagram
    participant User
    participant AWS_Config_Role
    participant AWS_Resource
    User->>AWS_Config_Role: Create IAM Role
    AWS_Config_Role->>AWS_Resource: Track Changes
    AWS_Resource-->>AWS_Config_Role: Notify Changes
```

**IAM Role Creation**

AWS Config creates an IAM role with the necessary permissions to track changes to your resources. This role includes permissions to read configuration data and log changes.

```yaml
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "config:Get*",
        "config:List*",
        "config:Describe*"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

#### Delivery Method

AWS Config needs a place to store the recorded configuration data. By default, this data is stored in an S3 bucket. You can also configure an SNS topic to receive notifications about changes to your resources.

```mermaid
sequenceDiagram
    participant User
    participant AWS_Config
    participant S3_Bucket
    participant SNS_Topic
    User->>AWS_Config: Configure Delivery Method
    AWS_Config->>S3_Bucket: Store Configuration Data
    AWS_Config->>SNS_Topic: Send Notifications
```

**S3 Bucket Configuration**

AWS Config stores the recorded configuration data in an S3 bucket. This bucket can be used to review the data with visualization tools or import it into third-party monitoring applications.

```http
PUT /my-config-bucket HTTP/1.1
Host: s3.amazonaws.com
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20150101/us-east-1/s3/aws4_request, SignedHeaders=host;x-amz-date, Signature=fe5f4965d6bd7c440300ce69bfb3e9b1e880f2a44a2657c8d05f2fb0f2c81b7a
x-amz-date: 20150101T000000Z
```

**SNS Topic Configuration**

You can configure an SNS topic to receive notifications about changes to your resources. This allows you to be alerted to any non-compliant changes.

```http
POST /my-sns-topic HTTP/1.1
Host: sns.us-east-1.amazonaws.com
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20150101/us-east-1/sns/aws4_request, SignedHeaders=host;x-amz-date, Signature=fe5f4965d6bd7c440300ce69bfb3e9b1e880f2a44a2657c8d05f2fb0f2c81b7a
x-amz-date: 20150101T000000Z
Content-Type: application/x-www-form-urlencoded
Content-Length: 123
Message=This is a test message&Subject=Test Message
```

### Real-World Examples and Recent Breaches

Recent breaches have highlighted the importance of compliance monitoring. For example, the Capital One breach in 2019 exposed sensitive customer data due to misconfigured AWS S3 buckets. Proper use of AWS Config rules could have helped detect and mitigate such misconfigurations.

### Common Pitfalls and How to Avoid Them

#### Misconfigured Recording Frequency

One common pitfall is misconfiguring the recording frequency. Continuous recording can generate a large amount of data, while scheduled recording might miss important changes. To avoid this, ensure that the recording frequency aligns with your compliance needs.

#### Insufficient Permissions

Another pitfall is insufficient permissions for the IAM role created by AWS Config. Ensure that the role has the necessary permissions to track changes to your resources.

#### Inadequate Storage and Notification Mechanisms

Inadequate storage and notification mechanisms can lead to missed compliance issues. Ensure that the S3 bucket and SNS topic are properly configured to store and notify about changes.

### How to Prevent / Defend

#### Detection

Use AWS Config to continuously monitor your resources for compliance issues. Regularly review the configuration data stored in the S3 bucket and use visualization tools to identify non-compliant changes.

#### Prevention

Implement strict IAM roles with the necessary permissions to track changes to your resources. Use AWS Config rules to enforce compliance with regulatory requirements and internal policies.

#### Secure Coding Fixes

Show the vulnerable pattern and the corrected secure version side by side:

**Vulnerable Pattern**

```yaml
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "config:Get*",
        "config:List*",
        "config:Describe*"
      ],
      "Resource": "*"
    }
  ]
}
```

**Secure Version**

```yaml
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "config:Get*",
        "config:List*",
        "config:Describe*"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "logs:CreateLogGroup",
        "logs:CreateLogStream",
        "logs:PutLogEvents"
      ],
      "Resource": "arn:aws:logs:*:*:*"
    }
  ]
}
```

#### Configuration Hardening

Ensure that the S3 bucket and SNS topic are properly configured with the necessary permissions and notifications.

### Practice Labs

For hands-on experience with AWS Config rules, consider the following labs:

- **CloudGoat**: A cloud security training platform that includes exercises on AWS Config rules.
- **flaws.cloud**: A cloud security training platform that includes exercises on AWS Config rules.
- **AWS Official Workshops**: AWS provides official workshops that cover AWS Config rules and other compliance-related topics.

By following these steps and best practices, you can effectively use AWS Config rules to ensure compliance in your DevSecOps environment.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Setting up AWS Config Rules/00-Overview|Overview]] | [[02-Introduction to Compliance as Code Part 1|Introduction to Compliance as Code Part 1]]
