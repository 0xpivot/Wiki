---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Docker Basics and Interactive Terminal Access

Docker is a platform that allows developers to package their applications into lightweight, portable containers. These containers encapsulate an application along with its dependencies, ensuring that the application runs consistently across different environments. One of the key features of Docker is the ability to interact with running containers, allowing users to inspect and debug them as needed.

### What is Docker?

Docker is an open-source containerization technology that automates the deployment, scaling, and management of applications. Containers are isolated processes that run on a single host operating system, sharing the kernel but having their own user space. This makes them more lightweight and efficient compared to traditional virtual machines.

### Why Use Docker?

- **Portability**: Applications packaged in Docker containers can run consistently across different environments, from development to production.
- **Isolation**: Each container runs in isolation, reducing conflicts between applications and ensuring consistent behavior.
- **Efficiency**: Containers share the host OS kernel, making them more lightweight and resource-efficient than virtual machines.

### Docker Commands Overview

To effectively manage Docker containers, several commands are essential. One of these is the `docker exec` command, which allows you to run a new process inside a running container.

### Interactive Terminal Access with `docker exec`

The `docker exec` command is used to run a new process inside a running container. When combined with the `-it` flag, it provides an interactive terminal session within the container.

#### Syntax

```bash
docker exec [-it] CONTAINER COMMAND [ARG...]
```

- `-i`: Keeps STDIN open even if not attached.
- `-t`: Allocates a pseudo-TTY.
- `CONTAINER`: The name or ID of the container.
- `COMMAND`: The command to execute inside the container.
- `ARG`: Arguments to pass to the command.

#### Example

Suppose you have a running container with the ID `abc123`. To access an interactive terminal inside this container, you would use:

```bash
docker exec -it abc123 bash
```

This command starts a Bash shell inside the container, allowing you to interact with the container's file system and environment.

### Navigating the Container's File System

Once inside the container, you can use standard Unix commands to navigate the file system and inspect files.

#### Example Commands

- `ls`: List files in the current directory.
- `cd`: Change directory.
- `pwd`: Print working directory.
- `cat`: Display file contents.
- `env`: Print all environment variables.

#### Full Example

Consider a container with the ID `abc123`. Here’s how you might interact with it:

```bash
# Start an interactive terminal session
docker exec -it abc123 bash

# List files in the current directory
ls

# Change to the home directory
cd /home

# List files in the home directory
ls

# Print all environment variables
env
```

### Using Container Names Instead of IDs

While container IDs are unique identifiers, they can be cumbersome to remember. Docker allows you to assign names to containers, making it easier to reference them.

#### Naming Containers

When starting a container, you can assign a name using the `--name` option:

```bash
docker run --name my-container -d ubuntu
```

#### Accessing Named Containers

To access a named container, you can use the container name instead of the ID:

```bash
docker exec -it my-container bash
```

### Real-World Examples and Use Cases

Interactive terminal access is particularly useful in debugging and troubleshooting scenarios. For instance, if you encounter issues with a complex configuration or application setup, you can use `docker exec` to inspect the container's state.

#### Example: Debugging a Complex Configuration

Suppose you have a container running a custom application with a complex configuration. You suspect that some environment variables are not being set correctly. You can use `docker exec` to inspect the environment variables:

```bash
docker exec -it my-container env
```

This command will list all environment variables inside the container, helping you identify any misconfigurations.

### Security Considerations

While interactive terminal access is powerful, it also poses security risks. Unauthorized access to a container can lead to data breaches or malicious activities.

#### How to Prevent / Defend

1. **Limit Access**: Ensure that only authorized users have access to the Docker daemon and the containers.
2. **Use Secure Credentials**: Avoid hardcoding sensitive information like passwords or API keys in your Dockerfiles or environment variables.
3. **Audit Logs**: Enable audit logs to track who accessed the containers and what actions were performed.
4. **Network Isolation**: Use network policies to isolate containers and restrict unauthorized access.

#### Secure Coding Practices

Here’s an example of how to securely set environment variables in a Dockerfile:

**Vulnerable Version**

```Dockerfile
FROM ubuntu
ENV SECRET_KEY=your_secret_key
CMD ["bash"]
```

**Secure Version**

```Dockerfile
FROM ubuntu
CMD ["bash"]
```

In the secure version, the secret key is not hardcoded in the Dockerfile. Instead, it can be passed as an environment variable when starting the container:

```bash
docker run --name my-container -e SECRET_KEY=your_secret_key -d ubuntu
```

### Conclusion

Interactive terminal access with `docker exec` is a powerful feature that enables developers to inspect and debug running containers. By understanding how to use this command effectively, you can ensure that your applications run smoothly and securely. Always follow best practices for security to prevent unauthorized access and protect your applications.

### Practice Labs

For hands-on experience with Docker basics, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs that cover Docker and container security.
- **OWASP Juice Shop**: A deliberately insecure web application that includes Docker-based challenges.
- **DVWA (Damn Vulnerable Web Application)**: Provides Docker-based environments for learning web application security.

These labs provide practical experience in using Docker commands and understanding container security.

---
<!-- nav -->
[[01-Docker Basics Commands Overview|Docker Basics Commands Overview]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/05-Docker Basics Commands Overview/00-Overview|Overview]] | [[03-Introduction to Docker Basics|Introduction to Docker Basics]]
