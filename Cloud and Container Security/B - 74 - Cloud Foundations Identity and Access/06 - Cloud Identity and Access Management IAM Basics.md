---
tags: [cloud, basics, foundations, vapt]
difficulty: beginner
module: "74 - Cloud Foundations Identity and Access"
topic: "74.06 Cloud Identity and Access Management IAM Basics"
---

# Cloud Identity and Access Management (IAM) Basics

## Introduction to Cloud IAM
Identity and Access Management (IAM) is the foundational security discipline that ensures the right individuals (or machine identities) can access the right resources at the right times for the right reasons. In traditional on-premises environments, security often relied on perimeter defenses (firewalls, DMZs, VLANs). In cloud computing, the traditional network perimeter is dissolved. Cloud resources are essentially exposed to the internet (via cloud provider APIs), making IAM the new primary security perimeter.

Cloud IAM acts as the gatekeeper for all actions performed within a cloud environment. Whether a user is logging into the web console, a script is running via a CLI, or a serverless function is accessing a database, every single action requires explicit evaluation against the cloud provider's IAM engine.

Understanding cloud IAM requires a paradigm shift from traditional network security. A misconfigured firewall might expose an application to the internet, but a misconfigured IAM policy can instantly grant an attacker complete control over the entire cloud infrastructure, bypassing all network controls entirely.

---

## The Core Philosophy: Authentication vs. Authorization

To understand IAM, one must cleanly separate its two distinct phases:

### 1. Authentication (AuthN): "Who are you?"
Authentication is the process of verifying the identity of a principal. It answers the question, "Is this entity who they claim to be?"
- **Human Identities:** Verified via passwords, Multi-Factor Authentication (MFA), biometric scans, or federated SSO tokens (SAML/OIDC).
- **Machine Identities:** Verified via API keys, X.509 certificates, JWTs, or instance metadata credentials.

### 2. Authorization (AuthZ): "What are you allowed to do?"
Authorization occurs immediately after successful authentication. It is the process of evaluating the authenticated identity's permissions against the requested resource and action.
- A user might successfully authenticate to an AWS account (AuthN successful) but be denied the ability to terminate an EC2 instance because they lack the necessary permissions (AuthZ failed).
- Authorization in the cloud is heavily policy-driven, relying on JSON/YAML documents that explicitly define allowed or denied actions.

---

## Anatomy of Cloud IAM

Every cloud IAM system (AWS, Azure, GCP) operates on a similar set of core components, even if the nomenclature differs slightly.

### 1. Principals (The "Who")
A principal is the entity making the request.
- **Root/Global Administrators:** The absolute highest level of privilege. Highly dangerous and should rarely be used.
- **Users:** Long-term credentials associated with a specific human.
- **Groups:** Collections of users, used to simplify management (e.g., assigning a policy to the 'DevOps' group rather than individual users).
- **Roles / Service Accounts:** Temporary or machine identities. Roles are assumed, granting temporary, time-bound credentials. This is the preferred method for granting permissions to applications and services.

### 2. Actions (The "What")
The specific API call or operation the principal is attempting to execute.
- Examples include `s3:GetObject`, `Microsoft.Compute/virtualMachines/start/action`, or `compute.instances.delete`.
- Cloud APIs are granular, often breaking down simple tasks into multiple distinct actions (e.g., listing instances vs. describing instance details).

### 3. Resources (The "Where")
The target entity upon which the action is being performed.
- Every cloud object has a unique identifier, such as an Amazon Resource Name (ARN) or a GCP Resource Name.
- Examples: `arn:aws:s3:::my-secure-bucket`, `projects/my-project/zones/us-central1-a/instances/my-vm`.

### 4. Conditions / Context (The "When / How")
Attributes that must be true for the policy to apply. This adds context-awareness to authorization.
- **Source IP:** Is the request originating from the corporate VPN?
- **Time of Day:** Is the request occurring during business hours?
- **MFA Status:** Did the user authenticate using a hardware security key?
- **Tags:** Does the resource have a tag `Environment = Production`?

---

## Access Control Models in the Cloud

### Role-Based Access Control (RBAC)
Permissions are tied to roles, and roles are assigned to principals. This is the traditional model and is heavily used in Azure and GCP.
- *Pros:* Easy to understand and manage at a high level.
- *Cons:* Role explosion (creating hundreds of micro-roles for specific edge cases).

### Attribute-Based Access Control (ABAC)
Permissions are granted based on attributes (tags) of the principal and the resource.
- Example: "Allow developers to modify EC2 instances IF the instance tag 'Project' matches the user tag 'Project'."
- *Pros:* Highly scalable. You don't need a new role for every project, just consistent tagging.
- *Cons:* Relies entirely on strict tagging governance. If an attacker can modify a tag, they can escalate privileges.

---

## The Policy Evaluation Engine

When a request is made to the cloud API, the IAM engine evaluates all relevant policies to render a single, definitive decision: **ALLOW** or **DENY**.

Most cloud providers utilize a deterministic evaluation logic:
1. **Implicit Deny:** By default, all access is denied. If no policy explicitly grants access, the request is rejected.
2. **Explicit Allow:** If a policy grants the action on the resource, the request is allowed.
3. **Explicit Deny:** If any policy anywhere denies the action, the request is denied. **An Explicit Deny ALWAYS overrides an Explicit Allow.**

---

## Visualizing the Cloud IAM Architecture

```text
+----------------+      +----------------+      +------------------+
|                |      |                |      |                  |
|   Principal    +----->+  Auth Engine   +----->+  Policy Engine   |
| (User/App/Role)|      | (Identity IDP) |      | (Authorization)  |
|                |      |                |      |                  |
+----------------+      +-------+--------+      +---------+--------+
                                |                         |
                                v                         v
                        +-------+--------+      +---------+--------+
                        |  MFA / Context |      |  Resource Policy |
                        |  Conditions    |      |  Role Bindings   |
                        +----------------+      +---------+--------+
                                                          |
                                                          v
                                                +---------+--------+
                                                |   Target Cloud   |
                                                |     Resource     |
                                                |  (S3, VM, DB)    |
                                                +------------------+
```

---

## Federation and Single Sign-On (SSO)

Managing distinct sets of credentials for every cloud provider is a massive security risk. Modern cloud architecture relies on Identity Federation.
- **Identity Provider (IdP):** A centralized system managing human identities (e.g., Okta, Entra ID, Ping Identity).
- **Service Provider (SP):** The cloud environment (e.g., AWS, GCP).
- **Flow:** When a user wants to access AWS, they log into Okta. Okta authenticates the user (via MFA) and generates a SAML or OIDC token. The user presents this token to AWS STS (Security Token Service), which exchanges the token for temporary, short-lived AWS credentials tied to a specific role.
- **Security Benefit:** There are no long-term AWS access keys on the developer's laptop. If the employee leaves, disabling their Okta account instantly severs their cloud access.

---

## Security Vulnerabilities & Misconfigurations in IAM

From a VAPT (Vulnerability Assessment and Penetration Testing) perspective, IAM is the most lucrative attack surface in the cloud.

1. **Over-permissive Roles (The wildcard `*`)**
   - Developers frequently use `Action: "*"` and `Resource: "*"` to bypass frustrating permission errors.
   - If an attacker compromises a credential with `*` access, they have full administrative control.

2. **Long-term Credential Leakage**
   - Hardcoding access keys in GitHub, embedding them in Docker images, or storing them in cleartext in configuration files.
   - Once exposed, attackers use automated bots to scrape these keys and utilize them within seconds.

3. **Privilege Escalation**
   - An attacker compromises a low-privileged identity but discovers it has the ability to modify IAM policies (`iam:PutUserPolicy`) or assign roles to itself (`iam:PassRole`).
   - The attacker leverages this to grant themselves administrator privileges.

4. **Lack of MFA and Conditional Access**
   - Failing to require MFA for sensitive operations (like terminating a database or modifying network routing).
   - Failing to restrict access to known corporate IP ranges.

---

## Auditing and Continuous Monitoring

Effective IAM requires constant vigilance:
- **Least Privilege Audits:** Regularly reviewing permissions to ensure principals only have the exact access they need.
- **Unused Credential Rotation:** Identifying and disabling IAM users or roles that haven't been used in 90 days.
- **CloudTrail/Audit Log Monitoring:** Analyzing API logs for anomalous behavior (e.g., a user who normally accesses S3 buckets suddenly attempting to modify IAM roles).

## Chaining Opportunities
- [[07 - Understanding AWS Policies Roles and Users]]
- [[08 - Understanding Azure Active Directory Entra ID Basics]]
- [[09 - Understanding GCP Service Accounts and IAM]]

## Related Notes
- [[10 - Cloud Storage Basics S3 Blobs Buckets]]
