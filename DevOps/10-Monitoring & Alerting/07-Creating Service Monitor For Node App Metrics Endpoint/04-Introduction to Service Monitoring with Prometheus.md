---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Service Monitoring with Prometheus

In the context of modern DevOps practices, monitoring the health and performance of applications is crucial. One of the most popular tools for this purpose is Prometheus, an open-source systems monitoring and alerting toolkit. This chapter will delve into creating a service monitor for a Node.js application's metrics endpoint using Prometheus. We'll cover the theoretical background, practical implementation, potential pitfalls, and security considerations.

### Background Theory

Prometheus is designed to scrape metrics from various endpoints and store them in a time-series database. These metrics can then be queried and visualized to provide insights into the system's behavior. A key component of Prometheus is the `service monitor`, which automates the discovery and scraping of metrics from services running in a Kubernetes cluster.

#### Key Concepts

- **Metrics**: Data points that represent the state of a system at a particular time. They can be simple counters, gauges, histograms, or summaries.
- **Service Monitor**: A Kubernetes custom resource definition (CRD) that defines how Prometheus should scrape metrics from a set of services.
- **Job**: A logical grouping of targets that Prometheus scrapes. Each job corresponds to a specific set of targets and scraping intervals.

### Setting Up the Environment

To follow along with this chapter, you'll need:

- A Kubernetes cluster (e.g., Minikube, GKE, EKS)
- Prometheus installed in your cluster (e.g., via Helm chart)
- A Node.js application exposing metrics

#### Example Node.js Application

Let's consider a simple Node.js application that exposes metrics via an HTTP endpoint. Here's a basic setup:

```javascript
// app.js
const express = require('express');
const promClient = require('prom-client');

const app = express();
const port = process.env.PORT || 3000;

// Create a new registry
const register = new promClient.Registry();

// Set the default registry
promClient.collectDefaultMetrics({ register });

// Create a counter metric
const httpRequestCounter = new promClient.Counter({
    name: 'http_requests_total',
    help: 'Total number of HTTP requests',
    labelNames: ['method', 'path'],
});

app.get('/', (req, res) => {
    httpRequestCounter.inc({ method: req.method, path: req.path });
    res.send('Hello World!');
});

app.listen(port, () => {
    console.log(`Server running on port ${port}`);
});
```

This application uses the `prom-client` library to expose metrics. The `http_requests_total` counter tracks the number of HTTP requests made to the `/` endpoint.

### Configuring Prometheus

Prometheus needs to be configured to scrape metrics from the Node.js application. This is done using a `service monitor` CRD.

#### Creating a Service Monitor

A `service monitor` is defined using a YAML manifest. Here’s an example:

```yaml
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: node-app-monitor
  namespace: default
spec:
  selector:
    matchLabels:
      app: node-app
  endpoints:
  - port: http
    interval: 30s
    path: /metrics
```

This manifest creates a `service monitor` named `node-app-monitor` in the `default` namespace. It selects pods labeled with `app: node-app` and configures Prometheus to scrape metrics from the `/metrics` endpoint every 30 seconds.

### Deploying the Application and Service Monitor

First, deploy the Node.js application to your Kubernetes cluster:

```yaml
# node-app-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: node-app
  namespace: default
spec:
  replicas: 1
  selector:
    matchLabels:
      app: node-app
  template:
    metadata:
      labels:
        app: node-app
    spec:
      containers:
      - name: node-app
        image: your-node-app-image
        ports:
        - containerPort: 3000
---
apiVersion: v1
kind: Service
metadata:
  name: node-app-service
  namespace: default
spec:
  selector:
    app: node-app
  ports:
  - protocol: TCP
    port: 80
    targetPort: 3000
```

Apply the deployment and service:

```bash
kubectl apply -f node-app-deployment.yaml
```

Next, apply the `service monitor`:

```bash
kubectl apply -f service-monitor.yaml
```

### Verifying the Setup

Once the application and `service monitor` are deployed, Prometheus should start scraping metrics from the Node.js application. You can verify this by accessing the Prometheus UI and querying the metrics.

#### Accessing Prometheus UI

If you installed Prometheus via a Helm chart, you can access the UI using:

```bash
kubectl port-forward svc/prometheus-server 9090:9090
```

Then, navigate to `http://localhost:9090` in your browser.

#### Querying Metrics

In the Prometheus UI, you can query the metrics exposed by the Node.js application. For example, to query the `http_requests_total` counter:

```promql
http_requests_total
```

This query will return the total number of HTTP requests made to the `/` endpoint.

### Understanding Labels

Prometheus automatically injects labels into the metrics it collects. These labels provide additional context about the source of the metrics. For example, the `http_requests_total` counter might have labels such as `container`, `pod`, `service`, `endpoint`, and `job`.

#### Example Labels

```json
{
  "http_requests_total": {
    "labels": {
      "container": "node-app",
      "pod": "node-app-5b7c6d5b7c",
      "service": "node-app-service",
      "endpoint": "/metrics",
      "job": "node-app-monitor"
    },
    "value": 2
  }
}
```

These labels help in filtering and aggregating metrics across different dimensions.

### Pitfalls and Best Practices

While setting up service monitors, there are several common pitfalls to avoid:

1. **Incorrect Scrape Intervals**: Ensure that the scrape interval is appropriate for the application's load. Too frequent scraping can lead to performance issues, while infrequent scraping may miss important events.
2. **Label Management**: Properly manage labels to ensure that metrics are easily filterable and aggregatable.
3. **Resource Constraints**: Monitor the resource usage of Prometheus and adjust configurations as needed to avoid overloading the system.

### Security Considerations

Monitoring systems like Prometheus handle sensitive data and can be a target for attacks. Here are some security best practices:

#### Secure Configuration

Ensure that Prometheus is properly secured:

- **Authentication and Authorization**: Use authentication mechanisms like OAuth2 or basic auth to restrict access to the Prometheus UI.
- **Network Isolation**: Run Prometheus in a secure network environment, isolated from other components.
- **TLS Encryption**: Enable TLS encryption for all communications between Prometheus and the monitored services.

#### Example Secure Configuration

Here’s an example of a secure Prometheus configuration:

```yaml
server:
  listenAddress: ":9090"
  tlsConfig:
    certFile: /etc/prometheus/prometheus.crt
    keyFile: /etc/prometheus/prometheus.key
web:
  externalUrl: "https://prometheus.example.com/"
  routePrefix: "/"
  enableAdminAPI: true
  enableWebhook: true
scrape_configs:
- job_name: 'node-app-monitor'
  static_configs:
  - targets: ['node-app-service.default.svc.cluster.local:80']
  scheme: https
  tls_config:
    ca_file: /etc/prometheus/ca.crt
```

This configuration enables TLS encryption for both the Prometheus server and the scrape targets.

### How to Prevent / Defend

#### Detection

Regularly monitor Prometheus logs and alerts for any suspicious activity. Use tools like Grafana to visualize and analyze metrics for anomalies.

#### Prevention

- **Use Strong Authentication**: Implement strong authentication mechanisms to protect access to Prometheus.
- **Limit Permissions**: Restrict permissions to only necessary users and roles.
- **Regular Audits**: Perform regular audits of Prometheus configurations and access logs.

#### Secure Coding Fixes

Compare the insecure and secure versions of the Prometheus configuration:

**Insecure Configuration**

```yaml
server:
  listenAddress: ":9090"
scrape_configs:
- job_name: 'node-app-monitor'
  static_configs:
  - targets: ['node-app-service.default.svc.cluster.local:80']
```

**Secure Configuration**

```yaml
server:
  listenAddress: ":9090"
  tlsConfig:
    certFile: /etc/prometheus/prometheus.crt
    keyFile: /etc/prometheus/prometheus.key
web:
  externalUrl: "https://prometheus.example.com/"
  routePrefix: "/"
  enableAdminAPI: true
  enableWebhook: true
scrape_configs:
- job_name: 'node-app-monitor'
  static_configs:
  - targets: ['node-app-service.default.svc.cluster.local:80']
  scheme: https
  tls_config:
    ca_file: /etc/prometheus/ca.crt
```

### Conclusion

Creating a service monitor for a Node.js application's metrics endpoint using Prometheus is a powerful way to gain visibility into the application's performance and health. By following best practices and implementing proper security measures, you can ensure that your monitoring setup is robust and secure.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but includes sections on monitoring and logging.
- **OWASP Juice Shop**: A deliberately insecure web application for learning about web security, including monitoring and logging.
- **Kubernetes Goat**: A Kubernetes-based security training platform that includes exercises on monitoring and logging.

By completing these labs, you can gain practical experience in setting up and securing monitoring systems like Prometheus.

---
<!-- nav -->
[[03-Introduction to Service Monitoring in DevOps|Introduction to Service Monitoring in DevOps]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/07-Creating Service Monitor For Node App Metrics Endpoint/00-Overview|Overview]] | [[05-Introduction to Service Monitors in Kubernetes|Introduction to Service Monitors in Kubernetes]]
