---
course: DevSecOps
topic: Getting Started with the DevSecOps Bootcamp
tags: [devsecops]
---

## Access Management in Kubernetes and AWS IAM Integration

### Introduction to Access Management

Access management is a critical component of securing any system, especially in the context of container orchestration platforms like Kubernetes. In Kubernetes, access management ensures that only authorized users and services can perform specific actions within the cluster. This is achieved through a combination of authentication and authorization mechanisms.

#### Authentication vs. Authorization

- **Authentication**: Verifies the identity of a user or service. For example, ensuring that a user is who they claim to be.
- **Authorization**: Determines what actions an authenticated user or service is allowed to perform. For example, allowing a user to deploy a new application but not delete existing ones.

### Kubernetes Role-Based Access Control (RBAC)

Kubernetes uses Role-Based Access Control (RBAC) to manage access to resources within the cluster. RBAC allows you to define roles and bind them to users or service accounts, thereby controlling their permissions.

#### Components of RBAC

- **Service Accounts**: Represents an identity in the system. Each pod runs with a service account that provides it with an identity.
- **Roles**: Define a set of permissions (verbs) that can be applied to resources (API objects).
- **RoleBindings**: Bind roles to subjects (users, groups, or service accounts).

#### Example: Creating a Role and RoleBinding

Let's create a role that allows read-only access to pods and then bind it to a service account.

```yaml
# pod-reader-role.yaml
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
# pod-reader-binding.yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: pod-reader-binding
  namespace: default
subjects:
- kind: ServiceAccount
  name: pod-reader-sa
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

To apply these configurations:

```sh
kubectl apply -f pod-reader-role.yaml
kubectl apply -f pod-reader-binding.yaml
```

### Integrating Kubernetes RBAC with AWS IAM

AWS Identity and Access Management (IAM) is used to manage access to AWS services. When using Amazon Elastic Kubernetes Service (EKS), you can integrate IAM with Kubernetes RBAC to provide a more robust access control mechanism.

#### Example: Using IAM Roles for Service Accounts

EKS supports IAM roles for service accounts, which allows you to grant IAM permissions to pods running in your cluster.

1. **Create an IAM Policy**:
    ```json
    {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Action": [
                    "s3:GetObject"
                ],
                "Resource": [
                    "arn:aws:s3:::my-bucket/*"
                ]
            }
        ]
    }
    ```

2. **Attach the Policy to an IAM Role**:
    ```sh
    aws iam create-policy --policy-name MyS3Policy --policy-document file://my-s3-policy.json
    aws iam create-role --role-name MyServiceRole --assume-role-policy-document file://trust-policy.json
    aws iam attach-role-policy --role-name MyServiceRole --policy-arn arn:aws:iam::123456789012:policy/MyS3Policy
    ```

3. **Map the IAM Role to a Service Account**:
    ```yaml
    apiVersion: rbac.authorization.k8s.io/v1
    kind: ClusterRole
    metadata:
      name: s3-access
    rules:
    - apiGroups: ["*"]
      resources: ["*"]
      verbs: ["*"]
    ---
    apiVersion: rbac.authorization.k8s.io/v1
    kind: ClusterRoleBinding
    metadata:
      name: s3-access-binding
    subjects:
    - kind: ServiceAccount
      name: my-service-account
      namespace: default
    roleRef:
      kind: ClusterRole
      name: s3-access
      apiGroup: rbac.authorization.k8s.io
    ```

4. **Annotate the Service Account**:
    ```yaml
    apiVersion: v1
    kind: ServiceAccount
    metadata:
      name: my-service-account
      annotations:
        eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/MyServiceRole
    ```

### Securing Applications Running Inside Kubernetes

Securing applications running inside Kubernetes involves several layers of protection, including securing container images, pods, and network traffic.

#### Container Image Security

Container images can contain vulnerabilities that can be exploited by attackers. To mitigate this risk, you should:

- **Use a trusted image registry**: Ensure that images come from a trusted source.
- **Scan images for vulnerabilities**: Use tools like Trivy or Clair to scan images for known vulnerabilities.
- **Sign images**: Use digital signatures to verify the authenticity of images.

#### Pod Security

Pods are the smallest deployable units in Kubernetes. Ensuring that pods are secure involves:

- **Limiting capabilities**: Use `securityContext` to limit the capabilities of containers running in pods.
- **Running as non-root**: Avoid running containers as root to reduce the attack surface.
- **Using SELinux/AppArmor**: Enable SELinux or AppArmor to enforce additional security policies.

#### Example: Pod Security Context

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  securityContext:
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
  containers:
  - name: my-container
    image: my-image
    securityContext:
      capabilities:
        drop:
        - ALL
      privileged: false
```

### Network Policies

Network policies allow you to control network traffic between pods and external entities. They enable you to implement micro-segmentation, which helps in isolating different parts of your application.

#### Example: Network Policy

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all-ingress
spec:
  podSelector: {}
  ingress: []
```

This policy denies all ingress traffic to all pods in the namespace.

### How to Prevent / Defend

#### Detection

- **Audit Logs**: Enable audit logs to track all API calls made to the Kubernetes API server.
- **Monitoring Tools**: Use monitoring tools like Prometheus and Grafana to monitor the health and security of your cluster.

#### Prevention

- **Least Privilege Principle**: Always follow the principle of least privilege. Grant only the minimum necessary permissions to users and services.
- **Regular Audits**: Regularly review and audit access controls to ensure they remain effective.

#### Secure Coding Fixes

Compare the insecure and secure versions of a service account configuration:

**Insecure Version**:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-service-account
```

**Secure Version**:
```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: my-service-account
  annotations:
    eks.amazonaws.com/role-arn: arn:aws:iam::123456789012:role/MyServiceRole
```

### Real-World Examples

#### Recent Breaches

- **CVE-2021-25741**: A vulnerability in Kubernetes allowed unauthorized access to the API server. This was due to improper validation of user input.
- **AWS EKS Incident**: In 2021, an incident occurred where unauthorized access to EKS clusters was possible due to misconfigured IAM roles.

### Practice Labs

For hands-on experience with DevSecOps in Kubernetes and AWS IAM integration, consider the following labs:

- **PortSwigger Web Security Academy**: Offers modules on Kubernetes security.
- **OWASP Juice Shop**: Provides a vulnerable web application to practice security testing.
- **CloudGoat**: Focuses on AWS security and includes scenarios for EKS and IAM.
- **Pacu**: A penetration testing framework for AWS that can help you understand and test IAM roles and policies.

By thoroughly understanding and implementing these concepts, you can significantly enhance the security of your Kubernetes clusters and applications running within them.

---
<!-- nav -->
[[12-Understanding Fundamental Concepts in DevSecOps|Understanding Fundamental Concepts in DevSecOps]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/05-Getting Started with the DevSecOps Bootcamp/DevSecOps Bootcamp Curriculum Overview/00-Overview|Overview]] | [[14-Automated Security Scanning and Reporting|Automated Security Scanning and Reporting]]
