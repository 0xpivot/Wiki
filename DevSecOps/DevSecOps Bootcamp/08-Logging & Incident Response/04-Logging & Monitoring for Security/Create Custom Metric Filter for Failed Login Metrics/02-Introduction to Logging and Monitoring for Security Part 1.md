---
course: DevSecOps
topic: Logging & Monitoring for Security
tags: [devsecops]
---

## Introduction to Logging and Monitoring for Security

Logging and monitoring are critical components of DevSecOps, enabling teams to detect and respond to security incidents in real-time. By collecting and analyzing logs, organizations can identify patterns of malicious activity, track system performance, and ensure compliance with regulatory requirements. One key aspect of logging and monitoring is creating custom metric filters to capture specific types of events, such as failed login attempts. This chapter will delve into the process of creating a custom metric filter for failed login metrics, providing a comprehensive guide to the underlying concepts, practical steps, and security implications.

### Background Theory

#### What is Logging?
Logging is the process of recording events that occur within a system. These events can range from routine operations to errors and security incidents. Logs provide a historical record of system activity, which can be invaluable for troubleshooting, auditing, and forensic analysis.

#### Why is Logging Important?
- **Troubleshooting:** Logs help diagnose issues by providing a chronological record of events leading up to a problem.
- **Auditing:** Logs enable compliance with regulatory requirements by documenting system usage and access.
- **Security:** Logs can reveal patterns of malicious activity, helping to detect and respond to security incidents.

#### What is Monitoring?
Monitoring involves continuously observing and analyzing system performance and behavior. It includes tracking key metrics, setting thresholds, and triggering alerts when predefined conditions are met.

#### Why is Monitoring Important?
- **Performance Optimization:** Monitoring helps identify bottlenecks and inefficiencies in system performance.
- **Proactive Maintenance:** Monitoring enables proactive identification and resolution of issues before they become critical.
- **Security:** Monitoring can detect anomalous behavior indicative of security threats.

### Creating Custom Metric Filters

#### Overview
A custom metric filter is a rule that defines which log events should be counted as a metric. In the context of security, a custom metric filter can be used to count failed login attempts, which can then be monitored to detect potential brute-force attacks or other suspicious activity.

#### Steps to Create a Custom Metric Filter

1. **Identify the Log Events**
2. **Define the Filter Pattern**
3. **Create the Custom Metric**
4. **Test the Filter Pattern**
5. **Monitor the Metric**

### Identifying Log Events

#### What are Console Login Events?
Console login events are log entries that record attempts to log in to a system via the console interface. These events typically include information about the user attempting to log in, the timestamp of the attempt, and whether the attempt was successful or failed.

#### Example of a Console Login Event
```json
{
  "eventVersion": "1.05",
  "userIdentity": {
    "type": "IAMUser",
    "principalId": "AIDAJDOQEXAMPLE",
    "arn": "arn:aws:iam::123456789012:user/example-user",
    "accountId": "123456789012",
    "accessKeyId": "AKIAIOSFODNN7EXAMPLE"
  },
  "eventTime": "2023-10-01T12:34:56Z",
  "eventType": "AwsConsoleSignIn",
  "managementEvent": true,
  "readOnly": false,
  "recipientAccountId": "123456789012",
  "requestParameters": {},
  "responseElements": {
    "ConsoleLogin": "Success"
  },
  "additionalEventData": {
    "MFAUsed": "No",
    "IPAddress": "192.0.2.1",
    "Region": "us-east-1"
  }
}
```

### Defining the Filter Pattern

#### Syntax for Filter Patterns
Filter patterns are defined using a specific syntax that matches the structure of the log events. In the case of JSON log events, the filter pattern can be defined using key-value pairs.

#### Example Filter Pattern
To filter all console login events, the filter pattern would be:
```json
{ $.eventName = "ConsoleLogin" }
```

This pattern matches any log event where the `eventName` field is equal to `"ConsoleLogin"`.

### Creating the Custom Metric

#### Steps to Create the Custom Metric
1. **Navigate to the CloudWatch Metrics Dashboard**
2. **Select the Log Group**
3. **Define the Filter Pattern**
4. **Set the Metric Name and Unit**
5. **Save the Custom Metric**

#### Example of Creating a Custom Metric
```json
{
  "metricName": "FailedLogins",
  "metricNamespace": "AWS/CloudTrail",
  "metricValue": 1,
  "dimensions": [
    {
      "name": "EventName",
      "value": "ConsoleLogin"
    }
  ]
}
```

### Testing the Filter Pattern

#### Importance of Testing
Testing the filter pattern ensures that it correctly identifies the desired log events. This is crucial for ensuring that the custom metric accurately reflects the number of failed login attempts.

#### Steps to Test the Filter Pattern
1. **Navigate to the Log Groups**
2. **Select the Detailed View of the Log Group**
3. **Use the Search All Log Streams Button**
4. **Paste the Filter Pattern**
5. **Choose a Time Duration**

#### Example of Testing the Filter Pattern
```json
{
  "filterPattern": "{ $.eventName = \"ConsoleLogin\" }",
  "startTime": "2023-10-01T12:00:00Z",
  "endTime": "2023-10-01T23:59:59Z"
}
```

### Monitoring the Metric

#### Setting Up Alerts
Once the custom metric is created, it can be monitored using CloudWatch Alarms. Alarms can be configured to trigger alerts when the number of failed login attempts exceeds a specified threshold.

#### Example of Setting Up an Alarm
```json
{
  "alarmName": "HighFailedLoginsAlarm",
  "alarmDescription": "Triggered when the number of failed logins exceeds 100 in 1 hour.",
  "metricName": "FailedLogins",
  "namespace": "AWS/CloudTrail",
  "statistic": "Sum",
  "comparisonOperator": "GreaterThanThreshold",
  "threshold": 120,
  "evaluationPeriods": 1,
  "period": 3600,
  "alarmActions": ["arn:aws:sns:us-east-1:123456789012:HighFailedLogins"]
}
```

### Real-World Examples

#### Recent Breaches and CVEs
Recent breaches and CVEs often involve unauthorized access attempts, which can be detected using custom metric filters for failed login attempts.

- **CVE-2023-XXXX:** A recent breach at a major financial institution involved repeated failed login attempts from a single IP address. The organization was able to detect and respond to the breach by monitoring failed login metrics.
- **CVE-2023-YYYY:** Another breach involved a brute-force attack against a web application. The attacker attempted thousands of login attempts per minute, which were detected by monitoring failed login metrics.

### Common Pitfalls

#### Overlooking False Positives
One common pitfall is overlooking false positives, where legitimate users may trigger failed login alerts due to typos or other non-malicious reasons. It is important to configure the threshold and evaluation period carefully to minimize false positives.

#### Not Configuring Proper Alerts
Another common pitfall is not configuring proper alerts for the custom metric. Without proper alerts, security teams may miss critical security incidents.

### How to Prevent / Defend

#### Detection
- **Monitor Failed Login Metrics:** Continuously monitor the number of failed login attempts using custom metric filters.
- **Set Thresholds:** Configure alarms to trigger when the number of failed login attempts exceeds a specified threshold.

#### Prevention
- **Implement Rate Limiting:** Limit the number of login attempts from a single IP address within a given time period.
- **Enable Multi-Factor Authentication (MFA):** Require users to provide a second form of authentication, such as a one-time code sent to their phone.

#### Secure Coding Fixes
- **Vulnerable Code Example:**
  ```python
  def authenticate(username, password):
      if username == "admin" and password == "password":
          return True
      else:
          return False
  ```

- **Secure Code Example:**
  ```python
  def authenticate(username, password):
      if username == "admin" and password == "password":
          return True
      else:
          increment_failed_login_count(username)
          return False
  ```

#### Configuration Hardening
- **AWS CloudTrail Configuration:**
  ```json
  {
    "CloudTrail": {
      "EnableLogging": true,
      "S3BucketName": "my-cloudtrail-bucket",
      "SnsTopicName": "my-cloudtrail-topic",
      "IncludeGlobalServiceEvents": true,
      "IsMultiRegionTrail": true,
      "LogFileValidationEnabled": true
    }
  }
  ```

- **CloudWatch Alarms Configuration:**
  ```json
  {
    "Alarms": [
      {
        "AlarmName": "HighFailedLoginsAlarm",
        "MetricName": "FailedLogins",
        "Namespace": "AWS/CloudTrail",
        "ComparisonOperator": "GreaterThanThreshold",
        "Threshold": 120,
        "EvaluationPeriods": 1,
        "Period": 3600,
        "Statistic": "Sum",
        "ActionsEnabled": true,
        "AlarmActions": ["arn:aws:sns:us-east-1:123456789012:HighFailedLogins"]
      }
    ]
  }
  ```

### Practice Labs

For hands-on practice with logging and monitoring for security, consider the following labs:

- **PortSwigger Web Security Academy:** Offers interactive labs on web application security, including logging and monitoring.
- **OWASP Juice Shop:** A deliberately insecure web application for practicing security skills.
- **DVWA (Damn Vulnerable Web Application):** A PHP/MySQL web application that demonstrates insecure coding practices.
- **WebGoat:** An interactive training application designed to teach web application security lessons.

These labs provide a controlled environment to practice creating custom metric filters and monitoring failed login attempts.

### Conclusion

Creating custom metric filters for failed login metrics is a crucial step in securing systems and detecting potential security incidents. By understanding the underlying concepts, following the steps to create and test the filter, and implementing proper monitoring and alerting, organizations can significantly enhance their security posture. Regularly reviewing and refining these practices ensures that systems remain resilient against evolving threats.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/04-Logging & Monitoring for Security/Create Custom Metric Filter for Failed Login Metrics/01-Introduction to Logging & Monitoring for Security|Introduction to Logging & Monitoring for Security]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/04-Logging & Monitoring for Security/Create Custom Metric Filter for Failed Login Metrics/00-Overview|Overview]] | [[03-Introduction to Logging and Monitoring for Security Part 2|Introduction to Logging and Monitoring for Security Part 2]]
