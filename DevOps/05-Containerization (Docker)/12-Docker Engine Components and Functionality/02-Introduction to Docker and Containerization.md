---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Docker and Containerization

Docker is a platform that automates the deployment of applications inside software containers. Containers are lightweight, portable, and self-sufficient units that encapsulate an application and its dependencies. They provide a consistent environment across different computing platforms, ensuring that the application runs the same way everywhere. This consistency is crucial in modern DevOps practices, where continuous integration and continuous delivery (CI/CD) pipelines are essential.

### Background Theory

Before diving into Docker, it's important to understand the concept of containerization. Containerization is a method of packaging software applications into isolated environments that contain all the necessary dependencies to run the application. This isolation ensures that the application will run consistently across different environments, whether it's a developer's local machine, a testing environment, or a production server.

Containers differ from virtual machines (VMs) in several key ways:

1. **Resource Efficiency**: Containers share the host operating system kernel, whereas VMs require their own full operating system instance. This makes containers much lighter and more efficient in terms of resource usage.
2. **Speed**: Containers can be started almost instantly, whereas VMs take longer to boot up.
3. **Portability**: Containers can be easily moved between different environments, as they encapsulate all dependencies within the container.

### Docker Engine Components

When you install Docker, you are essentially installing the Docker Engine, which is composed of three main components:

1. **Docker Server (Daemon)**: This is the core component of the Docker Engine that manages the containers, images, and other resources. The Docker daemon listens for API requests and performs the requested actions.
2. **Docker API**: This is the interface through which the Docker client communicates with the Docker daemon. The API allows users to interact with the Docker daemon programmatically.
3. **Docker CLI (Command Line Interface)**: This is the user-facing tool that allows users to interact with the Docker daemon using commands. The CLI provides a powerful set of commands to manage Docker resources.

#### Docker Server (Daemon)

The Docker daemon is the central component of the Docker Engine. It is responsible for managing the lifecycle of containers, including creating, starting, stopping, and deleting them. Additionally, the Docker daemon handles the management of Docker images, which are the building blocks of containers.

##### Key Responsibilities of the Docker Daemon

- **Pulling Images**: The Docker daemon can fetch Docker images from a registry, such as Docker Hub.
- **Storing Images**: Once pulled, images are stored locally on the host machine.
- **Starting Containers**: The Docker daemon starts containers based on the specified image.
- **Stopping Containers**: The Docker daemon can stop running containers.
- **Managing Volumes**: The Docker daemon manages persistent storage for containers.
- **Configuring Networks**: The Docker daemon sets up and manages networks for containers.
- **Building Images**: The Docker daemon can build custom Docker images from Dockerfiles.

#### Docker API

The Docker API is a RESTful interface that allows users to interact with the Docker daemon programmatically. The API provides a wide range of endpoints to perform various operations, such as creating containers, managing images, and configuring networks.

##### Example of Using the Docker API

To demonstrate the use of the Docker API, let's consider an example where we want to list all the running containers using an HTTP GET request.

```http
GET /v1.40/containers/json HTTP/1.1
Host: localhost:2375
```

The response from the Docker daemon would look like this:

```http
HTTP/1.1 200 OK
Content-Type: application/json

[
    {
        "Id": "abc123",
        "Names": ["/my-container"],
        "Image": "nginx:latest",
        "State": "running",
        "Status": "Up 10 minutes"
    }
]
```

In this example, the `GET` request to `/v1.40/containers/json` returns a JSON array containing information about the running containers.

#### Docker CLI (Command Line Interface)

The Docker CLI is the primary tool used to interact with the Docker daemon. It provides a set of commands that allow users to manage Docker resources, such as images, containers, and networks.

##### Common Docker CLI Commands

- `docker pull`: Pulls an image from a registry.
- `docker run`: Runs a new container.
- `docker stop`: Stops a running container.
- `docker rm`: Removes a container.
- `docker ps`: Lists all running containers.
- `docker images`: Lists all available images.
- `docker build`: Builds a new image from a Dockerfile.

### Detailed Explanation of Docker Components

#### Container Runtime

The container runtime is the component of the Docker daemon that is responsible for managing the lifecycle of containers. It handles tasks such as starting, stopping, and managing the execution of containers.

##### Starting a Container

To start a container, you can use the `docker run` command. For example, to start a container based on the `nginx:latest` image, you would use the following command:

```sh
docker run -d --name my-nginx nginx:latest
```

This command starts a new container named `my-nginx` based on the `nginx:latest` image in detached mode (`-d`).

##### Stopping a Container

To stop a running container, you can use the `docker stop` command. For example, to stop the `my-nginx` container, you would use the following command:

```sh
docker stop my-nginx
```

#### Volumes

Volumes are a feature of Docker that allow you to persist data outside of the container's writable layer. This is useful for scenarios where you need to store data that should survive the lifecycle of the container.

##### Creating a Volume

To create a volume, you can use the `docker volume create` command. For example, to create a volume named `my-volume`, you would use the following command:

```sh
docker volume create my-volume
```

##### Mounting a Volume

To mount a volume to a container, you can use the `-v` flag with the `docker run` command. For example, to mount the `my-volume` volume to the `/data` directory in the container, you would use the following command:

```sh
docker run -d --name my-container -v my-volume:/data my-image
```

#### Network Configuration

Docker provides a built-in networking model that allows containers to communicate with each other and with the external world. By default, Docker creates a bridge network that containers can join.

##### Creating a Network

To create a custom network, you can use the `docker network create` command. For example, to create a network named `my-network`, you would use the following command:

```sh
docker network create my-network
```

##### Connecting a Container to a Network

To connect a container to a network, you can use the `--network` flag with the `docker run` command. For example, to connect the `my-container` container to the `my-network` network, you would use the following command:

```sh
docker run -d --name my-container --network my-network my-image
```

#### Building Custom Docker Images

Docker allows you to build custom images from a `Dockerfile`. A `Dockerfile` is a text file that contains instructions for building a Docker image.

##### Example Dockerfile

Here is an example `Dockerfile` that builds an image based on the `nginx:latest` image and copies a custom configuration file into the container:

```Dockerfile
# Use the official Nginx image as the base image
FROM nginx:latest

# Copy the custom configuration file into the container
COPY ./custom.conf /etc/nginx/conf.d/

# Expose port 80
EXPOSE 80

# Start Nginx
CMD ["nginx", "-g", "daemon off;"]
```

To build the image from the `Dockerfile`, you would use the following command:

```sh
docker build -t my-nginx .
```

This command builds a new image tagged as `my-nginx` from the current directory.

### Real-World Examples and Recent CVEs

#### CVE-2019-14287: Docker API Authentication Bypass

CVE-2019-14287 is a critical vulnerability in Docker that allows an attacker to bypass authentication and gain unauthorized access to the Docker API. This vulnerability affects Docker versions prior to 19.03.8.

##### How the Vulnerability Works

The vulnerability arises from a flaw in the Docker API authentication mechanism. An attacker can send a specially crafted request to the Docker API that bypasses the authentication check, allowing them to execute arbitrary commands on the host machine.

##### Impact

An attacker exploiting this vulnerability could gain full control of the host machine, potentially leading to data theft, service disruption, or further exploitation of other vulnerabilities.

##### Detection and Prevention

To detect and prevent this vulnerability, follow these steps:

1. **Update Docker**: Ensure that you are using a version of Docker that is not affected by this vulnerability.
2. **Enable TLS**: Enable Transport Layer Security (TLS) for the Docker API to encrypt communication and prevent man-in-the-middle attacks.
3. **Use Strong Authentication**: Implement strong authentication mechanisms, such as OAuth or JWT, to protect the Docker API.

##### Secure Code Fix

Here is an example of how to enable TLS for the Docker API:

```sh
# Edit the Docker daemon configuration file (usually located at /etc/docker/daemon.json)
{
  "tls": true,
  "tlscacert": "/path/to/ca.pem",
  "tlscert": "/path/to/server-cert.pem",
  "tlskey": "/path/to/server-key.pem"
}

# Restart the Docker daemon
sudo systemctl restart docker
```

By enabling TLS, you ensure that all communication with the Docker API is encrypted and authenticated.

### Pitfalls and Common Mistakes

#### Overusing Privileged Mode

One common mistake is overusing privileged mode when running containers. Running containers in privileged mode grants the container extensive permissions, including access to all devices on the host machine. This can lead to security risks if the container is compromised.

##### How to Avoid

To avoid this pitfall, only use privileged mode when absolutely necessary. Instead, use capabilities to grant specific permissions to the container.

##### Example of Using Capabilities

Here is an example of how to run a container with specific capabilities instead of using privileged mode:

```sh
docker run --cap-add=NET_ADMIN --cap-add=SYS_ADMIN my-image
```

This command runs the `my-image` container with the `NET_ADMIN` and `SYS_ADMIN` capabilities, which are often sufficient for most use cases.

### How to Prevent / Defend

#### Secure Configuration

To secure your Docker setup, follow these best practices:

1. **Use Non-root Users**: Run containers as non-root users whenever possible to limit the potential damage if the container is compromised.
2. **Limit Capabilities**: Use capabilities to grant only the necessary permissions to the container.
3. **Use SELinux/AppArmor**: Enable SELinux or AppArmor to provide additional security controls for containers.
4. **Regularly Update**: Keep your Docker installation and images up to date to ensure you have the latest security patches.

#### Monitoring and Logging

Monitoring and logging are crucial for detecting and responding to security incidents. Here are some tips for monitoring and logging:

1. **Enable Audit Logs**: Enable audit logs for the Docker daemon to track all API requests and container actions.
2. **Use a Security Information and Event Management (SIEM) System**: Integrate your Docker setup with a SIEM system to centralize and analyze security events.
3. **Set Up Alerts**: Configure alerts for suspicious activity, such as unexpected container creation or network traffic.

### Hands-On Labs

For hands-on practice with Docker, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a series of labs focused on web application security, including Docker-related challenges.
- **OWASP Juice Shop**: A deliberately insecure web application that includes Docker-based challenges.
- **Docker Security Workshop**: A comprehensive workshop provided by Docker that covers various security aspects of Docker.

These labs provide practical experience with Docker and help reinforce the concepts covered in this chapter.

### Conclusion

Docker is a powerful tool for containerizing applications, providing a consistent and portable environment across different computing platforms. Understanding the components of the Docker Engine, such as the Docker daemon, API, and CLI, is essential for effectively managing Docker resources. By following best practices and implementing security measures, you can ensure that your Docker setup is secure and reliable.

---
<!-- nav -->
[[01-Introduction to Docker Engine Components and Functionality|Introduction to Docker Engine Components and Functionality]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/12-Docker Engine Components and Functionality/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/12-Docker Engine Components and Functionality/03-Practice Questions & Answers|Practice Questions & Answers]]
