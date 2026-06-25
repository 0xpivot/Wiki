---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management

### Introduction to Kubernetes Access Management

Kubernetes access management is a critical aspect of securing your Kubernetes clusters. It ensures that only authorized entities can interact with the cluster and its resources. This includes managing user identities, roles, and permissions. In this section, we will delve into the concepts of Kubernetes access management, how to configure and test access, and how to prevent unauthorized access.

### Configuring Access Credentials

In the context of Kubernetes, access credentials are typically managed through service accounts, which are used to authenticate and authorize API requests. Service accounts are associated with specific roles and role bindings, which define the permissions granted to the account.

#### Local Configuration of Access Credentials

When configuring access credentials locally, you typically use `kubectl` to interact with the Kubernetes cluster. The `kubectl` command-line tool uses a configuration file (`~/.kube/config`) to store the necessary credentials and cluster information.

```yaml
apiVersion: v1
kind: Config
clusters:
- name: my-cluster
  cluster:
    server: https://my-cluster.example.com
users:
- name: my-user
  user:
    token: <your-token>
contexts:
- context:
    cluster: my-cluster
    user: my-user
  name: my-context
current-context: my-context
```

This configuration file specifies the cluster details and the user credentials. The `token` field contains an authentication token that grants access to the cluster.

### Testing Access with `kubectl`

Once the access credentials are configured, you can test the access using `kubectl`. The `kubectl` command allows you to interact with the Kubernetes API server and perform various operations such as listing nodes, pods, and namespaces.

#### Example: Listing Nodes

To list the nodes in the cluster, you can use the following command:

```sh
kubectl get nodes
```

This command retrieves the list of nodes in the cluster and displays them. If the user has sufficient permissions, this command will succeed and return the list of nodes.

#### Example: Listing Namespaces

To list all namespaces in the cluster, you can use the following command:

```sh
kubectl get namespaces
```

This command retrieves the list of namespaces and displays them. If the user has sufficient permissions, this command will succeed and return the list of namespaces.

### Switching Users and Setting Environment Variables

In some scenarios, you might need to switch between different users to test their respective permissions. This can be achieved by setting environment variables that override the default credentials.

#### Example: Switching to Kubernetes Admin User

To switch to the Kubernetes admin user, you need to set the environment variables for the access keys. The following steps demonstrate how to achieve this:

1. **Get the Current Identity**

   First, verify the current identity using the `aws sts get-caller-identity` command:

   ```sh
   aws sts get-caller-identity
   ```

   This command returns the ARN of the currently configured user.

2. **Set Environment Variables**

   Next, set the environment variables for the new user's access keys:

   ```sh
   export AWS_ACCESS_KEY_ID=<new-access-key-id>
   export AWS_SECRET_ACCESS_KEY=<new-secret-access-key>
   ```

   These environment variables override the default credentials and allow you to authenticate as the new user.

3. **Verify the New Identity**

   After setting the environment variables, verify the new identity using the `aws sts get-caller-identity` command again:

   ```sh
   aws sts get-caller-identity
   ```

   This command should now return the ARN of the new user.

### Role-Based Access Control (RBAC)

Role-Based Access Control (RBAC) is a fundamental security feature in Kubernetes that allows you to manage access to resources based on roles and permissions. RBAC consists of three main components: Roles, RoleBindings, and ClusterRoles, ClusterRoleBindings.

#### Roles and RoleBindings

A Role defines a set of permissions that can be granted to a user or group. A RoleBinding associates a Role with a user or group, granting them the specified permissions.

```yaml
# Example Role
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]

# Example RoleBinding
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: default
subjects:
- kind: Group
  name: manager-group
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

In this example, the `pod-reader` Role grants the ability to read pods, and the `read-pods` RoleBinding associates this Role with the `manager-group`.

#### ClusterRoles and ClusterRoleBindings

ClusterRoles and ClusterRoleBindings are similar to Roles and RoleBindings but apply cluster-wide rather than within a specific namespace.

```yaml
# Example ClusterRole
apiVersion: rbac.authorization.k8s.io/v
kind: ClusterRole
metadata:
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]

# Example ClusterRoleBinding
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: read-pods-global
subjects:
- kind: Group
  name: manager-group
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: ClusterRole
  name: pod-reader
  apiGroup: rb
```

In this example, the `pod-reader` ClusterRole grants the ability to read pods across all namespaces, and the `read-pods-global` ClusterRoleBinding associates this ClusterRole with the `manager-group`.

### Recent Real-World Examples

Recent breaches and vulnerabilities related to Kubernetes access management highlight the importance of proper configuration and testing. For example, the CVE-2021-25741 vulnerability in Kubernetes allowed attackers to bypass RBAC restrictions and gain elevated privileges.

#### CVE-2021-25741

CVE-2021-25741 is a privilege escalation vulnerability in Kubernetes that affects versions prior to 1.21.4, 1.20.10, and 1.19.13. This vulnerability allows attackers to bypass RBAC restrictions and gain elevated privileges.

**Impact**: An attacker with access to a low-privileged account could potentially escalate their privileges and gain full control over the cluster.

**Mitigation**: Ensure that your Kubernetes cluster is updated to the latest version, and regularly review and audit your RBAC configurations.

### How to Prevent / Defend

#### Detection

To detect unauthorized access attempts, you can enable auditing in Kubernetes. Auditing logs provide detailed records of API requests, allowing you to identify and investigate suspicious activity.

```yaml
apiVersion: audit.k8s.io/v1
kind: Policy
rules:
- level: Metadata
  users: ["system:serviceaccount:kube-system:default"]
- level: Request
  users: ["system:serviceaccount:kube-system:default"]
- level: RequestResponse
  users: ["system:serviceaccount:kube-system:default"]
```

This configuration enables auditing at different levels for specific users.

#### Prevention

To prevent unauthorized access, follow these best practices:

1. **Least Privilege Principle**: Grant users the minimum permissions required to perform their tasks.
2. **Regular Audits**: Regularly review and audit RBAC configurations to ensure they are up-to-date and secure.
3. **Update Regularly**: Keep your Kubernetes cluster and dependencies up-to-date with the latest security patches.
4. **Use Strong Authentication**: Use strong authentication mechanisms such as multi-factor authentication (MFA).

#### Secure Coding Fixes

Here is an example of a vulnerable RBAC configuration and its secure counterpart:

**Vulnerable Configuration**

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

In this configuration, the `pod-reader` Role grants all verbs (`*`) on pods, which is overly permissive.

**Secure Configuration**

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

In this secure configuration, the `pod-reader` Role grants only the necessary verbs (`get`, `watch`, `list`) on pods.

### Hands-On Labs

To practice Kubernetes access management, you can use the following hands-on labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security.
- **OWASP WrongSecrets**: A series of challenges for learning about secrets management in Kubernetes.
- **kube-hunter**: A tool for hunting down security misconfigurations in Kubernetes clusters.

These labs provide practical experience in configuring and testing access management in Kubernetes.

### Conclusion

Kubernetes access management is a crucial aspect of securing your Kubernetes clusters. By properly configuring and testing access credentials, using RBAC, and following best practices, you can ensure that only authorized entities can interact with your cluster. Regular audits and updates are essential to maintaining a secure environment.

---
<!-- nav -->
[[04-Kubernetes Access Management Part 1|Kubernetes Access Management Part 1]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Review and Test Access/00-Overview|Overview]] | [[06-Kubernetes Access Management Part 3|Kubernetes Access Management Part 3]]
