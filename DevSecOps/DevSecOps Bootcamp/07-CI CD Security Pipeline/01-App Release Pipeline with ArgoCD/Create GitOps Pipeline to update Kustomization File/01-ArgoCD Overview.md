---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## ArgoCD Overview

### What is ArgoCD?

ArgoCD is a declarative, extensible, open-source continuous delivery tool for Kubernetes. It allows you to manage your Kubernetes applications using GitOps principles. ArgoCD provides features such as automated deployment, rollouts, and rollbacks, all driven by the state of your Git repository.

### Key Features of ArgoCD

- **Declarative Deployment**: Define the desired state of your applications in Git repositories.
- **Automated Sync**: Continuously synchronize the actual state of your Kubernetes cluster with the desired state in Git.
- **Rollout and Rollback**: Manage application rollouts and rollbacks in a controlled manner.
- **Access Control**: Enforce strict access control policies to ensure only authorized users can make changes.

### How ArgoCD Works

ArggoCD operates by watching the Git repository for changes and applying those changes to the Kubernetes cluster. This is done through a series of steps:

1. **Sync**: ArgoCD compares the desired state in Git with the actual state in the cluster.
2. **Apply**: If there are differences, ArgoCD applies the necessary changes to bring the cluster into alignment with the desired state.
3. **Monitor**: ArgoCD continuously monitors the cluster to ensure it remains in sync with the Git repository.

### Real-World Example: Recent CVEs

One recent example is the CVE-2021-20225, which affected the Kubernetes API server. This vulnerability allowed unauthorized users to bypass authentication and gain elevated privileges. A GitOps pipeline with proper access controls and regular audits could have helped mitigate this risk.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Create GitOps Pipeline to update Kustomization File/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Create GitOps Pipeline to update Kustomization File/02-Detailed Explanation of Concepts|Detailed Explanation of Concepts]]
