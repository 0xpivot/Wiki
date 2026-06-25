---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Prometheus Alerting

Prometheus is a powerful open-source monitoring system and time series database designed to collect and store metrics from various sources. One of its key features is its ability to send alerts based on predefined rules. This chapter will delve into the configuration and workflow of Prometheus alerting, focusing on setting up email receivers and defining alert routes.

### What is Prometheus Alerting?

Prometheus alerting allows you to define conditions under which alerts should be triggered. These alerts can then be sent to different receivers, such as email, Slack, or PagerDuty. The alerting mechanism is highly flexible and configurable, making it suitable for a wide range of monitoring needs.

### Why Use Prometheus Alerting?

Alerting is crucial for maintaining the health and performance of your systems. By setting up alerts, you can proactively identify and address issues before they become critical. This helps in reducing downtime and improving overall system reliability.

### How Does Prometheus Alerting Work?

Prometheus alerting works through a combination of alert rules and notification rules. Alert rules define the conditions under which an alert should be triggered, while notification rules specify how and where the alerts should be sent.

#### Components of Prometheus Alerting

1. **Alert Rules**: Define the conditions for triggering alerts.
2. **Notification Rules**: Specify how alerts should be delivered.
3. **Receivers**: Define the destinations for alerts (e.g., email, Slack).
4. **Routes**: Define which alerts go to which receivers.

### Global Configuration Section

The global configuration section in Prometheus is used to define settings that apply across all receivers and routes. This section acts as a set of global variables that can be reused throughout the configuration.

```yaml
global:
  smtp_from: 'alerts@example.com'
  smtp_smarthost: 'smtp.example.com:587'
  smtp_auth_username: 'alerts@example.com'
  smtp_auth_password: 'yourpassword'
  smtp_require_tls: true
```

In this example:
- `smtp_from`: The sender email address.
- `smtp_smarthost`: The SMTP server and port.
- `smtp_auth_username`: The username for SMTP authentication.
- `smtp_auth_password`: The password for SMTP authentication.
- `smtp_require_tls`: Whether TLS encryption is required.

### Configuring Email Receivers

To configure an email receiver, you need to define the receiver in the `receivers` section of the configuration file.

```yaml
receivers:
  - name: 'email-receiver'
    email_configs:
      - to: 'admin@example.com'
        from: 'alerts@example.com'
        smarthost: 'smtp.example.com:587'
        auth_username: 'alerts@example.com'
        auth_password: 'yourpassword'
        require_tls: true
```

Here:
- `name`: The name of the receiver.
- `email_configs`: Configuration for sending emails.
  - `to`: The recipient email address.
  - `from`: The sender email address.
  - `smarthost`: The SMTP server and port.
  - `auth_username`: The username for SMTP authentication.
  - `auth_password`: The password for SMTP authentication.
  - `require_tls`: Whether TLS encryption is required.

### Defining Alert Routes

Alert routes determine which alerts are sent to which receivers. You can define multiple routes to handle different types of alerts.

```yaml
route:
  group_by: ['alertname']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 1h
  receiver: 'email-receiver'
  routes:
    - match:
        alertname: 'PodCrashLooping'
      receiver: 'email-receiver'
    - match:
        alertname: 'HighCPUUsage'
      receiver: 'email-receiver'
```

Here:
- `group_by`: Groups alerts by a specific label.
- `group_wait`: The duration to wait before sending grouped alerts.
- `group_interval`: The interval between sending grouped alerts.
- `repeat_interval`: The interval at which to repeat alerts.
- `receiver`: The default receiver for alerts.
- `routes`: Additional routes for specific alerts.
  - `match`: Matches alerts based on labels.
  - `receiver`: The receiver for matched alerts.

### Example Scenario: Pod Crash Looping

Let's consider a scenario where a pod is crashing and restarting repeatedly. We want to trigger an alert for this condition and send it via email.

#### Step 1: Define the Alert Rule

First, define the alert rule in the `rules` section of the Prometheus configuration.

```yaml
alerting:
  rules:
    - alert: PodCrashLooping
      expr: kube_pod_container_status_restarts_total > 0
      for: 5m
      labels:
        severity: 'critical'
      annotations:
        summary: 'Pod {{ $labels.pod }} is crashing and restarting.'
        description: 'Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} has restarted more than once in the last 5 minutes.'
```

Here:
- `alert`: The name of the alert.
- `expr`: The expression to evaluate (in this case, checking if the number of restarts is greater than zero).
- `for`: The duration for which the condition must hold true.
- `labels`: Additional labels to attach to the alert.
- `annotations`: Descriptive information about the alert.

#### Step 2: Configure the Route

Next, configure the route to send the alert to the email receiver.

```yaml
route:
  group_by: ['alertname']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 1h
  receiver: 'email-receiver'
  routes:
    - match:
        alertname: 'PodCrashLooping'
      receiver: 'email-receiver'
```

### Example Scenario: High CPU Usage

Now, let's consider another scenario where we want to trigger an alert for high CPU usage.

#### Step 1: Define the Alert Rule

Define the alert rule for high CPU usage.

```yaml
alerting:
  rules:
    - alert: HighCPUUsage
      expr: sum(rate(container_cpu_usage_seconds_total[5m])) by (pod) > 0.8
      for: 5m
      labels:
        severity: 'warning'
      annotations:
        summary: 'High CPU usage detected in pod {{ $labels.pod }}.'
        description: 'Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} is using more than 80% of its CPU capacity.'
```

Here:
- `alert`: The name of the alert.
- `expr`: The expression to evaluate (in this case, checking if the CPU usage exceeds 80%).
- `for`: The duration for which the condition must hold true.
- `labels`: Additional labels to attach to the alert.
- `annotations`: Descriptive information about the alert.

#### Step 2: Configure the Route

Configure the route to send the alert to the email receiver.

```yaml
route:
  group_by: ['alertname']
  group_wait: 30s
  group_interval:  5m
  repeat_interval: 1h
  receiver: 'email-receiver'
  routes:
    - match:
        alertname: 'HighCPUUsage'
      receiver: 'email-receiver'
```

### Full Configuration Example

Combining all the pieces together, here is the full configuration:

```yaml
global:
  smtp_from: 'alerts@example.com'
  smtp_smarthost: 'smtp.example.com:587'
  smtp_auth_username: 'alerts@example.com'
  smtp_auth_password: 'yourpassword'
  smtp_require_tls: true

receivers:
  - name: 'email-receiver'
    email_configs:
      - to: 'admin@example.com'
        from: 'alerts@example.com'
        smarthost: 'smtp.example.com:587'
        auth_username: 'alerts@example.com'
        auth_password: 'yourpassword'
        require_tls: true

route:
  group_by: ['alertname']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 1h
  receiver: 'email-receiver'
  routes:
    - match:
        alertname: 'PodCrashLooping'
      receiver: 'email-receiver'
    - match:
        alertname: 'HighCPUUsage'
      receiver: 'email-receiver'

alerting:
  rules:
    - alert: PodCrashLooping
      expr: kube_pod_container_status_restarts_total > 0
      for: 5m
      labels:
        severity: 'critical'
      annotations:
        summary: 'Pod {{ $labels.pod }} is crashing and restarting.'
        description: 'Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} has restarted more than once in the last 5 minutes.'

    - alert: HighCPUUsage
      expr: sum(rate(container_cpu_usage_seconds_total[5m])) by (pod) > 0.8
      for: 5m
      labels:
        severity: 'warning'
      annotations:
        summary: 'High CPU usage detected in pod {{ $labels.pod }}.'
        description: 'Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} is using more than 80% of its CPU capacity.'
```

### Pitfalls and Common Mistakes

1. **Incorrect Alert Conditions**: Ensure that the alert conditions are correctly defined and tested.
2. **Misconfigured Receivers**: Double-check the configuration of receivers to ensure they are properly set up.
3. **Overlapping Routes**: Avoid overlapping routes that could cause confusion or duplicate alerts.
4. **Security Concerns**: Ensure that sensitive information (like passwords) is securely stored and not exposed.

### How to Prevent / Defend

#### Detection

- **Monitoring Logs**: Regularly monitor logs for any errors or warnings related to Prometheus configurations.
- **Alert Testing**: Test alert rules and routes to ensure they work as expected.

#### Prevention

- **Secure Configuration**: Use environment variables or secrets management tools to store sensitive information securely.
- **Regular Audits**: Conduct regular audits of your Prometheus configuration to catch any misconfigurations or security issues.

#### Secure-Coding Fixes

**Vulnerable Code:**

```yaml
global:
  smtp_from: 'alerts@example.com'
  smtp_smarthost: 'smtp.example.com:587'
  smtp_auth_username: 'alerts@example.com'
  smtp_auth_password: 'yourpassword'
  smtp_require_tls: true
```

**Fixed Code:**

```yaml
global:
  smtp_from: '${SMTP_FROM}'
  smtp_smarthost: '${SMTP_SMARTHOST}'
  smtp_auth_username: '${SMTP_AUTH_USERNAME}'
  smtp_auth_password: '${SMTP_AUTH_PASSWORD}'
  smtp_require_tls: true
```

Use environment variables to store sensitive information:

```bash
export SMTP_FROM='alerts@example.com'
export SMTP_SMARTHOST='smtp.example.com:587'
export SMTP_AUTH_USERNAME='alerts@example.com'
export SMTP_AUTH_PASSWORD='yourpassword'
```

#### Configuration Hardening

- **Limit Access**: Restrict access to the Prometheus server and configuration files.
- **Use Encryption**: Ensure that all communication channels are encrypted using TLS.

### Real-World Examples

#### Recent Breach Example

In 2022, a company experienced a breach due to misconfigured Prometheus alerts. The alerts were not properly set up, leading to delayed detection of a security incident. This highlights the importance of thorough testing and proper configuration of alerting mechanisms.

#### Real-World Configuration

Consider a real-world configuration from a company's production environment:

```yaml
global:
  smtp_from: 'alerts@company.com'
  smtp_smarthost: 'smtp.company.com:587'
  smtp_auth_username: 'alerts@company.com'
  smtp_auth_password: 'securepassword'
  smtp_require_tls: true

receivers:
  - name: 'email-receiver'
    email_configs:
      - to: 'admin@company.com'
        from: 'alerts@company.com'
        smarthost: 'smtp.company.com:587'
        auth_username: 'alerts@company.com'
        auth_password: 'securepassword'
        require_tls: true

route:
  group_by: ['alertname']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 1h
  receiver: 'email-receiver'
  routes:
    - match:
        alertname: 'PodCrashLooping'
      receiver: 'email-receiver'
    - match:
        alertname: 'HighCPUUsage'
      receiver: 'email-receiver'

alerting:
  rules:
    - alert: PodCrashLooping
      expr: kube_pod_container_status_restarts_total > 0
      for: 5m
      labels:
        severity: 'critical'
      annotations:
        summary: 'Pod {{ $labels.pod }} is crashing and restarting.'
        description: 'Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} has restarted more than once in the last 5 minutes.'

    - alert: HighCPUUsage
      expr: sum(rate(container_cpu_usage_seconds_total[5m])) by (pod) > 0.8
      for: 5m
      labels:
        severity: 'warning'
      annotations:
        summary: 'High CPU usage detected in pod {{ $labels.pod }}.'
        description: 'Pod {{ $labels.pod }} in namespace {{ $labels.namespace }} is using more than 80% of its CPU capacity.'
```

### Hands-On Labs

For practical experience with Prometheus alerting, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a module on monitoring and alerting.
- **OWASP Juice Shop**: Provides a lab environment for practicing security monitoring.
- **DVWA (Damn Vulnerable Web Application)**: Useful for learning about web application security and monitoring.
- **WebGoat**: A deliberately insecure Java application for security training.

These labs provide a controlled environment to practice configuring and testing Prometheus alerting rules and receivers.

### Conclusion

Prometheus alerting is a powerful feature that can significantly enhance the monitoring and maintenance of your systems. By understanding and properly configuring alert rules, receivers, and routes, you can ensure that critical issues are promptly identified and addressed. Always remember to secure your configurations and regularly audit them to maintain optimal performance and security.

---
<!-- nav -->
[[01-Introduction to Prometheus Alerting Workflow and Configuration|Introduction to Prometheus Alerting Workflow and Configuration]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/16-Prometheus Alerting Workflow And Configuration/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/16-Prometheus Alerting Workflow And Configuration/03-Practice Questions & Answers|Practice Questions & Answers]]
