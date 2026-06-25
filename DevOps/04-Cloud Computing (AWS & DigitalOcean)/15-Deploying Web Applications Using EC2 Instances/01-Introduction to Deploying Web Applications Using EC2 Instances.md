---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Deploying Web Applications Using EC2 Instances

Deploying web applications using Amazon EC2 instances is a fundamental task in DevOps. This process involves setting up an environment where your application can run reliably and securely. In this section, we will cover the steps involved in deploying a web application on an EC2 instance, including updating the package manager, installing Docker, starting the Docker daemon, and configuring user permissions.

### Updating the Package Manager

When you create a new EC2 instance and SSH into it, the first step is to ensure that the package manager is up to date. This is crucial because the package manager needs to have the most recent information about the available packages and their versions. Without this update, the package manager might not be able to fetch or install the necessary tools correctly.

#### Why Update the Package Manager?

Updating the package manager ensures that you have access to the latest versions of software packages. This is important for several reasons:

1. **Security**: Newer versions often contain security patches that address vulnerabilities found in older versions.
2. **Functionality**: Newer versions may include new features or improvements that are not present in older versions.
3. **Compatibility**: Some software dependencies might require newer versions of certain packages to function correctly.

#### How to Update the Package Manager

The specific command to update the package manager depends on the Linux distribution you are using. For Ubuntu and Debian-based systems, the command is `apt-get update`. For Red Hat and CentOS-based systems, the command is `yum update`.

```bash
sudo apt-get update
```

or

```bash
sudo yum update
```

#### Example: Updating the Package Manager

Let's assume you are using an Ubuntu-based system. Here is how you would update the package manager:

```bash
sudo apt-get update
```

This command will download the package lists from the repositories and update them. You should see output similar to the following:

```plaintext
Hit:1 http://archive.ubuntu.com/ubuntu focal InRelease
Get:2 http://security.ubuntu.com/ubuntu focal-security InRelease [114 kB]
Get:3 http://archive.ubuntu.com/ubuntu focal-updates InRelease [114 kB]
Get:4 http://archive.ubuntu.com/ubuntu focal-backports InRelease [108 kB]
Fetched 336 kB in 1s (336 kB/s)
Reading package lists... Done
```

### Installing Docker

Once the package manager is up to date, the next step is to install Docker. Docker is a platform that allows you to build, ship, and run distributed applications inside lightweight containers. Containers are isolated environments that contain all the necessary components to run an application, including libraries, dependencies, and configuration files.

#### Why Install Docker?

Docker provides several benefits for deploying web applications:

1. **Isolation**: Each container runs in isolation, which helps prevent conflicts between different applications.
2. **Portability**: Docker containers can run consistently across different environments, from development to production.
3. **Efficiency**: Containers are more lightweight than virtual machines, making them more efficient in terms of resource usage.

#### How to Install Docker

To install Docker on an Ubuntu-based system, you can use the following commands:

```bash
sudo apt-get install docker.io
```

This command will download and install the latest version of Docker from the repository. After installation, you can verify the version of Docker installed:

```bash
docker --version
```

You should see output similar to the following:

```plaintext
Docker version 19.03.12, build 48a66213fe
```

### Starting the Docker Daemon

After installing Docker, you need to start the Docker daemon. The Docker daemon is responsible for managing Docker containers and images. Without starting the daemon, you won't be able to pull images, run containers, or perform other Docker-related tasks.

#### Why Start the Docker Daemon?

Starting the Docker daemon is necessary because it initializes the Docker runtime environment. The daemon listens for Docker API requests and manages the lifecycle of Docker containers.

#### How to Start the Docker Daemon

To start the Docker daemon, you can use the following command:

```bash
sudo systemctl start docker
```

Alternatively, you can use the `service` command:

```bash
sudo service docker start
```

You can verify that the Docker daemon is running by checking the status:

```bash
sudo systemctl status docker
```

or

```bash
sudo service docker status
```

You should see output similar to the following:

```plaintext
● docker.service - Docker Application Container Engine
   Loaded: loaded (/lib/systemd/system/docker.service; enabled; vendor preset: enabled)
   Active: active (running) since Mon 2023-01-01 12:00:00 UTC; 1h ago
     Docs: https://docs.docker.com
 Main PID: 1234 (dockerd)
    Tasks: 10 (limit: 4915)
   Memory: 100.0M
   CGroup: /system.slice/docker.service
           └─1234 /usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock
```

### Configuring User Permissions

By default, you need to use `sudo` to run Docker commands. However, it is often more convenient to be able to run Docker commands without `sudo`. To achieve this, you need to add the current user to the `docker` group.

#### Why Configure User Permissions?

Adding the user to the `docker` group allows you to run Docker commands without needing `sudo`. This is particularly useful in development environments where you frequently interact with Docker.

#### How to Configure User Permissions

To add the current user to the `docker` group, you can use the following command:

```bash
sudo usermod -aG docker $USER
```

After running this command, you need to log out and log back in for the changes to take effect. Alternatively, you can use the following command to reload the group membership:

```bash
newgrp docker
```

You can verify that the user is added to the `docker` group by checking the group membership:

```bash
groups $USER
```

You should see output similar to the following:

```plaintext
username : username adm cdrom sudo dip plugdev lpadmin lxd sambashare docker
```

### Summary

In this section, we covered the steps involved in deploying a web application on an EC2 instance, including updating the package manager, installing Docker, starting the Docker daemon, and configuring user permissions. These steps are essential for setting up a reliable and secure environment for your web application.

### Real-World Examples

#### CVE-2021-21285: Docker API Unauthorized Access

In 2021, a critical vulnerability was discovered in Docker, identified as CVE-2021-21285. This vulnerability allowed unauthorized access to the Docker API, potentially leading to remote code execution. The vulnerability was due to a misconfiguration in the Docker daemon, which allowed unauthenticated access to the API.

**Impact**: An attacker could exploit this vulnerability to gain full control over the Docker daemon, allowing them to run arbitrary commands on the host system.

**Mitigation**: To prevent this vulnerability, ensure that the Docker daemon is properly configured to restrict access to the API. This can be done by setting appropriate firewall rules and enabling authentication mechanisms.

```yaml
# Example Docker daemon configuration to restrict API access
{
  "hosts": ["unix:///var/run/docker.sock"],
  "tls": true,
  "tlscacert": "/path/to/ca.pem",
  1. "tlscert": "/path/to/server-cert.pem",
  2. "tlskey": "/path/to/server-key.pem"
}
```

### Conclusion

Deploying web applications using EC2 instances involves several key steps, including updating the package manager, installing Docker, starting the Docker daemon, and configuring user permissions. By following these steps, you can set up a reliable and secure environment for your web application. Always ensure that your environment is properly configured to prevent potential security vulnerabilities.

### Practice Labs

For hands-on practice with deploying web applications using EC2 instances, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on web application security, including deployment scenarios.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for learning web security.

These labs provide practical experience in deploying and securing web applications, helping you master the concepts covered in this chapter.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/04-Cloud Computing (AWS & DigitalOcean)/15-Deploying Web Applications Using EC2 Instances/00-Overview|Overview]] | [[02-Introduction to EC2 Instances|Introduction to EC2 Instances]]
