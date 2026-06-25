---
course: DevSecOps
topic: Secure Continuous Deployment & DAST
tags: [devsecops]
---

## Secure Continuous Deployment to Server Using AWS Systems Manager (SSM)

### Introduction to AWS Systems Manager (SSM)

AWS Systems Manager (SSM) is a powerful service that helps you automate management tasks such as patching, configuration management, and operational tasks across your Amazon Elastic Compute Cloud (EC2) instances. One of the key features of SSM is its ability to manage and execute commands on EC2 instances in a controlled manner. This includes the `wait` command, which allows you to synchronize the execution of commands in a continuous deployment pipeline.

### Understanding the `wait` Command in SSM

The `wait` command in SSM is designed to ensure that subsequent commands are executed only after the previous command has completed successfully. This is particularly useful in continuous deployment scenarios where you want to ensure that each step in the deployment process is completed before moving on to the next.

#### Purpose of the `wait` Command

The primary purpose of the `wait` command is to avoid the need for arbitrary `sleep` commands, which can introduce delays and inefficiencies into your deployment process. By waiting for the actual completion of the previous command, you can achieve a more precise and efficient deployment workflow.

#### How the `wait` Command Works

When you use the `wait` command, you specify a command ID and an instance ID. The command ID is the unique identifier for the command you want to wait on, and the instance ID is the identifier for the EC2 instance on which the command is being executed.

Here’s a step-by-step breakdown of how the `wait` command works:

1. **Command Execution**: You first execute a command on an EC2 instance using SSM.
2. **Command ID**: The command execution returns a unique command ID.
3. **Wait Command**: You then use the `wait` command, specifying the command ID and instance ID.
4. **Completion Check**: The `wait` command checks the status of the specified command until it completes successfully.
5. **Next Command**: Once the previous command is completed, the `wait` command returns control to the next command in the pipeline.

### Example Usage of the `wait` Command

Let’s walk through a complete example of using the `wait` command in an SSM-based continuous deployment scenario.

#### Step 1: Execute a Command

First, you need to execute a command on an EC2 instance. For example, you might want to run a script to update the application on the server.

```sh
aws ssm send-command \
    --instance-ids i-1234567890abcdef0 \
    --document-name "AWS-RunShellScript" \
    --parameters '{"commands":["sudo apt-get update && sudo apt-get upgrade -y"]}'
```

This command updates the package list and upgrades all installed packages on the specified EC2 instance.

#### Step 2: Capture the Command ID

After executing the command, you will receive a response containing the command ID. You need to capture this ID for the `wait` command.

```json
{
    "Command": {
        "CommandId": "12345678-1234-1234-1234-1234567890ab",
        "DocumentName": "AWS-RunShellScript",
        "InstanceIds": [
            "i-11111111111111111"
        ],
        "Parameters": {
            "commands": [
                "sudo apt-get update && sudo apt-get upgrade -y"
            ]
        },
        "Status": "InProgress",
        "StatusDetails": "Executing"
    }
}
```

#### Step 3: Use the `wait` Command

Now, you can use the `wait` command to wait for the previous command to complete.

```sh
aws ssm wait command-executed \
    --command-id 12345678-1234-1234-1234-1234567890ab \
    --instance-id i-1234567890abcdef0
```

This command waits until the command with the specified ID (`12345678-1234-1234-1234-1234567890ab`) is executed on the specified instance (`i-1234567890abcdef0`).

#### Step 4: Verify Completion

Once the `wait` command completes, you can verify that the previous command has been executed successfully.

```sh
aws ssm list-command-invocations \
    --command-id 12345678-1234-1234-1234-1234567890ab \
    --details
```

This command lists the details of the command execution, including the status and output.

### Comparison with `sleep` Command

Using the `wait` command is generally more precise and efficient than using a `sleep` command. Here’s a comparison:

#### `sleep` Command

The `sleep` command introduces a fixed delay in your deployment process. For example:

```sh
sleep 60
```

This command pauses the execution for 60 seconds, regardless of whether the previous command has completed. This can lead to inefficiencies and potential failures if the previous command takes longer than expected.

#### `wait` Command

The `wait` command waits for the actual completion of the previous command, ensuring that subsequent steps are executed only when necessary. This avoids unnecessary delays and ensures that your deployment process is as efficient as possible.

### Real-World Examples and Recent Breaches

Recent breaches and vulnerabilities often highlight the importance of precise and efficient deployment processes. For example, the Log4j vulnerability (CVE-2021-44228) affected numerous systems due to delayed updates and inefficient deployment processes. Using tools like SSM with the `wait` command can help ensure that critical updates are applied promptly and correctly.

### Pitfalls and Common Mistakes

While the `wait` command is powerful, there are several pitfalls and common mistakes to be aware of:

1. **Incorrect Command ID**: Ensure that you are using the correct command ID. Using an incorrect ID can result in the `wait` command failing to synchronize properly.
2. **Instance ID Mismatch**: Make sure that the instance ID used in the `wait` command matches the instance on which the command was executed.
3. **Timeouts**: The `wait` command can timeout if the previous command does not complete within a reasonable time frame. Ensure that your deployment process is optimized to minimize such timeouts.

### How to Prevent / Defend

To ensure the secure and efficient use of the `wait` command in your continuous deployment process, follow these best practices:

#### Detection

1. **Monitor Command Status**: Regularly monitor the status of commands executed via SSM to ensure they are completing as expected.
2. **Logging and Auditing**: Enable detailed logging and auditing for SSM commands to track their execution and identify any issues.

#### Prevention

1. **Use IAM Policies**: Restrict access to SSM commands using IAM policies to ensure that only authorized users can execute commands.
2. **Secure Configuration Management**: Use secure configuration management practices to ensure that sensitive information is not exposed during command execution.

#### Secure Coding Fixes

Here’s an example of how to securely implement the `wait` command in a deployment script:

**Vulnerable Code:**

```sh
# Vulnerable code
aws ssm send-command \
    --instance-ids i-1234567890abcdef0 \
    --document-name "AWS-RunShellScript" \
    --parameters '{"commands":["sudo apt-get update && sudo apt-get upgrade -y"]}'

sleep 60
```

**Secure Code:**

```sh
# Secure code
aws ssm send-command \
    --instance-ids i-1234567890abcdef0 \
    --document-name "AWS-RunShellScript" \
    --parameters '{"commands":["sudo apt-get update && sudo apt-get upgrade -y"]}' > command_output.json

command_id=$(jq -r '.Command.CommandId' command_output.json)
instance_id="i-1234567890abcdef0"

aws ssm wait command-executed \
    --command-id "$command_id" \
    --instance-id "$instance_id"
```

In the secure code, we capture the command ID and use it in the `wait` command to ensure precise synchronization.

### Conclusion

Using the `wait` command in AWS Systems Manager (SSM) is a powerful way to ensure precise and efficient synchronization in your continuous deployment process. By avoiding arbitrary delays and ensuring that each step is completed before moving on, you can improve the reliability and security of your deployments. Always follow best practices for detection, prevention, and secure coding to ensure that your deployment process is robust and secure.

### Practice Labs

For hands-on practice with AWS SSM and continuous deployment, consider the following labs:

- **PortSwigger Web Security Academy**: Offers practical exercises in web application security, including integration with AWS services.
- **CloudGoat**: Provides a series of labs focused on securing AWS environments, including the use of SSM for secure deployment.
- **AWS Official Workshops**: Includes detailed workshops on using AWS services, including SSM, for secure and efficient deployment processes.

These labs will help you gain practical experience in implementing secure continuous deployment using AWS SSM.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/Secure Continuous Deployment to Server using SSM/00-Overview|Overview]] | [[02-Secure Continuous Deployment to Server Using SSM Part 1|Secure Continuous Deployment to Server Using SSM Part 1]]
