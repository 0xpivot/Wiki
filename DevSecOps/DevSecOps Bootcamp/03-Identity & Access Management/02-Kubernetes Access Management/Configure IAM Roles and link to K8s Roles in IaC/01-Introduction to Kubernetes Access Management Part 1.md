---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Introduction to Kubernetes Access Management

Kubernetes access management is a critical aspect of securing your Kubernetes clusters. It ensures that only authorized users and services can interact with the cluster resources, thereby reducing the risk of unauthorized access and potential security breaches. In this chapter, we will delve into the configuration of IAM roles and their linkage to Kubernetes roles within Infrastructure as Code (IaC) using AWS Elastic Kubernetes Service (EKS).

### Background Theory

Before diving into the specifics, let's understand the fundamental concepts involved:

- **IAM Roles**: Identity and Access Management (IAM) roles are used to grant permissions to entities within AWS. These roles can be assumed by users, services, or instances to perform specific actions within the AWS environment.
  
- **Kubernetes Roles**: In Kubernetes, roles are used to define sets of permissions for accessing resources within the cluster. These roles can be bound to users or groups to control access.

- **EKS Configuration**: EKS (Elastic Kubernetes Service) is a managed Kubernetes service provided by AWS. It simplifies the deployment, scaling, and operations of Kubernetes clusters in the cloud.

### Separation of Duties

In a typical setup, you might have different roles for managing the EKS cluster itself and managing the Kubernetes resources within the cluster. This separation is crucial for maintaining security and compliance.

#### EKS Cluster Admin vs. Kubernetes Admin

- **EKS Cluster Admin**: This role is responsible for managing the EKS cluster itself, including tasks such as adding node groups, updating the EKS version, configuring networking, and installing add-ons.
  
- **Kubernetes Admin**: This role is responsible for managing the Kubernetes resources within the cluster, such as deploying applications, managing pods, and configuring services.

### Configuring IAM Roles

To ensure proper access control, IAM roles need to be configured for both external administrators and developers. These roles can be defined in AWS IAM and then mapped to Kubernetes roles within the EKS cluster.

#### Creating IAM Roles

Let's create an IAM role for an administrator and a developer. We'll use the AWS Management Console for this example.

```bash
# Create an IAM role for an administrator
aws iam create-role --role-name EKSAdminRole --assume-role-policy-document file://trust-policy.json

# Attach policies to the role
aws iam attach-role-policy --role-name EKSAdminRole --policy-arn arn:aws:iam::aws:policy/AdministratorAccess

# Create an IAM role for a developer
aws iam create-role --role-name EKSDevRole --assume-role-policy-document file://trust-policy.json

# Attach policies to the role
aws iam attach-role-policy --role-name EKSDevRole --policy-arn arn:aws:iam::aws:policy/AmazonEKSClusterPolicy
```

Here, `trust-policy.json` is a JSON file defining the trust relationship for the role. An example of `trust-policy.json` is:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {
                "Service": "ec2.amazonaws.com"
            },
            "Action": "sts:AssumeRole"
        }
    ]
}
```

### Mapping IAM Roles to Kubernetes Roles

Once the IAM roles are created, they need to be mapped to Kubernetes roles within the EKS cluster. This mapping is done using the `aws-auth` ConfigMap in the `kube-system` namespace.

#### Configuring the aws-auth ConfigMap

The `aws-auth` ConfigMap is used to map IAM roles to Kubernetes RBAC roles. Here’s an example of how to configure it using Terraform:

```hcl
resource "kubernetes_config_map" "aws_auth" {
  metadata {
    name      = "aws-auth"
    namespace = "kube-system"
  }

  data = <<EOF
mapRoles: |
  - rolearn: ${var.admin_role_arn}
    username: system:node:{{EC2PrivateDNSName}}
    groups:
      - system:masters
  - rolearn: ${var.dev_role_arn}
    username: system:node:{{EC2PrivateDNSName}}
    groups:
      - system:devs
EOF
}
```

In this example, `admin_role_arn` and `dev_role_arn` are variables representing the ARNs of the IAM roles created earlier.

### Linking IAM Roles to Kubernetes Roles

To establish the link between IAM roles and Kubernetes roles, we need to define the mappings in the `aws-auth` ConfigMap. Each mapping consists of three key attributes:

1. **RoleARN**: The Amazon Resource Name (ARN) of the IAM role.
2. **Username**: A unique identifier for the user or group.
3. **Groups**: The Kubernetes groups to which the user or group belongs.

#### Example Mapping

Here’s an example of a mapping for an administrator:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: arn:aws:iam::123456789012:role/EKSAdminRole
      username: system:node:{{EC2PrivateDNSName}}
      groups:
        - system:masters
```

And for a developer:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: arn:aws:iam::123456789012:role/EKSDevRole
      username: system:node:{{EC2PrivateDNSName}}
      groups:
        - system:devs
```

### Mermaid Diagrams

To visualize the architecture and flow, we can use Mermaid diagrams.

#### Architecture Diagram

```mermaid
graph LR
  A[User] --> B[IAM Role]
  B --> C[Kubernetes Role]
  C --> D[Kubernetes Cluster]
  E[Terraform] --> B
  E --> C
```

This diagram shows the flow from the user assuming an IAM role, which is then mapped to a Kubernetes role, and finally interacts with the Kubernetes cluster.

### Common Pitfalls and Best Practices

#### Common Pitfalls

1. **Incorrect Role Mapping**: Ensure that the IAM role ARNs are correctly specified in the `aws-auth` ConfigMap.
2. **Insufficient Permissions**: Make sure that the IAM roles have the necessary permissions to perform their intended tasks.
3. **Overly Permissive Policies**: Avoid granting excessive permissions to IAM roles, especially those intended for developers.

#### Best Practices

1. **Least Privilege Principle**: Grant only the minimum necessary permissions to IAM roles.
2. **Regular Audits**: Regularly review and audit IAM roles and their associated permissions.
3. **Use Managed Policies**: Whenever possible, use AWS managed policies instead of custom policies.

### Real-World Examples

#### Recent Breaches

One notable breach involving Kubernetes and IAM roles occurred in 2021 when a misconfigured IAM role allowed unauthorized access to a Kubernetes cluster. This led to the exposure of sensitive data and potential compromise of the cluster.

#### Secure Coding Fixes

Here’s an example of a vulnerable configuration and its secure counterpart:

**Vulnerable Configuration**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: arn:aws:iam::123456789012:role/EKSVulnRole
      username: system:node:{{EC2PrivateDNSName}}
      groups:
        - system:masters
```

**Secure Configuration**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: aws-auth
  namespace: kube-system
data:
  mapRoles: |
    - rolearn: arn:aws:iam::123456789012:role/EKSSecureRole
      username: system:node:{{EC2PrivateDNSName}}
      groups:
        - system:devs
```

### How to Prevent / Defend

#### Detection

1. **Audit Logs**: Enable and monitor AWS CloudTrail logs to detect unauthorized access attempts.
2. **Kubernetes Audit Logs**: Enable Kubernetes audit logs to track API server requests.

#### Prevention

1. **IAM Role Policies**: Ensure that IAM role policies are least privilege and regularly reviewed.
2. **Terraform State Management**: Use version control for Terraform state files to track changes and prevent unauthorized modifications.

#### Secure-Coding Fixes

1. **Use Managed Policies**: Instead of custom policies, use AWS managed policies.
2. **Regular Reviews**: Conduct regular reviews of IAM roles and their associated permissions.

### Complete Example

#### Full HTTP Request and Response

Here’s an example of a full HTTP request and response for creating an IAM role using the AWS SDK:

**HTTP Request**

```http
POST / HTTP/1.1
Host: iam.amazonaws.com
Content-Type: application/x-www-form-urlencoded; charset=utf-8
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20150101/us-east-1/iam/aws4_request, SignedHeaders=content-type;host;x-amz-date, Signature=fe5fbd6c702c47dd1c1b8500f970c8b9c4dfe82e449b6c2d4d2d4290df04e1fb
X-Amz-Date: 20150101T000000Z
Content-Length: 123

Action=CreateRole&RoleName=EKSAdminRole&AssumeRolePolicyDocument={"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ec2.amazonaws.com"},"Action":"sts:AssumeRole"}]}
```

**HTTP Response**

```http
HTTP/1.1 200 OK
Content-Type: application/xml
Content-Length: 1234
Date: Thu, 01 Jan 2015 00:00:00 GMT

<?xml version="1.0"?>
<CreateRoleResponse xmlns="https://iam.amazonaws.com/doc/2010-05-08/">
  <CreateRoleResult>
    <Role>
      <Path>/</Path>
      <RoleName>EKSAdminRole</RoleName>
      <RoleId>AROAEXAMPLE</RoleId>
      <Arn>arn:aws:iam::123456789012:role/EKSAdminRole</Arn>
      <CreateDate>2015-01-01T00:00:00Z</CreateDate>
      <AssumeRolePolicyDocument>{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"ec2.amazonaws.com"},"Action":"sts:AssumeRole"}]}</AssumeRolePolicyDocument>
    </Role>
  </CreateRoleResult>
  <ResponseMetadata>
    <RequestId>EXAMPLE1-90ab-cdef-fedc-ba987EXAMPLE</RequestId>
  </_ResponseMetadata>
</CreateRoleResponse>
```

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but can be adapted for Kubernetes security practices.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **Kubernetes Goat**: A Kubernetes-based security training platform.

These labs provide practical experience in configuring IAM roles and linking them to Kubernetes roles within an EKS cluster.

### Conclusion

Proper configuration of IAM roles and their linkage to Kubernetes roles is essential for securing your Kubernetes clusters. By following the steps outlined in this chapter, you can ensure that only authorized users and services can interact with your cluster resources, thereby reducing the risk of unauthorized access and potential security breaches.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure IAM Roles and link to K8s Roles in IaC/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure IAM Roles and link to K8s Roles in IaC/02-Introduction to Kubernetes Access Management|Introduction to Kubernetes Access Management]]
