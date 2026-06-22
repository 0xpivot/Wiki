---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Introduction to App Release Pipeline with ArgoCD

In the realm of DevSecOps, one of the most critical aspects is ensuring that applications are deployed securely and efficiently. A key tool in achieving this is ArgoCD, an open-source declarative continuous delivery tool for Kubernetes. In this chapter, we will delve deep into how to set up an app release pipeline using ArgoCD, focusing on managing microservices applications with Kustomize.

### What is ArgoCD?

ArgoCD is a declarative continuous delivery tool for Kubernetes. It allows you to manage your applications in a GitOps manner, meaning that the desired state of your applications is stored in a Git repository. ArgoCD continuously compares the desired state (stored in Git) with the actual state (running in your Kubernetes cluster) and applies any necessary changes to bring them into alignment.

#### Why Use ArgoCD?

- **Declarative**: Define your application's desired state in a declarative way, making it easier to understand and maintain.
- **GitOps**: Store your application's desired state in a Git repository, enabling version control and collaboration.
- **Continuous Delivery**: Automatically deploy changes to your Kubernetes cluster when they are committed to the Git repository.
- **Rollback**: Easily roll back to previous versions of your application if something goes wrong.
- **Multi-cluster Management**: Manage multiple Kubernetes clusters from a single dashboard.

### What is Kustomize?

Kustomize is a tool for customizing Kubernetes manifests. It allows you to define a base set of resources and then customize them for different environments (e.g., development, staging, production) without duplicating code. This makes it easier to manage complex applications with many different configurations.

#### Why Use Kustomize?

- **Modularity**: Define a base set of resources and then customize them for different environments.
- **Reusability**: Avoid duplicating code by using overlays to modify base resources.
- **Version Control**: Store your customized resources in a Git repository, enabling version control and collaboration.
- **Ease of Maintenance**: Simplify the management of complex applications with many different configurations.

### Setting Up the Environment

Before we dive into the specifics of setting up an app release pipeline with ArgoCD and Kustomize, let's ensure that we have the necessary tools installed:

1. **Kubernetes Cluster**: Ensure you have access to a Kubernetes cluster. You can use a managed service like Google Kubernetes Engine (GKE), Amazon EKS, or Azure AKS, or you can set up a local cluster using Minikube.
2. **kubectl**: Install `kubectl`, the command-line tool for interacting with Kubernetes clusters.
3. **ArgoCD**: Install ArgoCD on your Kubernetes cluster. You can follow the official documentation to install it.
4. **Kustomize**: Install Kustomize. You can download it from the official GitHub repository or use a package manager like Homebrew on macOS.

### Creating the GitOps Repository

The first step in setting up an app release pipeline with ArgoCD is to create a GitOps repository. This repository will store the desired state of your applications.

```bash
mkdir gitops-repo
cd gitops-repo
git init
```

Next, we will create a directory structure for our microservices application. For this example, let's assume we have a simple microservices application with three services: `frontend`, `backend`, and `database`.

```bash
mkdir -p apps/frontend apps/backend apps/database
```

### Defining the Base Resources

We will start by defining the base resources for each service. These resources will be stored in the `apps` directory.

#### Frontend Service

Create a `deployment.yaml` file in the `apps/frontend` directory:

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
        image: myregistry/frontend:latest
        ports:
        - containerPort: 80
```

Create a `service.yaml` file in the `apps/frontend` directory:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: frontend
spec:
  selector:
    app: frontend
  ports:
    - protocol: TCP
      port: 80
      targetPort: 80
  type: LoadBalancer
```

#### Backend Service

Create a `deployment.yaml` file in the `apps/backend` directory:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  replicas: 3
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
        image: myregistry/backend:latest
        ports:
        - containerPort: 8080
```

Create a `service.yaml` file in the `apps/backend` directory:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: backend
spec:
  selector:
    app: backend
  ports:
    - protocol: TCP
      port: 8080
      targetPort: 8080
  type: ClusterIP
```

#### Database Service

Create a `deployment.yaml` file in the `apps/database` directory:

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
        image: postgres:latest
        ports:
        - containerPort: 5432
```

Create a `service.yaml` file in the `apps/database` directory:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: database
spec:
  selector:
    app: database
  ports:
    - protocol: TCP
      port: 5432
      targetPort: 5432
  type: ClusterIP
```

### Customizing the Resources with Kustomize

Now that we have defined the base resources, we will use Kustomize to customize them for different environments. Create a `kustomization.yaml` file in each service directory.

#### Frontend Service

Create a `kustomization.yaml` file in the `apps/frontend` directory:

```yaml
resources:
- deployment.yaml
- service.yaml
```

#### Backend Service

Create a `kustomization.yaml` file in the `apps/backend` directory:

```yaml
resources:
- deployment.yaml
- service.yaml
```

#### Database Service

Create a `kustomization.yaml` file in the `apps/database` directory:

```yaml
resources:
- deployment.yaml
- service.yaml
```

### Creating Overlays for Different Environments

To customize the resources for different environments, we will create overlays. For this example, let's create overlays for the `development` and `production` environments.

#### Development Overlay

Create a `dev` directory in each service directory and create a `kustomization.yaml` file in each `dev` directory.

##### Frontend Service

Create a `kustomization.yaml` file in the `apps/frontend/dev` directory:

```yaml
resources:
- ../../deployment.yaml
- ../../service.yaml
patchesStrategicMerge:
- patch.yaml
```

Create a `patch.yaml` file in the `apps/frontend/dev` directory:

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
          value: development
```

##### Backend Service

Create a `kustomization.yaml` file in the `apps/backend/dev` directory:

```yaml
resources:
- ../../deployment.yaml
- ../../service.yaml
patchesStrategicMerge:
- patch.yaml
```

Create a `patch.yaml` file in the `apps/backend/dev` directory:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  template:
    spec:
      containers:
      - name: backend
        env:
        - name: ENVIRONMENT
          value: development
```

##### Database Service

Create a `kustomization.yaml` file in the `apps/database/dev` directory:

```yaml
resources:
- ../../deployment.yaml
- ../../service.yaml
patchesStrategicMerge:
- patch.yaml
```

Create a `patch.yaml` file in the `apps/database/dev` directory:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: database
spec:
  template:
    spec:
      containers:
      - name: database
        env:
        - name: ENVIRONMENT
          value: development
```

#### Production Overlay

Create a `prod` directory in each service directory and create a `kustomization.yaml` file in each `prod` directory.

##### Frontend Service

Create a `kustomization.yaml` file in the `apps/frontend/prod` directory:

```yaml
resources:
- ../../deployment.yaml
- ../../service.yaml
patchesStrategicMerge:
- patch.yaml
```

Create a `patch.yaml` file in the `apps/frontend/prod` directory:

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
          value: production
```

##### Backend Service

Create a `kustomization.yaml` file in the `apps/backend/prod` directory:

```yaml
resources:
- ../../deployment.yaml
- ../../service.yaml
patchesStrategicMerge:
- patch.yaml
```

Create a `patch.yaml` file in the `apps/backend/prod` directory:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend
spec:
  template:
    spec:
      containers:
      - name: backend
        env:
        - name: ENVIRONMENT
          value: production
```

##### Database Service

Create a `kustomization.yaml` file in the `apps/database/prod` directory:

```yaml
resources:
- ../../deployment.yaml
- ../../service.yaml
patchesStrategicMerge:
- patch.yaml
```

Create a `patch.yaml` file in the `apps/database/prod` directory:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: database
spec:
  template:
    spec:
      containers:
      - name: database
        env:
        - name: ENVIRONMENT
          value: production
```

### Pushing Changes to the GitOps Repository

Now that we have defined the base resources and created overlays for different environments, we can push these changes to the GitOps repository.

```bash
git add .
git commit -m "Initial commit"
git push origin master
```

### Connecting to ArgoCD

To see the changes in action, we need to connect to ArgoCD and configure it to watch the GitOps repository.

#### Logging into ArgoCD

First, log into ArgoCD using the `argocd` CLI:

```bash
argocd login <ARGOCD_SERVER>
```

Replace `<ARGOCD_SERVER>` with the address of your ArgoCD server.

#### Adding the GitOps Repository

Add the GitOps repository to ArgoCD:

```bash
argocd repo add <GITOPS_REPO_URL> --name gitops-repo
```

Replace `<GITOPS_REPO_URL>` with the URL of your GitOps repository.

#### Creating an Application

Create an application in ArgoCD that watches the GitOps repository:

```bash
argocd app create myapp --repo <GITOPS_REPO_URL> --path apps --dest-server https://<KUBERNETES_API_SERVER> --dest-namespace default
```

Replace `<GITOPS_REPO_URL>` with the URL of your GitOps repository and `<KUBERNETES_API_SERVER>` with the address of your Kubernetes API server.

### Monitoring the Application

Once the application is created, ArgoCD will continuously compare the desired state (stored in the GitOps repository) with the actual state (running in your Kubernetes cluster) and apply any necessary changes to bring them into alignment.

To monitor the application, you can use the ArgoCD dashboard. To access the dashboard, you need to port forward the ArgoCD server:

```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```

Open a web browser and navigate to `http://localhost:8080`. Log in using the credentials you provided when installing ArgoCD.

### Real-World Examples and Recent CVEs

To illustrate the importance of using ArgoCD and Kustomize, let's look at some real-world examples and recent CVEs.

#### Example: CVE-2021-25741

CVE-2021-25741 is a vulnerability in Kubernetes that allows an attacker to escalate privileges by manipulating the `PodSecurityPolicy` resource. This vulnerability highlights the importance of using a declarative approach to manage your Kubernetes resources, as it ensures that the desired state is always enforced.

By using ArgoCD and Kustomize, you can define your `PodSecurityPolicy` resources in a declarative way and ensure that they are always applied correctly. This reduces the risk of misconfigurations and vulnerabilities.

#### Example: CVE-2021-25742

CVE-2021-25742 is another vulnerability in Kubernetes that allows an attacker to bypass the `PodSecurityPolicy` resource. This vulnerability highlights the importance of using a GitOps approach to manage your Kubernetes resources, as it ensures that the desired state is always stored in a Git repository and can be audited and reviewed.

By using ArgoCD and Kustomize, you can store your `PodSecurityPolicy` resources in a Git repository and ensure that they are always applied correctly. This reduces the risk of misconfigurations and vulnerabilities.

### How to Prevent / Defend

To prevent and defend against vulnerabilities in your Kubernetes cluster, you should follow these best practices:

1. **Use a Declarative Approach**: Define your Kubernetes resources in a declarative way using tools like ArgoCD and Kustomize. This ensures that the desired state is always enforced.
2. **Use a GitOps Approach**: Store your Kubernetes resources in a Git repository and use tools like ArgoCD to manage them. This ensures that the desired state is always stored in a Git repository and can be audited and reviewed.
3. **Audit and Review**: Regularly audit and review your Kubernetes resources to ensure that they are configured correctly and securely.
4. **Patch and Update**: Regularly patch and update your Kubernetes cluster to ensure that it is protected against known vulnerabilities.
5. **Use Network Policies**: Use network policies to restrict traffic between pods and ensure that only authorized traffic is allowed.
6. **Use RBAC**: Use Role-Based Access Control (RBAC) to restrict access to your Kubernetes resources and ensure that only authorized users can make changes.

### Conclusion

In this chapter, we have explored how to set up an app release pipeline using ArgoCD and Kustomize. We have covered the basics of ArgoCD and Kustomize, how to create a GitOps repository, how to define base resources, how to customize resources with Kustomize, how to create overlays for different environments, how to push changes to the GitOps repository, how to connect to ArgoCD, how to monitor the application, and how to prevent and defend against vulnerabilities.

By following these best practices, you can ensure that your Kubernetes cluster is deployed securely and efficiently.

---
<!-- nav -->
[[02-Introduction to App Release Pipeline with ArgoCD Using Kustomize|Introduction to App Release Pipeline with ArgoCD Using Kustomize]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/K8s Manifests for Microservices App using Kustomize/00-Overview|Overview]] | [[04-Introduction to Application Release Pipeline with ArgoCD and Kustomize|Introduction to Application Release Pipeline with ArgoCD and Kustomize]]
