---
course: DevSecOps
topic: EKS Blueprints
tags: [devsecops]
---

## Kubernetes Metric Server Overview

The Kubernetes Metric Server is a crucial component in managing and monitoring resource usage within a Kubernetes cluster. It aggregates resource consumption data from all worker nodes and provides this information to the Kubernetes API server. This allows administrators and developers to monitor and manage the resources being consumed by various pods and services within the cluster.

### Purpose of the Metric Server

The primary purpose of the Metric Server is to provide accurate and up-to-date information about resource usage within the cluster. This includes details about CPU and memory consumption across all nodes and pods. By having this data readily available, Kubernetes can make informed decisions about scheduling and scaling workloads.

#### Resource Consumption Data

- **CPU Usage**: Tracks the amount of CPU resources being utilized by each pod.
- **Memory Usage**: Monitors the memory consumption of each pod.
- **Node Utilization**: Aggregates this data across all nodes in the cluster.

### Installation and Deployment

The Metric Server is not installed by default in an Amazon EKS (Elastic Kubernetes Service) cluster. Therefore, it needs to be manually installed as an add-on. Below is a step-by-step guide on how to deploy the Metric Server in an EKS cluster.

#### Step-by-Step Deployment

1. **Download the Metric Server Manifest**:
    ```bash
    wget https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.6.1/components.yaml
    ```

2. **Modify the Manifest**:
    Ensure that the manifest is configured correctly for your environment. Specifically, check the `image` field to ensure it points to the correct image repository and tag.

3. **Apply the Manifest**:
    ```bash
    kubectl apply -f components.yaml
    ```

4. **Verify Deployment**:
    Check the status of the Metric Server deployment and pods.
    ```bash
    kubectl get deployments -n kube-system | grep metrics-server
    kubectl get pods -n kube-system | grep metrics-server
    ```

### Alternative: Cube State Metrics

An alternative to the Metric Server is Cube State Metrics, which was used in a DevOps boot camp. While the Metric Server focuses primarily on resource consumption, Cube State Metrics focuses more on the health and availability of Kubernetes objects.

#### Health Monitoring

Cube State Metrics provides detailed insights into the health of pods and nodes, including:

- **Pod Availability**: Ensures that pods are running and available.
- **Node Readiness**: Checks the readiness of nodes based on resource availability.

### Example: Deploying the Metric Server

Let's walk through a complete example of deploying the Metric Server in an EKS cluster.

#### Full Deployment Steps

1. **Download the Manifest**:
    ```bash
    wget https://github.com/kubernetes-sigs/metrics-server/releases/download/v0.6.1/components.yaml
    ```

2. **Inspect the Manifest**:
    ```yaml
    apiVersion: v1
    kind: ServiceAccount
    metadata:
      name: metrics-server
      namespace: kube-system
      labels:
        k8s-app: metrics-server
    ---
    apiVersion: rbac.authorization.k8s.io/v1
    kind: ClusterRole
    metadata:
      name: metrics-server:system:auth-delegator
    rules:
    - apiGroups:
      - ""
      resources:
      - nodes/proxy
      verbs:
      - "*"
    ---
    apiVersion: rbac.authorization.k8s.io/v1
    kind: ClusterRoleBinding
    metadata:
      name: metrics-server:system:auth-delegator
    roleRef:
      apiGroup: rbac.authorization.k8s.io
      kind: ClusterRole
      name: metrics-server:system:auth-delegator
    subjects:
    - kind: ServiceAccount
      name: metrics-server
      namespace: kube-system
    ---
    apiVersion: rbac.authorization.k8s.io/v1
    kind: Role
    metadata:
      name: metrics-server:system:metrics-reader
      namespace: kube-system
    rules:
    - apiGroups:
      - ""
      resources:
      - nodes/metrics
      verbs:
      - get
    ---
    apiVersion: rbac.authorization.k8s.io/v1
    kind: RoleBinding
    metadata:
      name: metrics-server-auth-reader
      namespace: kube-system
    roleRef:
      apiGroup: rb
    ```

3. **Apply the Manifest**:
    ```bash
    kubectl apply -f components.yaml
    ```

4. **Verify Deployment**:
    ```bash
    kubectl get deployments -n kube-system | grep metrics-server
    kubectl get pods -n kube-system | grep metrics-server
    ```

### Accessing External Services

When deploying applications or services that have a user interface (UI), it is often necessary to expose these services externally so they can be accessed via a browser. This requires configuring appropriate services and ingress controllers.

#### Example: Exposing a Service

Consider a scenario where you have a web application that needs to be accessible from the internet. You would typically create a service and an ingress controller to expose this application.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-web-app-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8080
  selector:
    app: my-web-app
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-web-app-ingress
spec:
  rules:
  - host: my-web-app.example.com
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: my-web-app-service
            port:
              number: 80
```

### Real-World Examples and Breaches

Recent breaches and vulnerabilities related to Kubernetes clusters highlight the importance of proper resource management and monitoring. For instance, the Kubernetes API server has been targeted in several attacks due to misconfigurations and lack of proper monitoring.

#### CVE Example

CVE-2021-25741: A vulnerability in the Kubernetes API server allowed unauthorized access to sensitive information. This underscores the need for robust monitoring and resource management tools like the Metric Server.

### How to Prevent / Defend

#### Detection

- **Monitoring Tools**: Use tools like Prometheus and Grafana to monitor resource usage and detect anomalies.
- **Logging**: Enable logging for all Kubernetes components and regularly review logs for suspicious activity.

#### Prevention

- **RBAC Configuration**: Ensure proper Role-Based Access Control (RBAC) is configured to restrict access to sensitive resources.
- **Network Policies**: Implement network policies to control traffic between pods and external networks.

#### Secure Coding Fixes

Compare the insecure and secure versions of a deployment configuration:

**Insecure Version**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-web-app
  template:
    metadata:
      labels:
        app: my-web-app
    spec:
      containers:
      - name: my-web-app-container
        image: my-web-app-image:latest
        ports:
        - containerPort: 8080
```

**Secure Version**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-web-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-web-app
  template:
    metadata:
      labels:
        app: my-web-app
    spec:
      containers:
      - name: my-web-app-container
        image: my-web-app-image:latest
        ports:
        - containerPort: 8080
        securityContext:
          runAsUser: 1000
          runAsNonRoot: true
```

### Conclusion

The Kubernetes Metric Server is a vital tool for monitoring and managing resource usage within a Kubernetes cluster. By providing accurate and up-to-date information about resource consumption, it enables better decision-making and resource management. Additionally, understanding alternatives like Cube State Metrics can help in choosing the right tool for specific monitoring needs. Proper deployment, configuration, and monitoring practices are essential to ensuring the security and reliability of Kubernetes clusters.

### Practice Labs

For hands-on experience with Kubernetes and EKS, consider the following labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security.
- **CloudGoat**: A cloud security lab that covers various aspects of AWS security, including EKS.
- **Pacu**: A penetration testing framework for AWS that includes modules for EKS.

These labs provide practical experience in deploying and securing Kubernetes clusters, including the use of tools like the Metric Server.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/02-EKS Blueprints/Overview of EKS Add ons we install/02-Introduction to EKS Blueprints and Cluster Operations|Introduction to EKS Blueprints and Cluster Operations]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/02-EKS Blueprints/Overview of EKS Add ons we install/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/02-EKS Blueprints/Overview of EKS Add ons we install/04-Overview of EKS Add-Ons|Overview of EKS Add-Ons]]
