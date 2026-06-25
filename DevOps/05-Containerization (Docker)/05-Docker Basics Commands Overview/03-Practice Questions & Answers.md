---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. What is the difference between `docker run` and `docker start`?**

The `docker run` command is used to create and start a new container from an image. It allows you to specify various options such as port bindings, environment variables, and container names. When you run `docker run`, Docker pulls the specified image (if it’s not already present locally), creates a new container, and starts it immediately.

On the other hand, `docker start` is used to start an existing container that has been previously stopped. This command does not pull any new images or create new containers; it simply restarts the specified container with the same attributes it had when it was originally created using `docker run`.

For example:
```bash
# Create and start a new container
docker run -d --name my_container nginx

# Stop the container
docker stop my_container

# Restart the stopped container
docker start my_container
```

**Q2. How can you bind a host port to a container port using Docker?**

To bind a host port to a container port, you can use the `-p` flag followed by the host port and the container port. The general syntax is:

```bash
docker run -p <host_port>:<container_port> <image_name>
```

For example, to map port 8080 on the host to port 80 on the container, you would run:

```bash
docker run -p 8080:80 nginx
```

This command maps the host's port 8080 to the container's port 80, allowing traffic to the host's port 8080 to be forwarded to the container's port  80.

**Q3. Explain how to view the logs of a Docker container.**

To view the logs of a Docker container, you can use the `docker logs` command followed by the container ID or name. For example:

```bash
docker logs <container_id_or_name>
```

If you don’t remember the exact container ID or name, you can list all containers (including stopped ones) using `docker ps -a` and find the ID or name from the output. Alternatively, you can use the `--follow` (`-f`) flag to continuously stream the logs as they are generated:

```bash
docker logs -f <container_id_or_name>
```

This is particularly useful for monitoring the output of a running container in real-time.

**Q4. How can you access the terminal of a running Docker container for debugging purposes?**

To access the terminal of a running Docker container, you can use the `docker exec` command. This allows you to execute a new process within the container. To get an interactive shell, you can use the `-it` flags:

```bash
docker exec -it <container_id_or_name> /bin/bash
```

This command opens an interactive shell (`/bin/bash`) in the specified container, allowing you to run commands directly within the container's environment. Once you’re done, you can exit the shell by typing `exit`.

For example, to access the terminal of a container named `redis_latest`:

```bash
docker exec -it redis_latest /bin/bash
```

**Q5. What is the purpose of the `docker ps -a` command?**

The `docker ps -a` command lists all Docker containers, both running and stopped. The `-a` flag stands for "all," meaning it shows every container regardless of its current state. This is useful for managing containers, especially when you need to identify stopped containers that may need to be restarted or removed.

For example:

```bash
docker ps -a
```

This command provides a comprehensive list of all containers, including their status, names, and IDs, making it easier to manage and troubleshoot your Docker environment.

**Q6. How can you name a Docker container during creation?**

When creating a Docker container, you can assign a custom name to it using the `--name` flag. This is particularly useful for easily identifying and managing multiple containers.

For example, to create a container from the `nginx` image and name it `webserver`:

```bash
docker run -d --name webserver nginx
```

This command runs the `nginx` image in detached mode (`-d`) and assigns the name `webserver` to the container. You can then refer to this container by its name in subsequent Docker commands, such as `docker logs webserver` or `docker stop webserver`.

**Q7. What is the significance of the `-d` flag in `docker run`?**

The `-d` flag in `docker run` stands for "detach." When you run a container with the `-d` flag, the container runs in the background, detached from the terminal. This means that the container continues to run even after you close your terminal session.

For example:

```bash
docker run -d nginx
```

This command starts an `nginx` container in detached mode. The container runs independently, and you can interact with it later using other Docker commands such as `docker ps`, `docker logs`, or `docker exec`.

**Q8. How can you clean up unused Docker images and containers?**

To clean up unused Docker images and containers, you can use the following commands:

1. **List all images**: Use `docker images` to list all locally available images.
2. **Remove unused images**: Use `docker image prune` to remove all dangling images (unused intermediate images). You can also use `docker rmi <image_id>` to remove specific images.
3. **List all containers**: Use `docker ps -a` to list all containers, both running and stopped.
4. **Remove stopped containers**: Use `docker container prune` to remove all stopped containers. You can also use `docker rm <container_id>` to remove specific containers.

For example:

```bash
# List all images
docker images

# Remove unused images
docker image prune

# List all containers
docker ps -a

# Remove stopped containers
docker container prune
```

These commands help you maintain a clean and efficient Docker environment by removing unnecessary images and containers.

---
<!-- nav -->
[[03-Introduction to Docker Basics|Introduction to Docker Basics]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/05-Docker Basics Commands Overview/00-Overview|Overview]]
