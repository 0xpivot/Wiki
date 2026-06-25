---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Setting Up the Project Structure

To begin, let's set up the project structure for our microservices application. We'll use Kustomize to organize our Kubernetes manifests and then integrate with ArgoCD for automated deployments.

### Creating the Base Folder

First, create a `base` folder in your project directory. This folder will contain the base Kubernetes manifests for your microservices.

```bash
mkdir -p my-project/base
cd my-project/base
```

### Adding Base Manifests

Next, add the base Kubernetes manifests for each microservice. These manifests should be generic and not environment-specific. For example, let's assume we have three microservices: `frontend`, `backend`, and `database`.

#### Example Manifests

Here are the base manifests for each microservice:

**frontend-deployment.yaml**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: frontend
  template:
    metadata:
      labels:
        app: frontend
    spec:
      containers:
      - name: frontend
        image: my-registry/frontend:latest
        ports:
        - containerPort: 80
```

**backend-deployment.yaml**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: backend
  template:
    metadata:
      labels:
        app: backend
    spec:
      containers:
      - name: backend
        image: my-registry/backend:latest
        ports:
        - containerPort: 8080
```

**database-deployment.yaml**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: database
spec:
  replicas: 1
  selector:
    matchLabels:
      app: database
  template:
    metadata:
      labels:
        app: database
    spec:
      containers:
      - name: database
        image: my-registry/database:latest
        ports:
        - containerPort: 5432
```

### Creating Overlays for Different Environments

Now, let's create overlays for different environments (dev, staging, prod).

#### Creating the Overlay Folders

Create separate folders for each environment within the `my-project` directory.

```bash
mkdir -p my-project/dev my-project/staging my-project/prod
```

#### Adding Customization Files

In each overlay folder, add customization files that modify the base manifests according to the environment requirements.

**Example Customization File for Dev Environment**

**my-project/dev/kustomization.yaml**
```yaml
resources:
- ../../base/frontend-deployment.yaml
- ../../base/backend-deployment.yaml
- ../../base/database-deployment.yaml

patchesStrategicMerge:
- dev-patch.yaml
```

**my-project/dev/dev-patch.yaml**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend
spec:
  template:
    spec:
      containers:
      - name: frontend
        env:
        - name: ENVIRONMENT
          value: "dev"
```

### Integrating with ArgoCD

Now that we have our project structure set up with Kustomize, let's integrate it with ArgoCD for automated deployments.

#### Installing ArgoCD

First, install ArgoCD in your Kubernetes cluster. You can use the following commands to install ArgoCD:

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

#### Configuring ArgoCD

Once ArgoCD is installed, configure it to sync with your Git repository containing the Kustomize manifests.

1. **Login to ArgoCD**:
   ```bash
   kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 --decode; echo
   ```

2. **Add Application to ArgoCD**:
   ```bash
   argocd app create my-app --repo https://github.com/my-repo/my-project.git --path my-project --dest-server https://kubernetes.default.svc --dest-namespace default
   ```

### Example of Full Deployment Process

Let's walk through a complete example of deploying the microservices application using Kustomize and ArgoCD.

#### Step 1: Commit Changes to Git Repository

Commit the changes to your Git repository.

```bash
git add .
git commit -m "Initial commit of Kustomize manifests"
git push origin main
```

#### Step 2: Sync with ArgoCD

Sync the changes with ArgoCD.

```bash
argocd app sync my-app
```

### Monitoring and Troubleshooting

Monitor the deployment status using ArgoCD.

```bash
argocd app get my-app
```

If there are issues, troubleshoot by checking the logs and events in the Kubernetes cluster.

```bash
kubectl get pods
kubectl describe pod <pod-name>
```

### Real-World Examples and Recent CVEs

Recent CVEs and breaches often highlight the importance of proper configuration management and automated deployment pipelines. For instance, the **CVE-2021-20225** in Kubernetes highlighted the risks associated with misconfigured RBAC permissions, which could be mitigated by using tools like Kustomize and ArgoCD to ensure consistent and secure configurations.

### How to Prevent / Defend

#### Secure Configuration Management

Ensure that your Kustomize manifests and ArgoCD configurations are secure by following best practices:

- **Use Role-Based Access Control (RBAC)**: Limit access to sensitive resources.
- **Encrypt Secrets**: Use Kubernetes secrets and encryption at rest.
- **Regular Audits**: Perform regular audits of your manifests and configurations.

#### Example of Vulnerable vs. Secure Code

**Vulnerable Code**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: vulnerable-pod
spec:
  containers:
  - name: vulnerable-container
    image: my-registry/vulnerable-image:latest
    ports:
    - containerPort: 80
```

**Secure Code**
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  containers:
  - name: secure-container
    image: my-registry/secure-image:latest
    ports:
    - containerPort: 80
    securityContext:
      runAsUser: 1000
      allowPrivilegeEscalation: false
```

### Conclusion

Using Kustomize and ArgoCD together provides a powerful and efficient way to manage and deploy microservices applications. By maintaining a clean and organized project structure, you can ensure consistency across different environments and automate the deployment process with ArgoCD. This approach not only improves efficiency but also enhances security by enforcing best practices and regular audits.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but can provide insights into securing your microservices.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **Kubernetes Goat**: A series of challenges to test your Kubernetes security knowledge.

These labs will help you gain practical experience in setting up and securing your microservices application using Kustomize and ArgoCD.

---
<!-- nav -->
[[12-Setting Up the Ingress Component|Setting Up the Ingress Component]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/K8s Manifests for Microservices App using Kustomize/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/K8s Manifests for Microservices App using Kustomize/14-Practice Questions & Answers|Practice Questions & Answers]]
