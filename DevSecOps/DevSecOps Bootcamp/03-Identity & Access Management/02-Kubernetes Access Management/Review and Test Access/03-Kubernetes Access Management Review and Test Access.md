---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management: Review and Test Access

### Background Theory

Kubernetes is an open-source container orchestration platform designed to automate the deployment, scaling, and management of containerized applications. One of the critical aspects of managing a Kubernetes cluster is ensuring proper access control to prevent unauthorized access and potential security breaches. Access management in Kubernetes involves defining roles and permissions, and then assigning these roles to users or service accounts.

### Role-Based Access Control (RBAC)

Role-Based Access Control (RBAC) is a method of regulating access to resources based on the roles of individual users within an organization. In Kubernetes, RBAC allows administrators to define roles and role bindings that specify which actions a user or service account can perform on a resource.

#### Roles and Role Bindings

- **Roles**: Define a set of permissions that can be granted to a user or service account.
- **Role Bindings**: Associate roles with users or groups of users.

#### Example of a Role and Role Binding

```yaml
# Role definition
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]

# Role binding definition
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

### External Identity Providers

In many organizations, Kubernetes clusters are integrated with external identity providers such as AWS IAM (Identity and Access Management). This integration allows users to assume roles defined in the external provider and gain access to the Kubernetes cluster.

#### AWS STS Assume Role Command

The AWS Security Token Service (STS) `AssumeRole` API operation enables a user to assume a role in another account. This is useful for granting temporary access to resources in the target account.

##### Example of Assuming a Role Using AWS CLI

```bash
aws sts assume-role --role-arn arn:aws:iam::123456789012:role/KubernetesAdmin --role-session-name KubernetesSession
```

This command returns a JSON object containing temporary credentials:

```json
{
    "Credentials": {
        "AccessKeyId": "ASIAIOSFODNN7EXAMPLE",
        "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "SessionToken": "AQoDYXdzEPT//////////wEXAMPLETOKEN",
        "Expiration": "2023-10-10T12:34:56Z"
    },
    "AssumedRoleUser": {
        "Arn": "arn:aws:sts::123456789012:assumed-role/KubernetesAdmin/johndoe",
        "AssumedRoleId": "AROACLKVTMIEXAMPLE:johndoe"
    }
}
```

### Exporting Credentials

To use the assumed role credentials in your local environment, you need to export the `AccessKeyId`, `SecretAccessKey`, and `SessionToken` as environment variables.

```bash
export AWS_ACCESS_KEY_ID=ASIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
export AWS_SESSION_TOKEN=AQoDYXdzEPT//////////wEXAMPLETOKEN
```

### Connecting to the Cluster

Once the credentials are exported, you can use them to authenticate with the Kubernetes cluster. This typically involves configuring the `kubeconfig` file to use the assumed role credentials.

#### Example of Configuring `kubeconfig`

```yaml
apiVersion: v1
kind: Config
clusters:
- name: my-cluster
  cluster:
    server: https://my-cluster.example.com
users:
- name: kubernetes-admin
  user:
    exec:
      apiVersion: client.authentication.k8s.io/v1alpha1
      command: aws
      args:
      - sts
      - assume-role
      - --role-arn
      - arn:aws:iam::123456789012:role/KubernetesAdmin
      - --role-session-name
      - KubernetesSession
contexts:
- context:
    cluster: my-cluster
    user: kubernetes-admin
  name: my-context
current-context: my-context
```

### Real-World Examples

#### CVE-2021-25741: Kubernetes RBAC Misconfiguration

In 2021, a misconfiguration in Kubernetes RBAC led to unauthorized access to sensitive resources. This vulnerability was due to improper role definitions and role bindings, allowing attackers to escalate privileges and gain unauthorized access.

**Example of Vulnerable Role Definition**

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
```

**Secure Role Definition**

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

### How to Prevent / Defend

#### Detection

- **Audit Logs**: Enable audit logs in Kubernetes to monitor access attempts and detect unauthorized activities.
- **Security Scanners**: Use tools like `kube-bench` or `kubescape` to scan your cluster for misconfigurations and vulnerabilities.

#### Prevention

- **Least Privilege Principle**: Ensure that roles are defined with the minimum necessary permissions.
- **Regular Audits**: Conduct regular audits of role definitions and role bindings to ensure compliance with security policies.

#### Secure Coding Fixes

**Vulnerable Code**

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
```

**Fixed Code**

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

### Mermaid Diagrams

#### Role and Role Binding Architecture

```mermaid
graph TD
    A[User] --> B[Role Binding]
    B --> C[Role]
    C --> D[Permissions]
    D --> E[Resources]
```

#### Assume Role Flow

```mermaid
sequenceDiagram
    participant User
    participant AWSCLI
    participant STSService
    participant KubeConfig
    User->>AWSCLI: aws sts assume-role
    AWSCLI->>STSService: AssumeRoleRequest
    STSService-->>AWSCLI: AssumeRoleResponse
    AWSCLI-->>User: Export Credentials
    User->>KubeConfig: Configure kubeconfig
```

### Practice Labs

For hands-on practice with Kubernetes access management, consider the following labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security.
- **OWASP WrongSecrets**: A series of challenges to learn about secrets management in Kubernetes.
- **Pacu**: A framework for testing AWS security configurations, including Kubernetes access management.

By thoroughly understanding and implementing these concepts, you can ensure robust access management in your Kubernetes clusters, preventing unauthorized access and potential security breaches.

---
<!-- nav -->
[[02-Kubernetes Access Management Review and Test Access Part 1|Kubernetes Access Management Review and Test Access Part 1]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Review and Test Access/00-Overview|Overview]] | [[04-Kubernetes Access Management Part 1|Kubernetes Access Management Part 1]]
