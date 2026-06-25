---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Kubernetes Config Maps and Authentication

In the context of Kubernetes, a Config Map is a Kubernetes object that stores configuration data as key-value pairs. This data can then be consumed by pods and other Kubernetes objects. Config Maps are useful because they allow you to separate configuration data from your application code, making it easier to manage and update.

### What is a Config Map?

A Config Map is an API object used to store non-confidential data in key-value pairs. Pods can consume the data in a Config Map as environment variables, command-line arguments, or as configuration files in a volume. This separation allows you to decouple configuration from your application logic, making it easier to change configurations without modifying the application itself.

#### Why Use Config Maps?

Using Config Maps offers several benefits:

1. **Decoupling Configuration from Code**: By storing configuration data in Config Maps, you can modify the configuration without changing the application code.
2. **Dynamic Updates**: Config Maps can be updated dynamically without restarting the pods that use them.
3. **Version Control**: Config Maps can be version-controlled separately from the application code, allowing you to track changes and roll back if necessary.

### Config Map Creation

To create a Config Map, you can define it in a YAML file and apply it using `kubectl`. Here is an example of a Config Map definition:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: my-config
data:
  app-setting1: value1
  app-setting2: value2
```

You can apply this Config Map using the following command:

```sh
kubectl apply -f configmap.yaml
```

### Authentication with Kubernetes

Authentication in Kubernetes is the process of verifying the identity of users and services that interact with the Kubernetes API server. This is crucial for ensuring that only authorized entities can access and manipulate resources within the cluster.

#### How Authentication Works

Kubernetes supports various forms of authentication, including:

1. **X.509 Client Certificates**: Each user or service is issued a client certificate, which is used to authenticate with the API server.
2. **Username and Password**: Basic authentication using username and password.
3. **Service Accounts**: Tokens associated with service accounts are used for authentication.
4. **Webhook Token Authentication**: Custom authentication plugins can be implemented using webhook token authentication.

### Configuring the Kubernetes Provider in Terraform

When creating an EKS cluster using Terraform, you often need to configure the Kubernetes provider to authenticate with the cluster. This involves setting up the necessary credentials and configuration to allow Terraform to interact with the Kubernetes API.

#### Example Terraform Configuration

Here is an example of a Terraform configuration that sets up an EKS cluster and configures the Kubernetes provider:

```hcl
provider "aws" {
  region = "us-west-2"
}

resource "aws_eks_cluster" "example" {
  name     = "example-cluster"
  role_arn = aws_iam_role.example.arn

  vpc_config {
    subnet_ids = [aws_subnet.example.id]
  }
}

resource "aws_iam_role" "example" {
  name = "example-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "eks.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy_attachment" "example" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
  role_arn   = aws_iam_role.example.arn
}

provider "kubernetes" {
  host                   = aws_eks_cluster.example.endpoint
  cluster_ca_certificate = base64decode(aws_eks_cluster.example.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.example.token
}

data "aws_eks_cluster_auth" "example" {
  name = aws_eks_cluster.example.name
}
```

### Terraform Plan and Apply

Before applying the configuration, it is essential to run `terraform plan` to validate the configuration and preview the changes that will be made. This step ensures that all attributes are correctly set and shows the resources that will be created.

#### Running Terraform Plan

```sh
terraform plan
```

This command will output a detailed plan of the actions Terraform will take, including the creation of resources. In the provided example, it states that it plans to add 50 resources.

### Dependencies and Providers

When working with Terraform, it is important to manage dependencies and providers effectively. Providers are responsible for interacting with different infrastructure services, such as AWS, Kubernetes, etc.

#### Example of Dependency Providers

```hcl
provider "aws" {
  region = "us-west-2"
}

provider "kubernetes" {
  host                   = aws_eks_cluster.example.endpoint
  cluster_ca_certificate = base64decode(aws_eks_cluster.example.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.example.token
}
```

### Real-World Examples and CVEs

Real-world examples and CVEs can help illustrate the importance of proper configuration and authentication in Kubernetes clusters.

#### Example: CVE-2021-25741

CVE-2021-25741 is a critical vulnerability in Kubernetes that allows an attacker to bypass authentication and gain unauthorized access to the cluster. This vulnerability highlights the importance of properly securing and managing authentication mechanisms.

### How to Prevent / Defend

#### Secure Configuration Practices

1. **Use Strong Authentication Mechanisms**: Ensure that strong authentication methods like X.509 certificates or service account tokens are used.
2. **Regularly Update and Patch**: Keep your Kubernetes cluster and related components up to date with the latest security patches.
3. **Audit and Monitor**: Regularly audit and monitor access to the Kubernetes API server to detect and respond to unauthorized access attempts.

#### Secure Code Fix

Here is an example of a vulnerable configuration and its secure counterpart:

**Vulnerable Configuration:**

```hcl
provider "kubernetes" {
  host                   = aws_eks_cluster.example.endpoint
  cluster_ca_certificate = base64decode(aws_eks_cluster.example.certificate_authority[0].data)
  token                  = "insecure-token"
}
```

**Secure Configuration:**

```hcl
provider "kubernetes" {
  host                   = aws_eks_cluster.example.endpoint
  cluster_ca_certificate = base64decode(aws_eks_cluster.example.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.example.token
}
```

### Conclusion

Creating an EKS cluster using Terraform involves several steps, including setting up Config Maps, configuring authentication, and managing dependencies. Understanding these concepts and practices is crucial for maintaining a secure and efficient Kubernetes cluster. By following best practices and regularly auditing your configurations, you can ensure that your cluster remains secure against potential threats.

### Practice Labs

For hands-on practice with Kubernetes and Terraform, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on web application security, including Kubernetes-related challenges.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **CloudGoat**: Provides a series of labs focused on AWS security, including EKS and Terraform configurations.

These labs provide practical experience and reinforce the theoretical knowledge gained from this chapter.

---
<!-- nav -->
[[05-Introduction to EKS Clusters and Worker Nodes|Introduction to EKS Clusters and Worker Nodes]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/10-Creating EKS Cluster Using Terraform Module/00-Overview|Overview]] | [[07-Kubernetes Authentication and Configuration with Terraform|Kubernetes Authentication and Configuration with Terraform]]
