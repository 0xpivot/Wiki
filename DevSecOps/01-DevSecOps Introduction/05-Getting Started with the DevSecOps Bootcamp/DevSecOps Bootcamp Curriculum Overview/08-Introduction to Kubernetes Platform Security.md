---
course: DevSecOps
topic: Getting Started with the DevSecOps Bootcamp
tags: [devsecops]
---

## Introduction to Kubernetes Platform Security

### Background Theory

Kubernetes is an open-source container orchestration system for automating deployment, scaling, and management of containerized applications. Originally designed by Google and now maintained by the Cloud Native Computing Foundation, Kubernetes has become the de facto standard for managing containerized workloads and services. As organizations increasingly adopt Kubernetes for their applications, the security implications have become a critical concern.

### Why Kubernetes Security Matters

Kubernetes introduces a new layer of complexity to the traditional cloud infrastructure. While it provides powerful tools for managing containerized applications, it also expands the attack surface. Security vulnerabilities in Kubernetes can lead to unauthorized access, data breaches, and service disruptions. Therefore, securing Kubernetes environments is essential for maintaining the integrity and confidentiality of applications and data.

### High-Level Concepts Covered in the Bootcamp

The Kubernetes security portion of the bootcamp will cover several key areas:

1. **Access Management**: Controlling who can access the Kubernetes cluster and what actions they can perform.
2. **Network Policies**: Configuring network policies to control traffic between pods and external networks.
3. **Pod Security Policies**: Enforcing security policies at the pod level to prevent insecure configurations.
4. **Secrets Management**: Safely storing and managing sensitive information such as passwords and API keys.
5. **Ingress Controllers**: Securing ingress controllers to protect the entry points to the Kubernetes cluster.
6. **Security Scanning**: Implementing security scanning tools to identify vulnerabilities in container images.
7. **Audit Logging**: Setting up audit logging to monitor and track activities within the Kubernetes cluster.

### Access Management to Kubernetes Cluster

#### What is Access Management?

Access management in Kubernetes refers to controlling who can access the Kubernetes cluster and what actions they can perform. This includes user authentication, authorization, and role-based access control (RBAC).

#### Why is Access Management Important?

Without proper access management, unauthorized users could gain access to the Kubernetes cluster and perform malicious actions. This could result in data breaches, service disruptions, and other security incidents.

#### How Does Access Management Work?

Access management in Kubernetes is primarily achieved through RBAC. RBAC allows administrators to define roles and permissions, and assign them to users or groups. Here’s a breakdown of the components involved:

- **Users**: Individuals who interact with the Kubernetes cluster.
- **Groups**: Collections of users.
- **Roles**: Sets of permissions that define what actions can be performed.
- **RoleBindings**: Bind roles to users or groups.
- **ClusterRoles**: Similar to roles but apply cluster-wide.
- **ClusterRoleBindings**: Bind cluster roles to users or groups.

#### Example of Access Management Configuration

Here is an example of how to configure access management using RBAC in Kubernetes:

```yaml
# Define a Role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]

# Define a RoleBinding
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

### Network Policies

#### What are Network Policies?

Network policies in Kubernetes allow you to control network traffic between pods and external networks. They provide a way to isolate pods and restrict communication based on labels and IP addresses.

#### Why are Network Policies Important?

Network policies help to reduce the attack surface by limiting unnecessary network traffic. Without network policies, any pod can communicate with any other pod, which can lead to security vulnerabilities.

#### How Do Network Policies Work?

Network policies are defined using `NetworkPolicy` objects. These objects specify the rules for allowing or denying traffic between pods. Here’s an example of a network policy:

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
```

This policy denies all ingress traffic to pods in the `default` namespace.

### Pod Security Policies

#### What are Pod Security Policies?

Pod security policies (PSPs) are a set of rules that enforce security controls at the pod level. They ensure that pods are configured securely and prevent insecure configurations.

#### Why are Pod Security Policies Important?

Pod security policies help to prevent common security issues such as running containers as root, mounting sensitive host directories, and executing privileged commands.

#### How Do Pod Security Policies Work?

Pod security policies are defined using `PodSecurityPolicy` objects. These objects specify the allowed and disallowed configurations for pods. Here’s an example of a pod security policy:

```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: restricted
spec:
  privileged: false
  seLinux:
    rule: RunAsAny
  supplementalGroups:
    rule: RunAsAny
  runAsUser:
    rule: MustRunAs
    ranges:
    - min: 1000
      max: 65535
  fsGroup:
    rule: RunAsAny
  volumes:
  - '*'
```

This policy restricts pods from running as privileged and limits the user IDs that can run the pods.

### Secrets Management

#### What is Secrets Management?

Secrets management in Kubernetes refers to the process of safely storing and managing sensitive information such as passwords, API keys, and certificates.

#### Why is Secrets Management Important?

Without proper secrets management, sensitive information could be exposed, leading to security breaches. Kubernetes provides mechanisms to store and manage secrets securely.

#### How Does Secrets Management Work?

Secrets in Kubernetes are stored as `Secret` objects. These objects can be used to store sensitive information and are accessible to pods through environment variables or volume mounts. Here’s an example of a secret:

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysecret
type: Opaque
data:
  password: cGFzc3dvcmQ=
```

This secret stores a base64-encoded password.

### Ingress Controllers

#### What are Ingress Controllers?

Ingress controllers in Kubernetes manage external access to the services in a cluster, typically HTTP. They provide a way to route traffic to different services based on rules.

#### Why are Ingress Controllers Important?

Ingress controllers help to secure the entry points to the Kubernetes cluster. Without proper configuration, ingress controllers could expose services to unauthorized access.

#### How Do Ingress Controllers Work?

Ingress controllers are configured using `Ingress` objects. These objects specify the rules for routing traffic to different services. Here’s an example of an ingress controller:

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: example-ingress
  namespace: default
spec:
  rules:
  - host: example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: example-service
            port:
              number: 80
```

This ingress controller routes traffic to the `example-service`.

### Security Scanning

#### What is Security Scanning?

Security scanning in Kubernetes involves using tools to identify vulnerabilities in container images before they are deployed.

#### Why is Security Scanning Important?

Security scanning helps to identify and mitigate vulnerabilities in container images, reducing the risk of security incidents.

#### How Does Security Scanning Work?

Security scanning tools such as Trivy and Clair can be integrated into the CI/CD pipeline to scan container images for vulnerabilities. Here’s an example of using Trivy to scan a container image:

```sh
trivy image --severity CRITICAL,HIGH myimage:latest
```

### Audit Logging

#### What is Audit Logging?

Audit logging in Kubernetes involves setting up logging to monitor and track activities within the Kubernetes cluster.

#### Why is Audit Logging Important?

Audit logging helps to detect and respond to security incidents by providing a record of activities within the cluster.

#### How Does Audit Logging Work?

Audit logging is configured using the `audit-policy.yaml` file. This file specifies the rules for logging activities. Here’s an example of an audit policy:

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: Metadata
  users: ["system:serviceaccount:kube-system:default"]
- level: RequestResponse
  verbs: ["create", "update", "delete"]
```

This policy logs metadata for activities performed by the `default` service account and logs request and response details for create, update, and delete operations.

### Real-World Examples and Recent Breaches

#### Example: CVE-2021-25741

CVE-2021-25741 is a vulnerability in Kubernetes that allows attackers to escalate privileges and execute arbitrary code. This vulnerability highlights the importance of keeping Kubernetes and its components up to date and securing access management.

#### Example: Docker Hub Breach

In 2021, Docker Hub experienced a breach that resulted in unauthorized access to container images. This breach underscores the importance of securing container images and implementing robust secrets management practices.

### How to Prevent / Defend

#### Access Management

**Detection**: Monitor access attempts using audit logging and alert on unauthorized access.

**Prevention**: Implement RBAC and limit access to the minimum necessary.

**Secure Coding Fix**:
- **Vulnerable Code**:
  ```yaml
  apiVersion: rbac.authorization.k8s.io/v1
  kind: RoleBinding
  metadata:
    name: admin-binding
    namespace: default
  subjects:
  - kind: User
    name: johndoe
    apiGroup: rbac.authorization.k8s.io
  roleRef:
    kind: ClusterRole
    name: cluster-admin
    apiGroup: rbac.authorization.k8s.io
  ```
- **Fixed Code**:
  ```yaml
  apiVersion: rbac.authorization.k8s.io/v1
  kind: RoleBinding
  metadata:
    name: limited-binding
    namespace: default
  subjects:
  - kind: User
    name: johndoe
    apiGroup: rbac.authorization.k8s.io
  roleRef:
    kind: Role
    name: pod-reader
    apiGroup: rbac.authorization.k8
  ```

#### Network Policies

**Detection**: Monitor network traffic using network policies and alert on unauthorized traffic.

**Prevention**: Implement network policies to restrict unnecessary network traffic.

**Secure Coding Fix**:
- **Vulnerable Code**:
  ```yaml
  apiVersion: networking.k8s.io/v1
  kind: NetworkPolicy
  metadata:
    name: allow-all-ingress
    namespace: default
  spec:
    podSelector: {}
    policyTypes:
    - Ingress
  ```
- **Fixed Code**:
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
  ```

#### Pod Security Policies

**Detection**: Monitor pod configurations using pod security policies and alert on insecure configurations.

**Prevention**: Implement pod security policies to enforce secure configurations.

**Secure Coding Fix**:
- **Vulnerable Code**:
  ```yaml
  apiVersion: policy/v1beta1
  kind: PodSecurityPolicy
  metadata:
    name: unrestricted
  spec:
    privileged: true
    seLinux:
      rule: RunAsAny
    supplementalGroups:
      rule: RunAsAny
    runAsUser:
      rule: RunAsAny
    fsGroup:
      rule: RunAsAny
    volumes:
    - '*'
  ```
- **Fixed Code**:
  ```yaml
  apiVersion: policy/v1beta1
  kind: PodSecurityPolicy
  metadata:
    name: restricted
  spec:
    privileged: false
    seLinux:
      rule: RunAsAny
    supplementalGroups:
      rule: RunAsAny
    runAsUser:
      rule: MustRunAs
      ranges:
      - min: 1000
        max: 65535
    fsGroup:
      rule: RunAsAny
    volumes:
    - '*'
  ```

#### Secrets Management

**Detection**: Monitor access to secrets using audit logging and alert on unauthorized access.

**Prevention**: Implement secrets management practices to securely store and manage sensitive information.

**Secure Coding Fix**:
- **Vulnerable Code**:
  ```yaml
  apiVersion: v1
  kind: Secret
  metadata:
    name: mysecret
  type: Opaque
  data:
    password: cGFzc3dvcmQ=
  ```
- **Fixed Code**:
  ```yaml
  apiVersion: v1
  kind: Secret
  metadata:
    name: mysecret
  type: Opaque
  data:
    password: cGFzc3dvcmQ=
  ```

#### Ingress Controllers

**Detection**: Monitor ingress traffic using audit logging and alert on unauthorized access.

**Prevention**: Implement ingress controllers to secure the entry points to the Kubernetes cluster.

**Secure Coding Fix**:
- **Vulnerable Code**:
  ```yaml
  apiVersion: networking.k8s.io/v1
  kind: Ingress
  metadata:
    name: example-ingress
    namespace: default
  spec:
    rules:
    - host: example.com
      http:
        paths:
        - path: /
          pathType: Prefix
          backend:
            service:
              name: example-service
              port:
                number: 80
  ```
- **Fixed Code**:
  ```yaml
  apiVersion: networking.k8s.io/v1
  kind: Ingress
  metadata:
    name: example-ingress
    namespace: default
  spec:
    rules:
    - host: example.com
      http:
        paths:
        - path: /
          pathType: Prefix
          backend:
            service:
              name: example-service
              port:
                number: 80
  ```

#### Security Scanning

**Detection**: Monitor container images using security scanning tools and alert on vulnerabilities.

**Prevention**: Implement security scanning tools to identify and mitigate vulnerabilities in container images.

**Secure Coding Fix**:
- **Vulnerable Code**:
  ```sh
  docker build -t myimage:latest .
  ```
- **Fixed Code**:
  ```sh
  trivy image --severity CRITICAL,HIGH myimage:latest
  ```

#### Audit Logging

**Detection**: Monitor activities within the Kubernetes cluster using audit logging and alert on suspicious activities.

**Prevention**: Implement audit logging to monitor and track activities within the Kubernetes cluster.

**Secure Coding Fix**:
- **Vulnerable Code**:
  ```yaml
  apiVersion: audit.k8s.io/v1
  kind: Policy
  rules:
  - level: None
  ```
- **Fixed Code**:
  ```yaml
  apiVersion: audit.k8s.io/v1
  kind: Policy
  rules:
  - level: Metadata
    users: ["system:serviceaccount:kube-system:default"]
  - level: RequestResponse
    verbs: ["create", "update", "delete"]
  ```

### Practice Labs

For hands-on practice with Kubernetes security, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on web application security, including some that touch on Kubernetes security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training, which can be deployed on Kubernetes.
- **Kubernetes Goat**: A Kubernetes-based security training platform that simulates various security scenarios.
- **CloudGoat**: A cloud security training platform that includes Kubernetes security exercises.

By thoroughly understanding and implementing these security measures, you can significantly enhance the security of your Kubernetes environments and protect against potential threats.

---
<!-- nav -->
[[09-Introduction to DevSecOps|Introduction to DevSecOps]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/05-Getting Started with the DevSecOps Bootcamp/DevSecOps Bootcamp Curriculum Overview/00-Overview|Overview]] | [[11-Security Essentials for DevSecOps|Security Essentials for DevSecOps]]
