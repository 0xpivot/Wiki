---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain how you would use Python to monitor a website running on a Linode server.**

To monitor a website running on a Linode server using Python, you would follow these steps:

1. **Set Up the Server**: Create a Linode server and install Docker on it.
2. **Run the Application**: Use Docker to run an application (e.g., EngineX) on the server.
3. **Write the Python Script**: Use the `requests` library to send an HTTP GET request to the application's endpoint.
4. **Check the Response**: Analyze the HTTP response status code to determine if the application is running correctly.
5. **Notify and Fix**: If the application is not responding correctly, send an email notification and potentially restart the Docker container or the server itself.

Here’s a sample Python script to perform these actions:

```python
import requests
import smtplib

def check_website(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Website is up and running successfully.")
        else:
            print("Application down, fix it.")
            send_email_notification()
    except requests.exceptions.RequestException as e:
        print(f"Error accessing the website: {e}")
        send_email_notification()

def send_email_notification():
    sender_email = "your-email@example.com"
    receiver_email = "receiver-email@example.com"
    message = """\
    Subject: Website Down Notification

    The website is currently down. Please take necessary action."""
    
    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login(sender_email, 'your-password')
        server.sendmail(sender_email, receiver_email, message)

if __name__ == "__main__":
    url = "http://your-server-ip:8080"
    check_website(url)
```

This script checks the website's status and sends an email notification if the website is down.

**Q2. How would you extend the Python script to automatically restart the Docker container if the website is down?**

To extend the Python script to automatically restart the Docker container, you can include SSH commands to interact with the server and restart the container. Here’s how you can modify the script:

1. **Install Paramiko**: Use the `paramiko` library to handle SSH connections.
2. **Restart the Container**: Execute SSH commands to restart the Docker container.

Here’s an extended version of the script:

```python
import paramiko
import requests
import smtplib

def check_website(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("Website is up and running successfully.")
        else:
            print("Application down, fix it.")
            send_email_notification()
            restart_container()
    except requests.exceptions.RequestException as e:
        print(f"Error accessing the website: {e}")
        send_email_notification()
        restart_container()

def send_email_notification():
    sender_email = "your-email@example.com"
    receiver_email = "receiver-email@example.com"
    message = """\
    Subject: Website Down Notification

    The website is currently down. Please take necessary action."""
    
    with smtplib.SMTP('smtp.example.com', 587) as server:
        server.starttls()
        server.login(sender_email, 'your-password')
        server.sendmail(sender_email, receiver_email, message)

def restart_container():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect('your-server-ip', username='root', password='your-root-password')

    # Restart the Docker container
    stdin, stdout, stderr = ssh.exec_command('docker restart your-container-name')
    print(stdout.read().decode())
    ssh.close()

if __name__ == "__main__":
    url = "http://your-server-ip:8080"
    check_website(url)
```

In this script, the `restart_container` function uses `paramiko` to connect to the server via SSH and restart the Docker container.

**Q3. What recent real-world examples can you cite where website monitoring and automatic recovery were crucial?**

One notable example is the widespread outages experienced by several major websites during the 2021 New Year's Eve. For instance, Twitter, Facebook, and Instagram faced significant downtime due to infrastructure issues. These incidents highlighted the importance of robust monitoring and automatic recovery mechanisms.

Another example is the 2021 GitHub outage, where the service went down for several hours. While the exact cause was not publicly disclosed, such incidents underscore the necessity of having automated monitoring and recovery systems in place to minimize downtime and ensure service availability.

In both cases, having a Python-based monitoring system that could detect issues and automatically trigger recovery actions would have significantly reduced the impact of these outages.

**Q4. How would you configure the Python script to run periodically to ensure continuous monitoring of the website?**

To ensure continuous monitoring of the website, you can configure the Python script to run periodically using a task scheduler like `cron` on Unix-based systems or Task Scheduler on Windows.

Here’s how you can set up a cron job to run the script every 5 minutes:

1. **Edit the crontab file**: Open the crontab file by running `crontab -e`.
2. **Add a cron job**: Add the following line to the crontab file to run the script every 5 minutes:

```bash
*/5 * * * * /usr/bin/python3 /path/to/your/script.py
```

This cron job will execute the Python script every 5 minutes, ensuring continuous monitoring of the website.

**Q5. Explain how you would handle different types of errors that might occur while monitoring the website.**

When monitoring a website, various types of errors can occur, including network errors, HTTP errors, and connection timeouts. To handle these errors effectively, you can use exception handling in your Python script.

Here’s an example of how you can handle different types of errors:

```python
import requests

def check_website(url):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            print("Website is up and running successfully.")
        else:
            print(f"HTTP error: {response.status_code}")
            send_email_notification()
    except requests.exceptions.Timeout:
        print("The request timed out.")
        send_email_notification()
    except requests.exceptions.ConnectionError:
        print("Failed to establish a connection.")
        send_email_notification()
    except requests.exceptions.HTTPError as e:
        print(f"HTTP error occurred: {e}")
        send_email_notification()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        send_email_notification()

def send_email_notification():
    # Email notification logic here
    pass

if __name__ == "__main__":
    url = "http://your-server-ip:8080"
    check_website(url)
```

In this script, different exceptions are caught and handled appropriately, ensuring that the script can gracefully handle various types of errors and notify the appropriate parties.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/19-Python Automation for Website Monitoring/10-Conclusion|Conclusion]] | [[DevOps/DevOps Bootcamp/10-Monitoring & Alerting/19-Python Automation for Website Monitoring/00-Overview|Overview]]
