---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management: Configuring Roles and ClusterRoles in Infrastructure as Code (IaC)

### Introduction to Kubernetes Access Management

Kubernetes access management is a critical aspect of securing your Kubernetes cluster. It ensures that users and applications have the appropriate permissions to perform specific actions within the cluster. This is achieved through the use of roles and role bindings, which define the permissions and associate them with specific users or groups.

### Understanding Roles and ClusterRoles

In Kubernetes, roles and cluster roles are used to define sets of permissions. These roles are then associated with users or groups via role bindings. The key difference between roles and cluster roles lies in their scope:

- **Roles**: Define permissions within a specific namespace.
- **ClusterRoles**: Define permissions across the entire cluster.

#### Role Definition

A role is a set of permissions that apply within a specific namespace. Here’s an example of a role definition:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: online-boutique
  name: namespace-viewer
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch"]
```

This role allows the user to view pods and services within the `online-boutique` namespace but does not allow them to modify or delete these resources.

#### ClusterRole Definition

A cluster role, on the other hand, defines permissions that apply across the entire cluster. Here’s an example of a cluster role definition:

```yaml
apiVersion: rbac.authorization.k8s.io/v
kind: ClusterRole
metadata:
  name: cluster-viewer
rules:
- apiGroups: [""]
  resources: ["nodes", "pods"]
  verbs: ["get", "list", "watch"]
```

This cluster role allows the user to view nodes and pods across the entire cluster.

### Mapping Users to Roles

Once roles and cluster roles are defined, they need to be associated with users or groups via role bindings. Role bindings specify which users or groups should have the permissions defined in the roles.

#### RoleBinding Example

Here’s an example of a role binding that associates a user with a role:

```yaml
apiVersion: rbas.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: namespace-viewer-binding
  namespace: online-boutique
subjects:
- kind: User
  name: developer-user
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: namespace-viewer
  apiGroup: rbac.authorization.k8s.io
```

This role binding associates the `developer-user` with the `namespace-viewer` role in the `online-boutique` namespace.

#### ClusterRoleBinding Example

Similarly, here’s an example of a cluster role binding:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: cluster-viewer-binding
subjects:
- kind: User
  name: admin-user
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: cluster-viewer
  apiGroup: rbac.authorization.k8s.io
```

This cluster role binding associates the `admin-user` with the `cluster-viewer` cluster role.

### Differences Between Roles and ClusterRoles

The primary difference between roles and cluster roles is their scope:

- **Roles**: Are scoped to a specific namespace and can only grant permissions within that namespace.
- **ClusterRoles**: Are scoped to the entire cluster and can grant permissions across all namespaces.

This distinction is crucial because it allows for fine-grained control over who can access what within the cluster.

### Real-World Examples and Recent Breaches

Recent breaches and vulnerabilities have highlighted the importance of proper access management in Kubernetes clusters. For example, the Kubernetes API server has been targeted in several attacks where unauthorized access led to data exfiltration and service disruption.

One notable breach involved an attacker gaining access to a Kubernetes cluster due to misconfigured RBAC (Role-Based Access Control) policies. In this case, a role was granted excessive permissions, allowing the attacker to escalate privileges and gain full control over the cluster.

To prevent such breaches, it is essential to follow best practices for RBAC configuration and regularly audit your cluster’s access controls.

### How to Prevent / Defend

#### Detection

Regularly auditing your cluster’s RBAC policies is crucial for detecting misconfigurations and unauthorized access. Tools like `kubectl auth can-i` can help verify permissions for specific users or groups.

```sh
kubectl auth can-i get pods --as=developer-user --namespace=online-boutique
```

This command checks whether the `developer-user` has permission to get pods in the `online-boutique` namespace.

#### Prevention

1. **Least Privilege Principle**: Always grant the minimum necessary permissions required for a user or group to perform their tasks.
2. **Regular Audits**: Regularly review and update RBAC policies to ensure they remain secure and aligned with current requirements.
3. **Automated Scanning**: Use tools like `kube-bench` or `kubescape` to automatically scan your cluster for misconfigurations and security issues.

#### Secure Coding Fixes

Here’s an example of a vulnerable role binding and its secure counterpart:

**Vulnerable Role Binding:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: vulnerable-binding
  namespace: online-boutique
subjects:
- kind: User
  name: developer-user
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: full-access-role
  apiGroup: rbac.authorization.k8s.io
```

**Secure Role Binding:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: secure-binding
  namespace: online-boutique
subjects:
- kind: User
  name: developer-user
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: namespace-viewer
  apiGroup: rbac.authorization.k8s.io
```

In the secure version, the `developer-user` is only granted the `namespace-viewer` role, which limits their permissions to viewing pods and services in the `online-boutique` namespace.

### Hands-On Labs

To practice configuring roles and role bindings in Kubernetes, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a module on Kubernetes security, including RBAC configuration.
- **OWASP Juice Shop**: A deliberately insecure web application that includes Kubernetes deployment scenarios.
- **Kubernetes Goat**: A Kubernetes-based security training platform that covers various aspects of Kubernetes security, including RBAC.

These labs provide practical experience in configuring and managing Kubernetes access controls.

### Conclusion

Proper configuration of roles and role bindings is essential for securing your Kubernetes cluster. By understanding the differences between roles and cluster roles, and by following best practices for RBAC configuration, you can ensure that your cluster remains secure and resilient against unauthorized access.

By regularly auditing your RBAC policies and using automated scanning tools, you can detect and prevent potential security issues. Additionally, practicing with hands-on labs will help solidify your understanding and skills in Kubernetes access management.

---
<!-- nav -->
[[08-Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 5|Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 5]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure K8s Role and ClusterRole in IaC/00-Overview|Overview]] | [[10-Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 7|Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 7]]
