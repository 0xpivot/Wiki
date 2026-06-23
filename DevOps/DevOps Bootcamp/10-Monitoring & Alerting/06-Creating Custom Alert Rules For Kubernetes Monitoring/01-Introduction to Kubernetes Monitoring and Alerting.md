---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Kubernetes Monitoring and Alerting

Kubernetes is a powerful orchestration platform for managing containerized applications. One of the critical aspects of maintaining a healthy Kubernetes cluster is monitoring and alerting. Monitoring helps in tracking various metrics such as CPU usage, memory consumption, and network traffic. Alerting, on the other hand, ensures that you are notified when certain conditions are met, allowing you to take corrective actions promptly.

In this chapter, we will delve into creating custom alert rules for Kubernetes monitoring. Specifically, we will focus on two scenarios:

1. **High CPU Usage on Kubernetes Nodes**: An alert when the CPU usage on a Kubernetes node exceeds 50%.
2. **Pod Crash Loop**: An alert when a pod fails to start and enters a crash loop.

### Background Theory

#### What is Kubernetes Monitoring?

Kubernetes monitoring involves collecting and analyzing metrics from various components within the cluster, including nodes, pods, and services. These metrics provide insights into the health and performance of the cluster. Common metrics include CPU usage, memory usage, disk space, network traffic, and application-specific metrics.

#### Why is Monitoring Important?

Monitoring is crucial for several reasons:

- **Proactive Maintenance**: By continuously monitoring the cluster, you can identify potential issues before they become critical.
- **Performance Optimization**: Monitoring helps in identifying bottlenecks and optimizing resource allocation.
- **Troubleshooting**: In case of failures, monitoring data can help in diagnosing the root cause.
- **Compliance**: Many organizations have compliance requirements that mandate continuous monitoring and logging.

#### How Does Monitoring Work in Kubernetes?

Kubernetes provides built-in mechanisms for monitoring through the Metrics Server and Prometheus. The Metrics Server collects resource metrics from the nodes and exposes them via the Kubernetes API. Prometheus is a popular monitoring system that can scrape metrics from various sources, including the Kubernetes API.

### Creating Custom Alert Rules

To create custom alert rules, we will use Prometheus, which is a widely adopted monitoring solution for Kubernetes clusters. Prometheus allows you to define alert rules using PromQL (Prometheus Query Language).

#### Step-by-Step Guide

1. **Set Up the Monitoring Directory**:
   - Create a directory named `monitoring` where you will store all your monitoring-related configuration files.
   - Open the `monitoring` directory in your preferred code editor (e.g., Visual Studio Code).

2. **Create the Alert Rule File**:
   - Create a new file named `alertrules.yaml` in the `monitoring` directory.
   - The structure of the alert rule file will be similar to the built-in alert rules provided by Prometheus.

3. **Define the Alert Rules**:
   - We will define two alert rules: one for high CPU usage on Kubernetes nodes and another for pods in a crash loop.

### High CPU Usage on Kubernetes Nodes

#### Alert Rule Definition

```yaml
groups:
- name: kubernetes-node-high-cpu-load
  rules:
  - alert: NodeHighCPULoad
    expr: sum(node_cpu_seconds_total{mode!="idle"}) by (instance) > 0.5 * sum(node_cpu_cores)
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Node {{ $labels.instance }} has high CPU load"
      description: "The node {{ $labels.instance }} has a CPU load exceeding 50% for more than 5 minutes."
```

#### Explanation

- **alert**: The name of the alert rule.
- **expr**: The PromQL expression that defines the condition for triggering the alert. Here, we are calculating the total non-idle CPU time (`node_cpu_seconds_total`) and comparing it to 50% of the total CPU cores (`node_cpu_cores`).
- **for**: The duration for which the condition must be true before the alert is triggered.
- **labels**: Additional metadata associated with the alert.
- **annotations**: Descriptive information about the alert, including a summary and a detailed description.

#### How to Prevent / Defend

- **Detection**: Use Prometheus to monitor the CPU usage on Kubernetes nodes.
- **Prevention**:
  - Ensure that the cluster is properly scaled to handle the workload.
  - Implement horizontal pod autoscaling (HPA) to automatically scale the number of replicas based on CPU usage.
  - Use resource quotas to limit the amount of resources that can be consumed by pods.

#### Secure-Coding Fixes

**Vulnerable Configuration**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: example-pod
spec:
  containers:
  - name: example-container
    image: example-image
    resources:
      limits:
        cpu: "1"
```

**Secure Configuration**:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: example-pod
spec:
  containers:
  - name: example-container
    image: example-image
    resources:
      limits:
        cpu: "2"
      requests:
        cpu: "1"
```

### Pod Crash Loop

#### Alert Rule Definition

```yaml
groups:
- name: kubernetes-pod-crash-loop
  rules:
  - alert: PodCrashLoop
    expr: count(kube_pod_container_status_restarts_total{job="kube-state-metrics", namespace!="", pod!=""}) by (namespace, pod) > 0
    for: 5m
    labels:
      severity: warning
    annotations:
      summary: "Pod {{ $labels.namespace }}/{{ $labels.pod }} is in a crash loop"
      description: "The pod {{ $labels.namespace }}/{{ $labels.pod }} has been restarting for more than 5 minutes."
```

#### Explanation

- **alert**: The name of the alert rule.
- **expr**: The PromQL expression that defines the condition for triggering the alert. Here, we are counting the number of restarts (`kube_pod_container_status_restarts_total`) for each pod.
- **for**: The duration for which the condition must be true before the alert is triggered.
- **labels**: Additional metadata associated with the alert.
- **annotations**: Descriptive information about the alert, including a summary and a detailed description.

#### How to Prevent / Defend

- **Detection**: Use Prometheus to monitor the number of restarts for each pod.
- **Prevention**:
  - Ensure that the pod's container images are up-to-date and free of bugs.
  - Implement liveness and readiness probes to detect and recover from failures.
  - Use resource requests and limits to ensure that the pod has enough resources to run successfully.

#### Secure-Coding Fixes

**Vulnerable Configuration**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: example-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: example-app
  template:
    metadata:
      labels:
        app: example-app
    spec:
      containers:
      - name: example-container
        image: example-image
        ports:
        - containerPort: 8080
```

**Secure Configuration**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: example-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: example-app
  template:
    metadata:
      labels:
        app: example-app
    spec:
      containers:
      - name: example-container
        image: example-image
        ports:
        - containerPort: 8080
        livenessProbe:
          httpGet:
            path: /healthz
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /readyz
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 10
```

### Real-World Examples

#### Recent CVEs and Breaches

- **CVE-2021-25741**: A vulnerability in the Kubernetes API server allowed attackers to bypass authentication and authorization checks. This highlights the importance of monitoring and alerting on unauthorized access attempts.
- **Breaches at Cloudflare**: In 2020, a misconfiguration in Cloudflare's Kubernetes cluster led to a data breach. Proper monitoring and alerting could have helped detect and mitigate the issue earlier.

### Conclusion

Creating custom alert rules for Kubernetes monitoring is essential for maintaining the health and performance of your cluster. By defining alerts for specific conditions such as high CPU usage and pod crash loops, you can proactively address issues before they become critical. Additionally, implementing secure coding practices and proper resource management can further enhance the resilience of your Kubernetes cluster.

### Practice Labs

For hands-on practice with Kubernetes monitoring and alerting, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web application security, including monitoring and alerting.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including monitoring and alerting.
- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security, including monitoring and alerting.

By completing these labs, you can gain practical experience in setting up and configuring custom alert rules for Kubernetes monitoring.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/06-Creating Custom Alert Rules For Kubernetes Monitoring/00-Overview|Overview]] | [[02-Creating Custom Alert Rules for Kubernetes Monitoring|Creating Custom Alert Rules for Kubernetes Monitoring]]
