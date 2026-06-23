---
course: DevSecOps
topic: Logging & Monitoring for Security
tags: [devsecops]
---

## Introduction to Logging and Monitoring for Security

Logging and monitoring are critical components of DevSecOps, providing visibility into system behavior and enabling proactive identification and mitigation of security issues. In this section, we will delve into the creation of custom metric filters for tracking failed login attempts, specifically within the context of AWS CloudWatch Logs and CloudTrail.

### Background Theory

#### What is Logging?
Logging is the process of recording events that occur during the operation of a system. These logs provide valuable information about the system's behavior, including errors, warnings, and normal operations. In a security context, logs can help identify unauthorized access attempts, suspicious activities, and potential breaches.

#### What is Monitoring?
Monitoring involves continuously observing and analyzing the logs to detect anomalies and alert on significant events. Effective monitoring ensures that security incidents are identified promptly, allowing for timely response and mitigation.

### Why Track Failed Login Attempts?

Tracking failed login attempts is crucial for several reasons:

1. **Early Detection of Brute-Force Attacks**: Frequent failed login attempts can indicate a brute-force attack, where an attacker tries to guess passwords through repeated attempts.
2. **Identifying Suspicious Activity**: Unusual patterns of failed login attempts can signal unauthorized access attempts or insider threats.
3. **Compliance Requirements**: Many regulatory frameworks require organizations to monitor and report on failed login attempts as part of their compliance obligations.

### How to Track Failed Login Attempts Using AWS CloudWatch Logs and CloudTrail

AWS CloudWatch Logs and CloudTrail are powerful tools for logging and monitoring activities within an AWS environment. By leveraging these services, we can create custom metric filters to track failed login attempts.

#### Step-by-Step Guide

1. **Enable CloudTrail**:
   - CloudTrail records API calls made within your AWS account and delivers log files to an Amazon S3 bucket.
   - Ensure CloudTrail is enabled and configured to deliver logs to a specific S3 bucket.

2. **Configure CloudWatch Logs**:
   - CloudWatch Logs collects and monitors log files from EC2 instances, AWS CloudTrail, and other sources.
   - Set up a log group to store the CloudTrail logs.

3. **Create a Custom Metric Filter**:
   - A metric filter allows you to extract specific data from log events and publish it to CloudWatch Metrics.
   - Define a pattern that matches failed login events and create a metric filter based on this pattern.

### Detailed Example: Creating a Custom Metric Filter for Failed Login Attempts

Let's walk through the process of creating a custom metric filter for tracking failed login attempts in the AWS Management Console.

#### Step 1: Enable CloudTrail

First, ensure that CloudTrail is enabled and configured to deliver logs to an S3 bucket.

```mermaid
sequenceDiagram
    participant User
    participant CloudTrail
    participant S3
    User->>CloudTrail: Enable CloudTrail
    CloudTrail->>S3: Deliver Log Files
```

#### Step 2: Configure CloudWatch Logs

Next, configure CloudWatch Logs to collect the CloudTrail logs.

```mermaid
sequenceDiagram
    participant User
    participant CloudTrail
    participant CloudWatchLogs
    User->>CloudTrail: Enable CloudTrail
    CloudTrail->>CloudWatchLogs: Deliver Log Files
```

#### Step 3: Create a Custom Metric Filter

Now, let's create a custom metric filter to track failed login attempts.

1. **Select the Log Group**:
   - Navigate to the CloudWatch Logs console.
   - Select the log group that contains the CloudTrail logs.

2. **Create a Metric Filter**:
   - Click on the "Actions" menu and select "Create metric filter".
   - Define a pattern that matches failed login events.

Here is an example of a CloudWatch Logs filter pattern for failed login attempts:

```json
{
  "logEvents": [
    {
      "timestamp": 1633072800000,
      "message": "{\n  \"eventVersion\": \"1.08\",\n  \"userIdentity\": {\n    \"type\": \"IAMUser\",\n    \"principalId\": \"AIDAJDPLRKLG7UEXAMPLE\",\n    \"arn\": \"arn:aws:iam::123456789012:user/Alice\",\n    \"accountId\": \"123456789012\",\n    \"accessKeyId\": \"AKIAIOSFODNN7EXAMPLE\",\n    \"userName\": \"Alice\"\n  },\n  \"eventTime\": \"2021-09-30T12:00:00Z\",\n  \"eventSource\": \"signin.amazonaws.com\",\n  \"eventName\": \"ConsoleLogin\",\n  \"awsRegion\": \"us-east-1\",\n  \"sourceIPAddress\": \"192.0.2.0\",\n  \"userAgent\": \"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.82 Safari/537.36\",\n  \"requestParameters\": null,\n  \"responseElements\": {\n    \"ConsoleLogin\": {\n      \"AuthenticationResult\": {\n        \"Status\": \"Failure\",\n        \"Reason\": \"Incorrect password\"\n      }\n    }\n  },\n  \"additionalEventData\": {\n    \"MFAUsed\": \"No\",\n    \"RequestId\": \"12345678-1234-1234-1234-123456789012\"\n  },\n  \"eventType\": \"AwsApiCall\",\n  \"managementEvent\": true,\n  \"readOnly\": false,\n  \"recipientAccountId\": \"123456789012\",\n  \"sharedEventID\": \"12345678-1234-1234-1234-123456789012\"\n}"
    }
  ]
}
```

Define a filter pattern that matches failed login events:

```json
{
  "filterPattern": "{ $.eventName = \"ConsoleLogin\" && $.responseElements.ConsoleLogin.AuthenticationResult.Status = \"Failure\" }"
}
```

3. **Publish to CloudWatch Metrics**:
   - Specify the metric namespace and dimensions.
   - For example, you might set the namespace to `AWS/CloudTrail` and the dimension to `FailedLogins`.

Here is the complete process in a sequence diagram:

```mermaid
sequenceDiagram
    participant User
    participant CloudWatchLogs
    participant CloudWatchMetrics
    User->>CloudWatchLogs: Define Filter Pattern
    CloudWatchLogs->>CloudWatchMetrics: Publish to Metrics
```

### Full HTTP Request and Response Example

When creating a metric filter via the AWS Management Console, the following HTTP request and response are generated:

#### HTTP Request

```http
POST /logs/metricFilters HTTP/1.1
Host: logs.us-east-1.amazonaws.com
Content-Type: application/x-amz-json-1.1
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20210930/us-east-1/logs/aws4_request, SignedHeaders=content-type;host;x-amz-date, Signature=abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890
X-Amz-Date: 20210930T120000Z
Content-Length: 123

{
  "logGroupName": "/aws/cloudtrail/MyCloudTrail",
  "filterName": "FailedLoginFilter",
  "filterPattern": "{ $.eventName = \"ConsoleLogin\" && $.responseElements.ConsoleLogin.AuthenticationResult.Status = \"Failure\" }",
  "metricTransformations": [
    {
      "metricName": "FailedLogins",
      "metricNamespace": "AWS/CloudTrail",
      "metricValue": "1"
    }
  ]
}
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Content-Type: application/x-amz-json-1.1
Content-Length: 123
Date: Thu, 30 Sep 2021 12:00:00 GMT

{
  "filterArn": "arn:aws:logs:us-east-1:123456789012:metric-filter:/aws/cloudtrail/MyCloudTrail/FailedLoginFilter"
}
```

### Real-World Examples and Recent Breaches

Recent breaches have highlighted the importance of monitoring failed login attempts. For instance, the SolarWinds breach involved attackers gaining access to systems through compromised credentials. By monitoring failed login attempts, organizations could have detected unusual activity and taken preventive measures.

### Common Pitfalls and Best Practices

#### Common Pitfalls

1. **Inadequate Logging**: Failing to log all relevant events can lead to blind spots in monitoring.
2. **Insufficient Monitoring**: Not setting up alerts for critical events can delay detection and response.
3. **Complex Patterns**: Overly complex filter patterns can lead to missed events or false positives.

#### Best Practices

1. **Centralize Logging**: Use a centralized logging solution to aggregate logs from various sources.
2. **Regular Audits**: Regularly review and audit log data to identify patterns and anomalies.
3. **Automated Alerts**: Set up automated alerts for critical events to ensure timely response.

### How to Prevent / Defend

#### Detection

1. **Set Up Alerts**: Configure alerts for high volumes of failed login attempts.
2. **Monitor Anomalies**: Use machine learning algorithms to detect unusual patterns in login attempts.

#### Prevention

1. **Multi-Factor Authentication (MFA)**: Require MFA for all users to reduce the risk of unauthorized access.
2. **Password Policies**: Enforce strong password policies to prevent weak passwords.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of the code:

##### Vulnerable Code

```python
def authenticate(username, password):
    user = get_user_by_username(username)
    if user and user.password == password:
        return True
    return False
```

##### Secure Code

```python
import bcrypt

def authenticate(username, password):
    user = get_user_by_username(username)
    if user and bcrypt.checkpw(password.encode('utf-8'), user.hashed_password):
        return True
    return False
```

### Configuration Hardening

#### IAM Policy Example

Ensure IAM policies are configured to restrict access to sensitive resources:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": [
        "iam:*"
      ],
      "Resource": "*",
      "Condition": {
        "NumericGreaterThan": {
          "aws:FailedAttempts": 5
        }
      }
    }
  ]
}
```

### Hands-On Labs

To practice these concepts, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice web security techniques.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates web application vulnerabilities.

By mastering the creation of custom metric filters for tracking failed login attempts, you can significantly enhance your organization's security posture and proactively defend against unauthorized access attempts.

---
<!-- nav -->
[[04-Introduction to Logging and Monitoring for Security Part 3|Introduction to Logging and Monitoring for Security Part 3]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/04-Logging & Monitoring for Security/Create Custom Metric Filter for Failed Login Metrics/00-Overview|Overview]] | [[06-Logging & Monitoring for Security Creating Custom Metric Filters for Failed Login Metrics|Logging & Monitoring for Security Creating Custom Metric Filters for Failed Login Metrics]]
