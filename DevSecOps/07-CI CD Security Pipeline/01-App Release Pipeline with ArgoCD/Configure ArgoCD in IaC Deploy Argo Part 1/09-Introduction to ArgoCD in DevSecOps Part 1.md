---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Introduction to ArgoCD in DevSecOps

ArgoCD is an open-source declarative continuous delivery tool for Kubernetes. It enables automated deployment of applications to Kubernetes clusters using GitOps principles. In this chapter, we will delve into configuring ArgoCD using Infrastructure as Code (IaC) and deploying it to manage our applications effectively.

### What is ArgoCD?

ArgoCD is a tool that helps you manage your Kubernetes applications using GitOps principles. GitOps is a set of practices that uses Git as a single source of truth for all infrastructure and application configurations. This approach ensures that your infrastructure and applications are version-controlled, auditable, and reproducible.

#### Why Use ArgoCD?

- **Declarative Deployment**: ArgoCD allows you to declare the desired state of your Kubernetes resources in Git repositories. This makes it easier to manage and track changes.
- **Automated Syncing**: ArgoCD can automatically sync your Kubernetes cluster with the desired state defined in Git. This ensures that your cluster is always up-to-date.
- **Rollback Mechanism**: Since all changes are version-controlled in Git, you can easily roll back to previous states if something goes wrong.
- **Multi-Cluster Management**: ArgoCD supports managing multiple Kubernetes clusters from a single control plane, making it ideal for large-scale deployments.

### Key Concepts

Before diving into the configuration, let's understand some key concepts:

- **Source**: The Git repository containing the Kubernetes manifests.
- **Destination**: The Kubernetes cluster where the manifests will be applied.
- **Sync Policy**: Defines how and when ArgoCD should sync the source with the destination.

### Setting Up ArgoCD

To set up ArgoCD, we need to configure it using Infrastructure as Code (IaC). We will use a Git repository as the source and a local Kubernetes cluster as the destination.

#### Step 1: Define the Source

The source is the Git repository containing the Kubernetes manifests. In this example, we will use a specific path within the repository.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/myrepo.git
    targetRevision: HEAD
    path: overlays/dev
```

Here, `repoURL` specifies the URL of the Git repository, `targetRevision` specifies the branch or commit to use, and `path` specifies the directory within the repository containing the Kubernetes manifests.

#### Step 2: Define the Destination

The destination is the Kubernetes cluster where the manifests will be applied. In this case, we are using a local Kubernetes cluster.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/myrepo.git
    targetRevision: HEAD
    path: overlays/dev
  destination:
    server: https://kubernetes.default.svc
    namespace: my-app-namespace
```

Here, `server` specifies the Kubernetes API server URL, and `namespace` specifies the namespace where the manifests will be applied.

#### Step 3: Define the Sync Policy

The sync policy defines how and when ArgoCD should sync the source with the destination. By default, ArgoCD will automatically sync any changes from the repository to the cluster.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/myrepo.git
    targetRevision: HEAD
    path: overlays/dev
  destination:
    server: https://kubernetes.default.svc
    namespace: my-app-namespace
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

Here, `prune` ensures that any resources in the cluster that are not defined in the Git repository are removed, and `selfHeal` ensures that any discrepancies between the desired state and the actual state are automatically resolved.

### Example Configuration

Let's put it all together in a complete example:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/myrepo.git
    targetRevision: HEAD
    path: overlays/dev
  destination:
    server: https://kubernetes.default.svc
    namespace: my-app-namespace
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

### How to Prevent / Defend

#### Detection

To detect any issues with ArgoCD, you can monitor the ArgoCD logs and the Kubernetes events. You can also use tools like Prometheus and Grafana to visualize the health of your ArgoCD setup.

#### Prevention

1. **Secure Git Repository**: Ensure that your Git repository is secure and only authorized users have access to it. Use SSH keys or HTTPS with credentials to authenticate.
2. **Namespace Isolation**: Run ArgoCD in a dedicated namespace (`argocd`) and ensure that it does not have unnecessary permissions to other namespaces.
3. **RBAC Policies**: Implement Role-Based Access Control (RBAC) policies to restrict the permissions of ArgoCD to only the necessary resources.
4. **Automated Syncing**: Turn off automated syncing during testing phases to avoid unintended changes. You can manually trigger syncs when needed.

### Real-World Examples

#### Recent CVEs/Breaches

One notable breach involving Kubernetes was the **CVE-2021-25741**. This vulnerability allowed attackers to bypass authentication and gain unauthorized access to Kubernetes clusters. While this specific CVE is not directly related to ArgoCD, it highlights the importance of securing your Kubernetes environment.

#### Secure Configuration Example

Let's compare a vulnerable configuration with a secure one:

**Vulnerable Configuration:**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/myrepo.git
    targetRevision: HEAD
    path: overlays/dev
  destination:
    server: https://kubernetes.default.svc
    namespace: my-app-namespace
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

**Secure Configuration:**

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
spec:
  project: default
  source:
    repoURL: git@github.com:myorg/myrepo.git
    targetRevision: HEAD
    path: overlays/dev
  destination:
    server: https://kubernetes.default.svc
    namespace: my-app-namespace
  syncPolicy:
    automated:
      prune: true
      selfHeal: false
```

In the secure configuration, we use SSH keys for authentication and disable automated syncing to prevent unintended changes.

### Hands-On Lab Suggestions

For hands-on practice with ArgoCD, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but can provide insights into securing your CI/CD pipelines.
- **OWASP Juice Shop**: A deliberately insecure web application for security training. It can help you understand the importance of securing your entire pipeline.
- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security. It includes scenarios for securing your ArgoCD setup.

### Conclusion

In this chapter, we covered the fundamentals of configuring ArgoCD using Infrastructure as Code (IaC) and deploying it to manage your applications effectively. We explored key concepts, provided detailed examples, and discussed how to prevent and defend against potential issues. By following these guidelines, you can ensure that your ArgoCD setup is secure and reliable.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Configure ArgoCD in IaC Deploy Argo Part 1/08-Introduction to ArgoCD in CICD Pipelines|Introduction to ArgoCD in CICD Pipelines]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Configure ArgoCD in IaC Deploy Argo Part 1/00-Overview|Overview]] | [[10-Introduction to ArgoCD in DevSecOps Part 2|Introduction to ArgoCD in DevSecOps Part 2]]
