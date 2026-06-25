---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Jenkins Installation Using Docker on DigitalOcean

### Introduction to Jenkins and Docker

Jenkins is an open-source automation server that provides hundreds of plugins to support building, deploying, and automating any project. Docker, on the other hand, is a platform that allows developers to package applications into containers—standardized executable packages containing software and all of its dependencies—to ensure that the software works seamlessly in any environment.

In this section, we will cover how to install Jenkins using Docker on DigitalOcean. This setup is particularly useful for continuous integration and continuous deployment (CI/CD) pipelines, where Jenkins can automate the testing and deployment processes.

### Setting Up Jenkins Using Docker

To set up Jenkins using Docker, we need to understand a few key concepts:

1. **Port Binding**: Jenkins runs on specific ports, and we need to bind these ports to our host machine.
2. **Running Containers in Background**: We need to ensure that the Jenkins container continues to run even after we close the terminal.
3. **Volume Mounting**: Jenkins stores a significant amount of data, including user configurations, job definitions, and plugin installations. We need to persist this data across container restarts.

#### Port Binding

Jenkins typically runs on two ports:
- **8080**: The default HTTP port for accessing the Jenkins web interface.
- **50000**: The default JNLP (Java Network Launch Protocol) port used for agent communication.

When setting up Jenkins in a Docker container, we need to bind these ports to our host machine. This ensures that we can access the Jenkins web interface and manage agents from our local machine.

```bash
docker run -p 8080:8080 -p 50000:50000 ...
```

Here, `-p 8080:8080` maps port 8080 on the host to port 8080 on the container, and `-p 50000:50000` maps port 50000 on the host to port 50000 on the container.

#### Running Containers in Background

To keep the Jenkins container running even after closing the terminal, we use the `--detach` (`-d`) flag. This flag tells Docker to run the container in the background.

```bash
docker run -d ...
```

This ensures that the container continues to run in the background, allowing us to interact with Jenkins through its web interface.

#### Volume Mounting

Jenkins stores a significant amount of data, including user configurations, job definitions, and plugin installations. To ensure that this data persists across container restarts, we need to mount a volume.

```bash
docker run -v /path/to/jenkins_home:/var/jenkins_home ...
```

Here, `/path/to/jenkins_home` is the directory on the host machine where Jenkins data will be stored, and `/var/jenkins_home` is the corresponding directory inside the container.

### Full Command Example

Putting it all together, the full command to run Jenkins in a Docker container on DigitalOcean would look like this:

```bash
docker run -p 8080:8080 -p 50000:50000 -v /path/to/jenkins_home:/var/jenkins_home -d jenkins/jenkins:lts
```

### Detailed Explanation of Each Component

1. **Port Binding**:
    - **8080**: The default HTTP port for accessing the Jenkins web interface.
    - **50000**: The default JNLP port used for agent communication.

2. **Running Containers in Background**:
    - `-d`: Runs the container in detached mode, ensuring it continues to run in the background.

3. **Volume Mounting**:
    - `-v /path/to/jenkins_home:/var/jenkins_home`: Mounts a volume to persist Jenkins data.

### Real-World Examples and Recent CVEs

#### Real-World Example: Jenkins Setup on DigitalOcean

Suppose we are setting up Jenkins on a DigitalOcean droplet. We would follow these steps:

1. **Create a Droplet**: Create a new droplet on DigitalOcean.
2. **Install Docker**: Install Docker on the droplet.
3. **Run Jenkins Container**: Run the Jenkins container using the command above.

#### Recent CVEs

One notable CVE related to Jenkins is **CVE-2019-1003000**, which affected Jenkins versions prior to 2.176.1. This vulnerability allowed attackers to execute arbitrary code on the Jenkins server. To mitigate such vulnerabilities, it is crucial to keep Jenkins and its plugins up-to-date.

### How to Prevent / Defend

#### Detection

To detect potential vulnerabilities in your Jenkins setup, you can use tools like:

- **Jenkins Security Scanner**: A tool that scans Jenkins instances for known vulnerabilities.
- **Trivy**: An open-source vulnerability scanner that can scan Docker images for known vulnerabilities.

#### Prevention

To prevent vulnerabilities and ensure the security of your Jenkins setup, follow these best practices:

1. **Keep Jenkins and Plugins Updated**: Regularly update Jenkins and its plugins to the latest versions.
2. **Use Secure Configurations**: Ensure that Jenkins is configured securely, including proper authentication and authorization mechanisms.
3. **Limit Access**: Restrict access to Jenkins to only authorized users and limit their permissions as much as possible.

#### Secure Coding Fixes

Here is an example of a vulnerable Jenkins configuration and its secure counterpart:

**Vulnerable Configuration**:
```yaml
# Jenkins Configuration as Code (JCasC)
jenkins:
  systemMessage: "Welcome to Jenkins!"
  securityRealm:
    local:
      allowsSignup: true
  authorizationStrategy:
    anyoneCanDoAnything: {}
```

**Secure Configuration**:
```yaml
# Jenkins Configuration as Code (JCasC)
jenkins:
  systemMessage: "Welcome to Jenkins!"
  securityRealm:
    local:
      allowsSignup: false
  authorizationStrategy:
    globalMatrix:
      permissions:
        - "hudson.model.Hudson.Administer:admin"
        - "hudson.model.Item.Build:authenticated"
        - "hudson.model.Item.Configure:authenticated"
        - "hudson.model.Item.Create:authenticated"
        - "hudson.model.Item.Delete:authenticated"
        - "hudson.model.Item.Read:anonymous"
```

### Complete Example

Let's walk through a complete example of setting up Jenkins on DigitalOcean using Docker.

#### Step 1: Create a Droplet

1. Log in to your DigitalOcean account.
2. Click on "Create" and select "Droplets".
3. Choose a plan and region.
4. Select an image (e.g., Ubuntu 20.04).
5. Add SSH keys for secure access.
6. Create the droplet.

#### Step 2: Install Docker

1. SSH into your droplet.
2. Update the package list:
    ```bash
    sudo apt-get update
    ```
3. Install Docker:
    ```bash
    sudo apt-get install -y docker.io
    ```

#### Step 3: Run Jenkins Container

1. Create a directory for Jenkins data:
    ```bash
    mkdir -p /path/to/jenkins_home
    ```
2. Run the Jenkins container:
    ```bash
    docker run -p 8080:8080 -p 50000:50000 -v /path/to/jenkins_home:/var/jenkins_home -d jenkins/jenkins:lts
    ```

#### Step 4: Access Jenkins

1. Open a web browser and navigate to `http://<your_droplet_ip>:8080`.
2. Follow the initial setup instructions to complete the installation.

### Diagrams

#### Docker Container Setup

```mermaid
graph LR
  A[DigitalOcean Droplet] --> B[Docker]
  B --> C[Jenkins Container]
  C --> D[Port 8080]
  C --> E[Port 50000]
  C --> F[Volume /var/jenkins_home]
  F --> G[/path/to/jenkins_home]
```

### Common Pitfalls

1. **Incorrect Port Binding**: Ensure that the correct ports are bound to avoid conflicts with other services.
2. **Volume Not Mounted**: Ensure that the volume is correctly mounted to persist Jenkins data.
3. **Outdated Jenkins Version**: Keep Jenkins and its plugins updated to avoid known vulnerabilities.

### Hands-On Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs to practice web security concepts.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for learning web security.

These labs provide practical experience in setting up and securing Jenkins environments.

### Conclusion

Setting up Jenkins using Docker on DigitalOcean is a powerful way to automate CI/CD pipelines. By understanding the key concepts of port binding, running containers in the background, and volume mounting, you can ensure a robust and secure Jenkins setup. Always keep Jenkins and its plugins updated, and use secure configurations to protect against vulnerabilities.

---
<!-- nav -->
[[02-Introduction to Jenkins and Its Role in DevOps|Introduction to Jenkins and Its Role in DevOps]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/27-Jenkins Installation Using Docker On DigitalOcean/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/27-Jenkins Installation Using Docker On DigitalOcean/04-Practice Questions & Answers|Practice Questions & Answers]]
