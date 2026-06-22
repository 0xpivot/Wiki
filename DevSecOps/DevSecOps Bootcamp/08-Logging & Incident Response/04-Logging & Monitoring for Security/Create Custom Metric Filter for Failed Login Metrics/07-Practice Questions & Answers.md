---
course: DevSecOps
topic: Logging & Monitoring for Security
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the process of creating a custom metric filter for failed login events in AWS CloudWatch Logs.**

To create a custom metric filter for failed login events in AWS CloudWatch Logs, follow these steps:

1. **Identify the Log Group**: Navigate to the CloudWatch Logs service and identify the log group containing the login events. For example, the log group might contain CloudTrail data.

2. **Create a Metric Filter**: Go to the Actions menu for the selected log group and choose "Create metric filter". 

3. **Define the Filter Pattern**: Use a filter pattern to match specific log events. For failed login events, the pattern might look like:
   ```json
   { $.eventName = "ConsoleLogin" && $.errorMessage = "Failed authentication" }
   ```
   This pattern matches any log events where `eventName` is `ConsoleLogin` and `errorMessage` includes `Failed authentication`.

4. **Test the Filter Pattern**: Use the test feature to ensure the pattern matches the desired log events. You can test with a specific chunk of log data or the entire log group.

5. **Configure the Metric Details**: Name the metric filter appropriately, such as "FailedLogin". Define the metric namespace (e.g., `LoginNamespace`) and the metric name (e.g., `FailedLogin`). Set the metric value to 1 for each occurrence of the failed login event.

6. **Create the Metric Filter**: Save the configuration to create the custom metric filter.

7. **Verify the Metric**: Ensure the custom metric appears in the CloudWatch Metrics dashboard after a failed login event occurs.

**Q2. How would you exploit a misconfigured CloudWatch metric filter for failed login events?**

A misconfigured CloudWatch metric filter for failed login events could potentially allow unauthorized access or provide insights into security weaknesses. Here’s how an attacker might exploit it:

1. **Identify Misconfiguration**: Check if the metric filter is not properly configured to capture all failed login events. For example, the filter pattern might miss certain types of failed login events due to incorrect syntax or incomplete conditions.

2. **Exploit Weaknesses**: If the filter misses some failed login events, an attacker could repeatedly attempt to log in with different credentials until they find a combination that slips past the filter.

3. **Monitor Metrics**: An attacker could monitor the custom metric to determine when failed login attempts are not being captured. This could indicate a window of opportunity to exploit the system.

4. **Automate Attacks**: Using automated tools, an attacker could systematically try different combinations of credentials and monitor the custom metric to identify successful bypasses.

**Q3. Why is it important to ensure that the custom metric filter for failed login events captures all relevant events?**

Ensuring that the custom metric filter for failed login events captures all relevant events is crucial for several reasons:

1. **Security Monitoring**: Accurate monitoring helps detect potential security breaches early. Missing failed login events can lead to undetected unauthorized access attempts.

2. **Compliance Requirements**: Many compliance standards require detailed logging and monitoring of access attempts. Failing to capture all failed login events can result in non-compliance.

3. **Incident Response**: Comprehensive logging aids in incident response by providing a complete picture of attempted access. This information is vital for understanding the scope and nature of an attack.

4. **Trend Analysis**: Capturing all failed login events allows for trend analysis, helping to identify patterns and potential vulnerabilities in the authentication process.

**Q4. How would you configure an alarm based on the custom metric filter for failed login events?**

To configure an alarm based on the custom metric filter for failed login events, follow these steps:

1. **Navigate to Alarms**: In the CloudWatch console, go to the "Alarms" section.

2. **Create a New Alarm**: Click on "Create alarm".

3. **Select the Metric**: Choose the custom metric namespace (`LoginNamespace`) and the metric name (`FailedLogin`) that you created earlier.

4. **Set the Threshold**: Define the threshold for triggering the alarm. For example, you might set the alarm to trigger if there are more than 5 failed login attempts within a 1-hour period.

5. **Configure the Alarm Settings**: Specify the actions to take when the alarm state changes, such as sending notifications via SNS (Simple Notification Service).

6. **Review and Create**: Review the settings and create the alarm.

Example configuration:
```plaintext
Metric: LoginNamespace.FailedLogin
Comparison Operator: GreaterThanThreshold
Threshold: 5
Period: 1 hour
Evaluation Periods: 1
```

This setup ensures that you are alerted promptly if there are multiple failed login attempts, allowing for timely intervention.

**Q5. What recent real-world examples illustrate the importance of monitoring failed login events?**

Recent real-world examples highlight the importance of monitoring failed login events:

1. **SolarWinds Supply Chain Attack (CVE-2020-1014)**: This attack involved the compromise of SolarWinds software, leading to unauthorized access to numerous organizations. Monitoring failed login events could have helped detect unusual access patterns and alert administrators to potential breaches.

2. **Colonial Pipeline Ransomware Attack (May 2021)**: The attackers gained access to the network through a compromised password. Monitoring failed login attempts could have flagged repeated unsuccessful login attempts, indicating a potential brute-force attack.

In both cases, robust monitoring of failed login events could have provided early warnings and facilitated quicker responses to security incidents.

---
<!-- nav -->
[[06-Logging & Monitoring for Security Creating Custom Metric Filters for Failed Login Metrics|Logging & Monitoring for Security Creating Custom Metric Filters for Failed Login Metrics]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/04-Logging & Monitoring for Security/Create Custom Metric Filter for Failed Login Metrics/00-Overview|Overview]]
