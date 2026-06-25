---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Introduction to Security Layers for AWS Access

In this section, we will delve into the intricacies of managing AWS access keys, particularly focusing on the root user and the associated security implications. We will explore the creation of CLI credentials, the inherent risks involved, and how to mitigate these risks through proper security practices.

### Understanding AWS Access Keys

AWS access keys are a set of credentials used to authenticate API calls made to AWS services. These keys consist of an access key ID and a secret access key. The access key ID is publicly visible, whereas the secret access key must be kept confidential. Together, these keys function similarly to an email and password pair, providing authentication for programmatic access to AWS resources via the AWS Command Line Interface (CLI).

#### Why Use Access Keys?

Access keys are essential for programmatic access to AWS services. They enable developers and administrators to automate tasks, manage resources, and integrate AWS services into their applications. Without access keys, manual intervention would be required for every interaction with AWS, which is impractical for large-scale operations.

### Creating New CLI Credentials

Let's walk through the process of creating new CLI credentials for a user in AWS. This example will focus on the root user, although the same principles apply to IAM users.

#### Step-by-Step Process

1. **Navigate to IAM Console**: Log in to the AWS Management Console and navigate to the Identity and Access Management (IAM) service.
2. **Select Users**: In the left-hand menu, select "Users."
3. **Choose User**: Select the user for whom you want to create access keys. In this case, we are using the root user.
4. **Create Access Key**: Click on the "Security credentials" tab and then click on "Create access key."

```mermaid
sequenceDiagram
    participant User as Root User
    participant IAM as AWS IAM Console
    User->>IAM: Navigate to IAM Console
    IAM-->>User: Display IAM Dashboard
    User->>IAM: Select Users
    IAM-->>User: List of Users
    User->>IAM: Choose Root User
    IAM-->>User: Display Security Credentials Tab
    User->>IAM: Create Access Key
    IAM-->>User: Generate Access Key Pair
```

#### Warning Messages

When creating access keys for the root user, AWS will display a warning message. This warning is crucial because it highlights the security risks associated with using root user credentials.

```mermaid
sequenceDiagram
    participant User as Root User
    participant IAM as AWS IAM Console
    IAM-->>User: Display Warning Message
    User->>IAM: Acknowledge Warning
    IAM-->>User: Generate Access Key Pair
```

### Access Key Pair

Once you acknowledge the warning, AWS will generate an access key pair consisting of an access key ID and a secret access key. These keys are displayed only once, so it is crucial to save them securely.

```mermaid
sequenceDiagram
    participant User as Root User
    participant IAM as AWS IAM Console
    IAM-->>User: Display Access Key Pair
    User->>IAM: Save Access Key Pair Securely
```

#### Example Access Key Pair

Here is an example of an access key pair:

- **Access Key ID**: `AKIAIOSFODNN7EXAMPLE`
- **Secret Access Key**: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`

These keys should be treated with the utmost confidentiality. Exposure of the secret access key can lead to unauthorized access to your AWS resources.

### Security Implications of Using Root User Credentials

Using root user credentials for programmatic access poses significant security risks. The root user has full administrative privileges, meaning that anyone with access to the root user credentials can perform any action within the AWS account, including deleting resources, modifying configurations, and accessing sensitive data.

#### Real-World Example: AWS Account Compromise

A notable example of the risks associated with using root user credentials is the compromise of an AWS account in 2017. An attacker gained access to the root user credentials and used them to deploy cryptocurrency mining software across the compromised account's resources. This incident resulted in significant financial losses and operational disruptions.

### How to Prevent / Defend Against Root User Credential Misuse

To mitigate the risks associated with using root user credentials, follow these best practices:

1. **Use IAM Users**: Instead of using the root user for programmatic access, create IAM users with the necessary permissions. This allows you to control access at a granular level and limit the potential damage in case of a breach.
2. **Enable Multi-Factor Authentication (MFA)**: Enable MFA for the root user and IAM users to add an additional layer of security.
3. **Rotate Access Keys Regularly**: Rotate access keys periodically to minimize the window of opportunity for an attacker to use stolen credentials.
4. **Monitor and Audit Access**: Use AWS CloudTrail to monitor and audit access to your AWS resources. This helps in detecting unauthorized activities and responding promptly.

#### Example: Creating an IAM User with Programmatic Access

Here is an example of creating an IAM user with programmatic access:

1. **Create IAM User**:
    - Navigate to the IAM console.
    - Click on "Add user."
    - Enter a username and select "Programmatic access."
    - Attach the necessary policies (e.g., `AmazonS3FullAccess`).

```mermaid
sequenceDiagram
    participant User as Admin
    participant IAM as AWS IAM Console
    User->>IAM: Navigate to IAM Console
    IAM-->>User: Display IAM Dashboard
    User->>IAM: Add User
    IAM-->>User: Enter Username
    User->>IAM: Select Programmatic Access
    IAM-->>User: Attach Policies
```

2. **Generate Access Key Pair**:
    - After creating the user, go to the "Security credentials" tab.
    - Click on "Create access key."

```mermaid
sequenceDiagram
    participant User as Admin
    participant IAM as AWS IAM Console
    User->>IAM: Navigate to Security Credentials
    IAM-->>User: Display Security Credentials Tab
    User->>IAM: Create Access Key
    IAM-->>User: Generate Access Key Pair
```

3. **Save Access Key Pair Securely**:
    - Download the access key pair and store it securely.

```mermaid
sequenceDiagram
    participant User as Admin
    participant IAM as AWS IAM Console
    IAM-->>User: Display Access Key Pair
    User->>IAM: Save Access Key Pair Securely
```

### Conclusion

Managing AWS access keys, especially for the root user, requires careful consideration of security practices. By following the best practices outlined above, you can significantly reduce the risk of unauthorized access and ensure the integrity of your AWS resources.

### Practice Labs

For hands-on experience with AWS access keys and IAM management, consider the following labs:

- **CloudGoat**: A cloud security training platform that includes scenarios for managing AWS access keys and IAM roles.
- **flaws.cloud**: A cloud security training platform that provides exercises for securing AWS accounts, including IAM management.

These labs provide practical experience in managing AWS access keys and implementing secure IAM practices.

---

This comprehensive explanation covers the creation of AWS access keys, the associated security risks, and best practices for mitigating those risks. By following these guidelines, you can ensure the security of your AWS resources and avoid common pitfalls.

---
<!-- nav -->
[[03-Introduction to Security Layers for AWS Access Part 2|Introduction to Security Layers for AWS Access Part 2]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Introduction to Security Layers for AWS Access/00-Overview|Overview]] | [[05-Introduction to Security Layers for AWS Access|Introduction to Security Layers for AWS Access]]
