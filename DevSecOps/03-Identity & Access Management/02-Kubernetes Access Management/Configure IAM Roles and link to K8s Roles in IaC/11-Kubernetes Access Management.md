---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management

### Introduction to Kubernetes Access Management

Kubernetes access management is a critical aspect of securing your Kubernetes cluster. It ensures that only authorized entities can interact with the cluster and perform specific actions. This involves managing identities, roles, and permissions across different components of the system, including AWS IAM roles and Kubernetes roles.

### AWS IAM Roles and Kubernetes Integration

AWS Identity and Access Management (IAM) roles are used to grant permissions to AWS services and resources. In the context of Kubernetes, particularly when using Amazon Elastic Kubernetes Service (EKS), IAM roles play a crucial role in controlling access to the cluster and its resources.

#### Creating IAM Roles

To create IAM roles, you typically define them as AWS resources. These roles can then be mapped to Kubernetes roles within the cluster. Here’s an example of how to create an IAM role using AWS CLI:

```bash
aws iam create-role --role-name MyKubernetesRole --assume-role-policy-document file://trust-policy.json
```

The `trust-policy.json` file specifies the trust relationship between the role and the entity assuming it. An example of a trust policy document might look like this:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "eks.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

This policy allows the EKS service to assume the role.

### Mapping IAM Roles to Kubernetes Roles

Once the IAM roles are created, they need to be mapped to Kubernetes roles. This mapping is typically done through a ConfigMap in the Kubernetes cluster. The ConfigMap contains the necessary information to link the IAM roles to Kubernetes roles.

#### Example Configuration

Here’s an example of a ConfigMap that maps IAM roles to Kubernetes roles:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: arn:aws:iam::123456789012:role/MyKubernetesRole
      username: system:node:{{EC2PrivateDNSName}}
      groups:
        - system:bootstrappers
        - system:nodes
```

In this example, the `rolearn` field specifies the ARN of the IAM role, and the `username` field defines how the role is mapped to a Kubernetes user. The `groups` field specifies the Kubernetes groups to which the role belongs.

### Creating Kubernetes Roles and Permissions

In addition to IAM roles, you also need to create Kubernetes roles and permissions. These roles define the actions that users can perform within the Kubernetes cluster.

#### Example Kubernetes Role

Here’s an example of a Kubernetes role definition:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: developer-role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
```

This role grants developers the ability to get, list, and watch pods in the `default` namespace.

#### Example Kubernetes ClusterRole

For administrative users, you might want to create a more comprehensive role:

```yaml
apiVersion: rbac.authorization.k8s.io/v
kind: ClusterRole
metadata:
  name: admin-role
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
```

This role grants administrative privileges across all namespaces and resources.

### Creating Users and Assigning Roles

Finally, you need to create users and assign them to the roles you’ve defined. This can be done using Kubernetes service accounts.

#### Example Service Account

Here’s an example of a service account:

```yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: developer-sa
  namespace: default
```

To bind the service account to a role, you can use a RoleBinding:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: developer-binding
  namespace: default
subjects:
- kind: ServiceAccount
  name: developer-sa
  namespace: default
roleRef:
  kind: Role
  name: developer-role
  apiGroup: rbac.authorization.k8s.io
```

### Pitfalls and Best Practices

#### Common Mistakes

1. **Overly Permissive Roles**: Avoid granting more permissions than necessary. Overly permissive roles can lead to security vulnerabilities.
2. **Incorrect Role Mapping**: Ensure that IAM roles are correctly mapped to Kubernetes roles. Incorrect mappings can result in unauthorized access.
3. **Missing Role Bindings**: Ensure that all service accounts are properly bound to roles. Missing bindings can leave your cluster exposed.

#### Best Practices

1. **Least Privilege Principle**: Grant the minimum necessary permissions to users and roles.
2. **Regular Audits**: Regularly review and audit role assignments and permissions to ensure they remain appropriate.
3. **Use Namespaces**: Utilize namespaces to isolate resources and control access at a granular level.

### Real-World Examples

#### Recent Breaches

One notable breach involving Kubernetes access management occurred in 2021 when a misconfigured Kubernetes cluster led to unauthorized access and data exfiltration. The root cause was overly permissive roles and incorrect role mappings.

#### Secure Configuration Example

Here’s a secure configuration example that demonstrates best practices:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: arn:aws:iam::123456789012:role/MyKubernetesRole
      username: system:node:{{EC2PrivateDNSName}}
      groups:
        - system:bootstrappers
        - system:nodes
---
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: developer-role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: admin-role
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
---
apiVersion: v1
kind: ServiceAccount
metadata:
  name: developer-sa
  namespace: default
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: developer-binding
  namespace: default
subjects:
- kind: ServiceAccount
  name: developer-sa
  namespace: default
roleRef:
  kind: Role
  name: developer-role
  apiGroup: rbac.authorization.k8s.io
```

### How to Prevent / Defend

#### Detection

1. **Audit Logs**: Enable and monitor audit logs to detect unauthorized access attempts.
2. **Network Monitoring**: Monitor network traffic to detect unusual patterns that may indicate a breach.

#### Prevention

1. **Role-Based Access Control (RBAC)**: Implement RBAC to enforce least privilege principles.
2. **Namespace Isolation**: Use namespaces to isolate resources and control access at a granular level.

#### Secure Coding Fixes

Here’s an example of a vulnerable configuration and its secure counterpart:

**Vulnerable Configuration:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: developer-role
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
```

**Secure Configuration:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: developer-role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
```

### Conclusion

Properly configuring IAM roles and linking them to Kubernetes roles is essential for securing your Kubernetes cluster. By following best practices and regularly auditing your configurations, you can minimize the risk of unauthorized access and ensure the integrity of your cluster.

### Practice Labs

For hands-on practice with Kubernetes access management, consider the following labs:

- **PortSwigger Web Security Academy**: Offers modules on Kubernetes security.
- **OWASP Juice Shop**: Provides a vulnerable application for practicing security techniques.
- **Kubernetes Goat**: A security-focused Kubernetes environment for learning and testing.

These labs provide practical experience in configuring and securing Kubernetes clusters, helping you master the concepts discussed in this chapter.

---
<!-- nav -->
[[10-Kubernetes Access Management Configuring IAM Roles and Linking to Kubernetes Roles in Infrastructure as Code|Kubernetes Access Management Configuring IAM Roles and Linking to Kubernetes Roles in Infrastructure as Code]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure IAM Roles and link to K8s Roles in IaC/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure IAM Roles and link to K8s Roles in IaC/12-Practice Questions & Answers|Practice Questions & Answers]]
