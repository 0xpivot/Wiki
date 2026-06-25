---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Nexus Repository Manager

The Nexus Repository Manager is a powerful artifact management solution that provides a centralized repository for storing and managing various types of artifacts such as Maven, npm, NuGet, and more. It simplifies the process of managing dependencies and ensures consistency across different environments. In this chapter, we will delve into the installation of Nexus Repository Manager as a Docker container on a DigitalOcean droplet. This approach offers several advantages, including ease of setup, portability, and scalability.

### Background Theory

Before diving into the practical steps, it’s essential to understand the underlying concepts:

#### What is Nexus Repository Manager?

Nexus Repository Manager is a software component designed to manage and distribute artifacts. Artifacts are files that are produced during the build process, such as JARs, WARs, and other binary files. Nexus Repository Manager provides a centralized location to store these artifacts, making them easily accessible to developers and build systems.

#### Why Use Nexus Repository Manager?

1. **Centralized Artifact Management**: Nexus Repository Manager allows you to centralize your artifact storage, ensuring that all team members are working with the same versions of dependencies.
2. **Improved Build Speed**: By caching frequently used artifacts, Nexus Repository Manager reduces the time required to fetch dependencies from remote repositories.
3. **Security and Compliance**: Nexus Repository Manager supports various security features, such as role-based access control, SSL/TLS encryption, and audit logging, which help ensure compliance with organizational policies and regulations.
4. **Scalability**: Nexus Repository Manager can handle large-scale deployments, supporting thousands of users and millions of artifacts.

#### How Does Nexus Repository Manager Work?

Nexus Repository Manager operates by providing a web interface and REST API for managing repositories. It supports multiple repository types, including hosted, proxy, and group repositories. Hosted repositories store artifacts directly, proxy repositories cache artifacts from remote repositories, and group repositories aggregate multiple repositories into a single logical repository.

### Prerequisites

To follow along with this chapter, you will need:

1. A DigitalOcean account.
2. Basic knowledge of Linux commands and Docker.
3. Access to a terminal or SSH client.

### Setting Up the DigitalOcean Droplet

Let's begin by setting up a new DigitalOcean droplet specifically for our Nexus Repository Manager installation.

#### Creating a New Droplet

1. **Log in to DigitalOcean**: Navigate to the DigitalOcean dashboard and log in to your account.
2. **Create a New Droplet**: Click on the "Create" button and select "Droplets."
3. **Choose the Plan**: Select a plan that meets your requirements. For this example, we will use a basic plan with 1GB of RAM and 1 vCPU.
4. **Select the Region**: Choose a region that is closest to your location or where your target audience is located.
5. **Configure Additional Settings**:
    - **Image**: Select a Linux distribution, such as Ubuntu 20.04 LTS.
    - **Size**: Choose the appropriate size based on your needs.
    - **Datacenter**: Select a datacenter within the chosen region.
    - **Authentication**: Choose SSH keys for authentication. If you don’t have any SSH keys, you can generate them using `ssh-keygen`.
    - **User Data**: Leave this blank unless you have specific scripts to run at boot time.
6. **Create the Droplet**: Review your settings and click "Create Droplet."

#### Connecting to the Droplet

Once the droplet is created, you can connect to it using SSH. The IP address of the droplet will be displayed in the DigitalOcean dashboard.

```sh
ssh root@<IP_ADDRESS>
```

Replace `<IP_ADDRESS>` with the actual IP address of your droplet.

### Configuring Firewall Rules

Before proceeding with the installation, it’s crucial to configure the firewall rules to allow necessary traffic.

#### Adding Firewall Rules

1. **Navigate to Firewall Configuration**: In the DigitalOcean dashboard, go to the "Firewalls" section.
2. **Create a New Firewall**: Click on "Create Firewall."
3. **Add Droplet**: Add the newly created droplet to the firewall.
4. **Configure Inbound Rules**:
    - **SSH (Port 22)**: Allow inbound traffic on port 22 to enable SSH connections.
    - **HTTP (Port 8081)**: Allow inbound traffic on port 8081, which is the default port for Nexus Repository Manager.
5. **Save the Firewall**: Review your settings and save the firewall.

### Installing Docker

To install Nexus Repository Manager as a Docker container, we first need to install Docker on the droplet.

#### Installing Docker

1. **Update Package Lists**:
    ```sh
    apt-get update
    ```

2. **Install Docker**:
    ```sh
    apt-get install -y docker.io
    ```

3. **Start Docker Service**:
    ```sh
    systemctl start docker
    ```

4. **Enable Docker to Start on Boot**:
    ```sh
    systemctl enable docker
    ```

5. **Verify Docker Installation**:
    ```sh
    docker --version
    ```

### Running Nexus Repository Manager as a Docker Container

Now that Docker is installed, we can proceed to run Nexus Repository Manager as a Docker container.

#### Pulling the Nexus Docker Image

1. **Pull the Nexus Docker Image**:
    ```sh
    docker pull sonatype/nexus3
    ```

2. **Run the Nexus Docker Container**:
    ```sh
    docker run -d -p 8081:8081 --name nexus sonatype/nexus3
    ```

This command does the following:
- `-d`: Runs the container in detached mode.
- `-p 8081:8081`: Maps port 8081 on the host to port 8081 on the container.
- `--name nexus`: Names the container as `nexus`.

#### Verifying the Installation

1. **Check the Running Containers**:
    ```sh
    docker ps
    ```

2. **Access Nexus Repository Manager**:
    Open a web browser and navigate to `http://<IP_ADDRESS>:8081`. You should see the Nexus Repository Manager login page.

### Security Considerations

While running Nexus Repository Manager as a Docker container simplifies the setup process, it is crucial to consider security best practices.

#### Securing the Docker Environment

1. **Use Non-root Users**: Avoid running Docker containers as the root user. Instead, create a non-root user and run the container with that user.
2. **Limit Network Exposure**: Restrict access to the container only from trusted networks.
3. **Regularly Update Docker**: Keep Docker and its components up to date to mitigate vulnerabilities.

#### Securing Nexus Repository Manager

1. **Enable SSL/TLS**: Configure Nexus Repository Manager to use SSL/TLS for secure communication.
2. **Role-Based Access Control**: Implement role-based access control to restrict access to sensitive repositories.
3. **Audit Logging**: Enable audit logging to track user activities and detect potential security incidents.

### Real-World Examples and Recent CVEs

#### Example: CVE-2021-21277

CVE-2021-21277 is a critical vulnerability in Sonatype Nexus Repository Manager 3.x that could allow an attacker to execute arbitrary code on the server. This vulnerability was due to improper validation of user input in the REST API.

**Impact**: An attacker could exploit this vulnerability to gain unauthorized access to the server and execute arbitrary code.

**Mitigation**: Ensure that you are running the latest version of Nexus Repository Manager and apply all security patches promptly.

### Complete Example: Full HTTP Request and Response

Here is a complete example of an HTTP request and response when accessing Nexus Repository Manager:

#### HTTP Request

```http
GET /service/rest/v1/status HTTP/1.1
Host: <IP_ADDRESS>:8081
Accept: application/json
Authorization: Basic <BASE64_ENCODED_CREDENTIALS>
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Mon, 01 Jan 2024 12:00:00 GMT
Content-Type: application/json;charset=UTF-8
Transfer-Encoding: chunked
Connection: keep-alive
Vary: Accept-Encoding
Cache-Control: no-cache, no-store, max-age=0, must-revalidate
Pragma: no-cache
Expires: 0
X-Frame-Options: SAMEORIGIN
X-XSS-Protection: 1; mode=block
X-Content-Type-Options: nosniff
Strict-Transport-Security: max-age=31536000 ; includeSubDomains
Content-Security-Policy: frame-ancestors 'self'

{
  "support": {
    "status": "OK",
    "message": "Nexus Repository Manager is running"
  },
  "repositories": {
    "count": 1,
    "items": [
      {
        "id": "maven-central",
        "name": "Maven Central",
        "type": "proxy",
        "format": "maven2",
        "online": true
      }
    ]
  }
}
```

### How to Prevent / Defend

#### Detection

1. **Monitor Logs**: Regularly review logs for suspicious activity.
2. **Use Security Tools**: Utilize tools like Sonatype Nexus IQ Server to scan for vulnerabilities in your artifacts.

#### Prevention

1. **Keep Software Updated**: Regularly update Nexus Repository Manager and all associated components.
2. **Implement Security Policies**: Enforce strict security policies, such as least privilege and network segmentation.

#### Secure Coding Fixes

Here is an example of a vulnerable configuration and its secure counterpart:

##### Vulnerable Configuration

```json
{
  "repositories": [
    {
      "id": "public",
      "name": "Public Repositories",
      "type": "group",
      "format": "maven2",
      "group": {
        "memberNames": ["maven-central", "maven-releases"]
      }
    }
  ]
}
```

##### Secure Configuration

```json
{
  "repositories": [
    {
      "id": "public",
      "name": "Public Repositories",
      "type": "group",
      "format": "maven2",
      "group": {
        "memberNames": ["maven-central", "maven-releases"],
        "strictContentValidation": true
      }
    }
  ]
}
```

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of web security challenges and labs.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.

These labs provide a safe environment to practice and reinforce the concepts covered in this chapter.

### Conclusion

In this chapter, we have explored the installation of Nexus Repository Manager as a Docker container on a DigitalOcean droplet. We covered the theoretical background, practical steps, and security considerations. By following these guidelines, you can effectively set up and manage Nexus Repository Manager in a secure and efficient manner.

---
<!-- nav -->
[[01-Introduction to DevOps and Nexus Repository Manager|Introduction to DevOps and Nexus Repository Manager]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/23-Installing Nexus as a Docker Container on DigitalOcean/00-Overview|Overview]] | [[03-Introduction to Nexus and Docker Containers|Introduction to Nexus and Docker Containers]]
