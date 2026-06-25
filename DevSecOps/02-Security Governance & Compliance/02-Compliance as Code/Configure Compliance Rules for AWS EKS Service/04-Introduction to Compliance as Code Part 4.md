---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## Introduction to Compliance as Code

Compliance as Code is a practice that integrates compliance requirements into the development and deployment processes through automated tools and configurations. This approach ensures that systems adhere to regulatory standards and internal policies throughout their lifecycle. In the context of AWS Elastic Kubernetes Service (EKS), compliance as code involves configuring and enforcing compliance rules using AWS Config and other services.

### Why Compliance as Code?

Compliance as Code is essential because it automates the enforcement of compliance rules, reducing the risk of human error and ensuring consistent adherence to regulations. This is particularly important in environments like EKS, where multiple teams may manage different clusters, leading to potential inconsistencies in compliance.

### How Compliance as Code Works

Compliance as Code works by defining compliance rules in code and using automation tools to enforce these rules. In AWS, this typically involves:

1. **Defining Compliance Rules**: Using AWS Config to define rules that check for specific configurations.
2. **Enforcing Compliance**: Automatically evaluating resources against these rules and taking corrective actions if necessary.
3. **Monitoring Compliance**: Continuously monitoring resources to ensure ongoing compliance.

### Example Scenario

Consider an organization with multiple EKS clusters managed by different teams. Each team might configure their clusters differently, leading to potential compliance issues. By implementing Compliance as Code, the organization can ensure that all clusters adhere to the same set of compliance rules.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Compliance Rules for AWS EKS Service/03-Introduction to Compliance as Code Part 3|Introduction to Compliance as Code Part 3]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Compliance Rules for AWS EKS Service/00-Overview|Overview]] | [[05-Introduction to Compliance as Code|Introduction to Compliance as Code]]
