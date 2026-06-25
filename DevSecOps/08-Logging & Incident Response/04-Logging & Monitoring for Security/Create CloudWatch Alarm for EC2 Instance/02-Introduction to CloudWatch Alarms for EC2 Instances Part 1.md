---
course: DevSecOps
topic: Logging & Monitoring for Security
tags: [devsecops]
---

## Introduction to CloudWatch Alarms for EC2 Instances

### Background Theory

CloudWatch is a monitoring service provided by Amazon Web Services (AWS) that provides visibility into your cloud resources and applications. It collects and tracks metrics, collects and monitors log files, and responds to system-wide changes, including changes in the health and scalability of your applications. One of the key features of CloudWatch is its ability to create alarms based on these metrics, which can trigger actions such as sending notifications or automatically scaling resources.

### Why Use CloudWatch Alarms?

CloudWatch Alarms are essential for maintaining the health and performance of your EC2 instances. They allow you to monitor various metrics such as CPU utilization, disk space, and network traffic. By setting up alarms, you can receive notifications when certain thresholds are crossed, enabling you to take proactive measures to avoid potential issues.

### How CloudWatch Alarms Work

When you create a CloudWatch Alarm, you define a metric to monitor, a threshold value, and a period of time over which the metric is evaluated. If the metric exceeds the threshold during the specified period, the alarm triggers an action, such as sending an email or SMS notification, or executing an AWS Lambda function.

#### Example Scenario

Consider a scenario where you have an EC2 instance running a web application. You want to ensure that the CPU utilization does not exceed 80%. If it does, you want to receive a notification so that you can investigate and take necessary actions.

### Creating a CloudWatch Alarm for EC2 Instance

To create a CloudWatch Alarm for an EC2 instance, you can use the AWS Management Console, AWS CLI, or AWS SDKs. Here, we will focus on using the AWS CLI.

#### Prerequisites

Before proceeding, ensure that you have the following:

1. **AWS CLI Installed**: The AWS Command Line Interface (CLI) is a unified tool to manage AWS services. Ensure it is installed and configured with your AWS credentials.
2. **EC2 Instance Running**: Ensure that your EC2 instance is running and that you have the necessary permissions to create CloudWatch Alarms.

#### Step-by-Step Guide

1. **Install `ifconfig`**:
   If you don't have `ifconfig` installed on your server, you can install it using the appropriate package manager. For example, on Ubuntu, you can use:
   ```sh
   sudo apt-get update
   sudo apt-get install net-tools
   ```

2. **Bring Down the Network Interface**:
   To simulate a failure, you can bring down a network interface using `ifconfig`. For example:
   ```sh
   sudo ifconfig eth0 down
   ```

3. **Create the CloudWatch Alarm**:
   Use the AWS CLI to create a CloudWatch Alarm. For example, to create an alarm for CPU utilization exceeding 80%:
   ```sh
   aws cloudwatch put-metric-alarm \
     --alarm-name "HighCPUUtilization" \
     --alarm-description "Alarm when CPU exceeds 80%" \
     --actions-enabled true \
     --metric-name CPUUtilization \
     --namespace AWS/EC2 \
     --statistic Average \
     --period 300 \
     --threshold 80 \
     --comparison-operator GreaterThanThreshold \
     --dimensions Name=InstanceId,Value=i-0123456789abcdef0 \
     --evaluation-periods 1 \
     --alarm-actions arn:aws:sns:us-east-1:123456789012:MyTopic
   ```

### Explanation of the Command

- **--alarm-name**: The name of the alarm.
- **--alarm-description**: A description of the alarm.
- **--actions-enabled**: Whether the alarm actions are enabled.
- **--metric-name**: The metric to monitor (CPUUtilization in this case).
- **--namespace**: The namespace of the metric (AWS/EC2 for EC2 instances).
- **--statistic**: The statistic to apply to the metric (Average in this case).
- **--period**: The period over which the metric is evaluated (300 seconds in this case).
- **--threshold**: The threshold value (80% in this case).
- **--comparison-operator**: The comparison operator (GreaterThanThreshold in this case).
- **--dimensions**: The dimensions of the metric (InstanceId in this case).
- **--evaluation-periods**: The number of periods over which data is compared to the specified threshold (1 in this case).
- **--alarm-actions**: The actions to take when the alarm is triggered (an SNS topic in this case).

### Full HTTP Request and Response

Here is an example of the full HTTP request and response for creating a CloudWatch Alarm using the AWS API:

```http
POST / HTTP/1.1
Host: monitoring.amazonaws.com
Content-Type: application/x-amz-json-1.1
X-Amz-Target: MonitorControl.PutMetricAlarm
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20170320/us-east-1/cloudwatch/aws4_request, SignedHeaders=content-type;host;x-amz-date;x-amz-target, Signature=fe5f0c8b9cf9b0e5c8f40fa052c6d9c83f3b7f8baf4e4c95b867b2a3c4fa11e0
X-Amz-Date: 20170320T193642Z
Content-Length: 444

{
    "AlarmName": "HighCPUUtilization",
    "AlarmDescription": "Alarm when CPU exceeds  80%",
    "ActionsEnabled": true,
    "MetricName": "CPUUtilization",
    "Namespace": "AWS/EC2",
    "Statistic": "Average",
    "Period": 300,
    "Threshold": 80,
    "ComparisonOperator": "GreaterThanThreshold",
    "EvaluationPeriods": 1,
    "Dimensions": [
        {
            "Name": "InstanceId",
            "Value": "i-0123456789abcdef0"
        }
    ],
    "AlarmActions": [
        "arn:aws:sns:us-east-1:123456789012:MyTopic"
    ]
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/x-amz-json-1.1
Content-Length: 2
Date: Mon, 20 Mar 2017 19:36:42 GMT

{}
```

### Cross-Connection and Alarm Status

Once the alarm is created, it appears in the CloudWatch console and is also linked to the EC2 instance. This allows you to see the alarm status directly from the instance view. You can click on the alarm to see more details and manage it.

### Real-World Examples

#### Recent Breaches and CVEs

One notable example is the breach of GitLab runners due to insufficient monitoring and alerting. In this case, the GitLab runners ran out of disk space, leading to service disruptions. Proper monitoring and alerting could have prevented this issue.

### Pitfalls and Common Mistakes

1. **Incorrect Threshold Values**: Setting incorrect threshold values can lead to false positives or missed alerts.
2. **Insufficient Actions**: Not specifying appropriate actions (such as notifications or auto-scaling) can render the alarm ineffective.
3. **Inconsistent Metric Collection**: Ensuring consistent collection of metrics is crucial for accurate monitoring.

### How to Prevent / Defend

#### Detection

- **Regularly Review Alarms**: Regularly review and test your CloudWatch Alarms to ensure they are functioning correctly.
- **Monitor Log Files**: Use CloudWatch Logs to monitor log files for any unusual activity.

#### Prevention

- **Set Appropriate Thresholds**: Set appropriate threshold values based on historical data and expected usage patterns.
- **Configure Multiple Alarms**: Configure multiple alarms for different metrics to provide comprehensive monitoring.

#### Secure Coding Fixes

Here is an example of a vulnerable configuration and its secure counterpart:

**Vulnerable Configuration**:
```json
{
    "AlarmName": "HighCPUUtilization",
    "AlarmDescription": "Alarm when CPU exceeds 80%",
    "ActionsEnabled": false,
    "MetricName": "CPUUtilization",
    "Namespace": "AWS/EC2",
    "Statistic": "Average",
    "Period": 300,
    "Threshold": 80,
    "ComparisonOperator": "GreaterThanThreshold",
    "EvaluationPeriods": 1,
    "Dimensions": [
        {
            "Name": "InstanceId",
            "Value": "i-0123456789abcdef0"
        }
    ]
}
```

**Secure Configuration**:
```json
{
    "AlarmName": "HighCPUUtilization",
    "AlarmDescription": "Alarm when CPU exceeds 80%",
    "ActionsEnabled": true,
    "MetricName": "CPUUtilization",
    "Namespace": "AWS/EC2",
    "Statistic": "Average",
    "Period": 300,
    "Threshold": 80,
    "ComparisonOperator": "GreaterThanThreshold",
    "EvaluationPeriods": 1,
    "Dimensions": [
        {
            "Name": "InstanceId",
            "Value": "i-0123456789abcdef0"
        }
    ],
    "AlarmActions": [
        "arn:aws:sns:us-east-1:123456789012:MyTopic"
    ]
}
```

### Hardening

- **Enable Encryption**: Enable encryption for CloudWatch logs to protect sensitive data.
- **Use IAM Policies**: Use IAM policies to restrict access to CloudWatch Alarms and other resources.

### Practice Labs

For hands-on practice with CloudWatch Alarms, consider the following labs:

- **CloudGoat**: A lab environment for practicing cloud security.
- **flaws.cloud**: A lab environment for practicing cloud security.
- **AWS Official Workshops**: Official AWS workshops provide guided exercises for learning CloudWatch and other AWS services.

### Conclusion

Creating CloudWatch Alarms for EC2 instances is a critical aspect of maintaining the health and performance of your cloud infrastructure. By setting up appropriate alarms and taking proactive measures, you can ensure that your applications run smoothly and efficiently.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/04-Logging & Monitoring for Security/Create CloudWatch Alarm for EC2 Instance/01-Introduction to CloudWatch Alarms and Monitoring|Introduction to CloudWatch Alarms and Monitoring]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/04-Logging & Monitoring for Security/Create CloudWatch Alarm for EC2 Instance/00-Overview|Overview]] | [[03-Introduction to CloudWatch Alarms for EC2 Instances|Introduction to CloudWatch Alarms for EC2 Instances]]
