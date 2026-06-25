---
course: DevSecOps
topic: Logging & Monitoring for Security
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain why setting up AWS Budgets is important for managing AWS costs and security.**

AWS Budgets allow you to set spending limits and receive notifications when your usage approaches or exceeds those limits. This helps in managing unexpected charges due to forgotten resources or unauthorized usage. From a security perspective, if an attacker gains access to your AWS account and starts using resources, AWS Budgets can alert you to unusual spending patterns, allowing you to investigate and mitigate potential threats. For example, if an attacker uses your AWS resources for cryptocurrency mining or other high-cost activities, you would be notified if the spending exceeds your budget thresholds.

**Q2. How would you configure an AWS Budget for monthly usage costs? Provide step-by-step instructions.**

To configure an AWS Budget for monthly usage costs:

1. Log in to the AWS Management Console.
2. Navigate to the "Billing & Cost Management" dashboard.
3. Click on "Budgets" under the "Cost Management" section.
4. Click on "Create budget".
5. Choose "Cost budget" and select "Monthly" as the time period.
6. Leave the default budget name or enter a custom name.
7. Set the budget limit to the maximum amount you wish to spend, e.g., $40 or $50.
8. Add a notification threshold at 85% of the budget and another at 100%.
9. Enter the email addresses where you want to receive notifications.
10. Ensure that all services are included in the budget scope.
11. Review the settings and click "Create budget".

**Q3. What are the advantages of using AWS Budgets over CloudWatch Alarms for monitoring AWS costs?**

AWS Budgets provide a more user-friendly interface compared to CloudWatch Alarms, making it easier for non-technical users to manage and monitor their AWS costs. AWS Budgets offer predefined thresholds and notifications for budget limits, such as 85% and 100%, which are automatically configured. Additionally, AWS Budgets integrate directly with the billing dashboard, providing detailed insights into which specific services are contributing to the overall cost. This level of detail is less straightforward to achieve with CloudWatch Alarms alone.

**Q4. How can AWS Budgets help in identifying unauthorized usage of AWS resources?**

AWS Budgets can help identify unauthorized usage by setting up alerts for unexpected increases in spending. If an attacker gains access to your AWS account and starts using resources for malicious purposes, such as running large EC2 instances for batch processing or other resource-intensive tasks, the spending will likely exceed your normal budget. By configuring AWS Budgets with notification thresholds, you can be alerted when spending reaches certain percentages of your budget, allowing you to investigate and take action promptly. For example, if your budget is set to $40 and you receive a notification that spending has reached 85% ($34), you can check your AWS console to identify any unauthorized activity.

**Q5. Describe a recent real-world scenario where AWS Budgets could have helped prevent financial loss.**

In the case of the Capital One data breach in 2019, an attacker gained unauthorized access to the company’s AWS S3 buckets and was able to download sensitive customer data. While this breach primarily involved data exfiltration rather than resource usage, unauthorized access to AWS resources can lead to significant financial losses if attackers use those resources for malicious activities. If Capital One had implemented AWS Budgets with appropriate spending limits and notification thresholds, they could have been alerted to any unusual spending patterns, potentially indicating unauthorized usage. This would have allowed them to investigate and take corrective actions sooner, mitigating both financial and reputational damage.

---
<!-- nav -->
[[03-Introduction to Logging and Monitoring for Security in DevSecOps|Introduction to Logging and Monitoring for Security in DevSecOps]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/04-Logging & Monitoring for Security/04-Configure AWS Budgets for Monthly Usage Costs/00-Overview|Overview]]
