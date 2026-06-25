---
course: DevSecOps
topic: AWS Cloud Security & Access Management
tags: [devsecops]
---

## Understanding AWS Access Management Using IAM Service

### Introduction to IAM

AWS Identity and Access Management (IAM) is a web service that helps you securely control access to AWS resources. With IAM, you can manage users, groups, roles, and permissions. This allows you to grant access to specific resources and actions within your AWS environment. IAM is crucial because it ensures that only authorized entities can perform actions, thereby enhancing the security of your AWS infrastructure.

### Key Concepts in IAM

#### Users
Users represent individuals who need access to AWS resources. Each user has a unique set of credentials (username and password) and can be assigned specific permissions.

#### Groups
Groups are collections of users. You can assign permissions to a group, which then applies to all members of that group. This simplifies permission management by allowing you to manage permissions at the group level rather than individually for each user.

#### Roles
Roles are similar to users but are intended for services or applications rather than people. Roles allow temporary access to AWS resources. They are particularly useful for cross-account access and for granting permissions to AWS services like Lambda functions or EC2 instances.

#### Policies
Policies define what actions are allowed or denied on specific resources. Policies can be attached to users, groups, or roles. There are two types of policies:

- **Managed Policies**: These are created and managed by AWS or by you. Managed policies can be attached to multiple entities.
- **Inline Policies**: These are embedded directly into a user, group, or role.

### Setting Up IAM Users and Groups

Let's walk through an example of setting up IAM users and groups.

#### Creating a User

To create a new IAM user, follow these steps:

1. Sign in to the AWS Management Console.
2. Open the IAM console.
3. In the navigation pane, choose **Users**.
4. Choose **Add user**.
5. Enter a username.
6. Select the type of access (programmatic access, AWS Management Console access, or both).
7. Set permissions for the user (you can attach policies later).

Here’s an example of creating a user via the AWS CLI:

```bash
aws iam create-user --user-name myUser
```

#### Creating a Group

To create a group, follow these steps:

1. In the IAM console, choose **Groups**.
2. Choose **Create group**.
3. Enter a group name.
4. Add users to the group.
5. Attach policies to the group.

Here’s an example of creating a group via the AWS CLI:

```bash
aws iam create-group --group-name myGroup
```

### Attaching Policies

Policies define the permissions granted to users, groups, or roles. Let's look at an example of attaching a policy to a group.

#### Example Policy

Consider a policy that allows read-only access to Amazon S3 buckets:

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
            "Resource": "arn:aws:s3:::*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:ListBucket",
                "s3:GetObject"
            ],
            "Resource": [
                "arn:aws:s3:::my-bucket",
                "arn:aws:s3:::my-bucket/*"
            ]
        }
    ]
}
```

This policy allows listing all buckets and getting bucket locations, as well as listing objects and downloading objects from `my-bucket`.

#### Attaching the Policy

To attach this policy to a group, you can use the following AWS CLI command:

```bash
aws iam put-group-policy \
    --group-name myGroup \
    --policy-name s3ReadOnlyPolicy \
    --policy-document file://path/to/policy.json
```

### Real-World Examples and Recent Breaches

#### Example: Capital One Data Breach (CVE-2019-11610)

In 2019, Capital One suffered a data breach due to misconfigured AWS S3 buckets. The attacker exploited a misconfigured WAF rule, which allowed unauthorized access to sensitive data stored in S3 buckets. This breach highlights the importance of proper IAM configuration and the need for strict access controls.

#### Example: Tesla Data Breach (CVE-2020-11022)

Tesla experienced a data breach where an attacker gained access to internal systems due to weak IAM configurations. The attacker used stolen credentials to access Tesla's internal systems, leading to the exposure of sensitive information. This incident underscores the necessity of strong IAM practices, including multi-factor authentication (MFA) and least privilege principles.

### How to Prevent / Defend

#### Detection

Regularly audit IAM configurations to identify and mitigate potential risks. Use AWS CloudTrail to log API calls and monitor access patterns. Additionally, use AWS Config to track resource configurations and ensure compliance with security policies.

#### Prevention

1. **Least Privilege Principle**: Grant only the minimum permissions necessary for users, groups, and roles.
2. **Multi-Factor Authentication (MFA)**: Enable MFA for all IAM users to add an extra layer of security.
3. **IAM Policies**: Use fine-grained policies to restrict access to specific resources and actions.
4. **Periodic Reviews**: Regularly review and update IAM configurations to address new threats and vulnerabilities.

#### Secure Coding Fixes

Here’s an example of a vulnerable IAM policy and its secure counterpart:

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

This policy grants full administrative access, which is highly insecure.

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
                "arn:aws:s3:::my-bucket",
                "arn:aws:s3:::my-bucket/*"
            ]
        }
    ]
}
```

This policy restricts access to specific S3 actions and resources, adhering to the least privilege principle.

### Hands-On Practice

For hands-on practice with AWS IAM, consider the following labs:

- **CloudGoat**: A cloud security training platform that includes scenarios for IAM misconfigurations and attacks.
- **flaws.cloud**: A cloud security training platform that provides real-world scenarios for practicing IAM configurations and securing AWS environments.
- **AWS Official Workshops**: AWS offers various workshops and labs that cover IAM and other security topics in depth.

These labs provide practical experience in configuring IAM and managing access to AWS resources securely.

### Conclusion

Understanding and effectively using AWS IAM is crucial for maintaining the security of your AWS environment. By properly configuring users, groups, roles, and policies, you can ensure that only authorized entities have access to

---
<!-- nav -->
[[01-Introduction to AWS Identity and Access Management (IAM)|Introduction to AWS Identity and Access Management (IAM)]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/01-AWS Cloud Security & Access Management/06-Understand AWS Access Management using IAM Service/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/01-AWS Cloud Security & Access Management/06-Understand AWS Access Management using IAM Service/03-Practice Questions & Answers|Practice Questions & Answers]]
