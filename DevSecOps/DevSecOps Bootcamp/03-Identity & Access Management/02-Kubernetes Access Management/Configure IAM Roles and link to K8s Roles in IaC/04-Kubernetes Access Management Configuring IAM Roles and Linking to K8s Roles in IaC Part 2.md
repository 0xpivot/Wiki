---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management: Configuring IAM Roles and Linking to K8s Roles in IaC

### Introduction to Kubernetes Access Management

Kubernetes access management is a critical aspect of securing your Kubernetes clusters. It ensures that only authorized entities can perform specific actions within the cluster. This includes controlling who can create, modify, or delete resources, as well as who can view the current state of the cluster. Proper access management helps prevent unauthorized access and potential security breaches.

### Human Users and Cluster Privileges

One of the most important security practices is to avoid granting direct access to the cluster to human users. Direct access typically means having full administrative privileges, which can lead to significant security risks. For instance, if a human user with full privileges is compromised, an attacker could gain complete control over the cluster, potentially leading to data breaches, service disruptions, or other malicious activities.

#### Example: CVE-2021-25741

CVE-2021-25741 is a real-world example where a misconfigured Kubernetes cluster allowed unauthorized access due to improper role management. In this case, a misconfigured `ClusterRole` and `RoleBinding` allowed a low-privileged user to escalate their privileges and gain full administrative access to the cluster. This highlights the importance of carefully managing roles and permissions.

### Automated Pipelines and Infrastructure as Code (IaC)

To mitigate these risks, it is recommended to enforce changes to the cluster through automated pipelines and Infrastructure as Code (IaC). This approach ensures that all changes are tracked, reviewed, and tested before being applied to the cluster. By using IaC tools like Terraform, Ansible, or Helm charts, you can maintain a consistent and auditable state of your infrastructure.

#### Example: Using Terraform for IaC

Here’s an example of how you might use Terraform to manage Kubernetes resources:

```hcl
provider "kubernetes" {
  config_path = "~/.kube/config"
}

resource "kubernetes_namespace" "example" {
  metadata {
    name = "example"
  }
}

resource "kubernetes_service_account" "example" {
  metadata {
    name      = "example"
    namespace = kubernetes_namespace.example.metadata[0].name
  }
}

resource "kubernetes_role" "example" {
  metadata {
    name      = "example"
    namespace = kubernetes_namespace.example.metadata[0].name
  }

  rule {
    api_groups   = [""]
    resources    = ["pods"]
    verbs        = ["get", "list", "watch"]
  }
}

resource "kubernetes_role_binding" "example" {
  metadata {
    name      = "example"
    namespace = kubernetes_namespace.example.metadata[0].name
  }

  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "Role"
    name      = kubernetes_role.example.metadata[0].name
  }

  subject {
    kind      = "ServiceAccount"
    name      = kubernetes_service_account.example.metadata[0].name
    namespace = kubernetes_namespace.example.metadata[0].name
  }
}
```

This Terraform configuration creates a namespace, a service account, a role, and a role binding. The role grants read-only access to pods within the namespace, and the role binding associates the role with the service account.

### Role-Based Access Control (RBAC)

Role-Based Access Control (RBAC) is a method of regulating access to resources based on the roles of individual users within an organization. In Kubernetes, RBAC is implemented using `ClusterRole`, `Role`, `RoleBinding`, and `ClusterRoleBinding`.

#### ClusterRole vs. Role

- **ClusterRole**: Defines a set of permissions at the cluster level. These permissions can be applied to any namespace.
- **Role**: Defines a set of permissions within a specific namespace.

#### RoleBinding vs. ClusterRoleBinding

- **RoleBinding**: Binds a `Role` to a user, group, or service account within a specific namespace.
- **ClusterRoleBinding**: Binds a `ClusterRole` to a user, group, or service account across the entire cluster.

### Configuring IAM Roles and Linking to K8s Roles in IaC

To configure IAM roles and link them to Kubernetes roles in IaC, you need to define the necessary roles and bindings in your IaC scripts. Here’s a step-by-step guide:

1. **Define IAM Roles**: Create IAM roles in your cloud provider (e.g., AWS, GCP) that correspond to the roles you want to use in Kubernetes.
2. **Link IAM Roles to Kubernetes Roles**: Use the cloud provider’s integration with Kubernetes to map IAM roles to Kubernetes roles.

#### Example: AWS IAM Roles and Kubernetes RBAC

In AWS, you can use the `aws-auth` ConfigMap to map IAM roles to Kubernetes roles. Here’s an example:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: arn:aws:iam::123456789012:role/k8s-admin
      username: system:node:{{EC2PrivateDNSName}}
      groups:
        - system:masters
```

This ConfigMap maps the IAM role `k8s-admin` to the `system:masters` group in Kubernetes, which grants full administrative privileges.

### Read-Only Access for Troubleshooting

For troubleshooting purposes, it is often useful to grant read-only access to certain users or service accounts. This allows them to inspect the state of the cluster without the ability to make changes.

#### Example: Read-Only Role

Here’s an example of a read-only role:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: read-only
rules:
- apiGroups: [""]
  resources: ["pods", "nodes", "services", "deployments", "replicasets"]
  verbs: ["get", "list", "watch"]
```

This `ClusterRole` grants read-only access to various resources in the cluster.

### Automating Changes Through Pipelines

To ensure that all changes to the cluster are made through automated pipelines, you can use tools like Jenkins, GitLab CI/CD, or Argo CD. These tools can integrate with your IaC scripts to apply changes in a controlled and auditable manner.

#### Example: GitLab CI/CD Pipeline

Here’s an example of a GitLab CI/CD pipeline that applies changes using Terraform:

```yaml
stages:
  - validate
  - plan
  - apply

validate:
  stage: validate
  script:
    - terraform init
    - terraform validate

plan:
  stage: plan
  script:
    - terraform init
    - terraform plan -out=tfplan

apply:
  stage: apply
  script:
    - terraform apply -auto-approve tfplan
  when: manual
```

This pipeline validates the Terraform configuration, plans the changes, and then applies them manually.

### How to Prevent / Defend

#### Detection

To detect unauthorized access attempts, you can use Kubernetes audit logs. These logs record all API calls made to the Kubernetes API server, allowing you to monitor and analyze access patterns.

#### Prevention

1. **Limit Direct Access**: Avoid granting direct access to the cluster to human users. Instead, use service accounts and roles for automation.
2. **Use IaC Tools**: Enforce changes through IaC tools like Terraform or Ansible.
3. **Audit Logs**: Enable and monitor Kubernetes audit logs to detect unauthorized access attempts.
4. **Network Policies**: Use Kubernetes Network Policies to restrict traffic between pods and namespaces.

#### Secure Coding Fixes

Here’s an example of a vulnerable configuration and its secure counterpart:

**Vulnerable Configuration:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: full-access
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
```

**Secure Configuration:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: limited-access
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch"]
```

The secure configuration limits the permissions to specific resources and verbs, reducing the risk of unauthorized access.

### Conclusion

Properly configuring IAM roles and linking them to Kubernetes roles in IaC is crucial for securing your Kubernetes clusters. By following best practices such as limiting direct access, using automated pipelines, and monitoring audit logs, you can significantly reduce the risk of unauthorized access and potential security breaches.

### Practice Labs

For hands-on practice with Kubernetes access management, consider the following labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security.
- **OWASP WrongSecrets**: A series of challenges to learn about Kubernetes security.
- **kube-hunter**: A tool for finding security issues in Kubernetes clusters.

These labs provide practical experience in configuring and securing Kubernetes clusters.

---
<!-- nav -->
[[03-Kubernetes Access Management Configuring IAM Roles and Linking to K8s Roles in IaC Part 1|Kubernetes Access Management Configuring IAM Roles and Linking to K8s Roles in IaC Part 1]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure IAM Roles and link to K8s Roles in IaC/00-Overview|Overview]] | [[05-Kubernetes Access Management Configuring IAM Roles and Linking to K8s Roles in IaC|Kubernetes Access Management Configuring IAM Roles and Linking to K8s Roles in IaC]]
