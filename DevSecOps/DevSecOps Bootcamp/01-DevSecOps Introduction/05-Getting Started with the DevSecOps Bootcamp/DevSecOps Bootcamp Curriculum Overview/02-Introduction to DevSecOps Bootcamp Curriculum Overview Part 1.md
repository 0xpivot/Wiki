---
course: DevSecOps
topic: Getting Started with the DevSecOps Bootcamp
tags: [devsecops]
---

## Introduction to DevSecOps Bootcamp Curriculum Overview

Welcome to the DevSecOps Bootcamp curriculum overview. This section will delve into the core concepts of AWS Identity and Access Management (IAM) and secure deployment practices. We'll cover the secure and proper usage of IAM users, groups, policies, and roles, as well as secure network configurations and dynamic application security testing (DAST).

### AWS Identity and Access Management (IAM)

AWS Identity and Access Management (IAM) is a web service that helps you securely control access to AWS resources. IAM enables you to manage users and their permissions, ensuring that only authorized individuals can access specific resources.

#### Users, Groups, and Policies

- **Users**: Individual accounts that can log in to the AWS Management Console or use the AWS CLI or SDKs. Each user has a unique set of permissions defined by policies attached to them.
- **Groups**: Collections of users that share similar permissions. Policies can be attached to groups, simplifying permission management.
- **Policies**: Documents that specify permissions. They define what actions a user or group can perform on which resources.

**Example Policy**:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListAllMyBuckets",
                "s3:GetBucketLocation"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": "arn:aws:s3:::example-bucket"
        }
    ]
}
```

This policy allows a user to list all buckets and get bucket locations, and specifically list the contents of `example-bucket`.

#### Roles

Roles are a crucial component of IAM, especially in automated environments. A role is an IAM entity that defines a set of permissions. Unlike users and groups, roles are not associated with specific individuals; instead, they are assumed by entities like EC2 instances, Lambda functions, or other AWS services.

**Why Roles Matter**:

- **Automation**: In automated environments, services and scripts interact with each other. Roles provide a way to grant temporary, limited permissions to these services.
- **Security**: Using roles reduces the risk of exposing long-term credentials. Roles can be configured to provide short-lived access tokens, enhancing security.

**Example Role Configuration**:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```

This role allows EC2 instances to assume the role and perform actions defined by the role's policies.

### Secure Deployment Practices

Secure deployment involves ensuring that your environment is configured correctly and securely. This includes secure access management and secure network configurations.

#### Secure Access Management

- **IAM Best Practices**:
  - Use least privilege principle: Grant only the minimum permissions necessary.
  - Rotate access keys regularly.
  - Use multi-factor authentication (MFA) for added security.

**Example of IAM User with MFA**:

```bash
# Enable MFA for an IAM user
aws iam enable-mfa-device --user-name my-user --serial-number arn:aws:iam::123456789012:mfa/my-user --authentication-code1 123456 --authentication-code2 654321
```

#### Secure Network Configurations

- **Network Security Groups (NSGs)**: Define rules for inbound and outbound traffic to instances.
- **Virtual Private Cloud (VPC)**: Isolate your resources in a logically isolated virtual network.

**Example VPC Configuration**:

```json
{
    "Resources": {
        "MyVPC": {
            "Type": "AWS::EC2::VPC",
            "Properties": {
                "CidrBlock": "10.0.0.0/16",
                "EnableDnsSupport": true,
                "EnableDnsHostnames": true
            }
        },
        "MySubnet": {
            "Type": "AWS::EC2::Subnet",
            "Properties": {
                "VpcId": { "Ref": "MyVPC" },
                "CidrBlock": "10.0.1.0/24"
            }
        },
        "MySecurityGroup": {
            "Type": "AWS::EC2::SecurityGroup",
             "Properties": {
                "GroupName": "MySecurityGroup",
                "GroupDescription": "Allow SSH access",
                "VpcId": { "Ref": "MyVPC" },
                "SecurityGroupIngress": [
                    {
                        "IpProtocol": "tcp",
                        "FromPort": "22",
                        "ToPort": "22",
                        "CidrIp": "0.0.0.0/0"
                    }
                ]
            }
        }
    }
}
```

### Dynamic Application Security Testing (DAST)

Dynamic Application Security Testing (DAST) is a type of security testing performed on a running application. DAST tools simulate attacks on the application to identify vulnerabilities.

#### Static Application Security Testing (SAST)

Static Application Security Testing (SAST) analyzes the source code of an application to find security vulnerabilities. SAST is also known as white-box testing.

**Example SAST Tool**: SonarQube

```bash
# Install SonarQube Scanner
wget https://binaries.sonarsource.com/Distribution/sonar-scanner-cli/sonar-scanner-cli-4.6.2.2472-linux.zip
unzip sonar-scanner-cli-4.6.2.2472-linux.zip
cd sonar-scanner-4.6.2.2472-linux/bin/

# Run SonarQube analysis
./sonar-scanner -Dsonar.projectKey=myproject -Dsonar.sources=src
```

### Real-World Examples and Recent Breaches

#### Example: Capital One Data Breach (CVE-2019-11510)

In 2019, Capital One suffered a data breach due to misconfigured AWS S3 buckets. The attacker exploited a misconfigured WAF rule, allowing unauthorized access to sensitive data.

**Mitigation**:

- Ensure proper configuration of S3 buckets and WAF rules.
- Regularly audit IAM policies and roles.

### How to Prevent / Defend

#### Detection and Prevention

- **IAM Policies**: Regularly review and update IAM policies to ensure least privilege.
- **Network Security**: Use VPCs and NSGs to isolate and control network traffic.
- **Application Security**: Implement both SAST and DAST to identify and mitigate vulnerabilities.

#### Secure Coding Fixes

**Vulnerable Code**:

```python
import boto3

def get_s3_data(bucket_name, key):
    s3 = boto3.resource('s3')
    obj = s3.Object(bucket_name, key)
    return obj.get()['Body'].read().decode('utf-8')
```

**Fixed Code**:

```python
import boto3

def get_s3_data(bucket_name, key):
    s3 = boto3.client('s3', config=boto3.session.Config(signature_version='s3v4'))
    response = s3.get_object(Bucket=bucket_name, Key=key)
    return response['Body'].read().decode('utf-8')
```

### Hands-On Labs

For practical experience, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web app for learning security.
- **WebGoat**: An interactive training application designed to teach web application security lessons.

### Conclusion

This overview has covered the foundational aspects of IAM, secure deployment practices, and dynamic application security testing. By understanding and implementing these principles, you can significantly enhance the security of your AWS environment and applications.

---

This expanded explanation covers the core concepts of IAM, secure deployment, and dynamic application security testing in depth, providing detailed explanations, real-world examples, and practical guidance.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/05-Getting Started with the DevSecOps Bootcamp/DevSecOps Bootcamp Curriculum Overview/01-Introduction to Application Security in DevSecOps|Introduction to Application Security in DevSecOps]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/05-Getting Started with the DevSecOps Bootcamp/DevSecOps Bootcamp Curriculum Overview/00-Overview|Overview]] | [[03-Introduction to DevSecOps Bootcamp Curriculum Overview|Introduction to DevSecOps Bootcamp Curriculum Overview]]
