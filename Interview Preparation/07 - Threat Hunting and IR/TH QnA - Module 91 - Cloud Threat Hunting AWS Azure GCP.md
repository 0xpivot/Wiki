---
tags: [interview, threat-hunting, ir, qna, scenario]
difficulty: expert
module: "Interview Prep - Threat Hunting and IR"
topic: "QnA - TH Module 91"
---

# Threat Hunting QnA: Cloud Threat Hunting (AWS, Azure, GCP)

## Formal Technical Questions

### Q1: Explain the differences between AWS CloudTrail, Azure Activity Logs, and GCP Cloud Audit Logs from a threat hunting perspective. How do you handle multi-cloud log normalization?
**Expert Answer:**
Threat hunting across multi-cloud environments requires a deep understanding of how each provider logs control plane and data plane events, as well as the idiosyncrasies of their respective schemas.
*   **AWS CloudTrail:** 
    *   Logs AWS API calls. Control plane events are logged by default. 
    *   Data plane events (e.g., S3 object-level logging, Lambda executions, DynamoDB item queries) must be explicitly enabled and incur additional costs. 
    *   The `userIdentity` element is critical. Hunters must parse `arn`, `accountId`, `type` (e.g., AssumedRole, IAMUser), and `sessionContext` to trace back an `AssumeRole` event to the original identity. 
    *   A massive challenge in AWS is tracking cross-account trust abuses where the `userIdentity` reflects the assumed role, but the source origin must be traced back through chained role assumptions.
*   **Azure Activity Logs:** 
    *   Captures subscription-level events (control plane), such as resource modifications, role assignments, and VM spin-ups. 
    *   However, it does *not* include Azure AD (Entra ID) audit logs (which contain sign-ins, MFA changes, and SPN modifications) or resource-specific data plane logs. Diagnostic Settings must be manually configured to send these to a Log Analytics Workspace or SIEM.
    *   Azure logs are heavily nested JSON objects containing `claims` arrays that need to be unrolled to find the actual Service Principal or User Principal Name executing the action.
*   **GCP Cloud Audit Logs:** 
    *   Categorized into Admin Activity, Data Access, System Event, and Policy Denied logs. 
    *   Admin Activity is on by default. Data Access is highly granular but off by default due to high volume. 
    *   GCP's log structure is strictly JSON and deeply nested (e.g., `protoPayload.authenticationInfo.principalEmail`), making it strongly typed but complex to query without unnesting operations in BigQuery or a SIEM.
*   **Normalization Strategy:** 
    *   To hunt effectively across all three, telemetry must be normalized into a standard schema like OCSF (Open Cybersecurity Schema Framework) or Elastic ECS. 
    *   Critical unified fields include: `Source_IP`, `Normalized_Identity` (mapping AWS ARN, Azure UPN, GCP Principal), `Action` (Create, Update, Delete, Read), `Resource_Type`, and `Outcome`.
    *   Without normalization, a hunter looking for "user creation" has to query `CreateUser` in AWS, `Add user` in Entra ID, and `google.admin.AdminService.insertUser` in GCP.

### Q2: Detail the indicators of compromise (IoCs) and behavioral indicators for an Azure AD "Golden SAML" attack. How would you hunt for it?
**Expert Answer:**
A Golden SAML attack occurs when an adversary steals the token-signing certificate from an Active Directory Federation Services (AD FS) server and forges SAML tokens to bypass authentication to Azure AD (now Entra ID). This allows them to impersonate *any* federated user.
*   **Indicators:** Traditional IoCs like IP addresses are often useless here because the attacker can present the forged token from anywhere, assuming conditional access does not block them.
*   **Hunting Methodology:**
    1.  **Immutable ID Analysis:** Hunt for logins where the `ImmutableID` does not map to a known, valid synced user, or where a high-privileged cloud-only account is suddenly logging in via a federated token. Legitimate federation requires the AD FS user and Azure AD user to match via this ID.
    2.  **MFA Bypass Anomalies:** Look in the Azure AD Sign-in logs for events where `Authentication Requirement` is satisfied by `Single-factor authentication` when the policy dictates MFA.
    3.  **Claim Verification:** Inspect the `AuthenticationDetails` array. If the claim shows the authentication came from the identity provider (meaning MFA was allegedly done on-prem) but no corresponding on-prem MFA log exists in the RADIUS/AD FS logs for that timestamp, the token is forged.
    4.  **AD FS Telemetry (On-Prem):** On the AD FS servers (Event ID 411, 501, 1200), hunt for anomalous export of the DKM (Distributed Key Manager) master key from the AD container, or abnormal LSASS access on the AD FS server indicating certificate extraction via tools like Mimikatz or ADFSpoof.
    5.  **Token Lifespan Anomalies:** Attackers often forge SAML tokens with highly extended expiration times. Hunting for tokens valid for days instead of standard hour intervals can reveal forged assertions.

## Scenario-Based Questions

### Q3: You are a senior incident responder. A highly privileged AWS EC2 instance was found mining cryptocurrency. You suspect the initial access vector was Server-Side Request Forgery (SSRF) to the Instance Metadata Service (IMDS). Walk me through your entire hunting and investigation lifecycle.
**Expert Answer:**
**Phase 1: Verification and Containment**
*   Immediately isolate the EC2 instance using a Security Group that denies all inbound and outbound traffic, except for IR forensic IP ranges. 
*   Snapshot the EBS volume and capture memory if the instance is still running (using tools like LiME or AWS Systems Manager Run Command).
*   Review VPC Flow Logs to identify command and control (C2) or mining pool communications. Document the outbound IP addresses.

**Phase 2: Tracing the SSRF & IMDS Abuse**
*   If IMDSv1 was in use, any process could query `http://169.254.169.254/latest/meta-data/iam/security-credentials/<role-name>` without a challenge-response token.
*   I would pull the web application access logs from the EC2 instance (e.g., Nginx, Apache) to look for anomalies, specifically URL parameters containing the IMDS IP or encoded variations (e.g., `http://169.254.169.254`, `http://[::ffff:169.254.169.254]`, `http://2852039166`). Look for GET/POST requests returning anomalous HTTP 200s or large payload sizes.
*   Identify the IAM role assigned to the instance via the AWS Management Console or CLI (`aws ec2 describe-instances`).

**Phase 3: CloudTrail Analysis for Credential Abuse**
*   In CloudTrail, I would filter for the extracted IAM Role name. The critical event is `AssumeRole`. 
*   If the attacker stole the credentials and used them outside AWS, CloudTrail will show API calls (e.g., `RunInstances`, `GetCallerIdentity`) originating from an IP address outside of the expected VPC or corporate NAT IP. 
*   The mismatch between the `sourceIpAddress` in CloudTrail and the expected EC2 instance IP is the smoking gun that the credential was exfiltrated and used remotely.

**Phase 4: Impact Analysis & Remediation**
*   Determine what other API calls the attacker made using the stolen session token. Did they enumerate S3 buckets (`ListBuckets`, `GetObject`)? Did they modify IAM policies (`PutUserPolicy`, `AttachRolePolicy`) to create a backdoor?
*   Remediation involves:
    1.  Rotating the compromised IAM role by detaching the old policies, revoking active sessions, and applying temporary explicit Deny policies.
    2.  Forcing the transition to IMDSv2 (which requires a PUT request to get a token with a TTL, effectively neutralizing simple SSRF).
    3.  Patching the underlying web application SSRF vulnerability.

### Q4: In GCP, an attacker has compromised a developer's local credentials via malware and is attempting to escalate privileges to Organization Administrator. How do you hunt for GCP IAM enumeration and privilege escalation?
**Expert Answer:**
*   **Enumeration Hunting:** Attackers using tools like `GCPBucketBrute` or `ScoutSuite` generate specific log patterns. I will query Cloud Audit Logs for high volumes of `testIamPermissions`, `getIamPolicy`, and `list` operations across multiple projects within a short timeframe originating from a single `principalEmail`.
*   **Privilege Escalation:** The attacker will likely attempt to modify IAM policies. I would hunt for the `SetIamPolicy` method on critical resources. Specifically, I'm looking for the addition of roles like `roles/editor`, `roles/owner`, or `roles/iam.securityAdmin` to user accounts or service accounts (`iam.serviceAccounts.actAs`).
*   **Anomaly Detection:** Use statistical analysis to detect an anomaly in the `userAgent`. Developer SDKs have specific user agents (e.g., `google-cloud-sdk`, `google-api-go-client`). If a generic `python-requests`, `curl`, or a completely unknown user agent suddenly executes `SetIamPolicy`, this warrants immediate investigation.
*   **Service Account Abuse:** If they pivot to a service account (by downloading the JSON key or using impersonation), the `authenticationInfo.serviceAccountDelegationInfo` array in the audit logs will reveal the chain of impersonation. I would hunt for long chains or unexpected cross-project impersonation where a low-level Dev service account suddenly generates a token for an infrastructure deployment service account.

## Deep-Dive Defensive Questions

### Q5: How do you detect and mitigate persistent backdoors created in cloud environments, specifically focusing on AWS Lambda and Azure Automation Runbooks?
**Expert Answer:**
Attackers increasingly use Serverless and PaaS offerings for persistence because they are rarely monitored by traditional EDR solutions and can blend into normal administrative automation.
*   **AWS Lambda Backdoors:**
    *   **Detection:** Hunt for `CreateFunction`, `UpdateFunctionCode`, or `UpdateFunctionConfiguration` in CloudTrail executed by unusual identities or at unusual times. Look for Lambda functions that have broad IAM execution roles attached (e.g., `AdministratorAccess`). Monitor for triggers added via `AddPermission` that allow external invocation (e.g., via a publicly accessible API Gateway, or an open Function URL). Analyze the Lambda code itself for remote execution shells, reverse shell logic, or excessive `boto3` calls.
    *   **Mitigation:** Enforce strict IAM boundaries. Lambda roles should have absolute least privilege. Implement SCPs (Service Control Policies) to prevent the creation of IAM roles that have excessive permissions, and prevent the usage of `lambda:AddPermission` to unapproved external principals.
*   **Azure Automation Runbooks:**
    *   **Detection:** Attackers can create Hybrid Runbook Workers to execute code on-prem or create cloud-only runbooks to manipulate Azure resources continuously. Hunt in Azure Activity logs for `Microsoft.Automation/automationAccounts/runbooks/write`. Examine the execution logs of runbooks for anomalous PowerShell or Python scripts, particularly those utilizing the `Az` module to enumerate Azure AD, export configurations, or manipulate Key Vaults. Look for runbooks triggered by unauthorized webhooks.
    *   **Mitigation:** Use Azure RBAC to heavily restrict who can create or modify Automation Accounts and Runbooks. Monitor Managed Identities assigned to these Automation Accounts, ensuring they do not have excessive Subscription or Tenant-level permissions. Audit Automation Account variables and credentials for unauthorized additions.

## Custom ASCII Diagram: Cloud Identity Attack Path

```text
+-------------------+       +-----------------------+       +-------------------+
| Attacker Machine  |       | Compromised EC2 (Web) |       | AWS IAM Service   |
| IP: 203.0.113.50  | ===>  | IP: 10.0.1.25         | ===>  | (Control Plane)   |
+-------------------+       | Role: App-Web-Role    |       +-------------------+
        |                   +-----------------------+               |
        | 1. SSRF via               | 2. Curl to IMDS               | 3. Returns
        |    vulnerable param       |    169.254.169.254            |    AccessKeyId,
        |    (?url=http://...)      |    requesting creds           |    SecretAccessKey,
        |                           v                               |    SessionToken
        |                   +-----------------------+               |
        |<================= | Metadata API          |<==============+
        | 4. Returns stolen | (IMDSv1)              |
        |    IAM credentials+-----------------------+
        v
+-------------------+
| Attacker Machine  | 5. AWS CLI configuration
| Configures AWS CLI|    with stolen credentials
| with stolen creds |
+-------------------+
        |
        | 6. aws s3 ls (Execution from outside AWS)
        v
+-------------------+
| AWS API Endpoint  | 7. CloudTrail logs request.
| (s3.amazonaws.com)|    *Anomaly Detection*: sourceIpAddress is 203.0.113.50
| Validates token   |    (Attacker IP), NOT the EC2 instance IP (10.0.1.25).
+-------------------+    *Alert Triggered*: Credentials used outside expected VPC.
```

## Real-World Attack Scenario
**The LAPSUS$ Style Cloud Extortion and Extortion Playbook**
An advanced threat group gained initial access via an outsourced support engineer's credentials, bypassing MFA via an "MFA Fatigue" (prompt bombing) attack late at night.
Once inside the Azure AD environment, they enumerated Global Administrators and discovered an unsecured Azure Logic App that had a system-assigned managed identity with `Owner` rights over the main production subscription.
They modified the Logic App to execute a REST API call that created a new persistent backdoor Service Principal and granted it Global Admin rights. They then proceeded to exfiltrate massive amounts of source code from Azure DevOps, delete production databases, and leave extortion notes within Azure Storage blobs.
**Hunting focus:** The critical hunting pivot is identifying the modification of the Logic App (`Microsoft.Logic/workflows/write`) and the subsequent Role Assignment creation (`Microsoft.Authorization/roleAssignments/write`) by a non-human identity acting abnormally. Advanced hunting requires correlating the MFA fatigue indicators in Sign-In logs with the immediate subsequent anomalous Logic App manipulation.

## Chaining Opportunities
*   Cloud compromised credentials often lead directly to **Lateral Movement** into on-prem environments if hybrid infrastructure is configured (e.g., Azure AD Connect, AWS Direct Connect, Hybrid Runbook Workers).
*   Data exfiltration in the cloud heavily involves Object Storage (S3, Azure Blob). Chaining identity access anomalies with massive egress patterns (Network/VPC Flow logs) or excessive `GetObject` calls is a core strategy.
*   Cross-tenant access abuse in Azure B2B relationships is a frequent chaining method for attackers looking to pivot from a compromised vendor to a target organization.

## Related Notes
*   [[08 - AWS IAM Privilege Escalation Vectors]]
*   [[12 - Detecting MFA Abuse and Token Theft]]
*   [[45 - Azure AD Entra ID Deep Dive for Hunters]]
*   [[55 - Server-Side Request Forgery Advanced Exploitation]]
*   [[67 - Exploiting and Defending AWS IMDSv1 vs IMDSv2]]
*   [[88 - OCSF and Elastic ECS Log Normalization Strategies]]
