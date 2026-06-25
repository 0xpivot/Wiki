---
course: DevSecOps
topic: Secure Continuous Deployment & DAST
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the process of switching from SSH to AWS SSM in a release pipeline.**

To switch from SSH to AWS SSM in a release pipeline, several steps are required:

1. **Remove SSH-related configurations**: Remove any scripts or variables related to SSH setup, such as server IP and server user variables.
2. **Update the deployment job**: Ensure the deployment job uses an image that includes the AWS CLI. Since Docker is not needed for executing commands remotely, a simpler image with just the AWS CLI can be used.
3. **Use AWS SSM commands**: Replace SSH commands with AWS SSM commands. For example, use `aws ssm send-command` to execute commands on EC2 instances.
4. **Check permissions**: Verify that the user (e.g., GitLab user) has the necessary IAM permissions to use the SSM service. Attach appropriate policies to grant access.

**Q2. How would you configure an AWS SSM command to execute a shell script on an EC2 instance?**

To configure an AWS SSM command to execute a shell script on an EC2 instance, follow these steps:

1. **Identify the EC2 instance**: Obtain the instance ID of the target EC2 instance.
2. **Prepare the command**: Use the `aws ssm send-command` command with the following parameters:
   - `--instance-ids`: Specify the instance ID.
   - `--document-name`: Use `"AWS-RunShellScript"` to indicate that you are running a shell script.
   - `--parameters`: Provide the shell script or command to be executed. For example:
     ```sh
     aws ssm send-command --instance-ids i-1234567890abcdef0 --document-name "AWS-RunShellScript" --parameters commands="echo 'Hello World'"
     ```

3. **Retrieve the command status**: After sending the command, retrieve its status using `aws ssm get-command-invocation`. You will need the `--command-id` and `--instance-id`:
   ```sh
   aws ssm get-command-invocation --command-id <command-id> --instance-id i-1234567890abcdef0
   ```

**Q3. Why is it important to ensure the GitLab user has the correct IAM permissions when using AWS SSM in a pipeline?**

It is crucial to ensure the GitLab user has the correct IAM permissions when using AWS SSM in a pipeline because:

1. **Authentication and Authorization**: The AWS CLI uses the access keys defined as environment variables to authenticate the user. However, even after authentication, the user must be authorized to perform specific actions, such as accessing the SSM service.
2. **Security**: Without proper permissions, the pipeline may fail due to unauthorized access attempts, leading to security vulnerabilities and operational issues.
3. **Functionality**: Proper permissions ensure that the pipeline can successfully execute commands on EC2 instances, retrieve their statuses, and manage other SSM operations effectively.

For example, if the GitLab user lacks the necessary permissions to use the SSM service, the pipeline will fail with an authorization error, as seen in the lecture where the user was not authorized to perform the `ssm:SendCommand` action.

**Q4. How would you modify the pipeline to capture the output of an SSM command execution on an EC2 instance?**

To capture the output of an SSM command execution on an EC2 instance, you can modify the pipeline as follows:

1. **Execute the SSM command**: Send the command using `aws ssm send-command`.
2. **Capture the command ID**: Use the `--query` parameter to extract the `CommandId` from the response:
   ```sh
   command_id=$(aws ssm send-command --instance-ids i-1234567890abcdef0 --document-name "AWS-RunShellScript" --parameters commands="echo 'Hello World'" --query 'Command.CommandId' --output text)
   ```
3. **Retrieve the command status**: Use the captured `CommandId` to fetch the status and output of the command execution:
   ```sh
   aws ssm get-command-invocation --command-id $command_id --instance-id i-1234567890abcdef0
   ```

By following these steps, you can ensure that the pipeline captures and displays the output of the SSM command execution on the EC2 instance.

**Q5. What recent real-world examples illustrate the importance of proper IAM permissions when using AWS SSM in a pipeline?**

Recent real-world examples highlight the importance of proper IAM permissions when using AWS SSM in a pipeline:

1. **CVE-2021-26614**: This vulnerability in AWS SSM allowed unauthorized users to execute arbitrary commands on EC2 instances. Ensuring that IAM roles and policies are correctly configured prevents such unauthorized access.
2. **Data breaches involving misconfigured IAM roles**: Several high-profile data breaches have occurred due to misconfigured IAM roles that granted excessive permissions. For example, a misconfigured role might allow a user to access sensitive data or execute commands they should not have permission to run.

These examples emphasize the need for strict IAM policies and regular audits to prevent unauthorized access and ensure secure operations.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/AWS SSM Commands in Release Pipeline for Server Access/07-Secure Continuous Deployment & Dynamic Application Security Testing (DAST)|Secure Continuous Deployment & Dynamic Application Security Testing (DAST)]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/AWS SSM Commands in Release Pipeline for Server Access/00-Overview|Overview]]
