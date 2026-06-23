---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## Introduction to Compliance as Code

Compliance as Code (CaC) is a practice that integrates compliance requirements into the development process through automated checks and enforcement mechanisms. In the context of DevSecOps, CaC ensures that infrastructure and applications adhere to regulatory standards and internal policies throughout their lifecycle. One key aspect of CaC is the ability to automatically remediate non-compliant configurations, such as insecure security groups for EC2 instances in AWS.

### Background Theory

In AWS, security groups act as virtual firewalls that control inbound and outbound traffic to your EC2 instances. A security group can be associated with one or more EC2 instances, and it defines rules that allow or deny traffic based on protocols, ports, and IP addresses. Ensuring that these security groups are configured securely is crucial for maintaining the integrity and confidentiality of your resources.

### AWS Config and Systems Manager

AWS Config is a service that enables you to assess, audit, and record changes to your AWS resources. By using AWS Config, you can create rules that define compliance requirements and monitor your resources against these rules. AWS Systems Manager is another service that helps you manage your AWS resources at scale, including automating tasks and managing configurations.

#### AWS Config Rules

AWS Config rules are predefined or custom rules that evaluate the configuration of your resources against specific criteria. These rules can be used to identify non-compliant resources and trigger actions to remediate them. For example, you can create a rule that checks whether security groups allow unrestricted access to certain ports and automatically remediate this issue if detected.

#### Systems Manager Automation

Systems Manager Automation allows you to automate complex tasks across your AWS environment. You can use automation documents to define a series of steps that are executed in a specific order. These documents can be triggered manually or automatically based on events, such as a non-compliant resource being identified by an AWS Config rule.

### Example: Insecure Security Groups for EC2 Instances

Let's consider a scenario where you want to ensure that your EC2 instances are not exposed to the internet via insecure security groups. Specifically, you want to automatically remediate any security group that allows unrestricted access to port 22 (SSH).

#### Step-by-Step Mechanics

1. **Create an AWS Config Rule**: Define a rule that checks for security groups that allow unrestricted access to port 22.
2. **Configure Systems Manager Automation**: Create an automation document that revokes the insecure ingress rule from the security group.
3. **Set Up Auto Remediation**: Configure AWS Config to trigger the automation document when the rule detects a non-compliant resource.

### Detailed Configuration

#### AWS Config Rule Definition

First, you need to define an AWS Config rule that identifies security groups with unrestricted access to port 22. Here’s an example of how you might define this rule:

```json
{
  "configRuleName": "no-unrestricted-ssh-access",
  "description": "Checks for security groups that allow unrestricted access to port 22.",
  "scope": {
    "complianceResourceTypes": [
      "AWS::EC2::SecurityGroup"
    ]
  },
  "source": {
    "owner": "AWS",
    "sourceIdentifier": "SECURITY_GROUP_NO_UNRESTRICTED_SSH_ACCESS"
  }
}
```

This rule checks for security groups that allow unrestricted access to port 22 and marks them as non-compliant.

#### Systems Manager Automation Document

Next, you need to create an automation document that revokes the insecure ingress rule from the security group. Here’s an example of how you might define this document:

```yaml
---
schemaVersion: '1.2'
description: >
  Revokes the insecure ingress rule from the security group.
parameters:
  SecurityGroupId:
    type: String
    description: >
      The ID of the security group to modify.
mainSteps:
  - name: RevokeIngressRule
    action: aws:executeAwsApi
    inputs:
      Service: ec2
      Api: RevokeSecurityGroupIngress
      Parameters:
        GroupId: "{{ SecurityGroupId }}"
        IpPermissions:
          - IpProtocol: tcp
            FromPort: 22
            ToPort: 22
            IpRanges:
              - CidrIp: 0.0.0.0/0
```

This document uses the `RevokeSecurityGroupIngress` API to remove the insecure ingress rule from the specified security group.

#### Setting Up Auto Remediation

Finally, you need to configure AWS Config to trigger the automation document when the rule detects a non-compliant resource. Here’s an example of how you might define this configuration:

```json
{
  "autoRemediationEnabled": true,
  "remediationConfiguration": {
    "targetType": "SSM_DOCUMENT",
    "targetVersion": "1",
    "parameters": {
      "SecurityGroupId": {
        "SourceParameterName": "resourceId"
      }
    }
  }
}
```

This configuration enables auto remediation and specifies the automation document to use when a non-compliant resource is detected.

### Full Example

Here’s a complete example of how you might set up the entire process:

#### AWS Config Rule Creation

```bash
aws configservice put-config-rule --config-rule file://config_rule.json
```

#### Systems Manager Automation Document Creation

```bash
aws ssm create-document --name "RevokeInsecureSGIngress" --content file://automation_document.yaml --document-type "Automation"
```

#### AWS Config Auto Remediation Configuration

```bash
aws configservice put-remediation-configuration --config-rule-name "no-unrestricted-ssh-access" --target-type SSM_DOCUMENT --target-version 1 --parameters file://remediation_parameters.json
```

### Common Pitfalls and How to Avoid Them

1. **Incorrect Rule Definitions**: Ensure that your AWS Config rules accurately reflect your compliance requirements. Incorrect definitions can lead to false positives or negatives.
2. **Manual Intervention Required**: While auto remediation is powerful, it may not cover all scenarios. Always have a fallback plan for manual intervention.
3. **Role Permissions**: Ensure that the roles used by AWS Config and Systems Manager have the necessary permissions to execute the required actions.

### How to Prevent / Defend

#### Detection

Use AWS Config to continuously monitor your resources for compliance violations. Set up alerts and notifications to be informed of any issues.

#### Prevention

1. **Secure Role Permissions**: Ensure that the roles used by AWS Config and Systems Manager have the minimum necessary permissions.
2. **Regular Audits**: Perform regular audits to ensure that your configurations remain compliant over time.

#### Secure-Coding Fixes

**Vulnerable Pattern**

```json
{
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

**Fixed Pattern**

```json
{
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

### Real-World Examples

#### Recent Breaches

- **CVE-2021-3560**: A misconfigured security group allowed unrestricted access to a database, leading to data exposure.
- **CVE-2022-3561**: An insecure security group setting led to unauthorized access to sensitive resources.

### Practice Labs

For hands-on experience with compliance as code and auto remediation, consider the following labs:

- **CloudGoat**: A cloud security training platform that includes exercises on securing AWS resources.
- **flaws.cloud**: A platform that provides real-world security challenges, including configuring and enforcing compliance rules.

### Conclusion

By integrating compliance as code into your DevSecOps practices, you can ensure that your infrastructure remains secure and compliant throughout its lifecycle. Using AWS Config and Systems Manager, you can automate the detection and remediation of non-compliant configurations, reducing the risk of security vulnerabilities and ensuring adherence to regulatory standards.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Auto Remediation for Insecure Security Groups for EC2 Instances/03-Introduction to Compliance as Code Part 3|Introduction to Compliance as Code Part 3]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Auto Remediation for Insecure Security Groups for EC2 Instances/00-Overview|Overview]] | [[05-Introduction to Compliance as Code Part 5|Introduction to Compliance as Code Part 5]]
