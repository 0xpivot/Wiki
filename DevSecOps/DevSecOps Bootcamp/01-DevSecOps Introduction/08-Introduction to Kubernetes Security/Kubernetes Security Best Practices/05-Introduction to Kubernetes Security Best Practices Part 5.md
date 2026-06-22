---
course: DevSecOps
topic: Introduction to Kubernetes Security
tags: [devsecops]
---

## Introduction to Kubernetes Security Best Practices

Kubernetes is a powerful container orchestration platform that simplifies the deployment, scaling, and management of containerized applications. However, with great power comes great responsibility, especially when it comes to security. In this section, we will delve into the key aspects of Kubernetes security, focusing on authentication, authorization, and network policies.

### Authentication in Kubernetes

In Kubernetes, authentication is the process of verifying the identity of entities that interact with the system. There are two primary types of entities that require authentication:

1. **Users**: These are human operators or automated scripts that interact with the Kubernetes API server.
2. **Service Accounts**: These are identities used by pods to communicate with the Kubernetes API server.

#### User Authentication

Users typically authenticate using client certificates. A client certificate is a digital certificate that verifies the identity of a user or a machine. Here’s how it works:

- **Client Certificate**: Each user is issued a client certificate signed by a trusted Certificate Authority (CA). This certificate contains the user's identity information.
- **API Server Verification**: When a user sends a request to the Kubernetes API server, the server verifies the client certificate against its trusted CA. If the certificate is valid, the user is authenticated.

**Example of Client Certificate Authentication**

```bash
# Generate a client certificate
openssl req -new -newkey rsa:2048 -nodes -keyout client.key -out client.csr -subj "/CN=alice/O=users"
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 365

# Use the client certificate to authenticate
kubectl config set-credentials alice --client-certificate=client.crt --client-key=client.key
```

#### Service Account Authentication

Service accounts are used by pods to authenticate with the Kubernetes API server. Instead of client certificates, service accounts use tokens for authentication.

- **Token**: Each service account is associated with a token stored in a secret within the same namespace. When a pod starts, the token is mounted into the pod, allowing it to authenticate with the API server.
- **API Server Verification**: The API server verifies the token against its trusted token issuer. If the token is valid, the service account is authenticated.

**Example of Service Account Token**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: service-account-token
  annotations:
    kubernetes.io/service-account.name: default
type: kubernetes.io/service-account-token
data:
  ca.crt: <base64-encoded-ca-certificate>
  namespace: ZGVmYXVsdA==
  token: <base64-encoded-token>
```

### Authorization in Kubernetes

Authorization is the process of determining whether an authenticated entity is allowed to perform a specific action. Kubernetes uses Role-Based Access Control (RBAC) to manage authorization.

#### Role-Based Access Control (RBAC)

RBAC allows you to define roles and bind those roles to users or service accounts. Roles specify the permissions granted to a user or service account.

- **Role**: A role is a set of permissions defined within a namespace.
- **ClusterRole**: A cluster role is a set of permissions defined across the entire cluster.
- **RoleBinding**: A role binding associates a role with a user or group within a namespace.
- **ClusterRoleBinding**: A cluster role binding associates a cluster role with a user or group across the entire cluster.

**Example of RBAC Configuration**

```yaml
# Define a role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]

# Bind the role to a user
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
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

### Least Privilege Principle

The principle of least privilege (PoLP) states that every module (such as a process, a user, or a program) should operate using the minimum levels of privilege necessary to complete the task. In Kubernetes, this means granting only the necessary permissions to users and service accounts.

**Example of Least Privilege**

```yaml
# Define a minimal role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: minimal-pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get"]

# Bind the minimal role to a service account
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: minimal-read-pods
  namespace: default
subjects:
- kind: ServiceAccount
  name: my-service-account
  namespace: default
roleRef:
  kind: Role
  name: minimal-pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### Network Policies in Kubernetes

By default, Kubernetes allows all pods to communicate with each other. However, this can lead to security vulnerabilities if an attacker gains access to one pod and can then access other pods. To mitigate this, Kubernetes provides network policies to control the communication between pods.

#### Network Policies

Network policies allow you to define rules that determine which pods can communicate with each other. You can specify ingress and egress rules to control incoming and outgoing traffic.

- **Ingress Rules**: Control incoming traffic to a pod.
- **Egress Rules**: Control outgoing traffic from a pod.

**Example of Network Policy**

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
  namespace: default
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector: {}
```

This network policy denies all ingress traffic to all pods in the `default` namespace.

### Real-World Examples and Recent Breaches

Recent breaches and CVEs highlight the importance of proper Kubernetes security practices. For instance, the Kubernetes Dashboard was found to be vulnerable to unauthorized access due to misconfigured RBAC settings.

**CVE-2020-8558**: This vulnerability allowed attackers to gain unauthorized access to the Kubernetes Dashboard due to misconfigured RBAC settings. The dashboard was accessible without proper authentication, leading to potential data breaches.

**How to Prevent / Defend**

To prevent such vulnerabilities, ensure that:

- **RBAC is properly configured**: Grant only the necessary permissions to users and service accounts.
- **Network policies are enforced**: Limit communication between pods to only what is necessary.
- **Regular audits**: Perform regular security audits to identify and mitigate potential vulnerabilities.

**Secure Coding Fixes**

Here is an example of a vulnerable RBAC configuration and its secure counterpart:

**Vulnerable RBAC Configuration**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: admin
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-binding
subjects:
- kind: User
  name: alice
roleRef:
  kind: ClusterRole
  name: admin
  apiGroup: rbac.authorization.k8s.io
```

**Secure RBAC Configuration**

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
  name: alice
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rb
```

### Hands-On Labs

To practice and reinforce these concepts, consider the following hands-on labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web security, including Kubernetes security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **Kubernetes Goat**: A security-focused Kubernetes environment designed for learning and testing security configurations.

These labs provide practical experience in configuring and securing Kubernetes clusters, helping you to apply the theoretical knowledge gained in this chapter.

### Conclusion

Kubernetes security is a critical aspect of deploying and managing containerized applications. By understanding and implementing best practices for authentication, authorization, and network policies, you can significantly enhance the security of your Kubernetes clusters. Regular audits and secure coding practices are essential to maintaining a robust security posture.

---
<!-- nav -->
[[04-Introduction to Kubernetes Security Best Practices Part 4|Introduction to Kubernetes Security Best Practices Part 4]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/08-Introduction to Kubernetes Security/Kubernetes Security Best Practices/00-Overview|Overview]] | [[06-Introduction to Kubernetes Security Best Practices Part 6|Introduction to Kubernetes Security Best Practices Part 6]]
