---
tags: [cloud, basics, foundations, vapt]
difficulty: beginner
module: "74 - Cloud Foundations Identity and Access"
topic: "74.03 Introduction to AWS Architecture and Services"
---

# 74.03 Introduction to AWS Architecture and Services

## 1. Executive Summary
Amazon Web Services (AWS) is the pioneer and dominant force in the public cloud computing market. For a Vulnerability Assessment and Penetration Testing (VAPT) professional, understanding AWS's global infrastructure, core services, and native security constructs is absolutely essential. An attack in AWS rarely looks like a traditional network intrusion. Instead, it involves exploiting misconfigured identity policies, abusing managed service trust relationships, and pivoting through cloud-native APIs. This document details the foundational architecture of AWS and examines its core services through an offensive security lens.

## 2. AWS Global Infrastructure Breakdown
AWS infrastructure is designed around geographic isolation and high availability. Understanding this hierarchy is crucial when mapping an organization's attack surface and understanding data residency boundaries.

### 2.1 Regions
A Region is a distinct geographic location (e.g., `us-east-1` in N. Virginia, `eu-west-1` in Ireland). 
- Regions are completely independent and isolated from one another. 
- When you deploy a resource (like an EC2 instance), it is bound to a specific region.
- **VAPT Context:** Attackers often operate in regions the target organization does not normally use (e.g., spinning up cryptominers in `ap-northeast-3`) to avoid detection by localized monitoring tools.

### 2.2 Availability Zones (AZs)
Within every Region, there are multiple (usually a minimum of 3) Availability Zones. An AZ consists of one or more discrete physical data centers with redundant power, networking, and connectivity.
- AZs are connected via high-bandwidth, ultra-low-latency networking.
- They allow customers to build highly available architectures. If one AZ experiences a physical failure, the others remain operational.

### 2.3 Edge Locations & Points of Presence
Edge locations are geographically dispersed data centers primarily used to cache content closer to end users.
- They power services like **Amazon CloudFront** (CDN) and **Amazon Route 53** (DNS).
- **VAPT Context:** Subdomain takeovers often involve dangling DNS records pointing to abandoned CloudFront distributions.

### 2.4 AWS Organizations & Accounts
The fundamental boundary of isolation in AWS is the **Account**. A large enterprise does not use a single AWS account; they use AWS Organizations to manage hundreds of accounts (e.g., a Dev Account, Prod Account, Security Account).
- **VAPT Context:** The ultimate goal of an attacker is often to compromise the management/billing account or abuse trust relationships (Cross-Account IAM Roles) to pivot from a low-security Dev account into a high-security Prod account.

## 3. ASCII Diagram: AWS Infrastructure Hierarchy

```text
+------------------------------------------------------------------------------------+
|                             AWS CLOUD INFRASTRUCTURE                               |
+------------------------------------------------------------------------------------+
|                                                                                    |
|  [ REGION: us-east-1 (N. Virginia) ]                                               |
|                                                                                    |
|   +---------------------------------+   +---------------------------------+        |
|   |  Availability Zone A (us-east-1a)   |  Availability Zone B (us-east-1b)   |        |
|   |  +---------------------------+  |   |  +---------------------------+  |        |
|   |  |     Physical Data Center  |  |   |  |     Physical Data Center  |  |        |
|   |  |     (Compute, Storage)    |  |   |  |     (Compute, Storage)    |  |        |
|   |  +---------------------------+  |   |  +---------------------------+  |        |
|   +---------------------------------+   +---------------------------------+        |
|                  |                                      |                          |
|                  +---------- Low Latency Link ----------+                          |
|                                                                                    |
+------------------------------------------------------------------------------------+
|                                  INTERNET                                          |
|                                     |                                              |
|  [ EDGE LOCATIONS ] <---------------+                                              |
|  (CloudFront CDN, WAF, Route 53)                                                   |
+------------------------------------------------------------------------------------+
```

## 4. Core AWS Services & Security Posture

### 4.1 Compute Services
- **Amazon EC2 (Elastic Compute Cloud):** Provides IaaS virtual machines. 
  - *Pentesting focus:* OS vulnerabilities, SSRF to IMDS (`169.254.169.254`), security group misconfigurations allowing direct SSH/RDP access.
- **AWS Lambda:** A serverless, event-driven compute service (FaaS). You upload code, and AWS runs it.
  - *Pentesting focus:* Event injection, insecure temporary storage (`/tmp`), executing shell commands from vulnerable application code, and abusing over-privileged Lambda execution roles.
- **Amazon ECS & EKS:** Managed container orchestration (Docker and Kubernetes).
  - *Pentesting focus:* Container escapes, exploiting overly permissive IAM roles attached to specific pods (IRSA - IAM Roles for Service Accounts).

### 4.2 Storage Services
- **Amazon S3 (Simple Storage Service):** Object storage. One of the most heavily utilized and frequently misconfigured services in AWS.
  - *Pentesting focus:* Identifying publicly readable or writable buckets, extracting sensitive configuration files or PII, and modifying JavaScript files hosted on S3 (leading to stored XSS on websites).
- **Amazon EBS (Elastic Block Store):** Block storage attached to EC2 instances (like a virtual hard drive).
  - *Pentesting focus:* Unencrypted EBS volumes can have snapshots created and shared with an attacker's external AWS account, leading to full data exfiltration without logging into the OS.

### 4.3 Networking Services
- **Amazon VPC (Virtual Private Cloud):** A logically isolated virtual network where AWS resources are launched.
- **Subnets:** Public subnets have a route to an Internet Gateway (IGW); private subnets do not.
- **Security Groups (SGs):** Stateful, host-level firewalls applied to instances (e.g., EC2, RDS). They only contain 'allow' rules.
- **Network ACLs (NACLs):** Stateless, subnet-level firewalls that act as a secondary layer of defense. Can contain both 'allow' and 'deny' rules.
  - *VAPT Context:* Reviewing VPC peering connections, evaluating Security Group rules for excessive open ports (e.g., `0.0.0.0/0`), and checking for exposed management interfaces.

### 4.4 Database Services
- **Amazon RDS (Relational Database Service):** Managed SQL databases (MySQL, PostgreSQL, Aurora).
- **Amazon DynamoDB:** Managed NoSQL database.
  - *Pentesting focus:* Checking if databases are deployed in public subnets, assessing weak database credentials, and checking IAM policies that might allow a user to dump DynamoDB tables directly via the AWS API.

## 5. AWS Identity and Access Management (IAM) Deep Dive
IAM is the absolute core of AWS security. A breach in AWS almost always traces back to an IAM flaw.

### 5.1 Core IAM Components
- **Users:** Represent human identities or specific service accounts. They have long-term credentials (Access Key ID and Secret Access Key).
- **Groups:** Collections of users. Policies are applied to groups to manage permissions at scale.
- **Roles:** The most critical concept. Roles do not have permanent credentials. Instead, they are *assumed* by trusted entities (like an EC2 instance, a Lambda function, or a user from another account), which receive temporary security credentials via the AWS Security Token Service (STS).
- **Policies:** JSON documents attached to identities or resources that explicitly define what actions are allowed or denied.

### 5.2 The Concept of AssumeRole
`sts:AssumeRole` is the primary mechanism for privilege escalation and lateral movement. If an attacker compromises a developer's access keys, and that developer has permission to assume a highly privileged "ProductionAdmin" role, the attacker can execute an API call to assume that role and gain its privileges.

**Example of a Dangerous IAM Policy:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*"
    }
  ]
}
```
*VAPT Note:* The above policy grants Administrator access. Identifying users or roles with this policy, or policies that allow them to *attach* this policy to themselves (`iam:AttachUserPolicy`), is a primary objective.

## 6. AWS Native Security & Governance Tools
AWS provides built-in tools to monitor and protect the environment. Pentesters must understand these to evade detection and defenders must configure them correctly.

- **AWS CloudTrail:** The most important auditing tool. It logs every single API call made in the AWS account. If an attacker creates a new user or stops an instance, CloudTrail records it.
  - *Evasion tactic:* Attackers will attempt to disable CloudTrail or delete the S3 bucket where logs are stored if they gain sufficient privileges.
- **AWS Config:** Continuously monitors and records AWS resource configurations and allows you to automate the evaluation of recorded configurations against desired guidelines (CSPM).
- **Amazon GuardDuty:** A managed threat detection service that continuously monitors CloudTrail logs, VPC Flow Logs, and DNS logs for malicious activity (e.g., detecting crypto-mining or API calls coming from known malicious IP addresses).
- **AWS KMS (Key Management Service):** Manages cryptographic keys. Even if an attacker steals an encrypted EBS volume, they cannot read the data unless they also have the IAM permissions to use the corresponding KMS key to decrypt it.

## 7. VAPT Perspective: Initial Attack Vectors in AWS

### 7.1 Exploiting S3 Misconfigurations
Using tools like `aws cli` or specialized scanners to find exposed buckets.
```bash
# Checking if a bucket allows unauthenticated listing
aws s3 ls s3://target-company-bucket --no-sign-request
```

### 7.2 Leaked Credentials in Source Code
Developers frequently hardcode AWS Access Keys into scripts and push them to public GitHub repositories. Automated bots scrape GitHub 24/7 to find these keys and instantly use them to launch EC2 instances for mining cryptocurrency.

### 7.3 Server-Side Request Forgery (SSRF) to IMDS
If a web application hosted on an EC2 instance is vulnerable to SSRF, an attacker can force the server to query the Instance Metadata Service.
- **IMDSv1:** Highly susceptible to SSRF. An attacker sends a request to `http://169.254.169.254/latest/meta-data/iam/security-credentials/role-name` and the server responds with the AccessKeyId, SecretAccessKey, and SessionToken.
- **IMDSv2:** Mitigates this by requiring a session token generated via an HTTP PUT request with a specific header, making simple SSRF exploitation much harder.

## 8. Privilege Escalation and Lateral Movement in AWS
Once an attacker has initial access (e.g., via stolen EC2 role credentials):
1. **Enumeration:** They use tools like `Pacu` or the AWS CLI to figure out "Who am I?" (`aws sts get-caller-identity`) and "What can I do?".
2. **Escalation:** They look for misconfigured IAM permissions. For example, if they have `iam:CreateAccessKey` permissions for another user, they can generate new keys for an administrator account.
3. **Lateral Movement:** They might discover that the current account has a VPC peering connection to a production account, allowing them to route network traffic to internal databases. Or, they might find a cross-account role they can assume.

## 9. Defensive Architecture (Well-Architected Framework)
AWS recommends the Well-Architected Framework, particularly the Security Pillar, which emphasizes:
- Implementing strong identity foundations (Principle of Least Privilege).
- Enabling traceability (CloudTrail everywhere).
- Applying security at all layers (Defense in Depth via VPCs, SGs, and WAF).
- Automating security best practices.
- Protecting data in transit and at rest.

## 10. Chaining Opportunities
- **[[01 - Introduction to Cloud Computing IaaS PaaS SaaS]]**: AWS provides all three models. EC2 is IaaS, Elastic Beanstalk is PaaS, and services like AWS WorkSpaces lean towards SaaS.
- **[[02 - Cloud Shared Responsibility Model]]**: The customer's responsibility changes drastically depending on whether they deploy a database on an EC2 instance (IaaS) or use Amazon RDS (PaaS).

## 11. Related Notes
- [[04 - Introduction to Azure Architecture and Services]]
- [[05 - Introduction to GCP Architecture and Services]]
- Exploiting SSRF in Cloud Environments
- AWS IAM Privilege Escalation Vectors
