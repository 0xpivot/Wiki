---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain how Python can be used to automate DevOps tasks, and provide an example of a specific task that can be automated.**

Python can be used to automate DevOps tasks by leveraging its extensive libraries and frameworks to interact with cloud services, manage infrastructure, and monitor applications. For instance, using the `boto3` library, you can automate the creation and management of Amazon Web Services (AWS) resources such as EC2 instances, VPCs, and S3 buckets. An example of a specific task that can be automated is creating and managing EC2 instances. Here’s a simple script to check the status of EC2 instances:

```python
import boto3

def check_ec2_instance_status():
    ec2 = boto3.client('ec2')
    response = ec2.describe_instance_status()
    for instance in response['InstanceStatuses']:
        print(f"Instance ID: {instance['InstanceId']}, Status: {instance['InstanceState']['Name']}")

check_ec2_instance_status()
```

This script uses the `boto3` client to describe the status of EC2 instances and prints out the instance IDs along with their current states.

**Q2. How does the `boto3` library differ from Terraform in terms of cloud resource management? Provide an example of when you might prefer one over the other.**

The `boto3` library is a Python SDK for AWS, providing low-level access to AWS services, whereas Terraform is an infrastructure as code (IaC) tool that allows you to define and provision infrastructure across multiple cloud providers. 

For example, `boto3` is more suitable for scripting and automation tasks within a Python environment, such as dynamically managing resources based on certain conditions. On the other hand, Terraform is better suited for defining and provisioning infrastructure in a declarative manner, making it easier to version control and collaborate on infrastructure definitions.

Here’s an example of when you might prefer `boto3` over Terraform: If you need to create an EC2 instance only when a specific condition is met (e.g., during peak load times), you might use `boto3` to write a Python script that checks the condition and creates the instance accordingly. This kind of dynamic behavior is harder to achieve with Terraform without additional scripting.

**Q3. Describe how you would write a Python program to monitor a remote server and notify you via email if the server goes down.**

To monitor a remote server and notify you via email if the server goes down, you can use Python to periodically check the server's status and send an email if the server is unresponsive. Here’s a basic outline of how you could implement this:

1. Use the `requests` library to ping the server and check if it responds successfully.
2. Use the `smtplib` library to send an email notification if the server is down.
3. Schedule the monitoring task to run at regular intervals using the `schedule` library.

Here’s a sample implementation:

```python
import requests
import smtplib
from email.mime.text import MIMEText
from schedule import every, run_pending
import time

def check_server_status(url):
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def send_email_notification(subject, body):
    sender = 'your-email@example.com'
    receiver = 'receiver-email@example.com'
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    with smtplib.SMTP('smtp.example.com') as server:
        server.login(sender, 'your-password')
        server.sendmail(sender, [receiver], msg.as_string())

def monitor_server():
    url = 'http://example.com'
    if not check_server_status(url):
        send_email_notification('Server Down', f'The server at {url} is down.')

# Schedule the monitoring task to run every 5 minutes
every(5).minutes.do(monitor_server)

while True:
    run_pending()
    time.sleep(1)
```

This script checks the server's status every 5 minutes and sends an email if the server is down.

**Q4. Explain how you would automate the recovery process for a failed server using Python.**

To automate the recovery process for a failed server using Python, you can follow these steps:

1. Check the server's status using a monitoring script.
2. If the server is down, attempt to restart the Docker container running the application.
3. If the Docker container fails to restart, reboot the server.
4. Send notifications via email or another communication channel to inform the team of the actions taken.

Here’s a sample implementation:

```python
import os
import subprocess
import smtplib
from email.mime.text import MIMEText
from schedule import every, run_pending
import time

def check_server_status(url):
    try:
        response = requests.get(url)
        return response.status_code == 200
    except requests.exceptions.RequestException:
        return False

def restart_docker_container(container_name):
    try:
        subprocess.run(['docker', 'restart', container_name], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def reboot_server():
    os.system('sudo reboot')

def send_email_notification(subject, body):
    sender = 'your-email@example.com'
    receiver = 'receiver-email@example.com'
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = receiver

    with smtplib.SMTP('smtp.example.com') as server:
        server.login(sender, 'your-password')
        server.sendmail(sender, [receiver], msg.as_string())

def monitor_and_recover_server():
    url = 'http://example.com'
    container_name = 'app-container'

    if not check_server_status(url):
        if not restart_docker_container(container_name):
            reboot_server()
            send_email_notification('Server Rebooted', f'The server at {url} was rebooted due to failure.')
        else:
            send_email_notification('Docker Container Restarted', f'The Docker container {container_name} was restarted.')

# Schedule the monitoring task to run every 5 minutes
every(5).minutes.do(monitor_and_recover_server)

while True:
    run_pending()
    time.sleep(1)
```

This script checks the server's status every 5 minutes and attempts to restart the Docker container if the server is down. If the container fails to restart, it reboots the server and sends an email notification.

**Q5. Discuss the benefits of documenting and storing your Python automation scripts.**

Documenting and storing your Python automation scripts offers several benefits:

1. **Reusability**: Well-documented scripts can be reused in future projects, saving time and effort.
2. **Collaboration**: Documentation helps other team members understand and utilize the scripts, fostering collaboration and knowledge sharing.
3. **Maintenance**: Detailed documentation makes it easier to maintain and update the scripts over time, reducing the risk of errors and inconsistencies.
4. **Training**: Documented scripts serve as training materials for new team members, helping them quickly understand the existing automation processes.
5. **Troubleshooting**: Clear documentation aids in troubleshooting issues by providing context and instructions on how the scripts should behave.

By maintaining a repository of well-documented scripts, you ensure that your team has a reliable and efficient way to handle repetitive tasks, leading to increased productivity and reduced operational overhead.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/03-Python & Scripting/13-Python Automation for DevOps Use Cases/07-Conclusion|Conclusion]] | [[DevOps/DevOps Bootcamp/03-Python & Scripting/13-Python Automation for DevOps Use Cases/00-Overview|Overview]]
