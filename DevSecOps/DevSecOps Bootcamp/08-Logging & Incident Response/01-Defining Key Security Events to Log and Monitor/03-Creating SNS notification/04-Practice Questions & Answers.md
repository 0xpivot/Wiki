---
course: DevSecOps
topic: Defining Key Security Events to Log and Monitor
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the purpose of AWS Config and how it relates to monitoring S3 bucket changes.**

AWS Config provides a detailed view of the resources associated with your AWS account, including how they are configured, how they are related to one another, and how the configurations and their relationships have changed over time. For monitoring S3 bucket changes, AWS Config can continuously watch the S3 bucket for any modifications, such as making the bucket publicly accessible. When a change is detected, AWS Config can trigger an alert, which can be sent via the SNS service.

**Q2. How does AWS SNS work in conjunction with AWS Config to send alerts?**

AWS SNS (Simple Notification Service) works by creating a topic to which subscribers can be added. When AWS Config detects a change in the configuration of an S3 bucket, it sends a message to the SNS topic. The SNS topic then forwards the message to all subscribed endpoints, such as email addresses or mobile devices. In the context of the demo, an email alert is sent to the specified email address when the S3 bucket configuration changes.

**Q3. Describe the steps involved in setting up an SNS topic and subscription for receiving email alerts.**

To set up an SNS topic and subscription for receiving email alerts:

1. Navigate to the SNS service in the AWS Management Console.
2. Click on "Topics" and then "Create topic".
3. Choose the "Standard" type and provide a name for the topic (e.g., "WBC SNS").
4. Click "Create topic".
5. Click on "Subscriptions" and then "Create subscription".
6. Select "Email" as the protocol.
7. Enter the email address where you want to receive the alerts.
8. Click "Create subscription".
9. Go to the specified email address and confirm the subscription by clicking the link in the confirmation email.

**Q4. Why is it important to ensure that the SNS subscription is confirmed before it becomes active?**

It is crucial to confirm the SNS subscription because the confirmation process ensures that the intended recipient actually wants to receive the notifications. Without confirmation, the subscription remains inactive, meaning no alerts will be sent to the specified email address. This prevents unauthorized or unintended recipients from receiving sensitive information and helps maintain the integrity and security of the notification system.

**Q5. What recent real-world examples or CVEs highlight the importance of monitoring S3 bucket configurations and sending alerts when changes occur?**

One notable example is the breach involving Capital One in 2019 (CVE-2019-11618). An attacker gained unauthorized access to a misconfigured S3 bucket, leading to the exposure of sensitive customer data. If proper monitoring and alerting mechanisms were in place, such as using AWS Config and SNS to detect and notify about changes to S3 bucket permissions, the breach might have been identified and mitigated more quickly. This underscores the importance of continuous monitoring and immediate alerts for changes in critical resource configurations.

---
<!-- nav -->
[[03-Introduction to SNS Notification Setup|Introduction to SNS Notification Setup]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/01-Defining Key Security Events to Log and Monitor/03-Creating SNS notification/00-Overview|Overview]]
