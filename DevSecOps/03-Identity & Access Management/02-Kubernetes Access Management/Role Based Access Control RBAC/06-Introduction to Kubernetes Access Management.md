---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Introduction to Kubernetes Access Management

Kubernetes is an open-source system for automating deployment, scaling, and management of containerized applications. One of the critical aspects of Kubernetes is its ability to manage access control, ensuring that only authorized entities can perform actions within the cluster. Role-Based Access Control (RBAC) is a fundamental mechanism used in Kubernetes to manage access permissions.

### What is Role-Based Access Control (RBAC)?

Role-Based Access Control (RBAC) is a method of restricting network access based on the roles of individual users within an organization. In Kubernetes, RBAC allows you to define who can access what resources and what actions they can perform on those resources. This is achieved through the use of roles and role bindings.

#### Roles

A role is a set of permissions that defines what actions can be performed on specific resources within a namespace. A role is bound to a specific namespace and defines the following:

- **Resources**: These are the objects within the namespace that the role applies to. Examples include pods, deployments, services, secrets, and more.
- **Actions**: These are the operations that can be performed on the resources. Common actions include `list`, `get`, `create`, `update`, `patch`, and `delete`.

For example, consider a role that allows a developer team to create and update pods but not delete them. This role would be defined as follows:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: development
  name: pod-manager
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["create", "update", "patch"]
```

In this example, the role `pod-manager` is defined in the `development` namespace and allows the creation, update, and patch operations on pods.

#### Role Bindings

While roles define the permissions, role bindings associate these roles with specific users or groups. A role binding links a role to one or more subjects (users or groups) and specifies the namespace where the role applies.

For instance, to bind the `pod-manager` role to a user named `alice`, you would create a role binding as follows:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: alice-pod-manager
  namespace: development
subjects:
- kind: User
  name: alice
roleRef:
  kind: Role
  name: pod-manager
  apiGroup: rbac.authorization.k8s.io
```

This role binding associates the `pod-manager` role with the user `alice` in the `development` namespace.

### Why Use RBAC?

RBAC provides several benefits:

- **Fine-grained Access Control**: You can define precise permissions for different roles, ensuring that users have only the access they need.
- **Namespace Isolation**: By defining roles at the namespace level, you can isolate access controls between different teams or projects.
- **Centralized Management**: All access control policies are managed centrally within the Kubernetes cluster, making it easier to enforce and audit access.

### How Does RBAC Work Under the Hood?

When a user attempts to perform an action within a Kubernetes cluster, the API server checks the RBAC rules to determine if the user has the necessary permissions. This process involves the following steps:

1. **Authentication**: The API server verifies the identity of the user.
2. **Authorization**: The API server checks the RBAC rules to determine if the authenticated user has the required permissions to perform the requested action.
3. **Access Decision**: Based on the RBAC rules, the API server either grants or denies access to the requested resource.

### Real-World Example: CVE-2021-25741

CVE-2021-25741 is a vulnerability in Kubernetes that allowed unauthorized access to sensitive resources due to misconfigured RBAC rules. In this case, a misconfigured role binding allowed a user to access and modify sensitive resources, leading to potential data breaches.

To prevent such vulnerabilities, it is crucial to ensure that RBAC rules are correctly configured and regularly audited. Here is an example of a misconfigured role binding:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: misconfigured-binding
  namespace: production
subjects:
- kind: Group
  name: developers
roleRef:
  kind: Role
  name: admin-role
  apiGroup: rbac.authorization.k8s.io
```

In this example, the `developers` group is granted administrative privileges in the `production` namespace, which is a significant security risk. To correct this, the role should be limited to the necessary permissions:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: corrected-binding
  namespace: production
subjects:
- kind: Group
  name: developers
roleRef:
  kind: Role
  name: restricted-role
  apiGroup: rbac.authorization.k8s.io
```

Here, the `restricted-role` is defined with limited permissions, reducing the risk of unauthorized access.

### How to Prevent / Defend Against Misconfigured RBAC Rules

#### Detection

To detect misconfigured RBAC rules, you can use tools like `kube-bench` or `kubescape`. These tools scan your Kubernetes cluster for misconfigurations and provide detailed reports.

Example using `kube-bench`:

```sh
wget https://github.com/aquasecurity/kube-bench/releases/download/v0.5.10/kube-bench_0.5.10_linux_amd64.tar.gz
tar xvf kube-bench_0.5.10_linux_amd64.tar.gz
./kube-bench run --check all
```

This command runs `kube-bench` to check for misconfigurations in your Kubernetes cluster.

#### Prevention

To prevent misconfigured RBAC rules, follow these best practices:

1. **Least Privilege Principle**: Grant users only the minimum permissions necessary to perform their tasks.
2. **Regular Audits**: Regularly review and audit RBAC configurations to ensure they remain secure.
3. **Automated Scanning**: Use automated tools to scan for misconfigurations and alert on potential issues.

#### Secure Coding Fixes

Here is an example of a vulnerable role binding and its corrected version:

**Vulnerable Role Binding:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: vulnerable-binding
  namespace: production
subjects:
- kind: User
  name: alice
roleRef:
  kind: Role
  name: admin-role
  apiGroup: rbac.authorization.k8s.io
```

**Corrected Role Binding:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: corrected-binding
  namespace: production
subjects:
- kind: User
  name: alice
roleRef:
  kind: Role
  name: restricted-role
  apiGroup: rbac.authorization.k8s.io
```

In the corrected version, the `admin-role` is replaced with a `restricted-role` that has limited permissions.

### Advanced RBAC Concepts

#### Cluster Roles and Cluster Role Bindings

Cluster roles and cluster role bindings are similar to roles and role bindings but apply across the entire cluster rather than a specific namespace. This makes them useful for granting administrative privileges.

Example of a cluster role:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: cluster-admin
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
```

Example of a cluster role binding:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: cluster-admin-binding
subjects:
- kind: User
  name: admin
roleRef:
  kind: ClusterRole
  name: cluster-admin
  apiGroup: rbac.authorization.k8s.io
```

#### Aggregated Roles

Aggregated roles allow you to combine multiple roles into a single role. This is useful for managing complex permission sets.

Example of an aggregated role:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: development
  name: aggregated-role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["create", "update", "patch"]
- apiGroups: ["apps"]
  resources: ["deployments"]
  verbs: ["get", "list"]
```

### Hands-On Practice

To practice RBAC concepts, you can use the following labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security concepts, including RBAC.
- **OWASP WrongSecrets**: A series of challenges that cover various security topics, including RBAC in Kubernetes.

These labs provide practical experience in configuring and auditing RBAC rules in a Kubernetes environment.

### Conclusion

Role-Based Access Control (RBAC) is a powerful mechanism for managing access permissions in Kubernetes. By understanding how roles and role bindings work, you can ensure that your Kubernetes cluster remains secure and that users have only the access they need. Regular audits and the use of automated tools can help detect and prevent misconfigurations, ensuring that your RBAC rules remain effective.

By following the principles of least privilege and regular auditing, you can maintain a secure and efficient Kubernetes environment.

---
<!-- nav -->
[[05-Introduction to Kubernetes Access Management Part 5|Introduction to Kubernetes Access Management Part 5]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Role Based Access Control RBAC/00-Overview|Overview]] | [[07-Kubernetes Access Management Role-Based Access Control (RBAC) Part 1|Kubernetes Access Management Role-Based Access Control (RBAC) Part 1]]
