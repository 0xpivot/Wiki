---
course: DevSecOps
topic: Secure Continuous Deployment & DAST
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the purpose of AWS Systems Manager (SSM) and how it differs from traditional SSH access.**

AWS Systems Manager (SSM) is a service designed to help users manage their AWS resources at scale. It provides a unified console for managing multiple resources, including EC2 instances, and allows for automated operations such as patch management, software inventory, and operational tasks. Unlike traditional SSH access, which requires direct network access to the server, SSM operates over the AWS infrastructure, providing a more secure method of executing commands and managing instances. SSM uses the AWS authentication mechanisms, ensuring that only authorized users can perform actions, and it does not require opening ports like SSH.

**Q2. How do you ensure that an EC2 instance is configured to work with AWS SSM? List the steps involved.**

To configure an EC2 instance to work with AWS SSM, follow these steps:

1. **Install the SSM Agent**: Ensure that the SSM agent is installed and running on the EC2 instance. Most AWS-provided AMIs come with the SSM agent pre-installed and running.
   
   ```bash
   sudo systemctl status amazon-ssm-agent
   ```

2. **Assign an IAM Role**: Assign an IAM role to the EC2 instance that has the necessary permissions to interact with SSM. Create an IAM role with the `AmazonSSMManagedInstanceCore` policy and attach it to the EC2 instance.

   - Go to the IAM console.
   - Create a new role for EC2 instances.
   - Attach the `AmazonSSMManagedInstanceCore` policy to the role.
   - Attach the role to the EC2 instance via the EC2 console under the "Security" tab.

3. **Verify Connectivity**: Use the Session Manager in the EC2 console to verify that you can establish a session with the instance.

   - Select the instance in the EC2 console.
   - Click on the "Connect" button.
   - Choose "Session Manager" to start a session.

**Q3. What are the benefits of using AWS SSM over traditional SSH access for managing EC2 instances?**

Using AWS SSM over traditional SSH access offers several benefits:

1. **Enhanced Security**: SSM leverages AWS’s secure infrastructure, eliminating the need to open SSH ports and reducing the attack surface.
   
2. **Unified Management**: SSM provides a centralized console for managing multiple EC2 instances, simplifying operations and reducing administrative overhead.
   
3. **Automated Operations**: SSM supports automated tasks such as patch management, software inventory, and compliance checks, improving operational efficiency.
   
4. **Auditability**: All actions performed via SSM are logged, making it easier to audit and track changes to the environment.
   
5. **Multi-Factor Authentication**: SSM integrates with AWS Identity and Access Management (IAM), allowing for multi-factor authentication and fine-grained access control.

**Q4. How would you troubleshoot an issue where an EC2 instance is unable to establish a session with AWS SSM?**

To troubleshoot an issue where an EC2 instance cannot establish a session with AWS SSM, follow these steps:

1. **Check SSM Agent Status**: Verify that the SSM agent is installed and running on the EC2 instance.

   ```bash
   sudo systemctl status amazon-ssm-agent
   ```

2. **Review IAM Role Permissions**: Ensure that the EC2 instance has the correct IAM role attached with the `AmazonSSMManagedInstanceCore` policy.

   - Go to the IAM console.
   - Check the roles associated with the EC2 instance.
   - Verify the policy attached to the role.

3. **Network Configuration**: Ensure that the EC2 instance has outbound network access to the SSM endpoint.

   - Check the security group settings.
   - Ensure that the instance can reach the SSM endpoint IP addresses.

4. **Logs and Events**: Review CloudWatch logs and events for any errors or warnings related to SSM interactions.

   - Go to the CloudWatch console.
   - Check the logs and events for the EC2 instance.

**Q5. Describe a recent real-world example where AWS SSM played a crucial role in securing an environment.**

In the context of recent breaches, AWS SSM has played a crucial role in securing environments by providing a secure and controlled way to manage instances without exposing SSH ports. For example, during the SolarWinds breach, many organizations were compromised due to exposed SSH ports and weak authentication mechanisms. By using AWS SSM, organizations could have mitigated the risk of unauthorized access by leveraging the secure AWS infrastructure and IAM controls. Additionally, SSM’s ability to enforce compliance and perform automated security checks helped organizations maintain a secure posture against such threats.

---
<!-- nav -->
[[06-Understanding IAM Roles and Policies in AWS|Understanding IAM Roles and Policies in AWS]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/Configure AWS Systems Manager for EC2 Server/00-Overview|Overview]]
