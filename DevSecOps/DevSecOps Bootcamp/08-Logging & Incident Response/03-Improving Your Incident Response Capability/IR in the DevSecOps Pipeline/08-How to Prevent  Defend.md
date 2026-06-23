---
course: DevSecOps
topic: Improving Your Incident Response Capability
tags: [devsecops]
---

## How to Prevent / Defend

### Prevention Strategies

1. **Implement Secure Coding Practices**: Follow established coding standards and guidelines to reduce the likelihood of introducing vulnerabilities into the codebase.
2. **Use Automated Tools**: Utilize tools like static and dynamic analysis to identify and address potential vulnerabilities.
3. **Enforce Security Policies**: Establish and enforce security policies across the development lifecycle to ensure consistency and reduce the risk of security incidents.

### Detection Strategies

1. **Continuous Monitoring**: Constantly watch systems and applications for signs of security incidents using tools like Splunk and ELK Stack.
2. **Set Up Alerts**: Configure alerts to notify security teams of potential incidents.
3. **Regular Audits**: Conduct regular audits to ensure that monitoring systems are functioning correctly.

### Response Strategies

1. **Containment**: Isolate affected systems to prevent further spread of the incident.
2. **Eradication**: Identify the root cause of the incident and remove the threat from the system.
3. **Recovery**: Restore affected systems to their normal state and validate that they are functioning correctly.

### Secure Coding Fix Example

#### Vulnerable Code

```python
# Vulnerable Code
def get_user_data(user_id):
    query = f"SELECT * FROM users WHERE id = {user_id}"
    result = execute_query(query)
    return result
```

#### Secure Code

```python
# Secure Code
def get_user_data(user_id):
    query = "SELECT * FROM users WHERE id = %s"
    result = execute_query(query, (user_id,))
    return result
```

### Hardening Example

#### Vulnerable Configuration

```json
{
  "log_sources": [
    {
      "name": "application_logs",
      "path": "/var/log/application.log",
      "type": "file"
    }
  ],
  "alerts": []
}
```

#### Hardened Configuration

```json
{
  "log_sources": [
    {
      "name": "application_logs",
      "path": "/var/log/application.log",
      "type": "file"
    },
    {
      "name": "network_traffic",
      "interface": "eth0",
      "type": "network"
    }
  ],
  "alerts": [
    {
      "name": "high_cpu_usage",
      "threshold": 90,
     _ "action": "notify_security_team"
    },
    {
      "name": "unusual_network_activity",
      "pattern": ".*malicious_pattern.*",
      "action": "investigate"
    }
  ]
}
```

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/03-Improving Your Incident Response Capability/IR in the DevSecOps Pipeline/07-Hands-On Labs|Hands-On Labs]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/03-Improving Your Incident Response Capability/IR in the DevSecOps Pipeline/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/03-Improving Your Incident Response Capability/IR in the DevSecOps Pipeline/09-Identification|Identification]]
