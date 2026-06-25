---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## Introduction to Compliance as Code

Compliance as Code (CaC) is a practice that integrates compliance requirements into the development lifecycle through automated checks and enforcement mechanisms. This approach ensures that systems and applications adhere to regulatory standards and internal policies throughout their entire lifecycle. One of the key components of CaC is the ability to automatically remediate non-compliant configurations, which significantly reduces the burden of manual intervention and ensures continuous compliance.

### Why Automate Compliance?

In the context of DevSecOps, automating compliance is crucial because it aligns with the principles of continuous integration and delivery (CI/CD). Manual compliance checks are time-consuming, error-prone, and often inconsistent. By automating these processes, organizations can ensure that compliance is maintained at all times, reducing the risk of non-compliance penalties and security vulnerabilities.

### AWS Config and Auto Remediation

AWS Config is a service that enables you to assess, audit, and record changes to your AWS resources. It provides a detailed view of your AWS resource configurations and allows you to track changes over time. One of the powerful features of AWS Config is its ability to perform auto remediation, which automatically corrects non-compliant resources based on predefined rules.

### Setting Up Auto Remediation for Insecure Security Groups

Security groups in AWS EC2 are virtual firewalls that control inbound and outbound traffic to instances. An insecure security group might allow unrestricted access to sensitive ports or protocols, posing significant security risks. To mitigate these risks, we can set up auto remediation to automatically fix non-compliant security groups.

#### Step-by-Step Guide to Auto Remediation

1. **Identify Non-Compliant Rules**: First, identify the non-compliant rules in your AWS Config dashboard. These rules indicate configurations that do not meet your organization's compliance standards.

2. **Select Non-Compliant Resources**: Once you have identified the non-compliant rules, select the resources that are affected by these rules. You can do this from the AWS Config dashboard.

3. **Configure Auto Remediation**: After selecting the non-compliant resources, you can configure auto remediation. This involves setting up a remediation action that will automatically correct the non-compliant configurations.

4. **Test and Monitor**: Finally, test the auto remediation setup to ensure it works as expected. Continuously monitor the system to detect any new non-compliant configurations and ensure they are automatically remediated.

### Detailed Example: Insecure Security Group Configuration

Let's walk through a detailed example of how to set up auto remediation for an insecure security group configuration in AWS EC2.

#### Background Theory

A security group in AWS EC2 is a virtual firewall that controls inbound and outbound traffic to instances. Each security group is associated with a set of rules that define allowed traffic. An insecure security group might allow unrestricted access to sensitive ports or protocols, such as SSH (port 22) or RDP (port 3389).

#### Identifying Non-Compliant Security Groups

To identify non-compliant security groups, you can use AWS Config to monitor and record the configurations of your EC2 instances. Here’s how you can do it:

1. **Enable AWS Config**: Ensure that AWS Config is enabled in your AWS account. This can be done from the AWS Management Console under the "Services" menu.

2. **Create a Configuration Recorder**: Create a configuration recorder to capture the current state of your resources. This can be done using the AWS CLI or the AWS Management Console.

```bash
aws configservice put-configuration-recorder --configuration-recorder file://recorder.json
```

Where `recorder.json` contains:

```json
{
    "name": "default",
    "roleARN": "arn:aws:iam::123456789012:role/aws-config-role",
    "recordingGroup": {
        "allSupported": true,
        "includeGlobalResourceTypes": true
    }
}
```

3. **Create a Delivery Channel**: Create a delivery channel to specify where the recorded configurations should be stored. This can be done using the AWS CLI or the AWS Management Console.

```bash
aws configservice put-delivery-channel --delivery-channel file://channel.json
```

Where `channel.json` contains:

```json
{
    "name": "default",
    "s3BucketName": "my-config-bucket",
    "snsTopicARN": "arn:aws:sns:us-east-1:123456789012:my-config-topic"
}
```

4. **Monitor Non-Compliant Resources**: Use AWS Config to monitor and record the configurations of your EC2 instances. You can create a custom rule to identify non-compliant security groups.

```bash
aws configservice put-evaluation-results --evaluation-results file://evaluations.json
```

Where `evaluations.json` contains:

```json
[
    {
        "ComplianceResourceType": "AWS::EC2::SecurityGroup",
        "ComplianceResourceId": "sg-12345678",
        "ComplianceType": "NON_COMPLIANT",
        "Annotation": "Security group allows unrestricted access to port 22."
    }
]
```

#### Configuring Auto Remediation

Once you have identified the non-compliant security groups, you can configure auto remediation to automatically correct the configurations. Here’s how you can do it:

1. **Create a Remediation Action**: Create a remediation action that will automatically correct the non-compliant configurations. This can be done using the AWS CLI or the AWS Management Console.

```bash
aws configservice put-remediation-configurations --remediation-configurations file://remediation.json
```

Where `remediation.json` contains:

```json
[
    {
        "ConfigRuleName": "insecure-security-group",
        "TargetId": "arn:aws:lambda:us-east-1:123456789012:function:remediate-insecure-security-group",
        "Parameters": {
            "Action": "REMOVE_RULE"
        },
        "Automatic": true
    }
]
```

2. **Create a Lambda Function**: Create a Lambda function that will execute the remediation action. This function should remove the non-compliant rules from the security group.

```python
import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    security_group_id = event['securityGroupId']
    ip_permissions = event['ipPermissions']

    response = ec2.revoke_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=ip_permissions
    )
    return response
```

3. **Test the Remediation Action**: Test the remediation action to ensure it works as expected. You can trigger the remediation action manually to verify that it correctly removes the non-compliant rules from the security group.

```bash
aws configservice start-remediation-execution --config-rule-name insecure-security-group --resource-keys file://keys.json
```

Where `keys.json` contains:

```json
[
    {
        "resourceKey": {
            "resourceId": "sg-12345678",
            "resourceType": "AWS::EC2::SecurityGroup"
        }
    }
]
```

### Real-World Examples and Recent Breaches

Recent breaches have highlighted the importance of securing security groups in AWS EC2. For example, the Capital One breach in 2019 was caused by misconfigured security groups that allowed unauthorized access to sensitive data. This breach resulted in the exposure of personal information of over 100 million customers.

### How to Prevent / Defend

To prevent and defend against insecure security group configurations, follow these steps:

1. **Regularly Audit Security Groups**: Regularly audit your security groups to ensure they are configured securely. Use tools like AWS Config to monitor and record the configurations of your EC2 instances.

2. **Implement Auto Remediation**: Implement auto remediation to automatically correct non-compliant configurations. This ensures that your security groups remain secure at all times.

3. **Use Secure Coding Practices**: Use secure coding practices to ensure that your applications are secure. This includes using secure libraries and frameworks, validating user input, and encrypting sensitive data.

4. **Monitor and Detect**: Continuously monitor and detect any new non-compliant configurations. Use tools like AWS CloudTrail to log and monitor API calls made to your AWS resources.

### Complete Example: Vulnerable vs. Secure Configuration

Here’s a complete example of a vulnerable security group configuration and its secure counterpart:

#### Vulnerable Configuration

```json
{
    "IpPermissions": [
        {
            "IpProtocol": "-1",
            "UserIdGroupPairs": [
                {
                    "GroupId": "sg-12345678",
                    "UserId": "123456789012"
                }
            ]
        }
    ]
}
```

This configuration allows unrestricted access to all ports and protocols.

#### Secure Configuration

```json
{
    "IpPermissions": [
        {
            "IpProtocol": "tcp",
            "FromPort": 22,
            "ToPort": 22,
            "UserIdGroupPairs": [
                {
                    "GroupId": "sg-12345678",
                    "UserId": "123456789012"
                }
            ]
        }
    ]
}
```

This configuration restricts access to port 22 (SSH) and only allows traffic from a specific security group.

### Conclusion

By automating compliance through auto remediation, organizations can ensure that their security groups remain secure at all times. This reduces the risk of security vulnerabilities and ensures continuous compliance with regulatory standards and internal policies.

### Practice Labs

For hands-on experience with compliance as code and auto remediation, consider the following labs:

- **CloudGoat**: A cloud security training platform that includes exercises on configuring and managing security groups in AWS.
- **flaws.cloud**: A cloud security training platform that includes exercises on identifying and remediating insecure security group configurations.
- **AWS Well-Architected Labs**: Official AWS labs that include exercises on configuring and managing security groups in AWS.

These labs provide practical experience in configuring and managing security groups in AWS, ensuring that you can effectively implement compliance as code in your organization.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Auto Remediation for Insecure Security Groups for EC2 Instances/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Auto Remediation for Insecure Security Groups for EC2 Instances/02-Introduction to Compliance as Code Part 2|Introduction to Compliance as Code Part 2]]
