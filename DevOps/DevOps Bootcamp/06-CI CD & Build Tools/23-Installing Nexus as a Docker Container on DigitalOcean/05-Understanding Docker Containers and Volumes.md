---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Understanding Docker Containers and Volumes

### Introduction to Docker Containers

Docker containers are lightweight, stand-alone, executable packages that include everything needed to run a piece of software, including the code, a runtime, libraries, environment variables, and configuration files. They are built using Docker images, which are essentially blueprints for creating containers. Containers are isolated from one another and from the host system, providing a consistent and portable environment for applications.

### Docker Volumes

Docker volumes are a way to persist data outside of the lifecycle of a container. By default, when a container is deleted, all the data within it is lost. However, by using volumes, you can store data in a way that it persists even after the container is removed. This is particularly useful for applications like Nexus, which require persistent storage for configurations and data.

### Mounting Volumes in Docker

When you mount a volume into a Docker container, you are essentially creating a link between a directory on the host machine and a directory inside the container. This allows the container to read from and write to the host's filesystem, ensuring that data remains available even if the container is stopped or removed.

#### Example: Mounting a Volume in Docker

Let's consider an example where we install Nexus as a Docker container on DigitalOcean and mount a volume for persistent storage.

```bash
docker run -d \
  -p 8081:8081 \
  -v /path/to/nexus-data:/nexus-data \
  --name nexus \
  sonatype/nexus3
```

In this command:
- `-d` runs the container in detached mode.
- `-p 8081:8081` maps port 8081 on the host to port 8081 in the container.
- `-v /path/to/nexus-data:/nexus-data` mounts the `/path/to/nexus-data` directory on the host to the `/nexus-data` directory in the container.
- `--name nexus` assigns the name `nexus` to the container.
- `sonatype/nexus3` is the Docker image used to create the container.

### Checking the Mounted Volume Inside the Container

Once the container is running, you can check the contents of the mounted volume inside the container. This ensures that the data is correctly replicated and accessible.

```bash
docker exec -it nexus bash
ls /nexus-data
```

In this command:
- `docker exec -it nexus bash` starts an interactive shell session inside the `nexus` container.
- `ls /nexus-data` lists the contents of the `/nexus-data` directory inside the container.

### Diagram: Docker Container with Mounted Volume

```mermaid
graph TB
    A[Host Machine] -->|Mounts Volume| B[Docker Container]
    B --> C[/nexus-data Directory]
    A --> D[/path/to/nexus-data Directory]
    D -->|Data Persistence| C
```

### Real-World Example: Persistent Storage in Nexus

In a real-world scenario, Nexus is often used in continuous integration and delivery pipelines to manage artifacts such as JAR files, WAR files, and Docker images. Without persistent storage, any data stored in Nexus would be lost whenever the container is restarted or removed. By mounting a volume, you ensure that the data remains available across container lifecycles.

### Pitfalls and Common Mistakes

One common mistake is not properly configuring the volume mount. If the paths are incorrect or the permissions are not set correctly, the data may not be accessible or may cause errors. Additionally, if the volume is not mounted correctly, the data may not persist as expected.

### How to Prevent / Defend

#### Detection

To detect issues with volume mounting, you can check the logs of the Docker daemon and the container itself. Look for any errors related to file access or permission issues.

```bash
docker logs nexus
```

#### Prevention

Ensure that the paths used for volume mounting are correct and that the necessary permissions are set. You can also use Docker's built-in volume management features to simplify the process.

#### Secure Coding Fix

Here is an example of a vulnerable configuration and a secure configuration:

**Vulnerable Configuration:**

```bash
docker run -d \
  -p 8081:8081 \
  --name nexus \
  sonatype/nexus3
```

**Secure Configuration:**

```bash
docker run -d \
  -p 8081:8081 \
  -v /path/to/nexus-data:/nexus-data \
  --name nexus \
  sonatype/nexus3
```

### Hardening

To further harden the setup, you can use Docker's security features such as AppArmor or SELinux policies to restrict the container's access to the host filesystem.

### Complete Example: Full HTTP Request and Response

While this example does not involve HTTP requests directly, let's consider a scenario where you might want to check the status of the Nexus service via an HTTP request.

#### HTTP Request

```http
GET /service/rest/v1/status HTTP/1.1
Host: localhost:8081
Authorization: Basic YWRtaW46YWRtaW4=
```

#### HTTP Response

```http
HTTP/1.1 200 OK
Date: Tue, 01 Aug 2023 12:00:00 GMT
Content-Type: application/json;charset=UTF-8
Transfer-Encoding: chunked

{
  "version": "3.32.0",
  "status": "RUNNING"
}
```

### Hands-On Lab Suggestions

For hands-on practice with Docker and Nexus, consider the following labs:

- **PortSwigger Web Security Academy**: While primarily focused on web security, this platform offers exercises that can help you understand how to secure Docker containers and their volumes.
- **OWASP Juice Shop**: This is a deliberately insecure web application that you can use to practice securing Docker environments.
- **DigitalOcean Tutorials**: DigitalOcean provides comprehensive tutorials on setting up and managing Docker containers, including Nexus.

By following these steps and practices, you can ensure that your Docker containers, especially those running critical services like Nexus, are properly configured and secured.

---
<!-- nav -->
[[04-Creating a Docker Volume|Creating a Docker Volume]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/23-Installing Nexus as a Docker Container on DigitalOcean/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/23-Installing Nexus as a Docker Container on DigitalOcean/06-Practice Questions & Answers|Practice Questions & Answers]]
