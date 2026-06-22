---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Creating the GitOps Pipeline

Now that we have our environment set up, let's create the GitOps pipeline to update the Kustomization file.

### Step 1: Define the Kustomization File

Create a `kustomization.yaml` file in the `manifests` directory:

```yaml
resources:
- example-configmap.yaml
```

Commit the changes to the repository:

```sh
git add .
git commit -m "Add kustomization file"
git push origin main
```

### Step 2: Configure ArgoCD Application

Configure an ArgoCD application to sync the `kustomization.yaml` file:

```sh
argocd app create my-app \
  --repo https://github.com/yourusername/your-repo.git \
  --path manifests \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace default
```

### Step 3: Update the Hardcoded Value Using YQ

We will use YQ to update the hardcoded value in the `example-configmap.yaml` file. First, let's install YQ in a Docker container.

#### Dockerfile

Create a `Dockerfile` to install YQ and Git:

```dockerfile
FROM gitlab/git-runner:alpine

RUN apk add --no-cache yq
```

Build the Docker image:

```sh
docker build -t my-gitops-pipeline .
```

#### GitOps Pipeline Job

Create a GitOps pipeline job to update the hardcoded value using YQ:

```sh
#!/bin/sh

# Update the hardcoded value in the YAML file
yq e '.data.value = "updated-value"' manifests/example-configmap.yaml > manifests/example-configmap.yaml.tmp
mv manifests/example-configmap.yaml.tmp manifests/example-configmap.yaml

# Commit and push the changes to the repository
git add .
git commit -m "Update hardcoded value"
git push origin main
```

Run the pipeline job using the Docker container:

```sh
docker run --rm -v $(pwd):/workspace -w /workspace my-gitops-pipeline
```

### Step 4: Verify the Changes

Verify that the changes have been applied to the ArgoCD application:

```sh
argocd app get my-app
```

### Step 5: Automate the Pipeline

To automate the pipeline, you can integrate it with a CI/CD system like GitLab CI/CD. Here is an example `.gitlab-ci.yml` file:

```yaml
stages:
  - deploy

deploy_dev:
  stage: deploy
  script:
    - docker run --rm -v $(pwd):/workspace -w /workspace my-gitops-pipeline
```

Commit the `.gitlab-ci.yml` file to the repository:

```sh
git add .gitlab-ci.yml
git commit -m "Add GitLab CI/CD pipeline"
git push origin main
```

---
<!-- nav -->
[[19-Creating a GitOps Pipeline with ArgoCD|Creating a GitOps Pipeline with ArgoCD]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Create GitOps Pipeline to update Kustomization File/00-Overview|Overview]] | [[21-Detailed Workflow of the Application Release Pipeline|Detailed Workflow of the Application Release Pipeline]]
