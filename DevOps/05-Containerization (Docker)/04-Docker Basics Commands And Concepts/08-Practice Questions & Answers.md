---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. What is the difference between a Docker container and a Docker image?**

A Docker image is a static file that contains all the necessary components to run a software application, including the code, libraries, and dependencies. An image is essentially a snapshot of the application's environment. On the other hand, a Docker container is a runtime instance of an image. It is the environment where the application runs, complete with its own filesystem, network interface, and process space. Containers are ephemeral and can be started, stopped, moved, and deleted without affecting the underlying image.

**Q2. How do you pull a Docker image from Docker Hub and run it as a container?**

To pull a Docker image from Docker Hub and run it as a container, you can use the following commands:

```bash
# Pull the image
docker pull redis

# Run the image as a container
docker run redis
```

This will download the `redis` image from Docker Hub and start a container based on that image. By default, the container will run in the foreground and will stop if you terminate it with `Ctrl+C`.

**Q3. Explain how to run a Docker container in detached mode and how to manage it.**

To run a Docker container in detached mode, you can use the `-d` flag with the `docker run` command. This allows the container to run in the background.

```bash
# Run the container in detached mode
docker run -d redis
```

To manage the container, you can use various Docker commands:

- **List running containers:**
  ```bash
  docker ps
  ```

- **Stop a container:**
  ```bash
  docker stop <container_id>
  ```

- **Restart a container:**
  ```bash
  docker start <container_id>
  ```

- **List all containers (both running and stopped):**
  ```bash
  docker ps -a
  ```

**Q4. How do you handle multiple instances of the same application running on different versions using Docker?**

To run multiple instances of the same application on different versions, you can specify the version or tag when pulling and running the Docker image. For example, to run two different versions of Redis:

```bash
# Pull and run Redis version 5.0.6
docker run -d --name redis5 redis:5.0.6

# Pull and run Redis version 4.0
docker run -d --name redis4 redis:4.0
```

This will start two separate containers, each running a different version of Redis.

**Q5. How do you bind a container's port to a host machine's port in Docker?**

To bind a container's port to a host machine's port, you can use the `-p` flag with the `docker run` command. For example, to bind port 6379 of a Redis container to port 6000 of the host machine:

```bash
# Bind container port 6379 to host port 6000
docker run -d -p 6000:6379 --name redis6000 redis
```

If you need to run multiple instances of the same container on different ports, you can bind each container to a unique host port:

```bash
# Bind container port 6379 to host port 6001
docker run -d -p 6001:6379 --name redis6001 redis
```

**Q6. What is the significance of tagging in Docker images?**

Tagging in Docker images is significant because it allows you to specify different versions or variants of an image. When you pull an image without specifying a tag, Docker defaults to the `latest` tag. However, you can specify a particular tag to ensure you are using a specific version of the image. For example:

```bash
# Pull the latest version of Redis
docker pull redis

# Pull a specific version of Redis
docker pull redis:4.0
```

Using tags ensures consistency and predictability in your deployments, especially when dealing with dependencies on specific versions of software.

**Q7. How do you inspect the details of a running Docker container?**

To inspect the details of a running Docker container, you can use the `docker inspect` command followed by the container ID or name. For example:

```bash
# Inspect a container by ID
docker inspect <container_id>

# Inspect a container by name
docker inspect redis6000
```

This command provides detailed information about the container, including its configuration, network settings, and resource usage.

**Q8. How do you stop and remove a Docker container?**

To stop and remove a Docker container, you can use the following commands:

```bash
# Stop the container
docker stop <container_id>

# Remove the container
docker rm <container_id>
```

Alternatively, you can combine these steps into a single command using the `--rm` flag when running the container, which automatically removes the container when it exits:

```bash
# Run and remove the container
docker run --rm redis
```

---
<!-- nav -->
[[07-Introduction to Docker Networking and Port Binding|Introduction to Docker Networking and Port Binding]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/04-Docker Basics Commands And Concepts/00-Overview|Overview]]
