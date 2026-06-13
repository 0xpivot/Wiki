---
tags: [cloud-security, defense, iam, imdsv2, cloudtrail, scp, guardrails]
difficulty: advanced
module: "37 - Cloud Infrastructure"
topic: "37.35 Defense"
---

# Cloud Defense: Least Privilege, IMDSv2, Logging, and SCPs

## 1. Introduction to Modern Cloud Security Architecture
Defending a cloud environment requires a fundamental paradigm shift from traditional perimeter-based security (firewalls, IDS/IPS) to identity-centric security. In the cloud, the API is the perimeter, and Identity is the firewall.
A robust, mature cloud defense strategy operates on multiple interlocking layers: preventive guardrails, secure default configurations, extremely granular access control, and comprehensive visibility. This note focuses extensively on the four foundational pillars of AWS/Cloud defense.

## 2. Defensive Architecture Overview

### ASCII Diagram: Multi-Layered Cloud Defense

```text
+-----------------------------------------------------------------+
|                      AWS Organizations                          |
|                                                                 |
|  [ SCPs: Preventive Guardrails - The Absolute Ceiling ]         |
|  (e.g., Explicitly Deny all access outside approved regions)    |
|                                                                 |
|   +-----------------------+       +-----------------------+     |
|   | Account: Production   |       | Account: SecOps       |     |
|   |                       |       |                       |     |
|   | +-------------------+ | Logs  | +-------------------+ |     |
|   | | EC2 Workloads     |---------+ | Centralized       | |     |
|   | | (IMDSv2 Enforced) | |       | | S3 Log Bucket     | |     |
|   | +-------------------+ |       | | (WORM Protected)  | |     |
|   |                       |       | +-------------------+ |     |
|   | +-------------------+ |       |                       |     |
|   | | IAM Policies      | |       | +-------------------+ |     |
|   | | (Least Privilege) | |       | | SIEM / GuardDuty  | |     |
|   | +-------------------+ |       | | Threat Detection  | |     |
|   +-----------------------+       +-----------------------+     |
+-----------------------------------------------------------------+
```

## 3. Pillar 1: Service Control Policies (SCPs)
SCPs are the ultimate preventive guardrails in an AWS Organization. They do not grant permissions; instead, they set the absolute maximum boundaries for what is permitted. If an SCP denies an action, **no entity** in the account (not even the root user or an Administrator) can perform that action.

**Critical Use Cases for SCPs:**
- **Region Restriction:** Deny all API calls to regions where the company does not operate. This severely mitigates the impact of stolen credentials being used to spin up expensive crypto-miners in obscure regions.
- **Protecting Security Tooling:** Explicitly deny the ability to stop CloudTrail logging, disable GuardDuty, or delete central S3 log buckets.
- **Preventing Root User Usage:** Deny all actions by the `root` user, forcing absolute reliance on federated, trackable identities.

**Example SCP: Prevent Disabling CloudTrail**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Deny",
      "Action": [
        "cloudtrail:StopLogging",
        "cloudtrail:DeleteTrail",
        "cloudtrail:DisableAWSServiceAccess"
      ],
      "Resource": "*"
    }
  ]
}
```

## 4. Pillar 2: Least Privilege IAM
While SCPs provide macro-level defense, IAM policies provide micro-level access control. The Principle of Least Privilege dictates that identities (users, roles, pipelines) should only possess the exact permissions necessary to perform their function, and nothing more.

**Advanced Best Practices:**
- **Eradicate Wildcards (`*`):** Never use `Action: "*"` or `Resource: "*"`. Instead of `s3:*` on `*`, explicitly use `s3:GetObject` on `arn:aws:s3:::my-specific-bucket/images/*`.
- **Leverage Condition Keys:** Conditions enforce rigid *context* around an API call.
  - `aws:SourceIp`: Restrict highly privileged actions so they can only be executed from corporate VPN IP addresses.
  - `aws:PrincipalTag`: Implement Attribute-Based Access Control (ABAC), allowing access only if the user's tag dynamically matches the resource's tag.
- **IAM Access Analyzer:** Utilize automated reasoning tools to mathematically prove whether resource policies inadvertently grant public or cross-account access, fundamentally preventing [[32 - Cloud Storage Mining]] and [[34 - Cloud Backdoor via IAM Role]].

## 5. Pillar 3: IMDSv2 Enforcement
The Instance Metadata Service (IMDS) provides EC2 instances with vital configuration data and, most importantly, temporary IAM credentials based on their attached role. IMDSv1 was highly susceptible to Server-Side Request Forgery (SSRF) attacks, where a vulnerability in a web app could be exploited to extract these cloud credentials.

**How IMDSv2 Defeats SSRF:**
IMDSv2 introduces highly secure session-oriented requests. 
1. The client must first send a `PUT` request with a specific, custom header (`X-aws-ec2-metadata-token-ttl-seconds`) to obtain a token.
2. The client then utilizes this token in subsequent `GET` requests to retrieve credentials.
Most SSRF vulnerabilities (e.g., tricking a PDF generator or a proxy into fetching a URL) only allow simple `GET` requests and cannot manipulate HTTP methods or inject custom headers. Therefore, IMDSv2 almost completely eradicates standard SSRF credential extractions.

**Defense Implementation:**
Enforce IMDSv2 globally using an SCP, and ensure all instances are launched with `HttpTokens` set to `required`.
```bash
aws ec2 modify-instance-metadata-options \
    --instance-id i-1234567890abcdef0 \
    --http-tokens required \
    --http-endpoint enabled
```

## 6. Pillar 4: Logging, Visibility, and Threat Detection

Without comprehensive logs, the cloud is a black box. Post-breach incident response is practically impossible without a continuous, immutable audit trail.

### A. AWS CloudTrail
CloudTrail rigorously records every single API call made in the account (Who made the call, from what IP, at what precise time, and what resources were affected).
- **Mandatory Configuration:** CloudTrail must be enabled across all regions, centralized into an isolated, tamper-proof SecOps AWS account, and protected with S3 Object Lock (WORM - Write Once Read Many) to prevent attacker tampering.

### B. Amazon GuardDuty
GuardDuty is a highly advanced managed threat detection service that analyzes CloudTrail logs, VPC Flow Logs, and DNS logs utilizing machine learning and proprietary threat intelligence feeds.
It detects active compromise instantly, such as:
- Credentials being used from anomalous IP addresses (e.g., an EC2 role being used from a residential IP, indicating extraction via SSRF).
- EC2 instances querying known command-and-control (C2) servers or mining pools.
- S3 bucket discovery and anomalous data exfiltration.

### C. Cloud Security Posture Management (CSPM)
Deploy tools like AWS Security Hub, Checkov, or Wiz to continuously, automatically scan the environment against strict compliance frameworks (e.g., CIS Foundations Benchmark). This ensures misconfigurations (like public S3 buckets or open Security Groups) are detected and remediated immediately before exploitation.

## 7. Chaining Opportunities
- Implementing these structural defenses directly breaks the attack chains described in [[34 - Cloud Backdoor via IAM Role]] (by enforcing SCPs) and [[31 - Kubernetes on Cloud — EKS, GKE, AKS]] (by rigorously enforcing IMDSv2).
- Proper logging ensures that the reconnaissance and enumeration phases of [[32 - Cloud Storage Mining]] are detected early, allowing defenders to respond before data exfiltration occurs.

## 8. Related Notes
- [[34 - Cloud Backdoor via IAM Role]]
- [[32 - Cloud Storage Mining]]
- [[30 - Terraform CloudFormation Misconfigurations]]
- [[31 - Kubernetes on Cloud — EKS, GKE, AKS]]
