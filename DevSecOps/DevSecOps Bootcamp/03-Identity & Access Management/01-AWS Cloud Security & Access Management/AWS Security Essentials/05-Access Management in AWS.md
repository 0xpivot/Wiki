---
course: DevSecOps
topic: AWS Cloud Security & Access Management
tags: [devsecops]
---

## Access Management in AWS

Access management is a critical aspect of securing your AWS environment. It ensures that only authorized individuals or services can access and perform actions on your resources. This section will delve into the concepts, mechanisms, and best practices for managing access in AWS, including roles, policies, and security configurations.

### Roles and Permissions

In AWS, roles and permissions are used to control access to resources. A role is an entity that defines a set of permissions. Users, services, or other entities can assume these roles to gain the associated permissions. Permissions are defined using policies, which are JSON documents that specify what actions can be performed on which resources.

#### Role Creation and Assignment

To create a role, you define a policy that specifies the permissions. Here’s an example of creating a role with specific permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket"
            ],
            "Resource": [
                "arn:aws:s3:::example-bucket"
            ]
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::example-bucket/*"
            ]
        }
    ]
}
```

This policy allows the role to list objects in the `example-bucket` and retrieve objects from it.

#### Assigning Roles to Users

Once a role is created, it can be assigned to users or services. This can be done through the AWS Management Console or programmatically using the AWS CLI or SDKs.

```bash
aws iam attach-role-policy --role-name ExampleRole --policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess
```

This command attaches the `AmazonS3ReadOnlyAccess` policy to the `ExampleRole`.

### Network Security Configuration

Network security is crucial for protecting your AWS resources. This includes configuring security groups, network ACLs, and VPCs.

#### Security Groups

Security groups act as virtual firewalls that control inbound and outbound traffic to your instances. Each security group consists of rules that allow or deny traffic based on protocol, port range, and source or destination.

```json
{
    "IpPermissions": [
        {
            "FromPort": 22,
            "ToPort": 22,
            "IpProtocol": "tcp",
            "UserIdGroupPairs": [],
            "IpRanges": [
                {
                    "CidrIp": "0.0.0.0/0"
                }
            ]
        }
    ]
}
```

This rule allows SSH traffic from any IP address.

#### Network ACLs

Network ACLs provide an additional layer of security by filtering traffic at the subnet level. They are stateless and can be used to allow or deny traffic based on protocol, port range, and source or destination.

```json
{
    "Rules": [
        {
            "RuleNumber": 100,
            "Protocol": "-1",
            "RuleAction": "allow",
            "Egress": false,
            "CidrBlock": "0.0.0.0/0"
        }
    ]
}
```

This rule allows all inbound traffic.

### Secret Management

Managing secrets such as private keys and API tokens is essential for maintaining the security of your applications. AWS provides several services for managing secrets, including AWS Secrets Manager and AWS Key Management Service (KMS).

#### AWS Secrets Manager

AWS Secrets Manager allows you to store, manage, and retrieve secrets securely. You can store secrets such as database credentials, API keys, and other sensitive information.

```json
{
    "Name": "MySecret",
    "SecretString": "{\"username\":\"myuser\",\"password\":\"mypassword\"}"
}
```

This JSON object represents a secret stored in AWS Secrets Manager.

#### AWS KMS

AWS KMS provides encryption keys that can be used to encrypt and decrypt data. It integrates with other AWS services to provide seamless encryption capabilities.

```json
{
    "KeyId": "alias/my-key",
    "Plaintext": "my-sensitive-data"
}
```

This JSON object represents a plaintext string that can be encrypted using a key managed by AWS KMS.

### Recent Real-World Examples

#### CVE-2021-20225

CVE-2021-20225 was a vulnerability in AWS IAM that allowed unauthorized access to resources. This vulnerability was due to improper validation of permissions in IAM policies.

**Impact:** Unauthorized access to resources.

**Mitigation:** Ensure proper validation of IAM policies and regularly review access logs.

#### Breach of Capital One

In 2019, Capital One suffered a breach due to misconfigured AWS S3 buckets. The attacker exploited a misconfiguration in the bucket policy, allowing unauthorized access to sensitive customer data.

**Impact:** Exposure of sensitive customer data.

**Mitigation:** Regularly audit S3 bucket policies and ensure proper access controls.

### How to Prevent / Defend

#### Detection

Regularly monitor and audit access logs to detect unauthorized access attempts. Use AWS CloudTrail to log API calls and AWS Config to track resource changes.

```json
{
    "Records": [
        {
            "eventVersion": "1.05",
            "userIdentity": {
                "type": "IAMUser",
                "principalId": "AIDAJDPLRKLG7UEXAMPLE",
                "arn": "arn:aws:sts::123456789012:user/MightyMouse",
                "accountId": "123456789012",
                "accessKeyId": "AKIAIOSFODNN7EXAMPLE",
                "userName": "MightyMouse",
                "sessionContext": {
                    "attributes": {
                        "mfaAuthenticated": "false",
                        "creationDate": "2020-06-22T18:29:42Z"
                    }
                }
            },
            "eventTime": "2020-06-22T18:29:42Z",
            "eventSource": "iam.amazonaws.com",
            "eventName": "CreateAccessKey",
            "awsRegion": "us-east-1",
            "sourceIPAddress": "192.0.2.1",
            "userAgent": "[AWSConsole]"
        }
    ]
}
```

This JSON object represents a CloudTrail log entry.

#### Prevention

Implement least privilege access by granting users and services only the permissions they need to perform their tasks. Use IAM roles and policies to enforce access controls.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Deny",
            "Action": "*",
            "Resource": "*",
            "Condition": {
                "Bool": {
                    "aws:MultiFactorAuthPresent": "false"
                }
            }
        }
    ]
}
```

This policy denies access to all actions unless multi-factor authentication (MFA) is present.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of IAM policies.

**Vulnerable Policy:**

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

**Secure Policy:**

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::example-bucket",
                "arn:aws:s3:::example-b
```

### Mermaid Diagrams

#### Access Control Flow

```mermaid
sequenceDiagram
    participant User
    participant IAM
    participant Resource
    User->>IAM: Request access
    IAM-->>User: Check permissions
    User->>Resource: Perform action
    Resource-->>User: Return result
```

#### Network Topology

```mermaid
graph TD
    A[Internet] --> B[Public Subnet]
    B --> C[Security Group]
    C --> D[Instance]
    E[VPC] --> F[Private Subnet]
    F --> G[Instance]
    H[Internet Gateway] --> B
    I[NAT Gateway] --> F
```

### Practice Labs

For hands-on practice with AWS security and access management, consider the following labs:

- **CloudGoat**: A cloud security training platform that simulates various AWS security scenarios.
- **flaws.cloud**: A cloud security training platform that focuses on identifying and fixing security misconfigurations in AWS.
- **AWS Well-Architected Labs**: Official AWS labs that cover various aspects of cloud architecture and security.

These labs provide practical experience in configuring and securing AWS environments, helping you to apply the concepts learned in this chapter.

---
<!-- nav -->
[[04-AWS Cloud Security & Access Management|AWS Cloud Security & Access Management]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/01-AWS Cloud Security & Access Management/AWS Security Essentials/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/01-AWS Cloud Security & Access Management/AWS Security Essentials/06-Practice Questions & Answers|Practice Questions & Answers]]
