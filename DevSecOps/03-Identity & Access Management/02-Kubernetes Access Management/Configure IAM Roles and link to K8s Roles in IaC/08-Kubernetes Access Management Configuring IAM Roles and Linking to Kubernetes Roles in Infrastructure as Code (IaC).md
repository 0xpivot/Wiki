---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management: Configuring IAM Roles and Linking to Kubernetes Roles in Infrastructure as Code (IaC)

### Introduction to Kubernetes Access Management

Kubernetes access management is a critical aspect of securing your cluster. It involves controlling who can access the cluster and what actions they can perform. One of the key components of Kubernetes access management is Role-Based Access Control (RBAC), which allows you to define roles and permissions for different users and groups within the cluster.

In many organizations, Kubernetes clusters run on cloud platforms such as Amazon Web Services (AWS). AWS provides Identity and Access Management (IAM) services to manage access to AWS resources. To integrate AWS IAM with Kubernetes RBAC, you need to map AWS IAM principals (users, roles, etc.) to Kubernetes roles and users.

This chapter will guide you through configuring IAM roles and linking them to Kubernetes roles using Infrastructure as Code (IaC) tools like Terraform. We'll cover the necessary background, detailed steps, and provide real-world examples to ensure you have a comprehensive understanding of the process.

### Background Theory

#### What is IAM?

IAM is a web service that enables you to securely control access to AWS resources. IAM allows you to manage users, groups, and permissions. Here are some key concepts:

- **Users**: Individual accounts that can sign in to AWS.
- **Groups**: Collections of users that share similar permissions.
- **Roles**: Temporary credentials that allow users or services to assume specific permissions.

#### What is Kubernetes RBAC?

Kubernetes RBAC is a mechanism for controlling access to the Kubernetes API. It allows you to define roles and permissions for different users and groups within the cluster. Key concepts include:

- **Roles**: Define a set of permissions.
- **RoleBindings**: Bind roles to users or groups.
- **ClusterRoles**: Similar to roles but apply cluster-wide.
- **ClusterRoleBindings**: Bind cluster roles to users or groups.

### Mapping AWS IAM Principals to Kubernetes Roles

To integrate AWS IAM with Kubernetes RBAC, you need to map AWS IAM principals to Kubernetes roles. This mapping is crucial because it ensures that users and roles in AWS have the appropriate permissions in Kubernetes.

#### Steps to Map AWS IAM Principals to Kubernetes Roles

1. **Define the Mapping**: Create a mapping object that defines which AWS IAM principal corresponds to which Kubernetes role.
2. **Create IAM Roles**: Use IaC tools like Terraform to create IAM roles in AWS.
3. **Link IAM Roles to Kubernetes Roles**: Use Kubernetes RBAC to bind these IAM roles to Kubernetes roles.

### Detailed Configuration Using Terraform

Terraform is a popular IaC tool that allows you to define and provision infrastructure as code. We'll use Terraform to create IAM roles and link them to Kubernetes roles.

#### Step 1: Define the Mapping Object

First, define a mapping object that specifies which AWS IAM principal corresponds to which Kubernetes role. This object will be used in your Terraform configuration.

```hcl
locals {
  aws_to_kubernetes_role_mapping = [
    {
      aws_principal = "arn:aws:iam::123456789012:role/example-role"
      kubernetes_user = "example-user"
      kubernetes_role = "example-role"
    },
    {
      aws_principal = "arn:aws:iam::123456789012:user/example-user"
      kubernetes_user = "example-user"
      kubernetes_role = "example-role"
    }
  ]
}
```

#### Step 2: Create IAM Roles in AWS

Next, create IAM roles in AWS using Terraform. Here’s an example of how to create an IAM role:

```hcl
resource "aws_iam_role" "example_role" {
  name = "example-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "example_policy_attachment" {
  role       = aws_iam_role.example_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
}
```

#### Step 3: Link IAM Roles to Kubernetes Roles

Now, link the IAM roles to Kubernetes roles using Kubernetes RBAC. Here’s an example of how to create a `RoleBinding` in Kubernetes:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: example-rolebinding
subjects:
- kind: User
  name: example-user
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: example-role
  apiGroup: rbac.authorization.k8s.io
```

### Complete Example: IAM Roles.tf File

Here’s a complete example of how to create IAM roles and link them to Kubernetes roles using Terraform:

```hcl
# IAM Roles.tf
resource "aws_iam_role" "example_role" {
  name = "example-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "example_policy_attachment" {
  role       = aws_iam_role.example_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ReadOnlyAccess"
}

locals {
  aws_to_kubernetes_role_mapping = [
    {
      aws_principal = aws_iam_role.example_role.arn
      kubernetes_user = "example-user"
      kubernetes_role = "example-role"
    }
  ]
}
```

### Real-World Examples and Recent Breaches

#### Example: CVE-2021-25741

CVE-2021-25741 was a vulnerability in Kubernetes that allowed attackers to escalate privileges by manipulating RBAC configurations. This highlights the importance of proper RBAC setup and regular audits.

#### Example: AWS IAM Misconfiguration

A recent breach involved an AWS IAM misconfiguration that allowed unauthorized access to Kubernetes clusters. Properly mapping IAM roles to Kubernetes roles can help prevent such issues.

### Pitfalls and Common Mistakes

#### Mistake 1: Incorrect Mapping

Ensure that the mapping between AWS IAM principals and Kubernetes roles is correct. Incorrect mapping can lead to unauthorized access.

#### Mistake 2: Missing Permissions

Make sure that the IAM roles have the necessary permissions to perform their intended actions in Kubernetes.

### How to Prevent / Defend

#### Detection

Regularly audit your IAM roles and Kubernetes RBAC configurations to ensure they are correctly set up. Tools like `kubectl auth can-i` can help verify permissions.

#### Prevention

1. **Use Least Privilege Principle**: Grant only the minimum necessary permissions.
2. **Regular Audits**: Conduct regular audits of IAM roles and Kubernetes RBAC configurations.
3. **Secure Coding Practices**: Follow secure coding practices to avoid common mistakes.

#### Secure-Coding Fixes

**Vulnerable Code:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: example-rolebinding
subjects:
- kind: User
  name: example-user
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: example-role
  apiGroup: rbac.authorization.k8s.io
```

**Fixed Code:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: example-rolebinding
subjects:
- kind: User
  name: example-user
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: example-role
  apiGroup: rbac.authorization.k8s.io
```

### Configuration Hardening

#### AWS IAM Hardening

1. **Enable MFA**: Require Multi-Factor Authentication (MFA) for IAM users.
2. **Use IAM Policies**: Use IAM policies to restrict access to specific resources.

#### Kubernetes RBAC Hardening

1. **Least Privilege**: Ensure roles have only the necessary permissions.
2. **Regular Audits**: Regularly review and update RBAC configurations.

### Conclusion

Integrating AWS IAM with Kubernetes RBAC is essential for securing your Kubernetes clusters. By following the steps outlined in this chapter, you can effectively map AWS IAM principals to Kubernetes roles and ensure proper access management.

### Practice Labs

For hands-on practice, consider the following labs:

- **Kubernetes Goat**: A Kubernetes security training platform.
- **OWASP WrongSecrets**: A series of challenges to learn about Kubernetes security.
- **kube-hunter**: A tool to find security issues in Kubernetes clusters.

These labs will help you gain practical experience in configuring IAM roles and linking them to Kubernetes roles.

---
<!-- nav -->
[[07-Kubernetes Access Management Configuring IAM Roles and Linking to K8s Roles in Infrastructure as Code (IaC)|Kubernetes Access Management Configuring IAM Roles and Linking to K8s Roles in Infrastructure as Code (IaC)]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure IAM Roles and link to K8s Roles in IaC/00-Overview|Overview]] | [[09-Kubernetes Access Management Configuring IAM Roles and Linking to Kubernetes Roles in Infrastructure as Code Part 1|Kubernetes Access Management Configuring IAM Roles and Linking to Kubernetes Roles in Infrastructure as Code Part 1]]
