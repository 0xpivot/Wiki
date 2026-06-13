---
tags: [cloud, enumeration, pentesting, tools, recon, aws, azure, gcp]
difficulty: advanced
module: "37 - Cloud Infrastructure"
topic: "37.26 Cloud Enumeration Tools"
---

# 26 - Cloud Enumeration Tools

## Introduction to Cloud Enumeration

In cloud penetration testing, enumeration is the process of mapping out the resources, identities, permissions, and configurations of a target cloud environment. Unlike traditional on-premises network enumeration (which relies heavily on port scanning and protocol fingerprinting like Nmap or Responder), cloud enumeration primarily relies on interacting with the cloud provider's APIs (Application Programming Interfaces).

Once an attacker compromises an identity (e.g., an AWS IAM user, an Azure Service Principal, or a GCP Service Account) or extracts temporary credentials via Server-Side Request Forgery (SSRF), the immediate next step is situational awareness. The attacker must answer:
1. Who am I? (Identity)
2. What can I do? (Permissions / RBAC)
3. What resources exist? (Compute, Storage, Databases)
4. Are there any misconfigurations I can exploit for privilege escalation?

Due to the immense size and complexity of cloud environments, manual enumeration via the CLI (e.g., running `aws ec2 describe-instances` endlessly) is inefficient and prone to human error. A sophisticated ecosystem of automated cloud enumeration tools has been developed to solve this problem.

## The Cloud Enumeration Ecosystem

Cloud enumeration tools generally fall into three categories:
1. **Auditing/Compliance Tools**: Designed for defenders to find misconfigurations against baselines (like CIS benchmarks). Attackers use these to find vulnerable setups.
2. **Offensive/Exploitation Frameworks**: Designed specifically for penetration testers to enumerate, escalate privileges, and exploit resources.
3. **Graphing/Mapping Tools**: Tools that ingest API data and build visual relationship graphs, crucial for identifying complex IAM privilege escalation paths.

### Tool Workflow ASCII Architecture

```text
+-----------------------+      +-------------------------+      +--------------------------+
|  Compromised Creds    |      |   Enumeration Tool      |      |   Target Cloud APIs      |
|-----------------------|      |-------------------------|      |--------------------------|
| - Access Key ID       | ===> | - Pacu                  | ===> | - AWS IAM API            |
| - Secret Access Key   |      | - ScoutSuite            |      | - Azure Resource Manager |
| - Session Token       |      | - AzureHound            |      | - GCP Resource API       |
+-----------------------+      +-----------+-------------+      +--------------------------+
                                           |
                                           v
                               +-----------+-------------+
                               |   Output / Analysis     |
                               |-------------------------|
                               | - JSON/HTML Reports     |
                               | - Neo4j Graph DB        |
                               | - Identified PrivEsc    |
                               |   Vectors               |
                               +-------------------------+
```

## Offensive Frameworks

### 1. Pacu (AWS)
Developed by Rhino Security Labs, Pacu is the premier exploitation framework for AWS. It is structured like Metasploit, using a modular architecture.

**Key Features:**
- `iam__enum_permissions`: Attempts to enumerate the exact permissions the current user holds. AWS does not have an API call to simply say "what can I do?" unless you have specific IAM read access. Pacu brute-forces API calls to infer permissions.
- `iam__privesc_scan`: Scans the enumerated IAM data for known privilege escalation paths (e.g., the ability to create a new policy version and attach it to yourself).
- Service-specific enumeration modules (EC2, S3, RDS, Lambda).

**Example Usage:**
```bash
# Start Pacu
pacu

# Inside the Pacu console
Pacu > set_keys
Pacu > run iam__enum_permissions
Pacu > run iam__privesc_scan
Pacu > run s3__download_bucket
```

### 2. Stratus Red Team (AWS, Azure, GCP, K8s)
Developed by DataDog, Stratus Red Team is a tool for executing offensive attack techniques against cloud environments. While technically a "detonation" framework, it is heavily used during purple teaming to validate if enumeration and attack techniques are detected.

### 3. ROADtools (Azure AD)
ROADtools is a framework to interact with Azure Active Directory. It is essential for enumerating users, service principals, applications, and their relationships.

**Key Features:**
- `roadrecon gather`: Connects to Azure AD and dumps all users, groups, devices, service principals, and role assignments into a local SQLite database.
- `roadrecon plugin gui`: Launches a web GUI to explore the dumped data.
- Capable of identifying over-privileged Service Principals and applications lacking multifactor authentication.

**Example Usage:**
```bash
# Authenticate using compromised credentials
roadrecon auth --username <user> --password <password>

# Dump the Azure AD directory
roadrecon gather

# Analyze the data visually
roadrecon plugin gui
```

## Graphing and Mapping Tools

Cloud identity and access management is incredibly complex. Graph theory is the best way to visualize how a low-level user might escalate to a domain admin through nested groups and cross-service permissions.

### 1. BloodHound Enterprise / AzureHound (Azure)
AzureHound is the data collector for BloodHound, adapted for Azure Active Directory and Azure Resource Manager (ARM).

It collects data about Azure AD users, groups, App Roles, Service Principals, and Azure RM role assignments (Subscriptions, Resource Groups). It then builds a Neo4j graph showing paths to privilege escalation.

**Example Usage:**
```bash
# Run AzureHound using an Azure CLI login session
azurehound -c "AzureHound" list --tenant "<TenantID>" -o azurehound_output.json
```
This output is then ingested into the BloodHound GUI, allowing attackers to run queries like "Find Shortest Path to Global Administrator."

### 2. PMapper (Principal Mapper) (AWS)
PMapper is a script and library for identifying risks in the configuration of AWS Identity and Access Management (IAM). It identifies privilege escalation risks and determines which principals can access specific resources. It builds a graph of IAM relationships.

**Example Usage:**
```bash
# Generate the graph
pmapper graph create

# Query the graph to see who can escalate privileges
pmapper arg --privesc
```

## Auditing and Compliance Tools (Used Offensively)

While designed for defenders, attackers frequently run these tools to generate a comprehensive map of the environment and identify "low-hanging fruit" misconfigurations (like public S3 buckets or unencrypted EBS volumes).

### 1. ScoutSuite (AWS, Azure, GCP, Alibaba)
ScoutSuite is an open-source multi-cloud security-auditing tool. It queries the cloud APIs, gathers configuration data, and generates a detailed HTML report.

Attackers love ScoutSuite because it requires read-only permissions and provides an immediate, easily digestible overview of the entire attack surface.

**Example Usage:**
```bash
# Run against AWS using current environment variables
scout aws

# Run against Azure
scout azure --cli
```

### 2. Cloudsplaining (AWS)
Developed by Salesforce, Cloudsplaining is an AWS IAM Security Assessment tool that identifies violations of least privilege and generates a risk-prioritized HTML report. It specifically highlights roles that allow Privilege Escalation, Data Exfiltration, or Resource Exposure.

**Example Usage:**
```bash
# Download IAM data
cloudsplaining download --profile default

# Scan the data
cloudsplaining scan --exclusions-file exclusions.yml --iam-data default.json
```

## Detection and Mitigation Strategies

Detecting cloud enumeration is notoriously difficult because enumeration tools use the exact same APIs as legitimate administrative tools (like the Azure Portal, AWS Management Console, or Terraform).

### 1. Behavioral Analytics and API Rate Limiting
- **Volume Anomalies**: Alert on sudden spikes in read-only API calls. A user making 500 `Describe*` or `List*` calls in 5 minutes is highly suspicious if their baseline is near zero.
- **User Agent Anomalies**: Many tools use custom user agents (e.g., `Pacu/1.0`, `ScoutSuite/5.0`). While sophisticated attackers will spoof standard `aws-cli` or `Boto3` user agents, catching lazy attackers is easy.
- **Geographic and IP Anomalies**: Alert if API calls originate from unexpected locations, commercial VPNs, or TOR exit nodes.

### 2. Honeytokens and Deception
The most effective way to detect enumeration is via deception.
- **AWS Spacecat / Canarytokens**: Deploy fake AWS access keys or Azure Service Principal credentials in code repositories or local files. If an enumeration tool like Pacu attempts to use these keys, you receive an immediate, high-fidelity alert.
- **Fake Resources**: Create fake, high-value looking S3 buckets or Key Vaults. Monitor logs for any identity attempting to list or read from them.

### 3. Principle of Least Privilege
The damage an enumeration tool can do is directly proportional to the permissions of the compromised identity.
- Do not grant broad `ReadOnlyAccess` or `SecurityAudit` roles to generic application instances or developers unless absolutely necessary.
- Deny access to IAM enumeration endpoints (`iam:ListUsers`, `iam:GetPolicy`) for identities that only need access to specific resources (like a Lambda function that only needs S3 write access).

## Chaining Opportunities

- **Initial Access**: Tools are deployed immediately following the extraction of credentials via `[[27 - Cloud SSRF to Credential Theft — Full Chain]]` or `[[24 - Cloud Metadata Endpoint Cheat Sheet]]`.
- **Privilege Escalation**: Tools like PMapper and Pacu directly map out the paths needed to execute privilege escalation.
- **Lateral Movement**: Tools like AzureHound identify paths to move from a single compromised `[[22 - Azure Service Principal Abuse]]` to global tenant dominance.

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

- `[[22 - Azure Service Principal Abuse]]`
- `[[23 - Azure Managed Identity Abuse]]`
- `[[24 - Cloud Metadata Endpoint Cheat Sheet]]`
- `[[27 - Cloud SSRF to Credential Theft — Full Chain]]`
