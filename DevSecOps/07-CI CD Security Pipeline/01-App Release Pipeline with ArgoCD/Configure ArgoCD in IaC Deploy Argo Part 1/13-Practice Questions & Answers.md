---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain how to deploy ArgoCD using a Helm chart in Terraform.**

To deploy ArgoCD using a Helm chart in Terraform, you can use the `helm_release` resource. Here’s an example:

```hcl
provider "helm" {
  kubernetes {
    host = var.kubernetes_host
    token = var.kubernetes_token
  }
}

resource "helm_release" "argocd" {
  name       = "argocd"
  repository = "https://argoproj.github.io/argo-helm"
  chart      = "argo-cd"
  version    = "latest"

  set {
    name  = "server.extraArgs.admin.password"
    value = var.argocd_admin_password
  }

  set {
    name  = "server.extraArgs.admin.username"
    value = var.argocd_admin_username
  }

  depends_on = [module.eks_cluster]
}
```

This configuration specifies the Helm chart repository, the chart name, and the version. Additionally, it sets specific parameters for the ArgoCD server, such as the admin username and password. The `depends_on` attribute ensures that the Helm chart is deployed only after the EKS cluster is created.

**Q2. How would you create a Kubernetes secret for ArgoCD to access a GitOps repository?**

To create a Kubernetes secret for ArgoCD to access a GitOps repository, you can use the `kubernetes_secret` resource in Terraform. Here’s an example:

```hcl
resource "kubernetes_secret" "argocd_gitops_repo" {
  metadata {
    name      = "argocd-gitops-repo"
    namespace = "argocd"
  }

  data = {
    username = base64encode(var.gitops_repo_username)
    password = base64encode(var.gitops_repo_password)
  }

  type = "Opaque"

  depends_on = [helm_release.argocd]
}
```

This configuration creates a secret named `argocd-gitops-repo` in the `argocd` namespace. The `data` block contains the encoded username and password for accessing the GitOps repository. The `depends_on` attribute ensures that the secret is created only after the ArgoCD Helm chart is deployed.

**Q3. Why is it important to set the `depends_on` attribute in Terraform configurations for ArgoCD deployment?**

Setting the `depends_on` attribute in Terraform configurations for ArgoCD deployment is crucial for ensuring the correct order of resource creation and destruction. For instance, the ArgoCD Helm chart should only be deployed after the EKS cluster is created. Similarly, the Kubernetes secret for the GitOps repository should only be created after the ArgoCD Helm chart is deployed.

By specifying dependencies, Terraform can create a dependency graph that ensures resources are created and destroyed in the correct order. This prevents errors such as trying to create a secret in a non-existent namespace or attempting to deploy a Helm chart to a non-existent cluster.

**Q4. Explain how to enable port forwarding for a Kubernetes admin to access the ArgoCD UI from a local machine.**

To enable port forwarding for a Kubernetes admin to access the ArgoCD UI from a local machine, you need to grant the necessary permissions to the Kubernetes admin role. Specifically, you need to add the `create` permission for the `pods/portforward` resource.

Here’s an example of how to modify the Kubernetes role:

```yaml
kind: Role
apiVersion: rbac.authorization.k8s.io/v1
metadata:
  name: cluster-admin
rules:
  - apiGroups: [""]
    resources: ["pods"]
    verbs: ["get", "list", "watch", "exec", "attach", "portforward"]
```

By adding the `portforward` verb to the `pods` resource, the Kubernetes admin will be able to perform port forwarding using the `kubectl port-forward` command. This allows the admin to access the ArgoCD UI from their local machine by creating a temporary proxy to the internal service.

**Q5. What is the purpose of creating an ArgoCD application manifest in the infrastructure repository?**

The purpose of creating an ArgoCD application manifest in the infrastructure repository is to define how ArgoCD should manage the deployment of applications from a Git repository to the Kubernetes cluster. The application manifest specifies the source (Git repository) and the destination (Kubernetes cluster) for the application deployment.

Here’s an example of an ArgoCD application manifest:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: online-boutique
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/example/online-boutique.git
    targetRevision: HEAD
    path: overlays/dev
  destination:
    server: https://kubernetes.default.svc
    namespace: online-boutique
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - createNamespace=true
```

This manifest defines the source repository (`repoURL`), the target revision (`targetRevision`), and the path within the repository (`path`). It also specifies the destination Kubernetes cluster (`server`) and namespace (`namespace`). The `syncPolicy` section enables automated synchronization, pruning, and self-healing, ensuring that the cluster remains in sync with the Git repository.

**Q6. How does the `Prune` option work in an ArgoCD application manifest?**

The `Prune` option in an ArgoCD application manifest controls whether ArgoCD should delete resources in the Kubernetes cluster that are no longer present in the Git repository. When `Prune` is set to `true`, ArgoCD will automatically remove any resources that are no longer defined in the Git repository.

For example, if you have a Kubernetes manifest file that includes a deployment and a service, and you later remove the service from the manifest, ArgoCD will delete the corresponding service in the cluster if `Prune` is enabled.

Here’s an example of enabling `Prune` in an ArgoCD application manifest:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: online-boutique
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/example/online-boutique.git
    targetRevision: HEAD
    path: overlays/dev
  destination:
    server: https://kubernetes.default.svc
    namespace: online-b_boutique
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - createNamespace=true
```

In this example, the `Prune` option is set to `true`, ensuring that any resources removed from the Git repository are also removed from the Kubernetes cluster.

**Q7. What is the significance of the `selfHeal` option in an ArgoCD application manifest?**

The `selfHeal` option in an ArgoCD application manifest is significant because it ensures that any manual changes made directly to the Kubernetes cluster are corrected to match the desired state defined in the Git repository. When `selfHeal` is set to `true`, ArgoCD will automatically reconcile any discrepancies between the cluster and the Git repository.

For example, if an admin manually deletes a pod or updates a deployment directly in the cluster without committing the changes to the Git repository, ArgoCD will detect these changes and revert them to the state defined in the Git repository.

Here’s an example of enabling `selfHeal` in an ArgoCD application manifest:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: online-boutique
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/example/online-boutique.git
    targetRevision: HEAD
    path: overlays/dev
  destination:
    server: https://kubernetes.default.svc
    namespace: online-boutique
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - createNamespace=true
```

In this example, the `selfHeal` option is set to `true`, ensuring that any manual changes in the cluster are automatically reverted to match the desired state defined in the Git repository.

**Q8. How does the `createNamespace` option in an ArgoCD application manifest work?**

The `createNamespace` option in an ArgoCD application manifest controls whether ArgoCD should automatically create a namespace in the Kubernetes cluster if it does not already exist. When `createNamespace` is set to `true`, ArgoCD will create the specified namespace if it is not present.

For example, if your application manifest specifies a namespace that does not yet exist in the cluster, ArgoCD will create it automatically.

Here’s an example of enabling `createNamespace` in an ArgoCD application manifest:

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: online-boutique
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/example/online-boutique.git
    targetRevision: HEAD
    path: overlays/dev
  destination:
    server: https://kubernetes.default.svc
    namespace: online-boutique
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - createNamespace=true
```

In this example, the `createNamespace` option is set to `true`, ensuring that the `online-boutique` namespace is created if it does not already exist in the cluster.

---
<!-- nav -->
[[12-Configuring ArgoCD in Infrastructure as Code (IaC)|Configuring ArgoCD in Infrastructure as Code (IaC)]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Configure ArgoCD in IaC Deploy Argo Part 1/00-Overview|Overview]]
