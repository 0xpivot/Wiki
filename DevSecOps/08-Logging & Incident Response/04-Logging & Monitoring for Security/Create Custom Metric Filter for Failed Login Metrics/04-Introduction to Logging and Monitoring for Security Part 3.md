---
course: DevSecOps
topic: Logging & Monitoring for Security
tags: [devsecops]
---

## Introduction to Logging and Monitoring for Security

Logging and monitoring are critical components of DevSecOps, enabling teams to detect and respond to security incidents promptly. In this section, we will delve into creating custom metric filters for tracking failed login attempts, which is a common security concern. This process involves setting up logging and monitoring tools to capture and analyze specific events, such as failed login attempts, and then using these insights to enhance security measures.

### What Are Logs and Metrics?

**Logs** are records of events that occur within an application or system. They provide detailed information about the activities performed by the system, including user actions, errors, and other significant events. Logs are essential for troubleshooting, auditing, and security analysis.

**Metrics**, on the other hand, are numerical measurements that describe the behavior of a system. Metrics can be used to track various aspects of system performance, such as CPU usage, memory consumption, and the number of failed login attempts. By analyzing metrics, teams can identify trends and anomalies that may indicate security issues.

### Why Track Failed Login Attempts?

Tracking failed login attempts is crucial for several reasons:

1. **Security Breach Detection**: Frequent failed login attempts can indicate a brute-force attack, where an attacker tries to guess a user's password through repeated attempts.
2. **Anomaly Detection**: Unusual patterns in failed login attempts can signal unauthorized access attempts or compromised accounts.
3. **Incident Response**: By monitoring failed login attempts, teams can quickly respond to potential security incidents and mitigate risks.

### Creating Custom Metric Filters

In this section, we will walk through the process of creating a custom metric filter to track failed login attempts. We will use AWS CloudWatch as our logging and monitoring platform, but the principles apply to other platforms as well.

#### Step 1: Define the Filter Pattern

The first step is to define the filter pattern that identifies failed login attempts. A filter pattern is a regular expression that matches specific log entries. For example, a typical log entry for a failed login attempt might look like this:

```
Failed login attempt for user 'admin' from IP address '192.168.1.1'
```

To create a filter pattern that matches this log entry, we can use the following regular expression:

```regex
Failed login attempt for user '.+' from IP address '.+'
```

This regular expression matches any string that starts with "Failed login attempt for user" followed by any characters (denoted by `.+`), and then "from IP address" followed by any characters.

#### Step 2: Define the Metric Namespace

A metric namespace is a category that groups related metrics together. In our case, we can create a namespace called `LoginNamespace` to group all metrics related to login events.

```yaml
MetricNamespace: LoginNamespace
```

#### Step 3: Define the Metric Name

The metric name is the specific identifier for the metric within the namespace. We can call our metric `FailedLogin`.

```yaml
MetricName: FailedLogin
```

#### Step 4: Define the Metric Value

The metric value is the numerical value that is published every time the filter pattern is matched. In our case, we can set the metric value to `1` every time a failed login attempt is detected.

```yaml
MetricValue: 1
```

#### Step 5: Create the Metric Filter

Now that we have defined the filter pattern, metric namespace, metric name, and metric value, we can create the metric filter. This can be done using the AWS Management Console or the AWS CLI.

##### Using the AWS Management Console

1. Navigate to the CloudWatch dashboard.
2. Click on "Logs" in the left-hand menu.
3. Select the log group where the failed login attempts are logged.
4. Click on "Create metric filter".
5. Enter the filter pattern, metric namespace, metric name, and metric value.
6. Click "Create filter".

##### Using the AWS CLI

We can also create the metric filter using the AWS CLI. Here is an example command:

```bash
aws logs put-metric-filter --log-group-name /var/log/auth.log --filter-name FailedLoginFilter --metric-transformations metricName=FailedLogin,metricNamespace=LoginNamespace,defaultValue=1 --filter-pattern 'Failed login attempt for user '.+' from IP address '.+'
```

### Example: Real-World Application

Let's consider a real-world scenario where a company uses AWS CloudWatch to monitor their application logs. The company wants to track failed login attempts to detect potential security breaches.

#### Log Group Configuration

First, we need to configure the log group where the failed login attempts are logged. This can be done using the AWS Management Console or the AWS CLI.

##### Using the AWS Management Console

1. Navigate to the CloudWatch dashboard.
2. Click on "Logs" in the left-hand menu.
3. Click on "Create log group".
4. Enter the name of the log group, such as `/var/log/auth.log`.
5. Click "Create log group".

##### Using the AWS CLI

We can also create the log group using the AWS CLI. Here is an example command:

```bash
aws logs create-log-group --log-group-name /var/log/auth.log
```

#### Log Stream Configuration

Next, we need to configure the log stream where the failed login attempts are logged. This can be done using the AWS Management Console or the AWS CLI.

##### Using the AWS Management Console

1. Navigate to the CloudWatch dashboard.
2. Click on "Logs" in the left-hand menu.
3. Select the log group where the failed login attempts are logged.
4. Click on "Create log stream".
5. Enter the name of the log stream, such as `auth.log`.
6. Click "Create log stream".

##### Using the AWS CLI

We can also create the log stream using the AWS CLI. Here is an example command:

```bash
aws logs create-log-stream --log-group-name /var/log/auth.log --log-stream-name auth.log
```

#### Log Data Ingestion

Once the log group and log stream are configured, we need to ingest the log data. This can be done using the AWS CLI or by configuring the application to send log data to CloudWatch.

##### Using the AWS CLI

We can use the `put-log-events` command to ingest log data into CloudWatch. Here is an example command:

```bash
aws logs put-log-events --log-group-name /var/log/auth.log --log-stream-name auth.log --log-events '[{"timestamp": 1633072800000, "message": "Failed login attempt for user 'admin' from IP address '192.168.1.1'"}]'
```

##### Configuring the Application

Alternatively, we can configure the application to send log data to CloudWatch using the AWS SDK. Here is an example code snippet in Python:

```python
import boto3

client = boto3.client('logs')

response = client.put_log_events(
    logGroupName='/var/log/auth.log',
    logStreamName='auth.log',
    logEvents=[
        {
            'timestamp': 1633072800000,
            'message': 'Failed login attempt for user \'admin\' from IP address \'192.168.1.1\''
        },
    ]
)
```

### Monitoring and Alerting

Once the metric filter is created, we can set up monitoring and alerting to detect and respond to failed login attempts. This can be done using CloudWatch Alarms.

#### Setting Up an Alarm

1. Navigate to the CloudWatch dashboard.
2. Click on "Alarms" in the left-hand menu.
3. Click on "Create alarm".
4. Select the metric namespace and metric name.
5. Set the threshold and evaluation period.
6. Configure the alarm actions, such as sending an email or triggering an SNS notification.
7. Click "Create alarm".

Here is an example of a CloudWatch Alarm configuration:

```yaml
AlarmName: FailedLoginAlarm
MetricNamespace: LoginNamespace
MetricName: FailedLogin
Threshold: 5
EvaluationPeriods: 1
ComparisonOperator: GreaterThanOrEqualToThreshold
ActionsEnabled: true
AlarmActions:
  - arn:aws:sns:us-east-1:123456789012:FailedLoginNotification
```

### Real-World Examples and Recent CVEs

#### Example: Brute-Force Attack Detection

In a recent breach, a company detected a brute-force attack on their login system. By monitoring failed login attempts, they were able to identify the attack and take immediate action to secure their systems.

#### CVE Example: CVE-2021-3129

CVE-2021-3129 is a vulnerability in the Apache Struts framework that allows attackers to execute arbitrary code by exploiting a deserialization flaw. By monitoring failed login attempts, organizations can detect and respond to such attacks more effectively.

### How to Prevent / Defend

#### Secure Coding Practices

To prevent brute-force attacks and other security breaches, it is important to follow secure coding practices. Here are some best practices:

1. **Use Strong Password Policies**: Enforce strong password policies, such as requiring complex passwords and enforcing password expiration.
2. **Implement Account Lockout Mechanisms**: Implement account lockout mechanisms to temporarily lock accounts after a certain number of failed login attempts.
3. **Use Multi-Factor Authentication (MFA)**: Implement multi-factor authentication to add an additional layer of security to the login process.

#### Secure Configuration

To secure the configuration of your logging and monitoring system, follow these best practices:

1. **Limit Access to Log Files**: Limit access to log files to authorized personnel only.
2. **Encrypt Log Data**: Encrypt log data to protect sensitive information.
3. **Regularly Review Log Data**: Regularly review log data to detect and respond to security incidents.

#### Secure Code Examples

Here is an example of a vulnerable code snippet that does not implement secure coding practices:

```python
# Vulnerable code
def authenticate(username, password):
    if username == 'admin' and password == 'password':
        return True
    else:
        return False
```

Here is an example of a secure code snippet that implements secure coding practices:

```python
# Secure code
import bcrypt

def hash_password(password):
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password

def authenticate(username, password):
    stored_password = get_stored_password(username)
    if bcrypt.checkpw(password.encode('utf-8'), stored_password):
        return True
    else:
        return False
```

### Conclusion

Creating custom metric filters for tracking failed login attempts is a crucial step in enhancing the security of your application. By monitoring and analyzing failed login attempts, you can detect and respond to potential security breaches more effectively. Follow the steps outlined in this chapter to set up logging and monitoring for your application, and implement secure coding practices to prevent security breaches.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice web security concepts, including logging and monitoring.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is vulnerable by design for educational purposes.

By completing these labs, you can gain practical experience in setting up logging and monitoring for security.

---
<!-- nav -->
[[03-Introduction to Logging and Monitoring for Security Part 2|Introduction to Logging and Monitoring for Security Part 2]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/04-Logging & Monitoring for Security/Create Custom Metric Filter for Failed Login Metrics/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/08-Logging & Incident Response/04-Logging & Monitoring for Security/Create Custom Metric Filter for Failed Login Metrics/05-Introduction to Logging and Monitoring for Security|Introduction to Logging and Monitoring for Security]]
