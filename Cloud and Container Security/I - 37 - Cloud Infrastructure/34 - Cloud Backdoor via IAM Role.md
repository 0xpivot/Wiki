---
tags: [cloud-security, iam, persistence, backdoor, aws, gcp, azure]
difficulty: advanced
module: "37 - Cloud Infrastructure"
topic: "37.34 Cloud Backdoor"
---

# Cloud Backdoors via IAM Persistence

## 1. Introduction to Cloud Persistence
When advanced attackers successfully compromise a cloud environment, their immediate operational goal shifts from initial access and lateral movement to establishing rock-solid persistence. While traditional on-premise persistence involves dropping disk-based malware, modifying registry keys, or creating local OS users, cloud persistence is overwhelmingly achieved through Identity and Access Management (IAM) manipulation. 
IAM backdoors are notoriously stealthy because they utilize native, legitimate administrative features. They do not trigger traditional antivirus or EDR solutions, and if executed carefully, they blend seamlessly into the massive, noisy enterprise identity structures of modern cloud accounts.

## 2. The Mechanics of IAM Identities

To comprehend cloud backdoors, one must deeply understand how identities operate, particularly within AWS:
- **IAM Users:** Long-term, permanent identities associated with static credentials (Access Key ID and Secret Access Key).
- **IAM Roles:** Short-term, assumable identities. Roles do not have static credentials; instead, an entity (a user, a cloud service like EC2, or another role) "assumes" the role and receives temporary session tokens.
- **Trust Policies (Resource-based policies for roles):** Define exactly *who* or *what* is allowed to assume the role.
- **Permissions Policies (Identity-based policies):** Define exactly *what* the role is authorized to do once it is assumed.

### ASCII Diagram: IAM Trust Policy Cross-Account Backdoor

```text
+-----------------------+              +------------------------+
| Attacker's External   |              | Victim's AWS Account   |
| AWS Account           |              | (Target Environment)   |
| (Account A)           |              |                        |
+-----------------------+              +------------------------+
            |                                      ^
            | (1) sts:AssumeRole API Call          | (2) Trust Policy Validates
            |     Targeting Victim's Role          |     Account A is Authorized
            v                                      |
+-------------------------------------------------------------+
|               Victim's IAM Role (e.g., 'DevOps-Admin')      |
+-------------------------------------------------------------+
            |
            | (3) Attacker silently inherits Role's Permissions
            v
+-------------------------------------------------------------+
| Full Access to S3, EC2, RDS, Lambda inside Victim Account   |
+-------------------------------------------------------------+
```

## 3. Advanced Techniques for IAM Backdooring

### A. Creating Shadow Admins (Access Keys)
The simplest, albeit loudest, backdoor involves creating a new set of long-term Access Keys for an existing, highly privileged IAM User.
If an attacker compromises an application or EC2 instance that happens to possess the `iam:CreateAccessKey` permission, they can dynamically generate a new key pair for the `AdminUser`.
```bash
aws iam create-access-key --user-name AdminUser
```
*Stealth factor: Low.* Competent SOCs and tools like GuardDuty easily spot newly generated keys.

### B. Modifying Trust Policies (Cross-Account AssumeRole)
This is arguably the most dangerous and stealthy backdoor available to cloud attackers. An attacker modifies the Trust Policy of an existing, highly privileged role in the victim's account to explicitly allow the attacker's own, external AWS account to assume it.
**Original Legitimate Trust Policy:**
```json
{
  "Effect": "Allow",
  "Principal": { "Service": "ec2.amazonaws.com" },
  "Action": "sts:AssumeRole"
}
```
**Backdoored Trust Policy:**
```json
{
  "Effect": "Allow",
  "Principal": { 
    "Service": "ec2.amazonaws.com",
    "AWS": "arn:aws:iam::999999999999:root"  // ATTACKER'S OWN ACCOUNT
  },
  "Action": "sts:AssumeRole"
}
```
Following this modification, the attacker can sit securely in their own AWS account (999999999999), execute `aws sts assume-role --role-arn arn:aws:iam::VICTIM:role/DevOps-Admin`, and immediately gain administrative access to the victim's cloud without needing any static passwords or access keys within the victim environment.

### C. Identity Provider (IdP) & SAML Manipulation
Large enterprises federate access using IdPs like Azure AD, Okta, or Ping Identity via SAML or OIDC. The cloud environment intrinsically trusts the IdP.
If an attacker possesses permissions such as `iam:UpdateSAMLProvider` or `iam:CreateSAMLProvider`, they can upload their own SAML metadata XML. This allows the attacker to forge SAML assertions locally and authenticate directly into high-privileged cloud roles, completely bypassing the organization's SSO, MFA, and logging mechanisms.

### D. Inline Policy Injection
Instead of creating new identities, an attacker stealthily adds a malicious inline policy to an innocuous, overlooked, or dormant IAM user or role.
For example, attaching an `AdministratorAccess` policy to a dormant `test-developer` user account that hasn't been logged into for a year.

### E. PassRole Abuse for Compute Persistence
If an attacker holds `iam:PassRole` and `ec2:RunInstances` permissions, they can provision a new EC2 instance and attach a highly privileged IAM role to it. They then install a reverse shell or cron job on the instance. Even if the attacker's initial access vectors are identified and revoked, the EC2 instance (and the attacker via the reverse shell) indefinitely retains the high-privilege access.

## 4. Exploit Walkthrough: The Cross-Account Pivot

Assume an attacker has compromised an EC2 instance that holds a role with `iam:UpdateAssumeRolePolicy` permissions.
1. **Identify Target Role:** The attacker lists roles and identifies a highly privileged role named `Production-DB-Admin`.
2. **Retrieve Current Policy:**
   `aws iam get-role --role-name Production-DB-Admin`
3. **Modify JSON Locally:** The attacker downloads the policy and adds their AWS account ARN to the `Principal` block.
4. **Update the Policy:**
   `aws iam update-assume-role-policy --role-name Production-DB-Admin --policy-document file://malicious-trust.json`
5. **Persistence Achieved:** The attacker drops access to the EC2 instance to avoid detection. They use their own laptop to run `aws sts assume-role` and silently re-enter the network whenever they desire.

## 5. Hunting and Discovery

Detecting IAM backdoors requires rigorous, automated monitoring of identity-centric events.
- **CloudTrail Analysis:** Aggressively monitor for high-risk API calls such as `CreateAccessKey`, `UpdateAssumeRolePolicy`, `PutRolePolicy`, `AttachUserPolicy`, and `CreateSAMLProvider`.
- **Anomalous Principal Discovery:** Scan all Trust Policies across the organization. Any `Principal` ARN that does not explicitly belong to a known internal AWS account should trigger an immediate critical incident response alert. Open-source tools like PMapper or AWS IAM Access Analyzer help visualize and detect these external trusts.
- **Session Analysis:** Monitor `sts:AssumeRole` events where the source IP originates outside authorized corporate VPN ranges or known AWS regions.

## 6. Defensive Countermeasures

- **Strict IAM Permissions:** Adhere rigidly to the principle of least privilege. Extremely few roles should ever possess `iam:*` or `iam:Update*` permissions.
- **Service Control Policies (SCPs):** Use AWS Organizations SCPs to establish immutable guardrails. For example, an SCP can explicitly deny `iam:CreateAccessKey` globally, forcing all users to rely on federated SSO.
- **Permission Boundaries:** Attach boundaries to developers so that even if they are allowed to create roles, the roles they create cannot exceed a predefined permission ceiling, physically preventing privilege escalation.
- **Configuration Management & Drift Detection:** Manage all IAM configurations via Infrastructure as Code (Terraform) [[30 - Terraform CloudFormation Misconfigurations]]. If drift is detected (e.g., a trust policy is manually altered), the CI/CD pipeline should automatically and instantly revert it to the secure state.

## 7. Chaining Opportunities
- Initial access via [[32 - Cloud Storage Mining]] (finding leaked keys) is immediately followed by establishing an IAM backdoor to ensure access isn't lost if the keys are rotated.
- An IAM backdoor enables long-term, invisible access to modify pipelines in [[33 - CI CD Pipeline Attacks]] or extract sensitive databases.

## 8. Related Notes
- [[35 - Defense — Least Privilege IAM, IMDSv2, Logging, SCP]]
- [[33 - CI CD Pipeline Attacks]]
- [[32 - Cloud Storage Mining]]
- [[30 - Terraform CloudFormation Misconfigurations]]
