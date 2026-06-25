---
course: DevSecOps
topic: AWS Cloud Security & Access Management
tags: [devsecops]
---

## Introduction to AWS Identity and Access Management (IAM)

AWS Identity and Access Management (IAM) is a service that helps you securely control access to your AWS resources. IAM enables you to manage users, groups, roles, and permissions to ensure that only authorized individuals or systems can perform actions within your AWS environment. This chapter will delve into the concepts of IAM users, groups, and policies, providing a comprehensive understanding of how to effectively manage access in AWS.

### Human Users vs. System Users

In AWS, users are categorized into two main types: human users and system users.

- **Human Users**: These are individual people who interact with AWS through the AWS Management Console or other AWS tools. They typically require console login credentials to access the AWS Management Console.
  
- **System Users**: These are applications, services, or automated processes that interact with AWS programmatically. They require programmatic access credentials, such as access keys and secret keys, to authenticate and authorize their actions.

#### Example: Creating a User for GitLab

When creating a user for GitLab, only programmatic access is relevant because GitLab is a system user. Here’s how you might set up a user for GitLab:

```bash
aws iam create-user --user-name GitLabUser
```

After creating the user, you would then generate access keys for programmatic access:

```bash
aws iam create-access-key --user-name GitLabUser
```

The output will provide the `AccessKeyId` and `SecretAccessKey`, which GitLab will use to authenticate with AWS.

### Root User and Programmatic Access

The root user is the initial account created when you sign up for AWS. It has full access to all resources and services. However, it is recommended to avoid using the root user for day-to-day operations and instead create IAM users with appropriate permissions.

For the root user, only UI access is relevant. AWS recommends removing access keys from the root user to prevent unauthorized programmatic access. Here’s how you can remove access keys from the root user:

```bash
aws iam delete-access-key --access-key-id <access-key-id> --user-name root
```

### IAM Policies

An IAM policy is a document that specifies permissions. Policies are used to grant or deny access to AWS resources. A policy defines who can do what to which resources and under which conditions.

#### Policy Structure

A policy is a JSON document that contains one or more statements. Each statement consists of the following elements:

- **Effect**: Specifies whether the statement allows or denies access (`Allow` or `Deny`).
- **Action**: Specifies the action(s) that the policy applies to.
- **Resource**: Specifies the AWS resource(s) that the policy applies to.
- **Condition**: Specifies the conditions under which the policy applies.

Here’s an example of a policy that allows starting and stopping EC2 instances:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:StartInstances",
                "ec2:StopInstances"
            ],
            "Resource": "arn:aws:ec2:*:*:instance/*",
            "Condition": {
                "StringEquals": {
                    "ec2:Owner": "your-account-id"
                }
            }
        },
        {
            "Effect": "Allow",
            "Action": "ec2:DescribeInstances",
            "Resource": "*"
        }
    ]
}
```

This policy allows the user to start and stop EC2 instances owned by a specific account and to describe all instances.

### Granular Permissions

Policies in AWS are highly granular, allowing you to specify exact permissions for each resource. You can grant read-only, write, delete, and other types of access to specific resources. Additionally, you can apply conditions to further restrict access.

#### Example: Conditional Access

Suppose you want to allow a user to start and stop instances only if the instances have a specific tag:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:StartInstances",
                "ec2:StopInstances"
            ],
            "Resource": "arn:aws:ec2:*:*:instance/*",
            "Condition": {
                "StringEquals": {
                    "ec2:ResourceTag/Environment": "production"
                }
            }
        }
    ]
}
```

This policy allows the user to start and stop instances only if they have the tag `Environment=production`.

### Using Managed Policies

AWS provides managed policies that you can use to quickly assign permissions to users. Managed policies are predefined sets of permissions that cover common use cases. You can attach these policies to users, groups, or roles.

#### Example: Attaching a Managed Policy

To attach a managed policy to a user, you can use the following command:

```bash
aws iam attach-user-policy --user-name GitLabUser --policy-arn arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess
```

This command attaches the `AmazonEC2ReadOnlyAccess` policy to the `GitLabUser`, granting read-only access to EC2 resources.

### How to Prevent / Defend

#### Detection

Regularly review IAM policies and access keys to ensure they are up-to-date and secure. Use AWS CloudTrail to log API calls and monitor for unauthorized access attempts.

#### Prevention

- **Least Privilege Principle**: Grant users only the permissions they need to perform their job functions.
- **MFA (Multi-Factor Authentication)**: Enable MFA for all IAM users to add an extra layer of security.
- **Periodic Review**: Regularly review and update IAM policies to reflect current business needs and security requirements.
- **Access Key Rotation**: Rotate access keys periodically to minimize the risk of unauthorized access.

#### Secure Coding Fixes

Compare the insecure and secure versions of a policy:

**Insecure Policy:**

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
                "ec2:StartInstances",
                "ec2:StopInstances"
            ],
            "Resource": "arn:aws:ec2:*:*:instance/*",
            "Condition": {
                "StringEquals": {
                    "ec2:Owner": "your-account-id"
                }
            }
        },
        {
            "Effect": "Allow",
            "Action": "ec2:DescribeInstances",
            2012-10-17",
            "Resource": "*"
        }
    ]
}
```

### Real-World Examples

#### Recent Breaches

One notable breach occurred in 2021 when a misconfigured S3 bucket exposed sensitive data due to overly permissive IAM policies. The bucket was accessible to anyone on the internet, leading to a significant data leak.

#### Secure Configuration

To prevent such breaches, ensure that IAM policies are tightly controlled and reviewed regularly. Use AWS Config to monitor compliance with security policies.

### Hands-On Labs

For practical experience with AWS IAM, consider the following labs:

- **CloudGoat**: A hands-on lab that simulates common cloud misconfigurations and vulnerabilities.
- **flaws.cloud**: A platform that provides real-world cloud security challenges and scenarios.
- **AWS Well-Architected Labs**: Official AWS labs that cover various aspects of cloud architecture and security.

These labs will help you gain hands-on experience with IAM and other AWS security features.

### Conclusion

Effective management of IAM users, groups, and policies is crucial for maintaining a secure AWS environment. By understanding the principles of least privilege, using managed policies, and regularly reviewing access controls, you can significantly reduce the risk of unauthorized access and data breaches.

---
<!-- nav -->
[[03-Introduction to AWS IAM Users, Groups, and Policies|Introduction to AWS IAM Users, Groups, and Policies]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/01-AWS Cloud Security & Access Management/IAM Users Groups Policies/00-Overview|Overview]] | [[05-AWS Cloud Security & Access Management IAM Users, Groups, and Policies|AWS Cloud Security & Access Management IAM Users, Groups, and Policies]]
