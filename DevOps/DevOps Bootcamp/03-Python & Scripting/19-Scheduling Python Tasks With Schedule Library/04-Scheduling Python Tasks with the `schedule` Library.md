---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Scheduling Python Tasks with the `schedule` Library

### Introduction to Task Scheduling

Task scheduling is an essential aspect of many applications, particularly those that require periodic execution of certain tasks. In Python, the `schedule` library provides a simple way to schedule tasks at specific intervals or times. This chapter will delve into the details of using the `schedule` library to manage and execute tasks efficiently.

### Background Theory

#### What is Task Scheduling?

Task scheduling refers to the process of planning and executing tasks at specified intervals or times. This is crucial for various applications such as:

- **Monitoring**: Regularly checking the status of systems or services.
- **Automation**: Automating repetitive tasks to save time and reduce errors.
- **Maintenance**: Performing routine maintenance tasks like backups or updates.

#### Why Use Task Scheduling?

Using task scheduling helps in:

- **Efficiency**: Automating tasks reduces manual intervention and ensures consistency.
- **Reliability**: Scheduled tasks can be configured to run even if the system restarts.
- **Flexibility**: Tasks can be scheduled to run at specific intervals or times, providing flexibility in task management.

### The `schedule` Library

The `schedule` library is a lightweight Python module that allows you to schedule functions to be executed periodically. It is easy to use and does not require complex setup.

#### Installation

To install the `schedule` library, you can use pip:

```bash
pip install schedule
```

### Basic Usage

Let's start with a basic example of how to use the `schedule` library to run a function periodically.

#### Example: Running a Function Every Minute

```python
import schedule
import time

def job():
    print("Job executed")

# Schedule the job to run every minute
schedule.every(1).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
```

In this example:
- The `job` function is defined to print a message.
- `schedule.every(1).minutes.do(job)` schedules the `job` function to run every minute.
- The `while True` loop keeps the script running and checks for pending jobs using `schedule.run_pending()`.

### Advanced Usage

Now, let's explore more advanced features of the `schedule` library.

#### Specifying Different Time Intervals

You can specify different time intervals for scheduling tasks. Here are some examples:

- **Every 10 seconds**:
  ```python
  schedule.every(10).seconds.do(job)
  ```

- **Every 5 minutes**:
  ```python
  schedule.every(5).minutes.do(job)
  ```

- **Every hour**:
  ```python
  schedule.every().hour.do(job)
  ```

- **Every day at a specific time**:
  ```python
  schedule.every().day.at("10:30").do(job)
  ```

### Monitoring Instance Status with AWS SDK

Let's integrate the `schedule` library with AWS SDK to monitor instance statuses periodically.

#### AWS SDK Setup

First, ensure you have the AWS SDK installed:

```bash
pip install boto3
```

Then, configure your AWS credentials:

```bash
aws configure
```

#### Monitoring Instances

We will use the `boto3` library to interact with AWS EC2 instances and the `schedule` library to schedule the monitoring task.

```python
import boto3
import schedule
import time

def monitor_instances():
    ec2 = boto3.client('ec2')
    response = ec2.describe_instance_status(IncludeAllInstances=True)
    for status in response['InstanceStatuses']:
        print(f"Instance ID: {status['InstanceId']}, State: {status['InstanceState']['Name']}")

# Schedule the monitoring task to run every 5 minutes
schedule.every(5).minutes.do(monitor_instances)

while True:
    schedule.run_pending()
    time.sleep(1)
```

In this example:
- The `monitor_instances` function uses the `boto3` client to describe instance statuses.
- `IncludeAllInstances=True` ensures that both running and non-running instances are included in the response.
- The `schedule.every(5).minutes.do(monitor_instances)` schedules the `monitor_instances` function to run every 5 minutes.

### Handling Different Instance States

AWS instances can be in different states such as `running`, `terminated`, `shutting-down`, etc. Let's handle these states explicitly.

#### Example: Handling Different Instance States

```python
import boto3
import schedule
import time

def monitor_instances():
    ec2 = boto3.client('ec2')
    response = ec2.describe_instance_status(IncludeAllInstances=True)
    for status in response['InstanceStatuses']:
        instance_id = status['InstanceId']
        state = status['InstanceState']['Name']
        print(f"Instance ID: {instance_id}, State: {state}")

# Schedule the monitoring task to run every 5 minutes
schedule.every(5).minutes.do(monitor_instances)

while True:
    schedule.run_pending()
    time.sleep(1)
```

In this example:
- The `monitor_instances` function prints the instance ID and state for each instance.

### Real-World Examples and Recent Breaches

#### Real-World Example: Monitoring EC2 Instances

Consider a scenario where you need to monitor the health of EC2 instances in an AWS environment. Using the `schedule` library, you can automate this process to run periodically.

#### Recent Breach Example: Unsecured AWS Instances

A recent breach involved unsecured AWS instances that were left open to the internet. By regularly monitoring instance statuses, you can detect and mitigate such vulnerabilities.

### Pitfalls and Common Mistakes

#### Common Mistakes

- **Not Handling Exceptions**: Always wrap your scheduled tasks in try-except blocks to handle exceptions gracefully.
- **Incorrect Time Intervals**: Ensure you specify the correct time intervals for your tasks.
- **Resource Leaks**: Make sure your tasks do not leave resources open, leading to potential leaks.

### How to Prevent / Defend

#### Detection

- **Logging**: Implement logging to track the execution of scheduled tasks.
- **Monitoring Tools**: Use monitoring tools like AWS CloudWatch to track the health of your instances.

#### Prevention

- **Secure Configuration**: Ensure your AWS instances are configured securely, with proper IAM roles and permissions.
- **Regular Audits**: Perform regular audits to check the health and security of your instances.

#### Secure Coding Fixes

##### Vulnerable Code

```python
import boto3
import schedule
import time

def monitor_instances():
    ec2 = boto3.client('ec2')
    response = ec2.describe_instance_status()
    for status in response['InstanceStatuses']:
        print(f"Instance ID: {status['InstanceId']}, State: {status['InstanceState']['Name']}")

# Schedule the monitoring task to run every 5 minutes
schedule.every(5).minutes.do(monitor_instances)

while True:
    schedule.run_pending()
    time.sleep(1)
```

##### Fixed Code

```python
import boto3
import schedule
import time

def monitor_instances():
    try:
        ec2 = boto3.client('ec2')
        response = ec2.describe_instance_status(IncludeAllInstances=True)
        for status in response['InstanceStatuses']:
            print(f"Instance ID: {status['InstanceId']}, State: {status['InstanceState']['Name']}")
    except Exception as e:
        print(f"Error: {e}")

# Schedule the monitoring task to run every 5 minutes
schedule.every(5).minutes.do(monitor_instances)

while True:
    schedule.run_pending()
    time.sleep(1)
```

### Conclusion

This chapter covered the basics and advanced usage of the `schedule` library in Python, integrating it with AWS SDK to monitor instance statuses. We also discussed real-world examples, recent breaches, common pitfalls, and how to prevent and defend against potential issues. By following these guidelines, you can effectively manage and schedule tasks in your Python applications.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises related to web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.
- **WebGoat**: An interactive, gamified training application for learning about web application security.

These labs provide practical experience in applying the concepts learned in this chapter.

---
<!-- nav -->
[[03-Introduction to Task Scheduling with the `schedule` Library|Introduction to Task Scheduling with the `schedule` Library]] | [[DevOps/DevOps Bootcamp/03-Python & Scripting/19-Scheduling Python Tasks With Schedule Library/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/03-Python & Scripting/19-Scheduling Python Tasks With Schedule Library/05-Practice Questions & Answers|Practice Questions & Answers]]
