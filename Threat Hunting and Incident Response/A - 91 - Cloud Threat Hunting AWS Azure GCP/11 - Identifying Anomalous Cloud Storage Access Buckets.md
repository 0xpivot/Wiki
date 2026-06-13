---
tags: [threat-hunting, cloud, aws, azure, vapt]
difficulty: advanced
module: "91 - Cloud Threat Hunting: AWS, Azure, GCP"
topic: "91.11 Identifying Anomalous Cloud Storage Access Buckets"
---

# Identifying Anomalous Cloud Storage Access Buckets

Cloud storage buckets (AWS S3, Azure Blob Storage, GCP Cloud Storage) represent the backbone of modern data lakes and application storage. Because they often hold a mix of publicly necessary assets and highly confidential intellectual property, they are a primary target for threat actors. As a threat hunter, your objective extends far beyond simply finding "open buckets" (which is a posture management task). You must identify anomalous access patterns that suggest compromise, stealthy exfiltration, or persistence. This requires deep inspection of data plane and control plane logs, understanding complex identity relationships, and applying statistical models to differentiate normal application behavior from malicious activity.

## Core Concepts of Cloud Storage Threats

Cloud storage can be attacked through several vectors, each leaving distinct forensic artifacts:
1. **Misconfiguration Exploitation**: World-readable or writable permissions that are discovered and exploited via automated scanning tools.
2. **Credential Theft**: Legitimate IAM keys stolen from a developer machine, compromised CI/CD pipeline, or vulnerable workload and used from anomalous geographic or network locations.
3. **Privilege Escalation & Persistence**: Modifying bucket policies to grant permanent access to an external, attacker-controlled account.
4. **Ransomware & Sabotage**: Rapid encryption, deletion, or overwriting of objects combined with the suspension of object versioning.
5. **Supply Chain Risks**: Over-permissive third-party roles or vendors accessing the data inappropriately.

### Control Plane vs. Data Plane Telemetry

A critical distinction in cloud storage hunting is the separation of logging planes:
- **Control Plane (Management Events)**: Involves administrative actions like creating buckets, changing bucket policies, enabling encryption, or modifying public access block settings (e.g., `PutBucketPolicy`, `DeleteBucket`, `PutBucketVersioning`). In AWS, these are tracked by CloudTrail natively and are relatively low-volume.
- **Data Plane (Data Events)**: Involves object-level operations inside the bucket (e.g., `GetObject`, `PutObject`, `ListBucket`). Because these can generate billions of events a day, they are typically NOT logged by default. They must be explicitly enabled (AWS CloudTrail Data Events or S3 Server Access Logs, Azure Storage Analytics logging, and GCP Data Access Audit Logs). Without data plane logs, detecting data exfiltration is virtually impossible.

## Anatomy of an Attack on Cloud Storage

```text
+-----------------------+      +-------------------------+      +---------------------------+
|  Compromised          |      |  Cloud Control          |      |  Cloud Storage            |
|  Identity / API Key   | ===> |  Plane (IAM/Policy)     | ===> |  Bucket (Data Plane)      |
|  (Anomalous Location) |      |  Disable Logging / PAB  |      |  Target: PII & Secrets    |
+-----------------------+      +-------------------------+      +---------------------------+
         |                                  |                                 |
         | (1) Steal & Assume Creds         | (2) Modify BucketPolicy         | (3) Bulk List / Get
         v                                  v                                 v
+-----------------------+      +-------------------------+      +---------------------------+
|  Threat Actor         |      |  CloudTrail /           |      |  S3 Access Logs /         |
|  Infrastructure (C2)  | <=== |  Management Audit Logs  | <=== |  Data Events (High Vol)   |
+-----------------------+      +-------------------------+      +---------------------------+
```

## Threat Hunting Methodologies

### 1. Identifying Data Exfiltration (Data Plane)

**Hypothesis:** An attacker has obtained valid credentials and is bulk-downloading objects from a highly sensitive, non-public bucket.

**Indicators to look for:**
- Exceptionally high volume of `GetObject` requests from a single IP, Identity, or User Agent within a condensed timeframe.
- `ListBucket` operations immediately followed by rapid, sequential `GetObject` operations.
- User Agent anomalies: For example, an IAM role associated with a microservice usually accesses S3 via `Boto3` or the `aws-sdk-java`. Suddenly, the same identity is using `aws-cli/2.0.0 Python/3.8.5` from an unknown IP.
- Network anomalies: Source IP originating from a Tor exit node, commercial VPN provider, or an ASN known for malicious bulletproof hosting.
- HTTP Status Code patterns: Attackers scanning a bucket often generate high volumes of `403 Forbidden` or `404 Not Found` errors before finding objects they have permission to read.

**Azure Kusto Query Language (KQL) Example for High Volume Access:**
```kusto
StorageBlobLogs
| where TimeGenerated > ago(1d)
| where OperationName == "GetBlob" or OperationName == "ListBlobs"
| where StatusCode == 200
| summarize CallCount = count(), TotalBytes = sum(ResponseHeaderSize + ResponseBodySize) 
  by CallerIpAddress, AccountName, UserAgentHeader, Identity
| where TotalBytes > 5000000000 // Greater than 5GB exfiltrated
| order by TotalBytes desc
| project CallerIpAddress, AccountName, Identity, CallCount, TotalBytes, UserAgentHeader
```

### 2. Spotting Bucket Policy Manipulation (Control Plane)

**Hypothesis:** An attacker with elevated IAM permissions is modifying a bucket policy to establish a backdoor, allowing access from an external AWS account they control.

**Indicators to look for:**
- `PutBucketPolicy`, `PutBucketAcl`, `DeleteBucketPolicy`, or `DeleteBucketPublicAccessBlock` events.
- Inspecting the `requestParameters` for suspicious JSON payloads. Look for an external AWS Account ID (e.g., `Principal: {"AWS": "arn:aws:iam::999999999999:root"}`), wildcards (`Principal: "*"`), or an unrecognized IAM User/Role.
- Changes originating from a highly privileged identity (e.g., `OrganizationAccountAccessRole`) that rarely modifies storage policies directly in production.
- Disabling logging via `PutBucketLogging` to hide subsequent data plane activity.

**Splunk SPL Example for Anomalous Cross-Account Policy:**
```spl
index=aws_cloudtrail eventName=PutBucketPolicy
| spath path=requestParameters.bucketPolicy
| search "requestParameters.bucketPolicy"="*\"Principal\":*"
| rex field=requestParameters.bucketPolicy "\"AWS\":\s*\"(?<principal_arn>[^\"]+)\""
| makemv principal_arn
| mvexpand principal_arn
| eval is_external = if(match(principal_arn, "^arn:aws:iam::123456789012:.*$"), "Internal", "External/Unknown")
| where is_external == "External/Unknown"
| table _time, user_arn, sourceIPAddress, bucketName, principal_arn, requestParameters.bucketPolicy
```
*(Note: Replace 123456789012 with your actual corporate AWS Account ID).*

### 3. Ransomware Behavior in Cloud Storage

**Hypothesis:** An attacker is attempting to extort the organization by rapidly encrypting or deleting objects inside a production datastore.

**Indicators to look for:**
- High frequency of `PutObject` operations that overwrite existing objects (often replacing them with encrypted variants).
- Unprecedented spikes in `DeleteObject` or `DeleteObjects` (batch deletion) API calls.
- Control plane changes to KMS keys associated with the bucket (e.g., creating a new Customer Managed Key, changing the default bucket encryption to an attacker-controlled key, or scheduling a KMS key for deletion).
- Precursor defense evasion: An attacker will often execute `PutBucketVersioning` with `<Status>Suspended</Status>` to prevent the victim from simply rolling back to a previous, unencrypted version of the objects. They may also modify bucket lifecycle rules to delete current and non-current versions after 1 day.

**AWS Athena Query for Object Deletion Spikes:**
```sql
SELECT
  useridentity.arn,
  eventsource,
  eventname,
  COUNT(*) as deletion_count,
  MIN(eventtime) as first_event,
  MAX(eventtime) as last_event
FROM cloudtrail_data_events
WHERE eventname IN ('DeleteObject', 'DeleteObjects')
  AND eventtime >= now() - interval '24' hour
GROUP BY useridentity.arn, eventsource, eventname
HAVING COUNT(*) > 1000
ORDER BY deletion_count DESC;
```

### 4. Cross-Account Access and VPC Endpoint Anomalies

If your organization utilizes a complex multi-account structure, identifying rogue cross-account access is vital. Attackers may bypass public IP monitoring by routing their exfiltration through internal networks.
- Look for `AssumeRole` events followed by data access from unexpected VPCs.
- Review S3 access logs where the `Requester` account ID does not match the bucket owner account ID, and the requester is not in an approved list of third-party vendors or internal accounts.
- Monitor access via VPC Endpoints (`vpce-*`). If a bucket policy mandates `aws:sourceVpce`, an attacker might compromise an EC2 instance within that specific VPC simply to act as a proxy to exfiltrate the S3 data.

## Real-World Attack Scenario

### Scenario: The Leaky Lambda to S3 Exfiltration

1. **Initial Access**: The threat actor identifies and exploits a Serverless Server-Side Request Forgery (SSRF) vulnerability in a Lambda function `[[12 - Serverless Function Lambda Abuse Detection]]`.
2. **Credential Access**: The attacker extracts the Lambda execution role credentials via the execution environment's internal environment variables.
3. **Discovery**: Using the stolen temporary credentials (`aws_access_key_id`, `aws_secret_access_key`, `aws_session_token`) on their own machine, the attacker enumerates S3 buckets using `aws s3 ls`.
4. **Execution/Exfiltration**: The attacker identifies a highly sensitive bucket named `corp-customer-pii-backup`. They execute `aws s3 sync s3://corp-customer-pii-backup /tmp/exfil` and rapidly download 200GB of data.
5. **Defense Evasion**: Realizing the theft might be noticed, the attacker executes `aws s3api put-bucket-lifecycle-configuration` to automatically delete all objects in the bucket after 1 day, attempting to destroy the forensic evidence and cause operational disruption.

**Hunter's Response:**
- The automated detection pipeline flagged an anomalous `AssumeRole` usage alert: temporary credentials assigned to the internal Lambda role were used from a residential ISP IP address (since the attacker ran the sync from their local machine, rather than from within the AWS Lambda environment).
- Correlating the `accessKeyId` to the specific Lambda role immediately confirmed the compromise vector.
- Upon reviewing the S3 Data Events in Athena, the hunter discovered 45,000 `GetObject` calls occurring over a span of 15 minutes originating from that same residential IP.
- The hunter immediately revoked the active IAM sessions for the Lambda role, isolated the Lambda function, and corrected the bucket's lifecycle policy to prevent data destruction.

## Detection Engineering & Log Sources

To effectively hunt for these anomalies and build high-fidelity alerts, you must aggregate, normalize, and analyze the following log sources:
- **AWS**: CloudTrail (Management Events), CloudTrail Data Events (Object Level), S3 Server Access Logs (useful for request headers and unauthenticated access attempts), VPC Flow Logs (for internal VPC exfiltration), AWS Macie alerts, and GuardDuty S3 Protection findings.
- **Azure**: Activity Logs, Storage Analytics Logs, Azure Defender for Storage alerts, and Azure AD Sign-in logs.
- **GCP**: Cloud Audit Logs (Admin Activity for control plane & Data Access for object interactions).

### Baseline and Anomaly Detection (UBA/UEBA)
Hardcoded thresholds (e.g., alert if > 1000 downloads) are notoriously prone to false positives in cloud environments where microservices perform massive bulk operations daily. Effective hunting requires statistical baselining:
- Calculate the average bytes downloaded per IAM user or Role per day over a rolling 30-day window.
- Trigger alerts when an identity exceeds 3 standard deviations from their moving average.
- Flag any `GetObject` activity from a geographical region where the organization has no employees or deployed workloads.
- Utilize machine learning models to cluster "normal" API call sequences and flag outliers (e.g., an identity that usually calls `PutObject` suddenly calling `GetBucketAcl` and `DeleteObject`).

## Remediation and Mitigation Strategies

1. **Enforce Public Access Blocks**: Universally use AWS Account-level or Organization-level "Block Public Access" to prevent accidental or malicious policy changes from exposing buckets to the internet.
2. **VPC Endpoints & Network Perimeters**: Mandate that sensitive buckets can only be accessed via specific internal VPC Endpoints. Use the `aws:sourceVpce` or `aws:SourceIp` conditions in the bucket policy to strictly deny access originating from the public internet, even if valid credentials are used.
3. **MFA Delete and Object Versioning**: Enable Object Versioning and MFA Delete. This requires physical MFA token authentication to permanently delete an object version, effectively neutralizing ransomware and sabotage attempts.
4. **Least Privilege IAM**: Radically remove wildcard (`*`) permissions in IAM policies attached to users and machine roles. A web server role should only have `s3:PutObject` on specific paths, not `s3:*`.
5. **Data Classification Integration**: Leverage native cloud tools like AWS Macie, Azure Purview, or GCP Cloud Data Loss Prevention (DLP) to automatically scan and classify data. Threat hunts should prioritize monitoring buckets containing PII, PHI, or financial data. A single `GetObject` on a highly sensitive credentials file is infinitely more critical than a million `GetObject` calls on a public images bucket.

---

## Chaining Opportunities
- Attackers often dump metadata and perform network discovery before accessing cloud data. Look for preceding anomalies in identity usage `[[14 - Correlating Cloud Identity with Network Activity]]`.
- If an attacker uses a compromised containerized workload to access storage, you must pivot to investigate the orchestrator's audit logs `[[13 - Hunting in Kubernetes Cluster Audit Logs]]`.
- Building a robust, cost-effective detection pipeline for high-volume S3 logs requires specialized big data SIEM architectures `[[15 - Building a Cloud Native Threat Hunting Pipeline]]`.

## Related Notes
- `[[01 - Identity and Access Management (IAM) Privilege Escalation]]`
- `[[03 - S3 Bucket Misconfigurations and Exploitation]]`
- `[[08 - Understanding CloudTrail Logging Mechanisms]]`
- `[[20 - Ransomware in the Cloud]]`
