---
course: DevSecOps
topic: IaC and GitOps for DevSecOps
tags: [devsecops]
---

## Managing Terraform State Locally

### What is Terraform State?

Terraform state is a file that stores the current state of your infrastructure. It contains information about the resources that Terraform manages, including their IDs, attributes, and dependencies. This state file is crucial for Terraform to understand the current state of your infrastructure and make changes accordingly.

### Why Manage Terraform State Locally?

Managing Terraform state locally means that the state file is stored on the local machine where Terraform is executed. While this approach is simple and straightforward, it has several drawbacks:

- **No Centralization**: Each developer or team member has their own copy of the state file, leading to inconsistencies and potential conflicts.
- **No Version Control**: Local state files are not version-controlled, making it difficult to track changes and roll back to previous states.
- **No Collaboration**: Multiple users cannot simultaneously work on the same infrastructure without risking conflicts and data loss.

### Real-World Example: Local State Issues

In a recent breach, a company experienced significant downtime due to a misconfiguration in their infrastructure. The root cause was that multiple developers were managing the state locally, leading to conflicting changes and a corrupted state file. This incident highlights the importance of centralizing the Terraform state.

---
<!-- nav -->
[[06-Infrastructure as Code (IaC) and GitOps for DevSecOps|Infrastructure as Code (IaC) and GitOps for DevSecOps]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/02-IaC and GitOps for DevSecOps/Configure Remote State for Terraform/00-Overview|Overview]] | [[08-Moving to Remote State Management|Moving to Remote State Management]]
