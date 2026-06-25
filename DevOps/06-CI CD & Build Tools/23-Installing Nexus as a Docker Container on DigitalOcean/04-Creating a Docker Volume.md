---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Creating a Docker Volume

When deploying applications in a containerized environment, it is crucial to manage persistent storage effectively. One of the ways to achieve this is by creating a Docker volume. A Docker volume is a mechanism for persistently storing data outside of the container’s writable layer. This ensures that even if the container is stopped or removed, the data remains intact.

### Why Use Docker Volumes?

Docker volumes provide several benefits:

1. **Persistence**: Data stored in a volume persists even after the container is deleted.
2. **Portability**: Volumes can be easily shared between containers.
3. **Efficiency**: Volumes are more efficient than bind mounts, especially when dealing with large amounts of data.

### Creating a Docker Volume

To create a Docker volume, you can use the `docker volume create` command. In the given context, we are creating a volume named `NexusData`.

```bash
docker volume create NexusData
```

This command creates a new volume named `NexusData`. Docker will manage the underlying storage for this volume, ensuring that the data is persisted even if the container is removed.

### Mounting the Volume in a Docker Container

Once the volume is created, it can be mounted into a Docker container using the `-v` flag in the `docker run` command. This allows the container to access the persistent storage provided by the volume.

#### Example: Running Nexus in a Docker Container

Let's run a Nexus container and mount the `NexusData` volume into it.

```bash
docker run -d --name nexus -p 8081:8081 -v NexusData:/nexus-data sonatype/nexus3
```

Here's a breakdown of the command:

- `-d`: Run the container in detached mode (in the background).
- `--name nexus`: Assign a name (`nexus`) to the container.
- `-p 8081:8081`: Map port 8081 on the host to port 8081 in the container.
- `-v NexusData:/nexus-data`: Mount the `NexusData` volume to `/nexus-data` in the container.
- `sonatype/nexus3`: Use the `sonatype/nexus3` Docker image.

### Verifying the Container and Port

After starting the container, you can verify that it is running and that the port is open using the `docker ps` and `netstat` commands.

#### Checking the Running Containers

```bash
docker ps
```

This command lists all running containers. You should see the `nexus` container listed.

#### Checking Open Ports

To check if the port is open, you can use the `netstat` command.

```bash
sudo apt-get update
sudo apt-get install net-tools
netstat -tuln | grep 8081
```

The `netstat` command shows all listening ports. The output should indicate that port 8081 is open.

### Accessing the Nexus Repository UI

Finally, you can access the Nexus Repository UI by navigating to the IP address of your server followed by the port number (8081).

```plaintext
http://<server-ip>:8081
```

### Diagram: Docker Volume and Container Architecture

```mermaid
graph LR
    A[Host System] --> B[Docker Volume (NexusData)]
    C[Docker Container (nexus)] --> D[Mount Point (/nexus-data)]
    B --> D
    E[HTTP Request] --> C
    C --> F[Response]
```

### Common Pitfalls and How to Prevent Them

#### Pitfall: Incorrect Volume Mounting

If the volume is not correctly mounted, the container may not have access to the persistent storage. Ensure that the volume name and mount point are correct.

**Vulnerable Code:**

```bash
docker run -d --name nexus -p 8081:8081 -v NexusData:/wrong-path sonatype/nexus3
```

**Secure Code:**

```bash
docker run -d --name nexus -p 8081:8081 -v NexusData:/nexus-data sonatype/nexus3
```

#### Pitfall: Port Mapping Issues

If the port mapping is incorrect, the container may not be accessible from the host. Ensure that the correct ports are mapped.

**Vulnerable Code:**

```bash
docker run -d --name nexus -p 8081:8080 -v NexusData:/nexus-data sonatype/nexus3
```

**Secure Code:**

```bash
docker run -d --name nexus -p  8081:8081 -v NexusData:/nexus-data sonatype/nexus3
```

### Real-World Examples and CVEs

#### Example: CVE-2021-21277

In 2021, Sonatype Nexus Repository Manager was found to have a critical vulnerability (CVE-2021-21277) that could allow remote code execution. This vulnerability highlights the importance of keeping your container images and configurations up-to-date.

**Detection:**

Regularly scan your Docker images for vulnerabilities using tools like Trivy or Clair.

**Prevention:**

1. **Keep Images Updated**: Regularly update the Docker images used in your deployments.
2. **Use Secure Configurations**: Follow best practices for securing Docker containers and volumes.
3. **Monitor and Audit**: Continuously monitor your container environments for suspicious activity.

### Hands-On Labs

For practical experience with deploying Nexus as a Docker container, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to web application security, including containerization and deployment.
- **OWASP Juice Shop**: A deliberately insecure web application for security training purposes. While not specifically focused on Docker, it provides a good environment to practice container management.
- **DigitalOcean Tutorials**: DigitalOcean offers detailed tutorials and guides on deploying various services, including Nexus, in a Docker environment.

By following these steps and best practices, you can ensure that your Nexus deployment is both functional and secure.

---
<!-- nav -->
[[03-Introduction to Nexus and Docker Containers|Introduction to Nexus and Docker Containers]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/23-Installing Nexus as a Docker Container on DigitalOcean/00-Overview|Overview]] | [[05-Understanding Docker Containers and Volumes|Understanding Docker Containers and Volumes]]
