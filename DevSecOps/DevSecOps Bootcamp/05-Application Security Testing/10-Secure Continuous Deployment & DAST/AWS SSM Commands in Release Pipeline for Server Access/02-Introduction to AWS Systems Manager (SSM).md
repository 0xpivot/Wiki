---
course: DevSecOps
topic: Secure Continuous Deployment & DAST
tags: [devsecops]
---

## Introduction to AWS Systems Manager (SSM)

AWS Systems Manager (SSM) is a powerful tool designed to help manage your Amazon Elastic Compute Cloud (EC2) instances and other AWS resources efficiently. It provides a suite of capabilities that enable you to automate tasks, maintain compliance, and troubleshoot issues across your infrastructure. One of the key features of SSM is the ability to execute commands remotely on your EC2 instances using the `send-command` feature.

### What is SSM?

SSM is a collection of tools that help you manage your AWS resources more effectively. It includes:

- **Session Manager**: A feature that allows you to establish a secure connection to your EC2 instances without needing to open up inbound ports or manage SSH keys.
- **Run Command**: A feature that enables you to run commands on multiple instances simultaneously.
- **State Manager**: A feature that allows you to configure and maintain the desired state of your instances.
- **Inventory**: A feature that provides visibility into the configuration details of your instances.

### Why Use SSM?

Using SSM offers several benefits:

- **Security**: SSM uses IAM roles and permissions to control access, ensuring that only authorized users can execute commands.
- **Efficiency**: You can manage multiple instances simultaneously, reducing the time and effort required to perform routine tasks.
- **Automation**: SSM integrates with other AWS services like CloudWatch Events and Lambda, enabling you to automate complex workflows.

### How Does SSM Work?

SSM operates by leveraging the AWS Agent, which is installed on your EC2 instances. This agent communicates with the SSM service to receive and execute commands. The communication between the agent and the service is encrypted and authenticated, ensuring secure execution.

### Example Scenario: Executing a Command Using SSM

Let's walk through an example of executing a command on an EC2 instance using SSM. We'll start by identifying the instance ID and then use the `send-command` feature to execute a command.

#### Step 1: Identify the Instance ID

The first step is to identify the instance ID of the EC2 instance you want to target. You can find this information in the EC2 dashboard within the AWS Management Console.

```markdown
Instance ID: i-0123456789abcdef0
```

#### Step 2: Execute the Command Using SSM

Once you have the instance ID, you can use the `aws ssm send-command` command to execute a command on the instance. Here’s an example of how to do this:

```bash
aws ssm send-command \
    --instance-ids i-0123456789abcdef0 \
    --document-name "AWS-RunShellScript" \
    --parameters '{"commands":["echo Hello World"]}'
```

This command sends a shell script to the specified instance and executes it. The output of the command will be available in the SSM console.

### Full HTTP Request and Response

Here’s a detailed breakdown of the HTTP request and response involved in executing the `send-command` operation:

```http
POST / HTTP/1.1
Host: ssm.us-west-2.amazonaws.com
Content-Type: application/x-amz-json-1.1
X-Amz-Target: AmazonSSM.SendCommand
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20191102/us-west-2/ssm/aws4_request, SignedHeaders=content-type;host;x-amz-date;x-amz-target, Signature=fe5f356c9d0bb846b6e4991ba50390ce95b41c6f95f9a4c9b9e4bfcf4c4530ff
X-Amz-Date: 20191102T194523Z
Content-Length: 179

{
    "DocumentName": "AWS-RunShellScript",
    "InstanceIds": ["i-0123456789abcdef0"],
    "Parameters": {
        "commands": ["echo Hello World"]
    }
}
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: application/x-amz-json-1.1
Content-Length: 134

{
    "Command": {
        "CommandId": "d-1234567890abcdef0",
        "DocumentName": "AWS-RunShellScript",
        "InstanceIds": ["i-0123456789abcdef0"],
        "Parameters": {
            "commands": ["echo Hello World"]
        },
        "Status": "InProgress"
    }
}
```

### Diagram: SSM Command Execution Flow

```mermaid
sequenceDiagram
    participant User
    participant SSM
    participant EC2
    User->>SSM: Send Command Request
    SSM->>EC2: Execute Command
    EC2-->>SSM: Command Output
    SSM-->>User: Command Status
```

### Pitfalls and Common Mistakes

When using SSM, there are several common pitfalls to avoid:

- **Incorrect Permissions**: Ensure that the IAM role attached to your EC2 instance has the necessary permissions to execute SSM commands.
- **Agent Installation**: Make sure the SSM Agent is installed and running on your EC2 instances.
- **Network Configuration**: Ensure that your instances can communicate with the SSM endpoint.

### How to Prevent / Defend

#### Detection

To detect unauthorized use of SSM, you can monitor CloudTrail logs for `SendCommand` API calls. Set up alerts for any suspicious activity.

#### Prevention

- **IAM Policies**: Use IAM policies to restrict access to SSM commands.
- **Network Isolation**: Use VPC endpoints to isolate SSM traffic.
- **Audit Logs**: Regularly review CloudTrail logs to ensure compliance.

#### Secure Coding Fixes

Here’s an example of how to securely configure IAM policies to restrict SSM access:

**Vulnerable Policy:**

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "ssm:*",
            "Resource": "*"
        }
    ]
}
```

**Secure Policy:**

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "ssm:DescribeInstances",
                "ssm:SendCommand"
            ],
            "Resource": "arn:aws:ssm:us-west-2:123456789012:managed-instance/*"
        }
    ]
}
```

### Real-World Examples

#### Recent CVEs and Breaches

One notable example is the exploitation of misconfigured IAM roles, leading to unauthorized access to SSM commands. For instance, in a breach involving a misconfigured IAM role, attackers were able to execute arbitrary commands on EC2 instances, leading to data exfiltration.

### Practice Labs

For hands-on practice with SSM, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a module on AWS security, including SSM.
- **CloudGoat**: Provides scenarios for practicing cloud security, including SSM usage.
- **AWS Official Workshops**: Includes labs on managing EC2 instances with SSM.

By mastering the use of SSM, you can significantly enhance the security and efficiency of your DevSecOps pipeline.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/AWS SSM Commands in Release Pipeline for Server Access/01-Introduction to AWS Systems Manager (SSM) Part 1|Introduction to AWS Systems Manager (SSM) Part 1]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/AWS SSM Commands in Release Pipeline for Server Access/00-Overview|Overview]] | [[03-Introduction to Secure Continuous Deployment and Dynamic Application Security Testing (DAST) Part 1|Introduction to Secure Continuous Deployment and Dynamic Application Security Testing (DAST) Part 1]]
