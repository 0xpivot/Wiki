---
course: DevSecOps
topic: Logging & Monitoring for Security
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain how CloudWatch alarms help in managing EC2 instances.**

CloudWatch alarms help in managing EC2 instances by providing automated proactive notifications when certain conditions are met. For example, if an EC2 instance goes down due to termination or crashes, a CloudWatch alarm can notify the administrator via email or trigger an automated action such as restarting the instance. This ensures that the administrator is aware of any issues and can take immediate action to resolve them, thereby maintaining the health and availability of the EC2 instances.

**Q2. How would you configure a CloudWatch alarm to notify you when an EC2 instance is down?**

To configure a CloudWatch alarm to notify you when an EC2 instance is down, follow these steps:

1. Navigate to the CloudWatch console and select "Alarms."
2. Click on "Create alarm."
3. Select the metric "Status Check Failed (Instance)" under the EC2 category.
4. Choose the specific EC2 instance ID you want to monitor.
5. Set the threshold to trigger the alarm when the status check fails (e.g., greater than zero).
6. Configure the notification settings by creating a new SNS topic and subscribing your email address.
7. Name the alarm (e.g., "EC2 instance down").
8. Review and create the alarm.

Here’s an example of setting up the alarm programmatically using AWS CLI:

```bash
aws cloudwatch put-metric-alarm \
--alarm-name "EC2InstanceDown" \
--metric-name StatusCheckFailed_Instance \
--namespace AWS/EC2 \
--statistic Sum \
--period 300 \
--threshold 1 \
--comparison-operator GreaterThanThreshold \
--dimensions Name=InstanceId,Value=i-0123456789abcdef0 \
--evaluation-periods 1 \
--alarm-actions arn:aws:sns:us-east-1:123456789012:MyTopic
```

**Q3. Why is it important to monitor the status check failed metric for EC2 instances?**

Monitoring the status check failed metric for EC2 instances is crucial because it indicates that the instance is not responding or is inaccessible. This could be due to various reasons such as hardware failure, network issues, or software crashes. By setting up an alarm for this metric, administrators can be promptly notified of any issues, allowing them to investigate and resolve the problem quickly. This helps in maintaining the reliability and availability of the EC2 instances, ensuring that applications hosted on these instances continue to function properly.

**Q4. How can you automate the recovery process when an EC2 instance is down using CloudWatch alarms?**

To automate the recovery process when an EC2 instance is down using CloudWatch alarms, you can configure the alarm to trigger an automated action when the instance status check fails. Here’s how you can do it:

1. Set up the CloudWatch alarm as described in Q2.
2. Under the "Actions" section, add an action to be performed when the alarm is triggered.
3. Choose an action such as "Reboot instance" or "Restart instance" using Systems Manager or EC2 actions.
4. Ensure that the IAM role associated with the EC2 instance has the necessary permissions to perform these actions.

Here’s an example of setting up an automated action using AWS CLI:

```bash
aws cloudwatch put-metric-alarm \
--alarm-name "EC2InstanceDown" \
--metric-name StatusCheckFailed_Instance \
--namespace AWS/EC2 \
--statistic Sum \
--period 300 \
--threshold 1 \
--comparison-operator GreaterThanThreshold \
--dimensions Name=InstanceId,Value=i-0123456789abcdef0 \
--evaluation-periods 1 \
--alarm-actions arn:aws:automate:us-east-1:instance-reboot
```

**Q5. What are the different states of a CloudWatch alarm and how do they work?**

CloudWatch alarms have three states: `OK`, `ALARM`, and `INSUFFICIENT_DATA`.

- **OK**: The metric is within the defined threshold. For example, if the threshold is set to greater than zero and the metric value is zero, the alarm state is `OK`.
- **ALARM**: The metric exceeds the defined threshold. For example, if the threshold is set to greater than zero and the metric value is greater than zero, the alarm state is `ALARM`.
- **INSUFFICIENT_DATA**: The alarm has not yet collected enough data to determine whether the metric is within the threshold. This typically occurs when the alarm is first created or if the metric data is not available.

These states help in understanding the current status of the monitored metric and taking appropriate actions based on the state.

**Q6. How can you use CloudWatch logs to troubleshoot issues with EC2 instances?**

CloudWatch logs can be used to troubleshoot issues with EC2 instances by analyzing the log data collected from the instances. Here’s how you can use CloudWatch logs:

1. Enable CloudWatch logging for your EC2 instances.
2. Use the CloudWatch Logs Insights feature to query and analyze the log data.
3. Look for error messages, warnings, or other indicators of issues in the logs.
4. Correlate the log data with the CloudWatch metrics and alarms to identify the root cause of the problem.

For example, if an EC2 instance goes down, you can check the CloudWatch logs to see if there were any errors or warnings that might indicate why the instance failed. This can help in diagnosing and resolving the issue.

**Q7. What recent real-world examples demonstrate the importance of monitoring EC2 instances with CloudWatch alarms?**

Recent real-world examples include:

- **GitLab Incident (CVE-2021-22205)**: In this incident, GitLab experienced a significant outage due to resource exhaustion on their EC2 instances. If they had configured CloudWatch alarms to monitor CPU and memory usage, they could have received early notifications and taken preventive actions to avoid the outage.
  
- **AWS Outage (February 2022)**: During this outage, multiple AWS regions experienced disruptions, leading to unavailability of EC2 instances. CloudWatch alarms could have helped in identifying the affected instances and triggering automated recovery processes, reducing the impact of the outage.

These examples highlight the importance of monitoring EC2 instances with CloudWatch alarms to ensure high availability and quick recovery from potential issues.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/04-Logging & Monitoring for Security/Create CloudWatch Alarm for EC2 Instance/11-Introduction to Logging and Monitoring for Security|Introduction to Logging and Monitoring for Security]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/04-Logging & Monitoring for Security/Create CloudWatch Alarm for EC2 Instance/00-Overview|Overview]]
