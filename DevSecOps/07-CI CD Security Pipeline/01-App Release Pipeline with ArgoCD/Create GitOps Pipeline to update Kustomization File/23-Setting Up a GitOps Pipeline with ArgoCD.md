---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Setting Up a GitOps Pipeline with ArgoCD

To set up a GitOps pipeline using ArgoCD, we need to follow several steps:

1. **Configure the Git Repository**: Set up a Git repository to store the desired state of your Kubernetes resources.
2. **Define the Application Manifests**: Write Kubernetes manifests (YAML files) that describe the desired state of your applications.
3. **Set Up ArgoCD**: Install and configure ArgoCD to watch the Git repository and synchronize the desired state with the live environment.
4. **Create CI/CD Pipelines**: Automate the process of updating the Git repository and triggering ArgoCD to apply the changes.

### Step 1: Configure the Git Repository

First, we need to set up a Git repository to store our Kubernetes manifests. This repository will act as the single source of truth for our infrastructure.

```bash
git init my-gitops-repo
cd my-gitops-repo
```

Next, we need to create a directory structure for our manifests. A common structure might look like this:

```
my-gitops-repo/
├── environments/
│   ├── dev/
│   │   ├── kustomization.yaml
│   │   └── ...
│   └── prod/
│       ├── kustomization.yaml
│       └── ...
└── base/
    ├── deployment.yaml
    ├── service.yaml
    └── ...
```

### Step 2: Define the Application Manifests

We need to define the Kubernetes manifests that describe our applications. For example, let's create a `deployment.yaml` and a `service.yaml` in the `base` directory.

```yaml
# base/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ad-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ad-service
  template:
    metadata:
      labels:
        app: ad-service
    spec:
      containers:
      - name: ad-service
        image: myregistry/ad-service:0.8.1
        ports:
        - containerPort: 8080
```

```yaml
# base/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: ad-service
spec:
  selector:
    app: ad-service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
```

### Step 3: Set Up ArgoCD

Now, we need to install and configure ArgoCD. We can use Helm to install ArgoCD in our Kubernetes cluster.

```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
helm install argocd argo/argo-cd --namespace argocd --create-namespace
```

Once ArgoCD is installed, we need to configure it to watch our Git repository and synchronize the desired state with the live environment.

```bash
kubectl config use-context <your-cluster-context>
argocd login --username admin --password <admin-password> --insecure
argocd repo add <your-git-repo-url>
argocd app create ad-service --repo <your-git-repo-url> --path environments/dev --dest-server <your-kubernetes-api-server> --dest-namespace default
```

### Step 4: Create CI/CD Pipelines

To fully automate the process, we need to create CI/CD pipelines that update the Git repository and trigger ArgoCD to apply the changes. We will use GitLab CI/CD as an example.

#### Creating the `.gitlab-ci.yml` File

In the root of our Git repository, we need to create a `.gitlab-ci.yml` file that defines our CI/CD pipeline.

```yaml
stages:
  - deploy_dev

deploy_dev:
  stage: deploy_dev
  script:
    - echo "Updating image tag in kustomization.yaml"
    - sed -i 's/image: myregistry\/ad-service:[^"]*/image: myregistry\/ad-service:0.9.1/' environments/dev/kustomization.yaml
    - git add .
    - git commit -m "Update ad-service image tag to 0.9.1"
    - git push origin HEAD
```

This pipeline does the following:

1. Updates the image tag in the `kustomization.yaml` file.
2. Commits the changes to the Git repository.
3. Pushes the changes to the remote repository.

### Full Example of a GitOps Pipeline

Let's walk through a complete example of a GitOps pipeline using ArgoCD and GitLab CI/CD.

#### Initial Setup

1. **Initialize the Git Repository**:

```bash
mkdir my-gitops-repo
cd my-gitops-repo
git init
```

2. **Create Directory Structure**:

```bash
mkdir -p environments/dev
mkdir base
```

3. **Add Kubernetes Manifests**:

```yaml
# base/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ad-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ad-service
  template:
    metadata:
      labels:
        app: ad-service
    spec:
      containers:
      - name: ad-service
        image: myregistry/ad-service:0.8.1
        ports:
        - containerPort: 8080
```

```yaml
# base/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: ad-service
spec:
  selector:
    app: ad-service
  ports:
  - protocol: TCP
    port: 80
    targetPort: 8080
```

4. **Create Kustomization File**:

```yaml
# environments/dev/kustomization.yaml
resources:
- ../../base/deployment.yaml
- ../../base/service.yaml
images:
- name: myregistry/ad-service
  newName: myregistry/ad-service
  newTag: 0.8.1
```

5. **Commit and Push Changes**:

```bash
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin <your-git-repo-url>
git push -u origin main
```

#### Install and Configure ArgoCD

1. **Install ArgoCD**:

```bash
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
helm install argocd argo/argo-cd --namespace argocd --create-namespace
```

2. **Login to ArgoCD**:

```bash
kubectl config use-context <your-cluster-context>
argocd login --username admin --password <admin-password> --insecure
```

3. **Add Git Repository**:

```bash
argocd repo add <your-git-repo-url>
```

4. **Create Application**:

```bash
argocd app create ad-service --repo <your-git-repo-url> --path environments/dev --dest-server <your-kubernetes-api-server> --dest-namespace default
```

#### Create CI/CD Pipeline

1. **Create `.gitlab-ci.yml` File**:

```yaml
stages:
  - deploy_dev

deploy_dev:
  stage: deploy_dev
  script:
    - echo "Updating image tag in kustomization.yaml"
    - sed -i 's/image: myregistry\/ad-service:[^"]*/image: myregistry\/ad-service:0.9.1/' environments/dev/kustomization.yaml
    - git add .
    - git commit -m "Update ad-service image tag to 0.9.1"
    - git push origin HEAD
```

2. **Commit and Push `.gitlab-ci.yml` File**:

```bash
git add .gitlab-ci.yml
git commit -m "Add GitLab CI/CD pipeline"
git push
```

### How to Prevent / Defend

#### Detection

To detect issues in your GitOps pipeline, you can use tools like:

- **ArgoCD Sync Health Check**: Regularly check the health of your ArgoCD application to ensure that the desired state matches the actual state.
- **CI/CD Pipeline Logs**: Monitor the logs of your CI/CD pipeline to detect any failures or errors.

#### Prevention

To prevent issues in your GitOps pipeline, you can implement the following best practices:

- **Automated Testing**: Ensure that your CI/CD pipeline includes automated testing to catch issues before they are deployed.
- **Code Reviews**: Implement code reviews to ensure that changes to your Git repository are reviewed and approved by other team members.
- **Access Controls**: Use access controls to restrict who can make changes to your Git repository and who can trigger deployments.

#### Secure Coding Fixes

Here is an example of a vulnerable vs. secure version of the `kustomization.yaml` file:

**Vulnerable Version**:

```yaml
# environments/dev/kustomization.yaml
resources:
- ../../base/deployment.yaml
- ../../base/service.yaml
images:
- name: myregistry/ad-service
  newName: myregistry/ad-service
  newTag: 0.8.1
```

**Secure Version**:

```yaml
# environments/dev/kustomization.yaml
resources:
- ../../base/deployment.yaml
- ../../base/service.yaml
images:
- name: myregistry/ad-service
  newName: myregistry/ad-service
  newTag: $(IMAGE_TAG)
```

In the secure version, we use a variable `$(IMAGE_TAG)` to dynamically set the image tag. This allows us to update the image tag in a controlled manner without modifying the `kustomization.yaml` file directly.

### Conclusion

By setting up a GitOps pipeline using ArgoCD and GitLab CI/CD, you can fully automate the process of deploying and managing your Kubernetes applications. This ensures that your infrastructure is always in a known good state and can be easily audited and rolled back if necessary. With the right tools and best practices, you can build a robust and reliable GitOps pipeline that helps you deliver high-quality applications to your users.

### Practice Labs

For hands-on practice with GitOps and ArgoCD, consider the following labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security and GitOps principles.
- **OWASP WrongSecrets**: A series of challenges that cover various aspects of DevSecOps, including GitOps.
- **Pacu**: A collection of cloud security tools that includes exercises for GitOps and ArgoCD.

These labs provide practical experience with the concepts covered in this chapter and help you build a deeper understanding of GitOps and ArgoCD.

---
<!-- nav -->
[[24-Setting Up Git Configuration for Commit Messages|Setting Up Git Configuration for Commit Messages]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Create GitOps Pipeline to update Kustomization File/00-Overview|Overview]] | [[26-Setting Up the Environment|Setting Up the Environment]]
