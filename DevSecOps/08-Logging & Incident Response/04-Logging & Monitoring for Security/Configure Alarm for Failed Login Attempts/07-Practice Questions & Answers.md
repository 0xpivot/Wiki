---
course: DevSecOps
topic: Logging & Monitoring for Security
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain why setting up an alarm for failed login attempts is crucial for system security.**

Failed login attempts can indicate potential security threats such as brute force attacks or unauthorized access attempts. Setting up an alarm helps in identifying these threats early, allowing administrators to take immediate actions like blocking IP addresses, reviewing logs, or enhancing security measures. This proactive approach is essential in preventing breaches and securing systems effectively.

**Q2. How would you configure an alarm for failed login attempts in AWS CloudWatch?**

To configure an alarm for failed login attempts in AWS CloudWatch, follow these steps:

1. **Select Metric**: Choose the metric namespace related to login attempts, typically under `AWS/CloudTrail` or a custom namespace.
2. **Select Statistic**: Use the `Sum` statistic to count the total number of failed login attempts.
3. **Set Threshold**: Define a threshold, e.g., 7 failed login attempts.
4. **Configure Period**: Set the period to 5 minutes.
5. **Create Topic**: Create an SNS topic to receive notifications.
6. **Subscribe to Topic**: Subscribe an email address to the SNS topic.
7. **Name the Alarm**: Give the alarm a descriptive name, such as "Multiple Failed Logins".
8. **Create Alarm**: Finalize the creation of the alarm.

Here’s a sample configuration snippet:

```python
import boto3

cloudwatch = boto3.client('cloudwatch')

response = cloudwatch.put_metric_alarm(
    AlarmName='Multiple Failed Logins',
    ComparisonOperator='GreaterThanThreshold',
    EvaluationPeriods=1,
    MetricName='FailedLoginAttempts',
    Namespace='Custom/Login',
    Period=300,
    Statistic='Sum',
    Threshold=7,
    ActionsEnabled=True,
    AlarmActions=['arn:aws:sns:region:account-id:topic-name'],
    OKActions=[],
    InsufficientDataActions=[],
)
```

**Q3. Why is it important to monitor failed login attempts within a specific time period (e.g., 5 minutes)?**

Monitoring failed login attempts within a specific time period, such as 5 minutes, helps in detecting patterns indicative of malicious activity. For instance, multiple failed login attempts within a short duration might suggest a brute force attack. By setting a threshold and monitoring within a specific period, you can quickly identify and respond to such threats, thereby enhancing system security.

**Q4. How can you leverage event history in CloudTrail to investigate failed login attempts?**

Event history in CloudTrail provides detailed logs of API calls made to AWS services, including login attempts. To investigate failed login attempts:

1. **Review Event History**: Check the event history to identify failed login attempts.
2. **Analyze User Agent**: Determine the type of user agent (browser, CLI, etc.) used for login attempts.
3. **Check IP Address**: Identify the source IP address of the failed login attempts.
4. **Take Action**: Based on the findings, take appropriate actions like blocking the IP address or enhancing security measures.

For example, if you notice multiple failed login attempts from a single IP address, you can block that IP address to prevent further unauthorized access attempts.

**Q5. What recent real-world examples demonstrate the importance of monitoring failed login attempts?**

One notable example is the 2021 SolarWinds breach, where attackers exploited a vulnerability to gain unauthorized access to systems. Monitoring failed login attempts could have helped detect unusual access patterns and alerted administrators to the breach earlier. Another example is the widespread use of brute force attacks targeting SSH and RDP services, where monitoring and alarming on failed login attempts can help mitigate such threats.

**Q6. How would you handle the scenario where the alarm goes into an 'Insufficient Data' state due to no failed login attempts?**

When the alarm goes into an 'Insufficient Data' state due to no failed login attempts, you can configure the alarm to treat missing data as being within the threshold. Here’s how:

1. **Edit Alarm Configuration**: Go to the CloudWatch console and edit the alarm configuration.
2. **Set Missing Data Handling**: Choose the option to treat missing data as being within the threshold.
3. **Update Alarm**: Save the changes to ensure the alarm remains in an 'OK' state when there are no failed login attempts.

This ensures that the alarm does not trigger false alerts and remains effective in monitoring actual security threats.

---
<!-- nav -->
[[06-Introduction to Logging and Monitoring for Security|Introduction to Logging and Monitoring for Security]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/04-Logging & Monitoring for Security/Configure Alarm for Failed Login Attempts/00-Overview|Overview]]
