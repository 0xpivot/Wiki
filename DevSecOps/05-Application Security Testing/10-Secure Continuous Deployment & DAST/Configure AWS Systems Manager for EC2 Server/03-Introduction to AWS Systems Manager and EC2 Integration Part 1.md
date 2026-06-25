---
course: DevSecOps
topic: Secure Continuous Deployment & DAST
tags: [devsecops]
---

## Introduction to AWS Systems Manager and EC2 Integration

AWS Systems Manager is a powerful tool designed to help manage your Amazon Elastic Compute Cloud (EC2) instances and other AWS resources efficiently. It provides a unified console to automate operational tasks such as patch management, inventory management, and configuration management. One of the key features of Systems Manager is the ability to establish secure sessions with EC2 instances using Session Manager, which allows you to interact with your instances without needing to open inbound ports or manage SSH keys.

### Background Theory

Before diving into the specifics of configuring AWS Systems Manager for an EC2 instance, it’s important to understand the underlying concepts:

1. **IAM Roles**: Identity and Access Management (IAM) roles are used to grant permissions to AWS services and resources. By assigning an IAM role to an EC2 instance, you can control what actions the instance can perform within AWS.
   
2. **Session Manager**: This feature of Systems Manager enables you to remotely access your EC2 instances securely without requiring SSH or RDP access. It uses the AWS Management Console or the AWS CLI to initiate a session.

3. **Permissions**: Properly configuring permissions is crucial to ensure that only authorized users can access and manage your EC2 instances via Systems Manager.

### Configuring IAM Role for EC2 Instance

To enable an EC2 instance to be managed by Systems Manager, you need to assign an IAM role that includes the necessary permissions. Here’s a step-by-step guide to configure this:

#### Step 1: Create an IAM Role

1. **Navigate to IAM Console**: Go to the AWS Management Console and navigate to the IAM service.
2. **Create New Role**: Click on “Roles” and then “Create role”.
3. **Select Trusted Entity**: Choose “EC2” as the trusted entity.
4. **Attach Policies**: Attach the following policies:
   - `AmazonSSMManagedInstanceCore`: This policy grants the minimum permissions required for an EC2 instance to be managed by Systems Manager.
   - `AmazonEC2RoleforSSM`: This policy grants additional permissions for Systems Manager to manage the instance.

```mermaid
graph TD
    A[Create IAM Role] --> B[Select EC2 as Trusted Entity]
    B --> C[Attach AmazonSSMManagedInstanceCore Policy]
    C --> D[Attach AmazonEC2RoleforSSM Policy]
```

#### Step 2: Assign IAM Role to EC2 Instance

Once the IAM role is created, you need to assign it to your EC2 instance:

1. **Navigate to EC2 Console**: Go to the AWS Management Console and navigate to the EC2 service.
2. **Select Instance**: Find the EC2 instance you want to configure and select it.
3. **Assign IAM Role**: In the “Security” tab, click on “Edit” and assign the IAM role you created earlier.

```mermaid
graph TD
    A[Select EC2 Instance] --> B[Go to Security Tab]
    B --> C[Click Edit]
    C --> D[Assign Created IAM Role]
```

### Verifying Systems Manager Connectivity

After assigning the IAM role, it may take some time for the changes to propagate and for the instance to become ready for Systems Manager connections. Here’s how you can verify the connectivity:

1. **Refresh Instance State**: Wait for the instance state to refresh and for the Session Manager connection option to pick up the change.
2. **Check Connection Status**: Once the instance is ready, you should see the “Active Connection” button in the Systems Manager console.

```mermaid
graph TD
    A[Wait for Changes to Propagate] --> B[Check Active Connection Button]
    B --> C[Verify Session Manager Connectivity]
```

### Establishing a Session with EC2 Instance

Once the instance is configured correctly, you can establish a session using Session Manager:

1. **Initiate Session**: In the Systems Manager console, find your EC2 instance and click on the “Active Connection” button.
2. **Access Terminal**: You will be presented with a terminal interface that allows you to interact with the instance securely.

```mermaid
graph TD
    A[Find EC2 Instance] --> B[Click Active Connection Button]
    B --> C[Access Terminal Interface]
```

### Real-World Examples and Recent Breaches

Recent breaches and vulnerabilities have highlighted the importance of securing remote access to EC2 instances. For example, the SolarWinds breach in 2020 demonstrated how critical it is to have robust security measures in place. Using Session Manager helps mitigate risks associated with traditional SSH access by providing a more controlled and secure method of accessing instances.

### Pitfalls and Common Mistakes

1. **Incorrect Permissions**: Failing to attach the correct IAM policies can result in insufficient permissions for Systems Manager to manage the instance.
2. **Propagation Delay**: It’s important to wait for the changes to propagate before attempting to establish a session.
3. **Network Configuration**: Ensure that the instance’s security group rules allow the necessary outbound traffic for Systems Manager.

### How to Prevent / Defend

#### Detection

1. **Audit Logs**: Regularly review CloudTrail logs to monitor access and activity related to Systems Manager.
2. **IAM Policies**: Use IAM policies to restrict access to Systems Manager to only authorized users.

#### Prevention

1. **Secure IAM Roles**: Ensure that IAM roles assigned to EC2 instances have the minimum necessary permissions.
2. **Use Session Manager**: Prefer using Session Manager over traditional SSH access to reduce exposure.

#### Secure Coding Fixes

Here’s an example of how to configure an IAM role securely:

**Vulnerable Code:**
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

**Fixed Code:**
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ssm:*",
                "ec2messages:*"
            ],
            "Resource": "*"
        }
    ]
}
```

### Complete Example

#### Full HTTP Request and Response

When configuring IAM roles and permissions, you might interact with the AWS API. Here’s an example of a complete HTTP request and response:

**HTTP Request:**
```http
POST / HTTP/1.1
Host: iam.amazonaws.com
Content-Type: application/x-amz-json-1.1
X-Amz-Target: iam.CreateRole
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20170320/us-east-1/iam/aws4_request, SignedHeaders=content-type;host;x-amz-date;x-amz-target, Signature=0b0c9f38b4e53d5a0b2c9f38b4e53d5a0b2c9f38b4e53d5a0b2c9f38b4e53d5a
X-Amz-Date: 20170320T120000Z

{
    "RoleName": "MyEC2InstanceRole",
    "AssumeRolePolicyDocument": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"ec2.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
}
```

**HTTP Response:**
```http
HTTP/1.1 200 OK
Content-Type: application/x-amz-json-1.1
x-amzn-RequestId: 12345678-1234-1234-1234-1234567890ab
x-amz-apigw-id: ABCDEFGHIJKLMNOPQRSTUVWXYZ

{
    "Role": {
        "Path": "/",
        "RoleName": "MyEC2InstanceRole",
        "RoleId": "AROAIOSFODNN7EXAMPLE",
        "Arn": "arn:aws:iam::123456789012:role/MyEC2InstanceRole",
        "CreateDate": "2017-03-20T12:00:00Z",
        "AssumeRolePolicyDocument": "{\"Version\":\"2012-10-17\",\"Statement\":[{\"Effect\":\"Allow\",\"Principal\":{\"Service\":\"ec2.amazonaws.com\"},\"Action\":\"sts:AssumeRole\"}]}"
    }
}
```

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers comprehensive modules on AWS security, including configuring IAM roles and using Session Manager.
- **CloudGoat**: Provides a series of challenges and scenarios to practice securing AWS environments, including EC2 instances.

By thoroughly understanding and implementing these steps, you can ensure that your EC2 instances are securely managed using AWS Systems Manager.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/Configure AWS Systems Manager for EC2 Server/02-Introduction to AWS Systems Manager (SSM)|Introduction to AWS Systems Manager (SSM)]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/Configure AWS Systems Manager for EC2 Server/00-Overview|Overview]] | [[04-Introduction to AWS Systems Manager and EC2 Integration|Introduction to AWS Systems Manager and EC2 Integration]]
