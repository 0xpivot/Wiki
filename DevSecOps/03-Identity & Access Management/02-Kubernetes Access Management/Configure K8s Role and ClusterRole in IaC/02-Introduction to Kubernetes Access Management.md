---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Introduction to Kubernetes Access Management

Kubernetes access management is a critical aspect of securing your cluster. It ensures that only authorized entities can perform specific actions within the cluster. This chapter will delve into configuring `Role` and `ClusterRole` using Infrastructure as Code (IaC) tools such as Terraform. We'll cover the creation of users, roles, and policies, and discuss how to manage these components securely.

### Background Theory

Before diving into the practical aspects, it's essential to understand the theoretical underpinnings of Kubernetes access management.

#### Kubernetes Users and Roles

In Kubernetes, users are typically defined outside the cluster, often through an external Identity Provider (IdP). These users are then mapped to Kubernetes identities using `User` objects. Roles and ClusterRoles define the permissions granted to these users.

- **Users**: Represent individual identities that interact with the cluster.
- **Roles**: Define a set of permissions that can be granted to users or groups within a namespace.
- **ClusterRoles**: Similar to Roles, but they apply across the entire cluster, not just within a single namespace.

#### Role-Based Access Control (RBAC)

RBAC is a method of controlling access to resources based on the roles of individual users within an organization. In Kubernetes, RBAC is implemented using `Role`, `ClusterRole`, `RoleBinding`, and `ClusterRoleBinding`.

- **Role**: A collection of permissions that apply within a specific namespace.
- **ClusterRole**: A collection of permissions that apply across the entire cluster.
- **RoleBinding**: Binds a Role to a set of subjects (users, groups, or service accounts) within a namespace.
- **ClusterRoleBinding**: Binds a ClusterRole to a set of subjects across the entire cluster.

### Creating Users in AWS

Let's start by creating users in AWS that will interact with the Kubernetes cluster. We'll create two users: `Kubernetes admin` and `Kubernetes developer`.

#### Creating the `Kubernetes admin` User

1. **Navigate to the AWS IAM Console**:
   - Go to the AWS Management Console.
   - Navigate to the IAM section.

2. **Create a New User**:
   - Click on "Users" in the left-hand menu.
   - Click on "Add user".
   - Enter the username `Kubernetes admin`.
   - Select "Programmatic access" since this user will only interact with the cluster via the command line interface (CLI).

3. **Set Permissions**:
   - Leave the "Access key ID" and "Secret access key" unchecked since this user does not need access to the AWS Management Console.
   - Proceed to the next step.

4. **Attach Policies**:
   - Since this is a Kubernetes admin user, it does not need direct permissions on AWS resources. However, it should be able to assume an IAM role.
   - Create a new policy to allow the `sts:AssumeRole` action.

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Resource": "*"
        }
    ]
}
```

- Attach this policy to the `Kubernetes admin` user.

#### Creating the `Kubernetes developer` User

Repeat the above steps to create the `Kubernetes developer` user. Ensure that this user also has the necessary permissions to assume an IAM role.

### Configuring Roles and ClusterRoles Using Terraform

Now that we have created the users, let's configure the roles and cluster roles using Terraform.

#### Setting Up Terraform

1. **Initialize Terraform**:
   - Ensure you have Terraform installed.
   - Initialize your Terraform project:

```bash
terraform init
```

2. **Define Variables**:
   - Define variables for the user names and other relevant information.

```hcl
variable "kubernetes_admin_user" {
  default = "Kubernetes admin"
}

variable "kubernetes_developer_user" {
  default = "Kubernetes developer"
}
```

3. **Create Roles and ClusterRoles**:
   - Define the roles and cluster roles in your Terraform configuration.

```hcl
resource "kubernetes_role" "admin" {
  metadata {
    name      = "admin-role"
    namespace = "default"
  }

  rule {
    api_groups   = ["*"]
    resources    = ["*"]
    verbs        = ["*"]
  }
}

resource "kubernetes_cluster_role" "developer" {
  metadata {
    name = "developer-cluster-role"
  }

  rule {
    api_groups   = [""]
    resources    = ["pods", "services"]
    verbs        = ["get", "list", "watch"]
  }
}
```

4. **Bind Roles to Users**:
   - Bind the roles to the respective users.

```hcl
resource "kubernetes_role_binding" "admin-binding" {
  metadata {
    name      = "admin-binding"
    namespace = "default"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = kubernetes_role.admin.metadata[0].name
  }

  subject {
    kind      = "User"
    name      = var.kubernetes_admin_user
    api_group = ""
  }
}

resource "kubernetes_cluster_role_binding" "developer-binding" {
  metadata {
    name = "developer-binding"
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = kubernetes_cluster_role.developer.metadata[0].name
  }

  subject {
    kind      = "User"
    name      = var.k_ubernetes_developer_user
    api_group = ""
  }
}
```

### Real-World Examples and Recent Breaches

#### Example: CVE-2021-25741

CVE-2021-25741 was a critical vulnerability in Kubernetes that allowed attackers to bypass RBAC restrictions and gain unauthorized access to the cluster. This vulnerability highlights the importance of proper RBAC configuration and regular audits.

- **Impact**: Attackers could execute arbitrary commands and gain elevated privileges.
- **Mitigation**: Ensure that RBAC policies are strictly enforced and regularly reviewed.

#### Example: AWS IAM Role Assumption

The ability to assume an IAM role is crucial for cross-account access and automation. However, misconfigured policies can lead to privilege escalation attacks.

- **Example**: An attacker might exploit a misconfigured policy to assume an IAM role with elevated permissions.
- **Mitigation**: Use least privilege principles and regularly audit IAM policies.

### Common Pitfalls and How to Avoid Them

#### Overly Permissive Policies

One common pitfall is creating overly permissive policies that grant more access than necessary. This can lead to security vulnerabilities.

- **How to Avoid**: Always follow the principle of least privilege. Grant only the minimum permissions required for a user or service account to perform their tasks.

#### Misconfigured RoleBindings

Misconfigured RoleBindings can lead to unintended access to resources.

- **How to Avoid**: Regularly review and audit RoleBindings to ensure they align with organizational policies.

### How to Prevent / Defend

#### Detection

- **Audit Logs**: Enable and monitor audit logs to detect unauthorized access attempts.
- **Security Tools**: Use security tools like Falco or Aqua Security to detect and alert on suspicious activities.

#### Prevention

- **Least Privilege**: Implement the principle of least privilege by granting minimal permissions.
- **Regular Audits**: Conduct regular audits of RBAC configurations to identify and mitigate potential risks.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of a policy:

**Vulnerable Policy**:

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

**Secure Policy**:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": "sts:AssumeRole",
            "Resource": "*"
        }
    ]
}
```

### Complete Example: Full HTTP Request and Response

Here’s a complete example of a full HTTP request and response for creating a role binding using the Kubernetes API.

**HTTP Request**:

```http
POST /apis/rbac.authorization.k8s.io/v1/namespaces/default/rolebindings HTTP/1.1
Host: <your-kubernetes-api-server>
Authorization: Bearer <your-token>
Content-Type: application/json

{
  "apiVersion": "rbac.authorization.k8s.io/v1",
  "kind": "RoleBinding",
  "metadata": {
    "name": "admin-binding",
    "namespace": "default"
  },
  "roleRef": {
    "apiGroup": "rbac.authorization.k8s.io",
    "kind": "Role",
    "name": "admin-role"
  },
  "subjects": [
    {
      "kind": "User",
      "name": "Kubernetes admin",
      "apiGroup": ""
    }
  ]
}
```

**HTTP Response**:

```http
HTTP/1.1 201 Created
Content-Type: application/json
Date: Mon, 01 Jan 2024 00:00:00 GMT
Content-Length: 1024

{
  "kind": "RoleBinding",
  "apiVersion": "rbac.authorization.k8s.io/v1",
  "metadata": {
    "name": "admin-binding",
    "namespace": "default",
    "selfLink": "/apis/rbac.authorization.k8s.io/v1/namespaces/default/rolebindings/admin-binding",
    "uid": "1234567890abcdef1234567890abcdef",
    "resourceVersion": "123456789",
    "creationTimestamp": "2024-01-01T00:00:00Z"
  },
  "roleRef": {
    "apiGroup": "rbac.authorization.k8s.io",
    "kind": "Role",
    "name": "admin-role"
  },
  "subjects": [
    {
      "kind": "User",
      "name": "Kubernetes admin",
      "apiGroup": ""
    }
  ]
}
```

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web security, including Kubernetes access management.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **Kubernetes Goat**: A security-focused Kubernetes environment for learning and testing security practices.

These labs provide a controlled environment to practice and reinforce the concepts covered in this chapter.

### Conclusion

Properly configuring Kubernetes access management using IaC tools like Terraform is crucial for maintaining the security and integrity of your cluster. By following the principles of least privilege and conducting regular audits, you can minimize the risk of unauthorized access and ensure that your cluster remains secure.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure K8s Role and ClusterRole in IaC/01-Introduction to Kubernetes Access Management Part 1|Introduction to Kubernetes Access Management Part 1]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure K8s Role and ClusterRole in IaC/00-Overview|Overview]] | [[03-Kubernetes Access Management Configuring Role and ClusterRole in Infrastructure as Code (IaC)|Kubernetes Access Management Configuring Role and ClusterRole in Infrastructure as Code (IaC)]]
