---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Introduction to Kubernetes Access Management

Kubernetes Access Management is a critical aspect of securing your Kubernetes clusters. It ensures that only authorized users and services can interact with the cluster resources. This chapter will delve into configuring Identity and Access Management (IAM) roles and linking them to Kubernetes roles using Infrastructure as Code (IaC) tools like Terraform. We'll cover the theoretical foundations, practical implementation, and security considerations.

### Background Theory

#### What is Kubernetes Access Management?

Kubernetes Access Management involves controlling who can access the Kubernetes API server and what actions they can perform. This includes managing user identities, defining roles and permissions, and enforcing these policies across the cluster.

#### Why is Access Management Important?

Access management is crucial because it prevents unauthorized access to sensitive resources within the cluster. Without proper access controls, malicious actors could exploit vulnerabilities to gain unauthorized access, leading to data breaches, service disruptions, or even complete takeover of the cluster.

#### How Does Access Management Work?

Access management in Kubernetes typically involves:

1. **User Authentication**: Verifying the identity of users and services.
2. **Role-Based Access Control (RBAC)**: Defining roles and permissions based on the principle of least privilege.
3. **Service Accounts**: Managing identities for applications running inside the cluster.

### Setting Up IAM Roles and Linking to Kubernetes Roles

In this section, we will configure IAM roles in AWS and link them to Kubernetes roles using Terraform. We'll start by creating the necessary IAM roles and then integrate them with the Kubernetes cluster.

#### Creating IAM Roles

IAM roles in AWS are used to grant permissions to entities such as EC2 instances, Lambda functions, and Kubernetes pods. These roles can be attached to Kubernetes service accounts to control access to AWS resources.

```terraform
resource "aws_iam_role" "eks_worker_node" {
  name = "eks-worker-node"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
  role       = aws_iam_role.eks_worker_node.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSCNIPolicy"
}
```

This Terraform configuration creates an IAM role named `eks-worker-node` and attaches the `AmazonEKSCNIPolicy` to it. The `assume_role_policy` allows EC2 instances to assume this role.

#### Linking IAM Roles to Kubernetes Roles

To link IAM roles to Kubernetes roles, we need to configure the Kubernetes cluster to recognize these roles. This is typically done using the `aws-auth` ConfigMap in the `kube-system` namespace.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: arn:aws:iam::123456789012:role/eks-worker-node
      username: system:node:{{EC2PrivateDNSName}}
      groups:
        - system:bootstrappers
        - system:nodes
```

This ConfigMap maps the IAM role `eks-worker-node` to the Kubernetes group `system:nodes`. This allows nodes assuming this role to authenticate with the Kubernetes API server.

### Implementing Access Management in Terraform

Now that we have the theoretical background, let's implement the access management configuration in our Terraform script.

#### Step-by-Step Implementation

1. **Define EKS Cluster Configuration**

   In our Terraform script, we need to define the EKS cluster configuration. This includes setting up the necessary attributes to enable IAM roles for service accounts.

   ```hcl
   resource "aws_eks_cluster" "example" {
     name     = "example-cluster"
     role_arn = aws_iam_role.example_cluster.arn

     vpc_config {
       subnet_ids = [aws_subnet.example.id]
     }

     enabled_cluster_log_types = ["api", "audit"]
   }
   ```

2. **Enable IAM Roles for Service Accounts**

   To enable IAM roles for service accounts, we need to set the `manage_aws_auth_config_map` attribute to `true`.

   ```hcl
   resource "aws_eks_cluster" "example" {
     name     = "example-cluster"
     role_arn = aws_iam_role.example_cluster.arn

     vpc_config {
       subnet_ids = [aws_subnet.example.id]
     }

     enabled_cluster_log_types = ["api", "audit"]

     # Enable IAM roles for service accounts
     enable_iam_roles_for_service_accounts = true
   }
   ```

3. **Create IAM Roles and Attach Policies**

   As shown earlier, we create IAM roles and attach policies to them.

   ```hcl
   resource "aws_iam_role" "eks_worker_node" {
     name = "eks-worker-node"

     assume_role_policy = jsonencode({
       Version = "2012-10-17"
       Statement = [
         {
           Action = "sts:AssumeRole"
           Effect = "Allow"
           Principal = {
             Service = "ec2.amazonaws.com"
           }
         },
       ]
     })
   }

   resource "aws_iam_role_policy_attachment" "eks_worker_node_policy" {
     role       = aws__iam_role.eks_worker_node.name
     policy_arn = "arn:aws:iam::aws:policy/AmazonEKSCNIPolicy"
   }
   ```

4. **Configure AWS Auth ConfigMap**

   Finally, we configure the `aws-auth` ConfigMap to map the IAM roles to Kubernetes roles.

   ```yaml
   apiVersion: v1
   kind: ConfigMap
   metadata:
     name: aws-auth
     namespace: kube-system
   data:
     mapRoles: |
       - rolearn: arn:aws:iam::123456789012:role/eks-worker-node
         username: system:node:{{EC2PrivateDNSName}}
         groups:
           - system:bootstrappers
           - system:nodes
   ```

### Real-World Examples and Recent Breaches

#### Example: CVE-2021-25741

CVE-2021-25741 is a critical vulnerability in Kubernetes that allows attackers to bypass RBAC restrictions and execute arbitrary commands on the cluster. This vulnerability highlights the importance of proper access management and regular security audits.

**Impact**: Attackers could gain unauthorized access to sensitive resources and execute arbitrary commands, leading to potential data breaches and service disruptions.

**Mitigation**: Ensure that RBAC policies are correctly configured and regularly audited. Use tools like `kube-bench` to check for compliance with security best practices.

#### Example: AWS IAM Role Hijacking

AWS IAM role hijacking is a common attack vector where attackers exploit misconfigured IAM roles to gain unauthorized access to AWS resources. This can lead to unauthorized access to Kubernetes clusters if IAM roles are improperly linked to Kubernetes service accounts.

**Impact**: Attackers can gain unauthorized access to Kubernetes clusters and execute arbitrary commands, leading to potential data breaches and service disruptions.

**Mitigation**: Regularly audit IAM roles and ensure that they are properly configured with the principle of least privilege. Use tools like `Pacu` to test for IAM role hijacking vulnerabilities.

### Common Pitfalls and Best Practices

#### Common Pitfalls

1. **Improper Role Configuration**: Misconfigured IAM roles can lead to unauthorized access to AWS resources.
2. **Insufficient RBAC Policies**: Inadequate RBAC policies can allow unauthorized access to Kubernetes resources.
3. **Manual User Creation**: Manually creating users can lead to errors and inconsistencies in access management.

#### Best Practices

1. **Use Infrastructure as Code**: Automate the creation and management of IAM roles and Kubernetes roles using IaC tools like Terraform.
2. **Regular Audits**: Regularly audit IAM roles and RBAC policies to ensure they are correctly configured.
3. **Principle of Least Privilege**: Ensure that IAM roles and Kubernetes roles are configured with the principle of least privilege.

### How to Prevent / Defend

#### Detection

1. **Audit Logs**: Regularly review audit logs to detect unauthorized access attempts.
2. **Security Tools**: Use security tools like `kube-bench` and `Pacu` to detect and mitigate vulnerabilities.

#### Prevention

1. **Proper Role Configuration**: Ensure that IAM roles and Kubernetes roles are properly configured with the principle of least privilege.
2. **Regular Audits**: Regularly audit IAM roles and RBAC policies to ensure they are correctly configured.
3. **Automated Management**: Use IaC tools like Terraform to automate the creation and management of IAM roles and Kubernetes roles.

#### Secure Coding Fixes

**Vulnerable Pattern**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: arn:aws:iam::123456789012:role/eks-worker-node
      username: system:node:{{EC2PrivateDNSName}}
      groups:
        - system:bootstrappers
        - system:nodes
```

**Secure Pattern**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: arn:aws:iam::123456789012:role/eks-worker-node
      username: system:node:{{EC2PrivateDNSName}}
      groups:
        - system:bootstrappers
        - system:nodes
  mapUsers: |
    - userarn: arn:aws:iam::123456789012:user/admin
      username: admin
      groups:
        - system:masters
```

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but can provide insights into securing Kubernetes clusters.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **Kubernetes Goat**: A deliberately insecure Kubernetes cluster for practicing Kubernetes security skills.
- **CloudGoat**: A deliberately insecure AWS environment for practicing cloud security skills.

These labs provide practical experience in configuring and securing Kubernetes clusters using IAM roles and RBAC policies.

### Conclusion

Kubernetes Access Management is a critical aspect of securing your Kubernetes clusters. By properly configuring IAM roles and linking them to Kubernetes roles using IaC tools like Terraform, you can ensure that only authorized users and services can interact with the cluster resources. Regular audits and proper role configuration are essential to maintaining the security of your Kubernetes clusters.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure IAM Roles and link to K8s Roles in IaC/01-Introduction to Kubernetes Access Management Part 1|Introduction to Kubernetes Access Management Part 1]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure IAM Roles and link to K8s Roles in IaC/00-Overview|Overview]] | [[03-Kubernetes Access Management Configuring IAM Roles and Linking to K8s Roles in IaC Part 1|Kubernetes Access Management Configuring IAM Roles and Linking to K8s Roles in IaC Part 1]]
