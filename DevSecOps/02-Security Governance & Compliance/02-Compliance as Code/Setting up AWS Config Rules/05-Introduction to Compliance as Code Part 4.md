---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## Introduction to Compliance as Code

Compliance as Code is a practice that integrates compliance requirements into the development process using automated tools and scripts. This approach ensures that compliance policies are enforced consistently across all environments and applications. In the context of AWS, AWS Config is a service that enables you to assess, audit, and evaluate the configurations of your AWS resources. By setting up AWS Config Rules, you can automate the enforcement of compliance policies and ensure that your resources adhere to specific standards.

### What is AWS Config?

AWS Config is a fully managed service that provides you with an inventory of the AWS resources in your account, continuous monitoring of configuration changes on your AWS resources, and allows you to automate the evaluation of your AWS resources against desired configurations. This helps you maintain compliance with internal policies and external regulations.

#### Key Features of AWS Config

- **Inventory**: AWS Config maintains an inventory of your AWS resources, including their properties and relationships.
- **Configuration Change Tracking**: It tracks changes to your resources and records them in a history.
- **Compliance Evaluation**: You can define rules to automatically evaluate your resources against compliance standards.

### Why Use AWS Config Rules?

Using AWS Config Rules is essential for maintaining compliance and ensuring that your AWS resources meet specific security and operational standards. Here are some reasons why you should use AWS Config Rules:

- **Automated Compliance Checks**: Automate the process of checking your resources against compliance standards.
- **Continuous Monitoring**: Continuously monitor your resources for any deviations from the defined rules.
- **Audit Trails**: Maintain detailed audit trails of configuration changes, which can be crucial for compliance audits.
- **Cost Efficiency**: Automate compliance checks to reduce manual effort and potential human errors.

### How AWS Config Rules Work

AWS Config Rules work by evaluating your AWS resources against predefined rules. These rules can be based on AWS-managed rules or custom rules that you create. When a rule is violated, AWS Config generates a non-compliant finding, which can trigger automated remediation actions or alert you to take corrective action.

#### Steps to Set Up AWS Config Rules

1. **Enable AWS Config**: First, you need to enable AWS Config in your AWS account.
2. **Create Config Rules**: Define the rules that you want to enforce on your resources.
3. **Monitor Compliance**: Continuously monitor your resources for compliance with the defined rules.
4. **Remediate Non-Compliance**: Take corrective actions when resources violate the rules.

### Example: Setting Up AWS Config Rules

Let's walk through an example of setting up AWS Config Rules to monitor EC2 instances and CloudTrail settings.

#### Step 1: Enable AWS Config

To enable AWS Config, you can use the AWS Management Console, AWS CLI, or AWS SDKs. Here’s how you can enable it using the AWS CLI:

```sh
aws configservice put-configuration-recorder --configuration-recorder name=default,roleARN=arn:aws:iam::123456789012:role/aws-config-role
```

This command sets up a default configuration recorder with the specified role ARN.

#### Step 2: Create Config Rules

Next, you need to create the Config Rules. For this example, we will create two rules: one to ensure that SSH access is restricted and another to ensure that CloudTrail is enabled.

##### Rule 1: Restricted SSH Access

To create a rule that checks for restricted SSH access, you can use the following AWS CLI command:

```sh
aws configservice put-config-rule --config-rule-name "restricted-ssh-access" --source owner=AWS,sourceIdentifier="SECURITY_GROUP_NO_SSH_ACCESS"
```

This rule checks that no security groups allow unrestricted SSH access.

##### Rule 2: CloudTrail Enabled

To create a rule that checks if CloudTrail is enabled, you can use the following AWS CLI command:

```sh
aws configservice put-config-rule --config-rule-name "cloudtrail-enabled" --source owner=AWS,sourceIdentifier="CLOUD_TRAIL_ENABLED"
```

This rule checks that CloudTrail is enabled for your account.

#### Step 3: Monitor Compliance

Once the rules are set up, AWS Config will continuously monitor your resources for compliance. You can view the compliance status in the AWS Management Console or using the AWS CLI.

```sh
aws configservice describe-compliance-by-config-rule --config-rules "restricted-ssh-access", "cloudtrail-enabled"
```

This command retrieves the compliance status for the specified rules.

#### Step 4: Remediate Non-Compliance

If a resource violates a rule, you can take corrective actions. For example, if an EC2 instance has a security group that allows unrestricted SSH access, you can modify the security group to restrict SSH access.

### Real-World Examples

#### Example 1: CVE-2021-20225

CVE-2021-20225 is a critical vulnerability in AWS Elastic Load Balancing (ELB) that could allow unauthorized access to sensitive data. By using AWS Config Rules, you can ensure that your ELB configurations comply with security best practices, such as restricting access to specific IP addresses.

```sh
aws configservice put-config-rule --config-rule-name "elb-restricted-access" --source owner=AWS,sourceIdentifier="ELB_RESTRICTED_ACCESS"
```

This rule checks that your ELB configurations restrict access to specific IP addresses.

#### Example 2: CloudTrail Misconfiguration

In 2020, a misconfiguration in CloudTrail led to the exposure of sensitive logs. By using AWS Config Rules, you can ensure that CloudTrail is properly configured to log all necessary events and that the logs are securely stored.

```sh
aws configservice put-config-rule --config-rule-name "cloudtrail-secure-storage" --source owner=AWS,sourceIdentifier="CLOUD_TRAIL_SECURE_STORAGE"
```

This rule checks that CloudTrail logs are stored securely and that the necessary events are being logged.

### How to Prevent / Defend

#### Detection

To detect non-compliance issues, you can use AWS Config to continuously monitor your resources. You can also set up alerts using Amazon CloudWatch Events to notify you when a resource becomes non-compliant.

```sh
aws cloudwatch put-rule --name "non-compliant-resource-alert" --event-pattern '{"source": ["aws.config"],"detail-type": ["Config Service Notification"],"detail": {"state": ["NON_COMPLIANT"]}}'
```

This rule triggers an alert when a resource becomes non-compliant.

#### Prevention

To prevent non-compliance issues, you can use AWS Config Rules to enforce compliance policies. You can also use AWS Organizations to enforce compliance policies across multiple accounts.

```sh
aws organizations put-organization-config-rule --config-rule-name "organization-wide-compliance" --source owner=AWS,sourceIdentifier="ORGANIZATION_WIDE_COMPLIANCE"
```

This rule enforces compliance policies across all accounts in your organization.

#### Secure Coding Fixes

Here’s an example of a secure coding fix for a non-compliant security group:

**Vulnerable Code:**

```json
{
  "GroupId": "sg-0123456789abcdef0",
  "IpPermissions": [
    {
      "IpProtocol": "tcp",
      "FromPort": 22,
      "ToPort": 22,
      "IpRanges": [
        {
          "CidrIp": "0.0.0.0/0"
        }
      ]
    }
  ]
}
```

**Fixed Code:**

```json
{
  "GroupId": "sg-0123456789abcdef0",
  "IpPermissions": [
    {
      "IpProtocol": "tcp",
      "FromPort": 22,
      "ToPort": 22,
      "IpRanges": [
        {
          "CidrIp": "192.168.1.0/24"
        }
      ]
    }
  ]
}
```

In the fixed code, SSH access is restricted to a specific IP range.

### Configuration Hardening

To harden your AWS Config setup, you can follow these best practices:

- **Enable All Resources**: Ensure that AWS Config is enabled for all resources in your account.
- **Use IAM Roles**: Use IAM roles to grant permissions to AWS Config.
- **Enable Detailed Monitoring**: Enable detailed monitoring to track all configuration changes.

### Conclusion

By using AWS Config Rules, you can automate the enforcement of compliance policies and ensure that your AWS resources meet specific security and operational standards. This helps you maintain compliance with internal policies and external regulations, and reduces the risk of security vulnerabilities.

### Practice Labs

For hands-on experience with AWS Config Rules, you can use the following labs:

- **CloudGoat**: A cloud security training platform that includes exercises on AWS Config.
- **flaws.cloud**: A cloud security training platform that includes exercises on AWS Config.
- **AWS Official Workshops**: AWS offers official workshops that cover AWS Config and other security services.

These labs provide a practical way to learn and apply the concepts covered in this chapter.

---
<!-- nav -->
[[04-Introduction to Compliance as Code Part 3|Introduction to Compliance as Code Part 3]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Setting up AWS Config Rules/00-Overview|Overview]] | [[06-Introduction to Compliance as Code Part 5|Introduction to Compliance as Code Part 5]]
