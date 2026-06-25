---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management: IAM Roles and Kubernetes Roles

### Introduction to Kubernetes Access Management

Kubernetes access management is a critical aspect of securing your cluster. It ensures that only authorized users and processes can interact with the cluster resources. In this section, we will delve into the concepts of IAM roles and Kubernetes roles, focusing on how they work together to provide fine-grained access control.

### Understanding IAM Roles

IAM (Identity and Access Management) roles are a fundamental component of cloud platforms like AWS. These roles define the permissions and actions that a user or service can perform within the cloud environment. IAM roles are particularly useful because they allow you to grant temporary, limited permissions to users and services without giving them permanent access.

#### What is an IAM Role?

An IAM role is an entity that defines a set of permissions. Unlike users, roles do not have credentials associated with them. Instead, they are assumed by entities such as EC2 instances, Lambda functions, or even Kubernetes clusters. When an entity assumes a role, it gains the permissions defined by that role.

#### Why Use IAM Roles?

IAM roles are essential for several reasons:

- **Least Privilege Principle**: By using roles, you can ensure that users and services have only the permissions necessary to perform their tasks. This minimizes the risk of unauthorized access.
- **Temporary Permissions**: IAM roles can be assumed temporarily, which means that once the task is completed, the permissions are no longer active. This reduces the window of opportunity for potential misuse.
- **Centralized Management**: IAM roles can be managed centrally, making it easier to update permissions across multiple services and users.

### Understanding Kubernetes Roles

Kubernetes roles are similar to IAM roles but are specific to the Kubernetes ecosystem. They define permissions within the Kubernetes cluster, allowing you to control who can access and modify resources within the cluster.

#### What is a Kubernetes Role?

A Kubernetes role is a resource that defines a set of permissions within a specific namespace. These permissions determine what actions a user or service account can perform on the resources within that namespace.

#### Why Use Kubernetes Roles?

Kubernetes roles are crucial for several reasons:

- **Namespace-Level Control**: Kubernetes roles allow you to control access at the namespace level, ensuring that users can only access the resources within their designated namespaces.
- **Fine-Grained Access Control**: Kubernetes roles provide granular control over the actions that can be performed, such as creating, deleting, or viewing resources.
- **Integration with IAM**: Kubernetes roles can be integrated with IAM roles, allowing you to manage access both within the Kubernetes cluster and the broader cloud environment.

### Admin User and Cluster Role

In the context of Kubernetes access management, the admin user typically has the highest level of permissions within the cluster. This is achieved through the assignment of a cluster role.

#### What is a Cluster Role?

A cluster role is a role that applies to the entire cluster, rather than a specific namespace. It defines permissions that can be used across all namespaces within the cluster.

#### Example: Creating a Cluster Role

To create a cluster role, you can use a YAML manifest. Here is an example of a cluster role that grants full administrative access:

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRole
metadata:
  name: admin-role
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
```

This cluster role allows the user to perform any action on any resource within the cluster.

#### Assigning the Cluster Role

Once the cluster role is created, it needs to be assigned to a user or service account. This is done using a `ClusterRoleBinding`.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: admin-binding
subjects:
- kind: User
  name: admin-user
roleRef:
  kind: ClusterRole
  name: admin-role
  apiGroup: rbac.authorization.k8s.io
```

This binding assigns the `admin-role` to the `admin-user`, granting them full administrative access to the cluster.

### Developer User and Namespace Role

For developer users, it is important to limit their access to only the resources within their designated namespace. This ensures that developers can troubleshoot and manage their applications without affecting other parts of the cluster.

#### What is a Namespace Role?

A namespace role is a role that applies to a specific namespace within the cluster. It defines permissions that can be used only within that namespace.

#### Example: Creating a Namespace Role

Here is an example of a namespace role that grants read-only access to pods, deployments, and services within a namespace:

```yaml
apiVersion: rbac.authorization.k8s.io/v
kind: Role
metadata:
  name: developer-role
  namespace: dev-namespace
rules:
- apiGroups: [""]
  resources: ["pods", "deployments", "services"]
  verbs: ["get", "list", "watch"]
```

This role allows the user to perform read-only operations on pods, deployments, and services within the `dev-namespace`.

#### Assigning the Namespace Role

Once the namespace role is created, it needs to be assigned to a user or service account. This is done using a `RoleBinding`.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: developer-binding
  namespace: dev-namespace
subjects:
- kind: User
  name: developer-user
roleRef:
  kind: Role
  name: developer-role
  apiGroup: rbac.authorization.k8s.io
```

This binding assigns the `developer-role` to the `developer-user` within the `dev-namespace`, granting them read-only access to the specified resources.

### Integrating IAM Roles with Kubernetes Roles

To integrate IAM roles with Kubernetes roles, you can use the AWS IAM Authenticator for Kubernetes. This tool allows you to authenticate users and service accounts using IAM roles.

#### What is the AWS IAM Authenticator?

The AWS IAM Authenticator is a tool that integrates AWS IAM roles with Kubernetes authentication. It allows you to use IAM roles to authenticate users and service accounts, providing a seamless way to manage access across both environments.

#### Setting Up the AWS IAM Authenticator

To set up the AWS IAM Authenticator, you need to configure it on your Kubernetes cluster. Here is a step-by-step guide:

1. **Install the AWS IAM Authenticator**:
   ```sh
   curl -o aws-iam-authenticator https://amazon-eks.s3-us-west-2.amazonaws.com/1.18.9/2020-11-02/bin/linux/amazon-eks/aws-iam-authenticator
   chmod +x ./aws-iam-authenticator
   mv ./aws-iam-authenticator /usr/local/bin/
   ```

2. **Configure the Authenticator**:
   Add the authenticator to your Kubernetes API server configuration. This typically involves updating the `kube-apiserver` configuration to include the `--enable-iam-authenticator` flag.

3. **Create IAM Roles**:
   Create IAM roles for your users and service accounts. These roles should have the necessary permissions to access the Kubernetes cluster.

4. **Map IAM Roles to Kubernetes Users**:
   Use the `mapUsers` field in the `aws-auth` ConfigMap to map IAM roles to Kubernetes users.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: arn:aws:iam::123456789012:role/k8s-admin
      username: admin
      groups:
        - system:masters
  mapUsers: |
    - userarn: arn:aws:iam::123456789012:user/developer
      username: developer
      groups:
        - system:authenticated
```

This configuration maps the `k8s-admin` IAM role to the `admin` user and the `developer` IAM role to the `developer` user.

### Real-World Examples and Recent Breaches

Recent breaches and vulnerabilities have highlighted the importance of proper access management in Kubernetes clusters. One notable example is the breach of a Kubernetes cluster due to misconfigured IAM roles.

#### CVE-2021-25741: Kubernetes RBAC Misconfiguration

CVE-2021-25741 is a vulnerability that affects Kubernetes clusters with misconfigured RBAC (Role-Based Access Control). This vulnerability allows attackers to escalate their privileges by exploiting misconfigured roles and bindings.

#### Example: Misconfigured IAM Role

Consider a scenario where an IAM role is misconfigured to grant excessive permissions to a Kubernetes user. This could allow an attacker to gain unauthorized access to sensitive resources within the cluster.

```yaml
# Misconfigured IAM Role
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": "*",
      "Resource": "*"
    }
  ]
}
```

This IAM role grants full administrative access to the user, which is a significant security risk.

#### Secure Configuration

To prevent such vulnerabilities, it is crucial to follow best practices for configuring IAM roles and Kubernetes roles.

```yaml
# Secure IAM Role
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "eks:DescribeCluster",
        "eks:ListClusters",
        "eks:ListNodegroups",
        "eks:DescribeNodegroup"
      ],
      "Resource": "*"
    }
  ]
}
```

This IAM role grants only the necessary permissions to access the EKS cluster and its resources.

### How to Prevent / Defend

#### Detection

To detect misconfigurations and unauthorized access, you can use tools like Kubernetes auditing and monitoring solutions.

##### Kubernetes Auditing

Kubernetes auditing logs all API requests, providing a detailed record of who did what and when. You can enable auditing by configuring the `audit-policy.yaml` file.

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: Metadata
  users: ["system:serviceaccount:kube-system:default"]
- level: Request
  users: ["system:anonymous"]
- level: RequestResponse
  nonResources:
  - path: "/healthz"
```

This configuration enables auditing for specific users and paths.

##### Monitoring Solutions

Monitoring solutions like Prometheus and Grafana can help you monitor Kubernetes clusters for unusual activity. You can set up alerts to notify you of suspicious behavior.

```yaml
# Prometheus Alert Rule
alert: UnauthorizedAccess
expr: sum(kube_apiserver_request_total{code="200"}) > 0
for: 5m
labels:
  severity: "critical"
annotations:
  summary: "Unauthorized access detected in Kubernetes cluster"
  description: "Unusual API requests detected in the Kubernetes cluster."
```

This alert rule triggers when unauthorized access is detected.

#### Prevention

To prevent unauthorized access, follow these best practices:

- **Least Privilege Principle**: Grant users and service accounts only the permissions necessary to perform their tasks.
- **Regular Audits**: Regularly review and audit IAM roles and Kubernetes roles to ensure they are properly configured.
- **Monitoring and Alerts**: Set up monitoring and alerts to detect and respond to unauthorized access quickly.

#### Secure Coding Fixes

To demonstrate secure coding practices, let's compare a vulnerable configuration with a secure one.

##### Vulnerable Configuration

```yaml
# Vulnerable Kubernetes Role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: developer-role
  namespace: dev-namespace
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
```

This role grants full administrative access to the developer, which is a significant security risk.

##### Secure Configuration

```yaml
# Secure Kubernetes Role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: developer-role
  namespace: dev-namespace
rules:
- apiGroups: [""]
  resources: ["pods", "deployments", "services"]
  verbs: ["get", "list", "watch"]
```

This role grants only the necessary permissions to the developer, ensuring that they can only perform read-only operations on the specified resources.

### Hands-On Labs

To practice Kubernetes access management, you can use the following hands-on labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on Kubernetes security, including access management.
- **OWASP Juice Shop**: A vulnerable web application that includes Kubernetes security challenges.
- **Kubernetes Goat**: A vulnerable Kubernetes cluster designed for security training.

These labs provide practical experience in configuring and managing Kubernetes access controls.

### Conclusion

Kubernetes access management is a critical aspect of securing your cluster. By understanding and implementing IAM roles and Kubernetes roles, you can ensure that only authorized users and processes can interact with the cluster resources. Following best practices and using tools like Kubernetes auditing and monitoring solutions can help you detect and prevent unauthorized access.

---
<!-- nav -->
[[05-Kubernetes Access Management IAM Roles and Kubernetes Roles Part 1|Kubernetes Access Management IAM Roles and Kubernetes Roles Part 1]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/IAM Roles and K8s Roles How it works/00-Overview|Overview]] | [[07-Kubernetes Access Management IAM Roles and Kubernetes Roles|Kubernetes Access Management IAM Roles and Kubernetes Roles]]
