---
tags: [interview, cloud-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Cloud Security"
topic: "QnA - Cloud Module 79"
---

# Advanced Cloud Security Architecture Interview Questions

## Custom ASCII Architecture Diagram
```text
                     +---------------------------------------+
                     |         Cloud Provider (AWS/GCP/Azure)|
                     |                                       |
  +----------+       |  +----------------+                   |
  | Attacker |=======>  | Compromised VM |                   |
  +----------+ SSRF  |  | (Limited Role) |                   |
                     |  +-------+--------+                   |
                     |          | 1. Query Metadata          |
                     |          v                            |
                     |  +----------------+                   |
                     |  |  IMDS / Token  |                   |
                     |  |  Service       |                   |
                     |  +-------+--------+                   |
                     |          | 2. Extract STS / JWT Token |
                     |          v                            |
                     |  +----------------+    3. PassRole    +----------------+
                     |  | IAM Role 'A'   |==================>| Admin IAM Role |
                     |  | (Developer)    |    (PrivEsc)      | (FullAccess)   |
                     |  +----------------+                   +----------------+
                     |                                               |
                     |                                               | 4. Cross-Account AssumeRole
                     |                                               v
                     |                                       +----------------+
                     |                                       | Production Env |
                     |                                       | (Target Data)  |
                     +---------------------------------------+----------------+
```

## Formal Technical Questions

**Q1: Explain the exact evaluation logic of AWS IAM policies, including the interplay between Service Control Policies (SCPs), Resource-Based Policies, IAM Permissions Boundaries, and Identity-Based Policies. What happens if a Resource-Based policy grants access, but an SCP explicitly denies it?**
**A1:** The evaluation of AWS IAM policies is a highly deterministic process that follows a strict flow to determine if a request is `Allowed` or `Denied`. The fundamental principle is that **default deny** applies unless explicitly allowed, but an **explicit deny** overrides any allow.
1.  **Deny Evaluation:** The engine first checks all applicable policies for an explicit `Deny`. This includes SCPs (applied at the Organization/OU level), Resource-based policies (e.g., S3 bucket policies), Identity-based policies (attached to the IAM user/role), Permissions Boundaries, and Session Policies. If *any* of these contain a `Deny` matching the request context, the request is immediately denied.
2.  **SCP Evaluation:** If no explicit deny is found, AWS checks the SCPs. If the account is governed by an SCP, the specific action must be explicitly allowed by the SCP. If the SCP does not allow it (even implicitly), the request is denied.
3.  **Resource-Based Policy Evaluation:** AWS then checks the resource-based policy. If the resource-based policy explicitly allows the action, and the principal is in the same account, the request is **Allowed**, even if the identity-based policy doesn't explicitly allow it (provided no bounds/SCPs block it). For cross-account access, *both* the resource-based policy of the target and the identity-based policy of the caller must allow the action.
4.  **Permissions Boundary & Session Policies:** If the action isn't allowed by a same-account resource policy, AWS checks if a Permissions Boundary or Session Policy is attached. These act as filters; the action must be allowed by both the boundary/session policy *and* the identity-based policy.
5.  **Identity-Based Policy:** Finally, AWS checks the identity-based policy. If it explicitly allows the action, the request succeeds. Otherwise, it defaults to deny.
*Scenario Answer:* If a Resource-Based policy explicitly grants access but an SCP explicitly denies it, the **SCP wins**. The explicit `Deny` in the SCP acts as an organizational-level guardrail that supersedes all other localized allows.

**Q2: In Google Cloud Platform (GCP), explain how role inheritance works across the Resource Hierarchy and how an attacker might abuse overlapping IAM bindings at different nodes (Organization, Folder, Project, Resource).**
**A2:** GCP's resource hierarchy is structured as Organization -> Folders -> Projects -> Resources. IAM policies in GCP are inherited downwards. This means a role binding applied at the Organization level automatically propagates to all Folders, Projects, and Resources beneath it.
Crucially, **allow policies cannot be overridden by deny policies at a lower level** in standard IAM (though GCP recently introduced IAM Deny policies to address this, traditional IAM operates purely on additive allows). 
An attacker abuses this by targeting identities that have high-level bindings. For example, if a Service Account is granted `roles/editor` at the Folder level, it has edit rights to every project within that folder. If an attacker compromises a VM in Project A (dev) and extracts a Service Account token that was lazily granted permissions at the Folder level instead of the Project level, the attacker can use that token to pivot laterally into Project B (prod) within the same folder. Attackers will actively enumerate the ancestor bindings using `gcloud projects get-iam-policy` and `gcloud asset search-all-iam-policies` to identify cross-project blast radii.

**Q3: Describe the mechanics of an Azure Active Directory (Entra ID) Primary Refresh Token (PRT). How is it generated, and how can an attacker steal or abuse it on a compromised endpoint to bypass MFA?**
**A3:** A Primary Refresh Token (PRT) is a crucial artifact in Azure AD/Entra ID for achieving Single Sign-On (SSO) across Windows, iOS, and Android devices. On Windows 10/11, when a device is Azure AD Joined or Hybrid Joined, the CloudAP authentication package authenticates the user with Azure AD and receives a PRT.
The PRT is fundamentally a JSON Web Token (JWT), but it is heavily protected. It contains a device claim and a session key. The cryptographic material (the session key) used to sign requests proving possession of the PRT is stored in the TPM (Trusted Platform Module) or isolated via virtualization-based security (VBS). Therefore, simply copying the PRT string from disk or memory isn't enough; you cannot easily exfiltrate the TPM-bound private key.
**Attacker Abuse:**
Instead of stealing the PRT directly, advanced attackers abuse the operating system APIs that interact with the PRT. Using tools like `Mimikatz` (specifically the `dpapi::cloudap` module) or `ROADtoken`, an attacker with SYSTEM privileges on a compromised host can request the CloudAP plugin to use the TPM to cryptographically sign a new authentication request on their behalf.
Because the PRT already contains an MFA claim (from when the user originally logged into the Windows machine), the attacker can request new access tokens for Azure resources (like Exchange Online or Azure Resource Manager) using this PRT. The newly minted access tokens will inherit the MFA claim, effectively bypassing conditional access policies requiring MFA, allowing the attacker to interact with cloud environments directly from the compromised machine (or by passing the derived tokens).

## Scenario-Based Questions

**Scenario 1:** You are conducting a Red Team engagement. You have achieved Remote Code Execution (RCE) on a standalone Linux EC2 instance. The instance is running IMDSv2 (Instance Metadata Service Version 2) in a strictly enforced manner (hop limit is 1). You need to dump the attached IAM role credentials to pivot further into the AWS environment.
**Q:** Walk through the exact technical steps and commands to retrieve the temporary credentials from IMDSv2, explaining why IMDSv2 requires these specific steps compared to IMDSv1.
**A:** IMDSv2 mitigates traditional Server-Side Request Forgery (SSRF) and simple `curl` extractions by requiring a session token (via a `PUT` request) before any metadata can be read. The hop limit of 1 also prevents the token from being requested through network proxies or certain container networking setups that decrement the TTL.
Since I have RCE on the instance (an interactive shell), the hop limit of 1 is not a barrier (my requests originate locally). The steps are:
1.  **Generate the IMDSv2 Session Token:** I must send a `PUT` request with a specific header specifying the TTL (Time To Live) for the token.
    ```bash
    TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" -H "X-aws-ec2-metadata-token-ttl-seconds: 21600")
    ```
2.  **Enumerate the attached IAM Role Name:** Using the obtained token, I send a `GET` request to list the IAM roles associated with the instance profile.
    ```bash
    curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/iam/security-credentials/
    ```
    *(Assume this returns `web-app-role`)*
3.  **Extract the Credentials:** I query the specific role to get the `AccessKeyId`, `SecretAccessKey`, and `Token`.
    ```bash
    curl -s -H "X-aws-ec2-metadata-token: $TOKEN" http://169.254.169.254/latest/meta-data/iam/security-credentials/web-app-role
    ```
These credentials can then be exported into my local environment variables (`AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN`) allowing me to run `aws cli` commands as the `web-app-role` identity.

**Scenario 2:** After dumping the credentials from the EC2 instance in Scenario 1, you attempt to run `aws ec2 describe-instances`, but you receive an `AccessDenied` error. However, running `aws sts get-caller-identity` works and confirms you are operating as `web-app-role`. You suspect a Permission Boundary, an SCP, or a lack of permissions in the Identity policy.
**Q:** How do you systematically enumerate what permissions you actually have, and how do you differentiate between an SCP blocking you versus an Identity policy that simply lacks the `ec2:DescribeInstances` allow?
**A:** This is a classic "blind IAM" enumeration problem.
1.  **Brute-force Enumeration (Active):** Without `iam:GetRolePolicy` or `iam:ListAttachedRolePolicies` permissions, I cannot read my own policy. I must rely on active enumeration using tools like `Pacu` or `enumerate-iam` to brute-force API calls and log which ones succeed and which fail.
2.  **Differentiating the Block:** The AWS API error messages often leak the nature of the block:
    *   If the Identity policy simply lacks the permission, the error typically reads: `User: arn:aws:sts::123456789012:assumed-role/web-app-role/i-123 is not authorized to perform: ec2:DescribeInstances because no identity-based policy allows the ec2:DescribeInstances action`.
    *   If an SCP is blocking the action, the error specifically mentions the organization policy: `...with an explicit deny in a service control policy` or `...because no service control policy allows the action`.
    *   If a Permissions Boundary is the cause, the error might state: `...because no permissions boundary allows the action`.
By carefully parsing the trailing part of the `AccessDeniedException` string, I can precisely map the guardrails in the environment and focus my attack path on services that the SCPs and boundaries have left unprotected.

## Deep-Dive Defensive Questions

**Q1: Multi-cloud environments often rely on Identity Federation (SAML/OIDC) to centralize access management (e.g., Okta federating into AWS, GCP, and Azure). Describe the architectural vulnerabilities introduced by this pattern and how defenders can monitor for "Golden SAML" style attacks across cloud planes.**
**A1:** Centralized identity federation creates a massive single point of failure: the Identity Provider (IdP). If an attacker compromises the IdP's token-signing infrastructure (as seen in the SolarWinds/Nobelium campaign with Golden SAML), they can forge assertions for *any* user to *any* federated cloud provider, completely bypassing the primary authentication mechanism and MFA.
**Vulnerabilities:**
*   **Token-Signing Certificate Theft:** If the private key used by the IdP to sign SAML assertions or OIDC JWTs is stolen from the on-premise AD FS server or cloud IdP instance, the attacker achieves persistence and universal access.
*   **Improper Trust Verification:** Misconfigured cloud trust policies might accept tokens with exceedingly long lifetimes, or fail to validate audience restrictions properly.
**Defensive Monitoring:**
1.  **Immutable Audit Trails:** Cloud logging (AWS CloudTrail, GCP Cloud Audit Logs, Azure Activity Logs) must be forwarded to a centralized, immutable SIEM.
2.  **Correlation of Auth Events:** Defenders must correlate the `AssumeRoleWithSAML` or `AssumeRoleWithWebIdentity` events in the cloud with the authentication logs of the IdP. A forged SAML token will trigger a login event in AWS CloudTrail, but there will be *no corresponding authentication event in Okta/AD FS* for that user at that time. This delta is the primary detection mechanism for Golden SAML.
3.  **Anomaly Detection on Session Claims:** Monitor for unusual values in the `Issuer` or `Subject` fields, or assertion lifetimes that deviate from the strict organizational standard.

**Q2: How do you mathematically guarantee that no external entity can access a specific highly sensitive AWS S3 bucket, regardless of any misconfigurations made by users with full IAM administrative privileges?**
**A2:** This requires implementing strict organizational guardrails using Service Control Policies (SCPs) and Resource-Based Policies that enforce "Data Perimeter" concepts. We cannot rely solely on IAM identity policies because an IAM Admin could easily grant themselves access.
To mathematically guarantee isolation, we implement an SCP at the Organizational Unit (OU) level containing the bucket:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "RestrictS3AccessToSpecificVPCEndpoint",
      "Effect": "Deny",
      "Action": "s3:*",
      "Resource": "arn:aws:s3:::highly-sensitive-bucket-name/*",
      "Condition": {
        "StringNotEquals": {
          "aws:SourceVpce": "vpce-0123456789abcdef0"
        }
      }
    }
  ]
}
```
**Mechanism:** This SCP explicitly denies *all* S3 actions against the specific bucket unless the request originates mathematically from a specific VPC Endpoint (`aws:SourceVpce`). Because SCPs supersede all other policies and cannot be modified by account-level IAM Admins (only Org Management account admins), even if an IAM user in the child account grants public access via a bucket policy, the SCP's explicit deny will block the access because the internet is not the specified VPC Endpoint. This establishes an unbreakable network-identity perimeter around the resource.

## Real-World Attack Scenario
**The SSRF to Shadow Admin Pivot**
In a notable real-world simulation mirroring attacks like the Capital One breach, an attacker exploited an unpatched web application susceptible to Server-Side Request Forgery (SSRF). The web server resided in an AWS VPC.
1.  **SSRF to Metadata:** The attacker used the SSRF to query `169.254.169.254` and dumped the IAM temporary credentials of the attached `WebApp-EC2-Role`.
2.  **Discovery:** The attacker found that `WebApp-EC2-Role` had very limited direct permissions, primarily able to write to an S3 log bucket and invoke a specific Lambda function.
3.  **Shadow Admin Abuse:** The attacker enumerated the IAM permissions and discovered a misconfiguration. The `WebApp-EC2-Role` had `iam:PassRole` over a highly privileged `Database-Admin-Role` and the ability to update the Lambda function code (`lambda:UpdateFunctionCode`).
4.  **The Pivot:** The attacker created a malicious Python script that assumed cross-account roles, zipped it, and uploaded it to the Lambda function. They then invoked the Lambda function, passing the `Database-Admin-Role` to the Lambda execution environment.
5.  **Exfiltration:** The Lambda function, now executing with database administrative privileges, queried the production RDS snapshots, modified the snapshot permissions to allow access from an external AWS account controlled by the attacker (`rds:ModifyDBSnapshotAttribute`), and effectively exfiltrated the entirety of the database without downloading the data through the compromised EC2 instance.

## Chaining Opportunities
*   **SSRF -> Instance Metadata (IMDS) -> Credential Access -> Cross-Account Role Assumption:** The most standard cloud pivot.
*   **IAM Privilege Escalation (PassRole) -> Serverless Backdoor (Lambda) -> Persistence & Defense Evasion:** Utilizing serverless functions to hide execution and maintain access after the initial EC2 instance is patched.
*   **MFA Fatigue / Token Theft -> Azure Entra ID PRT Hijacking -> Enterprise App Registration Backdoor:** Gaining initial access to an endpoint, stealing the PRT, and using it to register a malicious OAuth application in Entra ID for permanent graph API access.

## Related Notes
*   [[AWS Privilege Escalation Paths]]
*   [[IAM Policy Evaluation Logic]]
*   [[Identity Provider Federations and Vulnerabilities]]
*   [[Service Control Policies Best Practices]]
*   [[Azure Primary Refresh Token Theft]]
