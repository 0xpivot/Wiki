---
tags: [cloud, basics, enumeration, vapt]
difficulty: beginner
module: "75 - Cloud Enumeration and Reconnaissance"
topic: "75.06 Enumerating AWS IAM Permissions"
---

# Enumerating AWS IAM Permissions

## 1. Introduction to AWS IAM Enumeration
Identity and Access Management (IAM) is the security backbone of Amazon Web Services (AWS). It determines exactly "who" can do "what" within an AWS environment. In the context of a Vulnerability Assessment and Penetration Testing (VAPT) engagement or Red Teaming operation, enumerating AWS IAM permissions is arguably the most critical reconnaissance step once initial access is achieved. 

The goal of IAM enumeration is to fully map out the current security context (who am I?), identify what permissions are natively attached to the compromised identity, discover other entities (users, groups, roles) in the AWS account, and chart potential paths for privilege escalation or lateral movement. 

Unlike traditional networks where enumeration focuses on IP addresses and open ports, cloud enumeration focuses heavily on APIs, permissions, resource policies, and identity relationships. Failing to comprehensively enumerate IAM often results in missed exploitation opportunities, as misconfigurations in IAM are the leading cause of massive cloud breaches.

## 2. Core Concepts of AWS IAM
Before diving into enumeration techniques, it is crucial to understand the building blocks of AWS IAM:
- **IAM Users**: Long-term credentials representing a person or service. Uses Access Keys (Access Key ID and Secret Access Key).
- **IAM Groups**: A collection of IAM users. Policies attached to a group apply to all users within it.
- **IAM Roles**: Identities that are assumable by users, services, or cross-account entities. They rely on short-term, temporary credentials (STS).
- **Policies**: JSON documents that define permissions. They can be:
  - **AWS Managed Policies**: Maintained by AWS (e.g., `AdministratorAccess`).
  - **Customer Managed Policies**: Created and maintained by the account owner.
  - **Inline Policies**: Embedded directly into a single user, group, or role.
- **Trust Policies (AssumeRole Policy Document)**: Determine who or what service is allowed to assume a given role.
- **Resource-Based Policies**: Policies attached directly to a resource (e.g., S3 Bucket Policies, KMS Key Policies) rather than an identity.

## 3. Enumeration Flow and ASCII Diagram
The typical flow of IAM enumeration begins from a point of compromise (e.g., a leaked access key, a Server-Side Request Forgery on an EC2 instance, or a compromised CI/CD pipeline).

```mermaid
graph TD
    subgraph AWS IAM Enumeration Workflow
        A[Initial Access <br/> Leaked Keys / SSRF / Web Shell] --> B[1. Context Identification <br/> - sts:GetCallerIdentity Who am I? <br/> - Identify Account ID, ARN, and User ID]
        B --> C[2. Basic IAM Enumeration If permitted <br/> - iam:ListUsers, iam:ListRoles <br/> - iam:ListGroupsForUser]
        C --> D[3. Policy & Permission Extraction <br/> - iam:ListAttachedUserPolicies <br/> - iam:ListUserPolicies Inline <br/> - iam:GetPolicy / iam:GetPolicyVersion]
        D --> E[4. Analyzing Privilege Escalation Paths <br/> - Can I create a new user? iam:CreateUser <br/> - Can I attach a policy? iam:AttachUserPolicy <br/> - Can I pass a role? iam:PassRole]
        E --> F[Exploitation / PrivEsc]
    end
```

## 4. Phase 1: Context Identification
The absolute first step upon obtaining AWS credentials is to figure out what identity those credentials belong to. In traditional computing, this is the equivalent of running `whoami`. In AWS, this is done using the AWS Security Token Service (STS).

### Using the AWS CLI
```bash
aws sts get-caller-identity
```
**Sample Output:**
```json
{
    "UserId": "AKIAIOSFODNN7EXAMPLE",
    "Account": "123456789012",
    "Arn": "arn:aws:iam::123456789012:user/dev-sanchit"
}
```
This output provides:
- **Account**: The 12-digit AWS account ID.
- **Arn**: The Amazon Resource Name, which clearly identifies whether you are operating as an IAM User (`user/username`) or an Assumed Role (`assumed-role/RoleName/SessionName`).

If you are operating as an assumed role (e.g., from an EC2 Instance Metadata Service compromise), the ARN will look like: `arn:aws:sts::123456789012:assumed-role/WebRole/i-0abcdef1234567890`.

## 5. Phase 2: Enumerating the Compromised Identity's Permissions
Once you know who you are, you need to find out what you are allowed to do. AWS does not have a single `aws iam what-can-i-do` command. Instead, you must enumerate the policies attached to your identity.

### 5.1 Listing Attached Managed Policies
If you are an IAM user, check what managed policies are explicitly attached to you:
```bash
aws iam list-attached-user-policies --user-name dev-sanchit
```

### 5.2 Listing Inline Policies
Inline policies are directly embedded in the user object.
```bash
aws iam list-user-policies --user-name dev-sanchit
```
If this command returns a policy name (e.g., `CustomDevPolicy`), you must read its contents:
```bash
aws iam get-user-policy --user-name dev-sanchit --policy-name CustomDevPolicy
```

### 5.3 Enumerating Group Memberships
Users often inherit permissions via groups. Check which groups the user belongs to:
```bash
aws iam list-groups-for-user --user-name dev-sanchit
```
For every group returned, check the group's attached and inline policies:
```bash
aws iam list-attached-group-policies --group-name Developers
aws iam list-group-policies --group-name Developers
```

### 5.4 Reading Managed Policy Documents
If `list-attached-user-policies` showed an attached policy with an ARN like `arn:aws:iam::123456789012:policy/CustomAdmin`, you need to read the policy document to understand the permissions.

First, get the default version ID of the policy:
```bash
aws iam get-policy --policy-arn arn:aws:iam::123456789012:policy/CustomAdmin
```
Assume the default version is `v3`. Next, retrieve the JSON document for that version:
```bash
aws iam get-policy-version --policy-arn arn:aws:iam::123456789012:policy/CustomAdmin --version-id v3
```

## 6. Phase 3: Broad Environment Enumeration
If the compromised identity has broad `iam:List*` and `iam:Get*` permissions (often found in `SecurityAudit` or `ViewOnlyAccess` policies), you should enumerate the entire AWS account to map out all users, roles, and potential lateral movement targets.

### 6.1 Listing All Users
```bash
aws iam list-users
```

### 6.2 Listing All Roles
Roles are prime targets for privilege escalation, especially if they have weak Trust Policies (e.g., allowing `*` or wide IP ranges to assume them).
```bash
aws iam list-roles
```

### 6.3 Analyzing Trust Policies
When analyzing roles, pay close attention to the `AssumeRolePolicyDocument`. This defines who can call `sts:AssumeRole` on this role.
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "AWS": "arn:aws:iam::123456789012:root" },
      "Action": "sts:AssumeRole"
    }
  ]
}
```
If you find a role with a misconfigured trust policy, you might be able to assume it and inherit its (potentially higher) privileges.

## 7. Brute-Forcing Permissions
In many scenarios, the compromised identity lacks the `iam:List*` permissions necessary to read its own policies. This results in "Access Denied" errors when running the enumeration commands above.

When explicit enumeration fails, attackers use brute-forcing techniques. This involves attempting hundreds of safe, non-destructive API calls to see which ones succeed and which ones return Access Denied.

### Technique: DryRun Flags
Many AWS services support a `--dry-run` flag. This allows you to check if you have permissions to perform an action without actually executing it.
```bash
aws ec2 run-instances --image-id ami-123456 --instance-type t2.micro --dry-run
```
- If you lack permissions, the error is: `UnauthorizedOperation`.
- If you have permissions, the error is: `DryRunOperation`.

### Automated Brute-Forcing Tools
Tools like **Enumerate-IAM** (by Andres Riancho) automate this process by throwing thousands of API calls (e.g., `ListBuckets`, `DescribeInstances`) at the AWS API and recording the successful ones. This allows an attacker to map out effective permissions even when IAM policy reading is blocked.

## 8. Third-Party Tools for AWS IAM Enumeration
Manual enumeration using the AWS CLI is tedious and error-prone, especially in large environments with thousands of roles and policies. Several open-source tools streamline this process.

### 8.1 Pacu
Pacu, developed by Rhino Security Labs, is the premier AWS exploitation framework (similar to Metasploit, but for AWS).
- **Command:** `run iam__enum_permissions`
- **Functionality:** It automatically attempts to read the current user's policies. If it gets Access Denied, it seamlessly falls back to brute-forcing permissions to build a local database of what the credentials can do.
- **Command:** `run iam__privesc_scan`
- **Functionality:** Scans the enumerated IAM data for 21 known IAM privilege escalation vectors.

### 8.2 ScoutSuite
ScoutSuite is a multi-cloud security auditing tool. While primarily used by defenders, attackers use it post-compromise (if they have `SecurityAudit` permissions) to generate an HTML report detailing all misconfigurations, open security groups, and overly permissive IAM roles.

### 8.3 PMapper (Principal Mapper)
Developed by NCC Group, PMapper is arguably the most powerful tool for analyzing complex IAM relationships. It downloads all IAM objects (users, groups, roles, policies) and builds a local graph database. It can then query this graph to find hidden attack paths.
- Example: User A cannot access S3. User A can assume Role B. Role B can attach a policy to Role C. Role C has full S3 access. PMapper will visually map this 3-hop attack path.

### 8.4 Cloudsplaining
Cloudsplaining, by Salesforce, ingests AWS IAM policies and generates a risk-prioritized report identifying overprivileged identities, focusing heavily on privilege escalation, resource exposure, and data exfiltration risks.

## 9. Identifying Privilege Escalation Paths
During enumeration, attackers specifically look for risky IAM actions that allow them to escalate their privileges. Rhino Security Labs documented 21 distinct AWS IAM Privilege Escalation vectors. Key permissions to look for during enumeration include:

1. **iam:CreatePolicyVersion**: Allows an attacker to write a new version of an existing policy, potentially granting themselves `*` (Administrator) access.
2. **iam:AttachUserPolicy / iam:AttachGroupPolicy / iam:AttachRolePolicy**: Allows an attacker to attach existing powerful policies (like `AdministratorAccess`) to their own user.
3. **iam:PutUserPolicy / iam:PutGroupPolicy / iam:PutRolePolicy**: Allows an attacker to create an inline policy granting arbitrary permissions to themselves.
4. **iam:CreateAccessKey**: Allows an attacker to create new access keys for a higher-privileged user, bypassing the need for their password.
5. **iam:UpdateLoginProfile**: Allows an attacker to change the console password of another user (e.g., the root user or an admin).
6. **iam:PassRole + ec2:RunInstances**: The classic cloud pivot. Allows an attacker to create an EC2 instance, attach a highly privileged IAM role to it (`PassRole`), and then retrieve the role's credentials from the instance metadata.

## 10. Defensive Mechanisms and Evasion
Defenders have several ways to detect aggressive IAM enumeration.

### CloudTrail Monitoring
Every API call made during enumeration (e.g., `iam:ListUsers`, `sts:GetCallerIdentity`) is logged in AWS CloudTrail. Defenders create alerts for bursts of `AccessDenied` errors, which strongly indicate brute-force enumeration.

**Evasion Strategies:**
- **Low and Slow:** Throttle enumeration API calls to blend in with normal administrative traffic.
- **Targeted Enumeration:** Avoid broad `List*` calls if you already know the specific role or resource you are targeting.
- **Living off the Land:** If you compromise an instance running a legitimate automation script, inspect the script to see what API calls it natively makes, and piggyback on those permissions rather than actively scanning.

### AWS GuardDuty
GuardDuty is AWS's managed threat detection service. It actively monitors CloudTrail logs for malicious behavior.
- **Finding:** `Recon:IAMUser/UserPermissions`
- **Finding:** `UnauthorizedAccess:IAMUser/InstanceCredentialExfiltration.OutsideAWS` (Triggered if you use stolen EC2 metadata credentials from an IP outside the AWS environment).

To bypass GuardDuty when using stolen instance credentials, attackers often spin up an EC2 instance in their own AWS account, proxy their traffic through it, and perform enumeration from an AWS-owned IP address, which bypasses the `OutsideAWS` check.

## 11. Conclusion
AWS IAM Enumeration is a complex puzzle involving identities, policies, and trust relationships. A thorough enumeration phase allows a penetration tester to map the environment, identify misconfigurations, and construct sophisticated privilege escalation paths that might not be obvious from a cursory glance. Mastery of the AWS CLI, combined with an understanding of tools like Pacu and PMapper, is essential for modern cloud security assessments.

---
## Chaining Opportunities
- **[[09 - Cloud Metadata Services IMDS Overview]]**: Credentials extracted from IMDSv1/v2 are immediately subject to the enumeration techniques detailed in this note.
- **[[15 - AWS Privilege Escalation Vectors]]**: The outputs of IAM enumeration directly feed into the exploitation of the 21 Rhino IAM privilege escalation vectors.
- **[[20 - AWS S3 Bucket Enumeration and Exploitation]]**: IAM enumeration might reveal `s3:ListAllMyBuckets` or `s3:GetObject` permissions, leading directly to data exfiltration.

## Related Notes
- [[02 - Identity and Access Management Concepts]]
- [[12 - CloudTrail and CloudWatch for Attackers]]
- [[25 - Attacking AWS Lambda and Serverless]]
