---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Introduction to Kubernetes Access Management

Kubernetes is a powerful orchestration platform used to automate deployment, scaling, and management of containerized applications. One of the critical aspects of managing a Kubernetes cluster is ensuring that access to the cluster is properly controlled and restricted. This is achieved through Role-Based Access Control (RBAC), which allows you to specify who can access what resources in your cluster.

### Human User Permissions

In Kubernetes, human users are typically granted access through roles and cluster roles. A **role** defines a set of permissions that apply within a specific namespace, while a **cluster role** defines permissions that apply across the entire cluster. For example, an administrator might be given a cluster role that grants them full administrative access to the cluster, while developers might be given roles that allow them to manage only their own namespaces.

```yaml
# Example of a ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: admin-role
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]

# Example of a Role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: dev-namespace
  name: developer-role
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
```

### Application Users

While human user permissions are crucial, they only cover one aspect of access control. Applications and services also require access to the cluster. These applications can be either internal, running inside the cluster, or external, accessing the cluster from outside. Properly managing application access is essential to maintaining the security and integrity of the cluster.

#### Internal Applications

Internal applications, such as monitoring tools like Prometheus, need access to various resources within the cluster. For instance, Prometheus requires access to all pods to collect metrics. Other microservices might only need access to resources within their specific namespace.

```yaml
# Example of a ServiceAccount for Prometheus
apiVersion: v1
kind: ServiceAccount
metadata:
  name: prometheus
  namespace: monitoring
---
# Example of a RoleBinding for Prometheus
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: prometheus-metrics-reader
  namespace: monitoring
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: metrics-reader
subjects:
- kind: ServiceAccount
  name: prometheus
  namespace: monitoring
```

#### External Applications

External applications, such as Continuous Integration/Continuous Deployment (CI/CD) tools or infrastructure-as-code (IaC) tools like Terraform, also require access to the cluster. These tools might need to deploy applications or configure the cluster itself.

```yaml
# Example of a ServiceAccount for a CI/CD tool
apiVersion: v1
kind: ServiceAccount
metadata:
  name: ci-cd-tool
  namespace: default
---
# Example of a RoleBinding for a CI/CD tool
apiVersion: rbac.authorization.k8s.io/v
kind: RoleBinding
metadata:
  name: ci-cd-deployer
  namespace: default
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: deployer
subjects:
- kind: ServiceAccount
  name: ci-cd-tool
  namespace: default
```

### Service Accounts

Service accounts are Kubernetes resources that represent application users. They are used to authenticate and authorize applications and services that need to interact with the cluster. Each service account has a unique identity and can be assigned roles or cluster roles to define its permissions.

#### Creating a Service Account

To create a service account, you define a `ServiceAccount` resource in a YAML file and apply it to the cluster.

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-service-account
  namespace: default
```

#### Assigning Roles to Service Accounts

Once a service account is created, you can assign roles or cluster roles to it using `RoleBinding` or `ClusterRoleBinding`.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: my-service-account-binding
  namespace: default
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: Role
  name: my-role
subjects:
- kind: ServiceAccount
  name: my-service-account
  namespace: default
```

### Real-World Examples

#### CVE-2021-25741: Kubernetes API Server Privilege Escalation

CVE-2021-25741 is a privilege escalation vulnerability in the Kubernetes API server. An attacker with access to a service account could potentially escalate their privileges by manipulating certain API calls. This highlights the importance of properly configuring and securing service accounts.

```http
POST /apis/rbac.authorization.k8s.io/v1/namespaces/default/rolebindings HTTP/1.1
Host: kubernetes.default.svc.cluster.local
Authorization: Bearer <service-account-token>
Content-Type: application/json

{
  "apiVersion": "rbac.authorization.k8s.io/v1",
  "kind": "RoleBinding",
  "metadata": {
    "name": "escalated-rolebinding"
  },
  "roleRef": {
    "apiGroup": "rbac.authorization.k8s.io",
    "kind": "ClusterRole",
    "name": "admin"
  },
  "subjects": [
    {
      "kind": "ServiceAccount",
      "name": "my-service-account",
      "namespace": "default"
    }
  ]
}
```

#### How to Prevent / Defend

1. **Least Privilege Principle**: Ensure that service accounts are granted only the minimum necessary permissions.
2. **Regular Audits**: Regularly review and audit service account permissions to ensure they are still appropriate.
3. **Secure Token Storage**: Store service account tokens securely and rotate them regularly.
4. **Network Policies**: Implement network policies to restrict access to sensitive resources.
5. **Monitoring and Logging**: Enable monitoring and logging to detect unauthorized access attempts.

```yaml
# Example of a NetworkPolicy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
  namespace: default
spec:
  podSelector: {}
  ingress: []
  egress: []
```

### Common Pitfalls

1. **Overprivileged Service Accounts**: Granting excessive permissions to service accounts can lead to security vulnerabilities.
2. **Improper Token Management**: Storing service account tokens insecurely or failing to rotate them regularly can expose the cluster to attacks.
3. **Insufficient Auditing**: Failing to regularly review and audit service account permissions can result in outdated or overly permissive configurations.

### Conclusion

Properly managing access to a Kubernetes cluster is critical for maintaining its security and integrity. By using RBAC to define and enforce permissions for both human users and application users, you can ensure that only authorized entities have access to the resources they need. Understanding the concepts of roles, cluster roles, and service accounts, and implementing best practices for their use, will help you secure your Kubernetes environment effectively.

### Practice Labs

For hands-on experience with Kubernetes access management, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises on securing Kubernetes clusters.
- **OWASP Juice Shop**: Provides a vulnerable web application that can be deployed on Kubernetes for security testing.
- **Kubernetes Goat**: A vulnerable Kubernetes cluster designed for security training.

These labs will help you gain practical experience in configuring and securing Kubernetes clusters using RBAC and service accounts.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Role Based Access Control RBAC/01-Introduction to Kubernetes Access Management Part 1|Introduction to Kubernetes Access Management Part 1]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Role Based Access Control RBAC/00-Overview|Overview]] | [[03-Introduction to Kubernetes Access Management Part 3|Introduction to Kubernetes Access Management Part 3]]
