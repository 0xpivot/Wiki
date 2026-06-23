---
course: DevSecOps
topic: Logging & Monitoring for Security
tags: [devsecops]
---

## Introduction to Logging and Monitoring for Security

Logging and monitoring are critical components of DevSecOps, enabling teams to detect and respond to security incidents promptly. In the context of cloud environments, such as Amazon Web Services (AWS), logging and monitoring tools like CloudWatch play a pivotal role in maintaining system health and security. This chapter delves into creating a CloudWatch alarm for an EC2 instance, explaining the underlying concepts, steps, and best practices.

### What is CloudWatch?

Amazon CloudWatch is a monitoring and management service provided by AWS. It collects and tracks metrics, collects and monitors log files, and responds to system-wide changes, including changes in application performance. CloudWatch helps users gain insight into their applications, understand and react to system-wide performance changes, and optimize resource utilization.

#### Key Features of CloudWatch
- **Metrics**: Provides detailed monitoring of AWS resources and applications.
- **Logs**: Collects and monitors log data from AWS resources and custom applications.
- **Alarms**: Triggers actions based on rules defined by the user.
- **Events**: Tracks changes to AWS resources and sends notifications.

### Why Use CloudWatch Alarms?

CloudWatch alarms are essential for proactive monitoring and alerting. They help in detecting anomalies and triggering automated responses, ensuring that issues are addressed promptly. For example, if an EC2 instance's CPU usage exceeds a certain threshold, an alarm can be set to notify the team or automatically scale up resources.

### Setting Up a CloudWatch Alarm for an EC2 Instance

To create a CloudWatch alarm for an EC2 instance, follow these steps:

1. **Create an SNS Topic**:
   - An SNS (Simple Notification Service) topic is used to send notifications to subscribers.
   - Subscribers can be email addresses, SMS numbers, or other AWS services.

2. **Subscribe to the SNS Topic**:
   - After creating the SNS topic, subscribe to it to receive notifications.

3. **Create the CloudWatch Alarm**:
   - Define the metric to monitor (e.g., CPU usage).
   - Set the threshold and period for the alarm.
   - Specify the action to take when the alarm triggers (e.g., send an SNS notification).

4. **Trigger the Alarm**:
   - Intentionally cause the monitored condition to occur to test the alarm.

### Detailed Steps and Code Examples

#### Step 1: Create an SNS Topic

First, create an SNS topic to which the alarm will send notifications.

```python
import boto3

sns = boto3.client('sns')

response = sns.create_topic(
    Name='EC2InstanceAlarm'
)

topic_arn = response['TopicArn']
print(f'Topic ARN: {topic_arn}')
```

#### Step 2: Subscribe to the SNS Topic

Next, subscribe to the SNS topic to receive notifications.

```python
response = sns.subscribe(
    TopicArn=topic_arn,
    Protocol='email',
    Endpoint='your-email@example.com'
)

subscription_arn = response['SubscriptionArn']
print(f'Subscription ARN: {subscription_arn}')
```

#### Step 3: Confirm Subscription

After subscribing, you will receive an email to confirm the subscription.

```plaintext
Subject: Confirmation Required for Amazon SNS Subscription
Body: To confirm the subscription, visit the following URL:
https://sns.us-east-1.amazonaws.com/?Action=ConfirmSubscription&TopicArn=arn:aws:sns:us-east-1:123456789012:EC2InstanceAlarm&Token=abcdefg1234567890
```

Click the link to confirm the subscription.

#### Step 4: Create the CloudWatch Alarm

Now, create the CloudWatch alarm to monitor the EC2 instance.

```python
cloudwatch = boto3.client('cloudwatch')

response = cloudwatch.put_metric_alarm(
    AlarmName='EC2InstanceDownAlarm',
    MetricName='StatusCheckFailed_Instance',
    Namespace='AWS/EC2',
    Statistic='Average',
    Period=60,
    EvaluationPeriods=1,
    Threshold=1,
    ComparisonOperator='GreaterThanThreshold',
    ActionsEnabled=True,
    AlarmActions=[topic_arn],
    Dimensions=[
        {
            'Name': 'InstanceId',
            'Value': 'i-0123456789abcdef0'
        },
    ]
)
```

### Triggering the Alarm

To test the alarm, intentionally bring down the EC2 instance.

#### SSH into the EC2 Instance

```bash
ssh -i path/to/key.pem ec2-user@public-ip-address
```

#### Bring Down the Primary Interface

```bash
sudo ip link set dev eth0 down
```

This will cause the `StatusCheckFailed_Instance` metric to exceed the threshold, triggering the alarm.

### Full Example of HTTP Request and Response

When the alarm triggers, an HTTP request is sent to the SNS endpoint.

```http
POST / HTTP/1.1
Host: sns.us-east-1.amazonaws.com
Content-Type: application/json
X-Amz-Sns-Message-Type: Notification
X-Amz-Sns-Topic-Arn: arn:aws:sns:us-east-1:123456789012:EC2InstanceAlarm
X-Amz-Sns-MESSAGE-ID: 12345678-1234-1234-1234-123456789012
X-Amz-Sns-Timestamp: 2023-10-01T12:00:00Z
X-Amz-Sns-UNSUBSCRIBE-URL: https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:123456789012:EC2InstanceAlarm:12345678-1234-1234-1234-123456789012

{
  "Type": "Notification",
  "MessageId": "12345678-1234-1234-1234-123456789012",
  "TopicArn": "arn:aws:sns:us-east-1:123456789012:EC2InstanceAlarm",
  "Subject": "EC2 Instance Down Alarm",
  "Message": "{\"AlarmName\":\"EC2InstanceDownAlarm\",\"AlarmDescription\":null,\"AWSAccountId\":\"123456789012\",\"NewStateValue\":\"ALARM\",\"NewStateReason\":\"Threshold Crossed: 1 datapoint (1.0) was greater than or equal to the threshold (1.0).\",\"StateChangeTime\":\"2023-10-01T12:00:00Z\",\"Region\":\"US East (N. Virginia)\",\"OldStateValue\":\"OK\",\"Trigger\":{\"MetricName\":\"StatusCheckFailed_Instance\",\"Namespace\":\"AWS/EC2\",\"Statistic\":\"Average\",\"Unit\":null,\"Dimensions\":[{\"name\":\"InstanceId\",\"value\":\"i-0123456789abcdef0\"}],\"Period\":60,\"EvaluationPeriods\":1,\"ComparisonOperator\":\"GreaterThanThreshold\",\"Threshold\":1.0}}",
  "Timestamp": "2023-10-01T12:00:00Z",
  "SignatureVersion": "1",
  "Signature": "EXAMPLESIGNATURE",
  "SigningCertURL": "https://sns.us-east-1.amazonaws.com/SimpleNotificationService-EXAMPLE.pem",
  "UnsubscribeURL": "https://sns.us-east-1.amazonaws.com/?Action=Unsubscribe&SubscriptionArn=arn:aws:sns:us-east-1:123456789012:EC2InstanceAlarm:12345678-1234-1234-1234-123456789012"
}
```

### How to Prevent / Defend

#### Detection
- Regularly monitor CloudWatch logs and metrics.
- Use CloudTrail to track API calls and user activity.

#### Prevention
- Implement IAM policies to restrict access to critical resources.
- Use security groups and network ACLs to control inbound and outbound traffic.

#### Secure Coding Fixes
- Ensure that all EC2 instances are properly configured with security groups.
- Use IAM roles and policies to limit permissions.

#### Configuration Hardening
- Enable detailed monitoring for EC2 instances.
- Configure CloudWatch to send alerts to multiple recipients.

### Real-World Examples

#### Recent Breaches
- **CVE-2021-3427**: A vulnerability in AWS Elastic Load Balancing allowed unauthorized access to internal systems. Proper logging and monitoring could have detected this breach earlier.
- **AWS RDS Incident (2022)**: An issue with AWS RDS led to data loss. Regular monitoring and backups could have mitigated the impact.

### Practice Labs

For hands-on practice, consider the following labs:
- **PortSwigger Web Security Academy**: Offers comprehensive modules on web security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web vulnerabilities.

### Conclusion

Creating a CloudWatch alarm for an EC2 instance is a crucial step in maintaining system health and security. By following the detailed steps and best practices outlined in this chapter, you can ensure that your cloud environment is monitored effectively and that potential issues are detected and resolved promptly.

---
<!-- nav -->
[[07-Introduction to Logging and Monitoring for Security Part 1|Introduction to Logging and Monitoring for Security Part 1]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/04-Logging & Monitoring for Security/Create CloudWatch Alarm for EC2 Instance/00-Overview|Overview]] | [[09-Introduction to Logging and Monitoring for Security Part 3|Introduction to Logging and Monitoring for Security Part 3]]
