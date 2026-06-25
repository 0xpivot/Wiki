---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Helm and Microservices Deployment

Helm is a package manager for Kubernetes that simplifies the deployment and management of applications. It allows users to define, install, and upgrade even the most complex microservice-based applications using charts—packages that contain all the Kubernetes resources needed to deploy an application. In this chapter, we will delve deep into deploying microservices with Helm commands, covering the underlying mechanisms, potential pitfalls, and best practices for securing your deployments.

### What is Helm?

Helm is a tool that streamlines the process of deploying applications on Kubernetes. It uses a templating engine called Go Templates to generate Kubernetes manifests (YAML files) that describe the desired state of your application. These manifests are then applied to your Kubernetes cluster to create the necessary resources such as Pods, Services, Deployments, etc.

#### Why Use Helm?

1. **Reusability**: Helm charts can be reused across different environments, making it easier to manage multiple clusters.
2. **Version Control**: Helm supports versioning of charts, allowing you to track changes and roll back to previous versions if needed.
3. **Parameterization**: Helm charts can be parameterized, enabling you to customize deployments without modifying the chart itself.
4. **Dependency Management**: Helm charts can declare dependencies on other charts, simplifying the management of complex applications.

### Helm Commands and Workflow

The primary workflow for deploying microservices with Helm involves several key steps:

1. **Creating a Chart**: Define the structure and contents of your application.
2. **Installing a Release**: Deploy the application to your Kubernetes cluster.
3. **Upgrading a Release**: Update the application to a new version.
4. **Uninstalling a Release**: Remove the application from your cluster.

Let's explore each step in detail.

#### Creating a Chart

A Helm chart is a collection of files that describe a related set of Kubernetes resources. The basic structure of a chart includes:

- `Chart.yaml`: Metadata about the chart.
- `values.yaml`: Default values for parameters used in the templates.
- `templates/`: Directory containing the Kubernetes resource definitions.

Here is an example of a simple chart structure:

```yaml
# Chart.yaml
apiVersion: v2
name: myapp
version: 0.1.0
description: A Helm chart for myapp
```

```yaml
# values.yaml
replicaCount: 2
image:
  repository: myapp
  tag: latest
service:
  type: LoadBalancer
```

```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-deployment
spec:
  replicas: {{ .Values.replicaCount }}
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}
    spec:
      containers:
      - name: {{ .Release.Name }}
        image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
        ports:
        - containerPort: 80
```

```yaml
# templates/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}-service
spec:
  type: {{ .Values.service.type }}
  selector:
    app: {{ .Release.Name }}
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
```

#### Installing a Release

To install a release, you use the `helm install` command. This command takes the chart and the values file, generates the Kubernetes manifests, and applies them to your cluster.

```sh
helm install my-release ./myapp --values values.yaml
```

This command will create a release named `my-release` using the `myapp` chart and the values specified in `values.yaml`.

#### Upgrading a Release

If you need to update the application, you can use the `helm upgrade` command. This command will apply the new values and update the existing resources in the cluster.

```sh
helm upgrade my-release ./myapp --values updated-values.yaml
```

#### Uninstalling a Release

To remove the application from your cluster, you can use the `helm uninstall` command.

```sh
helm uninstall my-release
```

### Detailed Example: Deploying a Microservice Application

Let's walk through a detailed example of deploying a microservice application using Helm. We will deploy an application with a frontend service and a Redis backend.

#### Step 1: Create the Chart

First, we create the chart structure:

```sh
helm create myapp
```

This command creates a directory structure with the necessary files. We will modify the `values.yaml` and `templates` to suit our application.

```yaml
# values.yaml
frontend:
  replicaCount: 2
  image:
    repository: myapp-frontend
    tag: latest
  service:
    type: LoadBalancer
redis:
  replicaCount: 1
  image:
    repository: redis
    tag: latest
```

```yaml
# templates/frontend-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-frontend-deployment
spec:
  replicas: {{ .Values.frontend.replicaCount }}
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}-frontend
    spec:
      containers:
      - name: {{ .Release.Name }}-frontend
        image: "{{ .Values.frontend.image.repository }}:{{ .Values.frontend.image.tag }}"
        ports:
        - containerPort: 80
```

```yaml
# templates/frontend-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}-frontend-service
spec:
  type: {{ .Values.frontend.service.type }}
  selector:
    app: {{ .Release.Name }}-frontend
  ports:
  - protocol: TCP
    port: 80
    targetPort: 80
```

```yaml
# templates/redis-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-redis-deployment
spec:
  replicas: {{ .Values.redis.replicaCount }}
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}-redis
    spec:
      containers:
      - name: {{ .Release.Name }}-redis
        image: "{{ .Values.redis.image.repository }}:{{ .Values.redis.image.tag }}"
        ports:
        - containerPort: 6379
```

```yaml
# templates/redis-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}-redis-service
spec:
  selector:
    app: {{ .Release.Name }}-redis
  ports:
  - protocol: TCP
    port: 6379
    targetPort: 6379
```

#### Step 2: Install the Release

Now, we install the release using the `helm install` command:

```sh
helm install my-release ./myapp --values values.yaml
```

This command will create the necessary resources in the cluster, including the frontend deployment and service, and the Redis deployment and service.

#### Step 3: Verify the Deployment

We can verify the deployment by checking the status of the pods and services:

```sh
kubectl get pods
kubectl get svc
```

We should see the frontend and Redis pods running, and the frontend service with a LoadBalancer type.

#### Step 4: Access the Application

Since the frontend service is of type `LoadBalancer`, it will create a cloud-native load balancer. We can access the application using the load balancer IP address.

```sh
kubectl get svc my-release-frontend-service
```

This command will return the external IP address of the load balancer. We can then access the application using this IP address.

#### Step 5: Uninstall the Release

Finally, we can uninstall the release using the `helm uninstall` command:

```sh
helm uninstall my-release
```

This command will remove all the resources created by the release.

### Pitfalls and Best Practices

Deploying microservices with Helm can be powerful but also comes with potential pitfalls. Here are some common issues and best practices to avoid them:

#### Overriding Configuration

When overriding configuration values, ensure that you understand the implications of the changes. For example, changing the number of replicas or the image tag can affect the behavior of your application.

```yaml
# values.yaml
frontend:
  replicaCount: 2
  image:
    repository: myapp-frontend
    tag: latest
  service:
    type: LoadBalancer
redis:
  replicaCount: 1
  image:
    repository: redis
    tag: latest
```

#### Securing Helm Charts

Ensure that your Helm charts are secure by following best practices such as:

- Using secure images and tags.
- Limiting the permissions of the service accounts used by the pods.
- Enabling RBAC (Role-Based Access Control) to restrict access to the resources.

#### Monitoring and Logging

Implement monitoring and logging to ensure that your application is running smoothly. Use tools like Prometheus and Grafana for monitoring and ELK stack for logging.

### Real-World Examples and CVEs

Recent breaches and CVEs have highlighted the importance of securing your Helm deployments. For example, the CVE-2021-25742 affected Helm versions prior to 3.5.0, where a vulnerability allowed unauthorized access to the Tiller server. To mitigate such risks, always keep your Helm and Kubernetes versions up to date and follow secure coding practices.

### How to Prevent / Defend

#### Detection

Regularly audit your Helm charts and configurations to ensure they are secure. Use tools like `helm lint` to validate your charts and `kubectl` to inspect the resources in your cluster.

#### Prevention

- Keep your Helm and Kubernetes versions up to date.
- Use secure images and tags.
- Implement RBAC to restrict access to the resources.
- Enable monitoring and logging to detect anomalies.

#### Secure Coding Fixes

Compare the vulnerable and secure versions of your Helm charts and configurations.

**Vulnerable Version:**

```yaml
# values.yaml
frontend:
  replicaCount: 2
  image:
    repository: myapp-frontend
    tag: latest
  service:
    type: LoadBalancer
redis:
  replicaCount: 1
  image:
    repository: redis
    tag: latest
```

**Secure Version:**

```yaml
# values.yaml
frontend:
  replicaCount: 2
  image:
    repository: myapp-frontend
    tag: 1.0.0
  service:
    type: LoadBalancer
redis:
  replicaCount:  1
  image:
    repository: redis
    tag: 6.2.6
```

### Conclusion

Deploying microservices with Helm commands is a powerful way to manage complex applications on Kubernetes. By understanding the underlying mechanisms, following best practices, and implementing secure coding practices, you can ensure that your deployments are robust and secure.

### Practice Labs

For hands-on practice with deploying microservices with Helm, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive course on web security, including sections on deploying and securing microservices.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.
- **WebGoat**: An interactive, gamified training application for learning about web application security.

These labs provide practical experience in deploying and securing microservices with Helm, helping you to master the skills needed for real-world DevOps scenarios.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/14-Deploying Microservices with Helm Commands/00-Overview|Overview]] | [[02-Creating a Helmfile|Creating a Helmfile]]
