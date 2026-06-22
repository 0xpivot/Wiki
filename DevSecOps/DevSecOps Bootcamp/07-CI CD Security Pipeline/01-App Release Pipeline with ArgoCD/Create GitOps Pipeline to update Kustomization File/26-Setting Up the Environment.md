---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Setting Up the Environment

Before we dive into creating the GitOps pipeline, let's set up the necessary environment.

### Prerequisites

To follow along with this chapter, you will need the following:

- **Kubernetes Cluster**: A running Kubernetes cluster.
- **ArgoCD Installed**: ArgoCD installed on your Kubernetes cluster.
- **Git Repository**: A Git repository to store your application manifests.
- **Docker**: Docker installed on your local machine.

### Installing ArgoCD

To install ArgoCD on your Kubernetes cluster, you can use the following commands:

```sh
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Once ArgoCD is installed, you can access the ArgoCD dashboard using the following command:

```sh
argocd login --username admin --password $(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
```

### Creating a Git Repository

Create a Git repository to store your application manifests. For example, you can use GitHub or GitLab to create a new repository.

```sh
git clone https://github.com/yourusername/your-repo.git
cd your-repo
```

### Initializing the Repository

Initialize the repository with some basic files:

```sh
touch README.md
mkdir manifests
echo "apiVersion: v1
kind: ConfigMap
metadata:
  name: example-configmap
data:
  value: initial-value" > manifests/example-configmap.yaml
git add .
git commit -m "Initial commit"
git push origin main
```

---
<!-- nav -->
[[25-Setting Up a GitOps Pipeline with ArgoCD|Setting Up a GitOps Pipeline with ArgoCD]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Create GitOps Pipeline to update Kustomization File/00-Overview|Overview]] | [[27-Setting Up the GitOps Pipeline|Setting Up the GitOps Pipeline]]
