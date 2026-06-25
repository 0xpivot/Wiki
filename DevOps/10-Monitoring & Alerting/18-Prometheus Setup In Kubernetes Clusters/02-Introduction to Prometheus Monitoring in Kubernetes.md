---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Prometheus Monitoring in Kubernetes

Prometheus is an open-source systems monitoring and alerting toolkit originally built at SoundCloud. It is now a Cloud Native Computing Foundation (CNCF) project. Prometheus is widely used in Kubernetes environments due to its ability to collect and store metrics from various sources, including Kubernetes components, applications, and services. This chapter will delve into setting up Prometheus in a Kubernetes cluster, explaining the concepts, configurations, and practical steps involved.

### Background Theory

Before diving into the setup process, it’s essential to understand the core components and concepts of Prometheus:

1. **Prometheus Server**: The central component that scrapes metrics from configured targets and stores them in a time series database.
2. **Metrics**: Data points collected from various sources, such as CPU usage, memory consumption, and application-specific metrics.
3. **Scraping**: The process by which Prometheus periodically queries targets to retrieve metrics.
4. **Time Series Database**: A specialized database designed to store and query time-stamped data efficiently.
5. **Alertmanager**: A component that handles alerts sent by Prometheus and routes them to the appropriate recipients.
6. **Service Discovery**: Mechanisms that allow Prometheus to discover and monitor targets dynamically.

### Prometheus Configuration Files

The setup of Prometheus in a Kubernetes cluster involves several configuration files. These files define how Prometheus should behave, what metrics to scrape, and how to handle alerts. The primary configuration files include:

1. **prometheus.yml**: The main configuration file for the Prometheus server.
2. **rules.yml**: Contains predefined rules for alerting and recording.
3. **secrets.yaml**: Stores sensitive information like usernames and passwords for accessing certain resources.

#### Example `prometheus.yml` Configuration

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
```

This configuration file defines a job named `kubernetes-nodes`, which scrapes metrics from Kubernetes nodes. The `relabel_configs` section maps labels and adjusts the scraping behavior.

### Secrets Management

In Kubernetes, sensitive data such as usernames and passwords should be stored securely using `Secrets`. This ensures that credentials are not exposed in plain text within the cluster.

#### Example `secrets.yaml`

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: prometheus-secrets
type: Opaque
data:
  username: dXNlcm5hbWU=  # Base64 encoded value
  password: cGFzc3dvcmQ=  # Base64 encoded value
```

This secret stores the username and password for accessing certain resources. The values are base64 encoded for security.

### Grafana Integration

Grafana is a popular visualization tool that integrates seamlessly with Prometheus. It allows users to create dashboards and visualize metrics collected by Prometheus.

#### Example Grafana Configuration

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: grafana-config
data:
  grafana.ini: |
    [server]
    http_port = 3000
    domain = localhost
    protocol = http
    root_url = %(protocol)s://%(domain)s:%(http_port)s/
```

This configuration file sets up the basic settings for Grafana, including the port and domain.

### Custom Resource Definitions (CRDs)

Custom Resource Definitions (CRDs) are a way to extend the Kubernetes API with custom objects. In the context of Prometheus, CRDs are used to manage and configure Prometheus instances within the cluster.

#### Example CRD Definition

```yaml
apiVersion: apiextensions.k8s.io/v1
kind: CustomResourceDefinition
metadata:
  name: prometheuses.monitoring.coreos.com
spec:
  group: monitoring.coreos.com
  versions:
    - name: v1
      served: true
      storage: true
  scope: Namespaced
  names:
    plural: prometheuses
    singular: prometheus
    kind: Prometheus
    listKind: PrometheusList
```

This CRD defines a new resource type called `Prometheus` within the `monitoring.coreos.com` group.

### StatefulSets in Kubernetes

StatefulSets are used to manage stateful applications in Kubernetes. They ensure that each pod has a unique identity and persistent storage. In the context of Prometheus, StatefulSets are used to manage the Prometheus server and its associated components.

#### Example StatefulSet Definition

```yaml
apiVersion: apps/v1
kind: StatefulSet
metadata:
  name: prometheus
spec:
  serviceName: "prometheus"
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
        image: prom/prometheus:v2.32.1
        ports:
        - containerPort: 9090
        volumeMounts:
        - name: prometheus-storage
          mountPath: /prometheus
  volumeClaimTemplates:
  - metadata:
      name: prometheus-storage
    spec:
      accessModes: ["ReadWriteOnce"]
      resources:
        requests:
          storage: 10Gi
```

This StatefulSet definition creates a single replica of the Prometheus server, using the `prom/prometheus:v2.32.1` image. It also defines a PersistentVolumeClaim for storing Prometheus data.

### Setting Up Prometheus in Kubernetes

To set up Prometheus in a Kubernetes cluster, follow these steps:

1. **Deploy the Prometheus Operator**: The Prometheus Operator simplifies the deployment and management of Prometheus in Kubernetes.
2. **Create the Prometheus CRD**: Define the custom resource for Prometheus.
3. **Deploy the Prometheus StatefulSet**: Create the StatefulSet for the Prometheus server.
4. **Configure Metrics Scraping**: Set up the scraping configuration in `prometheus.yml`.
5. **Integrate with Grafana**: Deploy Grafana and configure it to use Prometheus as the data source.

#### Example Deployment Commands

```sh
kubectl apply -f prometheus-operator.yaml
kubectl apply -f prometheus-crd.yaml
kubectl apply -f prometheus-statefulset.yaml
kubectl apply -f grafana-deployment.yaml
```

### Common Pitfalls and How to Prevent Them

1. **Incorrect Configuration**: Ensure that the configuration files (`prometheus.yml`, `rules.yml`, etc.) are correctly formatted and contain the necessary settings.
2. **Security Vulnerabilities**: Use `Secrets` to store sensitive information securely. Regularly update the Prometheus server and related components to patch known vulnerabilities.
3. **Insufficient Storage**: Allocate sufficient storage for the Prometheus server to avoid data loss. Monitor disk usage and adjust storage settings as needed.

#### Secure Configuration Example

**Vulnerable Configuration**

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
      - job_name: 'kubernetes-nodes'
        kubernetes_sd_configs:
          - role: node
```

**Secure Configuration**

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
```

### Real-World Examples and Recent CVEs

Recent vulnerabilities in Prometheus include:

- **CVE-2021-25741**: A remote code execution vulnerability in the `prometheus-alertmanager` component.
- **CVE-2-2021-25742**: An information disclosure vulnerability in the `prometheus-server` component.

These vulnerabilities highlight the importance of keeping Prometheus and related components up-to-date and securing sensitive data.

### Detection and Prevention

To detect and prevent security issues in Prometheus, implement the following measures:

1. **Regular Updates**: Keep Prometheus and related components updated to the latest versions.
2. **Monitoring**: Use tools like `Falco` to monitor and detect suspicious activity within the cluster.
3. **Secure Configuration**: Follow best practices for configuring Prometheus and related components securely.

#### Example Falco Rule

```yaml
- rule: Prometheus Unauthorized Access
  desc: Detect unauthorized access attempts to Prometheus
  condition: evt.type == "open" and evt.arg.path contains "/prometheus"
  output: "Unauthorized access attempt to Prometheus: %proc.name %evt.arg.path"
  priority: WARNING
```

### Conclusion

Setting up Prometheus in a Kubernetes cluster involves several steps, including deploying the Prometheus Operator, creating the Prometheus CRD, and configuring metrics scraping. By following best practices and securing sensitive data, you can ensure that Prometheus operates effectively and securely within your Kubernetes environment.

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **Kubernetes Goat**: A Kubernetes-based security training platform.

These labs provide practical experience in setting up and managing Prometheus in a Kubernetes environment.

---
<!-- nav -->
[[01-Introduction to Prometheus Monitoring Stack in Kubernetes|Introduction to Prometheus Monitoring Stack in Kubernetes]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/18-Prometheus Setup In Kubernetes Clusters/00-Overview|Overview]] | [[03-Introduction to Prometheus in Kubernetes Clusters|Introduction to Prometheus in Kubernetes Clusters]]
