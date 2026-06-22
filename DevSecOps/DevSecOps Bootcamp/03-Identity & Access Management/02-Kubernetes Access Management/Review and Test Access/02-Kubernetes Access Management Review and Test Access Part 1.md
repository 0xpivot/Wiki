---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management: Review and Test Access

### Background Theory

Kubernetes is a powerful container orchestration platform that allows you to manage and scale applications across clusters of nodes. One of the critical aspects of managing a Kubernetes cluster is ensuring proper access control and authentication. This involves defining roles, permissions, and policies to ensure that only authorized users and services can interact with the cluster.

Access management in Kubernetes is primarily handled through Role-Based Access Control (RBAC). RBAC allows you to define roles and bind them to users or service accounts. Each role can have a set of permissions defined, such as read, write, or execute access to specific resources within the cluster.

### Key Concepts

#### Roles and Role Bindings

- **Role**: A role is a collection of permissions that define what actions can be performed on specific resources within the cluster. For example, a role might allow a user to read pods but not modify them.
- **Role Binding**: A role binding associates a role with a user or service account. This binding specifies which subjects (users or service accounts) are granted the permissions defined in the role.

#### Service Accounts

Service accounts are used to authenticate and authorize processes running inside pods. They provide a way to grant permissions to applications running in the cluster, allowing them to interact with the Kubernetes API.

### Example: Assumed Role Identity

Let's dive into an example of assuming a role identity in Kubernetes. This process involves using the `sts` (Security Token Service) to assume a role and retrieve temporary credentials.

```mermaid
sequenceDiagram
    participant User
    participant STS
    participant Kubernetes
    User->>STS: AssumeRole
    STS-->>User: Credentials (AccessKeyID, SecretAccessKey, SessionToken)
    User->>Kubernetes: Set Environment Variables
    Kubernetes-->>User: GetCallerIdentity
```

In this sequence, the user sends an `AssumeRole` request to the STS, which returns temporary credentials. These credentials are then used to set environment variables in the terminal, allowing the user to interact with the Kubernetes cluster.

### Detailed Steps

1. **Assume Role Command**:
   The `AssumeRole` command is used to assume a role and retrieve temporary credentials. Here’s an example of how this might look:

   ```bash
   aws sts assume-role --role-arn arn:aws:iam::123456789012:role/ExternalAdmin --role-session-name MySession
   ```

   This command assumes the role specified by the ARN (`arn:aws:iam::123456789012:role/ExternalAdmin`) and returns temporary credentials.

2. **Extracting Credentials**:
   The response from the `AssumeRole` command includes the `Credentials` object, which contains the `AccessKeyId`, `SecretAccessKey`, and `SessionToken`.

   ```json
   {
       "Credentials": {
           "AccessKeyId": "ASIAIOSFODNN7EXAMPLE",
           "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
           "SessionToken": "AQoDYXdzEJr...example...token"
       }
   }
   ```

3. **Setting Environment Variables**:
   To use these credentials in the terminal, you need to set them as environment variables. This can be done using the `export` command in a shell script.

   ```bash
   export AWS_ACCESS_KEY_ID=ASIAIOSFODNN7EXAMPLE
   export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
   export AWS_SESSION_TOKEN=AQoDYXdzEJr...example...token
   ```

4. **Using JQ for Parsing JSON**:
   The `jq` tool is often used to parse JSON output from commands like `AssumeRole`. If `jq` is not installed, you can install it using package managers like `apt` or `brew`.

   ```bash
   sudo apt-get install jq
   ```

   Once installed, you can use `jq` to extract the necessary fields from the JSON response.

   ```bash
   aws sts assume-role --role-arn arn:aws:iam::123456789012:role/ExternalAdmin --role-session-name MySession | jq -r '.Credentials.AccessKeyId'
   ```

5. **Executing Commands**:
   After setting the environment variables, you can execute commands that require these credentials. For example, you can use the `kubectl` command to interact with the Kubernetes cluster.

   ```bash
   kubectl get pods
   ```

### Common Pitfalls

- **Incorrect Role Name**: Ensure that the role name is correctly specified. In the example, the role name was initially specified incorrectly with an underscore instead of a hyphen.

- **Missing Dependencies**: Make sure that all required tools, such as `jq`, are installed and available in your environment.

### Real-World Examples

#### Recent Breaches

One notable breach involving Kubernetes access management occurred in 2021, where a misconfigured Kubernetes cluster allowed unauthorized access to sensitive data. The root cause was a misconfigured role binding that granted excessive permissions to a service account.

#### CVEs

CVE-2021-25741: This vulnerability involved a misconfiguration in Kubernetes RBAC that allowed unauthorized access to sensitive resources. The issue was resolved by tightening role bindings and ensuring that only necessary permissions were granted.

### How to Prevent / Defend

#### Detection

- **Audit Logs**: Enable audit logging in Kubernetes to track access attempts and identify unauthorized activities.
- **Monitoring Tools**: Use monitoring tools like Prometheus and Grafana to visualize and analyze access patterns.

#### Prevention

- **Least Privilege Principle**: Always follow the principle of least privilege. Grant only the minimum permissions necessary for a role or service account.
- **Regular Audits**: Conduct regular audits of role bindings and permissions to ensure that they remain appropriate and up-to-date.

#### Secure Coding Fixes

Here’s an example of a vulnerable role binding and its corrected version:

**Vulnerable Role Binding**:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: admin-binding
subjects:
- kind: User
  name: admin-user
roleRef:
  kind: ClusterRole
  name: cluster-admin
  apiGroup: rbac.authorization.k8s.io
```

**Corrected Role Binding**:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: restricted-binding
subjects:
- kind: User
  name: restricted-user
roleRef:
  kind: Role
  name: restricted-role
  apiGroup: rbac.authorization.k8s.io
```

In the corrected version, a more restricted role is used, limiting the permissions granted to the user.

### Complete Example

#### Full HTTP Request and Response

Here’s a complete example of an HTTP request and response for assuming a role:

**Request**:
```http
POST /sts/assumeRole HTTP/1.1
Host: sts.amazonaws.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 123

Action=AssumeRole&Version=2011-06-15&RoleArn=arn:aws:iam::123456789012:role/ExternalAdmin&RoleSessionName=MySession
```

**Response**:
```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 345

{
    "Credentials": {
        "AccessKeyId": "ASIAIOSFODNN7EXAMPLE",
        "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        "SessionToken": "AQoDYXdzEJr...example...token"
    }
}
```

#### Policy Configuration

Here’s an example of a Kubernetes RBAC policy configuration:

**IAM Policy JSON**:
```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
                "sts:AssumeRole"
            ],
            "Resource": [
                "arn:aws:iam::123456789012:role/ExternalAdmin"
            ]
        }
    ]
}
```

**Kubernetes Role Binding YAML**:
```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: external-admin-binding
subjects:
- kind: User
  name: external-admin-user
roleRef:
  kind: Role
  name: external-admin-role
  apiGroup: rbac.authorization.k8s.io
```

### Practice Labs

For hands-on practice with Kubernetes access management, consider the following labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security.
- **OWASP WrongSecrets**: A series of challenges focused on Kubernetes security.
- **kube-hunter**: A tool for hunting vulnerabilities in Kubernetes clusters.

These labs provide practical experience in configuring and testing access management in Kubernetes environments.

By thoroughly understanding and implementing these concepts, you can ensure robust access management in your Kubernetes clusters, protecting against unauthorized access and potential breaches.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Review and Test Access/01-Introduction to Kubernetes Access Management|Introduction to Kubernetes Access Management]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Review and Test Access/00-Overview|Overview]] | [[03-Kubernetes Access Management Review and Test Access|Kubernetes Access Management Review and Test Access]]
