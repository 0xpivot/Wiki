---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the importance of creating an admin user with limited privileges in an AWS account.**

Creating an admin user with limited privileges in an AWS account is crucial for several reasons:

1. **Security**: Using the root user for daily administrative tasks poses significant risks. The root user has unlimited access to all AWS services and features, including billing and account settings. Limiting the privileges of an admin user reduces the risk of accidental or malicious actions that could compromise the entire AWS environment.

2. **Compliance**: Many organizations are required to comply with regulatory standards that mandate the principle of least privilege. By creating an admin user with only the necessary permissions, organizations can better adhere to these compliance requirements.

3. **Auditability**: With a dedicated admin user, it becomes easier to track and audit actions performed within the AWS environment. This helps in identifying potential security issues and maintaining accountability.

4. **Operational Efficiency**: Assigning specific permissions to an admin user streamlines operations. The admin user can focus on tasks related to managing AWS resources without being burdened by unnecessary permissions.

**Q2. How would you create a user group in IAM for a DevOps team that needs access to EC2 and S3 services?**

To create a user group in IAM for a DevOps team that needs access to EC2 and S3 services, follow these steps:

1. **Log in to the AWS Management Console**: Use your admin credentials to access the IAM service.

2. **Create a Group**: Navigate to the "Groups" section in IAM and click on "Create group."

3. **Name the Group**: Provide a descriptive name for the group, such as "DevOpsTeam."

4. **Attach Policies**: Attach the necessary policies to the group. For EC2 and S3 access, you might use policies like `AmazonEC2FullAccess` and `AmazonS3FullAccess`. Alternatively, you can create custom policies to grant specific permissions.

5. **Add Users to the Group**: Once the group is created, navigate to the "Users" section and select the users you want to add to the group. Click on "Add to group" and choose the group you created.

Here is an example of a custom policy for EC2 and S3 access:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:*"
            ],
            "Resource": "*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "s3:*"
            ],
            "Resource": "*"
        }
    ]
}
```

This policy grants full access to EC2 and S3 services.

**Q3. What is the difference between IAM users and roles, and why are roles necessary for AWS services?**

IAM users and roles serve different purposes in AWS:

- **IAM Users**: These are accounts for individuals or applications that need to interact with AWS services. They can be assigned specific permissions and can log in to the AWS Management Console or use the AWS CLI.

- **IAM Roles**: These are similar to users but are intended to be assumed by AWS services or applications. Roles do not have credentials associated with them; instead, they are assumed by entities that need temporary access to perform specific tasks.

Roles are necessary for AWS services because:

1. **Service-to-Service Access**: AWS services often need to access other services to perform tasks. Instead of embedding credentials directly into the service, roles provide a secure way to grant temporary access.

2. **Least Privilege Principle**: Roles allow you to grant the minimum set of permissions required for a service to perform its tasks, adhering to the principle of least privilege.

3. **Temporary Credentials**: When a service assumes a role, it receives temporary credentials that expire after a set period, enhancing security by reducing the window of opportunity for misuse.

For example, an EC2 instance might assume a role to access S3 buckets. This ensures that the EC2 instance has only the necessary permissions to perform its tasks without having broader access to other services.

**Q4. How would you create a role for an AWS service like ECS that needs to create EC2 instances?**

To create a role for an AWS service like ECS that needs to create EC2 instances, follow these steps:

1. **Navigate to IAM**: Log in to the AWS Management Console and navigate to the IAM service.

2. **Create a Role**: Click on "Roles" and then "Create role."

3. **Select Trusted Entity**: Choose the type of trusted entity that will assume this role. For ECS, select "AWS service."

4. **Choose Service**: Select the specific service that will assume the role, such as "ECS."

5. **Attach Permissions Policy**: Attach a policy that grants the necessary permissions to create EC2 instances. You can use a managed policy like `AmazonEC2FullAccess` or create a custom policy.

6. **Name the Role**: Provide a descriptive name for the role, such as "ECSInstanceCreationRole."

7. **Review and Create**: Review the details and click "Create role."

Here is an example of a custom policy for ECS to create EC2 instances:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ec2:RunInstances",
                "ec2:TerminateInstances",
                "ec2:DescribeInstances"
            ],
            "Resource": "*"
        }
    ]
}
```

This policy grants permissions to run, terminate, and describe EC2 instances.

**Q5. Why is it recommended to use groups instead of assigning permissions directly to individual users?**

Using groups instead of assigning permissions directly to individual users is recommended for several reasons:

1. **Simplified Management**: Managing permissions at the group level simplifies the process of assigning and updating permissions. Changes made to a group automatically apply to all users in that group.

2. **Consistency**: Groups ensure consistency across users with similar roles. All members of a group receive the same set of permissions, reducing the likelihood of errors and inconsistencies.

3. **Scalability**: As the number of users grows, managing permissions at the group level becomes more efficient. Adding or removing users from a group is simpler than managing permissions for each user individually.

4. **Auditability**: Group-based permissions make it easier to audit access and permissions. You can review the permissions assigned to a group and quickly identify which users have access to specific resources.

By using groups, you can maintain a clear and organized structure for managing access and permissions in your AWS environment.

---
<!-- nav -->
[[02-IAM User Management Best Practices on AWS|IAM User Management Best Practices on AWS]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/17-IAM User Management Best Practices On AWS/00-Overview|Overview]]
