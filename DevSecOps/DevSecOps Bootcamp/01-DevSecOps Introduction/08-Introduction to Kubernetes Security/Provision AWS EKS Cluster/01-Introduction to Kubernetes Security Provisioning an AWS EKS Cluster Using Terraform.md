---
course: DevSecOps
topic: Introduction to Kubernetes Security
tags: [devsecops]
---

## Introduction to Kubernetes Security: Provisioning an AWS EKS Cluster Using Terraform

### Background Theory

Kubernetes (often abbreviated as K8s) is an open-source system for automating deployment, scaling, and management of containerized applications. One of the most popular ways to deploy Kubernetes is through managed services like Amazon Elastic Kubernetes Service (EKS). EKS simplifies the process of deploying, managing, and scaling Kubernetes clusters on AWS.

Terraform is an infrastructure as code (IaC) tool that allows you to define and provision your infrastructure using declarative configuration files. These configurations can then be used to create, modify, and destroy infrastructure resources in a consistent and repeatable manner.

### Setting Up the Terraform Project

Before we start provisioning the EKS cluster, we need to initialize our Terraform project. This involves downloading the necessary providers and modules required for the project.

#### Step 1: Initialize Terraform

The first step is to run the `terraform init` command. This command initializes the working directory containing the Terraform configuration files. It downloads the providers and modules specified in the configuration.

```bash
terraform init
```

This command does the following:

- Downloads the providers and modules specified in the `main.tf` file.
- Creates a `.terraform` directory in the current working directory.
- Stores the downloaded providers and modules in the `.terraform` directory.

#### Example Configuration

Here is an example of a `main.tf` file that specifies the AWS provider and other necessary modules:

```hcl
provider "aws" {
  region = "us-west-2"
}

module "eks_cluster" {
  source = "terraform-aws-modules/eks/aws"

  cluster_name = "my-cluster"
  version      = "1.21"

  subnets = ["subnet-1", "subnet-2"]
  vpc_id  = "vpc-12345678"
}
```

### Step 2: Plan the Configuration

Once the initialization is complete, the next step is to run the `terraform plan` command. This command generates an execution plan based on the configuration files and the current state of the infrastructure.

```bash
terraform plan -var-file="variables.tfvars"
```

The `-var-file` flag specifies the file containing the variable values. This file typically contains sensitive information such as access keys, secret keys, and other environment-specific settings.

#### Example Variables File

Here is an example of a `variables.tfvars` file:

```hcl
access_key = "AKIAIOSFODNN7EXAMPLE"
secret_key = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
region     = "us-west-2"
```

### Step 3: Apply the Configuration

After reviewing the plan, the final step is to apply the configuration using the `terraform apply` command. This command creates the resources defined in the configuration files.

```bash
terraform apply -var-file="variables.tfvars"
```

### Handling Warnings and Errors

During the execution of the `terraform plan` and `terraform apply` commands, you might encounter warnings or errors. One common warning is related to deprecated arguments.

#### Example Warning

```plaintext
Warning: Argument is deprecated

The argument "cluster_addons" is deprecated. Please use the "addons" argument instead.
```

This warning indicates that the `cluster_addons` argument is deprecated and should be replaced with the `addons` argument. However, in this case, the warning is a false positive due to a bug in Terraform. You can safely ignore this warning.

### How to Prevent / Defend

#### Detection

To detect issues during the Terraform execution, you can use tools like `tfsec` and `tflint`. These tools analyze your Terraform configuration files and identify potential security vulnerabilities and best practice violations.

#### Prevention

To prevent issues, ensure that your Terraform configuration files follow best practices and security guidelines. Here are some tips:

- **Use the latest version of Terraform**: Ensure that you are using the latest version of Terraform to avoid deprecated arguments and other issues.
- **Validate your configuration**: Use tools like `tfsec` and `tflint` to validate your configuration files.
- **Secure your variables**: Store sensitive information in a secure manner, such as using AWS Secrets Manager or HashiCorp Vault.

#### Secure Code Fix

Here is an example of a vulnerable configuration and its secure counterpart:

**Vulnerable Configuration**

```hcl
resource "aws_iam_role" "example" {
  name = "example-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": "*",
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}
```

**Secure Configuration**

```hcl
resource "aws_iam_role" "example" {
  name = "example-role"

  assume_role_policy = <<EOF
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
EOF
}
```

### Real-World Examples

#### Recent CVEs and Breaches

One recent example of a Kubernetes-related breach is the **CVE-2021-25741**. This vulnerability affects the Kubernetes API server and allows an attacker to bypass authentication and authorization checks. To mitigate this vulnerability, ensure that your Kubernetes cluster is up-to-date and follows best practices for securing the API server.

#### Example Exploit

Here is an example of an exploit for CVE-2021-25741:

```bash
curl -k https://<API_SERVER_IP>:6443/api/v1/namespaces/default/pods -H "Authorization: Bearer <TOKEN>"
```

This exploit uses an invalid token to bypass authentication and retrieve pod information.

### Mermaid Diagrams

#### Network Topology

```mermaid
graph TD
  A[User] -->|HTTPS Request| B[Load Balancer]
  B -->|HTTP Request| C[Kubernetes API Server]
  C -->|Internal Communication| D[ETCD]
  C -->|Internal Communication| E[Kubernetes Controller Manager]
  C -->|Internal Communication| F[Kubernetes Scheduler]
  C -->|Internal Communication| G[Kubernetes Node]
```

#### Request/Response Flow

```mermaid
sequenceDiagram
  participant User
  participant LoadBalancer
  participant APIServer
  participant ETCD
  participant ControllerManager
  participant Scheduler
  participant Node

  User->>LoadBalancer: HTTPS Request
  LoadBalancer->>APIServer: HTTP Request
  APIServer->>ETCD: Internal Communication
  APIServer->>ControllerManager: Internal Communication
  APIServer->>Scheduler: Internal Communication
  APIServer->>Node: Internal Communication
```

### Complete Example

#### Full HTTP Request and Response

```http
POST /api/v1/namespaces/default/pods HTTP/1.1
Host: <API_SERVER_IP>:6443
Content-Type: application/json
Authorization: Bearer <TOKEN>

{
  "apiVersion": "v1",
  "kind": "Pod",
  "metadata": {
    "name": "example-pod"
  },
  "spec": {
    "containers": [
      {
        "name": "example-container",
        "image": "nginx:latest"
      }
    ]
  }
}
```

```http
HTTP/1.1 201 Created
Date: Mon, 01 Jan 2024 00:00:00 GMT
Content-Type: application/json
Content-Length: 1234

{
  "kind": "Pod",
  "apiVersion": "v1",
  "metadata": {
    "name": "example-pod",
    "namespace": "default",
    "selfLink": "/api/v1/namespaces/default/pods/example-p
```

### Hands-On Labs

For hands-on practice with Kubernetes security, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a series of labs focused on web application security, including Kubernetes security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **Kubernetes Goat**: A vulnerable Kubernetes cluster for learning and practicing Kubernetes security.

These labs provide practical experience in identifying and mitigating security vulnerabilities in Kubernetes environments.

### Conclusion

Provisioning an AWS EKS cluster using Terraform involves several steps, including initializing the project, planning the configuration, and applying the configuration. By following best practices and using tools like `tfsec` and `tflint`, you can ensure that your Kubernetes cluster is secure and compliant with industry standards.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/08-Introduction to Kubernetes Security/Provision AWS EKS Cluster/00-Overview|Overview]] | [[02-Introduction to Kubernetes Security Provisioning an AWS EKS Cluster Part 1|Introduction to Kubernetes Security Provisioning an AWS EKS Cluster Part 1]]
