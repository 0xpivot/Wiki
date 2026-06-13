---
tags: [threat-hunting, cloud, aws, azure, vapt]
difficulty: advanced
module: "91 - Cloud Threat Hunting: AWS, Azure, GCP"
topic: "91.04 Analyzing AWS GuardDuty and Security Hub Findings"
---

# Analyzing AWS GuardDuty and Security Hub Findings

## 1. Introduction and Executive Summary

While manual hunting through raw CloudTrail logs via Athena or Splunk is a critical skill, AWS provides managed threat detection services designed to automate the identification of malicious activity. The two primary pillars of AWS native security monitoring are **Amazon GuardDuty** and **AWS Security Hub**.

- **GuardDuty** is a continuous security monitoring service that analyzes massive streams of metadata (CloudTrail Events, VPC Flow Logs, DNS Logs, EKS Audit Logs, and EBS volume data) using machine learning and integrated threat intelligence to detect unauthorized behavior.
- **Security Hub** is a Cloud Security Posture Management (CSPM) and alert aggregation service. It ingests findings from GuardDuty, Amazon Macie, IAM Access Analyzer, AWS Inspector, and third-party tools, normalizing them into a standard format called the AWS Security Finding Format (ASFF).

For a threat hunter, these services are often the starting point of an investigation (the trigger). The hunter's job is to take a GuardDuty finding, analyze its context, and correlate it with raw logs to uncover the full attack narrative.

## 2. GuardDuty Data Sources and Architecture

GuardDuty is powerful because it operates "under the hood." You do not need to enable VPC Flow Logs or DNS logging for GuardDuty to analyze them; it taps into the backend streams directly without impacting your AWS bill for log storage.

### Data Sources Analyzed:
1. **AWS CloudTrail Management Events:** Tracks API calls (e.g., `CreateUser`, `StopLogging`).
2. **AWS CloudTrail Data Events for S3:** Tracks object-level access (e.g., `GetObject`).
3. **VPC Flow Logs:** Tracks IP traffic going to and from network interfaces.
4. **DNS Logs:** Tracks DNS requests made by EC2 instances to the Route 53 Resolver.
5. **EKS Audit Logs:** Kubernetes API control plane activity.
6. **EBS Volume Data (Malware Protection):** Agentless scanning of EC2 storage volumes for known malware signatures.

## 3. Architecture Visualization: GuardDuty & Security Hub Flow

```text
  [VPC Flow Logs]  [DNS Logs]  [CloudTrail]  [EKS Logs]
        |              |             |            |
        +--------------+------+------+------------+
                              |
                     (Backend Data Streams)
                              |
                              v
                  +-----------------------+
                  |                       |
                  |   Amazon GuardDuty    | <--- Threat Intel / ML Models
                  |                       |
                  +-----------------------+
                              |
                     (Generates Findings)
                              |
                              v
                  +-----------------------+
                  |                       |
                  |    AWS Security Hub   | <--- Aggregates Macie, Inspector
                  |    (ASFF Normalization|
                  +-----------------------+
                              |
                              | (EventBridge Routing)
                              v
                 +--------------------------+
                 |    SIEM / SOAR / Slack   |
                 | (Splunk, PagerDuty, Jira)|
                 +--------------------------+
```

## 4. Dissecting GuardDuty Findings

GuardDuty findings follow a specific naming convention:
`ThreatPurpose:ResourceTypeAffected/ThreatFamilyName.DetectionMechanism`

### Critical Finding Types for Threat Hunters:
- `UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration.OutsideAWS`: This alerts when temporary credentials created for an EC2 instance (via IMDS) are utilized from an IP address outside of the AWS network. This is the hallmark of SSRF leading to credential theft.
- `PenTest:IAMUser/KaliLinux`: Indicates API calls originating from an IP known to belong to a Kali Linux EC2 AMI.
- `CryptoCurrency:EC2/BitcoinTool.B`: VPC Flow Log analysis detects an EC2 instance communicating with known cryptocurrency mining pools.
- `Discovery:S3/AnomalousBehavior`: Machine learning detects an IAM entity accessing S3 buckets in a pattern vastly different from their historical baseline (e.g., downloading thousands of files when they normally access none).
- `Impact:EC2/PortSweep`: An EC2 instance is actively scanning internal network segments.

## 5. Real-World Attack Scenario

### The Scenario: From Mining to Lateral Movement
1. **The Alert:** The SOC receives a high-severity GuardDuty finding in Security Hub: `CryptoCurrency:EC2/BitcoinTool.B` affecting instance `i-0abcd1234efgh5678`.
2. **Initial Triage:** A tier-1 analyst sees the cryptomining alert and assumes it's a simple case of a vulnerable web app being exploited to drop an XMRig miner. They isolate the instance.
3. **The Hunter's Deep Dive:** The threat hunter looks deeper at the ASFF JSON payload of the finding. They extract the `IAM Instance Profile` attached to the EC2 instance.
4. **Correlation:** The hunter queries CloudTrail in Athena for that specific IAM Role. They discover that *before* the cryptomining started, the role executed `sts:GetCallerIdentity` and `ssm:GetParameters` from a strange IP address.
5. **The Revelation:** The attacker didn't just install a miner. They used an RCE to steal the instance credentials, exfiltrated them, read AWS Systems Manager Parameter Store to steal database passwords, and *then* dropped the cryptominer as a distraction/monetization strategy.

## 6. Hunting Methodology: Triaging a Finding

When a GuardDuty alert fires, a threat hunter must answer several questions using raw logs:

1. **Verify the True Positive:** Is the threat intelligence accurate? Check the destination IP on VirusTotal or GreyNoise.
2. **Determine the Blast Radius:** 
   - If an EC2 instance is communicating with a C2 server, what IAM role does that instance possess?
   - Has that IAM role been used to make API calls (CloudTrail) since the time of the first C2 beacon?
3. **Trace the Root Cause:** How did the instance get compromised?
   - Check the VPC Flow Logs for inbound connections on unexpected ports prior to the outbound C2 beacon.
   - Check an Application Load Balancer (ALB) access logs for web exploits (e.g., Log4j or SQLi payloads).

## 7. Operationalizing the Hunt: Contextual Queries

### Athena SQL: Investigating an Instance Credential Exfiltration Alert
When GuardDuty triggers `InstanceCredentialExfiltration`, use this query to find exactly what the attacker did with the stolen credentials.

```sql
SELECT 
    eventTime,
    eventName,
    requestParameters,
    responseElements,
    sourceIPAddress,
    userAgent
FROM cloudtrail_logs
-- The role ARN attached to the compromised EC2 instance
WHERE userIdentity.arn = 'arn:aws:sts::123456789012:assumed-role/Web-Server-Role/i-0abcd1234efgh5678'
-- Exclude legitimate AWS IP ranges to only see the attacker's actions
AND sourceIPAddress NOT LIKE '10.%'
AND sourceIPAddress NOT LIKE '172.16.%'
AND sourceIPAddress NOT LIKE '192.168.%'
ORDER BY eventTime ASC;
```

### KQL (If logs are in Sentinel): Cross-Referencing GuardDuty with VPC Flow
This query correlates a GuardDuty finding involving a specific malicious IP with raw VPC Flow Logs to see the exact byte transfer volume.

```kql
let MaliciousIP = "198.51.100.42"; // IP extracted from GuardDuty finding
AWSVpcFlowLogs
| where TimeGenerated > ago(24h)
| where SrcAddr == MaliciousIP or DstAddr == MaliciousIP
| summarize TotalBytes = sum(Bytes), TotalPackets = sum(Packets) by SrcAddr, DstAddr, DstPort, Action
| sort by TotalBytes desc
```

## 8. Mitigation and Remediation
- **Automated Response:** Use Amazon EventBridge to trigger an AWS Lambda function that automatically isolates compromised EC2 instances (by attaching a deny-all Security Group) when GuardDuty fires critical findings.
- **Tuning:** Use GuardDuty Suppression Lists to silence expected behavior (e.g., a legitimate vulnerability scanner that triggers `PortSweep` alerts).
- **Consolidation:** Ensure all AWS accounts in the organization delegate GuardDuty administration to a centralized Security tooling account via AWS Organizations.

## 9. Chaining Opportunities
- **[[03 - Hunting for Compromised IAM Credentials in AWS]]**: GuardDuty alerts are often the first indicator that credentials discussed in Module 03 have been compromised.
- **[[02 - AWS CloudTrail Analysis for Persistence]]**: Once GuardDuty detects the initial breach, you must hunt through CloudTrail to ensure the attacker hasn't established persistence.
- **[[01 - Differences in Cloud vs On-Premises Hunting]]**: GuardDuty operates entirely differently than an on-premises NIDS/HIDS.

## 10. Related Notes
- [[AWS EventBridge Auto-Remediation]]
- [[Instance Metadata Service (IMDS) Version 1 vs 2]]
- [[AWS VPC Flow Log Analysis]]
- [[Cloud Security Posture Management (CSPM)]]
