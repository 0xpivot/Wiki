---
course: DevSecOps
topic: Logging & Monitoring for Security
tags: [devsecops]
---

## Logging and Monitoring for Security in DevSecOps

### Introduction to Logging and Monitoring

Logging and monitoring are critical components of DevSecOps, enabling teams to track system behavior, identify anomalies, and respond to security incidents promptly. In the context of cloud environments like AWS, logging and monitoring tools such as CloudTrail and CloudWatch play pivotal roles in ensuring comprehensive visibility and control over infrastructure activities.

### Understanding CloudTrail and CloudWatch

#### What is CloudTrail?

CloudTrail is a service that enables governance, compliance, operational auditing, and risk auditing of your AWS account. It captures API calls made to your AWS account and delivers log files to an Amazon S3 bucket. These logs provide detailed records of actions taken within your AWS environment, including:

- **API Calls**: All API calls made to your AWS services.
- **Console Actions**: Actions performed through the AWS Management Console.
- **CLI Commands**: Commands executed using the AWS CLI.
- **SDK Operations**: Operations performed using AWS SDKs.

#### Why Use CloudTrail?

CloudTrail provides several key benefits:

- **Auditability**: Detailed logs help in auditing and tracking changes made to your AWS resources.
- **Compliance**: Helps meet regulatory requirements by providing a record of all actions taken.
- **Security**: Detects unauthorized access attempts and other suspicious activities.
- **Operational Insights**: Provides insights into how your AWS resources are being used.

#### What is CloudWatch?

Amazon CloudWatch is a monitoring and observability service that provides data and actionable insights to monitor applications, respond to system-wide performance changes, optimize resource utilization, and get a unified view of operational health.

#### Why Use CloudWatch?

CloudWatch offers several advantages:

- **Real-Time Monitoring**: Monitors metrics, collects and tracks log files, and responds to changes in AWS resources.
- **Alerts and Notifications**: Sends notifications based on custom rules and thresholds.
- **Log Analysis**: Analyzes log data to identify patterns and trends.
- **Integration**: Integrates with various AWS services and third-party tools.

### Configuring Multi-Region Trail in CloudTrail

A Multi-Region Trail in CloudTrail captures API activity across multiple regions, providing a centralized view of all API calls made to your AWS account. This setup is crucial for organizations with a multi-region presence.

#### Steps to Configure Multi-Region Trail

1. **Sign in to the AWS Management Console**.
2. **Navigate to CloudTrail**.
3. **Create a new trail**:
    - **Name**: Provide a name for the trail.
    - **S3 Bucket**: Select an existing S3 bucket or create a new one.
    - **IAM Role**: Ensure the IAM role has the necessary permissions.
    - **Enable logging for all regions**: Check the box to enable logging for all regions.

```mermaid
sequenceDiagram
    participant User
    participant CloudTrail
    participant S3Bucket
    participant IAMRole

    User->>CloudTrail: Sign in to AWS Management Console
    User->>CloudTrail: Navigate to CloudTrail
    User->>CloudTrail: Create a new trail
    CloudTrail->>User: Enter trail details
    User->>CloudTrail: Enable logging for all regions
    CloudTrail->>S3Bucket: Store logs in S3 bucket
    CloudTrail->>IAMRole: Assign IAM role with necessary permissions
```

### Forwarding Logs to CloudWatch

Once CloudTrail is configured, the next step is to forward the logs to CloudWatch for further analysis and alerting.

#### Steps to Forward Logs to CloudWatch

1. **In CloudTrail**, select the trail you created.
2. **Under the "Logs" section**, click on "Configure".
3. **Select CloudWatch Logs** as the destination.
4. **Create a new log group** or select an existing one.
5. **Save the configuration**.

```mermaid
sequenceDiagram
    participant User
    participant CloudTrail
    participant CloudWatchLogs
    participant LogGroup

    User->>CloudTrail: Select the trail
    User->>CloudTrail: Navigate to "Logs" section
    User->>CloudTrail: Click on "Configure"
    User->>CloudTrail: Select CloudWatch Logs as destination
    CloudTrail->>CloudWatchLogs: Create a new log group
    CloudWatchLogs->>LogGroup: Store logs in log group
    User->>CloudTrail: Save the configuration
```

### Example of Failed Login Attempt

Let's consider an example where a user attempts to log in to the AWS console with incorrect credentials.

#### Raw Event Data

The following is an example of a failed login attempt captured by CloudTrail:

```json
{
    "eventVersion": "1.08",
    "userIdentity": {
        "type": "IAMUser",
        "principalId": "AIDAJDPLRKLG7UEXAMPLE",
        "arn": "arn:aws:iam::123456789012:user/Bob",
        "accountId": "123456789012",
        "accessKeyId": "AKIAIOSFODNN7EXAMPLE",
        "userName": "Bob",
        "sessionContext": {
            "attributes": {
                "mfaAuthenticated": "false",
                "creationDate": "2023-10-01T12:34:56Z"
            }
        }
    },
    "eventTime": "2023-10-01T12:34:56Z",
    "eventSource": "signin.amazonaws.com",
    "eventName": "ConsoleLogin",
    "awsRegion": "us-east-1",
    "sourceIPAddress": "192.0.2.0",
    "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "requestParameters": {},
    "responseElements": {
        "ConsoleLogin": "Failure",
        "Reason": "IncorrectPassword"
    },
    "additionalEventData": {
        "MFAUsed": "No",
        "RequestId": "12345678-1234-1234-1234-1234567890AB"
    },
    "eventType": "AwsConsoleSignIn",
    "recipientAccountId": "123456789012"
}
```

#### Explanation of Key Fields

- **eventVersion**: Version of the event schema.
- **userIdentity**: Details about the user performing the action.
- **eventTime**: Timestamp of the event.
- **eventSource**: Source of the event (in this case, `signin.amazonaws.com`).
- **eventName**: Name of the event (`ConsoleLogin`).
- **awsRegion**: Region where the event occurred.
- **sourceIPAddress**: IP address from which the event originated.
- **userAgent**: User agent string of the browser.
- **responseElements**: Contains the result of the login attempt (`ConsoleLogin: Failure`).
- **additionalEventData**: Additional details about the event.

### Sending Events to CloudWatch

When the failed login event is forwarded to CloudWatch, it can be analyzed and acted upon.

#### Raw HTTP Request and Response

Here is an example of the HTTP request and response for forwarding the event to CloudWatch:

```http
POST /logs HTTP/1.1
Host: logs.us-east-1.amazonaws.com
Content-Type: application/x-amz-json-1.1
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20231001/us-east-1/logs/aws4_request, SignedHeaders=content-type;host;x-amz-date, Signature=abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890
X-Amz-Date: 20231001T123456Z
Content-Length: 1234

{
    "logEvents": [
        {
            "timestamp": 1696131296000,
            "message": "{\"eventVersion\":\"1.08\",\"userIdentity\":{\"type\":\"IAMUser\",\"principalId\":\"AIDAJDPLRKLG7UEXAMPLE\",\"arn\":\"arn:aws:iam::123456789012:user/Bob\",\"accountId\":\"123456789012\",\"accessKeyId\":\"AKIAIOSFODNN7EXAMPLE\",\"userName\":\"Bob\",\"sessionContext\":{\"attributes\":{\"mfaAuthenticated\":\"false\",\"creationDate\":\"2023-10-01T12:34:56Z\"}}},\"eventTime\":\"2023-10-01T12:34:56Z\",\"eventSource\":\"signin.amazonaws.com\",\"eventName\":\"ConsoleLogin\",\"awsRegion\":\"us-east-1\",\"sourceIPAddress\":\"192.0.2.0\",\"userAgent\":\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36\",\"requestParameters\":{},\"responseElements\":{\"ConsoleLogin\":\"Failure\",\"Reason\":\"IncorrectPassword\"},\"additionalEventData\":{\"MFAUsed\":\"No\",\"RequestId\":\"12345678-1234-1234-1234-1234567890AB\"},\"eventType\":\"AwsConsoleSignIn\",\"recipientAccountId\":\"123456789012\"}"
        }
    ],
    "logStreamName": "console-login-events",
    "logGroupName": "/aws/cloudtrail/events"
}
```

```http
HTTP/1.1 200 OK
Content-Type: application/x-amz-json-1.1
Content-Length: 24
Connection: keep-alive
x-amzn-RequestId: 12345678-1234-1234-1234-1234567890AB
Date: Sun, 01 Oct 2023 12:34:56 GMT

{"rejectedLogEventsInfo":[]}
```

### Setting Up Alerts in CloudWatch

To detect and respond to failed login attempts, you can set up alerts in CloudWatch.

#### Creating an Alert Rule

1. **In CloudWatch**, navigate to the "Alarms" section.
2. **Create a new alarm**:
    - **Alarm name**: Provide a name for the alarm.
    - **Metric**: Select the metric to monitor (e.g., number of failed login attempts).
    - **Comparison operator**: Choose the comparison operator (e.g., Greater than).
    - **Threshold**: Set the threshold value (e.g., 5 failed attempts).
    - **Evaluation period**: Set the evaluation period (e.g., 1 hour).
    - **Actions**: Define the actions to take when the alarm triggers (e.g., send an email).

```mermaid
sequenceDiagram
    participant User
    participant CloudWatch
    participant Alarm

    User->>CloudWatch: Navigate to "Alarms" section
    User->>CloudWatch: Create a new alarm
    User->>CloudWatch: Provide alarm details
    CloudWatch->>Alarm: Set up alarm rule
    Alarm->>User: Trigger actions when alarm condition met
```

### Real-World Examples and Recent Breaches

#### Example: AWS Account Compromise via Brute Force Attack

In a recent breach, an attacker used a brute force attack to gain unauthorized access to an AWS account. The attacker attempted multiple login attempts with different credentials until they succeeded. This type of attack can be detected and prevented by setting up proper logging and monitoring.

#### CVE Example: CVE-2021-3504

CVE-2021-3504 is a vulnerability in AWS IAM that allows unauthorized access to AWS resources. By configuring CloudTrail and CloudWatch, organizations can detect and respond to such vulnerabilities promptly.

### How to Prevent / Defend

#### Secure Coding Practices

Ensure that IAM policies are properly configured to restrict access to sensitive resources. Use least privilege principles to minimize the risk of unauthorized access.

#### Configuration Hardening

- **Enable MFA**: Require multi-factor authentication (MFA) for all users.
- **Limit Login Attempts**: Implement rate limiting to prevent brute force attacks.
- **Monitor and Alert**: Set up alerts for failed login attempts and other suspicious activities.

#### Secure Configuration Example

Here is an example of a secure IAM policy that restricts access to specific resources:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::my-bucket",
                "arn:aws:s3:::my-bucket/*"
            ]
        }
    ]
}
```

#### Vulnerable vs. Secure Code

**Vulnerable Code**:
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

**Secure Code**:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::my-bucket",
                "arn:aws:s3:::my-bucket/*"
            ]
        }
    ]
}
```

### Conclusion

Proper logging and monitoring are essential for maintaining the security and integrity of your AWS environment. By configuring CloudTrail and CloudWatch, you can detect and respond to security incidents promptly, ensuring that your systems remain secure and compliant.

### Practice Labs

For hands-on practice with logging and monitoring in AWS, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a range of labs focused on web application security, including logging and monitoring.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for security testing.
- **CloudGoat**: A lab environment for practicing cloud security in AWS.
- **flaws.cloud**: A platform for learning and practicing cloud security.
- **Pacu**: A penetration testing framework for AWS.

These labs provide practical experience in setting up and managing logging and monitoring in cloud environments.

---
<!-- nav -->
[[14-Logging & Monitoring for Security Configuring Multi-Region Trail in CloudTrail and Forwarding Logs to CloudWatch|Logging & Monitoring for Security Configuring Multi-Region Trail in CloudTrail and Forwarding Logs to CloudWatch]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/04-Logging & Monitoring for Security/Configure Multi Region Trail in CloudTrail Forward Logs to CloudWatch/00-Overview|Overview]] | [[16-Viewing Event History in CloudTrail|Viewing Event History in CloudTrail]]
