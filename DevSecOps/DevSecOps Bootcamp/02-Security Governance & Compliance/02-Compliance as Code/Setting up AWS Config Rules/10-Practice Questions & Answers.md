---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain how AWS Config can help in maintaining compliance within an AWS environment.**

AWS Config helps in maintaining compliance by continuously monitoring and recording the state of AWS resources. It allows organizations to define compliance rules based on industry standards and best practices such as CIS benchmarks. By setting up AWS Config, you can automatically detect and alert on any deviations from these rules, ensuring that your AWS environment adheres to specified compliance requirements. For example, you can set up rules to ensure that SSH access is restricted and that CloudTrail logging is enabled, helping to maintain security and auditability.

**Q2. How would you configure AWS Config to monitor only specific resource types, such as EC2 instances, while excluding others?**

To configure AWS Config to monitor only specific resource types, such as EC2 instances, while excluding others, you would follow these steps:

1. Go to the AWS Config dashboard and start configuring your compliance settings.
2. In the configuration options, select the specific resource types you want to monitor, such as EC2 instances.
3. Use the override settings to exclude any resource types you do not wish to monitor. For example, you can exclude networking resources or other services.
4. Set the recording frequency according to your needs. If you want to monitor changes continuously, select continuous recording. Otherwise, you can choose daily recording to save costs.
5. Ensure that the IAM roles and permissions are correctly set up to allow AWS Config to record changes to the specified resources.
6. Configure the delivery method to store the compliance data in an S3 bucket or another storage solution.

Here’s a sample configuration snippet:

```python
import boto3

config = boto3.client('config')

response = config.put_config_rule(
    ConfigRule={
        'ConfigRuleName': 'EC2InstanceMonitoring',
        'Description': 'Monitor EC2 instances for compliance',
        'Scope': {
            'ComplianceResourceTypes': ['AWS::EC2::Instance']
        },
        'Source': {
            'Owner': 'AWS',
            'SourceIdentifier': 'EC2_INSTANCE_MONITORING'
        }
    }
)
```

**Q3. Why is it important to monitor IAM resource changes for compliance, and how would you set this up in AWS Config?**

Monitoring IAM resource changes is crucial for compliance because IAM controls access to AWS services and resources. Any unauthorized changes to IAM roles, policies, or users can lead to security vulnerabilities. Therefore, it is essential to monitor IAM changes to ensure that they comply with organizational policies and regulatory requirements.

To set up AWS Config to monitor IAM resource changes:

1. Go to the AWS Config dashboard and configure your compliance settings.
2. In the override settings, remove the exclusion for IAM resource types.
3. Set the recording frequency for IAM resources to either continuous or daily, depending on your needs and cost considerations.
4. Ensure that the IAM roles and permissions are correctly set up to allow AWS Config to record changes to IAM resources.
5. Configure the delivery method to store the compliance data in an S3 bucket or another storage solution.

Here’s a sample configuration snippet:

```python
import boto3

config = boto3.client('config')

response = config.put_config_rule(
    ConfigRule={
        'ConfigRuleName': 'IAMChangeMonitoring',
        'Description': 'Monitor IAM resource changes for compliance',
        'Scope': {
            'ComplianceResourceTypes': ['AWS::IAM::*']
        },
        'Source': {
            'Owner': 'AWS',
            'SourceIdentifier': 'IAM_CHANGE_MONITORING'
        }
    }
)
```

**Q4. How does AWS Config integrate with CloudTrail to enhance security and compliance monitoring?**

AWS Config integrates with CloudTrail to enhance security and compliance monitoring by leveraging CloudTrail logs to provide a detailed history of API calls made within an AWS account. This integration ensures that you can track and audit changes to your AWS resources, which is critical for maintaining compliance.

To set up this integration:

1. Ensure that CloudTrail is enabled in your AWS account.
2. In the AWS Config dashboard, configure compliance rules that check for CloudTrail status.
3. Monitor the compliance status of CloudTrail to ensure it remains enabled and properly configured.
4. Use the combined data from AWS Config and CloudTrail to gain comprehensive insights into the state and changes of your AWS resources.

For example, you can set up a rule to ensure that CloudTrail is always enabled:

```python
import boto3

config = boto3.client('config')

response = config.put_config_rule(
    ConfigRule={
        'ConfigRuleName': 'CloudTrailEnabled',
        'Description': 'Ensure CloudTrail is enabled',
        'Scope': {
            'ComplianceResourceTypes': ['AWS::CloudTrail::Trail']
        },
        'Source': {
            'Owner': 'AWS',
            'SourceIdentifier': 'CLOUDTRAIL_ENABLED'
        }
    }
)
```

**Q5. What recent real-world examples demonstrate the importance of using AWS Config for compliance monitoring?**

Recent real-world examples highlight the importance of using AWS Config for compliance monitoring:

1. **CVE-2021-20225**: A vulnerability in AWS CloudFormation templates allowed unauthorized access to sensitive resources. AWS Config could have helped detect and mitigate such issues by continuously monitoring and enforcing compliance rules related to resource access and configuration.

2. **SolarWinds Supply Chain Attack (2020)**: This attack compromised multiple organizations by injecting malicious code into software updates. AWS Config could have been used to monitor and detect unauthorized changes to AWS resources, potentially identifying the malicious activity early.

By using AWS Config, organizations can proactively monitor their AWS environments for compliance and security issues, reducing the risk of breaches and ensuring adherence to regulatory requirements.

---
<!-- nav -->
[[09-Setting Up AWS Config Rules|Setting Up AWS Config Rules]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Setting up AWS Config Rules/00-Overview|Overview]]
