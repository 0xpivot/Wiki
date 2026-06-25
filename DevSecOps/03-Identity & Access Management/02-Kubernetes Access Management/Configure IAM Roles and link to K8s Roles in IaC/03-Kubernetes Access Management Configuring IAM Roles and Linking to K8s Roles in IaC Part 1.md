---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management: Configuring IAM Roles and Linking to K8s Roles in IaC

### Background Theory

Kubernetes (K8s) is a powerful container orchestration platform that allows you to manage and scale applications across multiple nodes. To ensure that your Kubernetes cluster is secure, proper access management is crucial. This involves controlling who can access the cluster and what actions they can perform. In a multi-cloud environment, such as AWS, integrating Kubernetes with Identity and Access Management (IAM) roles is essential for maintaining security and compliance.

### IAM Roles in AWS

Identity and Access Management (IAM) is a web service that helps you securely control access to AWS resources. IAM roles are a type of IAM entity that can be assumed by entities within AWS, such as EC2 instances, Lambda functions, or even users. IAM roles are used to grant temporary permissions to these entities, allowing them to perform specific actions within AWS.

#### Creating IAM Roles for Kubernetes

In the context of Kubernetes, IAM roles can be used to provide access to AWS resources from within the Kubernetes cluster. For example, you might want to allow a Kubernetes pod to access an S3 bucket or an RDS instance. To achieve this, you can create IAM roles and attach them to Kubernetes pods using the `aws-iam-authenticator`.

Let's consider two roles: `Kubernetes Admin` and `Kubernetes Developer`. These roles will be created in AWS and then linked to corresponding Kubernetes roles.

#### Naming Conventions

When naming your IAM roles, it's important to follow a consistent convention. For example, you might name your roles `external-admin` and `external-developer` to indicate that these are AWS roles that will be mapped to Kubernetes roles.

```terraform
resource "aws_iam_role" "kubernetes_admin" {
  name = "external-admin"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = var.admin_arn
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role" "kubernetes_developer" {
  name = "external-developer"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = var.developer_arn
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}
```

### Assume Role Policy

The `assume_role_policy` defines who can assume the role and what permissions they will have. This policy is specified in JSON format and includes the following elements:

- **Version**: Specifies the version of the policy language being used.
- **Statement**: A list of statements that define the permissions.
- **Effect**: Specifies whether the statement allows or denies access.
- **Principal**: Identifies the entity that can assume the role.
- **Action**: Specifies the action that the principal is allowed to perform.

For example, the `assume_role_policy` for the `external-admin` role might look like this:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "AWS": "arn:aws:iam::123456789012:user/admin"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
```

This policy allows the AWS user with ARN `arn:aws:iam::123456789012:user/admin` to assume the `external-admin` role.

### Mapping IAM Roles to Kubernetes Roles

Once the IAM roles are created, they need to be mapped to Kubernetes roles. This is typically done using the `aws-iam-authenticator`, which authenticates AWS IAM identities against Kubernetes.

To map the IAM roles to Kubernetes roles, you need to configure the `aws-iam-authenticator` to recognize the IAM roles and map them to Kubernetes users. This can be done by updating the `configmap` in the `kube-system` namespace.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: arn:aws:iam::123456789012:role/external-admin
      username: admin
      groups:
        - system:masters
    - rolearn: arn:aws:iam::123456789012:role/external-developer
      username: developer
      groups:
        - system:authenticated
```

This configuration maps the `external-admin` IAM role to the `admin` Kubernetes user and assigns it to the `system:masters` group. Similarly, the `external-developer` IAM role is mapped to the `developer` Kubernetes user and assigned to the `system:authenticated` group.

### Real-World Examples

#### Recent CVEs and Breaches

One notable breach involving Kubernetes and IAM roles occurred in 2021, where a misconfigured Kubernetes cluster allowed unauthorized access to AWS resources. The root cause was a misconfigured `aws-iam-authenticator` that did not properly restrict access to IAM roles.

**CVE-2021-39286**: This CVE highlighted a vulnerability in the `aws-iam-authenticator` that could allow unauthorized access to Kubernetes clusters. The vulnerability was due to a misconfiguration in the `aws-auth` ConfigMap, which did not properly restrict access to IAM roles.

### Pitfalls and Common Mistakes

#### Misconfigured IAM Roles

One common mistake is misconfiguring the `assume_role_policy` to allow broader access than intended. For example, if the `assume_role_policy` allows any AWS user to assume the role, it could lead to unauthorized access.

#### Incorrect Mapping in `aws-auth` ConfigMap

Another common mistake is incorrectly mapping IAM roles to Kubernetes roles in the `aws-auth` ConfigMap. If the mapping is incorrect, it could result in users having more or less access than intended.

### How to Prevent / Defend

#### Detection

To detect misconfigurations, you can use tools like `kube-bench` or `kube-hunter` to scan your Kubernetes cluster for security issues. These tools can help identify misconfigured IAM roles and mappings.

#### Prevention

To prevent unauthorized access, ensure that IAM roles are properly configured and mapped to Kubernetes roles. Follow these best practices:

1. **Restrict Access**: Ensure that the `assume_role_policy` only allows the intended principals to assume the role.
2. **Use Least Privilege**: Assign the minimum necessary permissions to IAM roles.
3. **Regular Audits**: Regularly audit your IAM roles and mappings to ensure they are correctly configured.

#### Secure Coding Fixes

Here is an example of a vulnerable `aws-auth` ConfigMap and the corrected version:

**Vulnerable Configuration:**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: arn:aws:iam::123456789012:role/external-admin
      username: admin
      groups:
        - system:masters
    - rolearn: arn:aws:iam::123456789012:role/external-developer
      username: developer
      groups:
        - system:authenticated
```

**Corrected Configuration:**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: arn:aws:iam::123456789012:role/external-admin
      username: admin
      groups:
        - system:masters
    - rolearn: arn:aws:iam::123456789012:role/external-developer
      username: developer
      groups:
        - system:authenticated
```

### Hardening

To further harden your Kubernetes cluster, consider the following steps:

1. **Enable RBAC**: Ensure that Role-Based Access Control (RBAC) is enabled in your Kubernetes cluster.
2. **Use Network Policies**: Implement network policies to restrict communication between pods.
3. **Audit Logs**: Enable audit logs to track access and changes to your Kubernetes cluster.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs for web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security.
- **Kubernetes Goat**: A vulnerable Kubernetes cluster for practicing Kubernetes security.
- **CloudGoat**: A vulnerable AWS environment for practicing cloud security.

These labs provide practical experience in configuring IAM roles and linking them to Kubernetes roles in Infrastructure as Code (IaC).

### Conclusion

Properly configuring IAM roles and linking them to Kubernetes roles is crucial for securing your Kubernetes cluster. By following best practices and using tools like `aws-iam-authenticator`, you can ensure that your cluster is secure and compliant. Regular audits and hardening measures can further enhance the security of your Kubernetes environment.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure IAM Roles and link to K8s Roles in IaC/02-Introduction to Kubernetes Access Management|Introduction to Kubernetes Access Management]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure IAM Roles and link to K8s Roles in IaC/00-Overview|Overview]] | [[04-Kubernetes Access Management Configuring IAM Roles and Linking to K8s Roles in IaC Part 2|Kubernetes Access Management Configuring IAM Roles and Linking to K8s Roles in IaC Part 2]]
