---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management

### Background Theory

Kubernetes is a powerful orchestration platform used to manage containerized applications. One of the critical aspects of managing a Kubernetes cluster is ensuring proper access control. Access management in Kubernetes involves defining roles, permissions, and policies to restrict who can perform specific actions within the cluster. This ensures that the cluster remains secure and that only authorized personnel can make changes.

### Current User Configuration

In the context of the provided transcript, the current user is configured to have administrative access to the Kubernetes cluster. This user was set up during the execution of a Terraform `apply` command, which automatically granted them Kubernetes admin privileges. This is a common scenario in many organizations where the initial setup grants broad access to ensure the cluster can be properly configured and managed.

#### Why This Matters

Granting broad administrative access to a user can pose significant security risks. If this user's credentials are compromised, an attacker could gain full control over the Kubernetes cluster, potentially leading to data breaches, service disruptions, or other malicious activities.

#### How It Works Under the Hood

When Terraform applies the configuration, it typically uses an AWS IAM user with sufficient permissions to create and manage resources in the AWS environment. In this case, the IAM user is also given Kubernetes admin privileges. This means that the user can perform any action within the Kubernetes cluster, including creating, modifying, and deleting resources.

### Security Best Practices

As a security best practice, it is recommended to avoid granting human users direct administrative access to the Kubernetes cluster. Instead, access should be managed through roles and permissions that are tightly controlled and audited.

#### Real-World Example

A recent breach involving Kubernetes misconfiguration was the **CVE-2021-20225**. In this case, a misconfigured Kubernetes API server allowed unauthorized access to sensitive resources. This highlights the importance of proper access management and the risks associated with overly permissive configurations.

### Improving Access Control

To improve access control, the organization plans to implement a release pipeline for the infrastructure code. This pipeline will execute the Terraform `apply` command using a role rather than a human user. This approach ensures that the administrative actions are performed by a non-human entity, reducing the risk of credential compromise.

#### Implementation Details

The following steps outline how to set up a release pipeline using GitLab:

1. **Define the Pipeline**: Create a `.gitlab-ci.yml` file to define the pipeline stages.
2. **Use IAM Roles**: Configure the pipeline to assume an IAM role with the necessary permissions to execute Terraform commands.
3. **Secure Credentials**: Ensure that the pipeline does not store or expose sensitive credentials.

```yaml
stages:
  - deploy

deploy:
  stage: deploy
  script:
    - aws sts assume-role --role-arn arn:aws:iam::123456789012:role/TerraformDeployRole --role-session-name TerraformSession
    - terraform init
    - terraform apply -auto-approve
```

### Adjusting Configuration

The current configuration can be adjusted to ensure that the correct region is specified. This can be done by referencing the region variable directly in the configuration.

```bash
export AWS_DEFAULT_REGION=us-west-2
```

Alternatively, you can set the region using the `AWS configure` command:

```bash
aws configure set region us-west-2
```

### Executing Commands

To execute the commands, you need to ensure that the AWS credentials are correctly configured. This can be done by setting the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` environment variables.

```bash
export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
export AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

### Mermaid Diagrams

#### Access Flow Diagram

```mermaid
sequenceDiagram
  participant User as U
  participant Terraform as T
  participant IAM as I
  participant Kubernetes as K

  U->>T: Execute Terraform Apply
  T->>I: Assume IAM Role
  I->>K: Grant Admin Access
  K-->>U: Confirm Access
```

### Pitfalls and Common Mistakes

One common mistake is granting broad administrative access to human users. This increases the risk of credential compromise and unauthorized access. Another pitfall is not properly configuring the IAM roles and permissions, leading to overly permissive access.

### How to Prevent / Defend

#### Detection

To detect unauthorized access, you can enable and monitor Kubernetes audit logs. These logs capture all API requests and can be used to identify suspicious activity.

```bash
kubectl get events --all-namespaces
```

#### Prevention

To prevent unauthorized access, follow these steps:

1. **Use IAM Roles**: Ensure that administrative actions are performed by IAM roles rather than human users.
2. **Least Privilege Principle**: Grant the minimum necessary permissions to perform required tasks.
3. **Regular Audits**: Regularly review and audit access controls to ensure compliance.

#### Secure Coding Fixes

Here is an example of a vulnerable configuration and the corresponding secure configuration:

**Vulnerable Configuration**

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
  name: cluster-admin
  apiGroup: rbac.authorization.k8s.io
```

**Secure Configuration**

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: ClusterRoleBinding
metadata:
  name: restricted-binding
subjects:
- kind: Group
  name: devops-team
roleRef:
  kind: ClusterRole
  name: restricted-cluster-role
  apiGroup: rbac.authorization.k8s.io
```

### Hands-On Labs

For hands-on practice with Kubernetes access management, consider the following labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security.
- **OWASP WrongSecrets**: A series of challenges to learn about secrets management in Kubernetes.
- **kube-hunter**: A tool for identifying security issues in Kubernetes clusters.

These labs provide practical experience in configuring and securing Kubernetes access controls.

### Conclusion

Proper access management in Kubernetes is crucial for maintaining the security and integrity of the cluster. By following best practices, such as using IAM roles and adhering to the least privilege principle, you can significantly reduce the risk of unauthorized access and potential breaches. Regular audits and monitoring are essential to ensure that access controls remain effective and compliant.

---
<!-- nav -->
[[03-Kubernetes Access Management Review and Test Access|Kubernetes Access Management Review and Test Access]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Review and Test Access/00-Overview|Overview]] | [[05-Kubernetes Access Management Part 2|Kubernetes Access Management Part 2]]
