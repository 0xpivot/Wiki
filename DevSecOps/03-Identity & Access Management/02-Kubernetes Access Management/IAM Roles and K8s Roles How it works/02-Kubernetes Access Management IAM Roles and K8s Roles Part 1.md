---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management: IAM Roles and K8s Roles

### Introduction to Access Management in Kubernetes

Access management in Kubernetes is crucial for ensuring that only authorized entities can interact with the cluster. This includes both human users and automated processes such as continuous integration/continuous deployment (CI/CD) pipelines. The primary mechanisms for managing access in Kubernetes are Identity and Access Management (IAM) roles and Kubernetes roles.

### IAM Roles in AWS

IAM roles in AWS are a fundamental component of securing access to resources within an Amazon Elastic Kubernetes Service (EKS) cluster. An IAM role is an AWS identity that you can use to delegate permissions to entities that need to access your AWS resources. These roles are temporary and provide short-lived credentials, enhancing security by reducing the risk associated with long-lived credentials.

#### What is an IAM Role?

An IAM role is an AWS identity that you can use to delegate permissions to entities that need to access your AWS resources. Unlike IAM users, roles do not have their own permanent credentials. Instead, they provide temporary credentials that are valid for a limited time.

#### Why Use IAM Roles?

Using IAM roles is a best practice for several reasons:

1. **Least Privilege Principle**: IAM roles allow you to grant the minimum set of permissions necessary for a task, adhering to the principle of least privilege.
2. **Temporary Credentials**: IAM roles provide temporary credentials that expire after a short period, reducing the risk of credential exposure.
3. **Centralized Management**: IAM roles can be managed centrally, making it easier to update permissions across multiple entities.

#### How IAM Roles Work

When a user or service assumes an IAM role, they receive temporary security credentials that include an access key ID, a secret access key, and a security token. These credentials are valid for a limited time, typically 1 hour, and can be used to make API calls to AWS services.

```mermaid
sequenceDiagram
    participant User
    participant IAM
    participant EKS
    User->>IAM: Request to assume role
    IAM-->>User: Temporary credentials
    User->>EKS: Perform actions using temporary credentials
```

### Kubernetes Roles and RoleBindings

Kubernetes roles and role bindings are used to manage access within the Kubernetes cluster itself. A role defines a set of permissions, while a role binding associates a role with one or more subjects (users, groups, or service accounts).

#### What is a Kubernetes Role?

A Kubernetes role is a resource that defines a set of permissions for accessing Kubernetes resources. Roles are defined within a namespace and can be bound to specific subjects.

#### Why Use Kubernetes Roles?

Using Kubernetes roles allows you to define fine-grained access control policies within the cluster. This ensures that only authorized entities can perform specific actions, such as creating pods, deploying applications, or managing secrets.

#### How Kubernetes Roles Work

Roles are defined using YAML files and are applied to the cluster using `kubectl apply`. Once a role is defined, it can be bound to subjects using a role binding.

```yaml
# Example Role Definition
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

```yaml
# Example RoleBinding Definition
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

### Combining IAM Roles and Kubernetes Roles

To achieve comprehensive access management in an EKS cluster, you need to combine IAM roles and Kubernetes roles. IAM roles provide access to AWS resources, while Kubernetes roles provide access to Kubernetes resources.

#### Example Workflow

1. **Assume IAM Role**: A user or service assumes an IAM role to obtain temporary credentials.
2. **Use Temporary Credentials**: The temporary credentials are used to authenticate with the EKS cluster.
3. **Apply Kubernetes Role Binding**: The user or service is bound to a Kubernetes role within the cluster.

```mermaid
sequenceDiagram
    participant User
    participant IAM
    participant EKS
    participant KubernetesRole
    User->>IAM: Assume IAM role
    IAM-->>User: Temporary credentials
    User->>EKS: Authenticate with EKS using temporary credentials
    EKS-->>KubernetesRole: Apply Kubernetes role binding
```

### Real-World Examples and Recent Breaches

Recent breaches and vulnerabilities highlight the importance of proper access management in Kubernetes clusters. For example, the 2021 SolarWinds breach involved unauthorized access to Kubernetes clusters, leading to significant data exfiltration.

#### CVE-2021-25282: Kubernetes RBAC Misconfiguration

CVE-2021-25282 describes a misconfiguration in Kubernetes Role-Based Access Control (RBAC) that could allow unauthorized access to sensitive resources. This vulnerability underscores the need for strict RBAC policies and regular audits.

### Common Pitfalls and Best Practices

#### Common Pitfalls

1. **Overly Permissive Roles**: Avoid creating roles with overly broad permissions. Stick to the principle of least privilege.
2. **Static Credentials**: Avoid using static credentials for long periods. Use temporary credentials provided by IAM roles.
3. **Manual Role Management**: Manual management of roles and role bindings can lead to errors. Automate the process where possible.

#### Best Practices

1. **Least Privilege Principle**: Grant the minimum set of permissions necessary for a task.
2. **Temporary Credentials**: Use temporary credentials provided by IAM roles.
3. **Automated Role Management**: Use tools like Terraform or Ansible to automate the creation and management of roles and role bindings.

### How to Prevent / Defend

#### Detection

Regularly audit your IAM roles and Kubernetes roles to ensure that they are configured correctly. Use tools like AWS CloudTrail and Kubernetes audit logs to monitor access patterns.

#### Prevention

1. **Strict RBAC Policies**: Implement strict RBAC policies to limit access to sensitive resources.
2. **Automated Role Management**: Use automation tools to manage roles and role bindings.
3. **Regular Audits**: Conduct regular audits to identify and remediate misconfigurations.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of a role definition and role binding.

**Vulnerable Version**

```yaml
# Vulnerable Role Definition
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: default
  name: admin-role
rules:
- apiGroups: ["*"]
  resources: ["*"]
  verbs: ["*"]
```

**Secure Version**

```yaml
# Secure Role Definition
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

### Complete Example: Full HTTP Request and Response

#### Full HTTP Request

```http
POST /sts/assumeRole HTTP/1.1
Host: sts.amazonaws.com
Content-Type: application/x-www-form-urlencoded
X-Amz-Target: AWSSecurityTokenService.AssumeRole
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20170320/us-east-1/sts/aws4_request, SignedHeaders=host;x-amz-date, Signature=fe5f4faa6b6aca6ccdaec9cb8884befc9bc92a4f114b9cde63986f0e72e9e4b2
X-Amz-Date: 20170320T193642Z
Content-Length: 117

Action=AssumeRole&Version=2011-06-15&RoleArn=arn:aws:iam::123456789012:role/example-role&RoleSessionName=ExampleSession
```

#### Full HTTP Response

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 1024
Date: Mon, 20 Mar 2017 19:36:42 GMT

{
  "AssumeRoleResponse": {
    "AssumeRoleResult": {
      "Credentials": {
        "AccessKeyId": "ASIAIOSFODNN7EXAMPLE",
        "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "SessionToken": "AQoDYXdzEJr... (truncated)",
        "Expiration": "2017-03-20T20:36:42Z"
      },
      "AssumedRoleUser": {
        "Arn": "arn:aws:sts::123456789012:assumed-role/example-role/ExampleSession",
        "AssumedRoleId": "AROAIOSFODNN7EXAMPLE:ExampleSession"
      }
    }
  }
}
```

### Hands-On Labs

For hands-on practice with Kubernetes access management, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises on securing Kubernetes clusters.
- **OWASP Juice Shop**: Provides a vulnerable web application that can be deployed in a Kubernetes cluster.
- **Kubernetes Goat**: A security-focused Kubernetes environment designed for learning and testing.

These labs provide practical experience in setting up and securing Kubernetes clusters, including the use of IAM roles and Kubernetes roles.

### Conclusion

Proper access management in Kubernetes is essential for maintaining the security and integrity of your cluster. By combining IAM roles and Kubernetes roles, you can ensure that only authorized entities can access your resources. Regular audits and strict RBAC policies are key to preventing unauthorized access and mitigating risks.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/IAM Roles and K8s Roles How it works/02-Overview of Kubernetes Access Management|Overview of Kubernetes Access Management]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/IAM Roles and K8s Roles How it works/00-Overview|Overview]] | [[04-Kubernetes Access Management IAM Roles and K8s Roles|Kubernetes Access Management IAM Roles and K8s Roles]]
