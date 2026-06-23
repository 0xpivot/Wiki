---
course: DevSecOps
topic: Kubernetes Access Management
tags: [devsecops]
---

## Kubernetes Access Management: Configuring Roles and ClusterRoles in Infrastructure as Code (IaC)

### Introduction to Kubernetes Access Management

Kubernetes access management is a critical aspect of securing your Kubernetes clusters. It ensures that only authorized entities can interact with the cluster resources. This involves configuring roles and cluster roles, which define permissions for users and services. In this chapter, we will delve into the details of configuring these roles using Infrastructure as Code (IaC) tools such as Terraform.

### Understanding Roles and ClusterRoles

In Kubernetes, **roles** and **cluster roles** are used to define sets of permissions. A role is namespaced, meaning it applies only within a specific namespace, whereas a cluster role is cluster-wide and applies across all namespaces.

#### Role

A role defines a set of permissions within a specific namespace. Here is an example of a role definition:

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

This role allows read-only access to pods within the `default` namespace.

#### ClusterRole

A cluster role defines a set of permissions that apply across all namespaces. Here is an example of a cluster role definition:

```yaml
apiVersion: rbac.authorization.k8s.io/v
kind: ClusterRole
metadata:
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
```

This cluster role allows read-only access to pods across all namespaces.

### Configuring Roles and ClusterRoles Using Terraform

Terraform is a popular IaC tool that can be used to manage Kubernetes resources, including roles and cluster roles. Below is a detailed example of how to configure these roles using Terraform.

#### Prerequisites

Before you begin, ensure that you have the following:

1. **Terraform Installed**: Ensure that Terraform is installed on your local machine.
2. **AWS CLI Installed**: Ensure that the AWS CLI is installed and configured with appropriate credentials.
3. **EKS Cluster Created**: Ensure that an EKS cluster is created and accessible.

#### Step-by-Step Configuration

1. **Initialize Terraform**: Initialize Terraform in your project directory.

    ```sh
    terraform init
    ```

2. **Define Variables**: Define variables for your EKS cluster name and other necessary parameters.

    ```hcl
    variable "cluster_name" {
      description = "The name of the EKS cluster"
      type        = string
    }

    variable "namespace" {
      description = "The namespace for the role"
      type        = string
      default     = "default"
    }
    ```

3. **Configure Provider**: Configure the Kubernetes provider in your Terraform configuration.

    ```hcl
    provider "kubernetes" {
      host                   = var.cluster_name
      cluster_ca_certificate = filebase64("${path.module}/ca.crt")
      token                  = data.aws_eks_cluster_auth.cluster.token
    }
    ```

4. **Create Role**: Create a role using Terraform.

    ```hcl
    resource "kubernetes_role" "pod_reader" {
      metadata {
        name      = "pod-reader"
        namespace = var.namespace
      }

      rule {
        api_groups   = [""]
        resources    = ["pods"]
        verbs        = ["get", "watch", "list"]
      }
    }
    ```

5. **Create ClusterRole**: Create a cluster role using Terraform.

    ```hcl
    resource "kubernetes_cluster_role" "pod_reader" {
      metadata {
        name = "pod-reader"
      }

      rule {
        api_groups   = [""]
        resources    = ["pods"]
        verbs        = ["get", "watch", "list"]
      }
    }
    ```

6. **Apply Configuration**: Apply the Terraform configuration to create the roles.

    ```sh
    terraform apply
    ```

### Generating and Using Tokens

To authenticate with the Kubernetes cluster, you need to generate and use tokens. This is typically done using the AWS CLI.

#### Generating a Token

1. **Install AWS CLI**: Ensure that the AWS CLI is installed and configured with appropriate credentials.

    ```sh
    pip install awscli
    aws configure
    ```

2. **Generate Token**: Generate a token using the AWS CLI.

    ```sh
    aws eks get-token --cluster-name <cluster-name>
    ```

This command will return a token that can be used to authenticate with the Kubernetes cluster.

#### Using the Token

Once you have the token, you can use it to authenticate with the Kubernetes cluster. This is typically done by setting the `KUBECONFIG` environment variable or by using the token directly in your application.

### Real-World Examples and Recent Breaches

Recent breaches involving Kubernetes access management include:

- **CVE-2021-25741**: This vulnerability allowed unauthorized access to Kubernetes clusters due to misconfigured RBAC rules. Ensuring proper RBAC configuration is crucial to prevent such vulnerabilities.

- **AWS EKS Cluster Compromise**: In a recent incident, an attacker gained unauthorized access to an EKS cluster due to a misconfigured IAM role. Properly configuring IAM roles and RBAC rules is essential to prevent such incidents.

### How to Prevent / Defend

#### Detection

- **Audit Logs**: Enable audit logs in Kubernetes to monitor access attempts and detect unauthorized activities.
- **Security Tools**: Use security tools like Falco, Aqua Security, or Sysdig to monitor and detect suspicious activities.

#### Prevention

- **Least Privilege Principle**: Follow the least privilege principle by granting only the minimum necessary permissions to users and services.
- **Regular Audits**: Regularly audit RBAC configurations to ensure that they are properly configured and up-to-date.

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

### Network Topology and Request/Response Flow

Below is a mermaid diagram illustrating the network topology and request/response flow for accessing a Kubernetes cluster using a token.

```mermaid
graph TD
  A[User] --> B[AWS CLI]
  B --> C[Kubernetes API Server]
  C --> D[Cluster]
  D --> E[Pods]
  style A fill:#f96,stroke:#333,stroke-width:4px
  style B fill:#f96,stroke:#333,stroke-width:4px
  style C fill:#f96,stroke:#333,stroke-width:4px
  style D fill:#f96,stroke:#333,stroke-width:4px
  style E fill:#f96,stroke:#333,stroke-width:4px
```

### Complete Example: Full HTTP Request and Response

Here is a complete example of a full HTTP request and response for generating a token using the AWS CLI.

**HTTP Request**

```http
POST /sts/assumeRole HTTP/1.1
Host: sts.amazonaws.com
Content-Type: application/x-www-form-urlencoded
X-Amz-Target: AWSSecurityTokenService.AssumeRole
Authorization: AWS4-HMAC-SHA256 Credential=AKIAIOSFODNN7EXAMPLE/20230401/us-east-1/sts/aws4_request, SignedHeaders=host;x-amz-date, Signature=6b5f5c6d5e5b5f5c6d5e5b5f5c6d5e5b5f5c6d5e5b5f5c6d5e5b5f5c6d5e5b5f
X-Amz-Date: 20230401T000000Z
Content-Length: 142

Action=AssumeRole&RoleArn=arn:aws:iam::123456789012:role/example-role&RoleSessionName=ExampleSession
```

**HTTP Response**

```http
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 1024
Date: Mon, 01 Apr 2023 00:00:00 GMT

{
  "AssumedRoleUser": {
    "Arn": "arn:aws:sts::123456789012:assumed-role/example-role/ExampleSession",
    "AssumedRoleId": "AROACLKBEXAMPLE:ExampleSession"
  },
  "Credentials": {
    "AccessKeyId": "ASIAIOSFODNN7EXAMPLE",
    "SecretAccessKey": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    "SessionToken": "AQoDYXdzEJr...<truncated>...",
    "Expiration": "2023-04-01T01:00:00Z"
  }
}
```

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to Kubernetes security.
- **OWASP Juice Shop**: Provides a vulnerable web application that can be deployed on Kubernetes for security testing.
- **Kubernetes Goat**: A vulnerable Kubernetes cluster designed for security testing and learning.

By following these steps and best practices, you can effectively manage access to your Kubernetes clusters and ensure their security.

---
<!-- nav -->
[[04-Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 1|Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 1]] | [[DevSecOps/DevSecOps Bootcamp/03-Identity & Access Management/02-Kubernetes Access Management/Configure K8s Role and ClusterRole in IaC/00-Overview|Overview]] | [[06-Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 3|Kubernetes Access Management Configuring Roles and ClusterRoles in Infrastructure as Code (IaC) Part 3]]
