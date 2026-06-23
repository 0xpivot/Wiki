---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Introduction to Kubernetes Access Management

Kubernetes, often referred to as K8s, is an open-source system for automating deployment, scaling, and management of containerized applications. One of the critical aspects of managing a Kubernetes cluster is ensuring proper access control to its resources. Role-Based Access Control (RBAC) is a fundamental mechanism used to enforce access policies within Kubernetes clusters. This chapter delves deep into the concepts, mechanisms, and practical implementation of RBAC in Kubernetes, providing a comprehensive guide for both beginners and advanced users.

### What is Role-Based Access Control (RBAC)?

Role-Based Access Control (RBAC) is a method of restricting network access based on the roles of individual users within an organization. In the context of Kubernetes, RBAC enables administrators to define and enforce permissions for accessing Kubernetes resources based on roles assigned to users or groups. This ensures that only authorized individuals can perform specific actions within the cluster.

#### Why RBAC Matters

RBAC is crucial for several reasons:

1. **Security**: By limiting access to sensitive operations, RBAC helps prevent unauthorized access and potential security breaches.
2. **Compliance**: Many regulatory frameworks require strict access controls. RBAC helps organizations meet compliance requirements.
3. **Operational Efficiency**: RBAC simplifies the management of access rights, making it easier to grant and revoke permissions as needed.

### Components of RBAC in Kubernetes

RBAC in Kubernetes consists of several key components:

1. **Users**: Individuals or entities that interact with the Kubernetes cluster.
2. **Groups**: Collections of users that share similar roles or responsibilities.
3. **Roles**: Define sets of permissions that can be granted to users or groups.
4. **RoleBindings**: Bind roles to users or groups within a namespace.
5. **ClusterRoles**: Similar to roles but apply cluster-wide.
6. **ClusterRoleBindings**: Bind cluster roles to users or groups across the entire cluster.

### Authentication Sources in Kubernetes

Before diving into RBAC, it's essential to understand how Kubernetes authenticates users. Kubernetes supports various authentication methods, including:

- **Static Token Files**
- **Certificates**
- **LDAP/Active Directory**

#### Static Token Files

Static token files are simple text files containing authentication tokens. These tokens are used to authenticate users connecting to the Kubernetes API server.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: my-token
  namespace: default
type: kubernetes.io/service-account-token
stringData:
  token: eyJhbGciOiJSUzI1NiIsImtpZCI6IjIwMTYtMDItMjQifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQtdmVyc2lvbiI6IjIiLCJhdWQiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50IiwibmFtZSI6InRlbXBvciIsIkpXVCJ9.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQtdmVyc2lvbiI6IjIiLCJvcmlnaW4iOnsiaWQiOiJ0ZW1wb3IiLCJpdGVyYXRpb24iOiJ0ZW1wb3IifSwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50OmRlZmF1bHQ6dGVtcG9yIn0.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQtdmVyc2lvbiI6IjIiLCJvcmlnaW4iOnsiaWQiOiJ0ZW1wb3IiLCJpdGVyYXRpb24iOiJ0ZW1wb3IifSwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50OmRlZmF1bHQ6dGVtcG9yIn0.
```

To use this token, you would typically pass it via the `--token` flag when configuring the API server.

#### Certificates

Certificates provide a more secure method of authentication. Administrators must manually create certificates for each user. These certificates are then used to authenticate users connecting to the cluster.

```bash
openssl req -new -newkey rsa:2048 -nodes -keyout myuser.key -out myuser.csr
openssl x509 -req -days 365 -in myuser.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out myuser.crt
```

The generated certificate (`myuser.crt`) and key (`myuser.key`) can be used to authenticate the user.

#### LDAP/Active Directory

For larger organizations, integrating with existing LDAP or Active Directory services can simplify user management. Kubernetes can be configured to use these services as authentication sources.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: kube-apiserver-authentication
  namespace: kube-system
data:
  ldap.yaml: |
    kind: LdapConfig
    apiVersion: v1
    url: "ldap://ldap.example.com"
    bindDN: "cn=admin,dc=example,dc=com"
    bindPassword: "secretpassword"
    userSearch:
      baseDN: "ou=users,dc=example,dc=com"
      filter: "(uid=%v)"
    groupSearch:
      baseDN: "ou=groups,dc=example,dc=com"
      filter: "(memberUid=%v)"
```

This configuration maps LDAP settings to the Kubernetes API server.

### Role-Based Access Control (RBAC)

RBAC in Kubernetes is implemented through roles and role bindings. Roles define sets of permissions, while role bindings associate these roles with users or groups.

#### Roles

A role is a set of permissions that can be granted to users or groups. Roles are defined within a specific namespace.

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

This role grants read-only access to pods within the `default` namespace.

#### RoleBindings

A role binding associates a role with a user or group within a namespace.

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

This role binding grants the `pod-reader` role to the user `johndoe`.

#### ClusterRoles

Cluster roles are similar to roles but apply cluster-wide.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
```

This cluster role grants read-only access to pods across the entire cluster.

#### ClusterRoleBindings

Cluster role bindings associate cluster roles with users or groups across the entire cluster.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: read-pods-global
subjects:
- kind: User
  name: johndoe
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: pod-reader
  apiGroup: rb
```

This cluster role binding grants the `pod-reader` cluster role to the user `johndoe`.

### Real-World Examples and Breaches

Recent breaches and vulnerabilities have highlighted the importance of proper access control in Kubernetes clusters. For instance, the CVE-2020-8558 vulnerability in Kubernetes allowed attackers to bypass RBAC restrictions and gain elevated privileges.

#### CVE-2020-8558

CVE-2020-8558 was a critical vulnerability in Kubernetes that allowed attackers to bypass RBAC restrictions and execute arbitrary commands within the cluster. This vulnerability was due to a flaw in the way Kubernetes handled certain API requests.

**Example Exploit:**

An attacker could craft a malicious API request to exploit this vulnerability:

```http
POST /api/v1/namespaces/default/pods?dryRun=All&fieldManager=kubectl-create HTTP/1.1
Host: <cluster-ip>:<port>
Authorization: Bearer <valid-token>
Content-Type: application/json

{
  "apiVersion": "v1",
  "kind": "Pod",
  "metadata": {
    "name": "malicious-pod"
  },
  "spec": {
    "containers": [
      {
        "name": "malicious-container",
        "image": "attacker-image",
        "command": ["sh", "-c", "echo 'Exploited!' > /tmp/exploit.txt"]
      }
    ]
  }
}
```

This request would create a new pod with elevated privileges, allowing the attacker to execute arbitrary commands within the cluster.

### How to Prevent / Defend

To prevent such vulnerabilities and ensure robust access control in Kubernetes clusters, follow these best practices:

#### Secure Configuration

Ensure that all authentication sources are properly configured and secured. Use strong encryption and secure storage for credentials.

#### Regular Audits

Regularly audit RBAC configurations to ensure that only necessary permissions are granted. Use tools like `kubectl auth can-i` to check permissions.

```bash
kubectl auth can-i get pods --namespace=default
```

#### Least Privilege Principle

Adhere to the principle of least privilege by granting users only the minimum permissions required to perform their tasks.

#### Monitoring and Logging

Enable monitoring and logging to detect and respond to unauthorized access attempts. Use tools like Prometheus and Grafana for monitoring and Fluentd for logging.

#### Example Secure Configuration

Here is an example of a secure RBAC configuration:

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

This configuration ensures that only the necessary permissions are granted to the user `johndoe`.

### Hands-On Labs

To practice and reinforce the concepts learned in this chapter, consider the following hands-on labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice web security techniques.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **Kubernetes Goat**: A vulnerable Kubernetes cluster for practicing security and hardening techniques.
- **CloudGoat**: A vulnerable AWS environment for practicing cloud security.

These labs provide real-world scenarios and challenges to help you master Kubernetes access management and RBAC.

### Conclusion

Proper access management is crucial for securing Kubernetes clusters. Role-Based Access Control (RBAC) provides a powerful mechanism for enforcing access policies based on roles. By understanding the components of RBAC, configuring authentication sources, and adhering to best practices, you can ensure robust security for your Kubernetes clusters. Regular audits, monitoring, and adherence to the principle of least privilege are essential for maintaining a secure environment.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Role Based Access Control RBAC/00-Overview|Overview]] | [[02-Introduction to Kubernetes Access Management Part 2|Introduction to Kubernetes Access Management Part 2]]
