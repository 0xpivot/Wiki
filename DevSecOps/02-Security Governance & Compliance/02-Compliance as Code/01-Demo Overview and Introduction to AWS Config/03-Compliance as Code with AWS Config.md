---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## Compliance as Code with AWS Config

### Introduction to Compliance as Code

Compliance as Code is a DevSecOps practice that automates the enforcement of compliance policies within your infrastructure. This approach ensures that your systems adhere to regulatory requirements and internal policies through automated checks and remediations. One of the key services used for this in the AWS ecosystem is AWS Config.

AWS Config is a service that enables you to assess, audit, and record changes to your AWS resources. It helps you maintain compliance with internal policies and external regulations by continuously monitoring your resources and providing detailed reports on their configurations.

### Importance of Logging and CloudTrail

One of the critical aspects of maintaining compliance is ensuring that you have proper logging mechanisms in place. In the context of AWS, this means enabling CloudTrail across all regions.

#### What is CloudTrail?

CloudTrail is a service that enables governance, compliance, operational auditing, and risk auditing of your AWS account. It provides a history of AWS API calls made within your account, including the identity of the API caller, the time of the API call, the source IP address of the API caller, and the request parameters.

#### Why is CloudTrail Important?

CloudTrail is crucial because it allows you to:

- **Audit Actions**: Track who performed actions in your AWS account, when they were performed, and from which IP address.
- **Detect Unauthorized Activity**: Identify unauthorized access attempts or suspicious activity.
- **Maintain Compliance**: Ensure that your organization complies with regulatory requirements such as GDPR, HIPAA, and PCI-DSS.

#### Enabling CloudTrail

To ensure that CloudTrail is enabled in all regions, you can use the following AWS CLI command:

```bash
aws cloudtrail create-trail --name MyTrail --s3-bucket-name my-bucket --include-global-service-events
```

This command creates a new trail named `MyTrail` and specifies an S3 bucket (`my-bucket`) where the logs will be stored. The `--include-global-service-events` flag ensures that global service events are included in the trail.

#### Monitoring CloudTrail Status

Once CloudTrail is enabled, you can use AWS Config to monitor its status. AWS Config evaluates the compliance of your resources based on predefined rules. If CloudTrail is disabled, AWS Config will mark the resource as non-compliant.

Here is an example of how to check the status of CloudTrail using AWS Config:

```bash
aws configservice describe-compliance-by-config-rule --config-rule-names MyCloudTrailRule
```

This command retrieves the compliance details for the rule named `MyCloudTrailRule`.

### Example of a Real-World Breach

A real-world example of the importance of logging and monitoring is the Capital One breach in 2019 (CVE-2019-11510). The attacker exploited a misconfigured web application firewall (WAF) to gain unauthorized access to sensitive data. Proper logging and monitoring could have helped detect this unauthorized access earlier.

### How to Prevent / Defend

#### Detection

To detect if CloudTrail is disabled, you can set up an AWS Config rule that checks the status of CloudTrail. Here is an example of how to create such a rule:

```yaml
{
  "ConfigRuleName": "cloudtrail-enabled",
  "Description": "Checks if CloudTrail is enabled in all regions.",
  "Scope": {
    "ComplianceResourceTypes": [
      "AWS::CloudTrail::Trail"
    ]
  },
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "CLOUDTRAIL_ENABLED"
  }
}
```

This rule checks if CloudTrail is enabled in all regions. If it finds that CloudTrail is disabled, it marks the resource as non-compliant.

#### Prevention

To prevent CloudTrail from being disabled, you can use AWS Config to automatically remediate the issue. Here is an example of how to create a remediation action:

```yaml
{
  "RemediationAction": {
    "AwsApiCall": {
      "Service": "cloudtrail",
      "Api": "startLogging",
      "Region": "us-east-1",
      "Parameters": {
        "Name": "MyTrail"
      }
    }
  }
}
```

This action starts logging for the specified CloudTrail trail if it is disabled.

### Restricting Public Access to EC2 Instances

Another critical aspect of maintaining compliance is ensuring that your EC2 instances are not accessible from the public internet. This includes restricting access to administrative ports like SSH.

#### What is the Risk?

Allowing public access to your EC2 instances can expose them to various attacks, such as brute-force password guessing, exploitation of vulnerabilities, and unauthorized access.

#### How to Restrict Public Access

To restrict public access to your EC2 instances, you can use security groups and network ACLs. Here is an example of how to configure a security group to allow only specific IP addresses to access the SSH port:

```yaml
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

This configuration allows only the IP range `192.168.1.0/24` to access the SSH port on the EC2 instance.

#### Monitoring Security Group Configuration

To ensure that your security group configurations remain compliant, you can use AWS Config to monitor them. Here is an example of how to create a rule to check if public access is restricted:

```yaml
{
  "ConfigRuleName": "restrict-public-access",
  "Description": "Checks if public access is restricted for EC2 instances.",
  "Scope": {
    "ComplianceResourceTypes": [
      "AWS::EC2::SecurityGroup"
    ]
  },
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "RESTRICT_PUBLIC_ACCESS"
  }
}
```

This rule checks if public access is restricted for EC2 instances. If it finds that public access is allowed, it marks the resource as non-compliant.

### Example of a Real-World Breach

A real-world example of the importance of restricting public access is the Equifax breach in 2017 (CVE-2017-5638). The attacker exploited a vulnerability in Apache Struts to gain unauthorized access to sensitive data. Proper restrictions on public access could have prevented this unauthorized access.

### How to Prevent / Defend

#### Detection

To detect if public access is allowed, you can set up an AWS Config rule that checks the security group configurations. Here is an example of how to create such a rule:

```yaml
{
  "ConfigRuleName": "public-access-restricted",
  "Description": "Checks if public access is restricted for EC2 instances.",
  "Scope": {
    "ComplianceResourceTypes": [
      "AWS::EC2::SecurityGroup"
    ]
  },
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "PUBLIC_ACCESS_RESTRICTED"
  }
}
```

This rule checks if public access is restricted for EC2 instances. If it finds that public access is allowed, it marks the resource as non-compliant.

#### Prevention

To prevent public access from being allowed, you can use AWS Config to automatically remediate the issue. Here is an example of how to create a remediation action:

```yaml
{
  "RemediationAction": {
    "AwsApiCall": {
      "Service": "ec2",
      "Api": "authorizeSecurityGroupIngress",
      "Region": "us-east-1",
      "Parameters": {
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
    }
  }
}
```

This action authorizes only the specified IP range to access the SSH port on the EC2 instance.

### Conclusion

By using AWS Config to automate the enforcement of compliance policies, you can ensure that your AWS resources adhere to regulatory requirements and internal policies. This includes ensuring that CloudTrail is enabled and that public access to your EC2 instances is restricted. By setting up appropriate rules and remediation actions, you can detect and prevent non-compliance issues before they become major security risks.

### Practice Labs

For hands-on experience with AWS Config and compliance as code, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on web security, including compliance and logging practices.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing and compliance.
- **CloudGoat**: A series of labs designed to help you understand and implement security best practices in AWS.
- **flaws.cloud**: Provides a set of vulnerable environments for practicing security assessments and compliance checks.

These labs will help you gain practical experience in implementing and maintaining compliance as code in your AWS environment.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/01-Demo Overview and Introduction to AWS Config/02-Introduction to Compliance as Code|Introduction to Compliance as Code]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/01-Demo Overview and Introduction to AWS Config/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/01-Demo Overview and Introduction to AWS Config/04-Practice Questions & Answers|Practice Questions & Answers]]
