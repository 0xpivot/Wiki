---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Prometheus Client Libraries

In this section, we will delve into the process of exposing metrics in your own application using Prometheus client libraries. Specifically, we will focus on a simple Node.js application and the Prometheus client library for Node.js. This setup allows us to monitor and collect metrics from our application, which can then be used for various purposes such as visualization, alerting, and further analysis.

### What Are Metrics?

Metrics are quantitative measurements that provide insights into the behavior and performance of a system. They can include various types of data points, such as:

- **Counters**: Incremental values that represent the number of occurrences of an event.
- **Gauges**: Values that can increase or decrease over time, representing the current state of a metric.
- **Histograms**: Binned values that represent the distribution of a set of values.
- **Summaries**: Similar to histograms but pre-computed for specific quantiles.

### Why Expose Metrics?

Exposing metrics is crucial for several reasons:

- **Monitoring**: Metrics help in monitoring the health and performance of your application.
- **Troubleshooting**: They provide valuable data for diagnosing issues and identifying bottlenecks.
- **Visualization**: Metrics can be visualized using tools like Grafana to gain deeper insights.
- **Alerting**: You can set up alerts based on certain thresholds to notify you of potential issues.

### How Prometheus Works

Prometheus is an open-source monitoring system that collects and stores metrics from various sources. It scrapes metrics from instrumented services and stores them in a time-series database. The key components of Prometheus include:

- **Prometheus Server**: Collects and stores metrics.
- **Scraping**: Prometheus periodically fetches metrics from exporters.
- **Pushgateway**: An optional component for pushing metrics to Prometheus.
- **Alertmanager**: Manages and sends out alerts based on configured rules.

### Prometheus Client Libraries

Prometheus client libraries allow you to instrument your application to expose metrics. These libraries are available for various programming languages, including Node.js. By integrating a Prometheus client library into your application, you can easily expose metrics that Prometheus can scrape.

### Example Application Setup

Let's consider a simple Node.js application that we want to monitor. Here is the basic structure of the application:

```javascript
const http = require('http');

const hostname = '127.0.0.1';
const port = 3000;

const server = http.createServer((req, res) => {
  res.statusCode = 200;
  res.setHeader('Content-Type', 'text/plain');
  res.end('Hello, World!\n');
});

server.listen(port, hostname, () => {
  console.log(`Server running at http://${hostname}:${port}/`);
});
```

This application sets up a basic HTTP server that listens on `localhost` at port `3000`. When accessed, it returns a simple "Hello, World!" message.

### Integrating Prometheus Client Library

To expose metrics from this application, we will integrate the Prometheus client library for Node.js. First, install the library using npm:

```bash
npm install prom-client
```

Next, modify the application to include the Prometheus client library and expose some metrics:

```javascript
const http = require('http');
const { Counter, Histogram } = require('prom-client');

// Create a counter for HTTP requests
const httpRequestCounter = new Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'code']
});

// Create a histogram for HTTP request durations
const httpRequestDurationHistogram = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request duration in seconds',
  labelNames: ['method'],
  buckets: [0.1, 0.5, 1, 2.5, 5, 10]
});

const hostname = '127.0.0.1';
const port = 3000;

const server = http.createServer((req, res) => {
  const start = Date.now();

  // Increment the counter for the HTTP request
  httpRequestCounter.inc({ method: req.method, code: res.statusCode });

  // Simulate processing time
  setTimeout(() => {
    res.statusCode = 200;
    res.setHeader('Content-Type', 'text/plain');
    res.end('Hello, World!\n');

    // Record the duration of the HTTP request
    const duration = (Date.now() - start) / 1000;
    httpRequestDurationHistogram.observe({ method: req.method }, duration);
  }, 100);
});

server.listen(port, hostname, () => {
  console.log(`Server running at http://${hostname}:${port}/`);

  // Expose the metrics endpoint
  const metricsPath = '/metrics';
  const metricsPort = 8080;

  const metricsServer = http.createServer(async (req, res) => {
    if (req.url === metricsPath) {
      res.writeHead(200, { 'Content-Type': 'text/plain' });
      res.end(await registry.metrics());
    } else {
      res.writeHead(404);
      res.end();
    }
  });

  metricsServer.listen(metricsPort, () => {
    console.log(`Metrics server running at http://${hostname}:${metricsPort}${metricsPath}`);
  });
});
```

### Explanation of the Code

- **Counter**: A counter named `http_requests_total` is created to track the total number of HTTP requests. It includes labels for the HTTP method and status code.
- **Histogram**: A histogram named `http_request_duration_seconds` is created to measure the duration of HTTP requests. It includes labels for the HTTP method and predefined buckets.
- **Metrics Endpoint**: The `/metrics` endpoint is exposed on port `8080`, where Prometheus can scrape the metrics.

### Running the Application

Start the application by running:

```bash
node app.js
```

Access the application at `http://localhost:3000` and the metrics endpoint at `http://localhost:8080/metrics`.

### Configuring Prometheus

To scrape the metrics from our application, we need to configure Prometheus. Here is an example of a `prometheus.yml` configuration file:

```yaml
scrape_configs:
  - job_name: 'nodejs-app'
    static_configs:
      - targets: ['localhost:8080']
```

Start Prometheus with this configuration:

```bash
prometheus --config.file=prometheus.yml
```

### Visualizing Metrics with Grafana

Once Prometheus is scraping the metrics, you can visualize them using Grafana. Set up a Grafana instance and add a Prometheus data source. Then, create a dashboard to display the metrics.

### Real-World Examples

#### CVE-2021-44228 (Log4Shell)

The Log4Shell vulnerability (CVE-2021-44228) affected many Java applications, leading to remote code execution. While this vulnerability is not directly related to metrics exposure, it highlights the importance of monitoring and alerting on critical events. By exposing metrics related to logging and error handling, you can detect and respond to such vulnerabilities more effectively.

#### Recent Breaches

Recent breaches, such as the SolarWinds supply chain attack, underscore the importance of comprehensive monitoring and alerting. By exposing detailed metrics about your infrastructure, you can detect anomalies and potential security incidents more quickly.

### Pitfalls and Best Practices

#### Common Mistakes

- **Overexposure of Metrics**: Avoid exposing sensitive information through metrics.
- **Incorrect Configuration**: Ensure that Prometheus is correctly configured to scrape the metrics.
- **Performance Impact**: Be mindful of the performance impact of collecting and exposing metrics.

#### Best Practices

- **Use Labels Wisely**: Labels provide context and make it easier to filter and aggregate metrics.
- **Monitor Critical Components**: Focus on monitoring critical components and services.
- **Regularly Review Metrics**: Regularly review and refine the metrics you expose to ensure they remain relevant and useful.

### How to Prevent / Defend

#### Detection

- **Anomaly Detection**: Use anomaly detection techniques to identify unusual patterns in metrics.
- **Threshold-Based Alerts**: Set up threshold-based alerts to notify you of potential issues.

#### Prevention

- **Secure Configuration**: Ensure that Prometheus and Grafana are securely configured.
- **Least Privilege**: Follow the principle of least privilege when granting access to metrics and dashboards.

#### Secure Coding Fixes

Here is an example of a vulnerable and secure version of the code:

**Vulnerable Version**

```javascript
const http = require('http');
const { Counter, Histogram } = require('prom-client');

const httpRequestCounter = new Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'code']
});

const httpRequestDurationHistogram = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request duration in seconds',
  labelNames: ['method'],
  buckets: [0.1, 0.5, 1, 2.5, 5, 10]
});

const hostname = '127.0.0.1';
const port = 3000;

const server = http.createServer((req, res) => {
  const start = Date.now();

  httpRequestCounter.inc({ method: req.method, code: res.statusCode });

  setTimeout(() => {
    res.statusCode = 200;
    res.setHeader('Content-Type', 'text/plain');
    res.end('Hello, World!\n');

    const duration = (Date.now() - start) / 1000;
    httpRequestDurationHistogram.observe({ method: req.method }, duration);
  }, 100);
});

server.listen(port, hostname, () => {
  console.log(`Server running at http://${hostname}:${port}/`);

  const metricsPath = '/metrics';
  const metricsPort = 8080;

  const metricsServer = http.createServer(async (req, res) => {
    if (req.url === metricsPath) {
      res.writeHead(200, { 'Content-Type': 'text/plain' });
      res.end(await registry.metrics());
    } else {
      res.writeHead(404);
      res.end();
    }
  });

  metricsServer.listen(metricsPort, () => {
    console.log(`Metrics server running at http://${hostname}:${metricsPort}${metricsPath}`);
  });
});
```

**Secure Version**

```javascript
const http = require('http');
const { Counter, Histogram } = require('prom-client');

const httpRequestCounter = new Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'code']
});

const httpRequestDurationHistogram = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'HTTP request duration in seconds',
  labelNames: ['method'],
  buckets: [0.1, 0.5, 1, 2.5, 5, 10]
});

const hostname = '127.0.0.1';
const port = 3000;

const server = http.createServer((req, res) => {
  const start = Date.now();

  httpRequestCounter.inc({ method: req.method, code: res.statusCode });

  setTimeout(() => {
    res.statusCode = 200;
    res.setHeader('Content-Type', 'text/plain');
    res.end('Hello, World!\n');

    const duration = (Date.now() - start) / 1000;
    httpRequestDurationHistogram.observe({ method: req.method }, duration);
  }, 100);
});

server.listen(port, hostname, () => {
  console.log(`Server running at http://${hostname}:${port}/`);

  const metricsPath = '/metrics';
  const metricsPort = 8080;

  const metricsServer = http.createServer(async (req, res) => {
    if (req.url === metricsPath) {
      res.writeHead(200, { 'Content-Type': 'text/plain' });
      res.end(await registry.metrics());
    } else {
      res.writeHead(404);
      res.end();
    }
  });

  metricsServer.listen(metricsPort, () => {
    console.log(`Metrics server running at http://${hostname}:${metricsPort}${metricsPath}`);
  });
});
```

### Conclusion

By integrating Prometheus client libraries into your Node.js application, you can expose valuable metrics that can be used for monitoring, troubleshooting, and visualization. This setup provides a robust foundation for comprehensive monitoring and alerting, helping you maintain the health and performance of your application.

### Practice Labs

For hands-on practice with Prometheus and Grafana, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on web application security, including sections on monitoring and alerting.
- **OWASP Juice Shop**: A deliberately insecure web application for security training, which can be monitored using Prometheus and Grafana.
- **DVWA (Damn Vulnerable Web Application)**: Another web application for security training, which can be integrated with Prometheus for monitoring.

These labs provide practical experience in setting up and configuring Prometheus and Grafana, allowing you to apply the concepts learned in this chapter.

---
<!-- nav -->
[[03-Introduction to Monitoring with Prometheus Client Libraries|Introduction to Monitoring with Prometheus Client Libraries]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/10-Exposing Metrics with Prometheus Client Libraries/00-Overview|Overview]] | [[05-Creating Docker Login Secrets in Kubernetes|Creating Docker Login Secrets in Kubernetes]]
