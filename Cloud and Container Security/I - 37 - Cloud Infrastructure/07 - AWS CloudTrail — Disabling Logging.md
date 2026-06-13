---
tags: [aws, cloudtrail, logging, evasion, defense-evasion]
difficulty: intermediate
module: "37 - Cloud Infrastructure"
topic: "37.07 AWS CloudTrail"
---

# AWS CloudTrail — Disabling Logging and Defense Evasion

## 1. Introduction to AWS CloudTrail
AWS CloudTrail is the primary auditing and compliance service in AWS. It records AWS API calls for your account and delivers log files to an Amazon S3 bucket. It provides event history of AWS account activity, including actions taken through the AWS Management Console, AWS SDKs, command line tools, and other AWS services.

For a SOC (Security Operations Center) or a cloud incident response team, CloudTrail is the ultimate source of truth. Consequently, for an attacker, CloudTrail is the primary obstacle to stealth. Disabling, disrupting, or tampering with CloudTrail is a critical phase of post-exploitation known as **Defense Evasion**.

## 2. ASCII Architecture Diagram: CloudTrail Evasion

```text
   [ Attacker (Compromised IAM Admin) ]
             |
             |  1. Goal: Execute destructive actions without detection.
             v
   +---------------------------------------------------+
   |             [ Defense Evasion Tactics ]           |
   |                                                   |
   |  A. StopLogging                                   |
   |     aws cloudtrail stop-logging --name target     |
   |                                                   |
   |  B. DeleteTrail                                   |
   |     aws cloudtrail delete-trail --name target     |
   |                                                   |
   |  C. Tamper with S3 Bucket Policy                  |
   |     Deny CloudTrail write access to the bucket    |
   |                                                   |
   |  D. KMS Key Disablement                           |
   |     Disable the CMK used to encrypt the logs      |
   +-------------------------+-------------------------+
                             |
                             |  2. Trail stops recording events
                             v
   [ CloudTrail API ] -----------------X-> [ S3 Log Bucket ]
                             |
                             |  3. Attacker operates in the dark
                             v
   [ Exfiltrate Data / Deploy Ransomware / Backdoor IAM ]
                             |
                             |  4. Actions are NOT logged. SOC is blind.
                             v
                 [ Unnoticed Compromise ]
```

## 3. Defense Evasion Techniques

When an attacker gains sufficient privileges (usually `AdministratorAccess` or specific `cloudtrail:*` permissions), they will attempt to blind the defenders before executing noisy actions like exfiltrating large S3 buckets or deploying crypto-miners.

### 3.1. Stopping the Trail (`cloudtrail:StopLogging`)
The most direct method is simply turning the trail off.
- **Exploitation**:
  ```bash
  aws cloudtrail stop-logging --name arn:aws:cloudtrail:us-east-1:123456789012:trail/management-events
  ```
- **Impact**: API calls made after this command are no longer recorded. The `StopLogging` event itself *is* recorded, serving as a massive red flag, but subsequent actions are invisible.

### 3.2. Deleting the Trail (`cloudtrail:DeleteTrail`)
A more destructive approach is completely deleting the trail configuration.
- **Exploitation**:
  ```bash
  aws cloudtrail delete-trail --name management-events
  ```

### 3.3. S3 Bucket Policy Manipulation
Instead of touching the CloudTrail service directly, an attacker can modify the destination. CloudTrail relies on the S3 Bucket Policy to grant it permissions to `s3:PutObject`.
- **Exploitation**: The attacker modifies the S3 bucket policy of the log bucket to explicitly `Deny` the `cloudtrail.amazonaws.com` service principal.
- **Impact**: CloudTrail attempts to write logs, fails due to access denied, and silently drops the logs. The trail appears "Active" in the console, but no new logs arrive.

### 3.4. KMS Key Disablement
If the CloudTrail logs are encrypted using AWS KMS (a security best practice), the attacker can target the KMS key instead of the trail.
- **Exploitation**: The attacker disables or schedules the deletion of the KMS Customer Managed Key (CMK) used by the trail.
  ```bash
  aws kms disable-key --key-id arn:aws:kms:us-east-1:...
  ```
- **Impact**: CloudTrail can no longer encrypt the logs, and therefore fails to write them to S3. Again, the trail appears active, but logging ceases.

### 3.5. Event Selectors Manipulation
An attacker can subtly modify the trail to stop logging specific events, rather than shutting down the whole trail.
- **Exploitation**: Modifying the event selectors to exclude Management Events or to only log Read-Only events.
  ```bash
  aws cloudtrail put-event-selectors --trail-name management-events --event-selectors '[{"ReadWriteType": "ReadOnly"}]'
  ```
- **Impact**: The attacker's destructive write actions (creating users, deleting databases) are ignored by the trail.

## 4. Bypassing CloudTrail (Operating in the Shadows)
If an attacker lacks the permissions to disable CloudTrail, they must operate in ways that minimize log impact or utilize blind spots.

### 4.1. Data Events vs. Management Events
By default, CloudTrail only logs **Management Events** (control plane actions like creating an EC2 instance, attaching an IAM policy). It does **NOT** log **Data Events** (data plane actions like reading an object from S3, executing a Lambda function, or inserting data into DynamoDB) because of the high volume and cost.
- **Evasion Strategy**: An attacker who discovers a bucket containing sensitive data can download the entire bucket using `s3:GetObject`. Unless the victim explicitly enabled S3 Data Events for that bucket, the exfiltration is entirely invisible to CloudTrail.

### 4.2. Operating in Unsupported Regions
Historically, attackers would spin up infrastructure (like EC2 crypto-miners) in obscure AWS regions (e.g., `af-south-1` or `ap-east-1`) hoping that the administrators forgot to configure CloudTrail to operate globally or forgot to monitor those specific regions.
- **Note**: AWS now creates multi-region trails by default, but legacy environments might still have single-region trails.

## 5. Detecting Defense Evasion
SOC teams must implement alerting specifically tailored to catch defense evasion attempts.
- **Alert on Mutating API Calls**: Immediate high-severity alerts should trigger on any of the following CloudTrail events: `StopLogging`, `DeleteTrail`, `UpdateTrail`, `PutEventSelectors`.
- **CloudWatch Metrics**: Monitor the `S3 Delivery Errors` metric for CloudTrail. A sudden spike indicates that CloudTrail is failing to write to S3 (likely due to Bucket Policy or KMS tampering).
- **GuardDuty**: Amazon GuardDuty automatically detects CloudTrail evasion tactics and generates findings like `Stealth:IAMUser/CloudTrailLoggingDisabled`.

## 6. Remediation and Securing CloudTrail
1. **SCP Restrictions**: Use AWS Organizations Service Control Policies (SCPs) to explicitly deny the `cloudtrail:StopLogging` and `cloudtrail:DeleteTrail` actions for all users, including Administrators. Only a highly restricted Break-Glass role should be able to alter logging.
2. **Dedicated Log Account**: Centralize CloudTrail logs into a dedicated, isolated AWS Account (Log Archive account) where production admins have absolutely no access. This prevents a compromised admin in the production account from tampering with the S3 bucket policies.
3. **MFA Delete**: Enable MFA Delete on the S3 bucket storing the CloudTrail logs to prevent attackers from deleting historical logs to cover their tracks.
4. **Log File Validation**: Enable CloudTrail Log File Validation, which uses cryptographic hashing to provide integrity checks. If an attacker modifies an existing log file in S3, validation will fail and expose the tampering.

## 7. Conclusion
Disabling CloudTrail is the digital equivalent of cutting the wires to the security cameras before robbing a bank. It is an aggressive, noisy action that indicates an attacker has achieved high-level privileges and is preparing for a major impact event. Protecting the logging infrastructure is just as critical as protecting the data itself.

---

## Chaining Opportunities
- **[[01 - AWS IAM — Roles, Policies, Misconfigurations]]**: Defense evasion requires high privileges. Exploiting IAM to gain Admin access is the prerequisite to disabling CloudTrail.
- **[[02 - AWS S3 — Public Access, ACL Misconfiguration]]**: Understanding the lack of Data Events in default CloudTrail configurations allows attackers to exfiltrate S3 data completely undetected.
- **[[06 - AWS SecretsManager Parameter Store — Misconfigured Access]]**: Similar to S3, dumping secrets can sometimes slip under the radar if advanced logging and monitoring for Secrets Manager are not configured.

## Related Notes
- [[03 - AWS EC2 — Metadata Service (IMDS) Exploitation]]
- [[05 - AWS ECS EKS — Container Privilege Escalation]]
