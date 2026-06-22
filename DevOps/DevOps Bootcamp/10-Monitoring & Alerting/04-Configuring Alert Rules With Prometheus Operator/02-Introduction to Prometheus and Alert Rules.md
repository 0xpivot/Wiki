---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Prometheus and Alert Rules

Prometheus is an open-source systems monitoring and alerting toolkit originally built at SoundCloud. It is now a Cloud Native Computing Foundation (CNCF) project. Prometheus collects metrics from configured targets at specified intervals and stores them internally. The data model organizes metrics into time series, which are identified by metric name and key-value pairs. This allows for flexible querying and visualization of the collected metrics.

### What Are Alert Rules?

Alert rules in Prometheus are used to define conditions under which an alert should be triggered. These rules are evaluated periodically, and if the condition is met, an alert is fired. The alerts can then be sent to various notification channels such as email, Slack, PagerDuty, etc., depending on the configuration.

### Why Use Alert Rules?

Alert rules are crucial for maintaining the health and performance of your system. They help in identifying issues before they become critical, allowing for proactive measures to be taken. Without alert rules, you might miss important events that could lead to system downtime or performance degradation.

### How Alert Rules Work

Alert rules are defined in YAML files and are loaded by Prometheus. Each rule consists of a condition and an action. The condition is typically a PromQL (Prometheus Query Language) expression that evaluates to a boolean value. If the condition is true, the action is executed, usually sending an alert to a notification channel.

### Example of an Alert Rule

Here’s a simple example of an alert rule:

```yaml
groups:
- name: example
  rules:
  - alert: HighRequestLatency
    expr: job:request_latency_seconds:mean5m{job="api-server"} > 0.5
    for: 10m
    labels:
      severity: page
    annotations:
      summary: "High request latency on {{ $labels.job }}"
      description: "{{ $labels.job }} has a mean request latency above 0.5s for more than 10 minutes."
```

In this example, the alert `HighRequestLatency` is triggered if the mean request latency for the `api-server` job exceeds 0.5 seconds for more than 10 minutes.

### Background Theory

Prometheus uses a pull-based model to collect metrics from targets. The metrics are stored in a time-series database, and alert rules are evaluated against these metrics. The evaluation interval is configurable and defaults to every 15 seconds.

### Real-World Example

Consider a scenario where a company experienced a significant outage due to high request latency. The company had Prometheus set up but did not have appropriate alert rules configured. As a result, the issue was detected too late, leading to extended downtime and loss of revenue. By setting up proper alert rules, the company could have detected the issue earlier and taken corrective actions promptly.

---
<!-- nav -->
[[01-Introduction to Prometheus Operator and Alert Rules|Introduction to Prometheus Operator and Alert Rules]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/04-Configuring Alert Rules With Prometheus Operator/00-Overview|Overview]] | [[03-Introduction to Prometheus and Prometheus Operator|Introduction to Prometheus and Prometheus Operator]]
