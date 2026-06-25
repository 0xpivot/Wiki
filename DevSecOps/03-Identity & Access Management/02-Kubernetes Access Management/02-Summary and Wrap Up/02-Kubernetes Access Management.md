---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management

### Introduction to Kubernetes Access Management

Kubernetes Access Management is a critical aspect of securing your Kubernetes cluster. It involves controlling who can access the cluster and what actions they can perform within it. This is achieved through Role-Based Access Control (RBAC), Identity and Access Management (IAM), and other mechanisms. In this section, we will delve into the details of setting up RBAC policies and IAM roles for an Amazon EKS (Elastic Kubernetes Service) cluster.

### Role-Based Access Control (RBAC)

Role-Based Access Control (RBAC) is a method of regulating access to resources based on the roles of individual users within an organization. In Kubernetes, RBAC allows you to define roles and bind them to users or groups. Each role contains a set of permissions that specify what actions can be performed on which resources.

#### Key Concepts

- **Roles**: Define a set of permissions.
- **RoleBindings**: Bind roles to users or groups.
- **ClusterRoles**: Similar to roles but apply cluster-wide.
- **ClusterRoleBindings**: Bind cluster roles to users or groups.

#### Example: Creating an RBAC Policy

Let's create an RBAC policy for a developer and an admin in a Kubernetes cluster.

```yaml
# Developer Role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: developer-role
  namespace: development
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch"]

# Developer RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: developer-binding
  namespace: development
subjects:
- kind: User
  name: developer-user
roleRef:
  kind: Role
  name: developer-role
  apiGroup: rbac.authorization.k8s.io

# Admin ClusterRole
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: admin-clusterrole
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]

# Admin ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-binding
subjects:
- kind: User
  name: admin-user
roleRef:
  kind: ClusterRole
  name: admin-clusterrole
  apiGroup: rbac.authorization.k8s.io
```

### Identity and Access Management (IAM) in AWS

In AWS, Identity and Access Management (IAM) is used to manage access to AWS services. IAM roles can be created to grant permissions to users or groups. These roles can then be mapped to Kubernetes roles using RBAC.

#### Example: Creating IAM Roles

Let's create IAM roles for a developer and an admin in AWS.

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "eks:DescribeCluster"
      ],
      "Resource": "*"
    }
  ]
}
```

For the developer:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "eks:DescribeCluster"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "eks:ListClusters"
      ],
      "Resource": "*"
    }
  ]
}
```

For the admin:

```json
{
   "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "eks:*"
      ],
      "Resource": "*"
    }
  ]
}
```

### Mapping IAM Roles to Kubernetes Roles

To map IAM roles to Kubernetes roles, you need to configure the `aws-auth` ConfigMap in the `kube-system` namespace.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: arn:aws:iam::123456789012:role/k8s-developer
      username: system:node:{{EC2PrivateDNSName}}
      groups:
        - system:bootstrappers
        - system:nodes
        - k8s-developer
    - rolearn: arn:aws:iam::123456789012:role/k8s-admin
      username: system:node:{{EC2PrivateDNSName}}
      groups:
        - system:bootstrappers
        - system:nodes
        - k8s-admin
```

### Saving Configuration Changes

Once you have configured the access management settings, it is important to save these changes in a version control system like Git. This ensures that you can track changes and revert to previous configurations if necessary.

#### Example: Saving Configuration in Git

```bash
git status
# Output:
# On branch main
# Your branch is up to date with 'origin/main'.
#
# Changes not staged for commit:
#   (use "git add <file>..." to update what will be committed)
#   (use "git restore <file>..." to discard changes in working directory)
#	modified:   rbac-policies.yaml
#	modified:   iam-policy.json
#	modified:   aws-auth-configmap.yaml

git add .
git commit -m "Add RBAC and IAM policies for Kubernetes access management"
git push origin main
```

### Real-World Examples and Recent Breaches

Recent breaches involving Kubernetes clusters often involve misconfigured access controls. For example, the 2021 breach of a major cryptocurrency exchange involved unauthorized access to a Kubernetes cluster due to misconfigured RBAC policies.

#### Example: CVE-2021-25741

CVE-2021-25741 was a vulnerability in Kubernetes that allowed attackers to bypass RBAC restrictions and gain elevated privileges. This highlights the importance of properly configuring and regularly auditing access controls.

### How to Prevent / Defend

#### Detection

Regularly audit your RBAC policies and IAM roles to ensure they are correctly configured. Tools like `kubectl auth can-i` can help verify permissions.

```bash
kubectl auth can-i get pods --namespace=development
```

#### Prevention

- **Least Privilege Principle**: Ensure that users and roles have only the minimum permissions required to perform their tasks.
- **Regular Audits**: Conduct regular audits of your RBAC and IAM configurations.
- **Automated Compliance Checks**: Use tools like `kube-bench` to check compliance with best practices.

#### Secure Coding Fixes

**Vulnerable Code**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: developer-role
  namespace: development
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["*"]  # Vulnerable: All verbs allowed
```

**Fixed Code**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: developer-role
  namespace: development
rules:
- apiGroups: [""]
  resources: ["pods", "services"]
  verbs: ["get", "list", "watch"]  # Fixed: Limited verbs allowed
```

### Hardening Measures

- **Enable Network Policies**: Use Kubernetes Network Policies to restrict traffic between pods.
- **Use Pod Security Policies**: Implement Pod Security Policies to enforce security rules at the pod level.
- **Enable Audit Logging**: Enable audit logging to monitor and log all API calls made to the Kubernetes API server.

### Hands-On Labs

To practice Kubernetes access management, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a module on Kubernetes security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **Kubernetes Goat**: A Kubernetes-based security training platform.

### Conclusion

Properly configuring access management in Kubernetes is crucial for maintaining the security of your cluster. By using RBAC and IAM roles effectively, you can ensure that only authorized users have access to the resources they need. Regular audits and automated compliance checks are essential to maintaining a secure environment.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/07-Summary and Wrap Up/01-Introduction to Kubernetes Access Management|Introduction to Kubernetes Access Management]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/07-Summary and Wrap Up/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/07-Summary and Wrap Up/03-Practice Questions & Answers|Practice Questions & Answers]]
