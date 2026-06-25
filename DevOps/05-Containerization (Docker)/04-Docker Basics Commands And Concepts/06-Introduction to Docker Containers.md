---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Docker Containers

Docker is a platform that allows developers to package applications into containers—standardized executable components combining application source code with libraries and dependencies needed to run the application in any environment. This ensures consistency across development, testing, and production environments. In this section, we will delve into the basics of Docker commands and concepts, focusing specifically on how to work with Docker containers.

### What is a Container?

A container is a lightweight, standalone, executable package that includes everything needed to run a piece of software: code, runtime, system tools, system libraries, and settings. Containers are isolated from one another and from the host system, ensuring that the application runs consistently regardless of the environment.

#### Why Use Containers?

Containers provide several benefits:

1. **Portability**: Applications packaged in containers can run consistently across different environments (development, testing, staging, production).
2. **Isolation**: Each container runs in isolation from others, reducing conflicts between applications.
3. **Efficiency**: Containers share the host operating system kernel, making them more efficient than virtual machines.
4. **Scalability**: Containers can be easily scaled up or down based on demand.

### Working with Docker Images and Containers

Before diving into containers, it’s important to understand the relationship between Docker images and containers. A Docker image is a read-only template containing the instructions necessary to build a container. A container, on the other hand, is a running instance of an image.

#### Creating a Container from an Image

To create a container from an image, you use the `docker run` command. Let's take the example of creating a Redis container.

```bash
docker run redis
```

This command starts a Redis server inside a container. The `redis` argument specifies the image to use. By default, the container runs in an attached mode, meaning the terminal session is tied to the container process. If you press `Ctrl+C`, the container will stop running.

#### Checking Running Containers

To check the status of running containers, you can use the `docker ps` command.

```bash
docker ps
```

This command lists all currently running containers along with their details such as container ID, image name, and ports.

### Detached Mode

Running a container in detached mode allows the container to continue running even after you close the terminal session. To run a container in detached mode, use the `-d` flag with the `docker run` command.

```bash
docker run -d redis
```

In this case, the command will return immediately with the container ID, and the container will continue running in the background.

#### Example: Full Workflow

Let's walk through a complete workflow of starting a Redis container in both attached and detached modes.

1. **Start Redis in Attached Mode**

    ```bash
    docker run redis
    ```

    This will start the Redis server, and the terminal session will be tied to the container process.

2. **Check Running Containers**

    Open a new terminal tab and run:

    ```bash
    docker ps
    ```

    You should see the Redis container listed with its container ID, image name, and port mappings.

3. **Stop the Container**

    Press `Ctrl+C` in the original terminal tab to stop the Redis container. Then, run `docker ps` again to confirm that the container is no longer running.

4. **Start Redis in Detached Mode**

    ```bash
    docker run -d redis
    ```

    This will start the Redis server in the background, and the terminal session will return immediately with the container ID.

5. **Check Running Containers Again**

    Run `docker ps` to confirm that the Redis container is running in detached mode.

### Detailed Example: Full HTTP Request and Response

When working with Docker containers, especially those exposing services like Redis, it’s useful to understand the underlying network interactions. Here’s a detailed example of how to interact with a Redis container using HTTP requests.

1. **Start Redis Container**

    ```bash
    docker run -d -p 6379:6379 redis
    ```

    This command starts the Redis server in detached mode and maps port 6379 of the container to port 6379 of the host machine.

2. **Check Running Containers**

    ```bash
    docker ps
    ```

    You should see the Redis container listed with its container ID, image name, and port mappings.

3. **Interact with Redis Using Telnet**

    Since Redis uses a TCP protocol, you can interact with it using `telnet`.

    ```bash
    telnet localhost 6379
    ```

    Once connected, you can issue Redis commands like `PING`.

    ```plaintext
    PING
    +PONG
    ```

### Common Pitfalls and How to Prevent Them

#### Pitfall: Memory and Resource Management

Containers can consume significant resources, leading to performance issues or even crashes if not managed properly. Ensure that your Docker setup is configured to limit resource usage.

**Secure Configuration Example:**

```yaml
version: '3'
services:
  redis:
    image: redis
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
```

#### Pitfall: Data Persistence

By default, data stored in a container is lost when the container is removed. Use volumes to persist data across container lifecycles.

**Secure Configuration Example:**

```yaml
version: '3'
services:
  redis:
    image: redis
    volumes:
      - ./data:/data
```

### Real-World Examples and Recent CVEs

#### Example: CVE-2021-21247

CVE-2021-21247 is a critical vulnerability affecting Docker versions prior to 20.10.6. This vulnerability allows attackers to execute arbitrary code on the host system by exploiting the Docker daemon.

**Detection and Prevention:**

1. **Update Docker**: Ensure that Docker is updated to the latest version.
2. **Use Secure Configurations**: Implement secure configurations as shown above.
3. **Regular Audits**: Perform regular security audits to identify and mitigate vulnerabilities.

### Hands-On Labs

For practical experience with Docker, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on container security.
- **OWASP Juice Shop**: Provides a vulnerable web application that can be deployed in Docker containers.
- **DVWA (Damn Vulnerable Web Application)**: Another vulnerable web application that can be used to practice Docker and container security.

### Conclusion

Understanding Docker containers and their management is crucial for modern DevOps practices. By mastering the basics of Docker commands and concepts, you can ensure consistent and efficient deployment of applications across various environments. Always remember to follow secure coding practices and regularly update your Docker setup to mitigate potential vulnerabilities.

---
<!-- nav -->
[[05-Introduction to Docker Basics|Introduction to Docker Basics]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/04-Docker Basics Commands And Concepts/00-Overview|Overview]] | [[07-Introduction to Docker Networking and Port Binding|Introduction to Docker Networking and Port Binding]]
