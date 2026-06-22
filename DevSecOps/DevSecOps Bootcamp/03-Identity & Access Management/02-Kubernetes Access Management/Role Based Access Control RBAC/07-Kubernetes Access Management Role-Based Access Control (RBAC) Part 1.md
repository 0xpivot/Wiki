---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management: Role-Based Access Control (RBAC)

### Introduction to Kubernetes Access Management

Kubernetes is a powerful container orchestration platform that allows developers and operations teams to manage and scale applications efficiently. However, with great power comes great responsibility, particularly when it comes to managing access to the Kubernetes cluster. Access management ensures that only authorized entities can interact with the cluster, thereby maintaining the security and integrity of the system.

In Kubernetes, access management is primarily achieved through Role-Based Access Control (RBAC). RBAC is a method of regulating access to resources based on the roles of individual users within an organization. In the context of Kubernetes, RBAC allows administrators to define roles and bind them to users or service accounts, thereby controlling what actions those entities can perform within the cluster.

### Service Accounts in Kubernetes

Before diving into RBAC, it's essential to understand the concept of service accounts in Kubernetes. A service account is an object in Kubernetes that represents an identity for processes running in a Pod. Unlike human users, who might authenticate via usernames and passwords, service accounts are used to represent identities for applications and services running within the cluster.

#### Creating a Service Account

To create a service account, you can use a YAML configuration file. Here’s an example:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-service-account
  namespace: default
```

This configuration creates a service account named `my-service-account` in the `default` namespace. Once created, this service account can be used to grant permissions to the corresponding application or service.

### Roles and Cluster Roles

In Kubernetes, roles and cluster roles are used to define sets of permissions. A role is scoped to a specific namespace, while a cluster role is cluster-wide and can affect resources across all namespaces.

#### Role Configuration

A role defines a set of permissions for a specific namespace. Here’s an example of a role configuration file:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
```

In this example:
- `apiGroups`: Specifies the API group. An empty string `""` refers to the core API group.
- `resources`: Specifies the resources that the role applies to. In this case, it's `pods`.
- `verbs`: Specifies the actions that can be performed on the resources. Here, the verbs are `get`, `list`, and `watch`.

#### Cluster Role Configuration

A cluster role is similar to a role but is cluster-wide. Here’s an example of a cluster role configuration file:

```yaml
apiVersion: rbac.authorization.k8s.io/v
kind: ClusterRole
metadata:
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
```

The structure is identical to a role, but the `ClusterRole` kind indicates that this role applies to the entire cluster.

### Role Bindings and Cluster Role Bindings

Once roles and cluster roles are defined, they need to be bound to subjects (users, groups, or service accounts). This is done using role bindings and cluster role bindings.

#### Role Binding Configuration

A role binding binds a role to a subject within a specific namespace. Here’s an example:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: ServiceAccount
  name: my-service-account
  apiGroup: ""
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

In this example:
- `subjects`: Specifies the subject to which the role is bound. Here, it’s a service account named `my-service-account`.
- `roleRef`: References the role that is being bound. In this case, it’s the `pod-reader` role.

#### Cluster Role Binding Configuration

A cluster role binding binds a cluster role to a subject across the entire cluster. Here’s an example:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: read-pods-global
subjects:
- kind: ServiceAccount
  name: my-service-account
  namespace: default
roleRef:
  kind: ClusterRole
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

The structure is similar to a role binding, but the `ClusterRoleBinding` kind indicates that this binding applies to the entire cluster.

### Example: Metric Server and Prometheus

Let’s consider two common applications: the metric server and Prometheus. Both of these applications require access to certain resources within the Kubernetes cluster.

#### Metric Server

The metric server is a cluster-level resource that collects resource metrics from Kubelets and exposes them in Kubernetes APIs. To ensure that the metric server has the necessary permissions, we can create a service account and bind it to a role.

```yaml
# metric-server-service-account.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: metric-server
  namespace: kube-system

# metric-server-role.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: metric-server
rules:
- apiGroups: [""]
  resources: ["nodes", "nodes/metrics"]
  verbs: ["get"]

# metric-server-role-binding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: metric-server
subjects:
- kind: ServiceAccount
  name: metric-server
  namespace: kube-system
roleRef:
  kind: ClusterRole
  name: metric-server
  apiGroup: rbac.authorization.k8s.io
```

#### Prometheus

Prometheus is a monitoring system that scrapes metrics from various sources. To allow Prometheus to scrape metrics from pods, we can create a service account and bind it to a role.

```yaml
# prometheus-service-account.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: prometheus
  namespace: monitoring

# prometheus-role.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: monitoring
  name: prometheus
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch"]

# prometheus-role-binding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: prometheus
  namespace: monitoring
subjects:
- kind: ServiceAccount
  name: prometheus
  namespace: monitoring
roleRef:
  kind: Role
  name: prometheus
  apiGroup: rbac.authorization.k8s.io
```

### Real-World Examples and CVEs

RBAC is crucial for preventing unauthorized access to Kubernetes clusters. Several high-profile breaches have been attributed to misconfigured RBAC policies.

#### CVE-2020-8558

CVE-2020-8558 is a critical vulnerability in Kubernetes that allowed attackers to escalate privileges and gain full control of the cluster. This vulnerability was due to a flaw in the RBAC implementation, which allowed attackers to bypass RBAC checks and execute arbitrary commands.

**How to Prevent / Defend:**

1. **Regular Audits:** Regularly audit RBAC configurations to ensure that only necessary permissions are granted.
2. **Least Privilege Principle:** Follow the principle of least privilege, granting only the minimum permissions required for each role.
3. **Secure Configurations:** Ensure that RBAC configurations are secure and follow best practices. Use tools like `kube-bench` to check for compliance with CIS benchmarks.
4. **Monitoring:** Implement monitoring and logging to detect unauthorized access attempts.

### Common Pitfalls and Best Practices

#### Pitfall: Overly Permissive Roles

One common pitfall is creating overly permissive roles that grant more permissions than necessary. This can lead to security vulnerabilities if an attacker gains access to a service account with such permissions.

**Best Practice:**
- Define roles with the minimum necessary permissions.
- Regularly review and refine roles to ensure they remain secure.

#### Pitfall: Missing RBAC Configurations

Another pitfall is failing to configure RBAC at all, leaving the cluster open to unauthorized access.

**Best Practice:**
- Always configure RBAC for any new service or application.
- Use tools like `kubectl auth can-i` to verify permissions.

### Hands-On Labs

To practice and reinforce the concepts learned, consider the following hands-on labs:

- **Kubernetes Goat:** A Kubernetes-based security training platform that includes exercises on RBAC.
- **OWASP WrongSecrets:** A series of challenges that cover various aspects of Kubernetes security, including RBAC.
- **Kube-Hunter:** A tool for hunting down security issues in Kubernetes clusters, which can help identify misconfigurations in RBAC policies.

By following these best practices and engaging in hands-on labs, you can ensure that your Kubernetes cluster remains secure and compliant with best practices for access management.

### Conclusion

Role-Based Access Control (RBAC) is a fundamental aspect of securing a Kubernetes cluster. By understanding and properly implementing RBAC, you can ensure that only authorized entities have access to the resources they need, thereby maintaining the security and integrity of your cluster. Regular audits, following the principle of least privilege, and using tools for monitoring and detection are key to maintaining a secure Kubernetes environment.

---
<!-- nav -->
[[06-Introduction to Kubernetes Access Management|Introduction to Kubernetes Access Management]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Role Based Access Control RBAC/00-Overview|Overview]] | [[08-Kubernetes Access Management Role-Based Access Control (RBAC)|Kubernetes Access Management Role-Based Access Control (RBAC)]]
