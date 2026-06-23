---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Why is it important to choose a droplet with sufficient memory capacity when installing Nexus?**

The choice of a droplet with sufficient memory capacity is crucial when installing Nexus because Nexus requires a significant amount of memory to operate efficiently. Insufficient memory can lead to performance degradation, frequent crashes, and issues with storing and managing components. By selecting a droplet with 8GB of memory, you ensure that Nexus has enough resources to handle its operations without running out of storage or causing other resource-related problems. This setup also mimics a production environment, ensuring that the server can manage the load effectively.

**Q2. What are the prerequisites for installing Nexus on a Digital Ocean droplet?**

To install Nexus on a Digital Ocean droplet, the following prerequisites must be met:

1. **Operating System**: Ensure that the droplet is running an appropriate operating system, such as Ubuntu.
2. **Memory Capacity**: The droplet should have sufficient memory, typically 8GB or more, to support Nexus operations.
3. **Java Version**: Nexus requires Java version 8 to be installed on the droplet. This ensures compatibility with the Nexus application.

**Q3. Explain the significance of the `nexus` and `sonatype-work` directories after installing Nexus.**

After installing Nexus, the `nexus` and `sonatype-work` directories serve distinct purposes:

- **`nexus` Directory**: Contains the runtime and application binaries of Nexus. This includes the executable files needed to start and run the Nexus service.
  
- **`sonatype-work/nexus` Directory**: Stores the configuration settings, data, and logs for Nexus. This directory holds all the custom configurations, repository data, plugin installations, and logs related to the Nexus application. Backing up this directory ensures that all Nexus data and configurations can be restored in case of any issues.

**Q4. How do you secure the Nexus installation by creating a dedicated user?**

To secure the Nexus installation, follow these steps to create a dedicated user:

1. **Create User**: Use the `useradd` command to create a new user specifically for Nexus. For example:
   ```bash
   sudo useradd -m nexus
   ```
   
2. **Set Password**: Set a password for the new user using the `passwd` command:
   ```bash
   sudo passwd nexus
   ```

3. **Change Ownership**: Change the ownership of the `nexus` and `sonatype-work` directories to the new user:
   ```bash
   sudo chown -R nexus:nexus /opt/nexus
   sudo chown -R nexus:nexus /opt/sonatype-work
   ```

4. **Configure Nexus RC File**: Edit the `nexus.rc` file to specify the user under which the Nexus service should run:
   ```bash
   sudo nano /opt/nexus/nexus.rc
   ```
   Add or uncomment the following line:
   ```bash
   RUN_AS_USER=nexus
   ```

5. **Start Nexus Service**: Switch to the `nexus` user and start the Nexus service:
   ```bash
   su - nexus
   /opt/nexus/bin/nexus start
   ```

By following these steps, you ensure that the Nexus service runs with minimal privileges, enhancing the security of the installation.

**Q5. How do you configure the firewall to allow access to the Nexus service?**

To configure the firewall to allow access to the Nexus service, follow these steps:

1. **Identify Required Ports**: Determine the ports required for Nexus. Typically, Nexus uses Port 8081 for HTTP access.

2. **Add Firewall Rule**: Add a custom TCP rule to the firewall to allow inbound connections on Port 8081. For example, using Digital Ocean's firewall rules:
   - Go to the Digital Ocean control panel.
   - Navigate to the "Firewalls" section.
   - Select the firewall associated with your droplet.
   - Add a new rule to allow inbound traffic on Port 8081.

3. **Verify Access**: Once the rule is added, verify that you can access the Nexus UI by navigating to `http://<droplet-ip>:8081` in a web browser.

By configuring the firewall correctly, you ensure that the Nexus service is accessible externally while maintaining security by limiting unnecessary inbound traffic.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/24-Installing Nexus on Digital Ocean Droplet/08-Conclusion|Conclusion]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/24-Installing Nexus on Digital Ocean Droplet/00-Overview|Overview]]
