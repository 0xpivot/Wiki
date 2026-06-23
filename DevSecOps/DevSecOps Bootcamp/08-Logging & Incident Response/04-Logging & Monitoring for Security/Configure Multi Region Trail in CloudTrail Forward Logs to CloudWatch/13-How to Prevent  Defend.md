---
course: DevSecOps
topic: Logging & Monitoring for Security
tags: [devsecops]
---

## How to Prevent / Defend

### Detection

To detect potential security threats, you can set up CloudWatch Alarms based on specific metrics or log patterns. For example, you can create an alarm to notify you if there are multiple failed login attempts.

### Prevention

To prevent unauthorized access and ensure security, follow these best practices:

1. **Least Privilege Principle**:
    - Assign minimal necessary permissions to IAM users and roles.

2. **MFA (Multi-Factor Authentication)**:
    - Enable MFA for all IAM users.

3. **Regular Audits**:
    - Regularly review CloudTrail logs to identify suspicious activities.

4. **Secure S3 Bucket Policies**:
    - Ensure S3 bucket policies are correctly set to restrict access.

### Secure Coding Fixes

Here’s an example of a vulnerable IAM policy and its secure version:

#### Vulnerable IAM Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*"
    }
  ]
}
```

#### Secure IAM Policy

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:RunInstances",
        "ec2:TerminateInstances"
      ],
      "Resource": "*"
    }
  ]
}
```

### Hardening Measures

1. **IAM Role Usage**:
    - Use IAM roles instead of IAM users for EC2 instances.

2. **S3 Bucket Encryption**:
    - Enable server-side encryption for S3 buckets storing CloudTrail logs.

3. **CloudTrail Log Validation**:
    - Enable log validation to ensure the integrity of CloudTrail logs.

### Real-World Examples

#### Recent Breach Example: Capital One Data Breach (2019)

In the Capital One data breach, an attacker exploited a misconfigured web application firewall to gain unauthorized access to sensitive data. Proper logging and monitoring could have helped detect and mitigate such attacks.

#### CVE Example: CVE-2021-20225

This CVE involves a vulnerability in AWS CloudFormation that could allow unauthorized access to resources. Proper logging and monitoring would help detect such unauthorized access attempts.

### Practice Labs

For hands-on practice with logging and monitoring in AWS, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but includes sections on logging and monitoring.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another web application for learning about web security.
- **WebGoat**: An interactive training application for learning about web security.

These labs provide practical experience in setting up and managing logging and monitoring systems in cloud environments.

---
<!-- nav -->
[[12-Configuring Multi-Region Trail in CloudTrail|Configuring Multi-Region Trail in CloudTrail]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/04-Logging & Monitoring for Security/Configure Multi Region Trail in CloudTrail Forward Logs to CloudWatch/00-Overview|Overview]] | [[14-Logging & Monitoring for Security Configuring Multi-Region Trail in CloudTrail and Forwarding Logs to CloudWatch|Logging & Monitoring for Security Configuring Multi-Region Trail in CloudTrail and Forwarding Logs to CloudWatch]]
