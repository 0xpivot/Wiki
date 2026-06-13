---
tags: [cloud, basics, foundations, vapt]
difficulty: beginner
module: "74 - Cloud Foundations Identity and Access"
topic: "74.07 Understanding AWS Policies Roles and Users"
---

# Understanding AWS Policies, Roles, and Users

## Introduction to AWS IAM
AWS Identity and Access Management (IAM) is the central nervous system of Amazon Web Services. It dictates exactly who can access what services and resources, and under what conditions. Because AWS APIs control everything from creating network infrastructure to deleting petabytes of data, mastering AWS IAM is a non-negotiable requirement for both cloud engineers and security professionals.

Unlike traditional on-premises directory services, AWS IAM operates on a strict model of explicitly structured JSON documents (policies) that define permissions at an incredibly granular level.

---

## The AWS IAM Principals

### 1. The Root User
When an AWS account is first created, it comes with a Root User. This identity uses the email address and password used to create the account.
- **Security Posture:** The Root User has absolute, unrestricted access to the entire account. It can close the account, modify billing, and override any IAM policies.
- **Best Practice:** The Root User should be heavily locked down with MFA, its access keys deleted, and the password vaulted. It should NEVER be used for daily administrative tasks.

### 2. IAM Users
An IAM User is an entity that you create in AWS to represent the person or application that uses it to interact with AWS.
- Contains long-term credentials: A password for console access, and an Access Key ID + Secret Access Key for programmatic CLI/API access.
- **Risk:** Long-term credentials are a massive security risk if leaked. Modern AWS environments aim to minimize or entirely eliminate IAM Users in favor of federated identities and roles.

### 3. IAM Groups
A collection of IAM users. Groups allow you to specify permissions for multiple users easily.
- Instead of attaching a policy to ten different developers, you attach the policy to the `Developers` group, and place the users inside the group.
- **Note:** Groups are purely a management convenience. They are not true "principals" and cannot be referenced as a principal in a resource policy.

### 4. IAM Roles (The Backbone of Modern AWS Security)
Roles are the most important concept in AWS IAM. A role is an identity with permission policies that determine what the identity can and cannot do in AWS. However, unlike a User, a Role does not have long-term credentials (no password or access keys).
- Roles are **assumed** by a trusted entity.
- When assumed, AWS Security Token Service (STS) dynamically generates temporary, short-lived credentials (Access Key, Secret Key, and a Session Token) valid for typically 1 to 12 hours.
- Used for EC2 instances, Lambda functions, federated users (SSO), and cross-account access.

---

## Deep Dive: AWS IAM Roles and STS

The mechanics of assuming a role involve two distinct types of policies attached to the role itself:

### 1. The Trust Policy (AssumeRolePolicyDocument)
This defines **WHO** is allowed to assume the role. It establishes a trust relationship.
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```
*In this example, only the EC2 service is allowed to assume this role and request temporary credentials.*

### 2. The Permission Policy
This defines **WHAT** the role is allowed to do once it has been successfully assumed.

### The AssumeRole Flow Visualized

```text
+-------------------+       1. STS:AssumeRole         +-------------------+
|                   | ------------------------------> |                   |
|   IAM User /      |                                 |   AWS IAM Role    |
|   Compute Inst.   | <------------------------------ |                   |
|                   |    2. Temp Credentials          +---------+---------+
+---------+---------+       (AKIA..., Token)                    |
          |                                                     | 3. Evaluates
          |                                                     v    Trust Pol.
          |                                           +-------------------+
          | 4. API Call with Temp Creds               | Trust Policy      |
          +-----------------------------------------> | (Who can assume)  |
                                                      +---------+---------+
                                                                |
                                                                v
                                                      +-------------------+
                                                      | Permission Policy |
                                                      | (What role does)  |
                                                      +---------+---------+
                                                                | 5. Allows/
                                                                v    Denies
                                                      +-------------------+
                                                      | Target Resource   |
                                                      | (S3, EC2, KMS)    |
                                                      +-------------------+
```

---

## Anatomy of an AWS IAM Policy

Policies are JSON documents. Every policy contains one or more `Statement` blocks.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "AllowS3ReadAccess",
      "Effect": "Allow",
      "Action": [
        "s3:GetObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::my-company-data",
        "arn:aws:s3:::my-company-data/*"
      ],
      "Condition": {
        "IpAddress": {
          "aws:SourceIp": "192.168.100.0/24"
        }
      }
    }
  ]
}
```

### Policy Elements Breakdown:
- **Version:** Always `2012-10-17`. This dictates the syntax rules.
- **Effect:** Either `Allow` or `Deny`.
- **Action:** The specific API calls permitted. Prefix indicates the service (e.g., `s3:`, `ec2:`, `iam:`).
- **Resource:** The ARN (Amazon Resource Name) of the target.
- **Condition:** Optional. Adds context. In the example above, the request is only allowed if it originates from the `192.168.100.0/24` subnet.

### Identity-Based vs. Resource-Based Policies
- **Identity-Based:** Attached to Users, Groups, or Roles. They dictate what the *principal* can do. (e.g., AdministratorAccess).
- **Resource-Based:** Attached directly to a resource, like an S3 bucket or an SQS queue. These dictate *who* can access the resource. They uniquely require a `"Principal"` element inside the statement.

---

## AWS Policy Evaluation Logic

When an API call is made, AWS evaluates multiple layers of policies. Understanding this logic is critical for troubleshooting access denied errors and identifying vulnerabilities.

1. **Explicit Deny overrides everything.** If any policy (SCP, Identity-based, Resource-based, Permissions Boundary) contains a `Deny` for the action, the request is blocked.
2. **Organizations Service Control Policies (SCPs):** Does the SCP allow the action? If not, implicit deny.
3. **Resource-Based Policies:** Does the resource policy explicitly allow the action? If yes, and no explicit deny exists, access is granted (even if identity policy doesn't explicitly allow it, in single-account scenarios).
4. **Identity-Based Policies:** Does the principal's policy explicitly allow the action? If yes, allow.
5. **Permissions Boundaries & Session Policies:** These act as filters. They cannot grant access on their own, but they cap the maximum available permissions. If the boundary does not allow the action, it is denied.
6. **Implicit Deny:** If there is no explicit `Allow` found in any relevant policy, the request defaults to Deny.

---

## Common AWS IAM Attack Vectors

From an attacker's perspective, AWS IAM misconfigurations lead to full account compromise.

### 1. Privilege Escalation via `iam:PassRole`
If an attacker compromises an EC2 instance with an attached IAM role that allows `iam:PassRole` and `ec2:RunInstances`, they can create a new EC2 instance and attach a highly privileged role (e.g., `AdministratorAccess`) to it. They then log into the new instance and extract the administrator credentials.

### 2. Privilege Escalation via `iam:CreatePolicyVersion`
If an attacker has permissions to update an existing IAM policy attached to their user or role, they can simply write a new policy version granting themselves `Action: "*", Resource: "*"` and set it as the default version.

### 3. Cross-Account Role Assumption Abuse
If a trust policy uses a wildcard `{"AWS": "*"}` or points to an entire external AWS account without specifying a strict `Condition` (like `sts:ExternalId`), it may be vulnerable to the "Confused Deputy" attack, where external attackers leverage another account to assume the victim's roles.

## Chaining Opportunities
- [[06 - Cloud Identity and Access Management IAM Basics]]
- [[08 - Understanding Azure Active Directory Entra ID Basics]]
- [[09 - Understanding GCP Service Accounts and IAM]]

## Related Notes
- [[10 - Cloud Storage Basics S3 Blobs Buckets]]
