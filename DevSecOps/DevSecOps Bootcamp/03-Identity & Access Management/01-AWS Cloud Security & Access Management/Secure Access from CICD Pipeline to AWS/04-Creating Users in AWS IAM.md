---
course: DevSecOps
topic: AWS Cloud Security & Access Management
tags: [devsecops]
---

## Creating Users in AWS IAM

When working with AWS, managing access to resources is critical. One of the primary ways to manage access is through the creation and management of users within the Identity and Access Management (IAM) service. This section will delve into the process of creating a user, specifically an `admin` user, and discuss the various options available during this process.

### Background Theory

AWS IAM is a web service that helps you securely control access to AWS resources. You can use IAM to create and manage AWS users and groups, and to grant permissions to them. IAM also enables you to follow the principle of least privilege, which means granting users only the permissions they need to perform their jobs.

### Creating a User

To create a user in AWS IAM:

1. **Navigate to IAM**: Log in to the AWS Management Console and navigate to the IAM dashboard.
2. **Create User**: Click on the "Users" section and then click on the "Add user" button.

```mermaid
sequenceDiagram
    participant User as U
    participant IAM as I
    U->>I: Navigate to IAM Dashboard
    I-->>U: Display IAM Dashboard
    U->>I: Click on "Users"
    I-->>U: Display Users Section
    U->>I: Click on "Add user"
    I-->>U: Display Add User Form
```

### User Types

When creating a user, you have two main types of access to choose from:

- **Console Access**: Allows the user to log in to the AWS Management Console using a username and password.
- **Programmatic Access**: Provides the user with an access key ID and secret access key, which can be used to programmatically interact with AWS services.

#### Example: Creating an Admin User with Console Access

Let's walk through the steps to create an `admin` user with console access:

1. **User Name**: Enter `admin` as the user name.
2. **Access Type**: Select "Console access".
3. **Permissions**: For now, leave the permissions blank; we will assign them later.

```mermaid
sequenceDiagram
    participant User as U
    participant IAM as I
    U->>I: Enter "admin" as User Name
    U->>I: Select "Console access"
    U->>I: Leave Permissions Blank
    I-->>U: Confirm User Creation
```

### Password Authentication

When creating a user with console access, you need to specify the authentication method. The recommended approach is to set a new password for the user.

1. **Password**: Set a strong password for the user. A strong password should be at least 8 characters long and include a mix of uppercase letters, lowercase letters, numbers, and special characters.

```mermaid
sequenceDiagram
    participant User as U
    participant IAM as I
    U->>I: Set Strong Password
    I-->>U: Confirm Password
```

### Additional Considerations

#### Identity Center (Formerly AWS Single Sign-On)

AWS Identity Center is a service that allows you to centrally manage access to multiple AWS accounts and other applications. It is particularly useful when you have multiple AWS accounts and want to manage access to them from a single location.

However, Identity Center requires AWS Organizations, which is a service for centrally managing multiple AWS accounts. Since this demo does not involve multiple AWS accounts, we will stick with IAM users.

#### Recent Real-World Examples

One notable breach involving AWS credentials was the Capital One data breach in 2019. The attacker gained unauthorized access to Capital One’s AWS environment by exploiting a misconfigured web application firewall. This highlights the importance of securing access to AWS resources.

### How to Prevent / Defend

#### Detection

- **Audit Logs**: Enable AWS CloudTrail to monitor API calls made to your AWS resources. This can help detect unauthorized access attempts.
- **IAM Access Advisor**: Use IAM Access Advisor to see which services a user has accessed and when.

#### Prevention

- **Strong Password Policies**: Enforce strong password policies using IAM password policies.
- **Multi-Factor Authentication (MFA)**: Require MFA for all IAM users to add an extra layer of security.
- **Least Privilege Principle**: Assign only the minimum necessary permissions to users.

#### Secure Coding Fixes

**Vulnerable Code Example**:
```python
import boto3

# Vulnerable: Hardcoded credentials
access_key = 'AKIAIOSFODNN7EXAMPLE'
secret_key = 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'

session = boto3.Session(
    aws_access_key_id=access_key,
    aws_secret_access_key=secret_key
)
```

**Secure Code Example**:
```python
import boto3

# Secure: Use IAM roles and permissions
session = boto3.Session()
```

### Complete Example

#### Full HTTP Request and Response

Creating a user via the AWS CLI:

```bash
aws iam create-user --user-name admin
```

Response:
```json
{
    "User": {
        "Path": "/",
        "UserName": "admin",
        "UserId": "AIDAJDOQEXAMPLE",
        "Arn": "arn:aws:iam::123456789012:user/admin",
        "CreateDate": "2023-10-01T12:00:00Z"
    }
}
```

#### Policy Configuration

Example IAM policy for the `admin` user:

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

### Hands-On Labs

For practical experience with AWS IAM and Cloud Security, consider the following labs:

- **CloudGoat**: A cloud security training platform that simulates real-world cloud environments and vulnerabilities.
- **flaws.cloud**: A platform that provides hands-on labs for learning cloud security best practices.

These labs will help you apply the concepts learned in this chapter to real-world scenarios.

### Conclusion

Creating and managing users in AWS IAM is a fundamental aspect of securing your AWS environment. By following best practices such as using strong passwords, enabling MFA, and adhering to the principle of least privilege, you can significantly enhance the security of your AWS resources.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/01-AWS Cloud Security & Access Management/Secure Access from CICD Pipeline to AWS/03-AWS Cloud Security & Access Management|AWS Cloud Security & Access Management]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/01-AWS Cloud Security & Access Management/Secure Access from CICD Pipeline to AWS/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/01-AWS Cloud Security & Access Management/Secure Access from CICD Pipeline to AWS/05-Multi-Factor Authentication (MFA) in AWS|Multi-Factor Authentication (MFA) in AWS]]
