---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Docker Modules in Ansible for State Management

### Introduction to Docker and Ansible

Docker is a platform that allows developers to package applications into containers—standardized executable components combining application source code with the operating system libraries and dependencies required to run that code in any environment. This ensures consistency across development, testing, and production environments. Ansible, on the other hand, is a configuration management tool that can be used to manage the state of systems, including Docker containers.

In this context, managing the state of Docker containers often involves setting up users, groups, and permissions within those containers. The key point from the transcript is that the administrative username and group memberships should vary based on the execution environment. This is crucial for maintaining security and ensuring that the container behaves as expected in different contexts.

### Understanding User Management in Docker Containers

When working with Docker containers, it is essential to understand how user management works. By default, Docker containers run processes as the root user, which can pose significant security risks. Therefore, it is recommended to run processes as non-root users whenever possible.

#### Creating Users and Groups

To create a user and assign them to specific groups within a Docker container, you can use the `adduser` and `groupadd` commands. Here’s an example of how to create a user named `appuser` and add them to a group named `appgroup`:

```bash
RUN groupadd appgroup && \
    useradd -m -g appgroup appuser
```

This command sequence does the following:
- `groupadd appgroup`: Creates a new group called `appgroup`.
- `useradd -m -g appgroup appuser`: Creates a new user called `appuser`, assigns them to the `appgroup`, and creates a home directory for the user (`-m` flag).

#### Setting Environment-Specific Usernames

The transcript mentions that the admin name should be different depending on the execution environment. This can be achieved using environment variables. For instance, you might have different usernames for development, testing, and production environments.

Here’s an example of how to set the username dynamically using an environment variable:

```dockerfile
FROM ubuntu:latest

ARG ADMIN_USER=appuser
ENV ADMIN_USER=${ADMIN_USER}

RUN groupadd ${ADMIN_USER} && \
    useradd -m -g ${ADMIN_USER} ${ADMIN_USER}
```

In this example:
- `ARG ADMIN_USER=appuser`: Defines an argument `ADMIN_USER` with a default value of `appuser`.
- `ENV ADMIN_USER=${ADMIN_USER}`: Sets an environment variable `ADMIN_USER` to the value of the argument.
- `RUN groupadd ${ADMIN_USER} && useradd -m -g ${ADMIN_USER} ${ADMIN_USER}`: Uses the environment variable to create the user and group.

### Real-World Example: CVE-2021-21366

A real-world example of the importance of proper user management in Docker containers is the CVE-2021-21366 vulnerability. This vulnerability affected Docker versions prior to 20.10.6 and allowed attackers to escalate privileges by exploiting the `dockerd` service running as root. This highlights the importance of running services as non-root users whenever possible.

### How to Prevent / Defend

#### Secure Coding Practices

To prevent such vulnerabilities, follow these secure coding practices:
- Always run processes inside Docker containers as non-root users.
- Use environment variables to dynamically set usernames and group memberships based on the execution environment.

Here’s an example of a vulnerable Dockerfile and its secure counterpart:

**Vulnerable Dockerfile:**
```dockerfile
FROM ubuntu:latest

RUN apt-get update && apt-get install -y sudo
RUN useradd -m -s /bin/bash appuser
RUN echo "appuser ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers.d/appuser
USER appuser
```

**Secure Dockerfile:**
```dockerfile
FROM ubuntu:latest

ARG ADMIN_USER=appuser
ENV ADMIN_USER=${ADMIN_USER}

RUN groupadd ${ADMIN_USER} && \
    useradd -m -g ${ADMIN_USER} ${ADMIN_USER}
USER ${ADMIN_USER}
```

In the secure version:
- The `sudo` package is not installed, reducing the attack surface.
- The user is created with minimal permissions, and no `sudo` access is granted.

#### Configuration Hardening

To further harden your Docker configurations, consider the following steps:
- Use a base image that is known to be secure and regularly updated.
- Avoid installing unnecessary packages and services.
- Regularly audit your Dockerfiles and images for security vulnerabilities.

### Hands-On Practice

For hands-on practice with Docker and user management, consider using the following labs:
- **PortSwigger Web Security Academy**: Offers modules on Docker and container security.
- **OWASP Juice Shop**: Provides a vulnerable web application that can be deployed in Docker containers.
- **Docker Security Workshop**: A series of labs provided by Docker to help you understand and implement secure Docker practices.

### Conclusion

Proper user management in Docker containers is crucial for maintaining security and ensuring consistent behavior across different execution environments. By dynamically setting usernames and group memberships using environment variables, you can adapt your Docker configurations to different environments while minimizing security risks. Always follow secure coding practices and regularly audit your Docker configurations to stay ahead of potential vulnerabilities.

---
<!-- nav -->
[[03-Introduction to Docker Modules in Ansible for State Management|Introduction to Docker Modules in Ansible for State Management]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/16-Docker Modules in Ansible for State Management/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/07-Configuration Management (Ansible)/16-Docker Modules in Ansible for State Management/05-Practice Questions & Answers|Practice Questions & Answers]]
