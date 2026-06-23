---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain how the RBEQ policy and IAM roles are used to manage access in an EKS cluster.**

The Role-Based Access Control (RBEQ) policy in Kubernetes defines the permissions granted to different roles within the cluster. In the context of an Amazon EKS (Elastic Kubernetes Service) cluster, IAM roles are used to map AWS identities to Kubernetes roles. For example, a developer might have very limited read permissions to their specific application namespace, while an admin might have broader view permissions across the entire cluster. By configuring these roles and policies, you ensure that users only have the necessary access to perform their tasks, adhering to the principle of least privilege.

**Q2. How would you configure a feature branch in Git to save the state of your EKS cluster configuration?**

To configure a feature branch in Git to save the state of your EKS cluster configuration, follow these steps:

1. Ensure you have committed all changes related to the EKS cluster configuration in your current branch.
2. Create a new feature branch using `git checkout -b feature-branch-name`.
3. Push the new feature branch to the remote repository using `git push origin feature-branch-name`.

This process allows you to isolate the changes related to the EKS cluster configuration in a separate branch, making it easier to manage and review these changes without affecting the main branch.

**Q3. Why is it important to destroy the EKS cluster after completing the configuration phase?**

Destroying the EKS cluster after completing the configuration phase is crucial for several reasons:

1. **Cost Management**: Running an EKS cluster incurs costs, even if it's not actively being used. Destroying the cluster ensures you don't incur unnecessary charges.
2. **Clean State**: It ensures that the next time you provision the cluster, you start from a clean state, avoiding any residual configurations that could cause issues.
3. **Resource Cleanup**: Destroying the cluster also cleans up all associated resources, ensuring that there are no orphaned resources left behind.

To destroy the EKS cluster, you would use `terraform destroy` after ensuring that all AWS environment variables are cleaned up in a new terminal session. This command will remove all resources created by Terraform and clean the Terraform state.

**Q4. How does the principle of least privilege apply to the access management of an EKS cluster?**

The principle of least privilege (PoLP) is a security concept that restricts access rights for users, applications, and systems to the minimum level necessary to perform their tasks. In the context of an EKS cluster, PoLP is applied as follows:

1. **Role-Based Access Control (RBAC)**: Define roles and permissions in Kubernetes that grant users only the necessary access to perform their jobs. For example, a developer might have read-only access to a specific namespace, while an admin might have broader permissions.
2. **IAM Roles**: Use AWS Identity and Access Management (IAM) roles to map AWS identities to Kubernetes roles. This ensures that AWS users do not need additional privileges beyond what is required for their Kubernetes roles.
3. **Feature Branches**: Use feature branches to manage and isolate changes, ensuring that only necessary changes are pushed to the main branch and that access to sensitive configurations is controlled.

By adhering to PoLP, you minimize the risk of unauthorized access and potential security breaches.

**Q5. What recent real-world examples demonstrate the importance of proper access management in Kubernetes clusters?**

One notable example is the Kubernetes Dashboard vulnerability (CVE-2021-25741), which allowed unauthenticated attackers to execute arbitrary commands on the cluster. This vulnerability highlights the importance of proper access management and the principle of least privilege. If the cluster had been properly configured with strict RBAC policies and limited access, the impact of such vulnerabilities could have been significantly reduced.

Another example is the 2020 incident where a misconfigured Kubernetes cluster led to the exposure of sensitive data due to improper access controls. This underscores the necessity of carefully managing access to Kubernetes resources to prevent unauthorized access and data breaches.

---
<!-- nav -->
[[02-Kubernetes Access Management|Kubernetes Access Management]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/07-Summary and Wrap Up/00-Overview|Overview]]
