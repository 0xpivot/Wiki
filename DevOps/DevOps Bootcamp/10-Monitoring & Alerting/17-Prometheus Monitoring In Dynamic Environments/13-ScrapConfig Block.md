---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## ScrapConfig Block

The `ScrapConfig` block controls what resources Prometheus monitors. This is where you define the targets and specify how Prometheus should scrape them.

### What is ScrapConfig?

The `ScrapConfig` block defines the jobs and targets that Prometheus should scrape. Each job can have multiple targets, and you can configure various parameters such as the scrape interval, timeout, and relabeling rules.

### Why is ScrapConfig Important?

The `ScrapConfig` block is crucial because it determines which resources Prometheus monitors and how it interacts with them. Without proper configuration, Prometheus may miss important data or fail to scrape targets correctly.

### How Does ScrapConfig Work?

In the `prometheus.yml` configuration file, the `ScrapConfig` block is defined as follows:

```yaml
scrape_configs:
  - job_name: 'prometheus'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:9090']
```

This configuration tells Prometheus to scrape the `prometheus` job every 15 seconds, targeting the local Prometheus server at `localhost:9090`.

### Defining Multiple Jobs and Targets

You can define multiple jobs and targets in the `ScrapConfig` block. For example:

```yaml
scrape_configs:
  - job_name: 'prometheus'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node_exporter'
    scrape_interval: 30s
    static_configs:
      - targets: ['localhost:9100']
```

Here, the `prometheus` job scrapes the local Prometheus server every 15 seconds, while the `node_exporter` job scrapes the local Node Exporter every 30 seconds.

### Real-World Example

Consider a scenario where a company is monitoring a distributed system with multiple components. They might define multiple jobs and targets to cover all the components:

```yaml
scrape_configs:
  - job_name: 'prometheus'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'node_exporter'
    scrape_interval: 30s
    static_configs:
      - targets: ['localhost:9100']

  - job_name: 'app_server'
    scrape_interval: 10s
    static_configs:
      - targets: ['app-server-1:9101', 'app-server-2:9101']
```

### Pitfalls and Best Practices

- **Overloading Targets**: Setting the scrape interval too low can overload the monitored systems, especially if they have limited resources.
- **Target Availability**: Ensure that the targets are available and reachable. Use health checks to verify the availability of targets.

### How to Prevent / Defend

To prevent issues with the `ScrapConfig`, consider the following:

1. **Monitor Target Health**: Use Prometheus to monitor the health of the targets and adjust the scrape interval accordingly.
2. **Use Relabeling Rules**: Apply relabeling rules to dynamically modify the labels of targets, making it easier to manage and monitor them.

---
<!-- nav -->
[[12-Rule Files Block|Rule Files Block]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/17-Prometheus Monitoring In Dynamic Environments/00-Overview|Overview]] | [[14-Triggering Alerts|Triggering Alerts]]
