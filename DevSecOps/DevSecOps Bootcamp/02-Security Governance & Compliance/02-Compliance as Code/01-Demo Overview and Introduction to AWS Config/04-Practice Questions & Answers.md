---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. What is AWS Config and how does it help in maintaining compliance in AWS environments?**

AWS Config is a service provided by Amazon Web Services (AWS) that enables you to assess, audit, and manage your AWS resource configurations. It helps in maintaining compliance by continuously evaluating your resources against predefined security benchmarks, such as the Center for Internet Security (CIS) benchmarks. If a resource becomes non-compliant due to changes, AWS Config can alert you and even automatically remediate the issue to bring the resource back into compliance. This ensures that your AWS environment adheres to specified security policies and standards, reducing the risk of security breaches and regulatory non-compliance.

**Q2. How can AWS Config be configured to auto-remediate non-compliant resources?**

To configure AWS Config for auto-remediation, you need to set up remediation actions using AWS Systems Manager Automation documents. Here’s a high-level overview of the steps:

1. **Create a Remediation Action**: Define what action should be taken when a resource becomes non-compliant. For example, if CloudTrail is disabled, you might create an automation document to re-enable it.
   
2. **Configure AWS Config Rules**: Set up AWS Config rules to monitor specific compliance requirements. For instance, you can create a rule to ensure CloudTrail is always enabled.

3. **Link Remediation Actions to Config Rules**: Associate the remediation action with the corresponding AWS Config rule. When the rule detects a non-compliant state, it triggers the remediation action.

4. **Test and Validate**: Test the setup to ensure that the remediation actions work as expected. This involves simulating non-compliant states and verifying that the remediation actions restore compliance.

Here’s a simplified example of creating a remediation action using an AWS CLI command:

```bash
aws configservice put-remediation-configurations \
    --config-rules "ConfigRuleName=ensure-cloudtrail-enabled,TargetId=arn:aws:ssm:us-west-2:123456789012:document/AWS-EnableCloudTrail"
```

This command links the `ensure-cloudtrail-enabled` rule to an SSM document that enables CloudTrail.

**Q3. Explain why enabling CloudTrail in all regions is important for AWS compliance.**

Enabling CloudTrail in all regions is crucial for maintaining comprehensive visibility and auditing capabilities within your AWS environment. CloudTrail provides detailed records of API calls made within your AWS account, including who made the call, when it was made, and from which IP address. This information is essential for several reasons:

1. **Audit Trails**: CloudTrail logs provide a complete audit trail of all activities performed in your AWS account, which is critical for compliance with regulations such as GDPR, HIPAA, and PCI-DSS.

2. **Security Monitoring**: By tracking API activity, you can detect unauthorized access attempts or suspicious behavior early, helping to prevent security breaches.

3. **Incident Response**: In the event of a security incident, CloudTrail logs can be used to trace the sequence of events leading up to the incident, aiding in forensic analysis and response efforts.

4. **Compliance Checks**: Many compliance frameworks require continuous monitoring and logging of all activities. Ensuring CloudTrail is enabled in all regions helps meet these requirements.

Failure to enable CloudTrail in all regions can leave gaps in your audit logs, potentially missing critical events that occur outside the monitored region. This could lead to non-compliance and increased risk of undetected security issues.

**Q4. Why is it important to restrict incoming traffic to EC2 instances from all public IPs, and how can AWS Config help enforce this policy?**

Restricting incoming traffic to EC2 instances from all public IPs is crucial for maintaining the security and integrity of your AWS environment. Allowing unrestricted access from any public IP address increases the risk of unauthorized access, potential attacks, and data breaches. By limiting access to only trusted sources, you reduce the attack surface and enhance overall security.

AWS Config can help enforce this policy by setting up a rule to monitor and ensure that security groups associated with EC2 instances do not allow inbound traffic from all public IPs. Here’s how you can configure this:

1. **Create an AWS Config Rule**: Use the AWS Management Console or AWS CLI to create a custom rule that checks for security group rules that allow inbound traffic from `0.0.0.0/0`.

2. **Monitor Compliance**: Once the rule is active, AWS Config continuously monitors your security groups and alerts you if any non-compliant rules are detected.

3. **Auto-Remediation**: Optionally, you can configure the rule to automatically remove or modify the non-compliant security group rules to restrict access appropriately.

For example, you can use the following AWS CLI command to create a custom rule:

```bash
aws configservice put-config-rule \
    --config-rule-name "restrict-public-ip-access" \
    --source-owner "AWS" \
    --source-identifier "SECURITY_GROUP_NO_PUBLIC_IP_ACCESS" \
    --input-parameters '{"securityGroupRuleDescription": "Inbound rule should not allow traffic from all public IPs."}'
```

This rule ensures that security groups do not allow unrestricted inbound traffic, thereby enforcing a more secure posture for your EC2 instances.

**Q5. Provide a recent real-world example where AWS Config could have helped prevent a security breach.**

A notable example is the Capital One data breach in 2019, where a misconfigured web application firewall (WAF) led to unauthorized access to sensitive customer data. The attacker exploited a misconfiguration in the WAF settings, which allowed them to bypass authentication and gain access to over 100 million customer records.

In this scenario, AWS Config could have played a significant role in preventing the breach by:

1. **Monitoring Configuration Changes**: AWS Config could have been set up to monitor changes to the WAF configuration and alert the security team if any unauthorized modifications were made.

2. **Automated Remediation**: If AWS Config had been configured to automatically remediate misconfigurations, it could have restored the WAF settings to their intended state, potentially blocking the attacker’s access.

3. **Continuous Auditing**: Regular audits conducted by AWS Config could have identified the misconfiguration before it was exploited, allowing the organization to take corrective action proactively.

By leveraging AWS Config, organizations can implement robust monitoring and automated remediation processes to detect and mitigate misconfigurations that could otherwise lead to serious security breaches.

---
<!-- nav -->
[[03-Compliance as Code with AWS Config|Compliance as Code with AWS Config]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/01-Demo Overview and Introduction to AWS Config/00-Overview|Overview]]
