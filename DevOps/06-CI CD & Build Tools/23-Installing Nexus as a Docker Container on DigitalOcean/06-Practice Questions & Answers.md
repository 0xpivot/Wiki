---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the advantages of deploying Nexus as a Docker container compared to installing it directly on a DigitalOcean droplet.**

Nexus deployed as a Docker container offers several advantages over direct installation:

1. **Ease of Setup**: With Docker, you only need to install Docker runtime and pull the Nexus image. Direct installation requires setting up Java, downloading and unpacking the Nexus package, creating a user, configuring permissions, and starting the service manually.
   
2. **Portability**: Docker containers are portable across different environments, making it easier to move Nexus between development, testing, and production environments.
   
3. **Resource Management**: Docker allows better resource management and isolation, ensuring that Nexus does not interfere with other applications running on the same server.
   
4. **Maintenance**: Updating Nexus in a Docker environment is simpler; you can simply pull a new image and restart the container. In contrast, updating a directly installed Nexus involves downloading new packages, stopping the service, and restarting it.

**Q2. How would you configure a Docker container to ensure Nexus persists its data even after the container is stopped and restarted?**

To ensure Nexus persists its data even after the container is stopped and restarted, you need to configure Docker volumes. Here’s how:

1. **Create a Docker Volume**: Use the `docker volume create` command to create a named volume. For example:
   ```bash
   docker volume create nexus-data
   ```

2. **Run the Nexus Container with Volume Mount**: When running the Nexus container, mount the created volume to the appropriate directory within the container. For example:
   ```bash
   docker run -d -p 8081:8081 --name nexus -v nexus-data:/nexus-data sonatype/nexus3
   ```
   This command maps the `/nexus-data` directory inside the container to the `nexus-data` volume on the host, ensuring that Nexus data is stored persistently.

**Q3. Why is it important to run Nexus inside a Docker container with a non-root user? Provide an example of how this is achieved.**

Running Nexus inside a Docker container with a non-root user is important for security reasons. Running services as root increases the risk of privilege escalation attacks. By using a non-root user, you limit the potential damage that could be caused by vulnerabilities in the service.

In the context of the Nexus Docker image, this is achieved by default. The Dockerfile for the Nexus image specifies a user named `nexus`. You can verify this by inspecting the Docker image layers or checking the documentation. For example:

```bash
docker inspect sonatype/nexus3
```

This command will show the user settings within the image, confirming that the `nexus` user is used to run the service.

**Q4. How would you troubleshoot a situation where the Nexus Docker container is not accessible via its mapped port?**

To troubleshoot a situation where the Nexus Docker container is not accessible via its mapped port, follow these steps:

1. **Check if the Container is Running**: Use `docker ps` to confirm that the container is running.
   
2. **Verify Port Mapping**: Ensure that the correct port mapping is specified when running the container. For example:
   ```bash
   docker run -d -p 8081:8081 --name nexus sonatype/nexus3
   ```
   Confirm that the container is listening on the expected port inside the container.

3. **Check Firewall Rules**: Verify that the firewall rules on the DigitalOcean droplet allow traffic on the mapped port (e.g., 8081).

4. **Inspect Network Configuration**: Use `docker inspect <container_id>` to inspect the network configuration of the container and ensure that the port is correctly exposed.

5. **Test Connectivity**: From the host machine, try to connect to the port using tools like `curl` or `telnet` to ensure that the service is reachable:
   ```bash
   curl http://localhost:8081
   ```

6. **Check Logs**: Review the logs of the container using `docker logs <container_id>` to identify any errors or issues that might prevent the service from starting correctly.

**Q5. What are the steps to perform a backup of Nexus data when it is deployed as a Docker container?**

To perform a backup of Nexus data when it is deployed as a Docker container, follow these steps:

1. **Identify the Volume Path**: Determine the physical path on the host where the Docker volume is mounted. Use `docker volume inspect nexus-data` to get the details of the volume, including the mount point.

2. **Copy the Data**: Copy the contents of the volume to a backup location. For example:
   ```bash
   cp -r /var/lib/docker/volumes/nexus-data/_data /path/to/backup/location
   ```

3. **Verify the Backup**: Check that the backup contains all necessary Nexus data and configurations.

4. **Automate the Process**: Consider automating the backup process using scripts or tools like `cron` jobs to ensure regular backups.

By following these steps, you can ensure that Nexus data is safely backed up, even when deployed as a Docker container.

---
<!-- nav -->
[[05-Understanding Docker Containers and Volumes|Understanding Docker Containers and Volumes]] | [[DevOps/DevOps Bootcamp/06-CI CD & Build Tools/23-Installing Nexus as a Docker Container on DigitalOcean/00-Overview|Overview]]
