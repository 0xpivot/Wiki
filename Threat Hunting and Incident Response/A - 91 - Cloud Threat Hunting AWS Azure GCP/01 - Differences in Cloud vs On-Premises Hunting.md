---
tags: [threat-hunting, cloud, aws, azure, vapt]
difficulty: advanced
module: "91 - Cloud Threat Hunting: AWS, Azure, GCP"
topic: "91.01 Differences in Cloud vs On-Premises Hunting"
---

# Differences in Cloud vs On-Premises Hunting

## 1. Introduction and Executive Summary

Threat hunting in cloud environments (AWS, Azure, GCP) requires a fundamental paradigm shift from traditional on-premises network and endpoint hunting. In an on-premises environment, the primary focus is often on the traditional network perimeter, physical endpoints (servers, workstations), and Active Directory. Threat hunters rely heavily on artifacts such as PCAP (Packet Capture), NetFlow, Windows Event Logs, Sysmon, and EDR (Endpoint Detection and Response) telemetry.

In the cloud, the perimeter is completely redefined. The new perimeter is **Identity and Access Management (IAM)**. The infrastructure is abstracted, and everything is defined by software and accessed via APIs. Consequently, threat hunters must pivot from looking at IP addresses, MAC addresses, and process execution trees to analyzing API calls, IAM roles, trust policies, and ephemeral compute telemetry. This document explores the profound differences between cloud and on-premises threat hunting, detailing the shift in data sources, attack surfaces, and investigative methodologies.

## 2. The Shift in the Attack Surface

### 2.1 Identity is the New Perimeter
On-premises environments usually have a distinct inside and outside, separated by firewalls, DMZs, and VPNs. If an attacker wants to compromise a server, they must often traverse the network. In the cloud, the management plane (the APIs used to configure and manage the cloud) is exposed to the internet by design. 
If an attacker compromises an IAM credential (e.g., an AWS Access Key or Azure Service Principal), they can directly access the control plane from anywhere in the world, bypassing all network-level security controls (unless specific conditions like IP restrictions are enforced in IAM policies).

### 2.2 Abstraction of Infrastructure
Cloud environments abstract the underlying hardware and network. You do not have access to the physical switch or the hypervisor. This means:
- You cannot tap a port for raw PCAP in the same way (though features like VPC Traffic Mirroring exist, they are rarely deployed globally).
- You rely on provider-generated logs (e.g., VPC Flow Logs) which sample traffic and only provide metadata (IPs, ports, bytes transferred, accept/reject status), not packet payloads.
- Storage is abstracted into services like S3 or Azure Blob Storage, meaning you cannot do traditional digital forensics (disk imaging) on a storage bucket.

### 2.3 Ephemerality
On-premises servers often live for years. Cloud instances (EC2, VMs) might live for hours or minutes. Serverless functions (Lambda, Azure Functions) live for milliseconds. Containers orchestrate up and down continuously.
When an incident occurs on-premises, a forensic investigator can often pull the plug on a physical machine and image its drive. In the cloud, if a compromised container or auto-scaled VM is terminated, the evidence is gone forever unless continuous logging and automated snapshotting mechanisms were already in place.

## 3. Architecture Visualization: The Paradigm Shift

```text
+---------------------------------------------------------+
|                ON-PREMISES ARCHITECTURE                 |
|                                                         |
|  [Internet]                                             |
|      |                                                  |
|  [Firewall / WAF] <--- Network Perimeter                |
|      |                                                  |
|   +--+--+       +-------+                               |
|   | DMZ |-------| Web 1 |                               |
|   +--+--+       +-------+                               |
|      |                                                  |
|  [Internal FW]                                          |
|      |                                                  |
|   +--+--+       +-------+     +----------+              |
|   | LAN |-------| App 1 |-----| Active   |              |
|   +--+--+       +-------+     | Directory|              |
|                               +----------+              |
|                                                         |
|  Hunting Focus: PCAP, EDR, Windows Event Logs, Sysmon.  |
+---------------------------------------------------------+

                             VS

+---------------------------------------------------------+
|                  CLOUD ARCHITECTURE                     |
|                                                         |
|               [ Cloud Management APIs ]                 |
|               (AWS/Azure/GCP Endpoints)                 |
|                           ^                             |
|                           |                             |
|  [Internet] -----> [ IAM & Policies ] <--- NEW PERIMETER|
|                           |                             |
|      +--------------------+--------------------+        |
|      |                    |                    |        |
|  [Serverless]    [Ephemeral Compute]     [Managed DB]   |
|  (Lambda)        (EC2 Auto-Scaling)      (RDS/SQL)      |
|                                                         |
|                                                         |
|  Hunting Focus: API Logs (CloudTrail), IAM Audits,      |
|                 VPC Flow Logs, Cloud Native CSPM.       |
+---------------------------------------------------------+
```

## 4. Telemetry and Data Sources Comparison

Understanding mapping between on-premises logs and their cloud equivalents is critical for threat hunters.

### 4.1 Network Telemetry
- **On-Premises:** Full Packet Capture (PCAP), Zeek/Bro logs, Cisco NetFlow, firewall traffic logs.
- **Cloud:** AWS VPC Flow Logs, Azure Network Security Group (NSG) Flow Logs, GCP VPC Flow Logs.
- **Hunter's Adjustment:** Cloud flow logs are mostly metadata. You cannot inspect the payload for SQLi or malware signatures. You must rely on volumetric analysis, unusual port communications, and connections to known malicious IPs or Tor nodes.

### 4.2 Host and Execution Telemetry
- **On-Premises:** Sysmon (Event ID 1 Process Creation), Windows Event Logs (4688), Linux auditd, EDR.
- **Cloud:** While VMs still run these, cloud-native services rely on completely different logs. For serverless (AWS Lambda), you rely on CloudWatch Logs. For container orchestration, you rely on EKS/AKS audit logs (Kubernetes API logs).
- **Hunter's Adjustment:** You must monitor the control plane for instance creation/modification. A process creation on-prem is roughly equivalent to a `RunInstances` or `CreateFunction` API call in the cloud.

### 4.3 Identity and Authentication Telemetry
- **On-Premises:** Active Directory Domain Controller logs (Event ID 4624 Logon, 4768 TGT Request).
- **Cloud:** AWS CloudTrail, Azure Entra ID (formerly Azure AD) Sign-in Logs, GCP Cloud Audit Logs.
- **Hunter's Adjustment:** In the cloud, nearly every action is an API call authenticated via IAM. CloudTrail is the ultimate source of truth in AWS. An attacker doesn't need to "log on" to a machine; they issue an API request signed with a stolen Access Key. 

## 5. Hunting Methodologies: The API Centric Approach

Because the cloud is driven by APIs, hunting strategies must revolve around understanding API behavioral patterns.

1. **User-Agent Analysis:** Cloud APIs are accessed via tools. Common user agents include `aws-cli/2.0`, `Boto3`, `Terraform`, or standard browser agents. If an IAM user typically uses `Boto3` (a Python script) from a corporate IP, and suddenly the same user issues `ConsoleLogin` from a residential ISP, it is highly suspicious.
2. **Geo-Location and ASN Analysis:** While useful on-prem, this is vital in the cloud. Access keys can be used from anywhere. If an access key normally operates from the `us-east-1` region (if it's an EC2 role) and suddenly makes requests from a VPN exit node in another country, an investigation is warranted.
3. **Error Rate Analysis:** Attackers who steal credentials often do not know what permissions the credentials have. They will run enumeration scripts (like Pacu, ScoutSuite, or Cloudsplaining). This generates massive amounts of `AccessDenied` or `UnauthorizedOperation` errors in CloudTrail. Hunting for spikes in `AccessDenied` events grouped by `userIdentity.arn` is a primary cloud hunting technique.

## 6. Real-World Attack Scenario

### 6.1 The Scenario: Capital One-Style SSRF to IAM Exfiltration
A classic example demonstrating the difference between on-prem and cloud attacks.

1. **Initial Access (The Web App):** An attacker finds a Server-Side Request Forgery (SSRF) vulnerability in a web application hosted on an AWS EC2 instance. On-premises, an SSRF might be used to scan the internal network (192.168.x.x) or hit internal administration panels.
2. **Cloud Specific Pivot (IMDS):** In AWS, the attacker uses the SSRF to query the Instance Metadata Service (IMDS) located at the unroutable IP `169.254.169.254`. 
3. **Credential Theft:** The attacker queries `http://169.254.169.254/latest/meta-data/iam/security-credentials/WebRole`. The AWS infrastructure responds with temporary credentials (AccessKeyId, SecretAccessKey, and a SessionToken) meant ONLY for that specific EC2 instance.
4. **Exfiltration & Abuse (Control Plane):** The attacker extracts these credentials and configures them on their local machine via the AWS CLI. They are now operating on the AWS Management Plane from outside the network.
5. **Impact:** The attacker uses the `WebRole` to run `aws s3 sync s3://customer-data-bucket ./local-dir`, exfiltrating gigabytes of data.

### 6.2 The Hunting Perspective
If a hunter were using traditional on-prem techniques, they would only see HTTP traffic to the web application. They would miss the entirely out-of-band exfiltration.

**Cloud Hunting Steps for this scenario:**
1. **Analyze CloudTrail:** Search for the API call `GetCallerIdentity` or `ListBuckets` originating from the `WebRole`. 
2. **Identify the Anomaly:** The `WebRole` is assigned to an EC2 instance. Therefore, legitimate API calls using this role's temporary credentials MUST originate from an AWS public IP address belonging to that specific EC2 instance (or NAT gateway).
3. **The Smoking Gun:** If CloudTrail shows an API call made by `WebRole` originating from an IP address OUTSIDE of AWS (e.g., a residential ISP or a VPN provider), those credentials have been exfiltrated and are being used externally. 

## 7. Operationalizing the Hunt: Query Examples

### Splunk Search: Hunting for Exfiltrated IAM Roles
This query looks for temporary credentials (roles) being used from IP addresses that do not belong to the organization's known AWS IP ranges.

```splunk
index=aws_cloudtrail eventType=AwsApiCall 
| search userIdentity.type=AssumedRole
| lookup known_aws_ips ip AS sourceIPAddress OUTPUT is_aws_ip
| where is_aws_ip="false"
| stats count by sourceIPAddress, userIdentity.arn, eventName, awsRegion
| sort - count
```

### KQL (Azure Sentinel): Hunting for Unusual Service Principal Usage
This looks for an Azure Service Principal (the equivalent of an IAM role) signing in from a new geographic location or anomalous IP.

```kql
AADServicePrincipalSignInLogs
| where TimeGenerated > ago(7d)
| summarize dcount(IPAddress) by ServicePrincipalId, ServicePrincipalName
| where dcount_IPAddress > 1
| join kind=inner (
    AADServicePrincipalSignInLogs
    | where TimeGenerated > ago(1d)
) on ServicePrincipalId
| project TimeGenerated, ServicePrincipalName, IPAddress, LocationDetails
```

## 8. Chaining Opportunities
- **[[02 - AWS CloudTrail Analysis for Persistence]]**: Once an attacker compromises the control plane, their next step is to establish persistence, which can be tracked in CloudTrail.
- **[[03 - Hunting for Compromised IAM Credentials in AWS]]**: A deeper dive into how credentials leak and how to hunt for their initial abuse.
- **[[05 - Azure Activity Logs and Entra ID Sign-in Logs]]**: Applying these concepts specifically to the Azure ecosystem.

## 9. Related Notes
- [[IAM Privilege Escalation Techniques]]
- [[Capital One Breach Analysis]]
- [[Server-Side Request Forgery (SSRF) in Cloud]]
- [[Instance Metadata Service (IMDS) Version 1 vs 2]]
