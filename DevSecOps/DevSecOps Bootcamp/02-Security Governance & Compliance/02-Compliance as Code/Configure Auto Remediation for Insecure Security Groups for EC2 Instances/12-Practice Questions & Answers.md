---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the concept of auto remediation in AWS Config and why it is important in a large-scale infrastructure setup.**

Auto remediation in AWS Config automates the process of fixing non-compliant resources, such as security groups, without manual intervention. This is crucial in large-scale infrastructures where manually checking and fixing non-compliant resources daily would be highly inefficient and time-consuming. By automating the remediation process, AWS Config ensures continuous compliance, reducing the risk of security vulnerabilities and minimizing the administrative burden.

**Q2. How does AWS Config integrate with the Systems Manager (SSM) to perform auto remediation?**

AWS Config integrates with the Systems Manager (SSM) by delegating the task of fixing non-compliant resources to SSM. When AWS Config detects a non-compliant resource, it triggers an SSM document that contains the remediation logic. SSM then executes the specified actions, such as modifying security group rules, to bring the resource back into compliance. This integration leverages SSM's capabilities to manage and execute automation scripts across various AWS resources.

**Q3. Describe the steps involved in creating an IAM role for SSM to execute auto remediation scripts.**

To create an IAM role for SSM to execute auto remediation scripts:

1. Navigate to the IAM console and create a new role.
2. Select "Systems Manager" as the trusted entity.
3. Attach a custom policy to the role that grants the necessary permissions. The policy should include permissions to:
   - Revoke security group ingress.
   - Start and change request execution for SSM.
4. Ensure the policy includes the correct AWS account ID.
5. Name the role appropriately, such as `config-auto-remediation-role`.
6. Assign the role to SSM so it can assume the role and execute the remediation scripts.

**Q4. What are the potential costs associated with using auto remediation in AWS Config?**

Using auto remediation in AWS Config incurs costs due to the execution of remediation scripts. Every time a script is executed to fix a non-compliant resource, AWS charges for the execution. While the cost might be minimal in small setups, it can add up in large-scale environments where frequent changes and continuous monitoring occur. Administrators should be aware of these costs and monitor their usage to manage expenses effectively.

**Q5. How would you configure auto remediation to disable public access for security groups in an AWS environment?**

To configure auto remediation to disable public access for security groups:

1. Go to the AWS Config dashboard and identify the non-compliant security group rule.
2. Click on "Manage Remediation" for the rule.
3. Choose the "Automatic remediation" option and configure the retry settings (e.g., two retries every 60 seconds).
4. Select the appropriate remediation action, such as "Disable public access for security group."
5. Define the resource ID parameter as the security group ID.
6. Create an IAM role with the necessary permissions for SSM to execute the remediation script.
7. Assign the IAM role to the remediation action.
8. Save the configuration and allow AWS Config to automatically fix non-compliant security groups.

**Q6. Provide an example of a recent real-world scenario where auto remediation could have been beneficial.**

A recent real-world scenario where auto remediation could have been beneficial is the AWS S3 bucket misconfiguration incident reported in several breaches. For example, in the Capital One breach (CVE-2019-11510), a misconfigured S3 bucket exposed sensitive customer data. If auto remediation was enabled, AWS Config could have automatically corrected the misconfiguration by restricting public access to the S3 bucket, thereby preventing unauthorized access and mitigating the risk of data exposure.

---
<!-- nav -->
[[11-Configuring Auto Remediation for Insecure Security Groups|Configuring Auto Remediation for Insecure Security Groups]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Auto Remediation for Insecure Security Groups for EC2 Instances/00-Overview|Overview]]
