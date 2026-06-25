---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Introduction to Kubernetes Access Management

Kubernetes, often referred to as K8s, is an open-source system for automating deployment, scaling, and management of containerized applications. One of the critical aspects of managing a Kubernetes cluster is ensuring that only authorized entities can interact with the cluster. This is achieved through Role-Based Access Control (RBAC), which is a method of regulating access to resources based on the roles of individual users within an organization.

### What is RBAC?

Role-Based Access Control (RBAC) is a security model that restricts network access based on the roles of individual users within an organization. In the context of Kubernetes, RBAC allows administrators to define roles and bind them to users or groups, thereby controlling what actions those users or groups can perform within the cluster.

#### Why RBAC Matters

RBAC is crucial because it ensures that only authorized users can perform specific actions within the Kubernetes cluster. This helps in maintaining the integrity and security of the cluster by preventing unauthorized access and potential misuse of resources.

#### How RBAC Works

RBAC in Kubernetes operates through three main components:

1. **Roles**: Define a set of permissions.
2. **RoleBindings**: Bind roles to users or groups within a namespace.
3. **ClusterRoles**: Similar to Roles but apply across the entire cluster.
4. **ClusterRoleBindings**: Bind ClusterRoles to users or groups across the entire cluster.

### Creating Users, Groups, and Access in Self-Managed Clusters

In a self-managed Kubernetes cluster, you can create users, groups, and assign access to these entities. This involves defining roles and role bindings, and ensuring that the appropriate permissions are granted.

#### Example: Defining a Role

Let's define a role that allows a user to list pods in a specific namespace.

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "list"]
```

This role definition specifies that the user can perform `get` and `list` operations on pods within the `default` namespace.

#### Example: Binding a Role to a User

Next, we bind this role to a specific user.

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

Here, the `read-pods` role binding associates the `pod-reader` role with the user `johndoe`.

### Managed Kubernetes Clusters (AWS EKS, Azure AKS)

For managed Kubernetes clusters such as AWS EKS or Azure AKS, the cloud provider offers additional services to manage cluster access more easily. These services abstract away some of the complexities involved in setting up and managing RBAC.

#### Using AWS IAM with EKS

When using AWS EKS, you can leverage AWS Identity and Access Management (IAM) to manage access to your Kubernetes cluster. This involves integrating IAM with Kubernetes RBAC.

##### Step-by-Step Integration

1. **Create an IAM Policy**: Define the permissions required for accessing the Kubernetes cluster.
   
   ```json
   {
     "Version": "2012-10-17",
     "Statement": [
       {
         "Effect": "Allow",
         "Action": [
           "eks:DescribeCluster",
           "eks:ListClusters"
         ],
         "Resource": "*"
       }
     ]
   }
   ```

2. **Attach the Policy to an IAM User or Group**: Assign the policy to the appropriate IAM user or group.

3. **Map IAM Users to Kubernetes Users**: Use the AWS IAM Authenticator to map IAM users to Kubernetes users.

   ```bash
   kubectl apply -f https://raw.githubusercontent.com/kubernetes-sigs/aws-iam-authenticator/master/docs/examples/rbac.yaml
   ```

4. **Configure the AWS IAM Authenticator**: Ensure the authenticator is configured correctly to allow IAM users to authenticate with the Kubernetes cluster.

   ```bash
   aws eks --region <region> update-cluster-config --name <cluster-name> --enabled-features IAM
   ```

### Full Access Management Configuration

To achieve full access management, you need to configure both authentication and authorization. Here’s how you can set up a complete access management configuration using AWS IAM and Kubernetes RBAC.

#### Authentication with AWS IAM

1. **Install the AWS IAM Authenticator**:
   
   ```bash
   curl -o aws-iam-authenticator https://amazon-eks.s3-us-west-2.amazonaws.com/1.18.9/2020-11-02/bin/linux/amazon-eks/1.18.9/aws-iam-authenticator
   chmod +x ./aws-iam-authenticator
   mv ./aws-iam-authenticator /usr/local/bin/
   ```

2. **Configure the Authenticator**:
   
   ```bash
   aws eks --region <region> update-cluster-config --name <cluster-name> --enabled-features IAM
   ```

#### Authorization with Kubernetes RBAC

1. **Define Roles and RoleBindings**:
   
   ```yaml
   apiVersion: rbac.authorization.k8s.io/v1
   kind: Role
   metadata:
     namespace: default
     name: pod-reader
   rules:
   - apiGroups: [""]
     resources: ["pods"]
     verbs: ["get", "list"]
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
     apiGroup: rbac.authorization.k
   ```

2. **Apply the Configuration**:
   
   ```bash
   kubectl apply -f rbac-config.yaml
   ```

### Real-World Examples and Recent Breaches

Recent breaches involving Kubernetes clusters highlight the importance of proper access management. For instance, the breach of a Kubernetes cluster at a major cloud provider in 2021 was attributed to misconfigured RBAC policies, allowing unauthorized access to sensitive data.

#### CVE Example: CVE-2021-25741

CVE-2021-25741 is a vulnerability in Kubernetes that allows an attacker to bypass RBAC restrictions by manipulating the `Impersonate` header in API requests. This vulnerability underscores the need for robust RBAC configurations and regular audits.

### Pitfalls and Common Mistakes

1. **Overly Permissive Roles**: Avoid granting excessive permissions to roles. This can lead to unauthorized access and potential breaches.
   
2. **Misconfigured RoleBindings**: Incorrectly configuring role bindings can result in unintended access to resources.

3. **Outdated Policies**: Failing to regularly review and update RBAC policies can leave the cluster vulnerable to attacks.

### How to Prevent / Defend

#### Detection

1. **Audit Logs**: Enable audit logs to track all API requests and responses. This helps in identifying unauthorized access attempts.
   
   ```bash
   kubectl get events --all-namespaces
   ```

2. **Monitoring Tools**: Use monitoring tools like Prometheus and Grafana to monitor cluster activity and detect anomalies.

#### Prevention

1. **Least Privilege Principle**: Always follow the principle of least privilege. Grant only the minimum necessary permissions to roles and users.
   
2. **Regular Audits**: Conduct regular audits of RBAC configurations to ensure they remain secure and up-to-date.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of RBAC configurations:

**Vulnerable Configuration:**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["*"]
  verbs: ["*"]
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
  verbs: ["get", "list"]
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

### Hardening Measures

1. **Enable Network Policies**: Use Kubernetes Network Policies to control traffic flow within the cluster.
   
2. **Use Pod Security Policies**: Implement Pod Security Policies to enforce security constraints on pods.

### Hands-On Labs

To gain practical experience with Kubernetes access management, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on securing Kubernetes clusters.
- **OWASP Juice Shop**: Provides a vulnerable application to practice securing Kubernetes deployments.
- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security best practices.

By thoroughly understanding and implementing RBAC in Kubernetes, you can significantly enhance the security of your cluster and protect against unauthorized access and potential breaches.

---
<!-- nav -->
[[04-Introduction to Kubernetes Access Management Part 4|Introduction to Kubernetes Access Management Part 4]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Role Based Access Control RBAC/00-Overview|Overview]] | [[06-Introduction to Kubernetes Access Management|Introduction to Kubernetes Access Management]]
