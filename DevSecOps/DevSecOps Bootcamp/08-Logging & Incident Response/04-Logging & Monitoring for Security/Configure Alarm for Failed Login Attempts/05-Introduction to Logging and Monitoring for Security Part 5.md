---
course: DevSecOps
topic: Logging & Monitoring for Security
tags: [devsecops]
---

## Introduction to Logging and Monitoring for Security

In the realm of DevSecOps, logging and monitoring are foundational practices that enable proactive security management. By combining cloud trail events and CloudWatch, you can create a robust system to detect and respond to suspicious activities, such as failed login attempts. This chapter will delve into the details of configuring alarms for failed login attempts, explaining the underlying concepts, providing real-world examples, and offering practical guidance on how to implement and defend against potential threats.

### What Are Cloud Trail Events?

CloudTrail is an AWS service that enables governance, compliance, operational auditing, and risk auditing of your AWS account. It captures API calls made to your AWS account and delivers log files to an Amazon S3 bucket. These log files contain detailed information about the API calls, including the identity of the API caller, the time of the API call, the source IP address, and the request parameters.

#### Why Use CloudTrail?

- **Audit and Compliance**: CloudTrail logs provide a comprehensive record of actions taken within your AWS environment, which is crucial for compliance with regulatory requirements.
- **Operational Auditing**: You can track changes to resources and configurations, helping you understand who did what and when.
- **Security Monitoring**: By analyzing CloudTrail logs, you can identify unauthorized access attempts, unusual activity patterns, and other security incidents.

### What Is CloudWatch?

Amazon CloudWatch is a monitoring and observability service provided by AWS. It collects and tracks metrics, collects and monitors log files, and responds to system-wide performance changes. CloudWatch provides a unified view of your AWS resources, applications, and services.

#### Why Use CloudWatch?

- **Real-Time Monitoring**: CloudWatch allows you to monitor your AWS resources in real-time, providing immediate alerts for critical issues.
- **Custom Metrics**: You can define custom metrics to track specific aspects of your application's performance.
- **Alarms and Notifications**: CloudWatch can trigger alarms based on specific conditions and send notifications via email, SMS, or other channels.

### Combining CloudTrail and CloudWatch

By integrating CloudTrail and CloudWatch, you can create a powerful system for detecting and responding to security incidents. Here’s how it works:

1. **CloudTrail Logs**: CloudTrail captures API calls and writes them to an S3 bucket.
2. **CloudWatch Logs**: CloudWatch can ingest these logs and analyze them for specific patterns or anomalies.
3. **Alarms and Notifications**: Based on predefined conditions, CloudWatch can trigger alarms and send notifications to your team.

### Configuring Alarms for Failed Login Attempts

To configure alarms for failed login attempts, you need to set up CloudTrail to capture relevant API calls and then configure CloudWatch to monitor these logs and trigger alarms when necessary.

#### Step-by-Step Configuration

1. **Enable CloudTrail**:
    - Navigate to the CloudTrail console in the AWS Management Console.
    - Click on "Create trail".
    - Choose the S3 bucket where you want CloudTrail logs to be delivered.
    - Enable logging for all regions and services.
    - Click "Create".

2. **Configure CloudWatch Logs**:
    - In the CloudWatch console, navigate to "Logs".
    - Click on "Create log group".
    - Name the log group (e.g., `FailedLoginAttempts`).
    - Click "Create".

3. **Set Up Subscription Filter**:
    - In the CloudTrail console, navigate to the trail you created.
    - Click on "Edit trail".
    - Under "Advanced settings", enable "Send trail to CloudWatch Logs".
    - Select the log group you created earlier.
    - Click "Save".

4. **Create CloudWatch Metric Filter**:
    - In the CloudWatch console, navigate to "Logs".
    - Select the log group you created.
    - Click on "Metric filters".
    - Click "Create metric filter".
    - Define the filter pattern to match failed login attempts (e.g., `$.eventName = "ConsoleLogin"` and `$.errorCode = "InvalidClientTokenId"`).
    - Assign a metric name (e.g., `FailedLogins`).
    - Click "Create metric filter".

5. **Create CloudWatch Alarm**:
    - In the CloudWatch console, navigate to "Alarms".
    - Click "Create alarm".
    - Select the metric you created (`FailedLogins`).
    - Set the threshold (e.g., 3 failed logins in 5 minutes).
    - Configure the notification settings (e.g., send an email to your team).
    - Click "Create alarm".

### Real-World Example: Recent Breach

Consider the recent breach at Capital One in 2019, where a hacker accessed sensitive data of over 100 million customers. One of the key factors in this breach was the lack of proper logging and monitoring. Had the organization had a robust logging and monitoring system in place, they might have detected the unauthorized access attempts and taken preventive measures.

#### How to Prevent / Defend

1. **Secure Configuration**:
    - Ensure that CloudTrail is enabled for all regions and services.
    - Configure CloudWatch to monitor relevant logs and trigger alarms based on specific conditions.

2. **Detection**:
    - Regularly review CloudTrail logs for suspicious activity.
    - Use CloudWatch to monitor for failed login attempts and other security-related events.

3. **Prevention**:
    - Implement multi-factor authentication (MFA) to reduce the risk of unauthorized access.
    - Use IAM policies to restrict access to sensitive resources.

4. **Incident Response**:
    - Develop an incident response plan that includes steps to isolate affected systems and investigate the cause of the alarm.
    - Conduct regular security audits to ensure compliance with best practices.

### Complete Example: Full HTTP Request and Response

Here is a complete example of how to configure CloudWatch to monitor failed login attempts:

```http
POST /logs HTTP/1.1
Host: logs.region.amazonaws.com
Content-Type: application/json
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20190709/us-east-1/cloudwatch/aws4_request, SignedHeaders=content-type;host;x-amz-date, Signature=fe5f4faa6b30aa4e9a9345b9c597d6c0b6e5e8cc961cdce5f1691c2f6597fbfa
X-Amz-Date: 20190709T214100Z

{
  "logEvents": [
    {
      "timestamp": 1562709660000,
      "message": "{\"eventVersion\":\"1.05\",\"userIdentity\":{\"type\":\"IAMUser\",\"principalId\":\"AIDAJDPLRKLG7UEXAMPLE\",\"arn\":\"arn:aws:iam::123456789012:user/Maria\",\"accountId\":\"123456789012\",\"accessKeyId\":\"AKIAIOSFODNN7EXAMPLE\",\"userName\":\"Maria\",\"sessionContext\":{\"attributes\":{\"mfaAuthenticated\":\"false\",\"creationDate\":\"2019-07-09T21:41:00Z\"}}},\"eventTime\":\"2019-07-09T21:41:00Z\",\"eventSource\":\"iam.amazonaws.com\",\"eventName\":\"ConsoleLogin\",\"awsRegion\":\"us-east-1\",\"sourceIPAddress\":\"203.0.113.18\",\"userAgent\":\"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36\",\"requestParameters\":null,\"responseElements\":null,\"additionalEventData\":{\"MFAUsed\":\"No\",\"LoginTo\":\"https://console.aws.amazon.com/\",\"MobileVersion\":\"No\"},\"requestID\":\"12345678-1234-1234-1234-123456789012\",\"eventID\":\"12345678-1234-1234-1234-123456789012\",\"eventType\":\"AwsApiCall\",\"recipientAccountId\":\"1234567123456789012\"}"
    }
  ],
  "logStreamName": "FailedLoginAttempts",
  "logGroupName": "/aws/lambda/FailedLoginAttempts"
}
```

### Mermaid Diagrams

#### CloudTrail and CloudWatch Integration

```mermaid
graph TD
    A[CloudTrail] --> B[API Calls]
    B --> C[S3 Bucket]
    C --> D[CloudWatch Logs]
    D --> E[Metric Filters]
    E --> F[Alarms]
    F --> G[Notifications]
```

### Common Pitfalls and Best Practices

#### Common Pitfalls

- **Incomplete Logging**: Not capturing all relevant API calls can lead to blind spots in your security monitoring.
- **False Positives**: Overly broad alarm conditions can result in frequent false positives, leading to alert fatigue.
- **Insufficient Access Controls**: Failing to properly restrict access to CloudTrail and CloudWatch can expose sensitive data.

#### Best Practices

- **Regular Audits**: Conduct regular security audits to ensure compliance with best practices.
- **Multi-Factor Authentication**: Implement MFA to reduce the risk of unauthorized access.
- **Least Privilege Principle**: Follow the least privilege principle to minimize the risk of accidental or malicious damage.

### Hands-On Labs

For hands-on practice, consider using the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice web security concepts.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning web security.
- **WebGoat**: An interactive training application designed to teach web application security lessons.

### Conclusion

By combining CloudTrail and CloudWatch, you can create a powerful system for detecting and responding to security incidents. This chapter has covered the essential concepts, provided real-world examples, and offered practical guidance on how to implement and defend against potential threats. With a robust logging and monitoring system in place, you can proactively secure your systems and take preventive measures to mitigate risks.

---
<!-- nav -->
[[04-Introduction to Logging and Monitoring for Security Part 4|Introduction to Logging and Monitoring for Security Part 4]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/04-Logging & Monitoring for Security/Configure Alarm for Failed Login Attempts/00-Overview|Overview]] | [[06-Introduction to Logging and Monitoring for Security|Introduction to Logging and Monitoring for Security]]
