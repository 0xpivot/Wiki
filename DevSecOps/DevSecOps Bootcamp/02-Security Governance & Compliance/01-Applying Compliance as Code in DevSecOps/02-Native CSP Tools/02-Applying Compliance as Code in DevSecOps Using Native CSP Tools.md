---
course: DevSecOps
topic: Applying Compliance as Code in DevSecOps
tags: [devsecops]
---

## Applying Compliance as Code in DevSecOps Using Native CSP Tools

### Introduction

Compliance as Code (CaC) is a practice that integrates compliance requirements into the development process through automated checks and enforcement mechanisms. This approach ensures that compliance policies are consistently applied across all environments, reducing the risk of non-compliance and associated penalties. In the context of DevSecOps, leveraging native tools provided by Cloud Service Providers (CSPs) can significantly enhance the effectiveness of CaC.

### Understanding Compliance as Code

#### What is Compliance as Code?

Compliance as Code refers to the automation of compliance checks and enforcement using code. This means that compliance policies are defined in code, which can be version-controlled, tested, and deployed alongside application code. By doing so, organizations can ensure that their systems adhere to regulatory requirements and internal policies throughout the software development lifecycle.

#### Why is Compliance as Code Important?

Compliance as Code is crucial because it helps organizations maintain consistent compliance across different environments and teams. Traditional compliance approaches often rely on manual processes, which are error-prone and difficult to scale. Automating compliance checks and enforcement reduces the likelihood of human error and ensures that compliance policies are applied uniformly.

#### How Does Compliance as Code Work?

Compliance as Code typically involves the following steps:

1. **Define Compliance Policies**: Compliance policies are defined in code using a declarative language. These policies specify the desired state of the system in terms of compliance requirements.
2. **Automate Compliance Checks**: Automated tools are used to check whether the actual state of the system matches the desired state specified in the compliance policies.
3. **Enforce Compliance**: If the actual state does not match the desired state, automated tools can take corrective actions to bring the system into compliance.

### Leveraging Native CSP Tools

Cloud Service Providers (CSPs) offer a variety of native tools that can be used to implement Compliance as Code. These tools provide built-in capabilities for defining, checking, and enforcing compliance policies. Some popular CSPs include Amazon Web Services (AWS), Microsoft Azure, and Google Cloud Platform (GCP).

#### Example: AWS Security Hub

AWS Security Hub is a service that provides a comprehensive view of an organization’s security and compliance status across multiple accounts and services. It aggregates and prioritizes findings from multiple AWS security services and third-party partners.

##### Defining Compliance Policies

To define compliance policies in AWS Security Hub, you can use the `aws securityhub create-members` and `aws securityhub invite-members` commands to manage member accounts and enable Security Hub across them.

```bash
# Create members
aws securityhub create-members --account-details '[{"AccountId":"123456789012","Email":"member@example.com"}]'

# Invite members
aws securityhub invite-members --account-ids 123456789012
```

##### Automating Compliance Checks

AWS Security Hub automatically aggregates findings from various security services such as AWS Config, AWS Inspector, and AWS GuardDuty. You can configure Security Hub to send notifications and alerts based on these findings.

```yaml
# Example of a Security Hub finding
{
  "ProductArn": "arn:aws:securityhub:us-east-1::product/aws/securityhub",
  "AwsAccountId": "123456789012",
  "GeneratorId": "arn:aws:securityhub:us-east-1::product/aws/securityhub",
  "AwsRegion": "us-east-1",
  "Severity": {
    "Label": "MEDIUM"
  },
  "Title": "EC2 instance missing security group",
  "Description": "An EC2 instance is missing a security group.",
  "Resources": [
    {
      "Type": "AwsEc2Instance",
      "Id": "i-0123456789abcdef0",
      "Partition": "aws",
      "Region": "us-east-1",
      "Details": {
        "AwsEc2Instance": {
          "IamInstanceProfileArn": "arn:aws:iam::123456789012:instance-profile/my-instance-profile",
          "ImageId": "ami-0abcdef1234567890",
          "InstanceId": "i-0123456789abcdef0",
          "InstanceState": "running",
          "LaunchTime": "2023-01-01T00:00:00Z",
          "PlatformDetails": "Linux/UNIX",
          "PrivateIpAddress": "10.0.0.1",
          "PublicIpAddress": "192.0.2.1",
          "SubnetId": "subnet-0123456789abcdef0",
          "VpcId": "vpc-0123456789abcdef0"
        }
      }
    }
  ]
}
```

##### Enforcing Compliance

Security Hub can be configured to automatically remediate certain issues. For example, you can use AWS Lambda functions to automatically apply security groups to instances that are missing them.

```python
# Example Lambda function to apply security group
import boto3

def lambda_handler(event, context):
    ec2 = boto3.client('ec2')
    instance_id = event['resources'][0]['id']
    security_group_id = 'sg-0123456789abcdef0'
    
    response = ec2.modify_instance_attribute(
        InstanceId=instance_id,
        Groups=[security_group_id]
    )
    return response
```

### Real-World Examples

#### Recent Breaches and CVEs

One notable example of a breach related to compliance failures is the Capital One data breach in 2019. The breach was caused by misconfigured AWS S3 buckets, which exposed sensitive customer data. This incident highlights the importance of proper configuration management and compliance enforcement.

#### Example: Misconfigured S3 Bucket

A misconfigured S3 bucket can be exploited to gain unauthorized access to sensitive data. To prevent such issues, you can use AWS Config to monitor and enforce compliance policies related to S3 bucket configurations.

```json
# Example of an AWS Config rule for S3 bucket public access
{
  "ConfigRuleName": "s3-bucket-public-access",
  "Description": "Checks that S3 buckets are not publicly accessible.",
  "Scope": {
    "ComplianceResourceTypes": ["AWS::S3::Bucket"]
  },
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "S3_BUCKET_PUBLIC_ACCESS"
  }
}
```

### How to Prevent / Defend

#### Detection

To detect compliance violations, you can use tools like AWS Config, AWS Security Hub, and AWS Trusted Advisor. These tools provide continuous monitoring and alerting for compliance issues.

```bash
# Example of using AWS Config to detect non-compliant resources
aws configservice describe-compliance-by-config-rule --config-rule-names s3-bucket-public-access
```

#### Prevention

To prevent compliance violations, you can use tools like AWS CloudFormation, AWS CloudTrail, and AWS Identity and Access Management (IAM) to enforce compliance policies.

```yaml
# Example of an IAM policy to restrict access to S3 buckets
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": "s3:*",
      "Resource": "arn:aws:s3:::my-bucket/*",
      "Condition": {
        "StringNotEquals": {
          "aws:PrincipalTag/Department": "Finance"
        }
      }
    }
  ]
}
```

#### Secure Coding Fixes

To correct insecure configurations, you can use tools like AWS Lambda and AWS Systems Manager to automate remediation tasks.

```python
# Example Lambda function to correct S3 bucket permissions
import boto3

def lambda_handler(event, context):
    s3 = boto3.client('s3')
    bucket_name = event['resources'][0]['id']
    
    response = s3.put_bucket_policy(
        Bucket=bucket_name,
        Policy='{"Version":"2012-10-17","Statement":[{"Sid":"DenyPublicAccess","Effect":"Deny","Principal":"*","Action":"s3:*","Resource":["arn:aws:s3:::' + bucket_name + '","arn:aws:s3:::' + bucket_name + '/*"],"Condition":{"Bool":{"aws:SecureTransport":"false"}}}]}'
    )
    return response
```

### Conclusion

Applying Compliance as Code in DevSecOps using native CSP tools is essential for maintaining consistent compliance across different environments. By leveraging tools like AWS Security Hub, AWS Config, and AWS CloudFormation, organizations can automate compliance checks and enforcement, reducing the risk of non-compliance and associated penalties.

### Practice Labs

For hands-on experience with Compliance as Code in DevSecOps, consider the following labs:

- **PortSwigger Web Security Academy**: Offers modules on securing cloud infrastructure and implementing compliance policies.
- **OWASP Juice Shop**: Provides a vulnerable web application that can be used to practice securing cloud environments.
- **AWS Well-Architected Labs**: Includes labs on implementing compliance policies using AWS native tools.

By completing these labs, you can gain practical experience in applying Compliance as Code in DevSecOps using native CSP tools.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/02-Native CSP Tools/01-Introduction to Compliance as Code in DevSecOps|Introduction to Compliance as Code in DevSecOps]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/02-Native CSP Tools/00-Overview|Overview]] | [[03-Native Cloud Service Provider Tools for Compliance as Code|Native Cloud Service Provider Tools for Compliance as Code]]
