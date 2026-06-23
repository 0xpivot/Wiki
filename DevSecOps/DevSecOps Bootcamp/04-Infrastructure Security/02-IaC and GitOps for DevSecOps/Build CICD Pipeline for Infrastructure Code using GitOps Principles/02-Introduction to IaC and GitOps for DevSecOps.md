---
course: DevSecOps
topic: IaC and GitOps for DevSecOps
tags: [devsecops]
---

## Introduction to IaC and GitOps for DevSecOps

### What is Infrastructure as Code (IaC)?

Infrastructure as Code (IaC) is the practice of managing and provisioning computer data centers through machine-readable definition files, rather than physical hardware configuration or interactive configuration tools. This approach allows infrastructure to be treated as software, enabling developers and operations teams to manage infrastructure changes in a consistent and repeatable manner.

**Why IaC Matters:**
- **Consistency:** Ensures that environments are consistently configured across different stages (development, testing, production).
- **Automation:** Reduces manual errors and speeds up deployment processes.
- **Version Control:** Allows tracking of changes and rollbacks to previous states.
- **Collaboration:** Facilitates better collaboration among team members by providing a shared repository for infrastructure definitions.

### What is GitOps?

GitOps is an operational framework that uses Git as a single source of truth for all infrastructure and application configurations. It extends the principles of IaC by applying continuous delivery practices to infrastructure management. In GitOps, the desired state of the system is stored in a Git repository, and any changes to the infrastructure are made through pull requests, which can be reviewed and merged by authorized personnel.

**Why GitOps Matters:**
- **Centralized Management:** Simplifies management by centralizing all infrastructure definitions in a single Git repository.
- **Auditing and Compliance:** Provides a clear audit trail of all changes made to the infrastructure.
- **Automated Rollouts:** Enables automated rollouts and rollbacks of infrastructure changes.
- **Security:** Enhances security by enforcing strict change control processes through pull requests and approvals.

### Build CICD Pipeline for Infrastructure Code Using GitOps Principles

In this section, we will walk through the process of building a Continuous Integration and Continuous Deployment (CI/CD) pipeline for infrastructure code using GitOps principles. We will use GitLab as our CI/CD platform and Terraform as our IaC tool.

#### Setting Up the GitLab Pipeline Definition

To start, we need to create a GitLab pipeline definition file. This file will specify the stages and jobs that make up our CI/CD pipeline.

```yaml
# .gitlab-ci.yml
image: hashicorp/terraform:latest

stages:
  - init
  - plan
  - apply

variables:
  TF_LOG: "TRACE"
  TF_LOG_PATH: "/tmp/terraform.log"

init:
  stage: init
  script:
    - terraform init

plan:
  stage: plan
  script:
    - terraform plan -out=tfplan

apply:
  stage: apply
  script:
    - terraform apply -auto-approve tfplan
```

#### Explanation of the Pipeline Definition

- **Stages:** The pipeline is divided into three stages: `init`, `plan`, and `apply`.
  - `init`: Initializes the Terraform working directory.
  - `plan`: Creates a detailed execution plan.
  - `apply`: Applies the changes based on the plan.

- **Image:** We use the `hashicorp/terraform:latest` Docker image for all jobs. This ensures consistency across all stages.

- **Variables:** We set `TF_LOG` and `TF_LOG_PATH` to enable detailed logging for debugging purposes.

#### Detailed Steps for Each Stage

##### Init Stage

The `init` stage initializes the Terraform working directory. This step is crucial because it sets up the necessary backend and downloads any required plugins.

```bash
terraform init
```

- **Purpose:** Initializes the Terraform working directory.
- **Output:** Logs the initialization process, including any plugins downloaded.

##### Plan Stage

The `plan` stage creates a detailed execution plan. This step is important because it allows us to review the proposed changes before applying them.

```bash
terraform plan -out=tfplan
```

- **Purpose:** Generates a detailed execution plan.
- **Output:** A file named `tfplan` containing the execution plan.

##### Apply Stage

The `apply` stage applies the changes based on the plan. This step is critical because it actually modifies the infrastructure.

```bash
terraform apply -auto-approve tfplan
```

- **Purpose:** Applies the changes based on the plan.
- **Output:** Logs the application process, including any resources created or modified.

### Real-World Example: Recent Breaches and CVEs

#### Example: CVE-2021-21277

CVE-2021-21277 is a vulnerability in Terraform that allows unauthorized access to sensitive information due to improper handling of credentials. This vulnerability highlights the importance of proper credential management and secure coding practices.

**Impact:**
- Unauthorized access to sensitive information.
- Potential compromise of infrastructure.

**Detection:**
- Monitor logs for unauthorized access attempts.
- Use security tools to scan for vulnerabilities.

**Prevention:**
- Use secure credential management practices.
- Regularly update and patch Terraform installations.

#### Secure Coding Practices

Here is an example of how to securely manage credentials in Terraform:

**Vulnerable Code:**

```hcl
provider "aws" {
  access_key = "AKIAIOSFODNN7EXAMPLE"
  secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
}
```

**Secure Code:**

```hcl
provider "aws" {
  access_key = var.aws_access_key
  secret_key = var.aws_secret_key
}

variable "aws_access_key" {
  type = string
  sensitive = true
}

variable "aws_secret_key" {
  type = string
  sensitive = true
}
```

- **Explanation:** By using variables and marking them as sensitive, we ensure that credentials are not hardcoded in the Terraform configuration.

### Mermaid Diagrams

#### Pipeline Topology

```mermaid
graph TD
  A[Init] --> B[Plan]
  B --> C[Apply]
```

#### Request/Response Flow

```mermaid
sequenceDiagram
  participant User
  participant GitLab
  participant Terraform

  User->>GitLab: Commit Changes
  GitLab->>Terraform: Run Init
  Terraform-->>GitLab: Init Complete
  GitLab->>Terraform: Run Plan
  Terraform-->>GitLab: Plan Complete
  GitLab->>Terraform: Run Apply
  Terraform-->>GitLab: Apply Complete
```

### Common Pitfalls and How to Avoid Them

#### Pitfall: Hardcoding Credentials

**Explanation:** Hardcoding credentials in Terraform configuration files can lead to unauthorized access and compromise of infrastructure.

**How to Avoid:**
- Use variables and mark them as sensitive.
- Store credentials in a secure vault or secrets manager.

#### Pitfall: Improper Logging

**Explanation:** Lack of proper logging can make it difficult to diagnose issues and track changes.

**How to Avoid:**
- Enable detailed logging in Terraform.
- Store logs in a centralized location for easy access.

### Hands-On Labs

For practical experience with IaC and GitOps, consider the following labs:

- **PortSwigger Web Security Academy:** Focuses on web application security but includes modules on IaC and GitOps.
- **OWASP Juice Shop:** A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application):** Another popular web application for security training.

These labs provide a hands-on environment to practice and reinforce the concepts learned in this chapter.

### Conclusion

By following the principles of IaC and GitOps, organizations can achieve greater consistency, automation, and security in their infrastructure management. The steps outlined in this chapter provide a comprehensive guide to setting up a CI/CD pipeline for infrastructure code using GitOps principles. Through real-world examples, secure coding practices, and hands-on labs, readers can gain a deep understanding of these concepts and apply them effectively in their own projects.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/02-IaC and GitOps for DevSecOps/Build CICD Pipeline for Infrastructure Code using GitOps Principles/01-Introduction to IaC and GitOps for DevSecOps Part 1|Introduction to IaC and GitOps for DevSecOps Part 1]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/02-IaC and GitOps for DevSecOps/Build CICD Pipeline for Infrastructure Code using GitOps Principles/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/02-IaC and GitOps for DevSecOps/Build CICD Pipeline for Infrastructure Code using GitOps Principles/03-Introduction to Infrastructure as Code (IaC) and GitOps for DevSecOps Part 1|Introduction to Infrastructure as Code (IaC) and GitOps for DevSecOps Part 1]]
