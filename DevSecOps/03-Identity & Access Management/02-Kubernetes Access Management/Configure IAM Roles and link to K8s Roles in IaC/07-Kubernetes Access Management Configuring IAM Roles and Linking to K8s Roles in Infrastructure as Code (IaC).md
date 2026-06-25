---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management: Configuring IAM Roles and Linking to K8s Roles in Infrastructure as Code (IaC)

### Introduction to IAM Roles and Kubernetes Access Management

In the context of DevSecOps, managing access to Kubernetes clusters and associated resources is critical for maintaining security and compliance. One of the key mechanisms for achieving this is through the integration of Identity and Access Management (IAM) roles from cloud providers such as AWS with Kubernetes roles and permissions.

### Understanding IAM Roles in AWS

#### What is an IAM Role?

An IAM role is an entity within AWS that defines a set of permissions. Unlike IAM users, roles are not tied to specific individuals but are instead assumed by entities such as EC2 instances, Lambda functions, or even other AWS services. This allows for dynamic and flexible access control based on the context in which the role is being used.

#### Why Use IAM Roles?

Using IAM roles provides several benefits:
- **Least Privilege Principle**: You can grant only the necessary permissions required for a particular task, reducing the risk of unauthorized access.
- **Dynamic Access Control**: Roles can be assumed by different entities, allowing for fine-grained control over access based on the context.
- **Centralized Management**: IAM roles can be managed centrally, making it easier to update permissions across multiple services.

### Creating an IAM Role Using Terraform

To manage IAM roles in a consistent and reproducible manner, infrastructure as code (IaC) tools like Terraform are often used. Terraform allows you to define your infrastructure in code, making it easier to version control, test, and deploy changes.

#### Step-by-Step Guide to Creating an IAM Role in Terraform

1. **Define Variables**:
   Before creating the IAM role, you need to define variables that will be used to configure the role. These variables can be set in a `.tfvars` file.

   ```hcl
   variable "aws_user_arn" {
     description = "The ARN of the AWS user that will assume the admin role."
     type        = string
   }
   ```

2. **Create the IAM Role**:
   Use the `aws_iam_role` resource to create the IAM role. This resource requires a name and a description.

   ```hcl
   resource "aws_iam_role" "admin_role" {
     name = "admin-role"
     description = "Role for administrative access to AWS resources."

     assume_role_policy = jsonencode({
       Version = "2012-10-17"
       Statement = [
         {
           Effect = "Allow"
           Principal = {
             AWS = var.aws_user_arn
           }
           Action = "sts:AssumeRole"
         }
       ]
     })
   }
   ```

3. **Attach Policies to the IAM Role**:
   To define what actions the role can perform, you need to attach policies to it. These policies can be managed policies or inline policies.

   ```hcl
   resource "aws_iam_policy" "external_admin_policy" {
     name        = "external-admin-policy"
     description = "Policy for external admin access."

     policy = jsonencode({
       Version = "2012-10-17"
       Statement = [
         {
           Effect = "Allow"
           Action = "*"
           Resource = "*"
         }
       ]
     })
   }

   resource "aws_iam_role_policy_attachment" "attach_external_admin_policy" {
     role       = aws_iam_role.admin_role.name
     policy_arn = aws_iam_policy.external_admin_policy.arn
   }
   ```

### Linking IAM Roles to Kubernetes Roles

Once the IAM role is created, you need to link it to Kubernetes roles and permissions. This is typically done using a service account in Kubernetes that assumes the IAM role.

#### Service Account Configuration

1. **Create a Service Account**:
   Define a service account in Kubernetes that will assume the IAM role.

   ```yaml
   apiVersion: v1
   kind: ServiceAccount
   metadata:
     name: admin-service-account
     namespace: default
   ```

2. **Configure the Service Account to Assume the IAM Role**:
   Use annotations to specify the IAM role ARN that the service account should assume.

   ```yaml
   apiVersion: v1
   kind: ServiceAccount
   metadata:
     name: admin-service-account
     namespace: default
     annotations:
       eks.amazonaws.com/role-arn: ${var.aws_user_arn}
   ```

3. **Assign Kubernetes Roles to the Service Account**:
   Create a role binding that assigns Kubernetes roles to the service account.

   ```yaml
   apiVersion: rbac.authorization.k8s.io/v1
   kind: RoleBinding
   metadata:
     name: admin-role-binding
     namespace: default
   subjects:
   - kind: ServiceAccount
     name: admin-service-account
     namespace: default
   roleRef:
     kind: ClusterRole
     name: cluster-admin
     apiGroup: rbac.authorization.k8s.io
   ```

### Example: Full Terraform and Kubernetes Configuration

Here is a complete example of the Terraform and Kubernetes configurations:

```hcl
# main.tf
variable "aws_user_arn" {
  description = "The ARN of the AWS user that will assume the admin role."
  type        = string
}

resource "aws_iam_role" "admin_role" {
  name = "admin-role"
  description = "Role for administrative access to AWS resources."

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = var.aws_user_arn
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_policy" "external_admin_policy" {
  name        = "external-admin-policy"
  description = "Policy for external admin access."

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = "*"
        Resource = "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "attach_external_admin_policy" {
  role       = aws_iam_role.admin_role.name
  policy_arn = aws_iam_policy.external_admin_policy.arn
}
```

```yaml
# kubernetes.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: admin-service-account
  namespace: default
  annotations:
    eks.amazonaws.com/role-arn: ${var.aws_user_arn}

---
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: admin-role-binding
  namespace: default
subjects:
- kind: ServiceAccount
  name: admin-service-account
  namespace: default
roleRef:
  kind: ClusterRole
  name: cluster-admin
  apiGroup: rbac.authorization.k8s.io
```

### Real-World Examples and Recent Breaches

Recent breaches involving misconfigured IAM roles and Kubernetes access management include:

- **CVE-2021-20225**: A vulnerability in Amazon EKS allowed unauthorized access to Kubernetes clusters due to misconfigured IAM roles.
- **AWS S3 Bucket Exposure**: In 2021, multiple companies exposed sensitive data due to misconfigured IAM roles granting excessive permissions to S3 buckets.

### How to Prevent / Defend

#### Detection

- **Regular Audits**: Conduct regular audits of IAM roles and permissions to ensure they comply with least privilege principles.
- **Monitoring Tools**: Use monitoring tools like AWS CloudTrail and Kubernetes audit logs to track access and detect anomalies.

#### Prevention

- **Least Privilege**: Always assign the minimum necessary permissions to IAM roles and Kubernetes roles.
- **IAM Policies**: Use managed policies and inline policies to restrict access to specific resources and actions.
- **Service Account Annotations**: Ensure that service accounts are properly annotated with the correct IAM role ARNs.

#### Secure Coding Fixes

**Vulnerable Code**:
```hcl
resource "aws_iam_role" "admin_role" {
  name = "admin-role"
  description = "Role for administrative access to AWS resources."

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = "*"
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}
```

**Secure Code**:
```hcl
resource "aws_iam_role" "admin_role" {
  name = "admin-role"
  description = "Role for administrative access to AWS resources."

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = var.aws_user_arn
        }
        Action = "sts:AssumeRole"
      }
    ]
  })
}
```

### Conclusion

Properly configuring IAM roles and linking them to Kubernetes roles is essential for maintaining security and compliance in a DevSecOps environment. By following the steps outlined above and adhering to best practices, you can ensure that your infrastructure is secure and resilient against potential threats.

### Practice Labs

For hands-on practice with Kubernetes access management and IAM roles, consider the following labs:
- **Kubernetes Goat**: A Kubernetes-based security training platform.
- **OWASP WrongSecrets**: A series of challenges focused on Kubernetes security.
- **kube-hunter**: A tool for hunting vulnerabilities in Kubernetes clusters.

These labs provide practical experience in configuring and securing IAM roles and Kubernetes access management.

---
<!-- nav -->
[[06-Kubernetes Access Management Configuring IAM Roles and Linking to K8s Roles in Infrastructure as Code (IaC) Part 1|Kubernetes Access Management Configuring IAM Roles and Linking to K8s Roles in Infrastructure as Code (IaC) Part 1]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure IAM Roles and link to K8s Roles in IaC/00-Overview|Overview]] | [[08-Kubernetes Access Management Configuring IAM Roles and Linking to Kubernetes Roles in Infrastructure as Code (IaC)|Kubernetes Access Management Configuring IAM Roles and Linking to Kubernetes Roles in Infrastructure as Code (IaC)]]
