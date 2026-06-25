---
course: DevSecOps
topic: Defining Key Security Events to Log and Monitor
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the process of creating an AWS Config rule to ensure that S3 buckets are not publicly accessible.**

To create an AWS Config rule ensuring that S3 buckets are not publicly accessible, follow these steps:

1. Log in to the AWS Management Console.
2. Navigate to the AWS Config service.
3. Click on "Add Rule."
4. Filter the available rules to find the specific rule for S3 buckets. In this case, choose the rule that ensures public access is not available to S3 buckets.
5. Configure the rule by setting the trigger type to "configuration change" and "periodic." Set the resource type to "S3 bucket."
6. Define the frequency of the compliance checks. For example, set it to one hour for a proof-of-concept scenario.
7. Optionally, enable remediation actions to automatically fix any non-compliant configurations.
8. Click "Save" to create the rule.
9. Wait for the compliance evaluation to complete, which may take a few minutes.
10. Check the compliance status of the S3 buckets in the AWS Config dashboard.

**Q2. How would you configure an S3 bucket to trigger an alert if it becomes publicly accessible?**

To configure an S3 bucket to trigger an alert if it becomes publicly accessible, follow these steps:

1. Create an AWS Config rule as described in Q1.
2. Ensure the rule is set to trigger on configuration changes and periodically.
3. Configure the rule to notify you via an SNS topic when a bucket becomes non-compliant due to public access.
4. Set up an SNS subscription to receive notifications. You can subscribe via email or other supported methods.
5. Test the setup by intentionally making an S3 bucket publicly accessible and verifying that you receive an alert.

**Q3. Why is it important to prevent public access to S3 buckets? Provide a recent real-world example.**

Preventing public access to S3 buckets is crucial because it helps protect sensitive data from unauthorized access, which can lead to data breaches and compliance violations. A recent example is the 2021 breach involving a healthcare company, where a misconfigured S3 bucket led to the exposure of patient data. This incident highlights the importance of proper configuration and monitoring of S3 buckets to prevent such breaches.

**Q4. What remedial actions can AWS Config take in response to a non-compliant S3 bucket?**

AWS Config can take several remedial actions in response to a non-compliant S3 bucket:

1. **Automated Remediation:** AWS Config can automatically apply predefined remediation actions to fix the non-compliance issue. For example, it can modify the S3 bucket policy to restrict public access.
2. **Manual Intervention:** AWS Config can send alerts to administrators who can then manually intervene to correct the misconfiguration.
3. **Notification:** AWS Config can notify stakeholders through SNS topics, emails, or other mechanisms to inform them of the non-compliance and prompt corrective action.

**Q5. How does AWS Config evaluate the compliance status of S3 buckets?**

AWS Config evaluates the compliance status of S3 buckets by performing regular compliance checks according to the configured rule. The evaluation process involves:

1. **Trigger Conditions:** AWS Config triggers the evaluation based on the specified conditions, such as configuration changes or periodic checks.
2. **Resource Type:** The evaluation focuses on S3 buckets as defined in the rule.
3. **Compliance Checks:** AWS Config checks whether the S3 buckets meet the criteria specified in the rule, such as ensuring they are not publicly accessible.
4. **Evaluation Results:** The results of the compliance checks are displayed in the AWS Config dashboard, indicating whether the resources are compliant or non-compliant.

**Q6. What steps would you take to revert a non-compliant S3 bucket to a compliant state?**

To revert a non-compliant S3 bucket to a compliant state, follow these steps:

1. Identify the non-compliant S3 bucket using the AWS Config dashboard.
2. Navigate to the S3 Management Console and select the non-compliant bucket.
3. Modify the bucket’s permissions to remove public access. This typically involves updating the bucket policy or ACLs to restrict access.
4. Save the changes to the bucket configuration.
5. Verify the compliance status in the AWS Config dashboard to ensure the bucket is now compliant.
6. Monitor for further alerts or notifications to ensure ongoing compliance.

**Q7. How can you use AWS Config to monitor multiple S3 buckets for public access simultaneously?**

To use AWS Config to monitor multiple S3 buckets for public access simultaneously, follow these steps:

1. Create an AWS Config rule specifically designed to check for public access in S3 buckets.
2. Ensure the rule is configured to evaluate all S3 buckets in your account.
3. Set the evaluation frequency to a suitable interval (e.g., every hour).
4. Use the AWS Config dashboard to monitor the compliance status of all S3 buckets.
5. Configure SNS notifications to receive alerts for any non-compliant buckets.
6. Regularly review the compliance status and take corrective actions as needed.

By following these steps, you can effectively monitor multiple S3 buckets for public access and ensure they remain compliant with your security policies.

---
<!-- nav -->
[[03-Defining Key Security Events to Log and Monitor|Defining Key Security Events to Log and Monitor]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/01-Defining Key Security Events to Log and Monitor/02-Creating AWS Config Rule/00-Overview|Overview]]
