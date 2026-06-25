---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management: Role-Based Access Control (RBAC)

### Introduction to Kubernetes Access Management

Kubernetes is a powerful orchestration platform designed to manage containerized applications at scale. One of the critical aspects of managing such a platform is ensuring that access to resources is controlled and secure. This is achieved through Role-Based Access Control (RBAC), which allows administrators to define and enforce policies that determine who can access what resources within the Kubernetes cluster.

### Understanding Roles and Cluster Roles

In Kubernetes, roles and cluster roles are fundamental components of RBAC. A **role** is a set of permissions that apply to a specific namespace. On the other hand, a **cluster role** is a set of permissions that apply across the entire cluster, making it suitable for administrative tasks that span multiple namespaces.

#### Role Definition

A role is defined within a specific namespace and can grant permissions to resources within that namespace. Here’s an example of a role definition:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
```

This role grants the ability to read pods within the `default` namespace.

#### Cluster Role Definition

A cluster role, however, is defined at the cluster level and can grant permissions to resources across all namespaces. Here’s an example of a cluster role definition:

```yaml
apiVersion: rbac.authorization.k8s.io/v
kind: ClusterRole
metadata:
  name: admin-cluster-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "deployments"]
  verbs: ["get", "watch", "list", "create", "update", "patch", "delete"]
```

This cluster role grants comprehensive permissions to various resources across the entire cluster.

### Admin Group and Cluster Role Binding

To assign these roles and cluster roles to specific users or groups, Kubernetes uses role bindings and cluster role bindings. A **role binding** associates a role with a user or group within a specific namespace, whereas a **cluster role binding** associates a cluster role with a user or group across the entire cluster.

#### Role Binding Example

Here’s an example of a role binding that assigns the `pod-reader` role to a user named `alice` within the `default` namespace:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: alice-pod-reader
  namespace: default
subjects:
- kind: User
  name: alice
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

#### Cluster Role Binding Example

Here’s an example of a cluster role binding that assigns the `admin-cluster-role` to a group named `admins` across the entire cluster:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-cluster-binding
subjects:
- kind: Group
  name: admins
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: admin-cluster-role
  apiGroup: rbac.authorization.k8s.io
```

### User and Group Management in Kubernetes

Kubernetes itself does not provide built-in mechanisms for creating and managing users and groups. Instead, it relies on external sources to handle authentication and authorization. These external sources can include:

- **Static Files**: A simple file containing user details, usernames, and tokens.
- **Certificates**: Certificates signed by Kubernetes itself.
- **Third-Party Identity Services**: Services like LDAP, Active Directory, or OAuth providers.

#### Static File Example

Here’s an example of a static file (`users.yaml`) that defines users and their associated tokens:

```yaml
apiVersion: v1
kind: List
items:
- apiVersion: v1
  kind: Secret
  metadata:
    name: alice-token
    namespace: default
  type: Opaque
  data:
    token: <base64-encoded-token>
- apiVersion: v1
  kind: Secret
  metadata:
    name: bob-token
    namespace: default
  type: Opaque
  data:
    token: <base64-encoded-token>
```

#### Certificate Example

Here’s an example of a certificate-based authentication setup:

```yaml
apiVersion: certificates.k8s.io/v1
kind: CertificateSigningRequest
metadata:
  name: alice-csr
spec:
  groups:
  - system:authenticated
  request: <base64-encoded-csr>
  usages:
  - digital signature
  - key encipherment
  - client auth
```

### Real-World Examples and Recent Breaches

Recent breaches and vulnerabilities in Kubernetes clusters often stem from misconfigured RBAC settings or unauthorized access. For instance, the **CVE-2021-25741** highlighted issues with improper RBAC configurations leading to unauthorized access to sensitive resources.

#### CVE-2021-25741

This CVE involved a vulnerability in the Kubernetes API server that allowed attackers to bypass RBAC restrictions and gain elevated privileges. The issue was due to a flaw in how the API server handled certain types of requests.

### How to Prevent / Defend

To prevent such vulnerabilities and ensure secure access management in Kubernetes, follow these best practices:

#### Secure Configuration

1. **Limit Permissions**: Ensure that roles and cluster roles are as restrictive as possible. Avoid granting unnecessary permissions.
2. **Use Least Privilege Principle**: Assign the minimum necessary permissions required for a user or group to perform their tasks.
3. **Regular Audits**: Regularly review and audit RBAC configurations to identify and mitigate potential risks.

#### Detection and Prevention

1. **Monitoring**: Implement monitoring tools to detect unauthorized access attempts and suspicious activities.
2. **Logging**: Enable detailed logging of all RBAC-related events to track access patterns and identify anomalies.
3. **Automated Scanning**: Use automated scanning tools to detect misconfigurations and vulnerabilities in RBAC settings.

#### Secure Coding Fixes

Here’s an example of a vulnerable cluster role binding and its secure counterpart:

**Vulnerable Cluster Role Binding**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: insecure-admin-binding
subjects:
- kind: Group
  name: developers
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: admin-cluster-role
  apiGroup: rbac.authorization.k8s.io
```

**Secure Cluster Role Binding**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: secure-developer-binding
subjects:
- kind: Group
  name: developers
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: developer-cluster-role
  apiGroup: rbac.authorization.k8s.io
```

In the secure version, the `developer-cluster-role` is more restrictive than the `admin-cluster-role`, limiting the permissions granted to the `developers` group.

### Hands-On Labs

For practical experience with Kubernetes RBAC, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on securing Kubernetes deployments.
- **OWASP Juice Shop**: Provides a vulnerable application environment to practice securing Kubernetes resources.
- **Kubernetes Goat**: A hands-on lab specifically designed to teach Kubernetes security concepts, including RBAC.

By thoroughly understanding and implementing these principles, you can ensure robust access management in your Kubernetes clusters, protecting them from unauthorized access and potential breaches.

---
<!-- nav -->
[[07-Kubernetes Access Management Role-Based Access Control (RBAC) Part 1|Kubernetes Access Management Role-Based Access Control (RBAC) Part 1]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Role Based Access Control RBAC/00-Overview|Overview]] | [[09-Understanding Kubernetes Access Management|Understanding Kubernetes Access Management]]
