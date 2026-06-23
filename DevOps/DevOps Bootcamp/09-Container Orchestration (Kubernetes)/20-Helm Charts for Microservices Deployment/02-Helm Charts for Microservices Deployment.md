---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Helm Charts for Microservices Deployment

### Introduction to Helm Charts

Helm is a package manager for Kubernetes that simplifies the deployment and management of applications. Helm charts are collections of files that describe a related set of Kubernetes resources. They provide a way to package, configure, and deploy applications in a consistent and repeatable manner.

#### What is Helm?

Helm is a tool that streamlines the process of deploying applications onto Kubernetes clusters. It allows users to define, install, and upgrade even the most complex Kubernetes applications. Helm charts are essentially templates that can be customized and deployed across different environments.

#### Why Use Helm?

Using Helm offers several advantages:

1. **Consistency**: Helm ensures that deployments are consistent across different environments.
2. **Reusability**: Helm charts can be reused across multiple projects.
3. **Version Control**: Helm supports version control for your applications, making it easier to manage updates and rollbacks.
4. **Configuration Management**: Helm allows you to manage configurations through values files, making it easier to customize deployments.

### Service Configuration in Helm Charts

In the context of Helm charts, services are used to expose applications within a Kubernetes cluster. Services can be configured to expose applications externally or internally within the cluster.

#### Service Ports

Service ports are crucial for defining how traffic is routed to pods within a Kubernetes cluster. There are three main types of ports to consider:

1. **Container Port**: This is the port on which the container listens for incoming connections.
2. **Target Port**: This is the port on the pod that the service should forward traffic to.
3. **Service Port**: This is the port on which the service itself listens for incoming connections.

Let's break down each of these ports and their roles:

1. **Container Port**:
   - **Definition**: The port on which the container listens for incoming connections.
   - **Example**: If a container runs a web server listening on port 8080, the container port would be 8080.
   - **Usage**: This port is specified in the container definition within the deployment manifest.

2. **Target Port**:
   - **Definition**: The port on the pod that the service should forward traffic to.
   - **Example**: If the service forwards traffic to port 8080 on the pod, the target port would be 8080.
   - **Usage**: This port is specified in the service definition within the Helm chart.

3. **Service Port**:
   - **Definition**: The port on which the service itself listens for incoming connections.
   - **Example**: If the service listens on port 80, the service port would be 80.
   - **Usage**: This port is specified in the service definition within the Helm chart.

#### Configuring Service Ports in Helm Charts

To configure these ports in a Helm chart, you can use variables to make the configuration dynamic. Here’s an example of how to define these ports in a Helm chart:

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}-service
spec:
  selector:
    app: {{ .Chart.Name }}
  ports:
    - protocol: TCP
      port: {{ .Values.service.port }}
      targetPort: {{ .Values.container.port }}
      nodePort: {{ .Values.nodePort }}
  type: {{ .Values.service.type }}
```

In this example, `{{ .Values.service.port }}`, `{{ .Values.container.port }}`, and `{{ .Values.nodePort }}` are variables that can be defined in the `values.yaml` file.

#### Example `values.yaml` File

```yaml
container:
  port: 8080

service:
  port: 80
  type: LoadBalancer
nodePort: 30080
```

### Service Types in Helm Charts

Kubernetes services can be of different types, each serving a specific purpose:

1. **ClusterIP**: Exposes the service on a cluster-internal IP. This is the default type.
2. **NodePort**: Exposes the service on each Node's IP at a static port.
3. **LoadBalancer**: Exposes the service externally using a cloud provider's load balancer.
4. **ExternalName**: Maps the service to an external DNS name.

#### Configuring Service Type in Helm Charts

To make the service type configurable in a Helm chart, you can define a variable in the `values.yaml` file and use it in the service definition.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}-service
spec:
  selector:
    app: {{ .Chart.Name }}
  ports:
    - protocol: TCP
      port: {{ .Values.service.port }}
      targetPort: {{ .Values.container.port }}
      nodePort: {{ .Values.nodePort }}
  type: {{ .Values.service.type }}
```

#### Example `values.yaml` File

```yaml
container:
  port: 8080

service:
  port: 80
  type: LoadBalancer
nodePort: 30080
```

### Image Configuration in Helm Charts

Images are a critical component of Helm charts, as they define the Docker images that will be used to run the application. Images can be configured to allow for different versions and repositories.

#### Image Repository and Tag

An image in a Helm chart typically consists of two parts:

1. **Repository**: The location of the Docker image.
2. **Tag**: The version of the Docker image.

To configure these in a Helm chart, you can use variables to make the configuration dynamic.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-deployment
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Chart.Name }}
  template:
    metadata:
      labels:
        app: {{ .Chart.Name }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          ports:
            - containerPort: {{ .Values.container.port }}
```

#### Example `values.yaml` File

```yaml
replicaCount: 1

image:
  repository: myregistry/myapp
  tag: latest

container:
  port: 8080
```

### Complete Example of a Helm Chart

Here is a complete example of a Helm chart that includes both service and deployment configurations.

#### `templates/service.yaml`

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}-service
spec:
  selector:
    app: {{ .Chart.Name }}
  ports:
    - protocol: TCP
      port: {{ .Values.service.port }}
      targetPort: {{ .Values.container.port }}
      nodePort: {{ .Values.nodePort }}
  type: {{ .Values.service.type }}
```

#### `templates/deployment.yaml`

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-deployment
spec:
  replicas: {{ .Values.replicaCount }}
  selector:
    matchLabels:
      app: {{ .Chart.Name }}
  template:
    metadata:
      labels:
        app: {{ .Chart.Name }}
    spec:
      containers:
        - name: {{ .Chart.Name }}
          image: "{{ .Values.image.repository }}:{{ .Values.image.tag }}"
          ports:
            - containerPort: {{ .Values.container.port }}
```

#### `values.yaml`

```yaml
replicaCount: 1

image:
  repository: myregistry/myapp
  tag: latest

container:
  port: 8080

service:
  port: 80
  type: LoadBalancer
nodePort: 30080
```

### How to Prevent / Defend

#### Detection

To ensure that your Helm charts are secure, you can use tools like `helm lint` to check for common issues in your charts. Additionally, you can use static analysis tools like `kube-score` to evaluate the security posture of your Kubernetes manifests.

#### Prevention

1. **Use Secure Images**: Ensure that the Docker images used in your Helm charts are from trusted sources and are regularly updated.
2. **Limit Service Exposure**: Avoid exposing services unnecessarily. Use `ClusterIP` for internal services and `LoadBalancer` only when required.
3. **Use Role-Based Access Control (RBAC)**: Implement RBAC to restrict access to your Kubernetes resources.
4. **Regularly Update Dependencies**: Keep your Helm dependencies up-to-date to avoid known vulnerabilities.

#### Secure Coding Fixes

Here is an example of a vulnerable Helm chart and its secure counterpart:

##### Vulnerable Helm Chart

```yaml
apiVersion: v1
kind: Service
metadata:
  name: insecure-service
spec:
  selector:
    app: insecure-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: LoadBalancer
```

##### Secure Helm Chart

```yaml
apiVersion: v1
kind: Service
metadata:
  name: secure-service
spec:
  selector:
    app: secure-app
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8080
  type: ClusterIP
```

### Conclusion

Helm charts provide a powerful way to manage and deploy applications on Kubernetes. By understanding the configuration options available in Helm charts, you can create more flexible and secure deployments. Always ensure that your Helm charts are secure by following best practices and using tools to detect and prevent vulnerabilities.

### Practice Labs

For hands-on practice with Helm charts, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs that cover different aspects of web security, including Kubernetes and Helm.
- **OWASP Juice Shop**: A deliberately insecure web application that can be used to learn about various security vulnerabilities and how to mitigate them.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application that can be used to practice security testing and mitigation techniques.

These labs provide practical experience with deploying and securing applications using Helm charts and Kubernetes.

---
<!-- nav -->
[[01-Introduction to Helm Charts for Microservices Deployment|Introduction to Helm Charts for Microservices Deployment]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/20-Helm Charts for Microservices Deployment/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/20-Helm Charts for Microservices Deployment/03-Practice Questions & Answers|Practice Questions & Answers]]
