---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Introduction to Application Release Pipeline with ArgoCD

In the realm of DevSecOps, continuous integration and continuous delivery (CI/CD) pipelines play a crucial role in ensuring that applications are built, tested, and deployed efficiently and securely. One key component in modern CI/CD pipelines is Infrastructure as Code (IaC), which allows developers to manage infrastructure through code, ensuring consistency and reproducibility. In this context, ArgoCD, an open-source declarative continuous delivery tool for Kubernetes, is widely used to automate the deployment and management of applications.

### Why Use ArgoCD?

ArgoCD simplifies the process of deploying and managing applications on Kubernetes clusters by providing a declarative approach to continuous delivery. This means that you can define your desired state in a Git repository, and ArgoCD will automatically synchronize the actual state of your cluster with the desired state. This approach ensures that your applications are always in the correct state and helps in maintaining consistency across different environments.

### Challenges with Terraform and Kubernetes Manifests

When integrating Terraform with Kubernetes, one common challenge is handling Kubernetes manifest files that are not defined as Terraform resources. Terraform is primarily designed to manage infrastructure resources, such as virtual machines, networks, and storage, but it is not optimized for applying Kubernetes manifests directly. This is where ArgoCD comes into play.

#### Example Scenario

Consider a scenario where you have a Kubernetes manifest file that defines a custom resource for a specific application. This manifest file is not defined as a Terraform resource but needs to be applied to the cluster after ArgoCD is deployed and running. Here’s how you can handle this situation:

1. **Deploy ArgoCD**: First, ensure that ArgoCD is deployed and running in the cluster.
2. **Apply Kubernetes Manifest**: Once ArgoCD is up and running, you can apply the Kubernetes manifest file directly using `kubectl` commands.

### Deploying ArgoCD Using Terraform

Let’s start by deploying ArgoCD using Terraform. We’ll assume that you already have a Terraform configuration set up to manage your Kubernetes cluster.

```hcl
provider "kubernetes" {
  config_path = "~/.kube/config"
}

resource "kubernetes_namespace" "argocd" {
  metadata {
    name = "argocd"
  }
}

resource "helm_release" "argocd" {
  name       = "argocd"
  chart      = "argo/argo-cd"
  namespace  = kubernetes_namespace.argocd.metadata[0].name
  version    = "3.0.0"
  depends_on = [kubernetes_namespace.argocd]

  set {
    name  = "server.insecure"
    value = true
  }

  set {
    name  = "controller.repoServer"
    value = "https://github.com"
  }
}
```

This Terraform configuration deploys ArgoCD into the `argocd` namespace. The `helm_release` resource uses the official ArgoCD Helm chart to install ArgoCD.

### Applying Kubernetes Manifest Directly

Once ArgoCD is deployed, you can apply the Kubernetes manifest file directly using `kubectl`. This is done in a separate stage of the pipeline to ensure that ArgoCD is up and running before the manifest is applied.

#### Example Kubernetes Manifest

Here’s an example of a Kubernetes manifest file that defines a custom resource:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-app
        image: my-app:latest
        ports:
        - containerPort: 80
```

#### Applying the Manifest Using `kubectl`

To apply this manifest using `kubectl`, you would run the following command:

```bash
kubectl apply -f my-app-deployment.yaml
```

### Creating a Separate Stage in the Pipeline

To ensure that the `kubectl` command is executed only after ArgoCD is deployed, you can create a separate stage in your pipeline. This stage will wait until the previous stage (deploying ArgoCD) is completed before executing the `kubectl` command.

#### Example Pipeline Stage

Here’s an example of how you might configure this stage in a Jenkins pipeline:

```groovy
pipeline {
    agent any

    stages {
        stage('Deploy ArgoCD') {
            steps {
                script {
                    // Run Terraform to deploy ArgoCD
                    sh 'terraform init'
                    sh 'terraform apply -auto-approve'
                }
            }
        }
        stage('Apply Kubernetes Manifest') {
            steps {
                script {
                    // Wait for ArgoCD to be up and running
                    sleep 30

                    // Apply the Kubernetes manifest
                    sh 'kubectl apply -f my-app-deployment.yaml'
                }
            }
        }
    }
}
```

### Pitfalls and Best Practices

#### Common Mistakes

1. **Not Waiting for ArgoCD to Be Up and Running**: If you attempt to apply the Kubernetes manifest before ArgoCD is fully deployed, you may encounter errors.
2. **Using `kubectl` Commands in Terraform**: While it’s possible to use `kubectl` commands within Terraform, it’s generally not recommended due to the complexity and potential for errors.

#### Best Practices

1. **Use Separate Stages**: Ensure that the deployment of ArgoCD and the application of Kubernetes manifests are handled in separate stages of the pipeline.
2. **Wait for Completion**: Always wait for the previous stage to complete before moving on to the next stage.
3. **Use Proper Error Handling**: Implement proper error handling and logging to ensure that any issues are caught and addressed promptly.

### Real-World Examples and Recent CVEs

#### Example: CVE-2021-20225

CVE-2021-20225 is a vulnerability in ArgoCD that allows an attacker to bypass authentication and gain unauthorized access to the ArgoCD server. This vulnerability highlights the importance of securing your ArgoCD deployment and ensuring that all components are properly configured.

#### How to Prevent / Defend

1. **Secure Authentication**: Ensure that ArgoCD is configured with proper authentication mechanisms, such as OAuth2 or OpenID Connect.
2. **Regular Updates**: Keep ArgoCD and all related components up to date with the latest security patches.
3. **Network Segmentation**: Use network segmentation to isolate ArgoCD and other critical components from the rest of the environment.

### Secure Coding Fixes

#### Vulnerable Code

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: my-image:latest
    ports:
    - containerPort: 80
```

#### Secure Code

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-pod
spec:
  containers:
  - name: my-container
    image: my-image:latest
    ports:
    - containerPort: 80
    securityContext:
      capabilities:
        drop:
        - ALL
      readOnlyRootFilesystem: true
```

### Conclusion

In conclusion, integrating ArgoCD into your CI/CD pipeline can greatly enhance the efficiency and security of your application deployments. By carefully managing the deployment of ArgoCD and the application of Kubernetes manifests, you can ensure that your applications are always in the correct state and that your infrastructure is secure. Remember to follow best practices and stay vigilant against potential vulnerabilities to maintain a robust and secure DevSecOps environment.

### Hands-On Labs

For hands-on practice with ArgoCD and Kubernetes manifest management, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on web application security, including some that touch on CI/CD pipelines.
- **OWASP Juice Shop**: A deliberately insecure web application for security training, which can be used to practice deploying and securing applications.
- **Kubernetes Goat**: A Kubernetes-based security training platform that includes exercises on deploying and managing applications with ArgoCD.

By completing these labs, you can gain practical experience in deploying and managing applications with ArgoCD and Kubernetes, ensuring that you are well-prepared to handle real-world scenarios.

---
<!-- nav -->
[[03-Introduction to Application Release Pipeline with ArgoCD Part 2|Introduction to Application Release Pipeline with ArgoCD Part 2]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/IaC Pipeline Configuration Deploy Argo Part 2/00-Overview|Overview]] | [[05-Introduction to Infrastructure as Code (IaC) and Continuous Delivery with ArgoCD|Introduction to Infrastructure as Code (IaC) and Continuous Delivery with ArgoCD]]
