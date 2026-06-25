---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Evaluation Interval

The `evaluation_interval` option in the global configuration defines how often Prometheus evaluates the rules. This interval is crucial because it determines the frequency at which alerts are checked and new time series entries are created.

### What is the Evaluation Interval?

The evaluation interval is the period between two consecutive evaluations of the rules. By default, Prometheus evaluates rules every 15 seconds. However, this can be overridden to suit specific requirements.

### Why is the Evaluation Interval Important?

The evaluation interval affects the responsiveness of alerts and the creation of new time series entries. A shorter interval means more frequent evaluations, which can be beneficial for timely alerts but may also increase the load on the Prometheus server.

### How Does the Evaluation Interval Work?

In the `prometheus.yml` configuration file, the global evaluation interval is set using the `evaluation_interval` parameter:

```yaml
global:
  evaluation_interval: 15s
```

This configuration tells Prometheus to evaluate all rules every 15 seconds unless overridden.

### Real-World Example

Consider a scenario where a company is monitoring a critical service. They might set a shorter evaluation interval (e.g., 5 seconds) to ensure that alerts are triggered promptly. However, they might also set a longer interval (e.g., 60 seconds) for less critical services to reduce the load on the Prometheus server.

### Pitfalls and Best Practices

- **Overloading Prometheus**: Setting the evaluation interval too low can overload the Prometheus server, especially if it is handling a large number of rules.
- **Responsiveness**: Ensure the evaluation interval aligns with the required responsiveness for your use case. For real-time monitoring, a shorter interval is necessary.

### How to Prevent / Defend

To prevent overloading the Prometheus server, consider the following:

1. **Monitor Server Load**: Use Prometheus to monitor the load on the server and adjust the evaluation interval accordingly.
2. **Use Labels**: Apply labels to rules to group them and set different evaluation intervals based on their importance.

---
<!-- nav -->
[[02-Introduction to Prometheus Monitoring|Introduction to Prometheus Monitoring]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/17-Prometheus Monitoring In Dynamic Environments/00-Overview|Overview]] | [[04-Global Configuration and Scrape Interval|Global Configuration and Scrape Interval]]
