---
course: DevSecOps
topic: Logging & Monitoring for Security
tags: [devsecops]
---

## Introduction to Logging and Monitoring for Security

Logging and monitoring are critical components of a robust security strategy in DevSecOps environments. They enable organizations to detect and respond to security incidents promptly, ensuring that systems remain secure and operational. This chapter delves into configuring alarms for failed login attempts, a common yet crucial aspect of security monitoring.

### What is Logging?

Logging is the process of recording events that occur within a system. These logs provide a detailed record of activities, errors, and other significant occurrences. In the context of security, logs are essential for detecting unauthorized access attempts, identifying patterns of malicious activity, and auditing user actions.

#### Why Logging Matters

- **Detection**: Logs help identify suspicious behavior and potential security breaches.
- **Auditing**: Logs provide a historical record of system activities, which is crucial for compliance and forensic analysis.
- **Troubleshooting**: Logs assist in diagnosing issues and understanding the root cause of problems.

### What is Monitoring?

Monitoring involves continuously observing and analyzing system performance and behavior. In a security context, monitoring helps detect anomalies and potential threats in real-time.

#### Why Monitoring Matters

- **Real-Time Alerts**: Monitoring systems can trigger alerts immediately when suspicious activity is detected.
- **Proactive Defense**: By identifying threats early, organizations can take preventive actions before damage occurs.
- **Performance Optimization**: Monitoring also helps in optimizing system performance by identifying bottlenecks and inefficiencies.

### Failed Login Attempts

Failed login attempts are a common indicator of potential security threats. Attackers often attempt to gain unauthorized access by repeatedly guessing passwords or using automated tools to brute-force login credentials.

#### Why Failed Login Attempts Matter

- **Brute-Force Attacks**: Attackers may use automated tools to try numerous password combinations until they succeed.
- **Credential Stuffing**: Attackers may use stolen credentials from one service to attempt access to another.
- **Account Takeover**: Successful login attempts can lead to unauthorized access and potential data theft.

### Configuring Alarms for Failed Login Attempts

To effectively monitor and respond to failed login attempts, it is essential to configure alarms that trigger when a certain threshold of failed attempts is reached. This section explains how to set up such alarms and the underlying mechanisms involved.

#### Step-by-Step Configuration

1. **Identify the Source of Logs**:
   - Determine where login attempts are logged. This could be in application logs, system logs, or specific security logs.
   - Example: In an AWS environment, failed login attempts might be logged in CloudTrail or AWS Identity and Access Management (IAM).

2. **Set Up Log Collection**:
   - Use a centralized logging solution like ELK Stack (Elasticsearch, Logstash, Kibana) or Splunk to collect and aggregate logs.
   - Example: Using Logstash to ingest logs from various sources and store them in Elasticsearch.

```yaml
input {
  beats {
    port => 5044
  }
}

filter {
  grok {
    match => { "message" => "%{TIMESTAMP_ISO8601:timestamp} %{LOGLEVEL:loglevel} %{IP:ip} %{WORD:username} %{WORD:action}" }
  }
}

output {
  elasticsearch {
    hosts => ["localhost:9200"]
    index => "login-attempts-%{+YYYY.MM.dd}"
  }
}
```

3. **Define Metrics and Thresholds**:
   - Define metrics to track the number of failed login attempts.
   - Set thresholds for triggering alarms. For example, if there are more than 5 failed login attempts within a 15-minute interval, an alarm should be triggered.

```json
{
  "metric": "failed_login_attempts",
  "threshold": 5,
  "interval": "PT15M"
}
```

4. **Configure Alarms**:
   - Use a monitoring tool like Prometheus or AWS CloudWatch to define alarms based on the metrics and thresholds.
   - Example: Setting up an alarm in AWS CloudWatch to notify when the number of failed login attempts exceeds the defined threshold.

```yaml
Resources:
  FailedLoginAlarm:
    Type: AWS::CloudWatch::Alarm
    Properties:
      AlarmName: FailedLoginAttemptsAlarm
      ComparisonOperator: GreaterThanThreshold
      EvaluationPeriods: 1
      MetricName: FailedLoginAttempts
      Namespace: CustomMetrics
      Period: 900
      Statistic: Sum
      Threshold: 5
      ActionsEnabled: true
      AlarmActions:
        - !Ref SNSNotificationTopic
```

5. **Implement Response Actions**:
   - Define actions to take when an alarm is triggered. This could include blocking the IP address, sending notifications, or initiating further investigation.
   - Example: Blocking the IP address using AWS WAF.

```json
{
  "WebACL": {
    "DefaultAction": {
      "Type": "ALLOW"
    },
    "Rules": [
      {
        "Name": "BlockFailedLoginIP",
        "Priority": 1,
        "Statement": {
          "ByteMatchStatement": {
            "FieldToMatch": {
              "SingleHeader": {
                "Name": "X-Forwarded-For"
              }
            },
            "TextTransformations": [
              {
                "Priority": 1,
                "Type": "NONE"
              }
            ],
            "SearchString": "<blocked_ip>",
            "ComparisonOperator": "EQUALS"
          }
        },
        "Action": {
          "Type": "BLOCK"
        }
      }
    ]
  }
}
```

### Real-World Examples

#### Recent Breaches and CVEs

- **CVE-2021-44228 (Log4Shell)**: This vulnerability in Apache Log4j allowed attackers to execute arbitrary code by injecting malicious log messages. Proper logging and monitoring could have helped detect and mitigate such attacks.
- **SolarWinds Supply Chain Attack (2020)**: This attack involved the compromise of SolarWinds Orion software, leading to widespread infiltration of government and private sector networks. Effective monitoring and logging would have enabled earlier detection of the malicious activity.

### Common Pitfalls

- **Insufficient Logging**: Not logging enough information can make it difficult to trace the source of security incidents.
- **False Positives**: Overly sensitive alarms can generate false positives, leading to alert fatigue and reduced effectiveness.
- **Configuration Drift**: Changes in system configurations can invalidate existing logging and monitoring setups, requiring regular updates and validation.

### How to Prevent / Defend

#### Detection

- **Centralized Logging**: Use a centralized logging solution to aggregate and analyze logs from various sources.
- **Real-Time Monitoring**: Implement real-time monitoring to detect and respond to security incidents promptly.

#### Prevention

- **Rate Limiting**: Implement rate limiting to prevent brute-force attacks by restricting the number of login attempts from a single IP address.
- **Multi-Factor Authentication (MFA)**: Require MFA for login attempts to add an additional layer of security.

#### Secure Coding Fixes

- **Vulnerable Code**:
  
```python
def authenticate(username, password):
    if username == 'admin' and password == 'password':
        return True
    else:
        return False
```

- **Secure Code**:

```python
import bcrypt

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)

hashed_password = hash_password('password')

def authenticate(username, password):
    if username == 'admin' and check_password(hashed_password, password):
        return True
    else:
        return False
```

#### Configuration Hardening

- **AWS Security Groups**: Restrict inbound traffic to only necessary ports and IP addresses.
- **IAM Policies**: Use least privilege principles to restrict permissions and limit access to sensitive resources.

### Conclusion

Effective logging and monitoring are essential for maintaining the security of DevSecOps environments. By configuring alarms for failed login attempts, organizations can detect and respond to potential threats promptly. This chapter provided a comprehensive guide to setting up such alarms, including background theory, recent real-world examples, complete code, and practical defenses. 

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice web security techniques, including logging and monitoring.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing and monitoring.
- **DVWA (Damn Vulnerable Web Application)**: Provides a platform to learn about web application security, including logging and monitoring.

By leveraging these resources, you can gain practical experience in implementing and managing logging and monitoring systems for security.

---
<!-- nav -->
[[02-Introduction to Logging and Monitoring for Security Part 2|Introduction to Logging and Monitoring for Security Part 2]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/04-Logging & Monitoring for Security/Configure Alarm for Failed Login Attempts/00-Overview|Overview]] | [[04-Introduction to Logging and Monitoring for Security Part 4|Introduction to Logging and Monitoring for Security Part 4]]
