---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management: Configuring Roles and ClusterRoles in Infrastructure as Code (IaC)

### Introduction to Kubernetes Access Management

Kubernetes is a powerful container orchestration platform that manages the deployment, scaling, and operation of applications in containers. To ensure the security and integrity of the Kubernetes cluster, proper access management is essential. Access management in Kubernetes is achieved through the use of **Roles** and **ClusterRoles**, which define the permissions granted to users or groups within the cluster.

### Understanding Roles and ClusterRoles

#### What are Roles and ClusterRoles?

- **Roles**: A Role is a set of permissions that apply within a specific namespace. This means that a Role can only grant permissions to resources within the same namespace.
- **ClusterRoles**: A ClusterRole is similar to a Role but applies across the entire cluster. This means that a ClusterRole can grant permissions to resources in any namespace.

#### Why Use Roles and ClusterRoles?

Using Roles and ClusterRoles allows for fine-grained control over who can access and perform actions on Kubernetes resources. By defining roles and cluster roles, you can ensure that users and services only have the minimum necessary permissions required to perform their tasks. This principle is known as **least privilege** and is a fundamental aspect of secure system design.

#### How Roles and ClusterRoles Work

Roles and ClusterRoles are defined using YAML files and can be applied to the cluster using `kubectl` commands. Once defined, these roles can be bound to users or groups via **RoleBindings** and **ClusterRoleBindings**.

### Defining Permissions for Troubleshooting

In the context of the provided lecture, the goal is to allow users to view and troubleshoot various Kubernetes resources such as pods, services, config maps, secrets, and volumes. These permissions are read-only and are essential for monitoring and debugging purposes.

#### Required Permissions

The following permissions are typically required for troubleshooting:

- **get**: Retrieve information about a specific resource.
- **list**: List all instances of a resource type within a namespace.
- **watch**: Watch for changes to a specific resource or a collection of resources.
- **describe**: Provide detailed information about a specific resource.

These permissions are crucial for troubleshooting because they allow users to inspect the current state of resources and diagnose issues.

### Example Role Definition

Let's define a Role that grants the necessary permissions for troubleshooting. We will use YAML to define the role and apply it to the cluster.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: troubleshooter-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps", "secrets"]
  verbs: ["get", "list", "watch", "describe"]
```

This Role definition specifies the following:

- **namespace**: The role is defined in the `default` namespace.
- **resources**: The role grants permissions to `pods`, `services`, `configmaps`, and `secrets`.
- **verbs**: The role allows the `get`, `list`, `watch`, and `describe` operations on these resources.

### Binding the Role to a User or Group

To bind the role to a user or group, we need to create a RoleBinding. Here is an example of a RoleBinding that binds the `troubleshooter-role` to a user named `troubleshooter`.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: troubleshooter-binding
  namespace: default
subjects:
- kind: User
  name: troubleshooter
roleRef:
  kind: Role
  name: troubleshooter-role
  apiGroup: rbac.authorization.k8s.io
```

This RoleBinding binds the `troubleshooter-role` to the user `troubleshooter` in the `default` namespace.

### Extending Permissions to Other Resources

If additional resources need to be accessed, such as deployments, stateful sets, daemon sets, and others, these can be added to the Role definition. Here is an extended example:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: troubleshooter-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps", "secrets"]
  verbs: ["get", "list", "watch", "describe"]
- apiGroups: ["apps"]
  resources: ["deployments", "statefulsets", "daemonsets"]
  verbs: ["get", "list", "watch", "describe"]
```

This extended Role definition includes permissions for `deployments`, `statefulsets`, and `daemonsets` in the `apps` API group.

### Applying the Role and RoleBinding

To apply the Role and RoleBinding to the cluster, use the following `kubectl` commands:

```sh
kubectl apply -f troubleshooter-role.yaml
kubectl apply -f troubleshooter-binding.yaml
```

### Monitoring and Logging

To ensure that the roles and bindings are working correctly, it is important to monitor and log access attempts. Kubernetes provides built-in logging and auditing mechanisms that can be used to track access to resources.

#### Enabling Audit Logging

Audit logging can be enabled by configuring the `audit-policy.yaml` file and restarting the API server. Here is an example audit policy:

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: Metadata
  users: ["system:serviceaccount:kube-system:default"]
- level: Request
  users: ["system:serviceaccount:kube-system:default"]
- level: RequestResponse
  users: ["system:serviceaccount:kube-system:default"]
```

This audit policy logs metadata for all requests and full request and response data for specific users.

### Real-World Examples and Recent Breaches

Recent breaches and vulnerabilities in Kubernetes clusters often involve misconfigured access controls. For example, the **CVE-2021-25741** vulnerability in Kubernetes Dashboard allowed unauthorized access due to misconfigured RBAC rules. Ensuring that roles and bindings are correctly defined and monitored can help prevent such breaches.

### How to Prevent / Defend

#### Detection

To detect misconfigured roles and bindings, regularly review and audit the RBAC configurations. Tools like `kubectl auth can-i` can be used to check if a user or group has the necessary permissions.

#### Prevention

- **Least Privilege Principle**: Always follow the least privilege principle and grant only the minimum necessary permissions.
- **Regular Audits**: Regularly audit RBAC configurations to ensure that roles and bindings are correctly defined.
- **Monitoring and Logging**: Enable audit logging and monitor access attempts to detect any unauthorized access.

#### Secure Coding Fixes

Here is an example of a vulnerable Role definition and its secure counterpart:

**Vulnerable Role Definition:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: insecure-role
rules:
- apiGroups: [""]
  resources: ["*"]
  verbs: ["*"]
```

**Secure Role Definition:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: secure-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "configmaps", "secrets"]
  verbs: ["get", "list", "watch", "describe"]
```

### Conclusion

Properly configuring Roles and ClusterRoles in Kubernetes is essential for ensuring the security and integrity of the cluster. By following the principles of least privilege and regularly auditing RBAC configurations, you can prevent unauthorized access and ensure that users and services only have the necessary permissions.

### Practice Labs

For hands-on practice with Kubernetes access management, consider the following labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security.
- **OWASP WrongSecrets**: A series of challenges for learning about Kubernetes security.
- **kube-hunter**: A tool for hunting down security issues in Kubernetes clusters.

By completing these labs, you can gain practical experience in configuring and securing Kubernetes access management.

---
<!-- nav -->
[[07-Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 4|Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 4]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure K8s Role and ClusterRole in IaC/00-Overview|Overview]] | [[09-Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 6|Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 6]]
