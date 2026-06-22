---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Prometheus Setup in Kubernetes Clusters

Prometheus is an open-source monitoring system and time series database designed for monitoring and alerting. It collects metrics from configured targets at specified intervals and stores them internally. Prometheus is widely used in Kubernetes clusters to monitor the health and performance of applications and services.

### Configuration File

The configuration file is where Prometheus defines what endpoints it should scrape. These endpoints typically expose a `/metrics` endpoint, which Prometheus uses to gather data. The configuration file contains a list of targets, each with its own set of labels and scrape intervals.

#### Structure of the Configuration File

The configuration file is written in YAML format. Here is an example of a basic configuration file:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
```

In this example, `scrape_interval` specifies how often Prometheus should scrape the metrics from the targets. The `job_name` is a label that identifies the job being scraped. The `static_configs` section lists the targets to be scraped.

#### Example of a Real-World Configuration

Consider a more complex setup where multiple services are being monitored:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'kubernetes-nodes'
    kubernetes_sd_configs:
      - role: node
    relabel_configs:
      - action: labelmap
        regex: __meta_kubernetes_node_label_(.+)
      - target_label: __address__
        replacement: kubernetes.default.svc:443
      - source_labels: [__meta_kubernetes_node_name]
        regex: (.+)
        target_label: __metrics_path__
        replacement: /api/v1/nodes/${1}/proxy/metrics

  - job_name: 'kubernetes-pods'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        regex: (.+)
        target_label: __metrics_path__
        replacement: $1
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        regex: ([^:]+)(?::\d+)?;(\d+)
        target_label: __address__
        replacement: $1:$2
      - action: labelmap
        regex: __meta_kubernetes_pod_label_(.+)
```

This configuration file sets up scraping for Kubernetes nodes and pods. The `kubernetes_sd_configs` section uses the Kubernetes service discovery mechanism to automatically discover and scrape metrics from nodes and pods.

### Rules File

The rules file defines different rules for Prometheus. These rules can be alerting rules, recording rules, or grouping rules. Alerting rules define conditions under which alerts should be triggered, such as when CPU usage exceeds a certain threshold.

#### Structure of the Rules File

Here is an example of a rules file:

```yaml
groups:
  - name: example
    rules:
      - alert: HighCPUUsage
        expr: sum(rate(node_cpu_seconds_total{mode="idle"}[5m])) BY (instance) < 0.1
        for: 10m
        labels:
          severity: critical
        annotations:
          summary: "High CPU usage on {{ $labels.instance }}"
          description: "{{ $labels.instance }} has high CPU usage."
```

In this example, the `alert` rule `HighCPUUsage` triggers an alert when the idle CPU usage falls below 10% for 10 minutes. The `expr` field contains the PromQL expression that evaluates the condition. The `for` field specifies how long the condition must hold before the alert is fired.

### Mounting Configuration Files into Prometheus Pod

Both the configuration file and the rules file are mounted into the Prometheus pod. This allows Prometheus to access and reload the configuration dynamically.

#### Pod Configuration

Here is an example of a Kubernetes deployment for Prometheus:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:v2.32.0
        args:
        - "--config.file=/etc/prometheus/prometheus.yml"
        - "--storage.tsdb.path=/prometheus/"
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config-volume
          mountPath: /etc/prometheus/
        - name: storage-volume
          mountPath: /prometheus/
      volumes:
      - name: config-volume
        configMap:
          name: prometheus-config
      - name: storage-volume
        emptyDir: {}
```

In this deployment, the `configMap` named `prometheus-config` is mounted into the `/etc/prometheus/` directory of the Prometheus container. This allows Prometheus to access the configuration file and rules file.

### Config Reloader

The config reloader is a helper container that helps Prometheus reload its configuration when changes occur. It watches for changes in the configuration file and reloads the configuration accordingly.

#### Config Reloader Configuration

Here is an example of how the config reloader is configured:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: prometheus-deployment
spec:
  replicas: 1
  selector:
    matchLabels:
      app: prometheus
  template:
    metadata:
      labels:
        app: prometheus
    spec:
      containers:
      - name: prometheus
        image: prom/prometheus:v2.32.0
        args:
        - "--config.file=/etc/prometheus/prometheus.yml"
        - "--storage.tsdb.path=/prometheus/"
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: config-volume
          mountPath: /etc/prometheus/
        - name: storage-volume
          mountPath: /prometheus/
      - name: config-reloader
        image: jimmidyson/config-reload:v0.4.0
        args:
        - --webhook-url=http://localhost:9090/-/reload
        - --config-file-path=/etc/prometheus/prometheus.yml
        volumeMounts:
        - name: config-volume
          mountPath: /etc/prometheus/
      volumes:
      - name: config-volume
        configMap:
          name: prometheus-config
      - name: storage-volume
        emptyDir: {}
```

In this example, the `config-reloader` container is configured to watch for changes in the configuration file and trigger a reload of the configuration using the `/-/reload` endpoint of Prometheus.

### Accessing the Prometheus Endpoint

Prometheus runs on port 9090 by default. The endpoint is accessible via this port. The mount path inside the pod is `/etc/prometheus/`, which is where the configuration and rules files are mounted.

#### Example of Accessing the Prometheus Endpoint

To access the Prometheus endpoint, you can use the following command:

```bash
curl http://<prometheus-service-ip>:9090
```

This will return the Prometheus UI, which provides a dashboard for monitoring and querying metrics.

### Where Does the Configuration Come From?

The configuration and rules files can come from various sources, such as a ConfigMap in Kubernetes, a file stored in a persistent volume, or a remote server. The specific source depends on the deployment strategy and requirements.

#### Example of Using a ConfigMap

Here is an example of a ConfigMap for the Prometheus configuration:

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: prometheus-config
data:
  prometheus.yml: |
    global:
      scrape_interval: 15s

    scrape_configs:
      - job_name: 'prometheus'
        static_configs:
          - targets: ['localhost:9090']
```

This ConfigMap is referenced in the deployment configuration to provide the configuration file to Prometheus.

### Pitfalls and Best Practices

#### Common Mistakes

1. **Incorrect Configuration**: Ensure that the configuration file is correctly formatted and that all targets are reachable.
2. **Insufficient Permissions**: Ensure that the Prometheus pod has the necessary permissions to access the configuration and rules files.
3. **Overloading Prometheus**: Avoid configuring too many targets or complex queries that can overload Prometheus.

#### Best Practices

1. **Use Service Discovery**: Utilize Kubernetes service discovery mechanisms to automatically discover and scrape metrics from services.
2. **Regularly Update Prometheus**: Keep Prometheus and its dependencies up-to-date to benefit from the latest features and security patches.
3. **Monitor Prometheus Itself**: Set up monitoring for Prometheus to ensure it is functioning correctly and to detect any issues early.

### How to Prevent / Defend

#### Detection

1. **Monitoring Prometheus Metrics**: Monitor Prometheus's internal metrics to detect any anomalies or performance issues.
2. **Alerting**: Set up alerts for critical conditions, such as high CPU usage or memory leaks.

#### Prevention

1. **Secure Configuration Files**: Ensure that configuration files are securely stored and accessed only by authorized components.
2. **Limit Permissions**: Restrict the permissions of the Prometheus pod to the minimum required to perform its tasks.
3. **Regular Audits**: Regularly audit the Prometheus configuration and rules to ensure they are up-to-date and secure.

#### Secure Coding Fixes

Here is an example of a vulnerable configuration file and its secure counterpart:

**Vulnerable Configuration**

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
```

**Secure Configuration**

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'prometheus'
    kubernetes_sd_configs:
      - role: pod
    relabel_configs:
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_scrape]
        regex: true
      - source_labels: [__meta_kubernetes_pod_annotation_prometheus_io_path]
        regex: (.+)
        target_label: __metrics_path__
        replacement: $1
      - source_labels: [__address__, __meta_kubernetes_pod_annotation_prometheus_io_port]
        regex: ([^:]+)(?::\d+)?;(\d+)
        target_label: __address__
        replacement: $1:$2
      - action: labelmap
        regex: __meta_kubernetes_pod_label_(.+)
```

### Conclusion

Setting up Prometheus in a Kubernetes cluster involves configuring the targets to be scraped, defining rules for alerting and recording, and ensuring the configuration files are properly mounted and reloaded. By following best practices and securing the configuration, you can effectively monitor and manage your Kubernetes environment.

### Practice Labs

For hands-on practice with Prometheus setup in Kubernetes, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a module on monitoring and alerting with Prometheus.
- **OWASP Juice Shop**: Includes a section on setting up monitoring tools like Prometheus.
- **Kubernetes Goat**: Provides scenarios for setting up and securing Prometheus in a Kubernetes cluster.

These labs will help you gain practical experience in configuring and managing Prometheus in a Kubernetes environment.

---
<!-- nav -->
[[04-Introduction to Prometheus in Kubernetes|Introduction to Prometheus in Kubernetes]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/18-Prometheus Setup In Kubernetes Clusters/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/18-Prometheus Setup In Kubernetes Clusters/06-Practice Questions & Answers|Practice Questions & Answers]]
