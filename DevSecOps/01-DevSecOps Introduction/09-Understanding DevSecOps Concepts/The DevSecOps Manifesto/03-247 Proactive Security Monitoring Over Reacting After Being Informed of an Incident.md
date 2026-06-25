---
course: DevSecOps
topic: Understanding DevSecOps Concepts
tags: [devsecops]
---

## 24/7 Proactive Security Monitoring Over Reacting After Being Informed of an Incident

### What Is Proactive Security Monitoring?

Proactive security monitoring involves continuously monitoring an organization's systems and networks to detect and respond to security incidents in real-time. This approach contrasts with reactive monitoring, where security teams only become aware of incidents after they have occurred.

### Why Is Proactive Security Monitoring Important?

Reactive monitoring often leads to delayed detection and response, allowing attackers to cause significant damage before being identified. Proactive monitoring, on the other hand, enables organizations to detect and mitigate threats before they can cause harm.

### How Does Proactive Security Monitoring Work?

1. **Continuous Monitoring**: Tools like SIEM (Security Information and Event Management) systems are used to continuously monitor logs and network traffic.
2. **Real-Time Alerts**: Automated alerts are generated when suspicious activities are detected.
3. **Immediate Response**: Security teams can respond immediately to contain and mitigate threats.

### Real-World Example: Capital One Data Breach

The Capital One data breach in 2019 demonstrated the importance of proactive security monitoring. The attacker exploited a misconfigured firewall, which went undetected for months due to a lack of continuous monitoring. A proactive monitoring approach would have detected and responded to the breach much earlier.

### Code Example: SIEM Alert Script

```python
# Example of a simple SIEM alert script
import logging

logging.basicConfig(level=logging.INFO)

def generate_alert(log_entry):
    if "unauthorized access" in log_entry:
        logging.info("Unauthorized access detected!")
    else:
        logging.info("No unauthorized access detected.")

log_entry = "User attempted unauthorized access to /admin"
generate_alert(log_entry)
```

### How to Prevent / Defend

**Detection**: Implement continuous monitoring tools like SIEM systems to detect and alert on suspicious activities.

**Prevention**: Ensure that all systems and networks are continuously monitored for security incidents.

**Secure Coding Fix**: Compare the insecure code with the secure version.

```python
# Insecure code
def handle_request(request):
    # Vulnerable to path traversal
    filename = request.get("filename")
    with open(filename, "r") as file:
        content = file.read()
    return content

# Secure code
def handle_request(request):
    # Using a whitelist to prevent path traversal
    allowed_files = ["file1.txt", "file2.txt"]
    filename = request.get("filename")
    if filename in allowed_files:
        with open(filename, "r") as file:
            content = file.read()
        return content
    else:
        return "File not found."
```

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/09-Understanding DevSecOps Concepts/The DevSecOps Manifesto/02-Understanding DevSecOps Concepts|Understanding DevSecOps Concepts]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/09-Understanding DevSecOps Concepts/The DevSecOps Manifesto/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/09-Understanding DevSecOps Concepts/The DevSecOps Manifesto/04-Business-Driven Security Scores Over Just Rubber-Stamping Security|Business-Driven Security Scores Over Just Rubber-Stamping Security]]
