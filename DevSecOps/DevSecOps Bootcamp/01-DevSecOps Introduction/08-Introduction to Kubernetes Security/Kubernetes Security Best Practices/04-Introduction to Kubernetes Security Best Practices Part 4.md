---
course: DevSecOps
topic: Introduction to Kubernetes Security
tags: [devsecops]
---

## Introduction to Kubernetes Security Best Practices

Kubernetes is an open-source platform designed to automate deployment, scaling, and management of containerized applications. Given its widespread adoption, ensuring the security of Kubernetes clusters is paramount. This chapter delves into the fundamental concepts of Kubernetes security, focusing on user management, role-based access control (RBAC), and service accounts.

### User Management in Kubernetes

In Kubernetes, users are typically authenticated using client certificates. Each user, such as Sarah and Tom, is assigned a unique client certificate that is registered within the Kubernetes cluster. This certificate serves as a digital identity for the user, enabling them to interact securely with the cluster.

#### Client Certificates

Client certificates are X.509 certificates used for mutual TLS authentication. They contain a public key and are signed by a trusted Certificate Authority (CA). Here’s an example of how to generate a client certificate:

```bash
# Generate a private key for the user
openssl genrsa -out sarah.key 2048

# Create a certificate signing request (CSR)
openssl req -new -key sarah.key -out sarah.csr -subj "/CN=sarah/O=users"

# Sign the CSR with the CA
openssl x509 -req -in sarah.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out sarah.crt -days 365
```

The resulting `sarah.crt` and `sarah.key` files can be used to authenticate Sarah to the Kubernetes cluster.

#### Registering Users

Once the client certificates are generated, they need to be registered with the Kubernetes cluster. This is typically done by creating a `kubeconfig` file that includes the user's certificate and key.

```yaml
apiVersion: v1
kind: Config
clusters:
- name: my-cluster
  cluster:
    certificate-authority: /path/to/ca.crt
    server: https://<cluster-ip>:6443
users:
- name: sarah
  user:
    client-certificate: /path/to/sarah.crt
    client-key: /path/to/sarah.key
contexts:
- context:
    cluster: my-cluster
    user: sarah
  name: sarah-context
current-context: sarah-context
```

This `kubeconfig` file allows Sarah to authenticate to the cluster using her client certificate.

### Role-Based Access Control (RBAC)

RBAC is a method of regulating access to resources based on the roles of individual users within an organization. In Kubernetes, RBAC is implemented through roles and role bindings.

#### Roles

A role is a set of permissions defined for a specific namespace. It specifies what actions can be performed on which resources within that namespace. For example, a role might allow a user to read pods but not modify them.

Here’s an example of a role definition:

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

This role allows the user to perform `get`, `watch`, and `list` operations on pods in the `default` namespace.

#### Role Bindings

A role binding associates a role with one or more users or groups. It specifies which users or groups are granted the permissions defined by the role.

Here’s an example of a role binding:

```yaml
apiVersion: rbac.authorization.k8s.io/v
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: User
  name: sarah
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

This role binding grants Sarah the permissions defined by the `pod-reader` role.

#### Cluster Roles

Cluster roles are similar to roles but apply to the entire cluster rather than a specific namespace. They are useful for granting administrative privileges across multiple namespaces or the entire cluster.

Here’s an example of a cluster role definition:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: admin-role
rules:
- apiGroups: [""]
  resources: ["*"]
  verbs: ["*"]
```

This cluster role grants full administrative privileges across the entire cluster.

#### Cluster Role Bindings

Cluster role bindings associate a cluster role with one or more users or groups. They specify which users or groups are granted the permissions defined by the cluster role.

Here’s an example of a cluster role binding:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-binding
subjects:
- kind: User
  name: kate
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: admin-role
  apiGroup: rbac.authorization.k8s.io
```

This cluster role binding grants Kate the permissions defined by the `admin-role` cluster role.

### Non-Human Users: Service Accounts

Service accounts are Kubernetes resources that provide an identity for processes running in a pod. They are used to authenticate to the Kubernetes API server and other services within the cluster.

#### Creating Service Accounts

Service accounts are created automatically for each pod, but you can also create custom service accounts.

Here’s an example of creating a custom service account:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: custom-sa
  namespace: default
```

This service account can be used by pods to authenticate to the Kubernetes API server.

#### Assigning Roles to Service Accounts

Service accounts can be assigned roles just like human users. This allows you to control what actions the service account can perform within the cluster.

Here’s an example of assigning a role to a service account:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: sa-reader
  namespace: default
subjects:
- kind: ServiceAccount
  name: custom-sa
  namespace: default
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

This role binding grants the `custom-sa` service account the permissions defined by the `pod-reader` role.

### Real-World Examples and CVEs

Several high-profile breaches and vulnerabilities have highlighted the importance of proper Kubernetes security practices. For example, the CVE-2020-8558 vulnerability allowed attackers to escalate privileges and gain full control of a Kubernetes cluster by exploiting a flaw in the `kubectl` command-line tool.

To mitigate such vulnerabilities, it is crucial to follow best practices such as:

- Regularly updating Kubernetes components to the latest versions.
- Enforcing strict RBAC policies to limit unnecessary permissions.
- Using network policies to restrict traffic between pods and services.

### How to Prevent / Defend

#### Detection

To detect unauthorized access or suspicious activity within your Kubernetes cluster, you can use tools like:

- **Falco**: An open-source runtime security tool that monitors system calls and provides alerts for suspicious behavior.
- **Prometheus**: A monitoring system that can be configured to alert on unusual activity patterns.

#### Prevention

To prevent unauthorized access and ensure the security of your Kubernetes cluster, follow these best practices:

- **Use Strong Authentication Mechanisms**: Ensure that all users and service accounts are authenticated using strong mechanisms like client certificates.
- **Implement Strict RBAC Policies**: Define and enforce strict RBAC policies to limit unnecessary permissions.
- **Regularly Audit and Review Permissions**: Periodically review and audit the permissions assigned to users and service accounts to ensure they are still necessary.

#### Secure Coding Fixes

Here’s an example of a vulnerable RBAC configuration and its secure counterpart:

**Vulnerable Configuration:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["*"]
```

**Secure Configuration:**

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

By limiting the verbs to `get`, `watch`, and `list`, you reduce the risk of unauthorized modifications to pods.

### Conclusion

Ensuring the security of your Kubernetes cluster is critical to protecting your applications and data. By implementing robust user management, RBAC policies, and service accounts, you can significantly enhance the security posture of your Kubernetes environment. Regularly auditing and reviewing your configurations will help you stay ahead of potential threats and vulnerabilities.

### Practice Labs

For hands-on experience with Kubernetes security, consider the following practice labs:

- **Kubernetes Goat**: A hands-on lab that simulates various security challenges and vulnerabilities in a Kubernetes environment.
- **OWASP WrongSecrets**: A series of challenges that focus on securing Kubernetes deployments and identifying common vulnerabilities.

These labs provide practical experience and reinforce the theoretical concepts covered in this chapter.

---
<!-- nav -->
[[03-Introduction to Kubernetes Security Best Practices Part 3|Introduction to Kubernetes Security Best Practices Part 3]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/08-Introduction to Kubernetes Security/Kubernetes Security Best Practices/00-Overview|Overview]] | [[05-Introduction to Kubernetes Security Best Practices Part 5|Introduction to Kubernetes Security Best Practices Part 5]]
