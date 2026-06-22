---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. What is the primary purpose of using a scheduling library like `schedule` in Python?**

The primary purpose of using a scheduling library like `schedule` in Python is to automate the execution of tasks at specified intervals or times. This is particularly useful for tasks such as periodic monitoring, data collection, or any repetitive actions that need to occur without manual intervention. The `schedule` library allows developers to define when and how often certain functions should be executed, making it easier to manage and maintain automated processes.

**Q2. How do you install and import the `schedule` library in a Python project?**

To install the `schedule` library, you can use pip, the Python package installer. Here is the command to install it:

```bash
pip install schedule
```

Once installed, you can import the `schedule` library into your Python script using the following import statement:

```python
import schedule
```

**Q3. Explain how to use the `schedule` library to run a function every five minutes.**

To use the `schedule` library to run a function every five minutes, you first need to define the function that you want to execute periodically. Then, you can use the `schedule.every(interval).units.do(job)` method to specify the interval and the job to be executed. Here’s an example:

```python
import schedule
import time

def check_instance_statuses():
    print("Checking instance statuses...")

# Schedule the function to run every 5 minutes
schedule.every(5).minutes.do(check_instance_statuses)

# Keep the script running to allow the scheduled tasks to execute
while True:
    schedule.run_pending()
    time.sleep(1)
```

In this example, `check_instance_statuses` is the function that will be executed every five minutes. The `schedule.run_pending()` function checks and runs any scheduled jobs that are due to be executed, and `time.sleep(1)` ensures that the script does not consume excessive CPU resources by sleeping for one second between checks.

**Q4. How can you modify the `schedule` library to run a task every day at a specific time, such as 1 AM?**

To run a task every day at a specific time, such as 1 AM, you can use the `schedule.every().day.at('HH:MM').do(job)` method. Here is an example:

```python
import schedule
import time

def daily_task():
    print("Executing daily task at 1 AM...")

# Schedule the function to run every day at 1 AM
schedule.every().day.at("01:00").do(daily_task)

# Keep the script running to allow the scheduled tasks to execute
while True:
    schedule.run_pending()
    time.sleep(1)
```

In this example, `daily_task` is the function that will be executed every day at 1 AM. The `schedule.every().day.at("01:00")` method specifies that the job should be executed every day at the specified time.

**Q5. How can you ensure that the `schedule` library does not overload the system when running tasks frequently?**

To prevent overloading the system when running tasks frequently, you can adjust the frequency of the tasks to a more reasonable interval. Additionally, you can use the `time.sleep()` function to introduce a delay between checks for pending tasks. This reduces the number of times the `schedule.run_pending()` function is called, thereby reducing CPU usage. Here is an example:

```python
import schedule
import time

def check_status():
    print("Checking status...")

# Schedule the function to run every 5 minutes
schedule.every(5).minutes.do(check_status)

# Keep the script running to allow the scheduled tasks to execute
while True:
    schedule.run_pending()
    time.sleep(60)  # Sleep for 60 seconds between checks
```

In this example, the `time.sleep(60)` function introduces a 60-second delay between checks, ensuring that the script does not run continuously and potentially overload the system.

**Q6. How can you modify the `describe_instance_status` API call to include terminated instances in the output?**

To include terminated instances in the output of the `describe_instance_status` API call, you can set the `IncludeAllInstances` parameter to `True`. Here is an example:

```python
import boto3

ec2 = boto3.client('ec2')

response = ec2.describe_instance_status(
    IncludeAllInstances=True
)

for status in response['InstanceStatuses']:
    print(status)
```

In this example, the `IncludeAllInstances=True` parameter ensures that the API call includes the status of all instances, including those that are terminated. This allows you to monitor the status of both running and terminated instances.

**Q7. How can you visualize the output of the `describe_instance_status` API call in a simple web interface?**

To visualize the output of the `describe_instance_status` API call in a simple web interface, you can use a lightweight web framework like Flask. Here is an example:

```python
from flask import Flask, render_template
import boto3

app = Flask(__name__)

@app.route('/')
def index():
    ec2 = boto3.client('ec2')
    response = ec2.describe_instance_status(IncludeAllInstances=True)
    return render_template('index.html', instance_statuses=response['InstanceStatuses'])

if __name__ == '__main__':
    app.run(debug=True)
```

In this example, the Flask application defines a route `/` that calls the `describe_instance_status` API and passes the result to an HTML template (`index.html`). The `index.html` file can then display the instance statuses in a user-friendly format. This approach allows you to have a real-time update about the server statuses in your AWS account through a simple web interface.

---
<!-- nav -->
[[04-Scheduling Python Tasks with the `schedule` Library|Scheduling Python Tasks with the `schedule` Library]] | [[DevOps/DevOps Bootcamp/03-Python & Scripting/19-Scheduling Python Tasks With Schedule Library/00-Overview|Overview]]
