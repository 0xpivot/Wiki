---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Introduction to Kubernetes Access Management

Kubernetes is an open-source system for automating deployment, scaling, and management of containerized applications. One of the critical aspects of managing a Kubernetes cluster is ensuring that access to resources is controlled appropriately. This is achieved through Role-Based Access Control (RBAC), which allows you to define who can access what resources within the cluster. RBAC is a fundamental security mechanism that helps maintain the integrity and confidentiality of your Kubernetes environment.

### What is RBAC?

Role-Based Access Control (RBAC) is a method of regulating access to resources based on the roles of individual users within an organization. In Kubernetes, RBAC is used to control access to API objects such as Pods, Services, Deployments, and Namespaces. By defining roles and bindings, you can specify which users or groups can perform specific actions on these resources.

### Why is RBAC Important?

RBAC is crucial because it ensures that only authorized individuals can access and manipulate resources within the Kubernetes cluster. Without proper access control, unauthorized users could potentially gain access to sensitive data or disrupt the operation of the cluster. RBAC helps mitigate these risks by providing a fine-grained control mechanism.

### How Does RBAC Work?

RBAC in Kubernetes operates through three main components:

1. **Roles**: Define a set of permissions that can be granted to users or groups.
2. **Cluster Roles**: Similar to Roles, but apply cluster-wide.
3. **Role Bindings** and **Cluster Role Bindings**: Associate roles or cluster roles with users, groups, or service accounts.

### Components of RBAC

#### Roles

A Role is a list of permissions that can be granted to a user or group within a specific namespace. Roles are namespaced, meaning they apply only to resources within that namespace.

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

In this example, the `pod-reader` role grants the ability to get, watch, and list pods within the `default` namespace.

#### Cluster Roles

A Cluster Role is similar to a Role, but it applies across the entire cluster, not just within a single namespace. Cluster Roles can be used to grant permissions for cluster-wide resources such as Nodes or Namespaces.

```yaml
apiVersion: rbac.authorization.k8s.io/v
kind: ClusterRole
metadata:
  name: node-reader
rules:
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["get", "watch", "list"]
```

This `node-reader` cluster role grants the ability to get, watch, and list nodes across the entire cluster.

#### Role Bindings

A Role Binding associates a Role with a user, group, or service account within a specific namespace. It specifies which subjects (users, groups, or service accounts) are granted the permissions defined in the Role.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: User
  name: johndoe
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

In this example, the `read-pods` role binding grants the `johndoe` user the permissions defined in the `pod-reader` role within the `default` namespace.

#### Cluster Role Bindings

A Cluster Role Binding is similar to a Role Binding, but it associates a Cluster Role with a user, group, or service account across the entire cluster.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: read-nodes
subjects:
- kind: User
  name: johndoe
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: node-reader
  apiGroup: rbac.authorization.k8s.io
```

This `read-nodes` cluster role binding grants the `johndoe` user the permissions defined in the `node-reader` cluster role across the entire cluster.

### Granular Access Control

One of the key benefits of RBAC is the ability to define very granular access controls. Instead of granting broad access to all resources within a namespace, you can define access to specific resources or even specific attributes of those resources.

For example, consider a scenario where you have an application and a database in the same namespace. You might want to define separate roles for the application and the database, each with their own set of permissions.

```yaml
# Application Role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: myapp
  name: app-role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]

# Database Role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: myapp
  name: db-role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
```

Then, you can bind these roles to specific users or service accounts.

```yaml
# Application Role Binding
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: app-binding
  namespace: myapp
subjects:
- kind: User
  name: app-user
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: app-role
  apiGroup: rb
```

### Recent Real-World Examples

RBAC has been instrumental in preventing unauthorized access in several high-profile breaches. For instance, in the case of the Capital One breach in 2019, the attacker gained unauthorized access to sensitive data due to misconfigured access controls. Proper implementation of RBAC could have prevented such unauthorized access.

Another example is the Kubernetes dashboard vulnerability (CVE-2018-1002105), where an attacker could gain unauthorized access to the dashboard due to a flaw in the authentication mechanism. Implementing strict RBAC policies would have mitigated this risk.

### Common Pitfalls and Best Practices

#### Common Pitfalls

1. **Overly Broad Permissions**: Granting overly broad permissions can lead to security vulnerabilities. Always ensure that permissions are as restrictive as possible.
2. **Misconfigured Roles**: Misconfigured roles can inadvertently grant unnecessary permissions. Regularly review and audit roles to ensure they are correctly configured.
3. **Service Account Misuse**: Service accounts should be carefully managed to prevent unauthorized access. Ensure that service accounts are properly scoped and rotated regularly.

#### Best Practices

1. **Least Privilege Principle**: Follow the principle of least privilege by granting only the minimum necessary permissions required to perform a task.
2. **Regular Audits**: Regularly audit roles and bindings to ensure they are correctly configured and up-to-date.
3. **Use Namespaces**: Utilize namespaces to isolate resources and apply more granular access controls.
4. **Monitor and Log**: Monitor and log access attempts to detect and respond to unauthorized access quickly.

### How to Prevent / Defend

#### Detection

To detect unauthorized access, implement monitoring and logging mechanisms. Kubernetes provides tools like `kubectl auth can-i` to check if a user or service account has permission to perform a specific action.

```sh
kubectl auth can-i get pods --as=system:serviceaccount:myapp:app-user
```

This command checks if the `app-user` service account in the `myapp` namespace has permission to get pods.

#### Prevention

To prevent unauthorized access, follow these steps:

1. **Implement RBAC Policies**: Ensure that RBAC policies are implemented and enforced across the cluster.
2. **Regular Audits**: Conduct regular audits of roles and bindings to identify and correct misconfigurations.
3. **Least Privilege**: Apply the principle of least privilege by granting only the necessary permissions.
4. **Service Account Management**: Manage service accounts carefully to prevent unauthorized access.

#### Secure Coding Fixes

Here is an example of a vulnerable RBAC configuration and the corresponding secure configuration:

**Vulnerable Configuration**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: myapp
  name: admin-role
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
```

This role grants full administrative access to all resources in the `myapp` namespace, which is overly broad and insecure.

**Secure Configuration**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: myapp
  name: restricted-role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
```

This role restricts access to only the necessary resources and verbs, following the principle of least privilege.

### Conclusion

RBAC is a powerful tool for managing access to resources in a Kubernetes cluster. By defining roles and bindings, you can ensure that only authorized users or service accounts have access to specific resources. Following best practices and implementing strict RBAC policies can significantly enhance the security of your Kubernetes environment.

### Practice Labs

To gain hands-on experience with Kubernetes RBAC, consider the following practice labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive course on Kubernetes security, including RBAC.
- **OWASP Juice Shop**: A vulnerable web application that includes Kubernetes security challenges.
- **Kubernetes Goat**: A Kubernetes-based security training platform that covers RBAC and other security topics.

By practicing in these environments, you can gain a deeper understanding of how to effectively manage access in a Kubernetes cluster using RBAC.

---
<!-- nav -->
[[02-Introduction to Kubernetes Access Management Part 2|Introduction to Kubernetes Access Management Part 2]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Role Based Access Control RBAC/00-Overview|Overview]] | [[04-Introduction to Kubernetes Access Management Part 4|Introduction to Kubernetes Access Management Part 4]]
