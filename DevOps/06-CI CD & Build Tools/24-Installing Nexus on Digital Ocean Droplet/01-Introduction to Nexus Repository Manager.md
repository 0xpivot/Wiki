---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Nexus Repository Manager

The Nexus Repository Manager is a powerful artifact management solution used extensively in software development environments. It provides a centralized repository for storing and managing various types of artifacts such as Maven, npm, Docker, and more. Before diving into the installation process, it’s crucial to understand the prerequisites and the environment setup required for Nexus to function optimally.

### Prerequisites for Nexus Installation

One of the primary prerequisites for installing Nexus is having Java version 8 installed on the server. This is because Nexus is built on Java and specifically requires version 8 to ensure compatibility and stability. Let’s delve deeper into why this specific version is necessary and how it impacts the overall performance of Nexus.

#### Why Java Version 8?

Java version 8, also known as Java SE 8, was released in March 2014 and introduced several significant features and improvements. These enhancements include lambda expressions, new Date-Time API, and improved support for functional programming. However, the most critical aspect for Nexus is the stability and maturity of this version. Java 8 has been widely adopted and tested across various applications, making it a reliable choice for enterprise-level solutions like Nexus.

#### Memory Requirements

Another crucial factor to consider is the memory requirements for Nexus. Nexus is designed to handle large volumes of data and manage numerous artifacts efficiently. Therefore, it necessitates a server with sufficient memory capacity. In the context of this installation, we will be using a DigitalOcean droplet with 8 GB of RAM. This ensures that Nexus has ample resources to operate smoothly without running into memory constraints.

### Setting Up the DigitalOcean Droplet

To set up the DigitalOcean droplet, follow these steps:

1. **Choose the Droplet Size**: Navigate to the DigitalOcean dashboard and select the "Create Droplet" option. Choose the Ubuntu operating system and the "Basic Plan." Select the droplet size that offers 8 GB of RAM. This choice is essential to meet the memory requirements for Nexus.

2. **Configure Firewall Rules**: Once the droplet is created, configure the firewall rules to allow access on port 22 (SSH). This step is crucial for remotely accessing the droplet via SSH.

3. **Install Java Version 8**: Ensure that Java version 8 is installed on the droplet. This can be done using the following commands:

```bash
sudo apt update
sudo apt install openjdk-8-jdk
```

### Installing Nexus on the Droplet

With the prerequisites in place, we can proceed to install Nexus on the DigitalOcean droplet. The installation process involves downloading the Nexus package and configuring it to start automatically upon boot.

#### Downloading and Installing Nexus

1. **Download Nexus Package**:
   - Visit the Sonatype Nexus Repository Manager download page and download the latest version compatible with Java 8.
   - Transfer the downloaded package to the droplet using SCP or FTP.

2. **Extract and Install Nexus**:
   - Extract the downloaded package using the following command:

```bash
tar xvf nexus-<version>-unix.tar.gz
```

   - Move the extracted directory to `/opt/nexus`:

```bash
sudo mv nexus-<version> /opt/nexus
```

3. **Configure Nexus Service**:
   - Create a systemd service file for Nexus to ensure it starts automatically upon boot. Create a file named `nexus.service` in `/etc/systemd/system/` with the following content:

```ini
[Unit]
Description=Nexus service
After=network.target

[Service]
Type=forking
ExecStart=/opt/nexus/bin/nexus start
ExecStop=/opt/nexus/bin/nexus stop
User=nexus
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

   - Reload the systemd daemon and enable the Nexus service:

```bash
sudo systemctl daemon-reload
sudo systemctl enable nexus
```

4. **Start Nexus Service**:
   - Start the Nexus service using the following command:

```bash
sudo systemctl start nexus
```

### Verifying the Installation

Once the installation is complete, verify that Nexus is running correctly by accessing it through a web browser. Open a web browser and navigate to `http://<droplet-ip>:8081`. You should see the Nexus login screen, indicating that the installation was successful.

### Common Pitfalls and How to Prevent Them

#### Insufficient Memory Allocation

**Problem**: One common issue is insufficient memory allocation, leading to Nexus running out of memory and crashing.

**Prevention**:
- Ensure that the server has at least 8 GB of RAM.
- Monitor the memory usage of Nexus and adjust the heap size settings if necessary.

#### Incorrect Java Version

**Problem**: Using an incorrect version of Java can cause compatibility issues and prevent Nexus from starting.

**Prevention**:
- Always verify that Java version 8 is installed and configured correctly.
- Check the Java version using the command `java -version`.

### Secure Configuration and Hardening

#### Securing Nexus

**Detection**:
- Regularly monitor the Nexus logs for any unauthorized access attempts.
- Use tools like Sonatype Nexus Lifecycle to scan for vulnerabilities in hosted artifacts.

**Prevention**:
- Configure strong authentication mechanisms such as LDAP or Active Directory integration.
- Enable SSL/TLS encryption for all communications to the Nexus server.

#### Example of Vulnerable vs. Secure Configuration

**Vulnerable Configuration**:
```json
{
  "repositories": [
    {
      "name": "public",
      "type": "hosted",
      "format": "maven2",
      "security": {
        "enabled": false
      }
    }
  ]
}
```

**Secure Configuration**:
```json
{
  "repositories": [
    {
      "name": "public",
      "type": "hosted",
      "format": "maven2",
      "security": {
        "enabled": true,
        "authenticators": ["ldap"],
        "permissions": {
          "anonymous": ["read"],
          "authenticated": ["read", "write"]
        }
      }
    }
  ]
}
```

### Real-World Examples and Recent Breaches

#### Example: CVE-2019-10229

In 2019, a critical vulnerability (CVE-2019-10229) was discovered in Nexus Repository Manager 3.x versions prior to 3.16.1. This vulnerability allowed attackers to execute arbitrary code on the server by exploiting a deserialization flaw in the REST API.

**Impact**: This vulnerability could lead to complete compromise of the server hosting Nexus.

**Mitigation**:
- Ensure that Nexus is updated to the latest version.
- Regularly apply security patches and updates.

### Hands-On Labs

For practical experience in setting up and securing Nexus, consider the following labs:

- **PortSwigger Web Security Academy**: Offers detailed walkthroughs on securing web applications, including Nexus.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing security techniques.
- **DigitalOcean Tutorials**: Follow the official DigitalOcean tutorials for setting up and securing Nexus on a droplet.

By following these steps and best practices, you can successfully install and secure Nexus on a DigitalOcean droplet, ensuring optimal performance and robust security.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/24-Installing Nexus on Digital Ocean Droplet/00-Overview|Overview]] | [[02-Configuring Nexus to Run as the Nexus User|Configuring Nexus to Run as the Nexus User]]
