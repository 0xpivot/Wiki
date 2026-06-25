---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Monitoring High CPU Load Alerts in Kubernetes

Monitoring high CPU load alerts is a critical aspect of maintaining the health and performance of a Kubernetes cluster. This chapter delves into the intricacies of setting up and managing alerts for high CPU usage, focusing on the practical aspects of implementing these alerts and ensuring they function correctly.

### Background Theory

Kubernetes is a powerful orchestration platform designed to manage containerized applications at scale. One of the key challenges in managing such environments is ensuring that resources like CPU are used efficiently and that any issues are detected and resolved promptly. High CPU load can lead to degraded application performance, increased latency, and even service outages.

#### Why Monitor High CPU Load?

High CPU load can indicate several issues:

1. **Resource Contention**: Applications may be competing for CPU resources, leading to inefficiencies.
2. **Performance Bottlenecks**: Certain parts of the application might be CPU-intensive, causing delays.
3. **Malfunctioning Components**: A malfunctioning component could be consuming excessive CPU, leading to overall system degradation.

By monitoring high CPU load, you can proactively address these issues, ensuring that your applications run smoothly and efficiently.

### Setting Up High CPU Load Alerts

To set up high CPU load alerts in Kubernetes, you typically use tools like Prometheus and Alertmanager. These tools work together to monitor metrics and trigger alerts based on predefined conditions.

#### Prometheus

Prometheus is an open-source systems monitoring and alerting toolkit. It collects and stores metrics from configured targets at regular intervals and provides a flexible query language to analyze this data.

##### Prometheus Configuration

To configure Prometheus to monitor CPU usage, you need to set up a scrape target for your Kubernetes cluster. Here’s an example configuration:

```yaml
scrape_configs:
  - job_name: 'kubernetes-nodes'
    kubernetes_sd_configs:
      - role: node
    metric_relabel_configs:
      - source_labels: [__meta_kubernetes_node_label_kubernetes_io_hostname]
        target_label: instance
```

This configuration tells Prometheus to scrape metrics from Kubernetes nodes.

#### Alertmanager

Alertmanager is responsible for routing alerts to the appropriate receivers. It can handle various types of alerts and route them based on specific criteria.

##### Alertmanager Configuration

Here’s an example configuration for Alertmanager:

```yaml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 1h
  receiver: 'email'

receivers:
  - name: 'email'
    email_configs:
      - to: 'admin@example.com'
```

This configuration sets up an email receiver for alerts.

### Creating High CPU Load Alerts

To create alerts for high CPU load, you define alert rules in Prometheus. These rules specify the conditions under which an alert should be triggered.

#### Example Alert Rule

Here’s an example alert rule for high CPU load:

```yaml
groups:
  - name: high_cpu_load_alerts
    rules:
      - alert: HighCPULoad
        expr: sum(rate(container_cpu_usage_seconds_total{namespace!="",pod!=""}[5m])) by (namespace) > 0.8 * sum(machine_cpu_cores)
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "High CPU Load Detected"
          description: "CPU usage exceeds 80% of available cores in namespace {{ $labels.namespace }}"
```

This rule triggers an alert if the CPU usage in any namespace exceeds 80% of the available cores for more than 5 minutes.

### Testing High CPU Load Alerts

To ensure that your high CPU load alerts are functioning correctly, you can simulate high CPU usage scenarios. This involves creating pods that consume excessive CPU resources and observing the behavior of the alerts.

#### Simulating High CPU Load

You can create a pod that consumes high CPU resources using a simple `busybox` image:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: cpu-load-test
spec:
  containers:
  - name: cpu-load-test
    image: busybox
    command: ["sh", "-c", "while true; do echo 'Running...'; sleep 0.1; done"]
```

Deploy this pod and observe the CPU usage metrics in Prometheus.

### Handling Pod Crash Looping

Pod crash looping is another critical issue that can occur in Kubernetes clusters. When a pod repeatedly crashes and restarts, it can generate a large number of alerts.

#### Pod Crash Looping Scenario

If a pod is crashing and restarting frequently, you can observe this behavior in the Kubernetes dashboard or through `kubectl` commands.

```bash
kubectl get pods --all-namespaces
```

You can also check the logs of the pod to understand the root cause of the crashes.

```bash
kubectl logs <pod-name> -n <namespace>
```

### Configuring Pod Crash Looping Alerts

To configure alerts for pod crash looping, you can define additional alert rules in Prometheus.

#### Example Pod Crash Looping Alert Rule

Here’s an example alert rule for pod crash looping:

```yaml
groups:
  - name: pod_crash_looping_alerts
    rules:
      - alert: PodCrashLooping
        expr: count_over_time(kube_pod_container_status_restarts_total{namespace!="",pod!=""}[5m]) > 5
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: "Pod Crash Looping Detected"
          description: "Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} has restarted more than 5 times in the last 5 minutes"
```

This rule triggers an alert if a pod has restarted more than 5 times in the last 5 minutes.

### Testing Pod Crash Looping Alerts

To test the pod crash looping alerts, you can create a pod that repeatedly crashes and restarts.

#### Simulating Pod Crash Looping

You can create a pod that crashes and restarts using a simple `nginx` image with a misconfigured command:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: crash-loop-test
spec:
  containers:
  - name: crash-loop-test
    image: nginx
    command: ["sh", "-c", "echo 'Running...'; sleep 1; exit 1"]
```

Deploy this pod and observe the restarts in Prometheus.

### How to Prevent / Defend Against High CPU Load and Pod Crash Looping

#### Detecting High CPU Load

To detect high CPU load, you can use Prometheus to monitor CPU usage metrics and set up alerts based on these metrics.

##### Secure Coding Practices

Ensure that your applications are optimized for CPU usage. Avoid unnecessary computations and use efficient algorithms.

##### Configuration Hardening

Configure your Kubernetes cluster to limit CPU usage for pods. Use resource limits and requests to control CPU allocation.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  containers:
  - name: secure-container
    image: nginx
    resources:
      limits:
        cpu: "0.5"
      requests:
        cpu: "0.2"
```

#### Preventing Pod Crash Looping

To prevent pod crash looping, ensure that your applications are robust and can handle errors gracefully.

##### Secure Coding Practices

Implement proper error handling in your applications. Ensure that your applications can recover from errors without crashing.

##### Configuration Hardening

Configure your Kubernetes cluster to limit the number of restarts for pods. Use liveness and readiness probes to detect and recover from failures.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: secure-pod
spec:
  containers:
  - name: secure-container
    image: nginx
    livenessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 30
      periodSeconds: 10
    readinessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 10
```

### Real-World Examples and Recent Breaches

#### Real-World Example: High CPU Load in Production

In a recent incident, a production environment experienced high CPU load due to a misconfigured application. The application was consuming excessive CPU resources, leading to degraded performance and service outages. By setting up high CPU load alerts, the team was able to quickly identify and resolve the issue.

#### Real-World Example: Pod Crash Looping in Production

Another incident involved a pod that was repeatedly crashing and restarting due to a misconfigured command. The team set up pod crash looping alerts and was able to quickly identify and resolve the issue.

### Conclusion

Monitoring high CPU load and pod crash looping is crucial for maintaining the health and performance of a Kubernetes cluster. By setting up alerts and configuring your cluster appropriately, you can proactively address these issues and ensure that your applications run smoothly and efficiently.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but includes sections on monitoring and alerting.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills, including monitoring and alerting.
- **CloudGoat**: A cloud security training platform that includes exercises on monitoring and alerting in Kubernetes environments.
- **Pacu**: A cloud security testing framework that includes exercises on monitoring and alerting in AWS environments.

These labs provide practical experience in setting up and managing high CPU load and pod crash looping alerts in Kubernetes environments.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/13-Monitoring High CPU Load Alerts/00-Overview|Overview]] | [[02-Introduction to Monitoring High CPU Load Alerts|Introduction to Monitoring High CPU Load Alerts]]
