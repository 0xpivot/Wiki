---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Docker Basics: Commands and Concepts

### Introduction to Docker

Docker is an open-source platform that automates the deployment, scaling, and management of applications inside software containers. Containers allow developers to package up their applications with all of their dependencies into a standardized unit for software development. This ensures that the application works seamlessly in any environment.

#### What is a Container?

A container is a lightweight, stand-alone, executable package that includes everything needed to run a piece of software: code, runtime, system tools, system libraries, and settings. Containers are isolated from each other and the host system, ensuring that they do not interfere with each other.

#### Why Use Docker?

1. **Portability**: Docker containers can run on any system that supports Docker, including Windows, macOS, and Linux.
2. **Isolation**: Each container runs in isolation from others, ensuring that they do not affect each other.
3. **Consistency**: Docker ensures that the application runs the same way in every environment, reducing the "works on my machine" problem.
4. **Scalability**: Docker makes it easy to scale applications horizontally by spinning up more containers.

### Basic Docker Commands

#### `docker ps`

The `docker ps` command lists all the running containers on your system. By default, it shows only the running containers.

```bash
$ docker ps
```

This command outputs a table with columns such as CONTAINER ID, IMAGE, COMMAND, CREATED, STATUS, PORTS, and NAMES.

#### Example Output

```plaintext
CONTAINER ID   IMAGE          COMMAND                  CREATED       STATUS       PORTS     NAMES
838abc123456   redis:latest   "docker-entrypoint.s…"   2 hours ago   Up 2 hours   6379/tcp  redis_container
```

In this example, the container with ID `838abc123456` is running the `redis:latest` image.

### Detached Mode

When you start a Docker container in detached mode, it runs in the background. This is useful for long-running processes like databases or web servers.

#### Command

```bash
$ docker run -d <image_name>
```

For example:

```bash
$ docker run -d redis:latest
```

This starts the Redis server in detached mode.

### Stopping and Restarting Containers

#### Stopping a Container

To stop a running container, you need its container ID or name. You can use the `docker stop` command followed by the container ID or name.

```bash
$ docker stop <container_id_or_name>
```

For example:

```bash
$ docker stop 838abc123456
```

This stops the container with ID `838abc123456`.

#### Restarting a Container

To restart a stopped container, you can use the `docker start` command followed by the container ID or name.

```bash
$ docker start <container_id_or_name>
```

For example:

```bash
$ docker start 838abc123456
```

This starts the container with ID ` 838abc123456`.

### Listing All Containers

By default, `docker ps` shows only the running containers. To list all containers, including those that are stopped, you can use the `-a` flag.

```bash
$ docker ps -a
```

This command outputs a table with columns such as CONTAINER ID, IMAGE, COMMAND, CREATED, STATUS, PORTS, and NAMES.

#### Example Output

```plaintext
CONTAINER ID   IMAGE          COMMAND                  CREATED       STATUS         PORTS     NAMES
838abc123456   redis:latest   "docker-entrypoint.s…"   2 hours ago   Exited (0) 2   6379/tcp  redis_container
```

In this example, the container with ID `838abc123456` is stopped.

### Running Multiple Versions of the Same Application

Sometimes you might need to run multiple versions of the same application. For example, you might have two parallel applications that both use Redis but in different versions.

#### Starting Multiple Redis Containers

To run multiple Redis containers with different versions, you can specify the version in the image name.

```bash
$ docker run -d redis:5.0.6
$ docker run -d redis:6.2.6
```

These commands start two Redis containers with different versions.

### Detailed Example: Running and Managing Redis Containers

Let's walk through a detailed example of running and managing Redis containers using Docker.

#### Step 1: Start a Redis Container

First, start a Redis container in detached mode.

```bash
$ docker run -d --name redis_506 redis:5.0.6
```

This command starts a Redis container with the tag `5.0.6` and names it `redis_506`.

#### Step 2: Verify the Running Container

Check the running containers using `docker ps`.

```bash
$ docker ps
```

Example Output:

```plaintext
CONTAINER ID   IMAGE          COMMAND                  CREATED       STATUS       PORTS     NAMES
838abc123456   redis:5.0.6    "docker-entrypoint.s…"   2 hours ago   Up 2 hours   6379/tcp  redis_506
```

#### Step 3: Stop the Container

Stop the running Redis container.

```bash
$ docker stop redis_506
```

#### Step 4: List All Containers

List all containers, including the stopped ones.

```bash
$ docker ps -a
```

Example Output:

```plaintext
CONTAINER ID   IMAGE          COMMAND                  CREATED       STATUS         PORTS     NAMES
838abc123456   redis:5.0.6    "docker-entrypoint.s…"   2 hours ago   Exited (0) 2   6379/tcp  redis_506
```

#### Step 5: Restart the Container

Restart the stopped Redis container.

```bash
$ docker start redis_506
```

#### Step 6: Verify the Running Container Again

Check the running containers again.

```bash
$ docker ps
```

Example Output:

```plaintext
CONTAINER ID   IMAGE          COMMAND                  CREATED       STATUS       PORTS     NAMES
838abc123456   redis:5.0.6    "docker-entrypoint.s…"   2 hours ago   Up 2 hours   6379/tcp  redis_506
```

### Running Multiple Redis Containers with Different Versions

Now, let's run multiple Redis containers with different versions.

#### Step 1: Start Two Redis Containers with Different Versions

Start two Redis containers with different versions.

```bash
$ docker run -d --name redis_506 redis:5.0.6
$ docker run -d --name redis_626 redis:6.2.6
```

#### Step 2: Verify the Running Containers

Check the running containers using `docker ps`.

```bash
$ docker ps
```

Example Output:

```plaintext
CONTAINER ID   IMAGE          COMMAND                  CREATED       STATUS       PORTS     NAMES
838abc123456   redis:5.0.6    "docker-entrypoint.s…"   2 hours ago   Up 2 hours   6379/tcp  redis_506
938def123456   redis:6.2.6    "docker-entrypoint.s…"   2 hours ago   Up 2 hours   6379/tcp  redis_626
```

### How to Prevent / Defend

#### Detection

To detect running Docker containers, you can use the `docker ps` command. To detect stopped containers, use `docker ps -a`.

#### Prevention

1. **Use Secure Images**: Always use trusted and verified Docker images from reputable sources.
2. **Regular Updates**: Keep your Docker images and containers updated to the latest versions.
3. **Container Isolation**: Ensure that containers are properly isolated from each other and the host system.
4. **Monitoring**: Use monitoring tools to track the status and health of your containers.

#### Secure Coding Fixes

**Vulnerable Code**

```bash
$ docker run -d --name redis_506 redis:5.0.6
```

**Secure Code**

```bash
$ docker run -d --name redis_506 --restart unless-stopped redis:5.0.6
```

In the secure code, the `--restart unless-stopped` flag ensures that the container automatically restarts if it stops unexpectedly.

### Conclusion

Docker provides a powerful and flexible platform for deploying and managing applications. Understanding basic Docker commands and concepts is essential for effectively using Docker in your development workflow. By following best practices and using secure coding techniques, you can ensure that your Docker containers are reliable and secure.

### Practice Labs

For hands-on practice with Docker basics, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive set of labs covering various aspects of web security, including Docker.
- **OWASP Juice Shop**: A deliberately insecure web application for security training purposes, which can be deployed using Docker.
- **Docker Documentation**: Official Docker documentation provides numerous examples and tutorials to help you get started with Docker.

By completing these labs, you can gain practical experience with Docker and reinforce your understanding of the concepts covered in this chapter.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/05-Containerization (Docker)/04-Docker Basics Commands And Concepts/00-Overview|Overview]] | [[02-Introduction to Docker Basics Commands and Concepts|Introduction to Docker Basics Commands and Concepts]]
