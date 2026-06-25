---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Monitoring Kubernetes Microservices with Prometheus

### Introduction to Monitoring in Kubernetes

Monitoring is a critical aspect of managing a Kubernetes cluster, especially when dealing with microservices. A microservices architecture breaks down an application into smaller, independent services that communicate over a network. This approach increases flexibility and scalability but also introduces complexity in terms of monitoring and managing these services.

In Kubernetes, nodes are the physical or virtual machines that run your pods. Pods are the smallest deployable units in Kubernetes, containing one or more containers. Workloads such as Deployments, StatefulSets, and DaemonSets manage these pods. Services provide a stable endpoint for accessing these pods.

The primary goal of monitoring is to ensure that all components of the system are functioning correctly and efficiently. This includes:

1. **Node Resources**: Ensuring that nodes have sufficient CPU, memory, and disk space to run pods.
2. **Kubernetes Components**: Monitoring the health and performance of pods, deployments, and services.
3. **Applications**: Tracking the performance and availability of individual microservices and third-party applications.

### Node Resource Monitoring

#### Why Monitor Node Resources?

Nodes are the foundation of a Kubernetes cluster. If a node does not have enough resources, pods cannot run on it, leading to failures and downtime. Monitoring node resources helps in:

- **Proactive Management**: Identifying resource constraints before they cause issues.
- **Optimization**: Balancing workloads across nodes to maximize efficiency.
- **Troubleshooting**: Quickly identifying and resolving resource-related problems.

#### How to Monitor Node Resources

Prometheus is a popular open-source monitoring system that can be used to monitor Kubernetes nodes. Prometheus scrapes metrics from various sources and stores them in a time-series database. To monitor node resources, you can use the `node_exporter`, a Prometheus exporter that collects system metrics.

##### Example: Configuring `node_exporter`

1. **Deploy `node_exporter`**:
    ```yaml
    apiVersion: apps/v1
    kind: DaemonSet
    metadata:
      name: node-exporter
      namespace: monitoring
    spec:
      selector:
        matchLabels:
          app: node-exporter
      template:
        metadata:
          labels:
            app: node-exporter
        spec:
          containers:
          - name: node-exporter
            image: prom/node-exporter:v1.3.1
            args:
            - "--path.procfs=/host/proc"
            - "--path.sysfs=/host/sys"
            volumeMounts:
            - name: proc
              mountPath: /host/proc
            - name: sys
              mountPath: /host/sys
          volumes:
          - name: proc
            hostPath:
              path: /proc
          - name: sys
            hostPath:
              path: /sys
    ```

2. **Configure Prometheus to Scrape Metrics**:
    ```yaml
    scrape_configs:
      - job_name: 'kubernetes-nodes'
        static_configs:
          - targets: ['<node-ip>:9100']
    ```

3. **Example Metrics**:
    - `node_cpu_seconds_total`: Total CPU usage.
    - `node_memory_MemTotal_bytes`: Total memory available.
    - `node_filesystem_size_bytes`: Disk space usage.

### Monitoring Kubernetes Components

#### Why Monitor Kubernetes Components?

Monitoring Kubernetes components ensures that all pods, deployments, and services are running as expected. This includes:

- **Pod Health**: Checking if pods are running successfully or failing to start.
- **Service Availability**: Ensuring that services are accessible within the cluster.
- **Workload Status**: Monitoring the status of Deployments, StatefulSets, and DaemonSets.

#### How to Monitor Kubernetes Components

Prometheus can be configured to scrape metrics from the Kubernetes API server using the `kube-state-metrics` exporter.

##### Example: Configuring `kube-state-metrics`

1. **Deploy `kube-state-metrics`**:
    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: kube-state-metrics
      namespace: monitoring
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: kube-state-metrics
      template:
        metadata:
          labels:
            app: kube-state-metrics
        spec:
          containers:
          - name: kube-state-metrics
            image: quay.io/prometheus/kube-state-metrics:v2.3.0
            ports:
            - containerPort: 8080
            livenessProbe:
              httpGet:
                path: /healthz
                port: 8080
            readinessProbe:
              httpGet:
                path: /healthz
                port:  8080
            resources:
              requests:
                cpu: 100m
                memory: 200Mi
              limits:
                cpu: 200m
                memory: 400Mi
    ```

2. **Configure Prometheus to Scrape Metrics**:
    ```yaml
    scrape_configs:
      - job_name: 'kube-state-metrics'
        static_configs:
          - targets: ['<kube-state-metrics-service-ip>:8080']
    ```

3. **Example Metrics**:
    - `kube_pod_status_ready`: Indicates if a pod is ready.
    - `kube_deployment_status_replicas_available`: Number of available replicas in a deployment.
    - `kube_service_info`: Information about services.

### Monitoring Applications

#### Why Monitor Applications?

Monitoring applications ensures that microservices and third-party applications are performing as expected. This includes:

- **Third-Party Applications**: Monitoring databases, message brokers, and other external services.
- **Microservices**: Tracking the performance and availability of individual microservices.

#### Monitoring Third-Party Applications: Redis

Redis is a popular in-memory data store often used as a cache or message broker in microservices architectures. Monitoring Redis ensures that it is running correctly and is accessible within the cluster.

##### Example: Configuring Redis Exporter

1. **Deploy Redis Exporter**:
    ```yaml
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: redis-exporter
      namespace: monitoring
    spec:
      replicas: 1
      selector:
        matchLabels:
          app: redis-exporter
      template:
        metadata:
          labels:
            app: redis-exporter
        spec:
          containers:
          - name: redis-exporter
            image: oliver006/redis_exporter:v1.21.0
            ports:
            - containerPort: 9121
            env:
            - name: REDIS_ADDR
              value: 'redis://<redis-service-ip>:6379'
    ```

2. **Configure Prometheus to Scrape Metrics**:
    ```yaml
    scrape_configs:
      - job_name: 'redis-exporter'
        static_configs:
          - targets: ['<redis-exporter-service-ip>:9121']
    ```

3. **Example Metrics**:
    - `redis_connected_clients`: Number of connected clients.
    - `redis_used_memory`: Amount of memory used by Redis.
    - `redis_commands_total`: Total number of commands executed.

#### Monitoring Microservices

Monitoring microservices involves tracking their performance and availability. This includes:

- **Request Count**: Number of requests received by a microservice.
- **Error Responses**: Number of error responses returned by a microservice.

##### Example: Configuring Prometheus to Monitor Microservices

1. **Instrument Your Application**:
    ```go
    package main

    import (
        "net/http"

        "github.com/prometheus/client_golang/prometheus"
        "github.com/prometheus/client_golang/prometheus/promhttp"
    )

    var (
        requestsTotal = prometheus.NewCounter(
            prometheus.CounterOpts{
                Name: "requests_total",
                Help: "Total number of requests received.",
            },
        )
        errorsTotal = prometheus.NewCounter(
            prometheus.CounterOpts{
                Name: "errors_total",
                Help: "Total number of error responses returned.",
            },
        )
    )

    func init() {
        prometheus.MustRegister(requestsTotal)
        prometheus.MustRegister(errorsTotal)
    }

    func handler(w http.ResponseWriter, r *http.Request) {
        requestsTotal.Inc()
        // Process request
        if err := processRequest(r); err != nil {
            errorsTotal.Inc()
            http.Error(w, err.Error(), http.StatusInternalServerError)
            return
        }
        w.WriteHeader(http.StatusOK)
    }

    func main() {
        http.HandleFunc("/", handler)
        http.Handle("/metrics", promhttp.Handler())
        http.ListenAndServe(":8080", nil)
    }
    ```

2. **Configure Prometheus to Scrape Metrics**:
    ```yaml
    scrape_configs:
      - job_name: 'microservices'
        static_configs:
          - targets: ['<microservice-service-ip>:8080']
    ```

3. **Example Metrics**:
    - `requests_total`: Total number of requests received.
    - `errors_total`: Total number of error responses returned.

### Real-World Examples and Breaches

#### Recent CVEs and Breaches

Monitoring plays a crucial role in detecting and preventing security breaches. For example, the Log4j vulnerability (CVE-2021-44228) highlighted the importance of monitoring logs and system metrics to detect unusual activity.

##### Example: Detecting Log4j Exploits

1. **Monitor Logs**:
    - Use tools like Fluentd or Logstash to collect and analyze logs.
    - Look for suspicious patterns such as repeated attempts to access sensitive information.

2. **Monitor System Metrics**:
    - Use Prometheus to monitor system metrics like CPU usage, memory usage, and network traffic.
    - Set up alerts for unusual spikes in these metrics.

### How to Prevent / Defend

#### Detection

1. **Log Analysis**:
    - Use tools like Elasticsearch, Logstash, and Kibana (ELK stack) to analyze logs.
    - Set up alerts for suspicious patterns.

2. **Metric Monitoring**:
    - Use Prometheus to monitor system metrics.
    - Set up alerts for unusual spikes in CPU, memory, and network traffic.

#### Prevention

1. **Secure Configuration**:
    - Harden your Kubernetes cluster by following the Kubernetes Security Best Practices.
    - Use tools like kube-bench to check your cluster's security posture.

2. **Regular Audits**:
    - Perform regular security audits to identify and mitigate vulnerabilities.
    - Use tools like Trivy to scan your images for known vulnerabilities.

#### Secure Coding Fixes

1. **Instrumentation**:
    - Instrument your applications to expose metrics.
    - Use libraries like Prometheus client to expose metrics.

2. **Configuration Hardening**:
    - Harden your Prometheus configuration to prevent unauthorized access.
    - Use authentication and authorization mechanisms like OAuth2 Proxy.

### Conclusion

Monitoring Kubernetes microservices with Prometheus is essential for ensuring the health and performance of your cluster. By monitoring node resources, Kubernetes components, and applications, you can proactively manage your cluster and quickly identify and resolve issues. Using tools like `node_exporter`, `kube-state-metrics`, and custom exporters, you can gain deep insights into the behavior of your cluster and applications.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security but also covers Kubernetes and Prometheus.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **Kubernetes Goat**: A Kubernetes-based security training platform.

These labs provide practical experience in setting up and monitoring Kubernetes clusters with Prometheus.

---
<!-- nav -->
[[01-Introduction to Monitoring Kubernetes Microservices with Prometheus|Introduction to Monitoring Kubernetes Microservices with Prometheus]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/14-Monitoring Kubernetes Microservices With Prometheus/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/14-Monitoring Kubernetes Microservices With Prometheus/03-Practice Questions & Answers|Practice Questions & Answers]]
