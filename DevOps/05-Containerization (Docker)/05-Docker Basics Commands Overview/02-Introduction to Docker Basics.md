---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Docker Basics

Docker is a platform that allows developers to package their applications into lightweight, portable containers. Containers encapsulate an application along with its dependencies, ensuring that the application runs consistently across different environments. This section will cover several fundamental Docker commands and concepts, including `docker pull`, `docker run`, `docker start`, `docker stop`, `docker ps`, and `docker images`.

### Docker Pull

The `docker pull` command is used to download Docker images from a registry, such as Docker Hub, to your local machine. These images contain the necessary files and configurations to run a specific application or service.

#### Syntax
```bash
docker pull <image_name>:<tag>
```

- **`<image_name>`**: The name of the Docker image you want to pull.
- **`<tag>`**: The tag specifies the version of the image. Common tags include `latest`, `stable`, etc.

#### Example
To pull the latest version of the official Nginx image from Docker Hub:
```bash
docker pull nginx:latest
```

#### Under the Hood
When you execute `docker pull`, Docker communicates with the registry to fetch the manifest of the requested image. The manifest contains metadata about the image layers. Docker then downloads these layers and stores them locally. If a layer already exists on your system, Docker skips downloading it, making the process more efficient.

#### Real-World Example
In a recent breach, attackers exploited a misconfigured Docker registry that allowed unauthorized access to sensitive images. This highlights the importance of securing your Docker registries and using proper authentication mechanisms.

#### How to Prevent / Defend
- **Secure Registries**: Ensure that your Docker registries are properly secured with TLS encryption and strong authentication mechanisms.
- **Access Control**: Implement role-based access control (RBAC) to restrict who can pull images from the registry.
- **Regular Audits**: Regularly audit your Docker registries to ensure that only authorized users have access.

### Docker Run

The `docker run` command is used to start a new container from an existing image. It combines the functionality of `docker pull` and `docker start` into a single command. If the specified image is not present locally, `docker run` will automatically pull it from the registry.

#### Syntax
```bash
docker run [OPTIONS] IMAGE [COMMAND] [ARG...]
```

- **`[OPTIONS]`**: Various options that can be passed to customize the behavior of the container.
- **`IMAGE`**: The name of the Docker image.
- **`[COMMAND]`**: An optional command to run inside the container.
- **`[ARG...]`**: Additional arguments to pass to the command.

#### Example
To start a new container from the Nginx image and run it in detached mode:
```bash
docker run -d nginx:latest
```

#### Under the Hood
When you run `docker run`, Docker first checks if the specified image is present locally. If not, it pulls the image from the registry. Once the image is available, Docker creates a new container based on the image and starts it. The `-d` flag runs the container in detached mode, allowing you to continue using the terminal.

#### Real-World Example
In a recent incident, an organization inadvertently exposed a Docker container running a vulnerable version of a web server. This led to a data breach. Properly configuring and securing your Docker containers is crucial to avoid such incidents.

#### How to Prevent / Defend
- **Use Secure Images**: Always use trusted and secure images from reputable sources.
- **Update Regularly**: Keep your Docker images up-to-date with the latest security patches.
- **Container Security Best Practices**: Follow best practices for securing Docker containers, such as using non-root users and limiting unnecessary privileges.

### Docker Start and Docker Stop

The `docker start` and `docker stop` commands are used to manage the lifecycle of Docker containers. `docker start` resumes a stopped container, while `docker stop` gracefully stops a running container.

#### Syntax
```bash
docker start CONTAINER
docker stop CONTAINER
```

- **`CONTAINER`**: The name or ID of the Docker container.

#### Example
To start a previously stopped container named `my_container`:
```bash
docker start my_container
```

To stop a running container named `my_container`:
```bash
docker stop my_container
```

#### Under the Hood
When you run `docker start`, Docker sends a signal to the container to resume its execution. Conversely, `docker stop` sends a SIGTERM signal to the container, allowing it to perform any necessary cleanup before shutting down.

#### Real-World Example
In a production environment, a container may need to be restarted due to updates or maintenance. Properly managing the lifecycle of containers ensures that services remain available and stable.

#### How to Prevent / Defend
- **Graceful Shutdown**: Ensure that your containers handle shutdown signals gracefully to avoid data loss or corruption.
- **Monitoring and Alerts**: Set up monitoring and alerting to detect and respond to unexpected container restarts or failures.

### Docker Run with Options

The `docker run` command supports various options to customize the behavior of the container. One commonly used option is `-d` (detach), which runs the container in the background.

#### Syntax
```bash
docker run -d [OPTIONS] IMAGE [COMMAND] [ARG...]
```

- **`-d`**: Runs the container in detached mode.
- **`[OPTIONS]`**: Other options to further customize the container.

#### Example
To start a new container from the Nginx image and run it in detached mode:
```bash
docker run -d nginx:latest
```

#### Under the Hood
When you run `docker run -d`, Docker starts the container in the background and returns control to the terminal immediately. This allows you `docker run -d` to run multiple containers simultaneously without blocking the terminal.

#### Real-World Example
In a microservices architecture, multiple containers often run concurrently. Using the `-d` option ensures that each container runs independently without interfering with others.

#### How to Prevent / Defend
- **Resource Management**: Monitor and manage resources to ensure that containers do not consume excessive CPU or memory.
- **Logging and Monitoring**: Implement logging and monitoring to track the health and performance of your containers.

### Docker PS

The `docker ps` command lists all running containers. The `-a` flag can be used to list all containers, regardless of their current state.

#### Syntax
```bash
docker ps [-a]
```

- **`-a`**: Lists all containers, including those that are not currently running.

#### Example
To list all running containers:
```bash
docker ps
```

To list all containers, including those that are not running:
```bash
docker ps -a
```

#### Under the Hood
When you run `docker ps`, Docker queries the local Docker daemon to retrieve information about the containers. The `-a` flag instructs Docker to include containers in all states, not just those that are currently running.

#### Real-World Example
In a development environment, it is common to have multiple containers running at once. Using `docker ps` helps you keep track of which containers are active and which ones are not.

#### How to Prevent / Defend
- **Regular Cleanup**: Periodically review and remove unused or inactive containers to free up resources.
- **Security Audits**: Regularly audit your container inventory to ensure that no unauthorized containers are running.

### Docker Images

The `docker images` command lists all Docker images that are available locally on your system.

#### Syntax
```bash
docker images
```

#### Example
To list all local Docker images:
```bash
docker images
```

#### Under the Hood
When you run `docker images`, Docker queries the local Docker daemon to retrieve a list of all images stored on your system. Each image is associated with a unique identifier (ID) and a set of tags.

#### Real-World Example
In a development workflow, it is common to have multiple versions of the same image. Using `docker images` helps you manage and organize your local image collection.

#### How to Prevent / Defend
- **Regular Cleanup**: Periodically review and remove unused or outdated images to free up disk space.
- **Image Security**: Ensure that all images are from trusted sources and are regularly updated with security patches.

### Cleaning Up Stale Images and Containers

Over time, it is common to accumulate stale Docker images and containers that are no longer needed. Cleaning up these resources helps maintain optimal performance and security.

#### Syntax
```bash
docker rmi <image_id>
docker rm <container_id>
```

- **`docker rmi`**: Removes a Docker image.
- **`docker rm`**: Removes a Docker container.

#### Example
To remove a stale image with ID `abc123`:
```bash
docker rmi abc123
```

To remove a stale container with ID `def456`:
```bash
docker rm def456
```

#### Under the Hood
When you run `docker rmi`, Docker removes the specified image from your local system. Similarly, `docker rm` removes the specified container.

#### Real-World Example
In a development environment, it is common to create and discard multiple versions of images and containers. Regularly cleaning up these resources ensures that your system remains organized and efficient.

#### How to Prevent / Defend
- **Automated Cleanup**: Implement automated scripts or tools to periodically clean up unused images and containers.
- **Version Control**: Use version control systems to manage and track changes to your Docker images and containers.

### Conclusion

This chapter covered several fundamental Docker commands and concepts, including `docker pull`, `docker run`, `docker start`, `docker stop`, `docker ps`, and `docker images`. Understanding these commands is essential for effectively managing Docker containers and images. By following best practices and implementing proper security measures, you can ensure that your Docker environment remains secure and efficient.

### Practice Labs

For hands-on practice with Docker basics, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs that cover various aspects of web application security, including Docker.
- **OWASP Juice Shop**: A deliberately insecure web application that includes Docker-based challenges.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning web security, which can be run using Docker.

These labs provide practical experience with Docker and help reinforce the concepts covered in this chapter.

---
<!-- nav -->
[[02-Introduction to Docker Basics and Interactive Terminal Access|Introduction to Docker Basics and Interactive Terminal Access]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/05-Docker Basics Commands Overview/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/05-Docker Basics Commands Overview/04-Practice Questions & Answers|Practice Questions & Answers]]
