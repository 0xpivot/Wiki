---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## Introduction to Compliance as Code with AWS Config

### What is Compliance as Code?

Compliance as Code is an approach to ensuring that your infrastructure adheres to regulatory and organizational policies through automated checks and enforcement mechanisms. This method leverages Infrastructure as Code (IaC) tools to define compliance rules and continuously monitor and enforce them. By integrating compliance checks into your deployment pipeline, you can ensure that your infrastructure remains compliant throughout its lifecycle.

### Why Use Compliance as Code?

Using Compliance as Code helps organizations maintain regulatory compliance, reduce human error, and automate the enforcement of security policies. This approach ensures that your infrastructure is consistent and secure, reducing the risk of non-compliance penalties and data breaches.

### How Does AWS Config Fit In?

AWS Config is a service provided by Amazon Web Services (AWS) that enables you to assess, audit, and record changes to your AWS resources. It provides a detailed view of your AWS resource configurations, helping you understand and manage your resources more effectively. AWS Config integrates seamlessly with other AWS services like AWS Lambda and AWS CloudTrail to provide comprehensive compliance monitoring.

### Setting Up AWS Config

To set up AWS Config, you need to enable it in your AWS account and configure rules to check for compliance. Here’s a step-by-step guide:

1. **Enable AWS Config**:
    - Navigate to the AWS Management Console.
    - Go to the AWS Config service.
    - Click on "Get started" to enable AWS Config.

2. **Configure Rules**:
    - Define rules to check for specific compliance requirements.
    - You can use predefined rules or create custom rules using AWS Lambda functions.

Here is an example of enabling AWS Config using the AWS CLI:

```sh
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

3. **Create a Delivery Channel**:
    - Configure a delivery channel to store the configuration history in an S3 bucket.

```sh
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

### Example Rule: Ensure EC2 Instances Have Security Groups

Let’s create a rule to ensure that all EC2 instances have associated security groups.

#### Vulnerable Configuration

```yaml
Resources:
  MyEC2Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0c55b159cbfafe1f0
      InstanceType: t2.micro
```

#### Secure Configuration

```yaml
Resources:
  MyEC2Instance:
    Type: AWS::EC2::Instance
    Properties:
      ImageId: ami-0c55b159cbfafe1f0
      InstanceType: t2.micro
      SecurityGroupIds:
        - !Ref MySecurityGroup
  MySecurityGroup:
    Type: AWS::EC2::SecurityGroup
    Properties:
      GroupDescription: Enable SSH access
      VpcId: vpc-0123456789abcdef0
      SecurityGroupIngress:
        - IpProtocol: tcp
          FromPort: 22
          ToPort: 22
          CidrIp: 0.0.0.0/0
```

### Real-World Example: Recent Breach

Consider the breach at Capital One in 2019 (CVE-2019-11510). The attacker exploited misconfigured AWS S3 buckets, which could have been prevented with proper compliance checks. Using AWS Config, you can set up rules to ensure that S3 buckets are properly configured with encryption and access controls.

### How to Prevent / Defend

1. **Detection**:
    - Use AWS Config to continuously monitor your resources for compliance.
    - Set up alerts for non-compliant resources using AWS CloudWatch Events.

2. **Prevention**:
    - Implement strict IAM roles and permissions.
    - Use AWS Config rules to enforce compliance policies.

3. **Secure Coding Fixes**:
    - Always associate security groups with EC2 instances.
    - Ensure S3 buckets are encrypted and have restricted access.

### Practice Labs

For hands-on experience with AWS Config and Compliance as Code, consider the following labs:

- **CloudGoat**: A cloud security training platform that includes exercises on AWS Config and other AWS security services.
- **flaws.cloud**: A cloud security lab that covers various AWS services, including AWS Config.

By following these steps and using the provided examples, you can effectively implement Compliance as Code using AWS Config to ensure your infrastructure remains compliant and secure.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/01-Demo Overview and Introduction to AWS Config/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/01-Demo Overview and Introduction to AWS Config/02-Introduction to Compliance as Code|Introduction to Compliance as Code]]
