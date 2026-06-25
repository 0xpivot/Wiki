---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## Introduction to Compliance as Code

Compliance as Code is an approach to automating the enforcement of compliance policies within an organization’s IT infrastructure. This method leverages code to define, monitor, and enforce compliance requirements, ensuring that systems adhere to regulatory standards and internal policies. In the context of AWS, this involves using AWS Config Rules to automate the monitoring and enforcement of compliance policies across your AWS resources.

### What is AWS Config?

AWS Config is a service that enables you to assess, audit, and record configurations of your AWS resources. It provides a detailed view of your AWS resource configurations, changes made to those configurations, and helps you ensure that your resources remain in compliance with internal policies and external regulations.

#### Key Features of AWS Config

- **Configuration Recording**: AWS Config continuously records the configuration of your AWS resources.
- **Configuration Change Notification**: You receive notifications about changes to your AWS resource configurations.
- **Compliance Auditing**: AWS Config allows you to define rules to check whether your resources comply with specific criteria.
- **Integration with Other Services**: AWS Config integrates with other AWS services like AWS CloudTrail, AWS Lambda, and AWS Systems Manager.

### Why Use AWS Config Rules?

Using AWS Config Rules helps you maintain compliance with various regulatory requirements and internal policies. By automating the process of checking compliance, you can:

- **Reduce Manual Effort**: Automate the process of checking compliance, reducing the need for manual audits.
- **Ensure Consistency**: Ensure that all resources consistently meet compliance requirements.
- **Detect Non-Compliance Early**: Identify non-compliant resources early and take corrective actions promptly.
- **Maintain Audit Trails**: Maintain detailed logs of resource configurations and changes, useful for audits.

### How AWS Config Rules Work

AWS Config Rules are predefined or custom rules that check the configuration of your AWS resources against specified criteria. These rules can be used to:

- **Check Resource Configurations**: Verify that resources are configured according to specific criteria.
- **Enforce Policies**: Ensure that resources comply with organizational policies and regulatory requirements.
- **Generate Notifications**: Send alerts when resources become non-compliant.

#### Predefined Rules vs. Custom Rules

- **Predefined Rules**: AWS provides a set of predefined rules that cover common compliance scenarios. These rules are ready-to-use and can be easily enabled.
- **Custom Rules**: You can create custom rules using AWS Lambda functions to check for specific compliance criteria.

### Setting Up AWS Config Rules

To set up AWS Config Rules, follow these steps:

1. **Enable AWS Config**:
    - Navigate to the AWS Management Console.
    - Go to the AWS Config service.
    - Enable AWS Config for your account.

2. **Create a Configuration Recorder**:
    - Create a configuration recorder to record the configuration of your resources.
    - Specify the IAM role that AWS Config uses to record configurations.

3. **Create an Aggregator (Optional)**:
    - If you want to aggregate configuration data across multiple accounts or regions, create an aggregator.

4. **Define Config Rules**:
    - Choose predefined rules or create custom rules.
    - Configure the rule parameters and specify the resources to which the rule applies.

### Example: Setting Up a Config Rule

Let's walk through an example of setting up a Config Rule to ensure that all EC2 instances have a specific tag.

#### Step 1: Enable AWS Config

```mermaid
graph TD
  A[Enable AWS Config] --> B[Create Configuration Recorder]
  B --> C[Specify IAM Role]
  C --> D[Create Aggregator (Optional)]
```

1. **Enable AWS Config**:
    - Go to the AWS Management Console.
    - Navigate to the AWS Config service.
    - Click on "Get started" to enable AWS Config.

2. **Create a Configuration Recorder**:
    - Click on "Configuration recorders".
    - Click on "Create configuration recorder".
    - Name the recorder and select the IAM role.

3. **Create an Aggregator (Optional)**:
    - Click on "Aggregators".
    - Click on "Create aggregator".
    - Name the aggregator and specify the source accounts and regions.

#### Step 2: Define a Config Rule

1. **Choose a Predefined Rule**:
    - Go to the "Rules" section in AWS Config.
    - Click on "Create rule".
    - Select a predefined rule, such as "EC2 instances should have a specific tag".

2. **Configure the Rule Parameters**:
    - Specify the tag key and value.
    - Select the resources to which the rule applies.

3. **Review and Create the Rule**:
    - Review the rule details.
    - Click on "Create rule".

### Example: Full HTTP Request and Response

Here is an example of creating a Config Rule using the AWS CLI:

```bash
aws configservice put-config-rule --config-rule file://config_rule.json
```

Where `config_rule.json` contains:

```json
{
  "ConfigRuleName": "ec2-tag-check",
  "Description": "Ensures EC2 instances have a specific tag.",
  "Scope": {
    "ComplianceResourceTypes": [
      "AWS::EC2::Instance"
    ]
  },
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "EC2_INSTANCE_TAG_CHECK"
  },
  "InputParameters": {
    "tagKey": "Environment",
    "tagValue": "Production"
  }
}
```

### HTTP Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "ConfigRuleArn": "arn:aws:config:us-east-1:123456789012:config-rule/ec2-tag-check",
  "ConfigRuleId": "cr-1234567890abcdef",
  "ConfigRuleName": "ec2-tag-check",
  "Description": "Ensures EC2 instances have a specific tag.",
  "Scope": {
    "ComplianceResourceTypes": [
      "AWS::EC2::Instance"
    ]
  },
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "EC2_INSTANCE_TAG_CHECK"
  },
  "InputParameters": {
    "tagKey": "Environment",
    "tagValue": "Production"
  }
}
```

### Real-World Example: Recent Breach

Consider a recent breach where an organization was fined for not having proper tagging on their EC2 instances. By using AWS Config Rules, the organization could have automatically enforced tagging policies, preventing such a breach.

### Common Pitfalls and How to Avoid Them

- **Incomplete Rule Definitions**: Ensure that all necessary parameters are specified in the rule definition.
- **Incorrect Resource Selection**: Double-check that the rule applies to the correct resources.
- **Insufficient Monitoring**: Regularly review the compliance status and take corrective actions as needed.

### How to Prevent / Defend

#### Detection

- **Regular Audits**: Use AWS Config to regularly audit your resources for compliance.
- **Alerts and Notifications**: Set up alerts and notifications for non-compliant resources.

#### Prevention

- **Automated Enforcement**: Use AWS Config Rules to automatically enforce compliance policies.
- **Secure Coding Practices**: Implement secure coding practices to prevent misconfigurations.

#### Secure-Coding Fixes

**Vulnerable Pattern**

```json
{
  "ConfigRuleName": "ec2-tag-check",
  "Description": "Ensures EC2 instances have a specific tag.",
  "Scope": {
    "ComplianceResourceTypes": [
      "AWS::EC2::Instance"
    ]
  },
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "EC2_INSTANCE_TAG_CHECK"
  },
  "InputParameters": {
    "tagKey": "Environment",
    "tagValue": "Production"
  }
}
```

**Fixed Pattern**

```json
{
  "ConfigRuleName": "ec2-tag-check",
  "Description": "Ensures EC2 instances have a specific tag.",
  "Scope": {
    "ComplianceResourceTypes": [
      "AWS::EC2::Instance"
    ]
  },
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "EC2_INSTANCE_TAG_CHECK"
  },
  "InputParameters": {
    "tagKey": "Environment",
    "tagValue": "Production"
  },
  "MaximumExecutionFrequency": "One_Hour"
}
```

### Conclusion

By leveraging AWS Config Rules, you can automate the enforcement of compliance policies across your AWS resources. This ensures that your resources remain in compliance with regulatory standards and internal policies, reducing the risk of non-compliance and associated penalties.

### Practice Labs

For hands-on practice with AWS Config Rules, consider the following labs:

- **CloudGoat**: A hands-on lab for practicing AWS security best practices, including compliance as code.
- **flaws.cloud**: A lab environment for practicing AWS security and compliance.
- **AWS Official Workshops**: Official AWS workshops provide guided tutorials on using AWS Config and other services.

These labs will help you gain practical experience in setting up and managing AWS Config Rules effectively.

---
<!-- nav -->
[[06-Introduction to Compliance as Code Part 5|Introduction to Compliance as Code Part 5]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Setting up AWS Config Rules/00-Overview|Overview]] | [[08-Introduction to Compliance as Code|Introduction to Compliance as Code]]
