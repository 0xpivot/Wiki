---
course: DevSecOps
topic: Secure Continuous Deployment & DAST
tags: [devsecops]
---

## Secure Continuous Deployment to Server Using SSM

### Introduction to Secure Continuous Deployment

Secure Continuous Deployment (SCD) is a practice that combines continuous integration and continuous delivery (CI/CD) with security best practices to ensure that applications are deployed securely and efficiently. One of the key components of SCD is the ability to execute commands remotely on servers in a secure manner. In this context, AWS Systems Manager (SSM) provides a robust solution for managing and executing commands on EC2 instances.

### What is AWS Systems Manager (SSM)?

AWS Systems Manager (SSM) is a service that helps you manage your Amazon Elastic Compute Cloud (EC2) instances at scale. It enables you to automate tasks such as patch management, configuration management, and operational tasks like command execution. SSM provides a secure way to run commands on your EC2 instances without needing direct access via SSH.

#### Why Use SSM for Command Execution?

Using SSM for command execution offers several advantages over traditional methods like SSH:

1. **Security**: SSM uses IAM roles and permissions to control access, ensuring that only authorized users can execute commands.
2. **Auditability**: Every command executed through SSM is logged, providing a detailed audit trail.
3. **Scalability**: SSM allows you to execute commands across multiple instances simultaneously.
4. **Ease of Use**: SSM integrates seamlessly with other AWS services, making it easier to manage your infrastructure.

### Configuring SSM for Remote Command Execution

To configure SSM for remote command execution, you need to set up an SSM document and specify the commands you want to run. Here’s a step-by-step guide to setting this up:

#### Step 1: Create an SSM Document

An SSM document defines the actions to be performed on your EC2 instances. You can create a new SSM document using the AWS Management Console or the AWS CLI.

```bash
aws ssm create-document --name "MyCommandDocument" --content '{
  "schemaVersion": "2.2",
  "description": "Run a series of commands on EC2 instances",
  "parameters": {
    "commands": {
      "type": "StringList",
      "description": "List of commands to execute"
    }
  },
  "mainSteps": [
    {
      "action": "aws:runShellScript",
      "name": "runCommands",
      "inputs": {
        "runCommand": "{{ commands }}"
      }
    }
  ]
}'
```

This creates an SSM document named `MyCommandDocument` that accepts a list of shell commands to execute.

#### Step 2: Execute Commands Using SSM

Once the document is created, you can execute commands on your EC2 instances using the `send-command` API.

```bash
aws ssm send-command \
  --document-name "MyCommandDocument" \
  --instance-ids "i-0123456789abcdef0" \
  --parameters '{"commands":["echo Hello World", "ls -l"]}'
```

This command sends the specified commands to the EC2 instance with the given ID.

### Handling Command Invocation Status

When you execute commands using SSM, the commands may take some time to complete. To handle this, you need to check the command invocation status.

```bash
aws ssm list-command-invocations --command-id <command-id>
```

This command lists the status of the command invocations. The status can be `InProgress`, `Success`, or `Failed`.

### Example: Full Command Execution Flow

Let’s walk through a complete example of configuring and executing commands using SSM.

#### Step 1: Create the SSM Document

```bash
aws ssm create-document --name "MyCommandDocument" --content '{
  "schemaVersion": "2.2",
  "description": "Run a series of commands on EC2 instances",
  "parameters": {
    "commands": {
      "type": "StringList",
      "description": "List of commands to execute"
    }
  },
  "mainSteps": [
    {
      "action": "aws:runShellScript",
      "name": "runCommands",
      "inputs": {
        "runCommand": "{{ commands }}"
      }
    }
  ]
}'
```

#### Step 2: Send the Command

```bash
aws ssm send-command \
  --document-name "MyCommandDocument" \
  --instance-ids "i-0123456789abcdef0" \
  --parameters '{"commands":["echo Hello World", "ls -l"]}'
```

#### Step 3: Check Command Status

```bash
aws ssm list-command-invocations --command-id <command-id>
```

### Handling Variables in Commands

When executing commands, you might need to pass variables that should be interpreted correctly. This can be achieved by using double quotes around the variables.

```bash
aws ssm send-command \
  --document-name "MyCommandDocument" \
  --instance-ids "i-0123456789abcdef0" \
  --parameters '{"commands":["echo \"Hello $USER\""]}'
```

### Real-World Examples and Recent Breaches

Recent breaches have highlighted the importance of secure command execution. For example, the SolarWinds breach involved attackers gaining access to systems and executing malicious commands. Using SSM can help mitigate such risks by providing a secure and auditable method for command execution.

### How to Prevent / Defend

#### Detection

To detect unauthorized command execution, you can monitor SSM logs and set up alerts for suspicious activities. AWS CloudTrail can be used to log all API calls made to SSM.

```bash
aws cloudtrail lookup-events --lookup-attributes '{"AttributeKey":"EventName","AttributeValue":"SendCommand"}'
```

#### Prevention

1. **IAM Roles and Permissions**: Ensure that only authorized users have the necessary IAM roles to execute commands.
2. **Audit Logs**: Enable logging for SSM to track all command executions.
3. **Secure Coding Practices**: Use secure coding practices to avoid injecting malicious commands.

#### Secure Code Fix

**Vulnerable Code:**

```bash
aws ssm send-command \
  --document-name "MyCommandDocument" \
  --instance-ids "i-0123456789abcdef0" \
  --parameters '{"commands":["echo Hello $USER"]}'
```

**Fixed Code:**

```bash
aws ssm send-command \
  --document-name "MyCommandDocument" \
  --instance-ids "i-0123456789abcdef0" \
  --parameters '{"commands":["echo \"Hello $USER\""]}'
```

### Conclusion

Using AWS Systems Manager (SSM) for secure continuous deployment provides a robust and secure method for executing commands on EC2 instances. By following the steps outlined above, you can ensure that your deployments are both efficient and secure.

### Practice Labs

For hands-on experience with SSM and secure continuous deployment, consider the following labs:

- **PortSwigger Web Security Academy**: Offers practical exercises on securing web applications.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **CloudGoat**: Provides scenarios for learning AWS security best practices.

These labs will help you gain practical experience in implementing secure continuous deployment practices using SSM.

---
<!-- nav -->
[[02-Secure Continuous Deployment to Server Using SSM Part 1|Secure Continuous Deployment to Server Using SSM Part 1]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/Secure Continuous Deployment to Server using SSM/00-Overview|Overview]] | [[04-Secure Continuous Deployment to Server Using SSM Part 3|Secure Continuous Deployment to Server Using SSM Part 3]]
