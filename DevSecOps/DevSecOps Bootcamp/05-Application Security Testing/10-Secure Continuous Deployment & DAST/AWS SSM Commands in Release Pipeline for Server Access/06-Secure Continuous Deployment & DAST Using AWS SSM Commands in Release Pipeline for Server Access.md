---
course: DevSecOps
topic: Secure Continuous Deployment & DAST
tags: [devsecops]
---

## Secure Continuous Deployment & DAST Using AWS SSM Commands in Release Pipeline for Server Access

### Background Theory

In DevSecOps, continuous deployment (CD) is a critical practice that ensures code changes are automatically tested and deployed to production environments. This process often involves interacting with servers to start containers, run tests, and perform other operations. To securely manage these interactions, AWS Systems Manager (SSM) provides a suite of tools that can be integrated into your release pipeline.

AWS SSM allows you to remotely execute commands on managed instances using the `aws ssm send-command` API. This capability is particularly useful for starting containers on remote servers as part of your CD pipeline.

### Why Use AWS SSM?

Using AWS SSM for server access during continuous deployment offers several advantages:

1. **Security**: SSM uses IAM roles and permissions to control access, ensuring that only authorized users and services can execute commands.
2. **Automation**: SSM integrates seamlessly with other AWS services like Lambda and CloudWatch, enabling automated workflows.
3. **Logging and Auditing**: All commands executed via SSM are logged, providing an audit trail for compliance and troubleshooting purposes.
4. **Scalability**: SSM can handle large numbers of instances, making it suitable for distributed systems.

### How to Start a Container Using AWS SSM

To start a container on a server using AWS SSM, you need to follow these steps:

1. **Set Up Managed Instances**: Ensure that your servers are registered as managed instances in SSM.
2. **Configure IAM Roles**: Assign appropriate IAM roles to the instances to allow them to receive and execute SSM commands.
3. **Send Command**: Use the `aws ssm send-command` API to start the container.

#### Step-by-Step Mechanics

1. **Register Managed Instances**:
   - Register your EC2 instances with SSM using the AWS Management Console or the `aws ssm register-target-with-maintenance-window` command.
   
2. **Assign IAM Role**:
   - Create an IAM role with the necessary permissions to execute SSM commands.
   - Attach this role to your EC2 instances.

3. **Send Command**:
   - Use the `aws ssm send-command` API to execute a command on the instance.

Here’s a complete example:

```bash
# Define the instance ID and command
INSTANCE_ID="i-0123456789abcdef0"
COMMAND="docker run -d --name my-container my-image"

# Send the command to the instance
aws ssm send-command \
    --instance-ids $INSTANCE_ID \
    --document-name "AWS-RunShellScript" \
    --parameters commands="$COMMAND"
```

### Full HTTP Request and Response Example

When you send the command using the AWS CLI, it translates to an HTTP request to the AWS API. Here’s what the full HTTP request and response might look like:

```http
POST / HTTP/1.1
Host: ssm.us-west-2.amazonaws.com
Content-Type: application/x-amz-json-1.1
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20150101/us-west-2/ssm/aws4_request, SignedHeaders=content-type;host;x-amz-date, Signature=fe5f40b3c0f48c48e8d116f8c1fa2758e784c0f45c21d9c6c9e9a6faef108b7b
X-Amz-Date: 20150101T000000Z
Content-Length: 123

{
    "InstanceIds": ["i-0123456789abcdef0"],
    "DocumentName": "AWS-RunShellScript",
    "Parameters": {
        "commands": ["docker run -d --name my-container my-image"]
    }
}
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: application/x-amz-json-1.1
Content-Length: 123

{
    "Command": {
        "CommandId": "d-1234567890abcdef0",
        "DocumentName": "AWS-RunShellScript",
        "Parameters": {
            "commands": ["docker run -d --name my-container my-image"]
        },
        "InstanceIds": ["i-0123456789abcdef0"],
        "Status": "InProgress"
    }
}
```

### Mermaid Diagram: Command Execution Flow

A visual representation of the command execution flow can help understand the process better:

```mermaid
sequenceDiagram
    participant User
    participant AWSCLI
    participant SSM
    participant EC2Instance

    User->>AWSCLI: aws ssm send-command
    AWSCLI->>SSM: POST /send-command
    SSM-->>EC2Instance: Execute command
    EC2Instance-->>SSM: Command status
    SSM-->>AWSCLI: Command response
    AWSCLI-->>User: Command output
```

### Real-World Examples and Recent CVEs

Recent breaches and vulnerabilities have highlighted the importance of securing server access and command execution:

- **CVE-2021-26614**: A vulnerability in Docker allowed unauthorized access to the Docker daemon, leading to potential container hijacking. Ensuring that only authorized commands are executed via SSM helps mitigate such risks.
- **CVE-2022-22965**: A flaw in Kubernetes allowed attackers to escalate privileges and gain control over the cluster. Using SSM to manage container deployments adds an extra layer of security.

### Common Pitfalls and How to Avoid Them

1. **Incorrect IAM Permissions**: Ensure that the IAM role assigned to the instances has the correct permissions to execute SSM commands.
2. **Unsecured Commands**: Always validate and sanitize commands to prevent injection attacks.
3. **Logging and Monitoring**: Enable logging and monitoring to detect and respond to unauthorized access attempts.

### How to Prevent / Defend

#### Detection

- **Enable CloudTrail**: Log all API calls made to SSM and monitor for suspicious activity.
- **Use AWS Config**: Track changes to your infrastructure and detect unauthorized modifications.

#### Prevention

- **IAM Role Hardening**: Restrict IAM roles to the minimum necessary permissions.
- **Secure-Coding Practices**: Validate and sanitize all inputs to prevent injection attacks.

#### Secure Code Fix

Here’s an example of how to securely execute a command using SSM:

**Vulnerable Code:**

```bash
aws ssm send-command --instance-ids $INSTANCE_ID --document-name "AWS-RunShellScript" --parameters commands="$UNSANITIZED_COMMAND"
```

**Secure Code:**

```bash
# Sanitize input
SANITIZED_COMMAND=$(echo "$UNSANITIZED_COMMAND" | sed 's/[&|;()$]/\x20/g')

aws ssm send-command --instance-ids $INSTANCE_ID --document-name "AWS-RunShellScript

---
<!-- nav -->
[[05-Secure Continuous Deployment & DAST AWS SSM Commands in Release Pipeline for Server Access|Secure Continuous Deployment & DAST AWS SSM Commands in Release Pipeline for Server Access]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/AWS SSM Commands in Release Pipeline for Server Access/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/AWS SSM Commands in Release Pipeline for Server Access/07-Secure Continuous Deployment & Dynamic Application Security Testing (DAST)|Secure Continuous Deployment & Dynamic Application Security Testing (DAST)]]
