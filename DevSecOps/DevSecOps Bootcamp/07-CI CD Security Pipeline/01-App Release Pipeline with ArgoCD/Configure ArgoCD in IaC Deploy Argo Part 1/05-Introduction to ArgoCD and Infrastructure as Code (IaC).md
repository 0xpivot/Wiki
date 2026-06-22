---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Introduction to ArgoCD and Infrastructure as Code (IaC)

### What is ArgoCD?

ArgoCD is a declarative, GitOps continuous delivery tool for Kubernetes. It allows you to manage your Kubernetes applications using Git repositories. By leveraging Git as a single source of truth, ArgoCD ensures that your application deployments are consistent and reproducible. This approach aligns with the principles of GitOps, which emphasizes using Git as a central source of truth for infrastructure and application configurations.

### Why Use ArgoCD?

Using ArgoCD offers several benefits:

- **Consistency**: Ensures that your application deployments are consistent across different environments.
- **Reproducibility**: Allows you to reproduce deployments easily by referencing the Git repository.
- **Auditability**: Provides a clear audit trail of changes made to your infrastructure and applications.
- **Automation**: Enables automated deployment workflows, reducing manual intervention and minimizing human error.

### How Does ArgoCD Work?

ArgoCD works by continuously comparing the desired state of your Kubernetes applications (defined in Git) with the actual state of your cluster. If there are discrepancies, ArgoCD automatically applies the necessary changes to bring the cluster into alignment with the desired state.

### Dependencies and Order of Operations

When deploying and destroying resources in a Kubernetes cluster, the order of operations is crucial. In the context of the provided transcript, we need to ensure that the Helm chart is deployed before the EKS cluster is destroyed. Similarly, the Helm release should be removed before the EKS cluster is cleaned up.

#### Dependency Management in Terraform

Terraform uses a dependency graph to manage the order of resource creation and destruction. This graph is built based on the `depends_on` configuration in the Terraform files. By specifying dependencies, Terraform ensures that resources are created and destroyed in the correct order.

```terraform
resource "aws_eks_cluster" "example" {
  name     = "example"
  role_arn = aws_iam_role.example.arn
}

resource "helm_release" "example" {
  name       = "example"
  chart      = "stable/nginx-ingress"
  namespace  = "default"
  depends_on = [aws_eks_cluster.example]
}
```

In the above example, the `helm_release` resource depends on the `aws_eks_cluster` resource. This ensures that the Helm chart is deployed only after the EKS cluster is created.

### Declaring Variables in Terraform

Variables in Terraform are used to parameterize your infrastructure definitions. They allow you to pass dynamic values into your Terraform configurations. For sensitive values such as usernames and passwords, it is recommended to set them dynamically in a secure place, such as environment variables in your CI/CD pipeline.

```terraform
variable "username" {
  description = "Username for accessing the Git repository."
  type        = string
}

variable "password" {
  description = "Password for accessing the Git repository."
  type        = string
}
```

### Setting Environment Variables in CI/CD Pipelines

To securely set environment variables in your CI/CD pipeline, you can use tools like Jenkins, GitLab CI, or GitHub Actions. These tools provide mechanisms to store and inject sensitive values into your build processes.

#### Example Using GitHub Actions

```yaml
name: Deploy ArgoCD

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v2

    - name: Set up Terraform
      uses: hashicorp/setup-terraform@v1

    - name: Install dependencies
      run: terraform init

    - name: Apply Terraform
      env:
        TF_VAR_username: ${{ secrets.GIT_USERNAME }}
        TF_VAR_password: ${{ secrets.GIT_PASSWORD }}
      run: terraform apply -auto-approve
```

In this example, the `TF_VAR_username` and `TF_VAR_password` environment variables are set using secrets stored in GitHub.

### Complete Example: Deploying ArgoCD with Terraform

Let's walk through a complete example of deploying ArgoCD using Terraform. We'll cover the entire process, including creating the EKS cluster, deploying the Helm chart, and configuring ArgoCD to connect to a Git repository.

#### Step 1: Create the EKS Cluster

First, we create the EKS cluster using Terraform.

```terraform
provider "aws" {
  region = "us-west-2"
}

resource "aws_iam_role" "example" {
  name = "example"

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

resource "aws_eks_cluster" "example" {
  name     = "example"
  role_arn = aws_iam_role.example.arn
}
```

#### Step 2: Deploy the Helm Chart

Next, we deploy the Helm chart using the `helm_release` resource.

```terraform
resource "helm_release" "example" {
  name       = "argocd"
  chart      = "argo/argo-cd"
  namespace  = "argocd"
  depends_on = [aws_eks_cluster.example]

  set {
    name  = "server.insecure"
    value = "true"
  }

  set {
    name  = "controller.repoServer"
    value = "https://github.com/myorg/myrepo.git"
  }
}
```

#### Step 3: Configure ArgoCD

Finally, we configure ArgoCD to connect to the Git repository.

```terraform
resource "kubectl_manifest" "argocd_config" {
  yaml = <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-cm
  namespace: argocd
data:
  url: https://github.com/myorg/myrepo.git
  username: ${var.username}
  password: ${var.password}
EOF
  depends_on = [helm_release.example]
}
```

### Full Raw HTTP Messages and Responses

When interacting with the EKS cluster and ArgoCD, you will often send HTTP requests to manage resources. Here is an example of a full HTTP request and response for creating an EKS cluster.

#### HTTP Request

```http
POST /clusters HTTP/1.1
Host: eks.us-west-2.amazonaws.com
Content-Type: application/json
Authorization: Bearer <your-token>

{
  "name": "example",
  "roleArn": "arn:aws:iam::123456789012:role/example"
}
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "cluster": {
    "name": "example",
    "status": "CREATING",
    "arn": "arn:aws:eks:us-west-2:123456789012:cluster/example"
  }
}
```

### Common Pitfalls and How to Avoid Them

#### Incorrect Dependency Order

One common pitfall is specifying incorrect dependency order in Terraform. This can lead to errors during the creation or destruction of resources. To avoid this, ensure that you correctly specify dependencies using the `depends_on` configuration.

#### Missing Environment Variables

Another common issue is forgetting to set environment variables for sensitive values. Always ensure that you have securely set these variables in your CI/CD pipeline.

### How to Prevent / Defend

#### Detection

To detect issues with your ArgoCD and Terraform configurations, you can use tools like `terraform validate` and `kubectl describe` to check the status of your resources.

```bash
terraform validate
kubectl describe pods -n argocd
```

#### Prevention

To prevent issues, follow these best practices:

- **Use Secure Secrets Management**: Store sensitive values securely using tools like HashiCorp Vault or AWS Secrets Manager.
- **Automate Testing**: Use automated testing to validate your configurations before deploying them.
- **Regular Audits**: Regularly audit your configurations to ensure they remain secure and up-to-date.

#### Secure Coding Fixes

Here is an example of a vulnerable configuration and its secure counterpart.

**Vulnerable Configuration**

```terraform
resource "kubectl_manifest" "argocd_config" {
  yaml = <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-cm
  namespace: argocd
data:
  url: https://github.com/myorg/myrepo.git
  username: myusername
  password: mypassword
EOF
}
```

**Secure Configuration**

```terraform
resource "kubectl_manifest" "argocd_config" {
  yaml = <<EOF
apiVersion: v1
kind: ConfigMap
metadata:
  name: argocd-cm
  namespace: argocd
data:
  url: https://github.com/myorg/myrepo.git
  username: ${var.username}
  password: ${var.password}
EOF
  depends_on = [helm_release.example]
}
```

### Real-World Examples and Recent Breaches

#### Example: CVE-2021-20225

CVE-2021-20225 is a vulnerability in ArgoCD that allows unauthorized access to the API server. This vulnerability highlights the importance of securing your ArgoCD configurations and ensuring that sensitive values are not exposed.

#### Example: GitHub Data Breach

The GitHub data breach in 2022 underscores the importance of securing your Git repositories and ensuring that sensitive information is not stored in plaintext.

### Practice Labs

For hands-on practice with ArgoCD and Terraform, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **Kubernetes Goat**: A vulnerable Kubernetes cluster for learning about Kubernetes security.

By following these guidelines and best practices, you can effectively manage your ArgoCD and Terraform configurations to ensure secure and reliable deployments.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Configure ArgoCD in IaC Deploy Argo Part 1/04-Introduction to ArgoCD and IaC|Introduction to ArgoCD and IaC]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Configure ArgoCD in IaC Deploy Argo Part 1/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Configure ArgoCD in IaC Deploy Argo Part 1/06-Introduction to ArgoCD and Its Deployment Using Terraform|Introduction to ArgoCD and Its Deployment Using Terraform]]
