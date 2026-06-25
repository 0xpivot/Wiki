---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the process of using Python to automatically restart a Docker container on a remote server via SSH.**

To automatically restart a Docker container on a remote server using Python, follow these steps:

1. **Install the required library**: Use `pip` to install the `paramiko` library, which provides SSH functionality in Python.
   
   ```bash
   pip install paramiko
   ```

2. **Connect to the remote server**: Use the `SSHClient` class from `paramiko` to establish an SSH connection to the remote server. Provide the necessary details such as the server's IP address, username, and private key file.

   ```python
   import paramiko

   ssh = paramiko.SSHClient()
   ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
   ssh.connect('server_ip', username='username', key_filename='/path/to/private/key')
   ```

3. **Execute the Docker command**: Once connected, execute the Docker command to restart the container. For example, to restart a container with a specific ID:

   ```python
   stdin, stdout, stderr = ssh.exec_command('docker start container_id')
   print(stdout.read().decode())
   ```

4. **Close the SSH connection**: After executing the command, ensure to close the SSH connection to free up resources.

   ```python
   ssh.close()
   ```

**Q2. How would you handle the scenario where the server itself is unresponsive and needs to be restarted along with the Docker container?**

To handle a scenario where the server itself is unresponsive, you can use the `Linode API` to reboot the server and then restart the Docker container. Here’s how:

1. **Install the Linode API library**: Use `pip` to install the `linode_api4` library.

   ```bash
   pip install linode_api4
   ```

2. **Authenticate with the Linode API**: Create a Linode client using your API token.

   ```python
   from linode_api4 import LinodeClient

   client = LinodeClient('your_api_token')
   ```

3. **Reboot the server**: Identify the server instance and reboot it.

   ```python
   server = client.load(Linode, 'server_id')
   server.reboot()
   ```

4. **Wait for the server to become active**: Use a loop to wait until the server is in the running state before proceeding.

   ```python
   while True:
       server = client.load(Linode, 'server_id')
       if server.status == 'running':
           break
   ```

5. **Restart the Docker container**: Connect to the server via SSH and restart the Docker container as described in Q1.

6. **Notify the team**: Send an email or notification to inform the team that the server and application have been successfully restarted.

**Q3. What are the potential challenges when automating application recovery using Python SSH, and how can they be mitigated?**

Potential challenges include:

1. **Network latency and timeouts**: Ensure that your script handles network delays and timeouts gracefully. Use retries and appropriate timeouts when executing commands.

2. **Authentication issues**: Ensure that SSH keys and API tokens are correctly configured and stored securely. Avoid hardcoding sensitive information and use environment variables instead.

3. **Server unavailability**: Implement robust error handling and retry mechanisms to manage scenarios where the server is temporarily unavailable.

4. **Timing issues**: When restarting services, ensure that there is sufficient delay between actions to allow the system to stabilize. Use loops to check the status of services before proceeding.

Mitigation strategies include:

- **Use robust error handling**: Catch exceptions and handle errors gracefully.
- **Implement retries**: Retry failed operations with exponential backoff.
- **Use environment variables**: Store sensitive information like SSH keys and API tokens in environment variables.
- **Monitor and log**: Keep detailed logs of operations and monitor the system to detect and respond to failures promptly.

**Q4. How can you ensure that your automated recovery script is secure and does not expose sensitive information?**

To ensure security and prevent exposure of sensitive information:

1. **Use environment variables**: Store sensitive information like SSH keys and API tokens in environment variables rather than hardcoding them in the script.

2. **Secure key management**: Ensure that SSH keys and API tokens are stored securely and are not accessible to unauthorized users.

3. **Limit permissions**: Use least privilege principles to limit the permissions of the user accounts used for automation.

4. **Regular audits**: Regularly audit the script and configurations to identify and mitigate potential security vulnerabilities.

5. **Use secure communication protocols**: Ensure that all communications are encrypted using secure protocols like SSH and HTTPS.

**Q5. Explain how you would integrate a monitoring mechanism to periodically check the health of the application and trigger automatic recovery if needed.**

To integrate a monitoring mechanism:

1. **Create a monitoring function**: Define a function that checks the health of the application, such as by making HTTP requests to the application and verifying the response status.

2. **Use a scheduling library**: Use a scheduling library like `schedule` to periodically run the monitoring function.

   ```python
   import schedule
   import time

   def monitor_application():
       # Check application health and trigger recovery if needed
       pass

   schedule.every(5).minutes.do(monitor_application)

   while True:
       schedule.run_pending()
       time.sleep(1)
   ```

3. **Trigger automatic recovery**: Within the monitoring function, implement logic to trigger automatic recovery if the application is found to be unhealthy.

4. **Send notifications**: Optionally, send notifications to the team when the application is down and when it is recovered.

By integrating these components, you can ensure that your application is monitored continuously and automatically recovered when necessary.

---
<!-- nav -->
[[04-Automated Application Recovery Using Python SSH|Automated Application Recovery Using Python SSH]] | [[DevOps/DevOps Bootcamp/03-Python & Scripting/05-Automated Application Recovery Using Python SSH/00-Overview|Overview]]
