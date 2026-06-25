---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Kubernetes Authentication and Authorization

Kubernetes is an open-source container orchestration platform designed to automate the deployment, scaling, and management of containerized applications. One of the critical aspects of managing a Kubernetes cluster is ensuring that only authorized users can perform specific actions within the cluster. This is achieved through a combination of authentication and authorization mechanisms.

### Why Manage Permissions in a Kubernetes Cluster?

Managing permissions in a Kubernetes cluster is essential for several reasons:

1. **Security**: Ensuring that only authorized users can access and modify resources within the cluster helps prevent unauthorized access and potential security breaches.
2. **Least Privilege Principle**: Following the principle of least privilege ensures that users have only the minimum level of access necessary to perform their tasks. This reduces the risk of accidental or intentional misuse of privileges.
3. **Isolation**: Different teams or roles may require access to different parts of the cluster. Properly managing permissions ensures that each team can only access the resources they need, preventing accidental interference with other teams' work.

### Kubernetes Users and Groups

In Kubernetes, users and groups are typically managed using external identity providers such as LDAP, Active Directory, or OAuth2. These identity providers authenticate users and provide their identities to Kubernetes. Once authenticated, Kubernetes uses these identities to determine the permissions granted to each user.

#### Example Identity Providers

- **LDAP/Active Directory**: Commonly used in enterprise environments to manage user identities and group memberships.
- **OAuth2**: Often used in cloud environments to integrate with external identity providers like Google or GitHub.

### Role-Based Access Control (RBAC)

Role-Based Access Control (RBAC) is a method of regulating access to resources based on the roles of individual users within the organization. In Kubernetes, RBAC is implemented using four main types of objects:

1. **Roles**
2. **ClusterRoles**
3. **RoleBindings**
4. **ClusterRoleBindings**

#### Roles and ClusterRoles

- **Roles** define a set of permissions that apply to a specific namespace.
- **ClusterRoles** define a set of permissions that apply across the entire cluster.

##### Example Role Definition

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: development
  name: developer-role
rules:
- apiGroups: [""] # "" indicates the core API group
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
```

This role grants `get`, `list`, and `watch` permissions on pods within the `development` namespace.

##### Example ClusterRole Definition

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: admin-clusterrole
rules:
- apiGroups: [""]
  resources: ["nodes"]
  verbs: ["get", "list", "watch"]
```

This cluster role grants `get`, `list`, and `watch` permissions on nodes across the entire cluster.

#### RoleBindings and ClusterRoleBindings

- **RoleBindings** bind a role to a user or group within a specific namespace.
- **ClusterRoleBindings** bind a cluster role to a user or group across the entire cluster.

##### Example RoleBinding

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: developer-binding
  namespace: development
subjects:
- kind: User
  name: developer-user
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: developer-role
  apiGroup: rb
```

This role binding associates the `developer-user` with the `developer-role` in the `development` namespace.

##### Example ClusterRoleBinding

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-binding
subjects:
- kind: User
  name: admin-user
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: admin-clusterrole
  apiGroup: rbac.authorization.k8s.io
```

This cluster role binding associates the `admin-user` with the `admin-clusterrole` across the entire cluster.

### Managing Permissions for Developers and Administrators

In a typical Kubernetes environment, developers and administrators have different roles and therefore different sets of permissions.

#### Developer Permissions

Developers typically need access to specific namespaces where they deploy their applications. They should be limited to performing actions that are necessary for their tasks, such as creating, updating, and deleting resources within their namespace.

##### Example Developer Role

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: development
  name: developer-role
rules:
- apiGroups: [""]
  resources: ["pods", "services", "deployments"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
```

This role grants developers the ability to manage pods, services, and deployments within the `development` namespace.

##### Example Developer RoleBinding

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: developer-binding
  namespace: development
subjects:
- kind: User
  name: developer-user
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: developer-role
  apiGroup: rbac.authorization.k8s.io
```

This role binding associates the `developer-user` with the `developer-role` in the `development` namespace.

#### Administrator Permissions

Administrators typically need broader access to manage the entire cluster. They may need to create and manage namespaces, configure cluster-wide settings, and perform administrative tasks.

##### Example Administrator ClusterRole

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: admin-clusterrole
rules:
- apiGroups: [""]
  resources: ["nodes", "namespaces"]
  verbs: ["get", "list", "watch", "create", "update", "patch", "delete"]
```

This cluster role grants administrators the ability to manage nodes and namespaces across the entire cluster.

##### Example Administrator ClusterRoleBinding

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-binding
subjects:
- kind: User
  name: admin-user
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: admin-clusterrole
  apiGroup: rbac.authorization.k8s.io
```

This cluster role binding associates the `admin-user` with the `admin-clusterrole` across the entire cluster.

### Real-World Examples and Recent Breaches

Recent breaches and vulnerabilities have highlighted the importance of proper permission management in Kubernetes clusters. For example, the Kubernetes API server has been a target for attacks due to misconfigured permissions and exposed credentials.

#### CVE-2021-25741

CVE-2021-25741 is a vulnerability in the Kubernetes API server that allows attackers to bypass authentication and gain unauthorized access to the cluster. This vulnerability underscores the importance of properly configuring RBAC and ensuring that only authorized users have access to sensitive resources.

##### Example Vulnerable Configuration

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: vulnerable-clusterrole
rules:
- apiGroups: [""]
  resources: ["*"]
  verbs: ["*"]
```

This cluster role grants unrestricted access to all resources in the cluster, which is highly insecure.

##### Secure Configuration

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: secure-clusterrole
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch"]
```

This cluster role restricts access to only the necessary resources and verbs, adhering to the principle of least privilege.

### How to Prevent / Defend

Properly configuring RBAC and ensuring that only authorized users have access to sensitive resources is crucial for securing a Kubernetes cluster. Here are some best practices for preventing and defending against unauthorized access:

1. **Use External Identity Providers**: Integrate Kubernetes with external identity providers to manage user identities and group memberships.
2. **Implement Least Privilege Principle**: Ensure that users have only the minimum level of access necessary to perform their tasks.
3. **Regularly Audit Permissions**: Regularly review and audit permissions to ensure that they are up-to-date and aligned with organizational policies.
4. **Monitor API Server Logs**: Monitor API server logs for suspicious activity and unauthorized access attempts.
5. **Use Network Policies**: Implement network policies to restrict traffic between pods and limit exposure to sensitive resources.

#### Example Network Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: allow-from-same-namespace
  namespace: development
spec:
  podSelector:
    matchLabels:
      app: myapp
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app: myapp
```

This network policy restricts ingress traffic to pods labeled `app: myapp` within the `development` namespace.

### Hands-On Labs

To practice and reinforce your understanding of Kubernetes authentication and authorization, consider the following hands-on labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on web security, including Kubernetes security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **Kubernetes Goat**: A Kubernetes security training platform that simulates real-world security challenges.

These labs provide practical experience in configuring and securing Kubernetes clusters, helping you to apply the concepts learned in this chapter.

### Conclusion

Managing permissions in a Kubernetes cluster is a critical aspect of ensuring the security and stability of the environment. By properly configuring RBAC and adhering to the principle of least privilege, you can minimize the risk of unauthorized access and potential security breaches. Regularly auditing permissions and monitoring API server logs are essential steps in maintaining a secure Kubernetes cluster.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/22-Kubernetes Authentication Authorization And RBAC/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/22-Kubernetes Authentication Authorization And RBAC/02-Introduction to Kubernetes Security|Introduction to Kubernetes Security]]
