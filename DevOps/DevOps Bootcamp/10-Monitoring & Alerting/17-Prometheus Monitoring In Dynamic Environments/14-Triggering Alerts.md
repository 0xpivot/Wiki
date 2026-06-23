---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Triggering Alerts

Prometheus uses rules to trigger alerts based on certain conditions. Once an alert is triggered, it needs to be delivered to the appropriate recipients.

### How Does Prometheus Trigger Alerts?

Prometheus triggers alerts by evaluating the alerting rules defined in the rule files. When a condition specified in an alerting rule is met, Prometheus generates an alert.

### Who Receives the Alerts?

The recipients of the alerts are typically defined in the alerting rules themselves. You can specify labels and annotations to provide additional context and details about the alert.

### Real-World Example

Consider a scenario where a company is monitoring a critical service. They might define an alert to notify them when the CPU usage exceeds 80%:

```promql
alert: HighCPUUsage
expr: node_cpu_seconds_total{mode!="idle"} / node_cpu_seconds_total > 0.8
for: 5m
labels:
  severity: "critical"
annotations:
  summary: "High CPU usage detected on {{ $labels.instance }}"
  description: "CPU usage is above 80% on {{ $labels.instance }} for more than 5 minutes."
```

### Pitfalls and Best Practices

- **Recipient Management**: Ensure that the recipients of the alerts are properly managed and updated as needed.
- **Alert Fatigue**: Avoid triggering too many alerts, which can lead to alert fatigue and desensitization.

### How to Prevent / Defend

To prevent issues with alert delivery, consider the following:

1. **Manage Recipients**: Regularly review and update the list of recipients to ensure that alerts are delivered to the appropriate individuals.
2. **Reduce Noise**: Implement strategies to reduce alert noise, such as grouping similar alerts and setting appropriate thresholds.

---
<!-- nav -->
[[13-ScrapConfig Block|ScrapConfig Block]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/17-Prometheus Monitoring In Dynamic Environments/00-Overview|Overview]] | [[15-Visualization Tools|Visualization Tools]]
