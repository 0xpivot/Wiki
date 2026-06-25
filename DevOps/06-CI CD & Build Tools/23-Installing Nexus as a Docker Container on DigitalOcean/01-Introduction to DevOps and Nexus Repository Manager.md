---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to DevOps and Nexus Repository Manager

In the realm of DevOps, managing artifacts such as binaries, libraries, and dependencies is crucial for maintaining a smooth and efficient development process. One of the most popular tools for this purpose is the Nexus Repository Manager, which provides a centralized repository for storing and managing these artifacts. This chapter will guide you through the process of installing Nexus as a Docker container on a DigitalOcean droplet, covering every aspect from setting up the environment to configuring the necessary components.

### Prerequisites

Before diving into the installation process, ensure you have the following:

1. **DigitalOcean Account**: You need an active account on DigitalOcean to create and manage droplets.
2. **Droplet Setup**: A droplet with a Linux distribution (e.g., Ubuntu) and a firewall configured to allow SSH access on port 22.
3. **Basic Linux Knowledge**: Familiarity with basic Linux commands and concepts such as SSH, package management, and networking.

### Accessing the Droplet via SSH

To begin, you need to access your droplet via SSH. Open your terminal and execute the following command:

```sh
ssh root@your_droplet_ip
```

Replace `your_droplet_ip` with the actual IP address of your droplet. Upon successful connection, you should see the shell prompt of your droplet.

### Installing Docker

Since we are deploying Nexus as a Docker container, the first step is to install Docker on the droplet. Docker is a platform that allows you to build, ship, and run applications inside lightweight containers.

#### Updating Package Manager

Before installing Docker, it's essential to update the package manager to ensure you get the latest versions of packages.

```sh
sudo apt-get update
```

This command updates the list of available packages and their versions, but it does not install or upgrade any packages.

#### Installing Docker

Next, install Docker using the following command:

```sh
sudo apt-get install -y docker.io
```

This command installs the latest version of Docker available in the package repository. After installation, verify that Docker is running by checking its status:

```sh
sudo systemctl status docker
```

If Docker is running correctly, you should see output indicating that the service is active.

### Finding the Nexus Official Image

With Docker installed, the next step is to find the official Nexus image on Docker Hub. Docker Hub is a public registry where developers can store and share Docker images.

#### Searching for Nexus Image

Open your browser and navigate to [Docker Hub](https://hub.docker.com/). Search for "Nexus 3" and locate the official image provided by Sonatype. The image name is typically `sonatype/nexus3`.

#### Reviewing Documentation

Before proceeding with the installation, review the documentation for the Nexus image. This documentation provides important details such as required ports, environment variables, and volume configurations.

### Configuring Storage for Nexus

One of the critical aspects of running Nexus as a Docker container is ensuring that the data persists even if the container is restarted or recreated. This is achieved by mounting a volume from the host system to the container.

#### Understanding Volumes

A Docker volume is a persistent storage area that exists outside the lifecycle of a container. By default, data stored within a container is lost when the container is removed. However, by mounting a volume, you can ensure that the data remains on the host system.

#### Creating a Volume

To create a volume, use the following command:

```sh
sudo mkdir -p /var/lib/nexus-data
```

This command creates a directory `/var/lib/nexus-data` on the host system where Nexus data will be stored.

### Running Nexus as a Docker Container

Now that the environment is set up and the volume is created, you can proceed to run the Nexus container.

#### Running the Container

Use the following command to run the Nexus container:

```sh
docker run -d -p 8081:8081 -p 8082:8082 -v /var/lib/nexus-data:/nexus-data sonatype/nexus3
```

Let's break down the command:

- `-d`: Run the container in detached mode (in the background).
- `-p 8081:8081`: Map port 8081 on the host to port 8081 on the container.
- `-p 8 8082:8082`: Map port 8082 on the host to port  8082 on the container.
- `-v /var/lib/nexus-data:/nexus-data`: Mount the host directory `/var/lib/nexus-data` to the container directory `/nexus-data`.
- `sonatype/nexus3`: The official Nexus 3 image from Docker Hub.

### Verifying the Installation

After running the container, verify that Nexus is accessible by navigating to `http://your_droplet_ip:8081` in your web browser. You should see the Nexus login page.

### Security Considerations

While setting up Nexus, it's crucial to consider security measures to protect your artifacts and infrastructure.

#### Securing SSH Access

Ensure that SSH access to your droplet is secure by:

- Using strong passwords or SSH keys.
- Disabling root login via SSH.
- Limiting SSH access to specific IP addresses.

#### Securing Docker

Secure Docker by:

- Using TLS encryption for Docker communication.
- Restricting Docker daemon access to trusted users.

#### Securing Nexus

Secure Nexus by:

- Enforcing strong authentication mechanisms.
- Configuring access controls and permissions.
- Regularly updating Nexus to the latest version.

### How to Prevent / Defend

#### Detecting Vulnerabilities

Regularly scan your Docker images and containers for vulnerabilities using tools like Trivy or Clair.

#### Preventing Attacks

- Use network segmentation to isolate sensitive services.
- Implement firewalls and security groups to restrict access.
- Enable logging and monitoring to detect and respond to suspicious activities.

#### Secure Coding Practices

- Follow secure coding guidelines when developing applications.
- Use automated tools to identify and fix security issues.

### Conclusion

By following this comprehensive guide, you have successfully installed Nexus as a Docker container on a DigitalOcean droplet. This setup provides a robust and scalable solution for managing artifacts in your DevOps pipeline. Remember to regularly maintain and secure your environment to ensure optimal performance and security.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Focuses on web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for learning security concepts.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for security training.
- **WebGoat**: An interactive, gamified training application for learning web security.

These labs provide practical experience in various aspects of DevOps and security, helping you to apply the concepts learned in this chapter effectively.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/23-Installing Nexus as a Docker Container on DigitalOcean/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/23-Installing Nexus as a Docker Container on DigitalOcean/02-Introduction to Nexus Repository Manager|Introduction to Nexus Repository Manager]]
