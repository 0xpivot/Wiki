---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Prometheus Monitoring in Dynamic Environments

### Introduction to Prometheus

Prometheus is an open-source systems monitoring and alerting toolkit originally built at SoundCloud. It is designed to be highly scalable and flexible, making it suitable for dynamic environments such as cloud-native applications and microservices architectures. One of the key features of Prometheus is its ability to collect metrics from various sources using a simple and efficient pull model.

### Metrics Format in Prometheus

Prometheus uses a human-readable text-based format for metrics. Each metric entry consists of a name, labels, and a value. Additionally, metrics can have `type` and `help` attributes to enhance their readability and provide context.

#### Type Attribute

The `type` attribute specifies the kind of metric being recorded. There are three primary types:

1. **Counter**: This type is used for metrics that represent cumulative counts, such as the number of exceptions or the number of requests received. Counters can only increase or reset to zero upon restart.
   
   ```plaintext
   http_requests_total{method="post",code="200"} 15
   ```

   Here, `http_requests_total` is a counter that tracks the total number of HTTP POST requests that resulted in a 200 status code.

2. **Gauge**: Gauges represent metrics that can fluctuate up and down, such as the current CPU usage or the number of concurrent requests. Gauges can take any value within a range.

   ```plaintext
   cpu_usage_percent 75
   ```

   In this example, `cpu_usage_percent` is a gauge that indicates the current percentage of CPU usage.

3. **Histogram**: Histograms are used to track the distribution of values, such as the size of requests or the duration of operations. They provide quantiles and buckets to analyze the data.

   ```plaintext
   request_size_bytes_bucket{le="500"} 10
   request_size_bytes_bucket{le="1000"} 15
   request_size_bytes_sum 1250
   request_size_bytes_count 15
   ```

   Here, `request_size_bytes_bucket` is a histogram that records the number of requests whose sizes fall within specified ranges (`le` stands for "less than or equal to"). The `sum` and `count` fields provide additional statistical information.

### Help Attribute

The `help` attribute provides a description of the metric, explaining what it measures and why it is important. This helps users understand the context and significance of the metric.

```plaintext
# HELP http_requests_total Number of HTTP requests received.
# TYPE http_requests_total counter
http_requests_total{method="post",code="200"} 15
```

In this example, the `help` attribute explains that `http_requests_total` tracks the number of HTTP requests received, categorized by method and status code.

### How Prometheus Collects Metrics

Prometheus collects metrics from targets using a pull-based model. Targets must expose an HTTP endpoint that returns metrics in a format that Prometheus understands. By default, this endpoint is `/metrics`.

#### Steps for Metric Collection

1. **Expose Metrics Endpoint**: The target service must expose a `/metrics` endpoint that returns metrics in the Prometheus text format.
   
   ```plaintext
   GET /metrics
   HTTP/1.1 200 OK
   Content-Type: text/plain; version=0.0.4
   
   # HELP http_requests_total Number of HTTP requests received.
   # TYPE http_requests_total counter
   http_requests_total{method="post",code="200"} 15
   
   # HELP cpu_usage_percent Current CPU usage percentage.
   # TYPE cpu_usage_percent gauge
   cpu_usage_percent 75
   ```

2. **Prometheus Scrapes Metrics**: Prometheus periodically scrapes the `/metrics` endpoint of each target to collect the latest metric values.

   ```mermaid
sequenceDiagram
     participant Prometheus
     participant TargetService
     Prometheus->>TargetService: GET /metrics
     TargetService-->>Prometheus: HTTP/1.1 200 OK
     TargetService-->>Prometheus: Content-Type: text/plain; version=0.0.4
     TargetService-->>Prometheus: # HELP http_requests_total Number of HTTP requests received.
     TargetService-->>Prometheus: # TYPE http_requests_total counter
     TargetService-->>Prometheus: http_requests_total{method="post",code="200"} 15
     TargetService-->>Prometheus: # HELP cpu_usage_percent Current CPU usage percentage.
     TargetService-->>Prometheus: # TYPE cpu_usage_percent gauge
     TargetService-->>Prometheus: cpu_usage_percent 75
```

### Exporters for Non-Native Prometheus Endpoints

Many services do not natively expose Prometheus-compatible metrics. In such cases, an exporter is used to translate the service's metrics into a format that Prometheus can understand.

#### Example: Node Exporter

The Node Exporter is a popular exporter that exposes system and hardware metrics for Linux nodes. It runs as a daemon and exposes metrics via an HTTP server.

```plaintext
GET /metrics
HTTP/1.1 200 OK
Content-Type: text/plain; version=0.0.4

# HELP node_cpu_seconds_total Seconds the cpus spent in each mode.
# TYPE node_cpu_seconds_total counter
node_cpu_seconds_total{cpu="0",mode="idle"} 1.23456789e+08
node_cpu_seconds_total{cpu="0",mode="iowait"} 1.23456789e+07
node_cpu_seconds_total{cpu="0",mode="system"} 1.23456789e+07
node_cpu_seconds_total{cpu="0",mode="user"} 1.23456789e+07
```

### Real-World Examples and Recent Breaches

Prometheus has been widely adopted in various industries due to its robustness and flexibility. However, like any monitoring tool, it is not immune to security vulnerabilities.

#### CVE-2021-28909: Prometheus Remote Write API

In 2021, a critical vulnerability (CVE-2021-28909) was discovered in the Prometheus Remote Write API. This vulnerability allowed attackers to inject arbitrary metrics into the Prometheus database, potentially leading to data corruption or denial of service.

**How to Prevent / Defend**

1. **Secure Configuration**: Ensure that the Prometheus server is configured to only accept connections from trusted sources. Use firewall rules and network segmentation to restrict access.

2. **Authentication and Authorization**: Implement authentication and authorization mechanisms to control who can access the Prometheus server and its APIs. Use tools like OAuth2 Proxy or Prometheus Operator to manage access.

3. **Regular Updates**: Keep Prometheus and all related components up to date with the latest security patches and updates.

4. **Monitoring and Alerts**: Set up alerts to monitor for unusual activity or unauthorized access attempts. Use tools like Grafana to visualize and analyze Prometheus metrics.

### Pitfalls and Common Mistakes

1. **Incorrect Metric Types**: Using the wrong metric type can lead to incorrect data interpretation. For example, using a gauge for cumulative counts can result in unexpected behavior.

2. **Insufficient Documentation**: Failing to provide adequate documentation for metrics can make it difficult for users to understand their significance and context.

3. **Security Vulnerabilities**: Neglecting to secure Prometheus configurations and APIs can expose the system to attacks.

### Conclusion

Prometheus is a powerful tool for monitoring dynamic environments. Its text-based metrics format and pull-based model make it highly flexible and scalable. By understanding the different metric types and how Prometheus collects metrics, you can effectively monitor and troubleshoot your systems. Additionally, by implementing proper security measures, you can protect your Prometheus setup from potential vulnerabilities.

### Practice Labs

For hands-on experience with Prometheus, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises on securing Prometheus and other monitoring tools.
- **Grafana Learning Center**: Provides tutorials and labs on setting up and configuring Prometheus.
- **Prometheus Operator**: Official documentation and examples for deploying Prometheus in Kubernetes environments.

By combining theoretical knowledge with practical experience, you can become proficient in using Prometheus for effective monitoring and troubleshooting in dynamic environments.

---
<!-- nav -->
[[08-Prometheus Metrics Endpoint|Prometheus Metrics Endpoint]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/17-Prometheus Monitoring In Dynamic Environments/00-Overview|Overview]] | [[10-Querying Metrics Data with PromQL|Querying Metrics Data with PromQL]]
