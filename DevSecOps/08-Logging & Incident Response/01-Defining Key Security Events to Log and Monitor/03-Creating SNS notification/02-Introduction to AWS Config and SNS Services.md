---
course: DevSecOps
topic: Defining Key Security Events to Log and Monitor
tags: [devsecops]
---

## Introduction to AWS Config and SNS Services

### Background Theory

AWS Config is a service provided by Amazon Web Services (AWS) that enables you to assess, audit, and record changes to your AWS resources. This service provides a detailed view of the resources associated with your AWS account, including how they are configured, how they are related to one another, and how these configurations and relationships have changed over time. This historical data is crucial for compliance, auditing, and security purposes.

The primary focus of AWS Config in this context is to monitor changes to your AWS resources, particularly those that could pose security risks. For instance, changes to S3 buckets that make them publicly accessible can lead to data exposure and potential breaches. By monitoring these changes, you can take immediate action to mitigate risks.

### Why Monitor Changes?

Monitoring changes is essential because it allows you to:

- **Detect Unauthorized Access**: Identify when unauthorized users attempt to modify your resources.
- **Ensure Compliance**: Verify that your resources adhere to regulatory requirements.
- **Prevent Data Exposure**: Detect and respond to changes that might expose sensitive data.
- **Maintain Security Posture**: Keep track of changes that could weaken your security posture.

### How AWS Config Works

AWS Config works by continuously collecting configuration details about your AWS resources. These details are stored in a configuration history, which you can query to understand how your resources have changed over time. You can also set up rules to automatically evaluate your resources against specific criteria, such as whether they are compliant with certain policies.

### Real-World Example: Recent Breaches

A notable example of the importance of monitoring changes is the Capital One breach in 2019. An attacker exploited a misconfigured firewall rule, which allowed access to sensitive customer data. Had the organization been using AWS Config to monitor changes to their firewall rules, they might have detected the misconfiguration earlier and prevented the breach.

### Setting Up AWS Config

To set up AWS Config, you need to enable it in your AWS Management Console. Once enabled, you can define which resources to monitor and set up rules to evaluate these resources. For this example, we will focus on monitoring changes to S3 buckets.

### Monitoring S3 Buckets

S3 buckets are a common target for security breaches due to their ability to store large amounts of data. Making an S3 bucket publicly accessible can lead to data exposure. Therefore, it is crucial to monitor changes to S3 buckets to ensure they remain secure.

### Using SNS for Notifications

Amazon Simple Notification Service (SNS) is a fully managed pub/sub messaging service that enables you to send messages to multiple subscribers. In this context, SNS will be used to send email alerts when AWS Config detects changes to your S3 buckets.

### Steps to Set Up SNS Topic

1. **Create a New SNS Topic**:
    - Navigate to the SNS section in the AWS Management Console.
    - Click on "Topics" and then "Create topic".
    - Choose the "Standard" type and enter a name for the topic, e.g., `WBC-SNS`.

```mermaid
sequenceDiagram
    participant User
    participant SNS
    User->>SNS: Create Topic Request
    SNS-->>User: Topic Created Response
```

### Configuring AWS Config to Send Alerts via SNS

Once the SNS topic is created, you need to configure AWS Config to send notifications to this topic when it detects changes to your S3 buckets.

#### Step-by-Step Configuration

1. **Enable AWS Config**:
    - Navigate to the AWS Config section in the AWS Management Console.
    - Enable AWS Config if it is not already enabled.

2. **Define Rules**:
    - Define rules to monitor changes to your S3 buckets. For example, you can create a rule to detect when an S3 bucket is made publicly accessible.

3. **Set Up Notifications**:
    - Configure AWS Config to send notifications to the SNS topic you created when the defined rules are triggered.

```mermaid
sequenceDiagram
    participant User
    participant AWSConfig
    participant SNS
    User->>AWSConfig: Enable AWS Config
    AWSConfig-->>User: AWS Config Enabled
    User->>AWSConfig: Define Rule
    AWSConfig-->>User: Rule Defined
    User->>AWSConfig: Set Up Notification
    AWSConfig-->>SNS: Send Notification
    SNS-->>User: Email Alert Received
```

### Complete Example: Full Configuration

Here is a complete example of setting up AWS Config and SNS to monitor changes to S3 buckets and send email alerts.

#### Step 1: Create SNS Topic

Navigate to the SNS section in the AWS Management Console and create a new topic named `WBC-SNS`.

```mermaid
graph LR
    A[User] --> B[Navigate to SNS]
    B --> C[Create Topic]
    C --> D[Enter Name: WBC-SNS]
    D --> E[Topic Created]
```

#### Step 2: Enable AWS Config

Navigate to the AWS Config section and enable it if it is not already enabled.

```mermaid
graph LR
    A[User] --> B[Navigate to AWS Config]
    B --> C[Enable AWS Config]
    C --> D[AWS Config Enabled]
```

#### Step 3: Define Rule

Define a rule to monitor changes to S3 buckets. For example, create a rule to detect when an S3 bucket is made publicly accessible.

```mermaid
graph LR
    A[User] --> B[Define Rule]
    B --> C[Rule Defined]
```

#### Step  4: Set Up Notification

Configure AWS Config to send notifications to the SNS topic when the defined rule is triggered.

```mermaid
graph LR
    A[User] --> B[Set Up Notification]
    B --> C[Notification Configured]
```

### Full Raw HTTP Messages

Here is an example of the full raw HTTP messages involved in creating an SNS topic and setting up a notification.

#### Creating SNS Topic

```http
POST /topics HTTP/1.1
Host: sns.us-east-1.amazonaws.com
Content-Type: application/x-www-form-urlencoded
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20231001/us-east-1/sns/aws4_request, SignedHeaders=content-type;host;x-amz-date, Signature=7c9f1b5e9c1f93b5d9d3b890f8f5e6a4a9d5b0f9d5b0f9d5b0f9d5b0f9d5b0f9
X-Amz-Date: 20231001T000000Z
Content-Length: 54

Name=WBC-SNS&Type=standard
```

#### Setting Up Notification

```http
POST /topics/WBC-SNS HTTP/1.1
Host: sns.us-east-1.amazonaws.com
Content-Type: application/x-www-form-urlencoded
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20231001/us-east-1/sns/aws4_request, SignedHeaders=content-type;host;x-amz-date, Signature=7c9f1b5e9c1f93b5d9d3b890f8f5e6a4a9d5b0f9d5b0f9d5b0f9d5b0f9d5b0f9
X-Amz-Date: 20231001T000000Z
Content-Length: 116

Action=SetTopicAttributes&AttributeName=DeliveryPolicy&AttributeValue={"http":{"defaultHealthyRetryPolicy":{"minDelayTarget":1,"maxDelayTarget":20,"numRetries":3}}}
```

### Common Pitfalls and Best Practices

#### Pitfall: Misconfigured SNS Topic

One common pitfall is misconfiguring the SNS topic, which can result in notifications not being sent correctly. Ensure that the topic is properly configured and that the necessary permissions are in place.

#### Best Practice: Regular Audits

Regularly audit your AWS Config settings and SNS configurations to ensure they are functioning as intended. This includes checking for any unauthorized changes and verifying that notifications are being sent correctly.

### How to Prevent / Defend

#### Detection

- **Monitor AWS Config Logs**: Regularly review logs generated by AWS Config to identify any unauthorized changes.
- **Use CloudTrail**: Integrate AWS CloudTrail with AWS Config to get detailed activity logs for your AWS account.

#### Prevention

- **IAM Policies**: Ensure that IAM policies are properly configured to restrict access to sensitive resources.
- **Secure SNS Topics**: Secure SNS topics by ensuring that only authorized users can subscribe to them.

#### Secure Coding Fixes

##### Vulnerable Code

```python
# Vulnerable Code
import boto3

sns = boto3.client('sns')
response = sns.create_topic(Name='WBC-SNS', Attributes={'DeliveryPolicy': '{"http":{"defaultHealthyRetryPolicy":{"minDelayTarget":1,"maxDelayTarget":20,"numRetries":3}}}'})
print(response)
```

##### Fixed Code

```python
# Fixed Code
import boto3

sns = boto3.client('sns')
response = sns.create_topic(
    Name='WBC-SNS',
    Attributes={
        'DeliveryPolicy': '{"http":{"defaultHealthyRetryPolicy":{"minDelayTarget":1,"maxDelayTarget":20,"numRetries":3}}}',
        'Policy': '{"Version":"2012-10-17","Statement":[{"Sid":"AllowSubscription","Effect":"Allow","Principal":{"AWS":"arn:aws:iam::123456789012:root"},"Action":["sns:Subscribe"],"Resource":"arn:aws:sns:us-east-1:123456789012:WBC-SNS"}]}'
    }
)
print(response)
```

### Conclusion

By setting up AWS Config and SNS to monitor changes to your S3 buckets and send email alerts, you can significantly enhance your security posture. This setup ensures that you are promptly notified of any changes that could pose a security risk, allowing you to take immediate action to mitigate these risks.

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive labs on web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for security training.

These labs provide practical experience in setting up and managing AWS Config and SNS, helping you to apply the concepts learned in this chapter effectively.

---
<!-- nav -->
[[01-Introduction to AWS Config and SNS Notifications|Introduction to AWS Config and SNS Notifications]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/01-Defining Key Security Events to Log and Monitor/03-Creating SNS notification/00-Overview|Overview]] | [[03-Introduction to SNS Notification Setup|Introduction to SNS Notification Setup]]
