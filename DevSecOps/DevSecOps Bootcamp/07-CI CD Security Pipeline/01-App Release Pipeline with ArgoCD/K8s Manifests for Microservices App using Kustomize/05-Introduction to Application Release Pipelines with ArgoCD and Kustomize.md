---
course: DevSecOps
topic: App Release Pipeline with ArgoCD
tags: [devsecops]
---

## Introduction to Application Release Pipelines with ArgoCD and Kustomize

In the realm of modern DevSecOps practices, managing the deployment of microservices applications in Kubernetes environments requires a robust and flexible approach. One such approach involves using tools like ArgoCD and Kustomize to streamline the release pipeline and manage Kubernetes manifests efficiently. This chapter will delve deep into the concepts, mechanics, and practical applications of using Kustomize for managing Kubernetes manifests, particularly in the context of deploying microservices applications across multiple namespaces.

### What is Kustomize?

Kustomize is a tool that allows you to customize raw, template-free YAML files for multiple purposes, simply and safely. It is designed to work seamlessly with Kubernetes manifests, enabling developers to manage and deploy applications in a more modular and maintainable way. Kustomize operates by applying a series of transformations to base manifests, allowing for the creation of different configurations for various environments (development, staging, production) without duplicating code.

#### Why Use Kustomize?

The primary advantage of using Kustomize lies in its ability to parameterize and centralize configuration values. Instead of hardcoding values such as image names and versions in every manifest file, Kustomize allows you to define these values in a single place and apply them consistently across all your services. This reduces the risk of errors and makes it easier to manage changes, especially when dealing with multiple microservices.

### Kubernetes Manifests for Microservices

Before diving into the specifics of using Kustomize, it's essential to understand the structure and purpose of Kubernetes manifests. A Kubernetes manifest is a YAML file that describes the desired state of a resource in a Kubernetes cluster. These resources can include deployments, services, config maps, secrets, and more.

#### Example of a Basic Deployment Manifest

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-service
  template:
    metadata:
      labels:
        app: my-service
    spec:
      containers:
      - name: my-service
        image: gcr.io/my-project/my-service:v1.0.0
        ports:
        - containerPort: 8080
```

This manifest defines a deployment named `my-service` with three replicas. Each replica runs a container based on the image `gcr.io/my-project/my-service:v1.0.0`.

### Using Kustomize for Customization

Now that we have a basic understanding of Kubernetes manifests, let's explore how Kustomize can be used to customize these manifests for different environments.

#### Setting Up Kustomize

To get started with Kustomize, you need to create a directory structure that organizes your base manifests and customizations. Here’s an example directory structure:

```
kustomize/
├── base/
│   ├── deployment.yaml
│   └── kustomization.yaml
├── dev/
│   ├── kustomization.yaml
│   └── patches/
│       └── image-patch.yaml
└── prod/
    ├── kustomization.yaml
    └── patches/
        └── image-patch.yaml
```

- **base/**: Contains the base Kubernetes manifests.
- **dev/** and **prod/**: Contain environment-specific customizations.

#### Base Manifests

Let's start by creating a base deployment manifest (`base/deployment.yaml`):

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-service
  template:
    metadata:
      labels:
        app: my-service
    spec:
      containers:
      - name: my-service
        image: gcr.io/my-project/my-service:v1.0.0
        ports:
        - containerPort: 8080
```

Next, create a `kustomization.yaml` file in the `base/` directory to define the base resources:

```yaml
resources:
- deployment.yaml
```

#### Environment-Specific Customizations

Now, let's create customizations for the development and production environments.

##### Development Environment

Create a `kustomization.yaml` file in the `dev/` directory:

```yaml
resources:
- ../../base

patchesStrategicMerge:
- patches/image-patch.yaml
```

And create the `image-patch.yaml` file in the `dev/patches/` directory:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-service
spec:
  template:
    spec:
      containers:
      - name: my-service
        image: gcr.io/my-project/my-service:latest
```

This patch changes the image tag to `latest` for the development environment.

##### Production Environment

Similarly, create a `kustomization.yaml` file in the `prod/` directory:

```yaml
resources:
- ../../base

patchesStrategicMerge:
- patches/image-patch.yaml
```

And create the `image-patch.yaml` file in the `prod/patches/` directory:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-service
spec:
  template:
    spec:
      containers:
      - name: my-service
        image: gcr.io/my-project/my-service:v1.0.1
```

This patch changes the image tag to `v1.0.1` for the production environment.

### Applying Kustomize Configurations

To apply the Kustomize configurations, you can use the following commands:

```sh
# Apply the development configuration
kubectl apply -k kustomize/dev/

# Apply the production configuration
kubectl apply -k kustomize/prod/
```

### Managing Multiple Namespaces

In a microservices architecture, it's common to deploy services across multiple namespaces. Kustomize can help manage these namespaces efficiently.

#### Example Namespace Configuration

Create a `namespace.yaml` file in the `base/` directory:

```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: my-namespace
```

Update the `kustomization.yaml` file in the `base/` directory to include the namespace:

```yaml
resources:
- deployment.yaml
- namespace.yaml
```

Now, when you apply the Kustomize configurations, the namespace will be created automatically.

### Refactoring Manifests for Parameterization

As mentioned in the transcript, one of the key benefits of using Kustomize is the ability to parameterize values such as image names and versions. Let's refactor the manifest to use placeholders for these values.

#### Refactored Deployment Manifest

Update the `base/deployment.yaml` file to use a placeholder for the image name:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-service
  template:
    metadata:
      labels:
        app: my-service
    spec:
      containers:
      - name: my-service
        image: {{IMAGE_NAME}}
        ports:
        - containerPort:  8080
```

#### Using Kustomize to Set Parameters

Now, you can use Kustomize to set the actual image name and version in the environment-specific configurations.

##### Development Environment

Update the `image-patch.yaml` file in the `dev/patches/` directory:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-service
spec:
  template:
    spec:
      containers:
      - name: my-service
        image: gcr.io/my-project/my-service:latest
```

##### Production Environment

Update the `image-patch.yaml` file in the `prod/patches/` directory:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-service
spec:
  template:
    spec:
      containers:
      - name: my-service
        image: gcr.io/my-project/my-service:v1.0.1
```

### Automating Image Version Updates

One of the main advantages of using Kustomize is the ability to automate the updating of image versions through the CI/CD pipeline. This ensures that the correct version of the image is deployed without manual intervention.

#### Example CI/CD Pipeline Integration

Here’s an example of how you might integrate Kustomize into a CI/CD pipeline using ArgoCD:

1. **Build the Docker Image**: In your CI/CD pipeline, build the Docker image and push it to the container registry.
2. **Update Kustomize Configuration**: Use a script to update the Kustomize configuration with the new image version.
3. **Apply Kustomize Configuration**: Use ArgoCD to sync the updated Kustomize configuration to the Kubernetes cluster.

#### Example Script to Update Kustomize Configuration

```sh
#!/bin/bash

NEW_IMAGE_TAG="v1.0.1"
DEV_PATCH_FILE="kustomize/dev/patches/image-patch.yaml"
PROD_PATCH_FILE="kustomize/prod/patches/image-patch.yaml"

sed -i "s/image: .*/image: gcr.io\/my-project\/my-service:$NEW_IMAGE_TAG/" $DEV_PATCH_FILE
sed -i "s/image: .*/image: gcr.io\/my-project\/my-service:$NEW_IMAGE_TAG/" $PROD_PATCH_FILE
```

### Real-World Examples and Recent CVEs

Using Kustomize and ArgoCD can help mitigate several security risks associated with manual configuration management. For instance, consider the following recent CVEs:

- **CVE-2021-25741**: This vulnerability in Kubernetes allowed attackers to bypass RBAC restrictions and gain unauthorized access to resources. By using Kustomize and ArgoCD, you can ensure that your configurations are consistent and secure, reducing the risk of such vulnerabilities.
- **CVE-2022-2528**: This vulnerability in Kubernetes allowed attackers to escalate privileges by manipulating pod security contexts. Using Kustomize to manage your configurations ensures that security contexts are correctly set and consistent across all environments.

### How to Prevent / Defend

#### Detection

To detect misconfigurations or unauthorized changes, you can use tools like ArgoCD and Kustomize in conjunction with monitoring and alerting systems. For example, you can set up ArgoCD to monitor the state of your Kubernetes cluster and alert you if there are any discrepancies between the desired state and the actual state.

#### Prevention

To prevent unauthorized changes, you should implement strict RBAC policies and use tools like Kustomize to manage your configurations centrally. Additionally, you can use automated testing and validation tools to ensure that your configurations are correct and secure.

#### Secure Coding Fixes

Here’s an example of how you might refactor a vulnerable configuration to a secure one:

**Vulnerable Configuration**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-service
  template:
    metadata:
      labels:
        app: my-service
    spec:
      containers:
      - name: my-service
        image: gcr.io/my-project/my-service:v1.0.0
        ports:
        - containerPort: 8080
```

**Secure Configuration**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-service
  template:
    metadata:
      labels:
        app: my-service
    spec:
      containers:
      - name: my-service
        image: {{IMAGE_NAME}}
        ports:
        - containerPort: 8080
```

By using placeholders and Kustomize, you can ensure that the correct image version is deployed consistently across all environments.

### Conclusion

Using Kustomize and ArgoCD in your DevSecOps pipeline can significantly improve the management and security of your microservices applications. By centralizing and parameterizing your configurations, you can reduce the risk of errors and ensure that your applications are deployed consistently and securely. With the right tools and practices, you can build a robust and scalable release pipeline that meets the demands of modern DevSecOps.

### Practice Labs

For hands-on practice with Kustomize and ArgoCD, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but also covers Kubernetes and CI/CD pipelines.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including CI/CD pipelines.
- **Kubernetes Goat**: A Kubernetes-based lab for practicing Kubernetes security and CI/CD pipelines.

These labs provide a comprehensive learning experience and allow you to apply the concepts covered in this chapter in a practical setting.

---
<!-- nav -->
[[04-Introduction to Application Release Pipeline with ArgoCD and Kustomize|Introduction to Application Release Pipeline with ArgoCD and Kustomize]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/01-App Release Pipeline with ArgoCD/K8s Manifests for Microservices App using Kustomize/00-Overview|Overview]] | [[06-Introduction to Kubernetes Manifests and Kustomize|Introduction to Kubernetes Manifests and Kustomize]]
