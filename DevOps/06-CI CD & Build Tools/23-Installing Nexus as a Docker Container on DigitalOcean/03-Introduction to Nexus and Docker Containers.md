---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Nexus and Docker Containers

Nexus Repository Manager is a powerful tool used in DevOps environments to manage artifacts such as binaries, libraries, and other dependencies. It provides a centralized repository for storing and distributing these artifacts, making it easier to manage and share them across development teams. In this chapter, we will focus on installing Nexus as a Docker container on DigitalOcean, a popular cloud platform.

### Why Use Docker?

Docker is a containerization technology that allows developers to package applications and their dependencies into lightweight, portable containers. These containers can run consistently across different environments, ensuring that the application behaves the same way whether it is running locally on a developer's machine or in a production environment.

Using Docker for deploying Nexus offers several advantages:

1. **Portability**: Docker containers are highly portable and can run on any system that supports Docker, including local machines, virtual machines, and cloud platforms like DigitalOcean.
2. **Consistency**: Docker ensures that the application runs the same way in all environments, reducing the risk of "works on my machine" issues.
3. **Isolation**: Each Docker container runs in isolation, minimizing conflicts between different applications and services.
4. **Efficiency**: Docker containers are more efficient than traditional virtual machines, as they share the host operating system kernel and require fewer resources.

### Setting Up Nexus as a Docker Container

To set up Nexus as a Docker container on DigitalOcean, you need to follow these steps:

1. **Install Docker Runtime**: First, ensure that Docker is installed on your DigitalOcean droplet. You can install Docker using the following commands:

    ```sh
    sudo apt-get update
    sudo apt-get install -y docker.io
    ```

2. **Pull the Nexus Docker Image**: Next, pull the Nexus Docker image from Docker Hub. You can use the following command to pull the latest version of the Nexus image:

    ```sh
    docker pull sonatype/nexus3
    ```

3. **Run the Nexus Docker Container**: Once the image is pulled, you can run the container using the `docker run` command. Here is an example command to start the Nexus container:

    ```sh
    docker run -d -p 8081:8081 --name nexus sonatype/nexus3
    ```

    This command does the following:
    - `-d`: Runs the container in detached mode.
    - `-p 8081:8081`: Maps port 8081 of the container to port 8081 of the host.
    - `--name nexus`: Names the container `nexus`.
    - `sonatype/nexus3`: Specifies the Docker image to use.

### Running Services as Non-Root Users

It is a best practice to run services within Docker containers as non-root users. Running services as the root user increases the risk of privilege escalation attacks and other security vulnerabilities.

#### Creating a Non-Root User

In the Nexus Docker image, a non-root user named `nexus` is created by default. This user is used to run the Nexus service within the container. To verify this, you can enter the container's shell and check the current user:

```sh
docker ps
```

Take the container ID from the output and enter the shell:

```sh
docker exec -it <container_id> /bin/sh
```

Once inside the container, you should see a `$` prompt, indicating that you are running as the `nexus` user:

```sh
$ whoami
nexus
```

### Understanding the Dockerfile

The behavior of the Docker container, including the creation of the `nexus` user, is defined in the Dockerfile used to build the image. You can inspect the Dockerfile by looking at the image layers. To view the image layers, you can use the `docker history` command:

```sh
docker history sonatype/nexus3
```

This command will display the layers of the Docker image, showing the commands executed during the build process. You can see the creation of the `nexus` user in the output:

```sh
IMAGE               CREATED             CREATED BY                                      SIZE                COMMENT
<image_id>          2 days ago          /bin/sh -c #(nop) USER nexus                   0B
```

### Security Implications of Running as Root

Running services as the root user within a Docker container poses significant security risks. If an attacker gains access to a service running as root, they can potentially escalate their privileges and compromise the entire system.

#### Real-World Example: CVE-2021-21287

A real-world example of the risks associated with running services as root is the CVE-2021-21287 vulnerability in Docker. This vulnerability allowed attackers to escape the container and gain root access to the host system. The vulnerability was caused by a flaw in the Docker daemon that allowed unprivileged users to execute arbitrary code with elevated privileges.

### How to Prevent / Defend Against Running Services as Root

To prevent services from running as root within Docker containers, follow these best practices:

1. **Use Non-Root Users**: Always create and use non-root users for running services within Docker containers. This reduces the risk of privilege escalation attacks.
2. **Audit Docker Images**: Regularly audit Docker images to ensure that they are configured to run services as non-root users. You can use tools like `docker history` to inspect the image layers and verify the user settings.
3. **Implement Security Policies**: Implement security policies that enforce the use of non-root users for running services within Docker containers. This can be achieved through automated CI/CD pipelines that check and enforce these policies.

#### Secure Coding Practices

Here is an example of how to modify a Dockerfile to ensure that a service runs as a non-root user:

**Vulnerable Dockerfile:**

```Dockerfile
FROM ubuntu:latest
RUN apt-get update && apt-get install -y my-service
CMD ["my-service"]
```

**Secure Dockerfile:**

```Dockerfile
FROM ubuntu:latest
RUN apt-get update && apt-get install -y my-service
RUN groupadd -r mygroup && useradd -r -g mygroup myuser
USER myuser
CMD ["my-service"]
```

In the secure Dockerfile, a non-root user `myuser` is created and used to run the service.

### Conclusion

In this chapter, we covered the process of installing Nexus as a Docker container on DigitalOcean, emphasizing the importance of running services as non-root users for enhanced security. We explored the benefits of using Docker, the steps to set up Nexus, and the security implications of running services as root. By following best practices and implementing secure coding practices, you can ensure that your Docker containers are secure and reliable.

### Practice Labs

For hands-on experience with setting up Nexus as a Docker container, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive course on web security, including sections on Docker and container security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training, which includes exercises on Docker and container management.
- **DigitalOcean Tutorials**: DigitalOcean provides detailed tutorials and guides on setting up Docker containers, including Nexus.

By completing these labs, you can gain practical experience in deploying and securing Nexus as a Docker container.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/23-Installing Nexus as a Docker Container on DigitalOcean/02-Introduction to Nexus Repository Manager|Introduction to Nexus Repository Manager]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/23-Installing Nexus as a Docker Container on DigitalOcean/00-Overview|Overview]] | [[04-Creating a Docker Volume|Creating a Docker Volume]]
