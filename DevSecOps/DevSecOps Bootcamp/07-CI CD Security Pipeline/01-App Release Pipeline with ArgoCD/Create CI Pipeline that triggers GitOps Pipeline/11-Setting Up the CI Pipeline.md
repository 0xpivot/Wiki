---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Setting Up the CI Pipeline

To create a CI pipeline that triggers a GitOps pipeline, we need to define the necessary steps and configurations. We'll use a combination of GitLab CI/CD and ArgoCD to achieve this.

### Step 1: Define the CI Pipeline

First, we need to define the CI pipeline in a `.gitlab-ci.yml` file. This file will contain the steps required to build and test our microservices.

```yaml
stages:
  - build
  - test
  - deploy

build_microservice:
  stage: build
  script:
    - echo "Building microservice..."
    - docker build -t my-microservice:$CI_COMMIT_SHORT_SHA .
  artifacts:
    paths:
      - target/

test_microservice:
  stage: test
  script:
    - echo "Running tests..."
    - ./run-tests.sh

deploy_microservice:
  stage: deploy
  script:
    - echo "Deploying microservice..."
    - argocd app set my-microservice --param=image=my-microservice:$CI_COMMIT_SHORT_SHA
```

### Explanation of the CI Pipeline

- **Stages**: The pipeline is divided into three stages: `build`, `test`, and `deploy`.
- **Build Stage**: The `build_microservice` job builds the Docker image for the microservice.
- **Test Stage**: The `test_microservice` job runs tests on the microservice.
- **Deploy Stage**: The `deploy_microservice` job deploys the microservice using ArgoCD.

### Step 2: Configure ArgoCD

Next, we need to configure ArgoCD to manage the deployment of our microservices. We'll create an ArgoCD application that watches the Git repository for changes and updates the deployment accordingly.

#### Creating an ArgoCD Application

To create an ArgoCD application, we need to define a manifest file that describes the application. Here's an example manifest file (`argocd-application.yaml`):

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-microservice
spec:
  project: default
  source:
    repoURL: https://github.com/myorg/mymicroservice.git
    targetRevision: HEAD
    path: k8s
  destination:
    server: https://kubernetes.default.svc
    namespace: my-microservice
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
```

### Explanation of the ArgoCD Application

- **Metadata**: The metadata section defines the name of the application.
- **Spec**: The spec section contains the configuration for the application.
  - **Project**: The project in ArgoCD where the application belongs.
  - **Source**: The source section defines the Git repository and the path to the manifests.
  - **Destination**: The destination section defines the Kubernetes cluster and namespace where the application will be deployed.
  - **Sync Policy**: The sync policy section defines how ArgoCD should handle synchronization.

### Step 3: Trigger the GitOps Pipeline

When the CI pipeline completes successfully, it will trigger the GitOps pipeline by updating the ArgoCD application. This ensures that the microservice is deployed to the Kubernetes cluster with the correct configuration.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Create CI Pipeline that triggers GitOps Pipeline/10-Real-World Examples and Recent Breaches|Real-World Examples and Recent Breaches]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Create CI Pipeline that triggers GitOps Pipeline/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/Create CI Pipeline that triggers GitOps Pipeline/12-Conclusion|Conclusion]]
