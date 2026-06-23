---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## Compliance as Code: Configuring Auto Remediation for CloudTrail Logging

### Introduction to Compliance as Code

Compliance as Code (CaC) is an approach to ensuring that your infrastructure adheres to compliance standards through automated checks and configurations. This method leverages Infrastructure as Code (IaC) principles to enforce policies and remediate issues automatically. In the context of AWS, CloudTrail is a critical service that logs API calls made within your AWS environment. Ensuring that CloudTrail is always enabled and logging correctly is essential for maintaining compliance and security.

### Understanding CloudTrail

CloudTrail is an AWS service that enables governance, compliance, operational auditing, and risk auditing of your AWS account. It provides a history of API calls made within your AWS environment, including API calls made via the AWS Management Console, AWS SDKs, command-line tools, and other AWS services. CloudTrail captures API calls at the account level and delivers them to an Amazon S3 bucket.

#### Why CloudTrail Matters

1. **Auditability**: CloudTrail logs provide a detailed record of actions taken within your AWS environment, which is crucial for audit purposes.
2. **Security**: By monitoring API calls, you can detect unauthorized access or suspicious activities.
3. **Compliance**: Many regulatory requirements mandate the retention of activity logs for a certain period. CloudTrail helps meet these requirements.

#### How CloudTrail Works

CloudTrail captures API calls made to your AWS environment and delivers them to an Amazon S3 bucket. You can configure CloudTrail to log all API calls or specific ones. Additionally, CloudTrail can deliver log files to Amazon CloudWatch Logs for further analysis.

### Enabling Auto Remediation for CloudTrail Logging

Auto remediation is a process where automated scripts or configurations are used to correct non-compliant states in your infrastructure. In this section, we will configure auto remediation to ensure that CloudTrail logging is always enabled.

#### Setting Up the Automation Document

To configure auto remediation for CloudTrail logging, we need to create an automation document in AWS Systems Manager. This document will specify the actions to take when CloudTrail logging is disabled.

##### Step-by-Step Configuration

1. **Create an Automation Document**:
    - Navigate to the AWS Systems Manager console.
    - Go to the "Automation" section and click on "Documents".
    - Click on "Create document".

2. **Define Parameters**:
    - The automation document requires several parameters to function correctly. These include the CloudTrail ARN and the automation role.

```yaml
---
schemaVersion: '1.2'
description: Enable CloudTrail logging if it is disabled.
parameters:
  cloudtrailArn:
    type: String
    description: (Required) The ARN of the CloudTrail trail to enable logging for.
  startLogging:
    type: Boolean
    description: (Required) Whether to start logging. Set to true to enable logging.
  automationRoleArn:
    type: String
    description: (Required) The ARN of the IAM role that has the necessary permissions to execute this automation.
```

3. **Define the Steps**:
    - The automation document should include steps to check the current state of CloudTrail logging and to enable logging if it is disabled.

```yaml
---
schemaVersion: '1.2'
description: Enable CloudTrail logging if it is disabled.
mainSteps:
  - name: CheckCloudTrailStatus
    action: aws:executeAwsApi
    inputs:
      Service: CloudTrail
      Api: GetTrailStatus
      Parameters:
        Name: "{{ cloudtrailArn }}"
  - name: StartLogging
    action: aws:executeAwsApi
    inputs:
      Service: CloudTrail
      Api: StartLogging
      Parameters:
        Name: "{{ cloudtrailArn }}"
    condition:
      test: "{{ startLogging }}"
      operator: Equals
      value: true
```

4. **Assign the Automation Role**:
    - The automation role must have the necessary permissions to execute the CloudTrail API calls.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudtrail:GetTrailStatus",
        "cloudtrail:StartLogging"
      ],
      "Resource": "*"
    }
  ]
}
```

### Example Configuration

Let's walk through a complete example of configuring auto remediation for CloudTrail logging.

#### Step 1: Create the Automation Document

Navigate to the AWS Systems Manager console and create a new automation document with the following content:

```yaml
---
schemaVersion: '1.2'
description: Enable CloudTrail logging if it is disabled.
parameters:
  cloudtrailArn:
    type: String
    description: (Required) The ARN of the CloudTrail trail to enable logging for.
  startLogging:
    type: Boolean
    description: (Required) Whether to start logging. Set to true to enable logging.
  automationRoleArn:
    type: String
    description: (Required) The ARN of the IAM role that has the necessary permissions to execute this automation.
mainSteps:
  - name: CheckCloudTrailStatus
    action: aws:executeAwsApi
    inputs:
      Service: CloudTrail
      Api: GetTrailStatus
      Parameters:
        Name: "{{ cloudtrailArn }}"
  - name: StartLogging
    action: aws:executeAwsApi
    inputs:
      Service: CloudTrail
      Api: StartLogging
      Parameters:
        Name: "{{ cloudtrailArn }}"
    condition:
      test: "{{ startLogging }}"
      operator: Equals
      value: true
```

#### Step 2: Define the IAM Role

Create an IAM role with the necessary permissions to execute the CloudTrail API calls.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudtrail:GetTrailStatus",
        "cloudtrail:StartLogging"
      ],
      "Resource": "*"
    }
  ]
}
```

#### Step 3: Assign the IAM Role to the Automation Document

When creating the automation document, assign the IAM role ARN to the `automationRoleArn` parameter.

#### Step 4: Test the Automation Document

Test the automation document by invoking it with the appropriate parameters.

```bash
aws ssm start-automation-execution --document-name "EnableCloudTrailLogging" --parameters cloudtrailArn="arn:aws:cloudtrail:us-east-1:123456789012:trail/my-trail",startLogging="true",automationRoleArn="arn:aws:iam::123456789012:role/SSMAutomationRole"
```

### Common Pitfalls and Best Practices

#### Pitfall: Incorrect IAM Permissions

One common pitfall is assigning incorrect IAM permissions to the automation role. Ensure that the role has the necessary permissions to execute the CloudTrail API calls.

#### Best Practice: Regular Audits

Regularly audit your CloudTrail configuration to ensure that logging is always enabled. Use AWS Config rules to monitor the state of CloudTrail trails.

### Real-World Examples

#### Recent Breach Example: Capital One Data Breach (CVE-2019-11510)

In the Capital One data breach, the attacker exploited misconfigured AWS S3 buckets to gain unauthorized access to customer data. Proper logging and monitoring of API calls using CloudTrail could have helped detect and mitigate such attacks.

### How to Prevent / Defend

#### Detection

Use AWS Config rules to monitor the state of CloudTrail trails. For example, you can create a rule to check if CloudTrail logging is enabled.

```json
{
  "configRuleName": "cloudtrail-enabled",
  "inputParameters": {},
  "scope": {
    "complianceResourceTypes": ["AWS::CloudTrail::Trail"]
  },
  "source": {
    "owner": "AWS",
    "sourceIdentifier": "CLOUDTRAIL_ENABLED"
  }
}
```

#### Prevention

Ensure that the IAM role assigned to the automation document has the necessary permissions to execute the CloudTrail API calls.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudtrail:GetTrailStatus",
        "cloudtrail:StartLogging"
      ],
      "Resource": "*"
    }
  ]
}
```

#### Secure Coding Fix

Compare the vulnerable and secure versions of the IAM role policy.

**Vulnerable Version:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudtrail:GetTrailStatus"
      ],
      "Resource": "*"
    }
  ]
}
```

**Secure Version:**

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "cloudtrail:GetTrailStatus",
        "cloudtrail:StartLogging"
      ],
      "Resource": "*"
    }
  ]
}
```

### Conclusion

Configuring auto remediation for CloudTrail logging is a critical step in maintaining compliance and security in your AWS environment. By automating the process of enabling CloudTrail logging, you can ensure that your infrastructure remains compliant and secure. Regular audits and proper IAM permissions are essential to preventing and detecting issues.

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but includes modules on AWS security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for learning security concepts.
- **WebGoat**: An interactive web application security training tool.

These labs provide practical experience in securing and monitoring AWS environments, including CloudTrail configurations.

### Additional Resources

- **AWS Documentation**: Comprehensive guides and tutorials on AWS services, including CloudTrail.
- **AWS Config Rules**: Official documentation on AWS Config rules for monitoring resource compliance.
- **IAM Policy Simulator**: A tool provided by AWS to test IAM policies and permissions.

By following these guidelines and practices, you can ensure that your AWS environment remains compliant and secure through effective use of CloudTrail and auto remediation.

---
<!-- nav -->
[[04-Compliance as Code Configuring Auto Remediation for CloudTrail Logging Part 2|Compliance as Code Configuring Auto Remediation for CloudTrail Logging Part 2]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Auto Remediation for CloudTrail Logging if switched off/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Auto Remediation for CloudTrail Logging if switched off/06-Practice Questions & Answers|Practice Questions & Answers]]
