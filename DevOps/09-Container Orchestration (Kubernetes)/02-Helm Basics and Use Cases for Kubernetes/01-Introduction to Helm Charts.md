---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Helm Charts

Helm is a package manager for Kubernetes that simplifies the deployment and management of applications. A Helm chart is a collection of files that describe a related set of Kubernetes resources. These charts make it easier to manage complex deployments by providing a consistent way to define and install applications.

### What is Helm?

Helm is designed to simplify the process of deploying and managing applications on Kubernetes. It does this by using charts, which are collections of files that describe a related set of Kubernetes resources. Helm charts provide a consistent way to define and install applications, making it easier to manage complex deployments.

### Why Use Helm?

Using Helm provides several benefits:

1. **Consistency**: Helm charts ensure that applications are deployed consistently across different environments.
2. **Reusability**: Helm charts can be reused across different projects, reducing the amount of boilerplate code.
3. **Version Control**: Helm charts can be versioned, allowing you to track changes and roll back to previous versions if necessary.
4. **Dependency Management**: Helm charts can specify dependencies on other charts, making it easier to manage complex applications.

### How Helm Works

Helm operates using two main components: the `helm` client and the Tiller server. The `helm` client interacts with the Tiller server to manage the installation and upgrade of charts.

#### Components of a Helm Chart

A Helm chart consists of several key components:

1. **Chart Directory Structure**
2. **Chart.yaml**
3. **values.yaml**
4. **Templates Folder**
5. **Charts Folder**

Let's dive into each component in detail.

### Chart Directory Structure

The directory structure of a Helm chart is as follows:

```
mychart/
├── Chart.yaml
├── values.yaml
├── charts/
│   └── subchart/
│       ├── Chart.yaml
│       └── templates/
│           └── deployment.yaml
└── templates/
    ├── deployment.yaml
    └── service.yaml
```

#### Chart.yaml

The `Chart.yaml` file contains metadata about the chart, including the name, version, and dependencies. Here is an example of what a `Chart.yaml` might look like:

```yaml
apiVersion: v2
name: mychart
version: 0.1.0
description: A Helm chart for my application
dependencies:
  - name: subchart
    version: 0.1.0
    repository: file://charts/subchart
```

This file specifies the name of the chart (`mychart`), the version (`0.1.0`), and a description. It also lists any dependencies, such as the `subchart`.

#### values.yaml

The `values.yaml` file contains the default values for the chart. These values can be overridden when installing or upgrading the chart. Here is an example of what a `values.yaml` might look like:

```yaml
image:
  name: myapp
  tag: latest
port: 8080
version: 1.0.0
```

These values can be referenced in the template files to generate the final Kubernetes manifests.

#### Templates Folder

The `templates` folder contains the template files that are used to generate the Kubernetes manifests. These files use the Go templating language to inject values from `values.yaml`. Here is an example of a `deployment.yaml` template file:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: {{ .Release.Name }}
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}
    spec:
      containers:
      - name: {{ .Release.Name }}
        image: "{{ .Values.image.name }}:{{ .Values.image.tag }}"
        ports:
        - containerPort: {{ .Values.port }}
```

In this template, the `.Values.image.name`, `.Values.image.tag`, and `.Values.port` variables are replaced with the corresponding values from `values.yaml`.

#### Charts Folder

The `charts` folder contains any dependencies that the chart relies on. Each dependency is itself a Helm chart. This allows you to build complex applications by combining multiple charts.

### Example Helm Chart

Let's walk through an example Helm chart to see how these components work together.

#### Directory Structure

```
mychart/
├── Chart.yaml
├── values.yaml
├── charts/
│   └── subchart/
│       ├── Chart.yaml
│       └── templates/
│           └── deployment.yaml
└── templates/
    ├── deployment.yaml
    └── service.yaml
```

#### Chart.yaml

```yaml
apiVersion: v2
name: mychart
version: 0.1.0
description: A Helm chart for my application
dependencies:
  - name: subchart
    version: 0.1.0
    repository: file://charts/subchart
```

#### values.yaml

```yaml
image:
  name: myapp
  tag: latest
port: 8080
version: 1.0.0
```

#### templates/deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: {{ .Release.Name }}
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}
    spec:
      containers:
      - name: {{ .Release.Name }}
        image: "{{ .Values.image.name }}:{{ .Values.image.tag }}"
        ports:
        - containerPort: {{ .Values.port }}
```

#### templates/service.yaml

```yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}-service
spec:
  selector:
    app: {{ .Release.Name }}
  ports:
  - protocol: TCP
    port: 80
    targetPort: {{ .Values.port }}
  type: LoadBalancer
```

#### charts/subchart/Chart.yaml

```yaml
apiVersion: v2
name: subchart
version: 0.1.0
description: A subchart for my application
```

#### charts/subchart/templates/deployment.yaml

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-sub-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {{ .Release.Name }}-sub
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}-sub
    spec:
      containers:
      - name: {{ .Release.Name }}-sub
        image: "{{ .Values.image.name }}:{{ .Values.image.tag }}"
        ports:
        - containerPort: {{ .Values.port }}
```

### Installing a Helm Chart

To install a Helm chart, you use the `helm install` command. Here is an example:

```sh
helm install my-release ./mychart
```

This command installs the `mychart` chart with the release name `my-release`.

### Overriding Values

You can override the default values in `values.yaml` when installing or upgrading a chart. Here is an example:

```sh
helm install my-release ./mychart --set image.tag=1.2.3
```

This command overrides the `image.tag` value to `1.2.3`.

### Upgrading a Helm Chart

To upgrade a Helm chart, you use the `helm upgrade` command. Here is an example:

```sh
helm upgrade my-release ./mychart
```

This command upgrades the `my-release` release with the latest version of the `mychart` chart.

### Uninstalling a Helm Chart

To uninstall a Helm chart, you use the `helm uninstall` command. Here is an example:

```sh
helm uninstall my-release
```

This command uninstalls the `my-release` release.

### Real-World Examples

Here are some real-world examples of how Helm charts are used in production environments:

#### Example 1: Deploying a Web Application

Suppose you want to deploy a web application using Helm. You can create a chart that defines the deployment and service for the application. Here is an example:

```yaml
# Chart.yaml
apiVersion: v2
name: webapp
version: 0.1.0
description: A Helm chart for a web application
```

```yaml
# values.yaml
image:
  name: webapp
  tag: latest
port: 8080
```

```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-webapp-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: {{ .Release.Name }}-webapp
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}-webapp
    spec:
      containers:
      - name: {{ .Release.Name }}-webapp
        image: "{{ .Values.image.name }}:{{ .Values.image.tag }}"
        ports:
        - containerPort: {{ .Values.port }}
```

```yaml
# templates/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}-webapp-service
spec:
  selector:
    app: {{ .Release.Name }}-webapp
  ports:
  - protocol: TCP
    port: 80
    targetPort: {{ .Values.port }}
  type: LoadBalancer
```

#### Example 2: Deploying a Database

Suppose you want to deploy a database using Helm. You can create a chart that defines the deployment and service for the database. Here is an example:

```yaml
# Chart.yaml
apiVersion: v2
name: database
version: 0.1.0
description: A Helm chart for a database
```

```yaml
# values.yaml
image:
  name: postgres
  tag: latest
port: 5432
```

```yaml
# templates/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Release.Name }}-database-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {{ .Release.Name }}-database
  template:
    metadata:
      labels:
        app: {{ .Release.Name }}-database
    spec:
      containers:
      - name: {{ .Release.Name }}-database
        image: "{{ .Values.image.name }}:{{ .Values.image.tag }}"
        ports:
        - containerPort: {{ .Values.port }}
```

```yaml
# templates/service.yaml
apiVersion: v1
kind: Service
metadata:
  name: {{ .Release.Name }}-database-service
spec:
  selector:
    app: {{ .Release.Name }}-database
  ports:
  - protocol: TCP
    port: 5432
    targetPort: {{ .Values.port }}
  type: ClusterIP
```

### Common Pitfalls

When working with Helm charts, there are several common pitfalls to watch out for:

1. **Overwriting Values**: Make sure to carefully manage the values in `values.yaml` to avoid overwriting important configurations.
2. **Dependency Management**: Ensure that all dependencies are properly specified and managed.
3. **Template Errors**: Double-check your template files to avoid errors that can cause the deployment to fail.

### How to Prevent / Defend

To prevent issues with Helm charts, follow these best practices:

1. **Use Version Control**: Keep your Helm charts in version control to track changes and roll back to previous versions if necessary.
2. **Test Thoroughly**: Test your Helm charts thoroughly before deploying them to production.
3. **Secure Configuration**: Secure your Helm charts by using secrets and environment variables to manage sensitive data.

### Conclusion

Helm charts provide a powerful way to manage complex Kubernetes deployments. By understanding the components of a Helm chart and how they work together, you can create robust and maintainable applications. Always test your charts thoroughly and follow best practices to ensure the security and reliability of your deployments.

### Practice Labs

For hands-on practice with Helm charts, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs that cover web application security, including the use of Helm charts.
- **OWASP Juice Shop**: Provides a vulnerable web application that can be deployed using Helm charts.
- **Kubernetes Goat**: Offers a series of challenges that involve deploying and managing applications using Helm charts.

By completing these labs, you can gain practical experience with Helm charts and improve your skills in deploying and managing Kubernetes applications.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/02-Helm Basics and Use Cases for Kubernetes/00-Overview|Overview]] | [[02-Introduction to Helm and Its Role in Kubernetes|Introduction to Helm and Its Role in Kubernetes]]
