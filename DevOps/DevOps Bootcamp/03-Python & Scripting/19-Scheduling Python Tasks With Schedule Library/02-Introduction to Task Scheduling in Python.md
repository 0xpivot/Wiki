---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Task Scheduling in Python

Task scheduling is a fundamental aspect of many applications, particularly those involving periodic operations such as monitoring system status, sending notifications, or performing regular maintenance tasks. In Python, one of the most popular libraries for task scheduling is the `schedule` library. This library allows you to define and manage scheduled tasks in a simple and intuitive manner.

### Why Use Task Scheduling?

In many scenarios, executing a script or function only once is insufficient. For instance, if you are monitoring the status of a server or a set of instances, you would want to check their status periodically rather than manually executing the script each time. Task scheduling helps automate these repetitive tasks, ensuring they run at specified intervals without human intervention.

### Common Use Cases

1. **Monitoring System Status**: Regularly checking the health of servers, databases, or other critical systems.
2. **Data Processing**: Running data processing jobs at specific times, such as daily backups or weekly reports.
3. **Notification Systems**: Sending out alerts or notifications based on predefined schedules.
4. **Maintenance Tasks**: Performing routine maintenance tasks like cleaning up logs or updating software.

### The `schedule` Library

The `schedule` library is a lightweight Python module designed for scheduling tasks. It provides a simple API for defining and managing scheduled tasks. Here’s how you can install and use it:

```bash
pip install schedule==1.10.0
```

Once installed, you can import the `schedule` module in your Python script and start defining your tasks.

### Example: Monitoring Instance Status

Let's walk through an example where we monitor the status of instances every five minutes using the `schedule` library.

#### Step 1: Install the `schedule` Library

First, ensure the `schedule` library is installed:

```bash
pip install schedule==1.10.0
```

#### Step 2: Import the `schedule` Module

Next, import the `schedule` module in your Python script:

```python
import schedule
import time
```

#### Step 3: Define the Task Function

Define a function that represents the task you want to perform. In this case, we'll create a function named `check_instance_status`:

```python
def check_instance_status():
    print("Checking instance status...")
    # Add your logic to check the status of instances here
```

#### Step 4: Schedule the Task

Use the `schedule.every()` method to specify the interval at which the task should run. In this example, we'll run the task every five minutes:

```python
schedule.every(5).minutes.do(check_instance_status)
```

#### Step 5: Run the Scheduler

Finally, run the scheduler in an infinite loop to keep the script running and executing the scheduled tasks:

```python
while True:
    schedule.run_pending()
    time.sleep(1)
```

### Complete Example

Here is the complete code for the example:

```python
import schedule
import time

def check_instance_status():
    print("Checking instance status...")
    # Add your logic to check the status of instances here

# Schedule the task to run every 5 minutes
schedule.every(5).minutes.do(check_instance_status)

# Run the scheduler in an infinite loop
while True:
    schedule.run_pending()
    time.sleep(1)
```

### Explanation of the Code

1. **Importing Modules**:
   - `schedule`: The task scheduling library.
   - `time`: Used to introduce delays in the infinite loop.

2. **Defining the Task Function**:
   - `check_instance_status()`: A placeholder function where you would implement the logic to check the status of instances.

3. **Scheduling the Task**:
   - `schedule.every(5).minutes.do(check_instance_status)`: Schedules the `check_instance_status` function to run every five minutes.

4. **Running the Scheduler**:
   - `while True`: An infinite loop to keep the script running.
   - `schedule.run_pending()`: Checks and runs any pending scheduled tasks.
   - `time.sleep(1)`: Pauses the loop for one second to avoid high CPU usage.

### Real-World Examples

#### Example 1: Monitoring Server Health

Suppose you are monitoring the health of a server. You might want to check the CPU usage, memory usage, and disk space every five minutes. Here’s how you could implement this:

```python
import schedule
import time
import psutil

def check_server_health():
    cpu_usage = psutil.cpu_percent(interval=1)
    memory_usage = psutil.virtual_memory().percent
    disk_usage = psutil.disk_usage('/').percent
    print(f"CPU Usage: {cpu_usage}%")
    print(f"Memory Usage: {memory_usage}%")
    print(f"Disk Usage: {disk_usage}%")

schedule.every(5).minutes.do(check_server_health)

while True:
    schedule.run_pending()
    time.sleep(1)
```

#### Example 2: Sending Daily Reports

If you need to send daily reports, you can schedule a task to run at a specific time each day:

```python
import schedule
import time
from datetime import datetime

def send_daily_report():
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"Sending daily report at {current_time}")

schedule.every().day.at("08:00").do(send_daily_report)

while True:
    schedule.run_pending()
    time.sleep(1)
```

### Pitfalls and Best Practices

#### Common Mistakes

1. **Infinite Loops**: Ensure your infinite loop does not consume excessive CPU resources. Use `time.sleep()` to introduce delays.
2. **Task Overlap**: Be cautious of overlapping tasks. If a task takes longer than the interval between executions, it may cause issues.
3. **Error Handling**: Implement error handling within your task functions to prevent the entire script from failing due to a single error.

#### Best Practices

1. **Logging**: Use logging to track the execution of scheduled tasks and any errors that occur.
2. **Testing**: Thoroughly test your scheduled tasks to ensure they behave as expected.
3. **Documentation**: Document your scheduled tasks and their intervals to maintain clarity and ease future maintenance.

### How to Prevent / Defend

#### Detection

1. **Logging**: Implement comprehensive logging to track the execution of scheduled tasks.
2. **Monitoring Tools**: Use monitoring tools like Prometheus or Grafana to visualize the performance and behavior of your scheduled tasks.

#### Prevention

1. **Error Handling**: Implement robust error handling within your task functions to prevent failures from causing the entire script to fail.
2. **Resource Management**: Ensure your tasks do not consume excessive resources. Use `time.sleep()` to introduce delays in infinite loops.

#### Secure Coding Fixes

##### Vulnerable Code

```python
def check_instance_status():
    print("Checking instance status...")
    # Add your logic to check the status of instances here
```

##### Secure Code

```python
import logging

logging.basicConfig(filename='scheduled_tasks.log', level=logging.INFO)

def check_instance_status():
    try:
        print("Checking instance status...")
        # Add your logic to check the status of instances here
        logging.info("Instance status checked successfully.")
    except Exception as e:
        logging.error(f"Error occurred: {str(e)}")
```

### Conclusion

Task scheduling is a crucial aspect of automating repetitive tasks in Python. The `schedule` library provides a simple and effective way to manage scheduled tasks. By following best practices and implementing robust error handling, you can ensure your scheduled tasks run smoothly and securely.

### Practice Labs

For hands-on practice with task scheduling in Python, consider the following labs:

- **PortSwigger Web Security Academy**: Offers exercises related to web application security, including task scheduling.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills, including task scheduling.
- **DVWA (Damn Vulnerable Web Application)**: Another web application for practicing security skills, including task scheduling.

These labs provide practical experience in applying task scheduling concepts in real-world scenarios.

---
<!-- nav -->
[[01-Introduction to Scheduling Python Tasks with the `schedule` Library|Introduction to Scheduling Python Tasks with the `schedule` Library]] | [[DevOps/DevOps Bootcamp/03-Python & Scripting/19-Scheduling Python Tasks With Schedule Library/00-Overview|Overview]] | [[03-Introduction to Task Scheduling with the `schedule` Library|Introduction to Task Scheduling with the `schedule` Library]]
