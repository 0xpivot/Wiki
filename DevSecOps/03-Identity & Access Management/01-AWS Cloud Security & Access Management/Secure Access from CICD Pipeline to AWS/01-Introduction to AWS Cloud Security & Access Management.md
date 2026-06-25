---
course: DevSecOps
topic: AWS Cloud Security & Access Management
tags: [devsecops]
---

## Introduction to AWS Cloud Security & Access Management

AWS Cloud Security and Access Management is a critical aspect of DevSecOps practices, ensuring that your infrastructure and applications remain secure throughout their lifecycle. This chapter will delve into the intricacies of securing access from a Continuous Integration and Continuous Deployment (CI/CD) pipeline to AWS resources. We'll cover the fundamental concepts, policies, and best practices to ensure robust security.

### Understanding AWS Policies

AWS provides a variety of policies out-of-the-box for different services. These policies define permissions that allow or deny actions on specific resources. Policies can be attached to IAM users, groups, or roles, providing granular control over access.

#### Policy Types

- **IAM Policies**: Define permissions for IAM users, groups, and roles.
- **Resource Policies**: Attached directly to AWS resources, such as S3 buckets or DynamoDB tables.
- **Service Control Policies (SCP)**: Used in Organizations to control access across accounts.

#### Example Policies

Let's look at some example policies:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "ec2:*",
            "Resource": "*"
        }
    ]
}
```

This policy allows all EC2 actions on all resources.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Deny",
            "Action": "iam:DeleteUser",
            "Resource": "arn:aws:iam::123456789012:user/Admin"
        }
    ]
}
```

This policy denies the `DeleteUser` action on the specified IAM user.

### Creating and Assigning Policies

To create and assign policies, follow these steps:

1. **Navigate to IAM Console**:
   - Go to the AWS Management Console.
   - Select "IAM" from the services list.

2. **Create a New Policy**:
   - Click on "Policies" in the left navigation pane.
   - Click "Create policy".
   - Choose "JSON" to write custom policies.

3. **Assign Policy to User**:
   - Navigate to "Users" in the IAM console.
   - Select the user to whom you want to assign the policy.
   - Click "Add permissions".
   - Attach the desired policy.

### Administrator Access Policy

The Administrator Access policy is a pre-defined policy that grants full administrative access to all AWS services. This policy should be used cautiously, as it provides broad permissions.

#### Creating an Admin User

Here’s how to create an admin user and assign the Administrator Access policy:

1. **Create User**:
   - Go to "Users" in the IAM console.
   - Click "Add user".
   - Enter the user name (e.g., `AdminUser`).
   - Select "Programmatic access" and/or "AWS Management Console access".

2. **Set Permissions**:
   - Under "Permissions", select "Attach existing policies directly".
   - Search for "AdministratorAccess" and select it.
   - Click "Next: Tags" and then "Next: Review".

3. **Review and Create**:
   - Review the settings and click "Create user".

4. **Copy Credentials**:
   - After creating the user, copy the access key and secret key. These credentials are required for programmatic access.

### Logging In with Admin Account

Once the admin user is created, you can log in using the provided credentials.

#### Signing In

1. **Copy Sign-In URL**:
   - The sign-in URL includes the account ID and is typically in the format `https://console.aws.amazon.com/console/home?region=us-east-1#`.

2. **Provide Password**:
   - Open the sign-in URL in a browser.
   - Enter the username and password associated with the admin user.

3. **Remember Account**:
   - Check the option to remember the account for future logins.

### Navigating AWS Services

After logging in, you can navigate through various AWS services, such as EC2, S3, RDS, etc.

#### Example: EC2 Dashboard

1. **Navigate to EC2**:
   - From the AWS Management Console, select "EC2" from the services list.
   - You can view and manage EC2 instances, security groups, and other resources.

2. **Launch New Instance**:
   - Click "Launch Instance" to start a new EC2 instance.
   - Follow the prompts to configure the instance type, AMI, storage, and networking settings.

### Multi-Factor Authentication (MFA)

Multi-Factor Authentication (MFA) adds an extra layer of security by requiring a second form of authentication in addition to the password. This helps protect against unauthorized access even if the password is compromised.

#### Enabling MFA

1. **Navigate to IAM User**:
   - Go to "Users" in the IAM console.
   - Select the user for whom you want to enable MFA.

2. **Enable MFA**:
   - Click "Add MFA device".
   - Follow the instructions to configure the MFA device (e.g., using an authenticator app).

3. **Verify MFA**:
   - After enabling MFA, verify the setup by entering the MFA code during login.

### Best Practices for Securing Access

To ensure robust security, follow these best practices:

1. **Least Privilege Principle**:
   - Grant users the minimum permissions necessary to perform their tasks.
   - Avoid using the Administrator Access policy unless absolutely necessary.

2. **Use IAM Roles**:
   - Instead of attaching policies directly to users, use IAM roles to grant permissions.
   - Roles can be assumed by EC2 instances, Lambda functions, and other AWS services.

3. **Enable MFA**:
   - Require MFA for all IAM users, especially those with administrative privileges.

4. **Regularly Audit Permissions**:
   - Periodically review and audit IAM policies to ensure they are still appropriate.
   - Remove unused policies and permissions.

### Real-World Examples and Breaches

Recent breaches and vulnerabilities highlight the importance of proper access management:

- **CVE-2021-44228 (Log4Shell)**: This vulnerability allowed attackers to execute arbitrary code on servers running Apache Log4j. Proper access management could have limited the scope of the breach.
- **AWS Misconfiguration Breaches**: Several high-profile breaches occurred due to misconfigured IAM policies, allowing unauthorized access to sensitive data.

### How to Prevent / Defend

#### Detection

- **AWS CloudTrail**: Monitor API calls made to your AWS account.
- **AWS Config**: Track changes to your AWS resources and configurations.
- **IAM Access Advisor**: Provides insights into which services and actions have been used by IAM entities.

#### Prevention

- **IAM Policies**: Use least privilege principles and regularly review policies.
- **MFA**: Enable MFA for all IAM users.
- **IAM Roles**: Use roles instead of direct policy attachments.

#### Secure Coding Fixes

Compare the insecure and secure versions of IAM policies:

**Insecure Policy**:
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

**Secure Policy**:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:DescribeInstances",
                "ec2:RunInstances"
            ],
            "Resource": "*"
        }
    ]
}
```

### Conclusion

Securing access from a CI/CD pipeline to AWS resources is crucial for maintaining the integrity and confidentiality of your infrastructure. By following best practices, using IAM policies effectively, and enabling MFA, you can significantly enhance your security posture.

### Practice Labs

For hands-on experience, consider the following labs:

- **CloudGoat**: A series of labs designed to help you understand and mitigate common cloud security issues.
- **flaws.cloud**: A platform that simulates real-world cloud environments to test your security skills.
- **AWS Well-Architected Labs**: Official AWS labs that guide you through best practices for designing and deploying secure architectures.

By engaging with these labs, you can gain practical experience in securing your AWS environment.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/01-AWS Cloud Security & Access Management/Secure Access from CICD Pipeline to AWS/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/01-AWS Cloud Security & Access Management/Secure Access from CICD Pipeline to AWS/02-Introduction to AWS Cloud Security and Access Management|Introduction to AWS Cloud Security and Access Management]]
