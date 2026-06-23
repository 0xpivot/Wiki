---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the process of creating a droplet on DigitalOcean, including the steps involved in setting up the server and configuring SSH access.**

The process of creating a droplet on DigitalOcean involves several steps:

1. **Create a DigitalOcean Account**: Sign up for a DigitalOcean account, which often comes with a free tier or initial credits.
   
2. **Select the Droplet Configuration**: Click on "Create Droplet" and select the desired operating system (e.g., Ubuntu). Choose the plan that provides the necessary resources (CPU, RAM, storage).

3. **Choose Region**: Select a region that is geographically close to your location to minimize latency.

4. **Configure Authentication**: Set up authentication methods. For security reasons, it is recommended to use SSH keys instead of a root password. Generate an SSH key pair on your local machine and upload the public key to DigitalOcean.

5. **Review and Create Droplet**: Review the configuration settings and click "Create Droplet". The droplet will start provisioning and become available shortly.

6. **Access the Droplet**: Once the droplet is active, you can SSH into it using the public IP address and the SSH key configured earlier. Use the following command:
   ```bash
   ssh root@<public_ip_address>
   ```

**Q2. How would you configure a firewall to allow SSH access to your droplet from your local machine?**

To configure a firewall to allow SSH access to your droplet from your local machine, follow these steps:

1. **Identify Your Local Machine’s IP Address**: Determine the public IP address of your local machine. This can be done via online services like `whatismyip.com` or using the terminal command `curl ifconfig.me`.

2. **Create a Firewall Rule**: Go to the DigitalOcean Networking tab and create a new firewall rule. Name it appropriately (e.g., "my_droplet_firewall").

3. **Set Up Inbound Rules**: Add an inbound rule to allow traffic on port 22 (SSH) from your local machine’s IP address. Ensure that the source IP is correctly specified.

4. **Assign Firewall to Droplet**: Assign the newly created firewall to your droplet. Navigate to the droplets tab, select your droplet, and assign the firewall rule.

5. **Verify Connectivity**: Test connectivity by attempting to SSH into the droplet from your local machine.

**Q3. Why is it recommended to use SSH keys over a root password for accessing a droplet? Provide an explanation and recent real-world examples.**

Using SSH keys over a root password is recommended due to enhanced security. SSH keys provide a more secure method of authentication compared to passwords, which can be vulnerable to brute-force attacks and phishing attempts.

Recent real-world examples include:

- **CVE-2021-20225**: This vulnerability affected the SSH daemon in OpenSSH, allowing attackers to bypass authentication mechanisms. Using SSH keys reduces the risk of such vulnerabilities impacting your setup.
  
- **SolarWinds Supply Chain Attack (2020)**: This attack involved the compromise of SolarWinds software, leading to unauthorized access to numerous organizations' networks. Strong authentication practices, such as using SSH keys, can mitigate the risk of such breaches.

By using SSH keys, you ensure that only authorized users with the private key can access the droplet, enhancing overall security.

**Q4. How would you install Java version 8 on an Ubuntu droplet? Provide the necessary commands.**

To install Java version 8 on an Ubuntu droplet, follow these steps:

1. **Update Package List**: Ensure your package list is up-to-date.
   ```bash
   sudo apt-get update
   ```

2. **Install Java 8**: Install the specific version of Java 8 required.
   ```bash
   sudo apt-get install openjdk-8-jdk
   ```

3. **Verify Installation**: Check the installed version of Java to confirm the installation.
   ```bash
   java -version
   ```

This will install OpenJDK version 8, which is compatible with many applications requiring a specific version of Java.

**Q5. What are the benefits of starting with a clean slate on a new droplet?**

Starting with a clean slate on a new droplet offers several benefits:

1. **Control Over Environment**: You can install and configure exactly what you need, ensuring a consistent and controlled environment.
   
2. **Security**: A clean slate minimizes the risk of inheriting pre-installed software with known vulnerabilities.
   
3. **Optimization**: You can tailor the droplet’s configuration to meet specific performance requirements, optimizing resource usage.
   
4. **Ease of Management**: Managing a droplet with only the necessary components simplifies maintenance and troubleshooting.

By starting from a clean slate, you gain full control over the server’s configuration, ensuring it meets your specific needs while maintaining security and performance.

---
<!-- nav -->
[[04-Creating a Linux Droplet on DigitalOcean|Creating a Linux Droplet on DigitalOcean]] | [[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/12-Creating A Linux Droplet On DigitalOcean/00-Overview|Overview]]
