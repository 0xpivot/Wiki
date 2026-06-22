---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Defining Custom Metrics

### Counter Metrics

A counter metric is used to count events, such as the number of HTTP requests received by an application. In the context of the lecture, we want to expose the number of total HTTP requests to our application.

#### Example: Counting HTTP Requests

Let's consider a simple Python application using the `prometheus_client` library to count HTTP requests.

```python
from prometheus_client import start_http_server, Counter

# Define a counter metric
http_requests_total = Counter('http_requests_total', 'Total number of HTTP requests')

# Increment the counter when a new request is received
def handle_request():
    http_requests_total.inc()

# Start the HTTP server to expose metrics
start_http_server(8000)

# Simulate handling requests
for _ in range(10):
    handle_request()
```

### Histogram Metrics

A histogram metric is used to measure the distribution of a set of values. In the context of the lecture, we want to expose the duration of HTTP requests using a histogram.

#### Example: Measuring Request Duration

Let's extend the previous example to include a histogram metric for measuring the duration of HTTP requests.

```python
from prometheus_client import start_http_server, Counter, Histogram
import time

# Define a histogram metric
request_duration_seconds = Histogram('request_duration_seconds', 'Duration of HTTP requests',
                                     buckets=[0.1, 0.5, 1.0, 2.5, 5.0])

# Increment the counter and record the duration when a new request is received
def handle_request():
    start_time = time.time()
    # Simulate processing time
    time.sleep(0.3)
    end_time = time.time()
    duration = end_time - start_time
    request_duration_seconds.observe(duration)
    http_requests_total.inc()

# Start the HTTP server to expose metrics
start_http_server(8000)

# Simulate handling requests
for _ in range(10):
    handle_request()
```

### Explanation of Histogram Buckets

Histograms work by dividing the range of possible values into buckets. Each bucket represents a range of values. When a value is recorded, it is assigned to the appropriate bucket based on its value. This allows us to measure the distribution of values and understand how they are spread out.

For example, in the above code, the `buckets` parameter is set to `[0.1, 0.5, 1.0, 2.5, 5.0]`. This means that the histogram will have the following buckets:

- 0.1 to 0.5 seconds
- 0.5 to 1.0 seconds
- 1.0 to 2.5 seconds
- 2.5 to 5.0 seconds
- Greater than 5.0 seconds

Each request duration is recorded and assigned to the appropriate bucket.

### How to Prevent / Defend

#### Detection

To detect potential issues with metrics, you can use Prometheus alerts. Alerts can be configured to trigger when certain conditions are met, such as when the number of HTTP requests exceeds a threshold or when the average request duration exceeds a certain value.

#### Prevention

To prevent issues with metrics, ensure that your application is properly instrumented and that you are collecting meaningful metrics. Avoid collecting unnecessary metrics that could clutter your monitoring dashboard.

#### Secure Coding Fixes

Ensure that your metrics are collected securely and that sensitive information is not exposed through metrics. For example, avoid exposing user-specific data in metrics.

#### Configuration Hardening

Configure your Prometheus server to only scrape metrics from trusted sources. Use authentication and authorization mechanisms to restrict access to metrics.

### Real-World Examples

#### CVE-2021-25285: Prometheus Remote Write Authentication Bypass

In 2021, a vulnerability was discovered in Prometheus that allowed an attacker to bypass authentication and write arbitrary metrics to the Prometheus server. This could lead to unauthorized access and manipulation of metrics.

**Impact:** An attacker could manipulate metrics to hide performance issues or to cause false alarms.

**Mitigation:** Ensure that Prometheus is configured with proper authentication and authorization mechanisms. Use TLS to encrypt communication between the Prometheus server and clients.

### Conclusion

Instrumenting your application with Prometheus client libraries allows you to expose valuable metrics that can be used for monitoring and alerting. By defining and exposing custom metrics, you can gain deeper insights into the behavior and performance of your application. Always ensure that your metrics are collected securely and that you have proper detection and prevention mechanisms in place to protect against potential issues.

### Practice Labs

For hands-on practice with Prometheus and client libraries, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a module on monitoring and logging, which includes exercises on setting up Prometheus and Grafana.
- **OWASP Juice Shop**: A deliberately insecure web application that includes a Prometheus setup for monitoring.

These labs provide practical experience in setting up and using Prometheus client libraries in real-world scenarios.

---
<!-- nav -->
[[05-Creating Docker Login Secrets in Kubernetes|Creating Docker Login Secrets in Kubernetes]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/10-Exposing Metrics with Prometheus Client Libraries/00-Overview|Overview]] | [[07-Exposing Metrics with Prometheus Client Libraries|Exposing Metrics with Prometheus Client Libraries]]
