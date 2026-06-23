---
course: DevSecOps
topic: Introduction to Kubernetes Security
tags: [devsecops]
---

## Managing Users and Permissions in Kubernetes

Once your application is deployed and running in Kubernetes, managing users and their permissions becomes crucial. This involves controlling who can access the cluster and what actions they can perform once inside. Proper management of users and permissions helps mitigate the risk of unauthorized access and ensures that the cluster remains secure.

### Who Can Access the Cluster?

Access to the Kubernetes cluster can be granted to both human users and application users (such as service accounts). Each type of user requires different levels of access and permissions based on their role and responsibilities.

#### Human Users

Human users typically include developers, operators, and administrators. These users may need varying levels of access depending on their roles. For example, a developer might need access to deploy and manage applications, while an administrator might require full access to manage the cluster.

#### Application Users (Service Accounts)

Application users, also known as service accounts, are used by applications to interact with the Kubernetes API. Service accounts are typically used by automated systems and do not require the same level of access as human users.

### Role-Based Access Control (RBAC)

Role-Based Access Control (RBAC) is a method of regulating access to resources based on the roles of individual users within an organization. In Kubernetes, RBAC allows you to define roles and bind them to users or groups, ensuring that each user has only the permissions necessary to perform their tasks.

#### Roles and RoleBindings

Roles define a set of permissions that can be granted to users or groups. RoleBindings associate roles with specific users or groups, granting them the permissions defined in the role.

Here is an example of defining a role and binding it to a user:

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

---
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

In this example, a role named `pod-reader` is defined with permissions to read pods. This role is then bound to the user `johndoe`.

#### ClusterRoles and ClusterRoleBindings

ClusterRoles and ClusterRoleBindings are similar to Roles and RoleBindings, but they apply cluster-wide rather than being scoped to a specific namespace.

Here is an example of defining a cluster role and binding it to a user:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: pod-reader-cluster
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]

---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: read-pods-cluster
subjects:
- kind: User
  name: johndoe
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: pod-reader-cluster
  apiGroup: rbac.authorization.k8s.io
```

In this example, a cluster role named `pod-reader-cluster` is defined with permissions to read pods across the entire cluster. This role is then bound to the user `johndoe`.

### How to Prevent / Defend Against Unauthorized Access

To prevent unauthorized access to the Kubernetes cluster, you should implement strict RBAC policies and regularly audit user permissions. Here are some steps to take:

1. **Implement RBAC**: Define roles and role bindings carefully to ensure that users have only the permissions necessary to perform their tasks.

2. **Regular Audits**: Regularly review and audit user permissions to ensure that they remain appropriate and up-to-date.

3. **Least Privilege Principle**: Follow the principle of least privilege by granting users only the minimum permissions required to perform their tasks.

4. **Two-Factor Authentication (2FA)**: Implement two-factor authentication for human users to add an additional layer of security.

5. **Automated Monitoring**: Use automated monitoring tools to detect and alert on unauthorized access attempts.

### Real-World Examples and CVEs

One notable example of a security issue related to unauthorized access is the Kubernetes API server vulnerability (CVE-2020-8558). This vulnerability allowed an attacker to bypass authentication and gain unauthorized access to the cluster. Proper implementation of RBAC and regular audits can help mitigate such vulnerabilities.

Another example is the container breakout vulnerability (CVE-2019-5736) in the Linux kernel, which allowed a container to escape its namespace and gain access to the host system. This vulnerability underscores the importance of securing all aspects of a Kubernetes deployment, including user and permission management.

### Summary

Managing users and permissions in Kubernetes is crucial for maintaining the security of the cluster. By implementing RBAC and following the principle of least privilege, you can ensure that users have only the permissions necessary to perform their tasks. Regular audits and monitoring can help detect and prevent unauthorized access.

### Practice Labs

To gain hands-on experience with Kubernetes security best practices, consider the following labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security.
- **OWASP WrongSecrets**: A series of challenges focused on Kubernetes security.
- **kube-hunter**: A tool for detecting and exploiting security issues in Kubernetes clusters.

These labs provide practical experience in securing Kubernetes deployments and identifying potential vulnerabilities.

### Conclusion

Securing Kubernetes deployments involves several key practices, including running applications with non-root users, avoiding privileged containers, and managing users and permissions through RBAC. By following these best practices and regularly auditing and monitoring your cluster, you can significantly reduce the risk of security breaches and ensure the integrity of your Kubernetes environment.

---
<!-- nav -->
[[14-Ensuring Developer Compliance with Security Policies|Ensuring Developer Compliance with Security Policies]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/08-Introduction to Kubernetes Security/Kubernetes Security Best Practices/00-Overview|Overview]] | [[16-Pod Communication and Encryption in Kubernetes|Pod Communication and Encryption in Kubernetes]]
