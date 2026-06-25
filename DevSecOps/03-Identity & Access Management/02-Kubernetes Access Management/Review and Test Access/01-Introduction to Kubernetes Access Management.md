---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Introduction to Kubernetes Access Management

Kubernetes access management is a critical aspect of securing your cluster. It ensures that only authorized entities can interact with the cluster and its resources. This includes managing user roles, permissions, and authentication mechanisms. In this chapter, we will delve deep into the concepts of Kubernetes access management, focusing on how to review and test access within a Kubernetes cluster.

### Background Theory

Kubernetes uses Role-Based Access Control (RBAC) to manage access to the API server. RBAC allows you to define roles and bind those roles to users or service accounts. This ensures that only authorized entities can perform specific actions within the cluster.

#### Key Concepts

- **Role**: A set of permissions that define what actions can be performed on which resources.
- **ClusterRole**: Similar to a Role, but it applies cluster-wide.
- **RoleBinding**: Binds a Role to a user or group.
- **ClusterRoleBinding**: Binds a ClusterRole to a user or group.

### Creating and Configuring a Kubernetes Cluster

Before diving into access management, let's briefly cover the creation and configuration of a Kubernetes cluster. We'll use Amazon Elastic Kubernetes Service (EKS) as an example.

#### Step-by-Step Creation of an EKS Cluster

1. **Create an EKS Cluster**:
    - Navigate to the AWS Management Console.
    - Go to the EKS service.
    - Click on "Get started" to create a new cluster.
    - Fill out the required details such as cluster name, VPC, subnets, etc.
    - Create the cluster.

2. **Check the Cluster Status**:
    - Once the cluster is created, you can check its status in the AWS console.
    - Ensure the cluster is active and ready to use.

3. **Review Cluster Configuration**:
    - Go to the "Resources" section of the EKS console.
    - Here, you can see various components like pods, deployments, services, config maps, and secrets.

### Config Maps and Secrets

Config maps and secrets are essential components in Kubernetes for storing configuration data and sensitive information, respectively.

#### Config Maps

Config maps store non-confidential data in key-value pairs. They are used to externalize configuration data so that container images can be reused across environments.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: example-config
data:
  example-key: example-value
```

#### Secrets

Secrets store sensitive data such as passwords, tokens, and keys. They are encoded in base64 to ensure that the data remains confidential.

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: example-secret
type: Opaque
data:
  password: cGFzc3dvcmQ=  # Base64 encoded value
```

### AWS Auth Config Map

In an EKS cluster, the `aws-auth` ConfigMap is crucial for managing IAM roles and users that can access the cluster.

#### Structure of aws-auth Config Map

The `aws-auth` ConfigMap contains mappings between IAM roles/users and Kubernetes usernames/groups.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: arn:aws:iam::123456789012:role/example-role
      username: system:node:{{EC2PrivateDNSName}}
      groups:
        - system:bootstrappers
        - system:nodes
```

### Reviewing and Testing Access

To ensure that your Kubernetes cluster is properly configured and that access is managed correctly, you need to review and test the access controls.

#### Steps to Review Access

1. **Check Config Maps**:
    - Navigate to the `kube-system` namespace in the Kubernetes dashboard.
    - Look for the `aws-auth` ConfigMap.
    - Verify the contents to ensure correct mappings.

2. **Check Roles and RoleBindings**:
    - Use `kubectl` commands to list roles and role bindings.
    - Example commands:
      ```sh
      kubectl get roles --all-namespaces
      kubectl get rolebindings --all-namespaces
      ```

3. **Test Access**:
    - Create a test user or service account.
    - Bind the user/service account to a role.
    - Attempt to perform actions that should be allowed or denied based on the role.

### Real-World Examples and Recent Breaches

Recent breaches and vulnerabilities have highlighted the importance of proper access management in Kubernetes clusters.

#### Example: CVE-2021-25741

CVE-2021-25741 is a privilege escalation vulnerability in Kubernetes. An attacker with access to a pod could potentially escalate their privileges to gain control of the entire cluster.

- **Impact**: Allows an attacker to execute arbitrary code with elevated privileges.
- **Mitigation**: Ensure that all pods run with the least necessary privileges. Use RBAC to restrict access.

### How to Prevent / Defend

#### Detection

- **Audit Logs**: Enable audit logging in Kubernetes to track all API requests.
- **Monitoring Tools**: Use tools like Prometheus and Grafana to monitor cluster activity.

#### Prevention

- **Least Privilege Principle**: Assign the minimum necessary permissions to users and service accounts.
- **Regular Audits**: Conduct regular audits of roles and permissions to ensure compliance.

#### Secure Coding Fixes

##### Vulnerable Code Example

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: full-access-role
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  namespace: default
  name: full-access-binding
subjects:
- kind: User
  name: example-user
roleRef:
  kind: Role
  name: full-access-role
  apiGroup: rbac.authorization.k8s.io
```

##### Secure Code Example

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: limited-access-role
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list", "watch"]
---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  namespace: default
  name: limited-access-binding
subjects:
- kind: User
  name: example-user
roleRef:
  kind: Role
  name: limited-access-role
  apiGroup: rbac.authorization.k8s.io
```

### Hands-On Labs

For practical experience with Kubernetes access management, consider the following labs:

- **PortSwigger Web Security Academy**: Offers modules on Kubernetes security.
- **OWASP Juice Shop**: Contains challenges related to Kubernetes security.
- **Kubernetes Goat**: Provides a platform to practice Kubernetes security scenarios.

### Conclusion

Properly managing access in a Kubernetes cluster is crucial for maintaining the security and integrity of your environment. By understanding and implementing the principles of RBAC, regularly reviewing and testing access controls, and using secure coding practices, you can significantly reduce the risk of unauthorized access and potential breaches.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Review and Test Access/00-Overview|Overview]] | [[02-Kubernetes Access Management Review and Test Access Part 1|Kubernetes Access Management Review and Test Access Part 1]]
