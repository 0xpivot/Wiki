---
course: DevSecOps
topic: Compliance as Code
tags: [devsecops]
---

## Introduction to Compliance as Code

Compliance as Code is an approach to ensuring that your infrastructure and applications adhere to regulatory requirements and internal policies through automated checks and configurations. This method leverages Infrastructure as Code (IaC) principles to define and enforce compliance rules programmatically. In the context of AWS Elastic Kubernetes Service (EKS), this means setting up automated checks to ensure that your EKS clusters and associated resources comply with specified standards.

### Why Compliance as Code?

Compliance as Code is essential because it helps organizations maintain regulatory compliance and internal policies in a scalable and consistent manner. Traditional manual compliance checks can be time-consuming and error-prone, whereas automated checks can run continuously and provide immediate feedback on any deviations from the defined policies.

### Key Concepts

- **AWS Config**: A service that enables you to assess, audit, and record changes to your AWS resources. It provides a way to continuously monitor and record the configuration of your resources.
- **Config Rules**: Customizable rules that you can create to check the compliance of your AWS resources against specific criteria.
- **EKS Cluster**: A managed Kubernetes service provided by AWS that simplifies the deployment, scaling, and operations of Kubernetes clusters.

### Example Scenario

Consider a scenario where you have an EKS cluster used for critical business operations. You want to ensure that the cluster is always running a recent version of Kubernetes to benefit from the latest security patches and features. Additionally, you want to ensure that SSH access to the nodes is restricted to prevent unauthorized access.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Compliance Rules for AWS EKS Service/04-Introduction to Compliance as Code Part 4|Introduction to Compliance as Code Part 4]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/02-Compliance as Code/Configure Compliance Rules for AWS EKS Service/00-Overview|Overview]] | [[06-Compliance Checks for EKS Clusters|Compliance Checks for EKS Clusters]]
