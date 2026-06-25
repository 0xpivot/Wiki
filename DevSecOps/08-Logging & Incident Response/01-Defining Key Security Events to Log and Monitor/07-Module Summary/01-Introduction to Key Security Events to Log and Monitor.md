---
course: DevSecOps
topic: Defining Key Security Events to Log and Monitor
tags: [devsecops]
---

## Introduction to Key Security Events to Log and Monitor

In the realm of DevSecOps, one of the most critical aspects is ensuring that your system can effectively log and monitor key security events. This capability is essential for forensic investigations, compliance adherence, and proactive threat detection. In this chapter, we will delve deep into the importance of logging, the types of key security events to monitor, and how to implement robust logging mechanisms.

### Why Logging is Critical to Forensic Investigation

Logging is the process of recording events that occur within a system. These logs serve as a digital trail of activities, providing invaluable information for forensic investigations. When an incident occurs, logs can help investigators understand what happened, how it happened, and potentially identify the perpetrator.

#### Importance of Logs in Incident Response

Imagine a scenario where a breach has occurred in a financial institution. Without proper logging, the forensic team would have limited information to work with. However, with comprehensive logs, they can trace the steps taken by the attacker, identify vulnerabilities exploited, and understand the timeline of the attack. This information is crucial for both remediation and future prevention.

### Key Data Points Required for Logging

The data points that need to be logged depend on the operating environment and the industry standards applicable to your organization. For instance, financial institutions must adhere to strict regulations such as PCI DSS, which mandates capturing specific data elements.

#### Non-Discretionary Data Elements

Non-discretionary data elements are those that must be captured regardless of the organization's preferences. These typically include:

- **Timestamp**: The exact time when the event occurred.
- **Event Type**: The nature of the event (e.g., login attempt, file access).
- **User ID**: The identity of the user performing the action.
- **IP Address**: The IP address from which the action was initiated.
- **Resource Accessed**: The specific resource (file, database, etc.) accessed.
- **Success/Failure Indicator**: Whether the action was successful or failed.

### Real-World Example: Financial Services Compliance

Consider a recent breach in a financial institution, such as the Capital One breach in 2019 (CVE-2019-11510). The attacker exploited a misconfigured server to gain unauthorized access to sensitive customer data. Proper logging could have provided insights into the actions taken by the attacker, helping to identify the vulnerability and take corrective measures.

#### Full Raw HTTP Request and Response

Here is an example of a full HTTP request and response that might be logged during a login attempt:

```http
POST /login HTTP/1.1
Host: example.com
Content-Type: application/x-www-form-urlencoded
Content-Length: 29

username=admin&password=secret

HTTP/1.1 200 OK
Date: Mon, 27 Jul 2020 12:28:53 GMT
Server: Apache/2.4.41 (Ubuntu)
Content-Length: 17
Content-Type: text/html; charset=UTF-8

Login Successful!
```

### How to Prevent / Defend

To ensure that your logging mechanism is robust and effective, follow these best practices:

#### Secure Coding Fixes

Compare the insecure and secure versions of a login function:

**Insecure Version:**

```python
def login(username, password):
    # Check credentials
    if username == "admin" and password == "secret":
        return "Login Successful!"
    else:
        return "Login Failed"
```

**Secure Version:**

```python
import hashlib

def login(username, password):
    # Hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    # Check credentials
    if username == "admin" and hashed_password == "hashed_secret":
        return "Login Successful!"
    else:
        return "Login Failed"
```

#### Configuration Hardening

Ensure that your logging configuration is hardened against tampering. Here is an example of a hardened logging configuration in an Nginx server:

```nginx
log_format custom '$remote_addr - $remote_user [$time_local] "$request" '
                  '$status $body_bytes_sent "$http_referer" '
                  '"$http_user_agent" "$http_x_forwarded_for"';

access_log /var/log/nginx/access.log custom;
error_log /var/log/nginx/error.log warn;

# Disable logging of certain requests
if ($request_uri ~* "^/api/private") {
    access_log off;
}
```

### Automatic Detection of Changes and Misconfigurations

In a cloud environment, automatic detection of changes and misconfigurations is crucial. Tools like AWS Config, Azure Policy, and Google Cloud Policy can help monitor and enforce compliance with predefined rules.

#### Built-In Services for Change Detection

AWS Config, for example, provides a way to continuously audit your AWS environment. Here is an example of an AWS Config rule to detect unauthorized access:

```json
{
  "ConfigRuleName": "UnauthorizedAccess",
  "Description": "Detects unauthorized access attempts.",
  "Scope": {
    "ComplianceResourceTypes": [
      "AWS::EC2::Instance",
      "AWS::IAM::Role"
    ]
  },
  "Source": {
    "Owner": "AWS",
    "SourceIdentifier": "UnauthorizedAccess"
  }
}
```

### Proof of Concept Implementation

While the proof of concept implemented in this module may not be production-ready, it serves as a foundation for building more robust solutions. For instance, you can start with a simple script to monitor changes in IAM roles:

```bash
#!/bin/bash

# Monitor IAM role changes
aws iam get-role --role-name ExampleRole > current_state.json

while true; do
  aws iam get-role --role-name ExampleRole > new_state.json
  diff current_state.json new_state.json
  if [ $? -ne 0 ]; then
    echo "IAM Role change detected!"
    mv new_state.json current_state.json
  fi
  sleep 60
done
```

### Hands-On Labs

For practical experience, consider using the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs to practice web security concepts.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **CloudGoat**: Provides a set of labs to practice cloud security concepts on AWS.

### Conclusion

In conclusion, logging and monitoring key security events are fundamental to maintaining the security and integrity of your systems. By understanding the importance of logging, identifying the necessary data points, and implementing robust logging mechanisms, you can significantly enhance your ability to detect and respond to security incidents. Always remember to follow best practices for secure coding, configuration hardening, and automatic detection of changes and misconfigurations.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/01-Defining Key Security Events to Log and Monitor/07-Module Summary/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/01-Defining Key Security Events to Log and Monitor/07-Module Summary/02-Practice Questions & Answers|Practice Questions & Answers]]
