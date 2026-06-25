---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Monitoring High CPU Load Alerts

Monitoring high CPU load alerts is a critical aspect of maintaining the performance and reliability of your systems. In this section, we will delve deep into the process of setting up and monitoring high CPU load alerts using tools like Prometheus and Alertmanager. We will cover the theoretical background, practical setup, and real-world examples to ensure you understand the entire workflow.

### Background Theory

#### What is CPU Load?

CPU load refers to the amount of work that a CPU is performing at any given time. It is typically measured as a percentage of the total processing capacity of the CPU. High CPU load can indicate that the system is under heavy usage, which can lead to performance degradation, increased latency, and even system crashes if not managed properly.

#### Why Monitor CPU Load?

Monitoring CPU load is essential for several reasons:

1. **Performance Optimization**: By keeping track of CPU load, you can identify bottlenecks and optimize resource allocation.
2. **Proactive Maintenance**: High CPU load can be an indicator of underlying issues such as inefficient code, resource leaks, or hardware limitations.
3. **System Reliability**: Ensuring that CPU load stays within acceptable limits helps maintain the overall stability and reliability of the system.

### Setting Up CPU Load Monitoring

To monitor high CPU load, we will use Prometheus, a popular open-source monitoring system, along with Alertmanager, which handles the alerting mechanism.

#### Installing Prometheus and Alertmanager

First, you need to install Prometheus and Alertmanager. You can download them from their respective websites or use package managers like `apt` or `yum`.

```bash
# Install Prometheus
wget https://github.com/prometheus/prometheus/releases/download/v2.32.0/prometheus-2.32.0.linux-amd64.tar.gz
tar xvfz prometheus-2.32.0.linux-amd64.tar.gz
cd prometheus-2.32.0.linux-amd64

# Install Alertmanager
wget https://github.com/prometheus/alertmanager/releases/download/v0.23.0/alertmanager-0.23.0.linux-amd64.tar.gz
tar xvfz alertmanager-0.23.0.linux-amd64.tar.gz
cd alertmanager-0.23.0.linux-amd64
```

#### Configuring Prometheus

Prometheus needs to be configured to scrape metrics from your system. Create a `prometheus.yml` configuration file:

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'node_exporter'
    static_configs:
      - targets: ['localhost:9100']
```

Start Prometheus:

```bash
./prometheus --config.file=prometheus.yml
```

#### Configuring Alertmanager

Alertmanager needs to be configured to handle alerts. Create an `alertmanager.yml` configuration file:

```yaml
global:
  resolve_timeout: 5m

route:
  group_by: ['alertname']
  group_wait: 30s
  group_interval: 5m
  repeat_interval: 1h
  receiver: 'email'

receivers:
  - name: 'email'
    email_configs:
      - to: 'your-email@example.com'
        from: 'alertmanager@example.com'
        smarthost: 'smtp.example.com:587'
        auth_username: 'username'
        auth_password: 'password'
```

Start Alertmanager:

```bash
./alertmanager --config.file=alertmanager.yml
```

### Creating High CPU Load Alerts

Now that Prometheus and Alertmanager are set up, we need to create alerts for high CPU load.

#### Define the Alert Rule

Create a `rules.yml` file to define the alert rule:

```yaml
groups:
  - name: cpu_load_rules
    rules:
      - alert: HostHighCPULoad
        expr: node_cpu_seconds_total{mode="idle"} / node_cpu_core_total * 100 < 20
        for: 1m
        labels:
          severity: "critical"
        annotations:
          summary: "Host {{ $labels.instance }} has high CPU load"
          description: "The host {{ $labels.instance }} has a CPU load above 80% for more than 1 minute."
```

Add the rule file to Prometheus:

```yaml
rule_files:
  - 'rules.yml'
```

Restart Prometheus to apply the changes:

```bash
./prometheus --config.file=prometheus.yml
```

### Testing the Alert

To test the alert, we will simulate high CPU load using a stress test tool like `stress`.

#### Simulating High CPU Load

Install `stress`:

```bash
sudo apt-get install stress
```

Run `stress` to simulate high CPU load:

```bash
stress --cpu 4 --timeout 60s
```

This command will run four CPU stressors for 60 seconds.

#### Checking the Alert

After running the stress test, check the Prometheus UI to see if the alert is triggered. Navigate to `http://localhost:9090` and go to the "Alerts" tab.

If the alert is triggered, you should see an entry for `HostHighCPULoad`. This means that the alert has been sent to Alertmanager.

### Understanding the Alert Flow

Let's break down the flow of the alert from Prometheus to Alertmanager and finally to the email recipient.

#### Prometheus to Alertmanager

Prometheus sends alerts to Alertmanager via an HTTP POST request. The request includes the alert details in JSON format.

```http
POST /api/v2/alerts HTTP/1.1
Content-Type: application/json

[
  {
    "labels": {
      "alertname": "HostHighCPULoad",
      "instance": "localhost:9100",
      "severity": "critical"
    },
    "annotations": {
      "summary": "Host localhost:9100 has high CPU load",
      "description": "The host localhost:9100 has a CPU load above 80% for more than 1 minute."
    },
    "startsAt": "2023-10-01T12:00:00Z",
    "endsAt": "0001-01-01T00:00:00Z",
    "generatorURL": "http://localhost:9090/graph?g0.expr=node_cpu_seconds_total%7Bmode%3D%22idle%22%7D+%2F+node_cpu_core_total+*+100+%3C+20&g0.tab=0"
  }
]
```

#### Alertmanager to Email

Alertmanager processes the alert and sends it to the configured email address. The email content includes the alert details.

```plaintext
Subject: [ALERT] HostHighCPULoad

Summary: Host localhost:9100 has high CPU load
Description: The host localhost:9100 has a CPU load above 80% for more than 1 minute.
```

### Real-World Examples

#### Recent Breaches and CVEs

High CPU load can be indicative of various security issues, such as DDoS attacks, resource exhaustion, or malicious activities. For example, in the case of the 2021 SolarWinds breach, attackers used high CPU load to mask their activities.

#### Example: SolarWinds Breach

In the SolarWinds breach, attackers injected malicious code into the Orion software, which caused high CPU load. This high load was often overlooked as normal system behavior, allowing the attackers to remain undetected.

### Pitfalls and Common Mistakes

#### Overlooking Low Thresholds

One common mistake is setting the threshold for high CPU load too low. This can result in false positives, leading to unnecessary alerts and potential alert fatigue.

#### Not Configuring Proper Retention Policies

Another pitfall is not configuring proper retention policies for alert data. Without proper retention, you may lose valuable historical data that could help in troubleshooting and analysis.

### How to Prevent / Defend

#### Detection

To detect high CPU load, you can use tools like Prometheus and Grafana to visualize and analyze CPU load metrics over time. Set up alerts to notify you when CPU load exceeds a certain threshold.

#### Prevention

To prevent high CPU load, ensure that your systems are optimized and that you have proper resource management practices in place. Regularly review and update your alert thresholds based on actual system behavior.

#### Secure Coding Fixes

Here is an example of how to implement secure coding practices to prevent high CPU load:

**Vulnerable Code:**

```python
def process_data(data):
    for item in data:
        # Heavy computation
        result = complex_computation(item)
        print(result)
```

**Secure Code:**

```python
import concurrent.futures

def process_data(data):
    with concurrent.futures.ThreadPoolExecutor() as executor:
        results = list(executor.map(complex_computation, data))
        for result in results:
            print(result)
```

By using a thread pool, you can distribute the heavy computation across multiple threads, reducing the overall CPU load.

#### Configuration Hardening

Ensure that your Prometheus and Alertmanager configurations are hardened against unauthorized access. Use strong authentication mechanisms and limit access to only authorized users.

### Conclusion

Monitoring high CPU load alerts is crucial for maintaining the performance and reliability of your systems. By setting up Prometheus and Alertmanager, defining alert rules, and testing the alerts, you can effectively manage high CPU load scenarios. Understanding the flow of alerts and implementing proper detection and prevention strategies will help you maintain a stable and secure environment.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web security, including monitoring and alerting.
- **OWASP Juice Shop**: A deliberately insecure web application for security training. It includes scenarios where high CPU load can be a symptom of security issues.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for security training. It includes scenarios where high CPU load can be a symptom of security issues.

These labs provide real-world scenarios where you can apply the concepts learned in this chapter.

---
<!-- nav -->
[[01-Introduction to Monitoring High CPU Load Alerts in Kubernetes|Introduction to Monitoring High CPU Load Alerts in Kubernetes]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/13-Monitoring High CPU Load Alerts/00-Overview|Overview]] | [[03-Monitoring High CPU Load Alerts|Monitoring High CPU Load Alerts]]
