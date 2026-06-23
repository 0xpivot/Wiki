---
course: DevSecOps
topic: AWS Cloud Security & Access Management
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. How do you create a new IAM user in AWS with both console and programmatic access?**

To create a new IAM user in AWS with both console and programmatic access, follow these steps:

1. Go to the IAM dashboard in the AWS Management Console.
2. Click on "Users" and then "Add user."
3. Enter the username, e.g., `admin`.
4. Select "AWS Management Console access" and choose "Password" as the authentication type.
5. Set a custom password or let the user set their own password upon first login.
6. Optionally, uncheck "Require password reset on next sign-in."
7. Select "Programmatic access" to enable API access.
8. Click "Next: Permissions."
9. Choose "Attach existing policies directly."
10. Search for and select the appropriate policies, such as "AdministratorAccess" for full access.
11. Review the settings and click "Create user."

**Q2. Explain the difference between using IAM users and Identity Center for managing AWS users.**

IAM users are individual entities managed directly within the IAM service. They are suitable for small to medium-sized environments where centralized management across multiple AWS accounts is not required. IAM users can be assigned specific permissions and roles via policies.

Identity Center (formerly known as AWS Single Sign-On) is designed for large enterprises with multiple AWS accounts and services. It centralizes user management and access control across all AWS accounts and third-party SaaS applications. Identity Center requires AWS Organizations to manage multiple accounts, providing a unified view and control over user access.

**Q3. How would you ensure that a newly created IAM user has multi-factor authentication (MFA) enabled?**

To ensure that a newly created IAM user has MFA enabled, follow these steps:

1. After creating the IAM user, navigate to the IAM dashboard.
2. Locate the user and click on their name.
3. Under the "Security credentials" tab, click on "Assign MFA device."
4. Follow the prompts to configure MFA, either using a virtual MFA app (like Google Authenticator) or a hardware token.
5. Verify the MFA setup by entering the generated code from the MFA device.

**Q4. Describe how to create an IAM user for a CI/CD pipeline with restricted access to specific AWS services.**

To create an IAM user for a CI/CD pipeline with restricted access to specific AWS services, follow these steps:

1. Go to the IAM dashboard and click on "Users" and then "Add user."
2. Enter the username, e.g., `gitlab-user`.
3. Select "Programmatic access" to enable API access.
4. Click "Next: Permissions."
5. Choose "Attach existing policies directly."
6. Search for and select the appropriate policies for the services the pipeline needs access to, such as "AmazonEC2ContainerRegistryReadOnly" for ECR.
7. Review the settings and click "Create user."
8. Download the access key and secret key for the user.
9. Replace the root user’s access keys in the CI/CD pipeline configuration with the new access keys.

**Q5. What are some best practices for securing IAM users and their access keys in a CI/CD pipeline?**

Some best practices for securing IAM users and their access keys in a CI/CD pipeline include:

1. **Least Privilege Principle**: Grant IAM users only the permissions necessary to perform their tasks.
2. **Use IAM Roles Instead of Users**: For services like EC2, use IAM roles instead of users to avoid hardcoding access keys.
3. **Enable MFA**: Require MFA for all IAM users, including those used in CI/CD pipelines.
4. **Rotate Access Keys Regularly**: Schedule regular rotation of access keys to minimize exposure.
5. **Monitor Usage**: Use AWS CloudTrail to monitor API calls made by IAM users and detect unauthorized activity.
6. **Use Secrets Management Tools**: Store access keys securely using tools like AWS Secrets Manager or HashiCorp Vault.
7. **Limit Long-Term Credentials**: Avoid using long-term credentials in CI/CD pipelines; use temporary credentials when possible.

**Q6. How can you use the IAM credential report to audit and manage IAM users' security settings?**

The IAM credential report can be used to audit and manage IAM users' security settings by following these steps:

1. Generate the IAM credential report by navigating to the IAM dashboard and clicking on "Credential Report."
2. Download the report, which contains metadata about IAM users’ credentials, such as password age, MFA status, and access key usage.
3. Analyze the report to identify users who lack MFA, have weak passwords, or have unused access keys.
4. Take corrective actions, such as enabling MFA, enforcing stronger password policies, and rotating or deleting unused access keys.
5. Regularly review the credential report to maintain compliance with security best practices.

**Q7. Why is it important to separate human IAM users from system IAM users in a CI/CD pipeline?**

Separating human IAM users from system IAM users in a CI/CD pipeline is important for several reasons:

1. **Least Privilege Principle**: Human users typically require broader permissions for administrative tasks, while system users need only the minimal permissions required to perform their automated tasks.
2. **Auditability**: Separation allows for clearer auditing and tracking of actions performed by humans versus automated systems.
3. **Security Isolation**: If a system user’s credentials are compromised, the damage is limited to the specific permissions granted to that user, rather than potentially granting access to the entire AWS environment.
4. **Compliance**: Many compliance standards require strict separation of duties and least privilege access, which is easier to achieve with distinct IAM users for humans and systems.

**Q8. How would you troubleshoot an issue where a CI/CD pipeline fails due to incorrect AWS access keys?**

To troubleshoot an issue where a CI/CD pipeline fails due to incorrect AWS access keys, follow these steps:

1. **Verify Access Key Configuration**: Ensure that the correct access key and secret key are configured in the CI/CD pipeline settings.
2. **Check Key Rotation**: Confirm that the access keys have not expired or been rotated recently without updating the pipeline configuration.
3. **Review IAM User Policies**: Check the IAM user policies to ensure they grant sufficient permissions for the pipeline’s operations.
4. **Test Credentials Independently**: Use the AWS CLI or SDK to manually test the access keys outside of the pipeline to confirm they work correctly.
5. **Check for Errors in Logs**: Examine the pipeline logs for specific error messages related to AWS access, such as "AccessDenied" or "InvalidAccessKeyId."
6. **Update Credentials**: If the access keys are incorrect or expired, update them in the pipeline configuration and re-run the pipeline.

By following these steps, you can identify and resolve issues related to incorrect AWS access keys in a CI/CD pipeline.

---
<!-- nav -->
[[08-User Creation and Password Policies in AWS|User Creation and Password Policies in AWS]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/01-AWS Cloud Security & Access Management/Secure Access from CICD Pipeline to AWS/00-Overview|Overview]]
