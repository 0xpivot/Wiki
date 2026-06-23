---
course: DevSecOps
topic: AWS Cloud Security & Access Management
tags: [devsecops]
---

## Introduction to AWS IAM Users, Groups, and Policies

In the realm of DevSecOps, managing access control in cloud environments such as AWS is critical. This chapter delves into the core concepts of AWS Identity and Access Management (IAM) focusing on users, groups, and policies. We'll explore how these components work together to enforce the principle of least privilege, ensuring that each entity within your organization has only the permissions necessary to perform their tasks.

### Least Privilege Access

The principle of least privilege (PoLP) is a fundamental security concept that states that every module (such as a process, a user, or a program) must be able to access only the information and resources that are necessary for its legitimate purpose. This approach minimizes the potential damage that can occur if a system is compromised.

#### Why Least Privilege Matters

- **Security**: By limiting permissions, you reduce the attack surface. An attacker who gains access to a low-privilege account has limited capabilities.
- **Compliance**: Many regulatory frameworks require organizations to implement least privilege access controls.
- **Auditability**: It makes it easier to track and audit actions performed by different users, as each user has a well-defined set of permissions.

#### How to Implement Least Privilege

To implement least privilege, start by identifying the minimum set of permissions required for each role within your organization. Then, assign these permissions to individual users or groups. Here’s a step-by-step guide:

1. **Identify Roles**: Define roles based on job functions (e.g., developer, administrator, auditor).
2. **Define Permissions**: Determine the specific permissions needed for each role.
3. **Assign Permissions**: Assign these permissions to users or groups.
4. **Review and Update**: Regularly review and update permissions to ensure they remain appropriate.

### IAM Users

An IAM user is an entity that you create in AWS to represent a person or service that needs to interact with AWS resources. Each user has a unique name and can be assigned specific permissions.

#### Creating an IAM User

To create an IAM user, follow these steps:

1. Log in to the AWS Management Console.
2. Navigate to the IAM dashboard.
3. Click on "Users" and then "Add user."
4. Enter a username and select the type of access (programmatic access, AWS Management Console access, or both).
5. Set up the initial password and access key if needed.
6. Attach policies or permissions to the user.

Here’s an example of creating an IAM user via the AWS CLI:

```bash
aws iam create-user --user-name Developer1
```

### IAM Groups

Groups are collections of IAM users. You can attach policies to groups, which simplifies permission management. Instead of assigning permissions to each user individually, you can assign them to a group and then add users to that group.

#### Creating an IAM Group

To create an IAM group, follow these steps:

1. Log in to the AWS Management Console.
2. Navigate to the IAM dashboard.
3. Click on "Groups" and then "Create group."
4. Enter a group name and attach policies to the group.
5. Add users to the group.

Here’s an example of creating an IAM group via the AWS CLI:

```bash
aws iam create-group --group-name Developers
```

### IAM Policies

Policies define what actions a user or group can perform on which resources. Policies are written in JSON format and can be attached to users, groups, or roles.

#### Policy Structure

A typical policy looks like this:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:RunInstances",
                "ecr:PutImage"
            ],
            "Resource": "*"
        }
    ]
}
```

- **Version**: Specifies the version of the policy language.
- **Statement**: Contains one or more statements defining permissions.
- **Effect**: Determines whether the statement allows or denies access.
- **Action**: Specifies the actions allowed or denied.
- **Resource**: Specifies the resources to which the action applies.

#### Example: Developer Policy

Let’s create a policy for developers that allows them to create EC2 instances and push images to an ECR registry:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:RunInstances",
                "ecr:PutImage"
            ],
            "Resource": "*"
        }
    ]
}
```

### Assigning Policies to Users and Groups

Once you have created a policy, you can attach it to a user or group.

#### Attaching a Policy to a Group

```bash
aws iam attach-group-policy --group-name Developers --policy-arn arn:aws:iam::aws:policy/AmazonEC2FullAccess
```

### Managing Large Teams

In larger organizations, managing permissions for hundreds of users can become complex. Using groups helps streamline this process.

#### Example: Networking Administrators

For networking administrators, you might create a group with permissions limited to networking services:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:Describe*",
                "vpc:*"
            ],
            "Resource": "*"
        }
    ]
}
```

### Real-World Examples and Breaches

#### Recent Breaches

One notable breach occurred in 2021 where an attacker gained unauthorized access to an AWS account due to misconfigured IAM policies. The attacker was able to escalate privileges and gain access to sensitive data.

#### CVE Example

CVE-2021-20225 involved a misconfiguration in IAM policies that allowed unauthorized access to S3 buckets. This highlights the importance of properly configuring IAM policies to prevent such vulnerabilities.

### How to Prevent / Defend

#### Detection

Regularly audit IAM policies and user permissions using tools like AWS Trusted Advisor or third-party security scanners.

#### Prevention

1. **Least Privilege**: Ensure that each user or group has only the permissions necessary for their role.
2. **Regular Audits**: Conduct regular audits of IAM policies and user permissions.
3. **Multi-Factor Authentication (MFA)**: Enable MFA for all IAM users to add an extra layer of security.
4. **IAM Access Analyzer**: Use AWS IAM Access Analyzer to automatically discover and analyze permissions granted to IAM principals.

#### Secure Coding Fixes

**Vulnerable Code Example**:

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

**Secure Code Example**:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:RunInstances",
                "ecr:PutImage"
            ],
            "Resource": "*"
        }
    ]
}
```

### Conclusion

Managing access control in AWS using IAM users, groups, and policies is essential for maintaining security and compliance. By adhering to the principle of least privilege and regularly auditing permissions, you can significantly reduce the risk of unauthorized access and data breaches.

### Practice Labs

For hands-on experience with AWS IAM, consider the following labs:

- **CloudGoat**: A series of labs designed to help you understand and mitigate common cloud security issues.
- **flaws.cloud**: A platform that simulates real-world cloud environments with intentional security flaws for educational purposes.
- **AWS Official Workshops**: AWS provides various workshops that cover IAM and other security topics in depth.

By completing these labs, you can gain practical experience in managing IAM users, groups, and policies effectively.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/01-AWS Cloud Security & Access Management/IAM Users Groups Policies/00-Overview|Overview]] | [[02-Introduction to AWS IAM Users, Groups, and Policies Part 2|Introduction to AWS IAM Users, Groups, and Policies Part 2]]
