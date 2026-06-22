---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management

### Introduction to Kubernetes Access Management

Kubernetes access management is a critical aspect of securing your Kubernetes clusters. It involves controlling who can access the cluster and what actions they can perform. This is achieved through roles, role bindings, and service accounts. In this section, we will delve into the concepts of Kubernetes access management, focusing on the `admin` role and how it interacts with the cluster.

### Understanding Roles and Role Bindings

In Kubernetes, roles define a set of permissions that can be granted to users or groups. A role binding associates a role with a user or group, effectively granting them the permissions defined in the role. There are two types of roles:

- **ClusterRole**: Defines permissions at the cluster level.
- **Role**: Defines permissions within a specific namespace.

Similarly, there are two types of role bindings:

- **ClusterRoleBinding**: Binds a ClusterRole to a user or group across the entire cluster.
- **RoleBinding**: Binds a Role to a user or group within a specific namespace.

#### Example: Defining a ClusterRole

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: my-cluster-role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
```

This `ClusterRole` grants the ability to list and watch pods across the entire cluster.

#### Example: Binding a ClusterRole

```yaml
apiVersion: rbac.authorization.k8s.io/v
kind: ClusterRoleBinding
metadata:
  name: my-cluster-role-binding
subjects:
- kind: User
  name: alice
roleRef:
  kind: ClusterRole
  name: my-cluster-role
  apiGroup: rbac.authorization.k8s.io
```

This `ClusterRoleBinding` binds the `my-cluster-role` to the user `alice`.

### The `admin` Role

The `admin` role is a predefined role in Kubernetes that provides full administrative access to the cluster. This includes the ability to manage all resources across all namespaces. However, in some configurations, the `admin` role may be restricted to read-only access.

#### Example: Configuring the `admin` Role

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: admin
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
```

This `ClusterRole` defines the `admin` role with full administrative access.

### Mapping AWS Credentials to Kubernetes Roles

When using AWS credentials to authenticate with a Kubernetes cluster, the credentials are mapped to a specific role within the cluster. This mapping is typically done through an IAM role in AWS that is associated with the Kubernetes cluster.

#### Example: IAM Role Configuration

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "sts:AssumeRole"
      ],
      "Resource": "arn:aws:iam::123456789012:role/KubernetesAdminRole"
    }
  ]
}
```

This IAM role allows the assumption of the `KubernetesAdminRole`, which is then mapped to the `admin` role in the Kubernetes cluster.

### Testing Access with `kubectl`

To test the access granted by the `admin` role, we can use the `kubectl` command-line tool. The `admin` role should allow us to view resources in the `kube-system` namespace, which contains the control plane components of the cluster.

#### Example: Listing Pods in `kube-system` Namespace

```sh
kubectl get pods --namespace=kube-system
```

This command lists all pods in the `kube-system` namespace.

#### Example: Attempting to Delete a Pod

```sh
kubectl delete pod <pod-name> --namespace=kube-system
```

If the `admin` role is restricted to read-only access, attempting to delete a pod will result in an error.

### Real-World Examples and CVEs

Recent breaches and CVEs related to Kubernetes access management highlight the importance of proper role management and access control. For example, CVE-2021-25741 involved a vulnerability in the Kubernetes API server that allowed unauthorized access to sensitive resources.

#### Example: CVE-2021-25741

CVE-2021-25741 was a privilege escalation vulnerability in the Kubernetes API server. An attacker could exploit this vulnerability to gain elevated privileges and access sensitive resources.

### How to Prevent / Defend

#### Detection

To detect unauthorized access attempts, you can enable audit logging in Kubernetes. Audit logs record all API requests, allowing you to monitor and analyze access patterns.

#### Example: Enabling Audit Logging

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: Metadata
  users: ["system:serviceaccount:kube-system:default"]
- level: Request
  users: ["system:anonymous"]
- level: None
  users: ["system:unauthenticated"]
```

This audit policy logs metadata for requests from the `default` service account in the `kube-system` namespace and logs full requests for anonymous users.

#### Prevention

To prevent unauthorized access, ensure that roles and role bindings are properly configured and that least privilege principles are followed. Avoid granting unnecessary permissions to users and roles.

#### Secure Coding Fixes

Compare the insecure and secure versions of a role definition:

**Insecure Version**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: insecure-admin
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
```

**Secure Version**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: secure-admin
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch"]
```

The secure version restricts the `admin` role to only necessary permissions.

### Hands-On Labs

For practical experience with Kubernetes access management, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a module on Kubernetes security, including access management.
- **OWASP Juice Shop**: Provides a Kubernetes deployment scenario where you can practice securing access.
- **Kubernetes Goat**: A red team exercise for Kubernetes, covering various aspects of security, including access management.

By thoroughly understanding and implementing these concepts, you can ensure that your Kubernetes cluster remains secure and compliant with best practices.

---
<!-- nav -->
[[06-Kubernetes Access Management Part 3|Kubernetes Access Management Part 3]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Review and Test Access/00-Overview|Overview]] | [[08-Kubernetes Access Management Part 5|Kubernetes Access Management Part 5]]
