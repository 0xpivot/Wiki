---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Creating a CI Pipeline that Triggers a GitOps Pipeline Using ArgoCD

### Background Theory

In modern DevSecOps practices, continuous integration (CI) and continuous delivery (CD) pipelines are essential for automating the testing and deployment processes. GitOps is an emerging practice that uses Git as a single source of truth for infrastructure and application configurations. ArgoCD is a popular open-source tool that implements GitOps principles to manage Kubernetes applications.

The goal is to create a CI pipeline that automatically triggers a GitOps pipeline whenever changes are committed and pushed to the repository. This ensures that your application is continuously tested and deployed in a controlled manner.

### Step-by-Step Mechanics

#### Committing Changes

When you make changes to your application or configuration files, you first need to commit these changes to your local Git repository. This step records the changes in your local history.

```bash
git add .
git commit -m "Add new pipeline configuration"
```

**Explanation:**
- `git add .`: Adds all modified files to the staging area.
- `git commit -m "Add new pipeline configuration"`: Commits the staged changes with a descriptive message.

#### Pushing Changes

After committing the changes locally, you need to push them to the remote repository. This step updates the remote repository with your latest changes.

```bash
git push origin main
```

**Explanation:**
- `git push origin main`: Pushes the committed changes to the `main` branch of the remote repository named `origin`.

### Triggering the CI Pipeline

Once the changes are pushed to the remote repository, the CI pipeline can be triggered automatically. This is typically configured using a CI/CD service like GitHub Actions, GitLab CI, or Jenkins.

#### Example: GitHub Actions

Here’s an example of how you might configure a GitHub Actions workflow to trigger a CI pipeline:

```yaml
name: CI Pipeline

on:
  push:
    branches:
      - main

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v2

    - name: Set up Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '14'

    - name: Install dependencies
      run: npm install

    - name: Run tests
      run: npm test

    - name: Deploy to ArgoCD
      run: |
        kubectl apply -f ./k8s/deployment.yaml
        argocd app sync my-app
```

**Explanation:**
- `on: push`: Specifies that the workflow should run on pushes to the `main` branch.
- `jobs.build`: Defines the job to be executed.
- `steps`: Lists the steps to be performed in the job.
  - `actions/checkout@v2`: Checks out the code from the repository.
  - `actions/setup-node@v2`: Sets up Node.js environment.
  - `npm install`: Installs project dependencies.
  - `npm test`: Runs the tests.
  - `kubectl apply -f ./k8s/deployment.yaml`: Applies the Kubernetes deployment configuration.
  - `argocd app sync my-app`: Syncs the ArgoCD application.

### GitOps Pipeline with ArgoCD

ArgoCD manages the deployment of Kubernetes applications based on the GitOps principles. Once the CI pipeline completes successfully, the GitOps pipeline will be triggered to update the application in the Kubernetes cluster.

#### Example: ArgoCD Application Configuration

Here’s an example of an ArgoCD application configuration:

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
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: my-app
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

**Explanation:**
- `metadata.name`: Name of the ArgoCD application.
- `spec.project`: Project in which the application resides.
- `spec.source.repoURL`: URL of the Git repository.
- `spec.source.targetRevision`: Revision to deploy (typically `HEAD` for the latest).
- `spec.source.path`: Path within the repository containing the Kubernetes manifests.
- `spec.destination.server`: Server URL of the Kubernetes cluster.
- `spec.destination.namespace`: Namespace in which the application will be deployed.
- `spec.syncPolicy`: Policy for automatic synchronization.
  - `prune`: Prunes resources that are not present in the manifest.
  - `selfHeal`: Automatically heals the application if it diverges from the desired state.
  - `syncOptions`: Additional options for synchronization.

### Real-World Examples

#### Recent Breach Example: CVE-2021-20225

CVE-2021-20225 was a critical vulnerability in ArgoCD that allowed attackers to gain unauthorized access to the Kubernetes cluster. This highlights the importance of securing your GitOps pipeline.

**Detection:**
- Regularly audit your ArgoCD configurations and permissions.
- Monitor for unauthorized access attempts and unusual activity.

**Prevention:**
- Ensure that ArgoCD is updated to the latest version.
- Use RBAC (Role-Based Access Control) to restrict access to sensitive resources.
- Enable TLS for secure communication between ArgoCD and the Kubernetes API server.

### How to Prevent / Defend

#### Secure Code Fix

**Vulnerable Pattern:**

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
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: my-app
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
```

**Secure Pattern:**

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
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: my-app
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
  revisionHistoryLimit: 10
  syncWindow:
    type: SyncPeriodic
    value: 1h
```

**Explanation:**
- `revisionHistoryLimit`: Limits the number of revisions stored in the ArgoCD application history.
- `syncWindow`: Controls the frequency of synchronization.

#### Configuration Hardening

**Example: Enabling TLS for ArgoCD**

```yaml
apiVersion: v1
kind: Secret

---
<!-- nav -->
[[04-Introduction to CICD Pipelines and GitOps|Introduction to CICD Pipelines and GitOps]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Create CI Pipeline that triggers GitOps Pipeline/00-Overview|Overview]] | [[06-Handling Environment Variables|Handling Environment Variables]]
