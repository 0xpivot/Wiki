---
course: DevSecOps
topic: Secure Continuous Deployment & DAST
tags: [devsecops]
---

## Introduction to AWS Systems Manager (SSM)

AWS Systems Manager (SSM) is a powerful tool designed to help manage your Amazon Elastic Compute Cloud (EC2) instances more efficiently. It provides a suite of capabilities that enable you to automate tasks, maintain compliance, and troubleshoot issues across your infrastructure. One of the key components of SSM is the SSM Agent, which is installed on your EC2 instances to facilitate communication between AWS and your servers.

### What is the SSM Agent?

The SSM Agent is a lightweight daemon that runs on your EC2 instances. Its primary role is to receive and execute commands sent from the SSM service. These commands can range from simple tasks like installing software to complex operations such as patch management and configuration validation.

#### Why is the SSM Agent Important?

Without the SSM Agent, you would need to manually manage your EC2 instances, which can be time-consuming and error-prone. By leveraging the SSM Agent, you can automate many routine tasks, reducing the likelihood of human error and freeing up your time to focus on more strategic initiatives.

#### How Does the SSM Agent Work?

When you send a command to an EC2 instance via SSM, the following steps occur:

1. **Command Submission**: You submit a command through the AWS Management Console, AWS CLI, or SDKs.
2. **Authentication and Authorization**: AWS verifies your credentials and checks if you have the necessary permissions to execute the command.
3. **Command Forwarding**: Once authenticated, the command is forwarded to the SSM service.
4. **Agent Communication**: The SSM service communicates with the SSM Agent on the target EC2 instance.
5. **Command Execution**: The SSM Agent executes the command on the server.
6. **Response Transmission**: The results of the command execution are transmitted back to the SSM service and then to you.

### Example: Installing Docker Using SSM

Let's walk through an example of using SSM to install Docker on an EC2 instance.

#### Step-by-Step Process

1. **Submit Command**:
    ```bash
    aws ssm send-command --instance-ids i-1234567890abcdef0 --document-name "AWS-RunShellScript" --parameters commands="sudo apt-get update && sudo apt-get install -y docker.io"
    ```

2. **Authentication and Authorization**:
    - AWS verifies your credentials.
    - Checks if you have the necessary permissions to execute the command.

3. **Command Forwarding**:
    - The command is forwarded to the SSM service.

4. **Agent Communication**:
    - The SSM service contacts the SSM Agent on the EC2 instance.

5. **Command Execution**:
    - The SSM Agent runs the provided shell script on the server.

6. **Response Transmission**:
    - The results are transmitted back to the SSM service and then to you.

#### Full Raw HTTP Response

```http
HTTP/1.1 200 OK
Content-Type: application/json
Date: Mon, 01 Jan 2024 12:00:00 GMT
Content-Length: 1234

{
  "Command": {
    "CommandId": "d-1234567890abcdef0",
    "DocumentName": "AWS-RunShellScript",
    "Parameters": {
      "commands": [
        "sudo apt-get update && sudo apt-get install -y docker.io"
      ]
    },
    "Status": "Success",
    "StandardOutputContent": "Docker was successfully installed on the server.",
    "StandardErrorContent": ""
  }
}
```

### Session Manager: Secure Access Without SSH

Session Manager is a feature of SSM that allows you to securely access your EC2 instances without needing to open an SSH port. This is particularly useful in environments where you want to minimize the attack surface.

#### How Session Manager Works

1. **Connect Options**: In the AWS Management Console, you can choose different connect options for your EC2 instance, including SSH client, Instance Connect, and Session Manager.
2. **Browser-Based Shell**: Session Manager provides a browser-based shell with a user interface, making it easy to access your instances from anywhere.
3. **CLI Version**: Behind the scenes, the AWS CLI version of Session Manager is used to establish the connection.

#### Example: Using Session Manager

To use Session Manager, you can either use the browser-based shell or the AWS CLI.

##### Browser-Based Shell

1. **Navigate to EC2 Instance**: Go to the EC2 dashboard in the AWS Management Console.
2. **Select Instance**: Choose the instance you want to connect to.
3. **Click Connect**: Click on the "Connect" button.
4. **Choose Session Manager**: Select "Session Manager" from the list of connect options.

##### AWS CLI Version

```bash
aws ssm start-session --target i-1234567890abcdef0
```

#### Full Raw HTTP Response

```http
HTTP/1.1 200 OK
Content-Type: application/json
Date: Mon, 01 Jan 2024 12:00:00 GMT
Content-Length: 1234

{
  "SessionId": "sess-1234567890abcdef0",
  "Target": "i-1234567890abcdef0",
  "Status": "Active",
  "StartDateTime": "2024-01-01T12:00:00Z",
  "EndDateTime": null
}
```

### Pitfalls and Common Mistakes

1. **Incorrect Permissions**: Ensure that you have the necessary permissions to execute commands on your EC2 instances.
2. **Missing SSM Agent**: Make sure the SSM Agent is installed on your EC2 instances. Without it, commands will fail.
3. **Network Issues**: Ensure that your EC2 instances can communicate with the SSM service. Network restrictions can cause issues.

### How to Prevent / Defend

#### Detection

- **Monitor Logs**: Regularly monitor the logs generated by the SSM service to detect any unauthorized access attempts.
- **Audit Trails**: Enable audit trails to track who executed which commands and when.

#### Prevention

- **IAM Policies**: Use IAM policies to restrict access to the SSM service. Only grant permissions to trusted users.
- **Security Groups**: Configure security groups to allow traffic only from trusted sources.

#### Secure Coding Fixes

**Vulnerable Code**

```python
import boto3

ssm_client = boto3.client('ssm')
response = ssm_client.send_command(
    InstanceIds=['i-1234567890abcdef0'],
    DocumentName='AWS-RunShellScript',
    Parameters={
        'commands': ['sudo apt-get update && sudo apt-get install -y docker.io']
    }
)
print(response)
```

**Secure Code**

```python
import boto3

# Create a session with restricted permissions
session = boto3.Session(
    aws_access_key_id='YOUR_ACCESS_KEY',
    aws_secret_access_key='YOUR_SECRET_KEY',
    region_name='us-west-2'
)

ssm_client = session.client('ssm')
response = ssm_client.send_command(
    InstanceIds=['i-1234567890abcdef0'],
    DocumentName='AWS-RunShellScript',
    Parameters={
        'commands': ['sudo apt-get update && sudo apt-get install -y docker.io']
    }
)
print(response)
```

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2023-XXXX**: A vulnerability was discovered in the SSM Agent that allowed attackers to execute arbitrary commands on EC2 instances. This was mitigated by updating the SSM Agent to the latest version.
- **Breaches**: Several organizations were breached due to misconfigured IAM policies that granted excessive permissions to the SSM service. Ensuring proper IAM policies and regular audits can prevent such incidents.

### Practice Labs

For hands-on practice with AWS Systems Manager, consider the following labs:

- **CloudGoat**: A cloud security training platform that includes exercises on configuring and securing AWS services, including SSM.
- **flaws.cloud**: A cloud security training environment that provides scenarios for practicing secure deployment and management of EC2 instances using SSM.

By thoroughly understanding and implementing the concepts covered in this chapter, you can effectively manage your EC2 instances using AWS Systems Manager, ensuring both efficiency and security.

### Conclusion

AWS Systems Manager, with its SSM Agent and Session Manager features, provides a robust framework for managing your EC2 instances. By leveraging these tools, you can automate routine tasks, ensure compliance, and secure your infrastructure. Always remember to follow best practices for detection, prevention, and secure coding to protect your environment from potential threats.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/Configure AWS Systems Manager for EC2 Server/01-Introduction to AWS Systems Manager (SSM) Part 1|Introduction to AWS Systems Manager (SSM) Part 1]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/Configure AWS Systems Manager for EC2 Server/00-Overview|Overview]] | [[03-Introduction to AWS Systems Manager and EC2 Integration Part 1|Introduction to AWS Systems Manager and EC2 Integration Part 1]]
