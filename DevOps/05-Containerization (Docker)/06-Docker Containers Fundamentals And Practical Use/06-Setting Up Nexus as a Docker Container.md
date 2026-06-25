---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Setting Up Nexus as a Docker Container

### Prerequisites

Before setting up Nexus as a Docker container, ensure you have the following:

1. **Docker Installed**: Make sure Docker is installed on your machine. You can check this by running `docker --version`.
2. **Docker Compose (Optional)**: Docker Compose is useful for managing multi-container applications. Install it if you plan to use it.

### Step-by-Step Guide

#### Step 1: Pull the Nexus Docker Image

First, pull the Nexus Docker image from Docker Hub:

```bash
docker pull sonatype/nexus3
```

This command downloads the latest version of the Nexus Docker image.

#### Step 2: Run the Nexus Docker Container

Next, run the Nexus Docker container:

```bash
docker run -d -p 8081:8081 -p 8082:8082 --name nexus sonatype/nexus3
```

Here’s a breakdown of the command:

- `-d`: Runs the container in detached mode (in the background).
- `-p 8081:8081`: Maps port 8081 on the host to port 8081 on the container. This is the default HTTP port for Nexus.
- `-p 8082:8082`: Maps port 8082 on the host to port 8082 on the container. This is the default HTTPS port for Nexus.
- `--name nexus`: Names the container `nexus`.

#### Step 3: Access Nexus

Once the container is running, you can access Nexus by navigating to `http://localhost:8081` in your web browser. The initial login credentials are:

- Username: `admin`
- Password: `admin123`

#### Step 4: Configure Nexus

After logging in, you may want to configure Nexus according to your needs. This includes setting up repositories, configuring security, and managing access control.

### Diagram: Nexus as a Docker Container

```mermaid
graph LR
    A[Host Machine] --> B[Docker Engine]
    B --> C[Docker Container (Nexus)]
    C --> D[Nexus Web Interface]
```

### Common Pitfalls and How to Prevent Them

#### Pitfall 1: Incorrect Port Mapping

**Problem**: If you map the wrong ports, you won’t be able to access Nexus through the correct URL.

**Solution**: Always double-check the port mappings in your `docker run` command. Ensure that the ports on the host match the ports on the container.

#### Pitfall 2: Insufficient Disk Space

**Problem**: Running out of disk space can cause Nexus to fail.

**Solution**: Monitor disk usage and ensure that there is enough free space on the host machine. You can also configure Nexus to use an external storage volume.

### How to Prevent / Defend

#### Detection

- **Log Monitoring**: Regularly monitor logs for errors related to disk space or port mapping issues.
- **Health Checks**: Use health checks to ensure that the Nexus container is running correctly.

#### Prevention

- **Resource Allocation**: Allocate sufficient resources (CPU, memory, disk space) to the Docker container.
- **Regular Backups**: Implement regular backups of Nexus data to prevent data loss.

---
<!-- nav -->
[[06-Real-World Examples and Recent CVEs|Real-World Examples and Recent CVEs]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/06-Docker Containers Fundamentals And Practical Use/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/06-Docker Containers Fundamentals And Practical Use/08-Conclusion|Conclusion]]
