---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. How do you build a Java application using Gradle and deploy it to a remote server?**

To build a Java application using Gradle and deploy it to a remote server, follow these steps:

1. Clone the repository containing the Java application source code.
2. Navigate to the root directory of the project.
3. Execute the `gradle build` command to compile the Java code and create a JAR file.
4. Use the `scp` command to securely copy the JAR file to the remote server. For example:
   ```bash
   scp /path/to/local/jarfile.jar root@remote-server-ip:/root/
   ```
5. SSH into the remote server and run the JAR file using the `java -jar` command:
   ```bash
   java -jar /root/jarfile.jar
   ```

**Q2. What steps are required to make a Java application accessible via a web browser after deployment?**

To make a Java application accessible via a web browser after deployment, you need to:

1. Ensure the Java application is listening on a specific port (e.g., 7071).
2. Open the necessary port on the server's firewall. For instance, if using DigitalOcean, you would:
   - Go to the firewall settings.
   - Add a new rule to allow traffic on the specified port (custom TCP rule).
3. Access the application through a web browser by navigating to `http://<public-ip>:<port>`.

**Q3. Explain how to ensure a Java application continues to run even after closing the terminal session.**

To ensure a Java application continues to run even after closing the terminal session, you can use a process manager like `nohup`, `screen`, or `tmux`. Here’s how to use `nohup`:

1. Run the Java application with `nohup`:
   ```bash
   nohup java -jar /root/jarfile.jar &
   ```
2. Redirect the output to a log file:
   ```bash
   nohup java -jar /root/jarfile.jar > /root/app.log 2>&1 &
   ```
This ensures the application runs in the background and continues even after the terminal session is closed.

**Q4. How can you verify that a Java application is running on a remote server and determine its listening port?**

To verify that a Java application is running on a remote server and determine its listening port, you can use the following commands:

1. Check the running processes using `ps`:
   ```bash
   ps aux | grep java
   ```
2. Identify the process ID (PID) of the Java application.
3. Use `netstat` to find the listening port:
   ```bash
   sudo netstat -ltnp | grep <PID>
   ```
Alternatively, if `netstat` is not installed, you can install it using:
```bash
sudo apt-get install net-tools
```
Then repeat the `netstat` command to find the port.

**Q5. Describe a recent real-world example where a misconfigured firewall led to security issues in a deployed application.**

A notable example is the data breach at Capital One in 2019 (CVE-2019-11510). The attacker exploited a misconfigured firewall rule that allowed unauthorized access to sensitive customer data. The firewall rule was incorrectly set, allowing access to an internal web application that processed credit card applications. This incident highlights the importance of properly configuring firewall rules to prevent unauthorized access to critical services.

In the context of deploying a Java application, ensuring that firewall rules are correctly configured to only allow necessary ports and traffic is crucial to maintaining the security of the application.

---
<!-- nav -->
[[02-Deploying a Java Application to a Remote Server|Deploying a Java Application to a Remote Server]] | [[DevOps/DevOps Bootcamp/11-Miscellaneous/06-Deploying Java Application to Remote Server/00-Overview|Overview]]
