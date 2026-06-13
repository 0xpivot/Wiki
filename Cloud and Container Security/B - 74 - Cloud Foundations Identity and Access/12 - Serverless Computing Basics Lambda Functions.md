---
tags: [cloud, basics, foundations, vapt]
difficulty: beginner
module: "74 - Cloud Foundations Identity and Access"
topic: "74.12 Serverless Computing Basics Lambda Functions"
---

# Serverless Computing Basics: Lambda Functions

## 1. Introduction and Core Concepts

Serverless computing represents a massive paradigm shift in cloud architecture. It abstracts away the underlying operating system and infrastructure layer, allowing developers to focus entirely on writing and deploying application code. In a serverless model, the cloud provider dynamically manages the allocation, provisioning, and scaling of compute resources. You are billed purely on consumption—paying only for the exact compute time your code consumes, often calculated down to the millisecond. 

AWS Lambda, Azure Functions, and Google Cloud Functions are the industry-leading implementations of this event-driven model. While the term "serverless" implies the absence of servers, physical servers are still heavily involved; however, the responsibility for their management, OS patching, scaling, and hardware maintenance is shifted entirely to the Cloud Service Provider (CSP). 

From a security perspective, this shift in responsibility is a double-edged sword. While you no longer need to worry about traditional infrastructure vulnerabilities (like outdated Linux kernels or SSH key management), the attack surface morphs. Security focus must pivot sharply towards application logic, Identity and Access Management (IAM), dependency management, and the complex web of triggers and event sources that invoke the functions.

### 1.1 The Serverless Execution Model

A serverless function is fundamentally an event-driven piece of code. It remains dormant until a specific event triggers its execution. 

1.  **Event Source:** An action occurs in the cloud environment (e.g., an HTTP request via an API Gateway, a file uploaded to an S3 bucket, a message placed on an SQS queue, a change in a DynamoDB table, or a scheduled cron event via EventBridge).
2.  **Trigger Configuration:** The event source is explicitly configured to invoke a specific serverless function when the event occurs.
3.  **Execution Environment (Micro-VM/Container):** Upon invocation, the cloud provider rapidly provisions a secure, isolated execution environment (often a micro-VM like AWS Firecracker).
4.  **Execution:** The function code is injected into this environment, and the event payload (often a JSON object) is passed to the function handler. The code executes and processes the payload.
5.  **Termination/Freeze:** Once execution completes, the environment is either immediately destroyed or temporarily frozen ("kept warm") for a short period to handle subsequent requests more rapidly, mitigating the latency associated with "cold starts."

## 2. In-Depth Architecture and the Shared Responsibility Model

In the context of AWS Lambda (and analogous services), the Shared Responsibility Model looks drastically different compared to traditional EC2 instances or containerized workloads. The CSP assumes responsibility for securing the physical data center, the network fabric, the hypervisor, the host operating system, and the isolation of the execution environment itself. 

The customer's security responsibilities are tightly confined to the following areas:
*   **The Application Code:** The actual logic executing within the function.
*   **Third-Party Dependencies:** The libraries and packages bundled with the deployment artifact.
*   **Identity and Access Management (IAM):** The roles, policies, and permissions assigned to the function, dictating what other cloud resources it can access.
*   **Event Source Configuration:** Securing the services that trigger the function (e.g., placing WAFs in front of API Gateways).
*   **Data Security:** Data classification, validation, and encryption (in transit and at rest).

## 3. Visualizing Serverless Architecture and Attack Flow

The following diagram illustrates a common serverless workflow and highlights where vulnerabilities can be introduced and exploited by an attacker.

```text
                                +-----------------------------------+
                                |        CLOUD ENVIRONMENT          |
                                |                                   |
  +-------+    Malicious JSON   |  +-----------------------------+  |
  |       | ---Payload--------->|  |        API Gateway          |  |
  | Attac |                     |  |  (Entry Point / Trigger)    |  |
  | ker   | <-------------------|  +-------------+---------------+  |
  |       |    Extracted Data   |                |                  |
  +-------+                     |                | Invoke (Passes Event)
                                |                v                  |
                                |  +-----------------------------+  |
                                |  |       Lambda Function       |  |
                                |  |                             |  |
                                |  |  +-----------------------+  |  |
                                |  |  | Execution Environment |  |  |
                                |  |  |                       |  |  |
                                |  |  |  [Vulnerable Code:    |  |  |
                                |  |  |   Command Injection]  |  |  |
                                |  |  |         |             |  |  |
                                |  |  |         v             |  |  |
                                |  |  |  [Dump Env Variables] |  |  |
                                |  |  +-----------------------+  |  |
                                |  |             |               |  |
                                |  +-------------|---------------+  |
                                |                |  Uses Stolen IAM |
                                |                |  Execution Role  |
                                |                v                  |
                                |  +-----------------------------+  |
                                |  |      Backend Services       |  |
                                |  |  (e.g., DynamoDB, S3, RDS)  |  |
                                |  +-----------------------------+  |
                                +-----------------------------------+
```

## 4. The Serverless Attack Surface

The attack surface in serverless environments is distinctly different from traditional VM-based architectures. Traditional network scanning tools are largely ineffective against Lambda functions.

### 4.1 Event Data Injection (The New Input Validation)
Because serverless functions are event-driven, they consume data from a vast and varied array of sources (API Gateway, S3 metadata, SNS messages, SQS queues, CloudWatch logs). If the function code does not rigorously validate, type-check, and sanitize this incoming event payload, it is highly susceptible to injection attacks. 
This is the serverless equivalent of traditional web input validation flaws, but the attack vectors are more complex because the malicious input might be an S3 object metadata field, rather than a standard HTTP POST parameter.

### 4.2 Over-Privileged IAM Execution Roles
Every Lambda function executes under an assumed identity, known as the IAM Execution Role. A widespread and dangerous misconfiguration is assigning overly broad permissions to this role. Developers often use managed policies like `AdministratorAccess` or wildcard actions (e.g., `s3:*`, `dynamodb:*`) to avoid permission errors during rapid development, and these excessive permissions often make it into production. If the function's code is compromised via an injection flaw, the attacker instantly inherits these permissions, leading to lateral movement, privilege escalation, or massive data exfiltration.

### 4.3 Insecure Third-Party Dependencies
Functions rely heavily on third-party open-source libraries and packages (npm, pip, maven). The traditional risk of vulnerable dependencies remains, but it is amplified because serverless applications are often highly decentralized into dozens or hundreds of micro-functions, making centralized dependency management and vulnerability scanning much more challenging. A vulnerable dependency in one small, seemingly insignificant function can compromise the execution environment.

### 4.4 Insecure Storage and Secrets Management
Developers sometimes take shortcuts and hardcode secrets (API keys, database credentials, encryption keys) directly into the function code or store them as plain-text environment variables. In AWS Lambda, environment variables are easily accessible if an attacker achieves arbitrary code execution within the function context.

### 4.5 Denial of Wallet (DoW) Attacks
Unlike traditional Denial of Service (DoS) attacks that aim to crash a server by exhausting CPU or memory, serverless functions scale automatically and near-infinitely by design. An attacker can intentionally trigger a function millions of times. The service won't crash, but the cloud provider will bill the customer for every single execution, leading to astronomical and unexpected costs. This is often termed a Denial of Wallet (DoW) attack.

## 5. Attack Vectors and VAPT Methodology

Testing serverless applications requires a significant shift in methodology, focusing heavily on application logic, source code review, and IAM configuration auditing.

### 5.1 Code Review and Static Analysis (SAST)
The most effective way to identify vulnerabilities in serverless applications is through rigorous source code review (White-box testing).
1.  **Analyze Event Handling:** Scrutinize how the function parses and uses the `event` object. Look for direct, unsanitized use of event data in system commands (OS Command Injection), database queries (SQL/NoSQL Injection), or file system operations (Path Traversal).
    *Example of Vulnerable Python Code:*
    ```python
    import os
    def lambda_handler(event, context):
        # Vulnerable to command injection via the 'target' field
        target_ip = event['target']
        result = os.popen(f"ping -c 1 {target_ip}").read()
        return result
    ```
2.  **Examine Secrets Management:** Search the codebase for hardcoded credentials or the use of plain-text environment variables for sensitive data. Verify if the function securely retrieves secrets at runtime using services like AWS Secrets Manager or Systems Manager Parameter Store.
3.  **Dependency Scanning:** Use package-specific audit tools (e.g., `npm audit`, `pip-audit`, or dedicated SAST tools like Snyk) to identify vulnerable third-party libraries bundled within the deployment zip file.

### 5.2 Dynamic Testing (DAST)
Testing deployed functions involves interacting with their external triggers.
1.  **Fuzzing Event Payloads:** If the function is triggered by an API Gateway, deeply fuzz the HTTP parameters, headers, and JSON body. If triggered by an S3 upload, upload files with malformed names, excessive metadata, or malicious internal content.
2.  **Testing for Injection:** Attempt standard injection payloads (SQLi, Command Injection) through all identified input vectors.
3.  **Testing Environment Variable Extraction:** If you suspect a command injection vulnerability, attempt to execute commands that print the environment variables to the response output (e.g., `printenv`, `env`, or reading `/proc/self/environ`). In AWS Lambda, environment variables contain extremely sensitive information, including the AWS session token, access key, and secret key assigned to the function's execution role.

### 5.3 IAM Role Auditing
1.  **Review the Execution Role Policy:** Use the cloud console or CLI to inspect the specific IAM role associated with the Lambda function.
2.  **Identify Wildcards:** Look for IAM policies that utilize wildcards (`*`) for `Action` or `Resource` fields (e.g., `Action: ["s3:*"]`, `Resource: ["*"]`).
3.  **Assess Least Privilege:** Determine if the function actually requires all the permissions granted to it. If a function's sole purpose is to read an image from a specific S3 bucket, resize it, and write it to another specific bucket, its policy should be strictly limited to those two buckets and those specific actions (`s3:GetObject`, `s3:PutObject`).

## 6. Defense and Mitigation Strategies

Securing serverless functions requires a defense-in-depth approach tailored specifically to the event-driven, ephemeral model.

### 6.1 Strict Input Validation
Treat the entire incoming event payload as untrusted user input, regardless of the event source (even if it comes from an internal AWS service). Implement rigorous input validation, sanitization, and strict type checking before the data is processed by the core business logic. Utilize established validation libraries (like Joi for Node.js or Pydantic for Python).

### 6.2 Enforce Principle of Least Privilege (PoLP)
This is arguably the most critical defense mechanism. Create a unique, highly specific IAM execution role for *every individual function*. The role must grant only the absolute minimum permissions required for that specific function to execute its intended task. Never use wildcards for resources; specify exact ARNs (Amazon Resource Names).

### 6.3 Secure Secrets Management
Never hardcode secrets in source code or store them as plain-text environment variables. Utilize managed secret storage services (e.g., AWS Secrets Manager, Azure Key Vault). The Lambda function should be granted specific IAM permissions to retrieve the required secret via API call at runtime. 

### 6.4 API Gateway Security Controls
If the function is exposed to the internet via an API Gateway, heavily utilize the Gateway's built-in security features. Implement Web Application Firewalls (WAF), enforce rate limiting, set up usage plans to mitigate DoW attacks, and require strong authentication (e.g., Amazon Cognito, OAuth, custom Lambda Authorizers) before allowing the API Gateway to invoke the backend function.

### 6.5 Ephemeral Storage Security (/tmp)
Lambda functions have access to a small amount of ephemeral storage located at `/tmp`. Ensure that sensitive data written to `/tmp` during execution is encrypted and, crucially, properly deleted when the execution completes. Because the execution container might be reused for subsequent invocations (a "warm start"), failing to clear `/tmp` can expose data to a completely different user's execution context.

## 7. Chaining Opportunities

Serverless vulnerabilities are frequently chained together to achieve a catastrophic impact that goes far beyond the initial function compromise.

*   **OS Command Injection + Over-Privileged IAM Role = Cloud Account Compromise:** An attacker exploits an OS Command Injection flaw in a Lambda function triggered via an API Gateway. They execute code to dump the environment variables, extracting the temporary AWS credentials of the execution role. If that role has broad permissions (e.g., `AdministratorAccess`), the attacker uses those credentials via the AWS CLI to pivot, create new administrative IAM users, or exfiltrate databases across the entire cloud environment.
*   **Vulnerable Dependency + Insecure /tmp Storage = Cross-Tenant Data Leakage:** A vulnerable dependency allows an attacker to read arbitrary local files. The function processes sensitive PII and temporarily writes it to `/tmp` for processing. Due to container reuse, the attacker invokes the function repeatedly and uses the file read vulnerability to extract the PII left behind in `/tmp` by previous, legitimate executions.
*   **Missing Rate Limits + Heavy Compute Function = Denial of Wallet:** A public-facing API triggers a Lambda function that performs highly complex and time-consuming cryptographic calculations. Because no rate limits are configured on the API Gateway, the attacker scripts thousands of concurrent requests. AWS auto-scales to handle the load, resulting in a massive, unexpected bill for the victim organization.

## 8. Related Notes
*   [[02 - Identity and Access Management IAM Core Principles]]
*   [[11 - Cloud Networking VPCs Subnets and Security Groups]]
*   [[14 - Cloud API Gateways and Endpoints]]
*   [[18 - Cloud Specific Exploitation SSRF and Metadata APIs]]
