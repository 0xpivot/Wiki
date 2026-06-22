---
course: DevSecOps
topic: AWS Cloud Security & Access Management
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the difference between a root user and an admin user in AWS IAM.**

The root user is the initial user created when an AWS account is set up. This user has full administrative privileges over all AWS resources within the account. The root user can perform any action, including accessing billing information, closing the account, and updating account settings. However, due to the high level of risk associated with having too many users with full administrative access, it is recommended to use the root user only for critical administrative tasks.

An admin user, on the other hand, is a custom user created specifically for administrative purposes. This user is granted permissions through policies that allow it to manage resources and perform administrative tasks without needing the full access of the root user. Admin users are used to avoid the risks associated with using the root user for day-to-day operations and to adhere to the principle of least privilege.

**Q2. How would you configure programmatic access for a CI/CD tool like GitLab to interact with AWS resources?**

To configure programmatic access for a CI/CD tool like GitLab, you would first create an IAM user dedicated to this purpose. Since GitLab does not require UI access, you would enable only programmatic access for this user. After creating the user, you would generate access keys (access key ID and secret access key) for the user. These keys are then configured in GitLab as environment variables or secrets, allowing GitLab to authenticate and interact with AWS resources programmatically.

Here’s an example of how you might configure these keys in a GitLab CI/CD pipeline:

```yaml
stages:
  - deploy

deploy:
  stage: deploy
  script:
    - aws configure set aws_access_key_id $AWS_ACCESS_KEY_ID
    - aws configure set aws_secret_access_key $AWS_SECRET_ACCESS_KEY
    - aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin $AWS_ACCOUNT_ID.dkr.ecr.us-west-2.amazonaws.com
```

Ensure that `$AWS_ACCESS_KEY_ID` and `$AWS_SECRET_ACCESS_KEY` are securely stored as GitLab CI/CD variables.

**Q3. Why is it important to adhere to the principle of least privilege when assigning permissions to IAM users?**

Adhering to the principle of least privilege is crucial for maintaining a secure environment. By granting users only the permissions necessary to perform their job functions, you minimize the potential damage that could result from compromised credentials or malicious actions. If a user with excessive permissions is compromised, an attacker could potentially gain access to sensitive data or critical systems. By limiting permissions to the minimum required, you reduce the attack surface and mitigate the risk of unauthorized access.

For example, in a recent breach involving a misconfigured S3 bucket (CVE-2021-44228), an IAM user with overly broad permissions was able to upload and modify files in the bucket, leading to unauthorized data exposure. Adhering to least privilege principles would have restricted the user’s permissions to only those needed for their role, preventing such a breach.

**Q4. How do IAM groups help in managing permissions for multiple users?**

IAM groups are collections of IAM users that share common permissions. Instead of assigning permissions directly to each user, you can assign permissions to a group, and then add users to that group. This approach simplifies permission management, especially in large organizations where there might be hundreds of users.

For example, you can create a "Developer" group and assign policies that grant permissions to create EC2 instances and push to ECR repositories. Then, you can add all developers to this group. When a new developer joins the team, you simply add them to the "Developer" group, and they automatically inherit the group's permissions. Similarly, when a developer leaves the team, you can remove them from the group, and they lose access to the resources controlled by the group's policies.

This method ensures consistency in permission assignment and makes it easier to manage access control across a large number of users.

**Q5. What are the key differences between console login and programmatic access in AWS IAM?**

Console login and programmatic access are two distinct methods of accessing AWS resources, each serving different purposes.

- **Console Login**: This method involves logging into the AWS Management Console using a username and password. It is primarily intended for human users who need to interact with AWS services through the web interface. Console login provides a graphical interface for managing AWS resources and performing administrative tasks.

- **Programmatic Access**: This method involves using access keys (an access key ID and a secret access key) to authenticate API requests made to AWS services. Programmatic access is typically used by applications, scripts, and automation tools that need to interact with AWS services programmatically. It does not require a web interface and is suitable for non-human entities like CI/CD pipelines, servers, and other automated systems.

By separating these two types of access, AWS allows for better control and security. For instance, removing programmatic access keys from the root user reduces the risk of unauthorized access through stolen credentials, while ensuring that human users can still manage the account through the console.

---
<!-- nav -->
[[05-AWS Cloud Security & Access Management IAM Users, Groups, and Policies|AWS Cloud Security & Access Management IAM Users, Groups, and Policies]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/01-AWS Cloud Security & Access Management/IAM Users Groups Policies/00-Overview|Overview]]
