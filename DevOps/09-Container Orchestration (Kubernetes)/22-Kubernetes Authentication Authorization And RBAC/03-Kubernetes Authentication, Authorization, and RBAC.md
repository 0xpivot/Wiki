---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Kubernetes Authentication, Authorization, and RBAC

### Introduction to Kubernetes Authentication and Authorization

Kubernetes is a powerful platform for deploying, scaling, and managing containerized applications. However, with great power comes great responsibility, particularly when it comes to securing the cluster. One of the key aspects of securing a Kubernetes cluster is managing authentication and authorization. This ensures that only authorized users and processes can interact with the cluster and perform specific actions.

### Understanding Roles and Cluster Roles

In Kubernetes, roles and cluster roles are fundamental components used to define permissions. A **role** is a set of permissions that apply within a specific namespace. On the other hand, a **cluster role** is a set of permissions that apply across the entire cluster, not limited to a single namespace.

#### Role vs. Cluster Role

- **Role**: 
  - **Definition**: A role is a set of permissions that are scoped to a specific namespace.
  - **Use Case**: Roles are typically used for granting permissions to users or services that need to operate within a particular namespace.
  - **Example**: A developer might need read/write access to pods and deployments within a development namespace.

- **Cluster Role**:
  - **Definition**: A cluster role is a set of permissions that are scoped to the entire cluster.
  - **Use Case**: Cluster roles are used for granting permissions to users or services that need to operate across multiple namespaces or perform cluster-wide operations.
  - **Example**: An administrator might need read/write access to all namespaces and resources within the cluster.

### Creating and Managing Cluster Roles

To manage cluster-wide operations, such as managing all namespaces or configuring volumes available cluster-wide, you need to define permissions using cluster roles. Let's walk through the process of creating a cluster role and attaching it to a user or group.

#### Step-by-Step Process

1. **Define the Cluster Role**:
   - Create a YAML file that defines the cluster role.
   - Specify the resources and verbs (permissions) that the role should grant.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: admin-cluster-role
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
```

2. **Create the Cluster Role**:
   - Apply the YAML file to create the cluster role.

```bash
kubectl apply -f admin-cluster-role.yaml
```

3. **Create a User Group**:
   - Define a group of users that will be assigned the cluster role.
   - This can be done using a static file, certificates, or an external identity service like LDAP.

4. **Attach the Cluster Role to the User Group**:
   - Create a cluster role binding that attaches the cluster role to the user group.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-cluster-role-binding
subjects:
- kind: Group
  name: admin-group
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: admin-cluster-role
  apiGroup: rb
```

5. **Apply the Cluster Role Binding**:
   - Apply the YAML file to create the cluster role binding.

```bash
kubectl apply -f admin-cluster-role-binding.yaml
```

### External Sources for Users and Groups

Kubernetes itself does not provide built-in mechanisms for creating and managing users and groups. Instead, it relies on external sources to handle these tasks. Here are some common methods:

1. **Static File**:
   - A static file containing user details, usernames, and tokens.
   - Example: `/etc/kubernetes/auth/users.yaml`.

2. **Certificates**:
   - Certificates signed by Kubernetes itself.
   - Example: `openssl x509 -in user.crt -text`.

3. **Third-Party Identity Service**:
   - Services like LDAP, Active Directory, or OAuth providers.
   - Example: `ldap://ldap.example.com`.

### Real-World Examples and Recent Breaches

Recent breaches and vulnerabilities have highlighted the importance of proper authentication and authorization in Kubernetes clusters. For instance:

- **CVE-2021-25741**: A vulnerability in Kubernetes API server allowed unauthorized access due to improper validation of user credentials.
- **CVE-2020-8558**: A privilege escalation vulnerability in Kubernetes allowed attackers to gain elevated privileges by manipulating pod security contexts.

These examples underscore the need for robust security practices, including proper role management and external identity services.

### How to Prevent / Defend

#### Detection

- **Audit Logs**: Enable audit logging to track all API requests and responses.
- **Monitoring Tools**: Use tools like Prometheus and Grafana to monitor cluster activity.

#### Prevention

- **Least Privilege Principle**: Grant users and services the minimum necessary permissions.
- **External Identity Management**: Use external identity services to manage users and groups.

#### Secure Coding Fixes

- **Vulnerable Code**:
  ```yaml
  apiVersion: rbac.authorization.k8s.io/v1
  kind: ClusterRole
  metadata:
    name: insecure-cluster-role
  rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
  ```

- **Secure Code**:
  ```yaml
  apiVersion: rbac.authorization.k8s.io/v1
  kind: ClusterRole
  metadata:
    name: secure-cluster-role
  rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch"]
  ```

### Conclusion

Managing authentication and authorization in Kubernetes is crucial for maintaining the security and integrity of your cluster. By understanding the differences between roles and cluster roles, and by leveraging external identity services, you can ensure that only authorized users and processes can interact with your cluster. Always follow best practices and stay vigilant against potential threats.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on Kubernetes security.
- **OWASP Juice Shop**: Provides a vulnerable application for testing and learning.
- **Kubernetes Goat**: A vulnerable Kubernetes environment for security training.

By engaging with these labs, you can deepen your understanding and practical skills in Kubernetes security.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/22-Kubernetes Authentication Authorization And RBAC/02-Introduction to Kubernetes Security|Introduction to Kubernetes Security]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/22-Kubernetes Authentication Authorization And RBAC/00-Overview|Overview]] | [[04-Kubernetes Authentication, Authorization, and Role-Based Access Control (RBAC)|Kubernetes Authentication, Authorization, and Role-Based Access Control (RBAC)]]
