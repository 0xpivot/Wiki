---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## Configuring Auto Remediation for Insecure Security Groups

In this section, we will configure auto-remediation for insecure security groups associated with EC2 instances. Specifically, we will focus on restricting SSH access to ensure compliance with security policies.

### Step-by-Step Configuration

#### 1. Create an IAM Role

First, create an IAM role that AWS Systems Manager will use to execute the remediation script. This role should have the necessary permissions to modify security groups.

```bash
aws iam create-role --role-name SSMRemediationRole --assume-role-policy-document '{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ssm.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}'
```

Next, attach the necessary policies to the role. For modifying security groups, you need the `AmazonEC2FullAccess` policy.

```bash
aws iam attach-role-policy --role-name SSMRemediationRole --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess
```

#### 2. Define the Remediation Action

Now, define the remediation action in AWS Config. This action will remove SSH access from all addresses for non-compliant security groups.

```bash
aws configservice put-remediation-configurations --remediation-configurations '[{
  "ConfigRuleName": "restricted-ssh-rule",
  "TargetId": "arn:aws:iam::123456789012:role/SSMRemediationRole",
  "Parameters": {
    "SecurityGroupId": {
      "ParameterValue": "sg-0123456789abcdef0"
    }
  }
}]'
```

### Detailed Explanation

The above commands create an IAM role named `SSMRemediationRole` and attach the `AmazonEC2FullAccess` policy to it. This role is then used as the target for the remediation action defined in AWS Config.

The `put-remediation-configurations` command specifies the `ConfigRuleName` (`restricted-ssh-rule`) and the `TargetId`, which is the ARN of the IAM role. The `Parameters` field includes the `SecurityGroupId` of the security group to be remediated.

### Mermaid Diagram

Here is a mermaid diagram illustrating the flow of the remediation process:

```mermaid
sequenceDiagram
  participant User
  participant IAM
  participant SSM
  participant Config
  participant EC2

  User->>IAM: Create IAM Role
  IAM-->>User: Role Created
  User->>IAM: Attach Policy
  IAM-->>User: Policy Attached
  User->>Config: Define Remediation Action
  Config-->>User: Action Defined
  Config->>SSM: Execute Script
  SSM-->>Config: Script Executed
  SSM->>EC2: Modify Security Group
  EC2-->>SSM: Security Group Modified
```

### Pitfalls and Common Mistakes

- **Insufficient Permissions**: Ensure that the IAM role has the necessary permissions to modify security groups. Missing permissions can cause the remediation action to fail.
- **Incorrect Security Group ID**: Double-check the `SecurityGroupId` parameter to ensure it points to the correct security group. An incorrect ID can lead to unintended modifications.
- **Manual Overrides**: Be cautious of manual overrides that might bypass the automated remediation process. Regular audits can help identify such issues.

### How to Prevent / Defend

#### Detection

To detect non-compliant security groups, you can use AWS Config rules. For example, the `restricted-ssh-rule` can be configured to check for SSH access from all addresses.

```json
{
  "ConfigRuleName": "restricted-ssh-rule",
  "Description": "Checks for SSH access from all addresses",
  "Scope": {
    "ComplianceResourceTypes": ["AWS::EC2::SecurityGroup"]
  },
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "SECURITY_GROUP_NO_SSH_FROM_ALL"
  }
}
```

#### Prevention

To prevent non-compliance, ensure that the remediation action is correctly configured and that the IAM role has the necessary permissions. Regularly review and update the remediation configurations to adapt to changing compliance requirements.

#### Secure Coding Fix

Here is a comparison of a vulnerable security group configuration versus a secure one:

**Vulnerable Configuration**

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

**Secure Configuration**

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

### Complete Example

#### Full HTTP Request and Response

Here is an example of the full HTTP request and response for creating a new security group rule:

**Request**

```http
POST /?Action=AuthorizeSecurityGroupIngress&Version=2016-11-15 HTTP/1.1
Host: ec2.amazonaws.com
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20150101/us-west-2/ec2/aws4_request, SignedHeaders=host;x-amz-date, Signature=fe5f4faa6b30aa4e96ffdebea9080cf845d4c9b02b4c6f6f89cb3a1c2f9b40ac
X-Amz-Date: 20150101T000000Z
Content-Type: application/x-www-form-urlencoded; charset=utf-8

GroupId=sg-0123456789abcdef0&IpPermissions.1.IpProtocol=tcp&IpPermissions.1.FromPort=22&IpPermissions.1.ToPort=22&IpPermissions.1.IpRanges.1.CidrIp=0.0.0.0/0
```

**Response**

```http
HTTP/1.1 200 OK
Content-Type: text/xml
Content-Length: 342
Connection: keep-alive
Date: Thu, 01 Jan 2015 00:00:00 GMT
Server: AmazonEC2

<?xml version="1.0" encoding="UTF-8"?>
<AuthorizeSecurityGroupIngressResponse xmlns="http://ec2.amazonaws.com/doc/2016-11-15/">
  <requestId>7a62c49f-347e-4fc4-9331-6e8eEXAMPLE</requestId>
  <return>true</return>
</AuthorizeSecurityGroupIngressResponse>
```

### Hands-On Lab Suggestions

For hands-on practice with Compliance as Code, consider the following labs:

- **CloudGoat**: A cloud security training platform that includes scenarios for configuring and enforcing compliance policies.
- **flaws.cloud**: A cloud security training environment that covers various aspects of securing AWS resources, including compliance as code.
- **AWS Official Workshops**: AWS provides several workshops and labs that cover compliance and security best practices, including Compliance as Code.

By following these steps and best practices, you can effectively implement Compliance as Code to ensure that your AWS resources remain compliant with your organization’s security policies.

---
<!-- nav -->
[[10-Compliance as Code Configuring Auto Remediation for Insecure Security Groups for EC2 Instances|Compliance as Code Configuring Auto Remediation for Insecure Security Groups for EC2 Instances]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Auto Remediation for Insecure Security Groups for EC2 Instances/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Auto Remediation for Insecure Security Groups for EC2 Instances/12-Practice Questions & Answers|Practice Questions & Answers]]
