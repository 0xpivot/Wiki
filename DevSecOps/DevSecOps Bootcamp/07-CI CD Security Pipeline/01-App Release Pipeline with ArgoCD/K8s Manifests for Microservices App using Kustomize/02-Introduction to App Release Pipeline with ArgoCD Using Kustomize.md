---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Introduction to App Release Pipeline with ArgoCD Using Kustomize

In this section, we will delve into the process of setting up an application release pipeline using ArgoCD and Kustomize for managing Kubernetes manifests. This approach allows us to maintain a GitOps workflow, ensuring that our infrastructure and applications are version-controlled and declaratively managed.

### What is GitOps?

GitOps is a set of practices that uses Git as a single source of truth for all infrastructure and application configurations. This means that all changes to the system are made via Git pull requests, allowing for version control, collaboration, and auditability. GitOps is particularly useful in DevSecOps environments where continuous integration and delivery (CI/CD) pipelines are essential.

### What is ArgoCD?

ArgoCD is a declarative, extensible, and easy-to-use continuous delivery tool for Kubernetes. It provides a GitOps operator that syncs the desired state of your Kubernetes cluster with the actual state, ensuring that the cluster remains in the desired state at all times. ArgoCD supports various features such as automated rollouts, rollbacks, and synchronization of resources.

### What is Kustomize?

Kustomize is a tool for customizing Kubernetes YAML files. It allows you to create a base set of YAML files and then apply customizations on top of them. This makes it easier to manage different environments (development, staging, production) without duplicating code. Kustomize works by applying patches and overlays to the base YAML files.

### Why Use ArgoCD and Kustomize Together?

Using ArgoCD and Kustomize together provides a powerful combination for managing Kubernetes applications:

- **Declarative Management**: Both tools enforce a declarative approach to managing Kubernetes resources.
- **Version Control**: All changes are tracked in Git, providing a clear history and audit trail.
- **Environment Customization**: Kustomize allows you to customize your application for different environments without duplicating code.
- **Automated Syncing**: ArgoCD automatically syncs the desired state with the actual state of the cluster.

### Setting Up the Environment

To get started, we need to set up our environment with the necessary tools and repositories.

#### Prerequisites

- A Kubernetes cluster (e.g., Minikube, GKE, EKS)
- `kubectl` installed and configured to access the cluster
- `git` installed
- `argocd` CLI installed
- `kustomize` installed

#### Cloning the Repository

First, we need to clone the GitOps repository where our Kubernetes manifests will reside.

```bash
git clone https://github.com/your-repo.git
cd your-repo
```

### Adding Kubernetes Manifest Files

The first step is to add the Kubernetes manifest files to the GitOps repository. These files will define the deployments and services for our microservices application.

#### Directory Structure

We will organize our repository using the following directory structure:

```
your-repo/
├── base/
│   ├── deployment.yaml
│   └── service.yaml
└── overlays/
    ├── development/
    │   ├── kustomization.yaml
    │   └── patch.yaml
    └── production/
        ├── kustomization.yaml
        └── patch.yaml
```

#### Base Configuration

In the `base` directory, we will create the basic Kubernetes manifest files.

```yaml
# base/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: myapp
  template:
    metadata:
      labels:
        app: myapp
    spec:
      containers:
      - name: myapp-container
        image: myapp-image:latest
        ports:
        - containerPort: 8080
```

```yaml
# base/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: myapp-service
spec:
  selector:
    app: myapp
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
```

### Using Kustomize for Customization

Next, we will use Kustomize to customize these base configurations for different environments.

#### Development Environment

In the `overlays/development` directory, we will create a `kustomization.yaml` file and a `patch.yaml` file.

```yaml
# overlays/development/kustomization.yaml
resources:
- ../../base/deployment.yaml
- ../../base/service.yaml
patchesStrategicMerge:
- patch.yaml
```

```yaml
# overlays/development/patch.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-deployment
spec:
  template:
    spec:
      containers:
      - name: myapp-container
        image: myapp-image:dev
```

#### Production Environment

Similarly, in the `overlays/production` directory, we will create a `kustomization.yaml` file and a `patch.yaml` file.

```yaml
# overlays/production/kustomization.yaml
resources:
- ../../base/deployment.yaml
- ../../base/service.yaml
patchesStrategicMerge:
- patch.yaml
```

```yaml
# overlays//production/patch.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-deployment
spec:
  template:
    spec:
      containers:
      - name: myapp-container
        image: myapp-image:prod
```

### Committing Changes to Git

After creating the necessary files, we need to commit these changes to the Git repository.

```bash
git add .
git commit -m "Add base and overlay configurations"
git push origin main
```

### Configuring ArgoCD

Now that our repository is set up, we need to configure ArgoCD to sync the desired state with the actual state of the cluster.

#### Installing ArgoCD

If ArgoCD is not already installed in your cluster, you can install it using the following command:

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

#### Logging into ArgoCD

Once ArgoCD is installed, you can log in using the following command:

```bash
argocd login localhost:2746 --username admin --password $(kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d)
```

#### Creating an Application

Next, we need to create an application in ArgoCD that points to our GitOps repository.

```bash
argocd app create myapp \
  --repo https://github.com/your-repo.git \
  --path overlays/development \
  --dest-server https://kubernetes.default.svc \
  --dest-namespace default
```

### Monitoring the Application

ArgoCD will automatically sync the desired state with the actual state of the cluster. You can monitor the status of the application using the following command:

```bash
argocd app get myapp
```

### Handling Rollouts and Rollbacks

ArgoCD supports automated rollouts and rollbacks. You can trigger a rollout by updating the Git repository and pushing the changes. ArgoCD will automatically detect the changes and apply them to the cluster.

To rollback to a previous version, you can use the following command:

```bash
argocd app rollback myapp --revision <revision-number>
```

### How to Prevent / Defend

#### Detection

To ensure that your GitOps workflow is secure, you should implement the following detection mechanisms:

- **Audit Logs**: Enable audit logs in both Git and ArgoCD to track all changes and actions.
- **Webhooks**: Set up webhooks in your Git repository to trigger notifications or actions when changes are pushed.

#### Prevention

To prevent unauthorized changes and ensure the integrity of your GitOps workflow, you should implement the following prevention mechanisms:

- **Access Controls**: Restrict access to the Git repository and ArgoCD dashboard to only authorized users.
- **Branch Protection**: Use branch protection rules in your Git repository to prevent direct pushes to critical branches.
- **Code Reviews**: Implement a code review process for all changes to the Git repository.

#### Secure Coding Fixes

Here is an example of a vulnerable configuration and its secure counterpart:

**Vulnerable Configuration**

```yaml
# overlays/development/patch.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-deployment
spec:
  template:
    spec:
      containers:
      - name: myapp-container
        image: myapp-image:dev
        securityContext:
          runAsUser: 0
```

**Secure Configuration**

```yaml
# overlays/development/patch.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: myapp-deployment
spec:
  template:
    spec:
      containers:
      - name: myapp-container
        image: myapp-image:dev
        securityContext:
          runAsUser: 1000
```

### Real-World Examples

#### Recent CVEs and Breaches

One recent example of a breach related to Kubernetes misconfiguration is the **CVE-2021-25741**, which affected the Kubernetes API server. This vulnerability allowed attackers to bypass authentication and gain unauthorized access to the cluster. To prevent such vulnerabilities, it is crucial to follow best practices for securing your Kubernetes cluster and GitOps workflow.

### Conclusion

By using ArgoCD and Kustomize together, you can effectively manage your Kubernetes applications and maintain a GitOps workflow. This approach ensures that your infrastructure and applications are version-controlled, declaratively managed, and easily customizable for different environments. Additionally, implementing proper detection and prevention mechanisms will help you secure your GitOps workflow and prevent unauthorized changes.

### Practice Labs

For hands-on practice with ArgoCD and Kustomize, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs for learning web security concepts.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **Kubernetes Goat**: A vulnerable Kubernetes cluster for practicing security and hardening techniques.

These labs provide practical experience in setting up and managing Kubernetes applications using GitOps principles.

---
<!-- nav -->
[[01-Introduction to App Release Pipeline with ArgoCD Using Kustomize Part 1|Introduction to App Release Pipeline with ArgoCD Using Kustomize Part 1]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/K8s Manifests for Microservices App using Kustomize/00-Overview|Overview]] | [[03-Introduction to App Release Pipeline with ArgoCD|Introduction to App Release Pipeline with ArgoCD]]
