---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. What are the key differences between Docker containers and virtual machines?**

Docker containers and virtual machines both provide isolated environments for running applications, but they differ in several key aspects:

- **Resource Usage**: Virtual machines require a full operating system to run, which consumes more resources. Docker containers share the host OS kernel, making them much lighter and more resource-efficient.
  
- **Boot Time**: Virtual machines take longer to boot because they need to initialize a full operating system. Docker containers, on the other hand, can start almost instantly since they only need to load the necessary components of the host OS.

- **Portability**: Both Docker and VMs allow for portable applications, but Docker containers are generally easier to move across different hosts due to their smaller size and simpler setup requirements.

- **Isolation**: Virtual machines offer stronger isolation because each VM has its own OS and hardware abstraction layer. Docker containers share the same OS kernel, so isolation is less strict but still effective for most use cases.

**Q2. How do you build a custom Docker image using a Dockerfile?**

To build a custom Docker image using a Dockerfile, follow these steps:

1. Create a `Dockerfile` in your project directory. The `Dockerfile` specifies the base image, any additional packages or dependencies, and the command to run the application.

```dockerfile
# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME World

# Run app.py when the container launches
CMD ["python", "app.py"]
```

2. Build the Docker image using the `docker build` command:

```bash
docker build -t my-app .
```

This command tells Docker to build an image named `my-app` from the `Dockerfile` in the current directory (`.`).

3. Once the image is built, you can run it using the `docker run` command:

```bash
docker run -p 4000:80 my-app
```

This command maps port 80 inside the container to port 4000 on the host machine and starts the container.

**Q3. Explain how Docker volumes work and why they are important for persistent storage.**

Docker volumes provide a way to store data that persists beyond the lifetime of a container. They are managed by Docker and can be shared and reused among containers. Here’s how they work:

- **Data Persistence**: When a container is deleted, any data written to the container's writable layer is lost. Docker volumes solve this problem by providing a dedicated space for data that can be mounted to one or more containers.

- **Volume Types**: There are two types of volumes in Docker:
  - **Named Volumes**: These are created and managed by Docker. You can create a named volume using the `docker volume create` command.
  - **Bind Mounts**: These mount a file or directory from the host filesystem into the container. Bind mounts are useful for development purposes but may not be suitable for production environments.

- **Usage Example**: Suppose you have a database container that needs to store its data persistently. You can use a named volume to store the database files:

```bash
docker volume create dbdata
docker run -d --name some-mysql -v dbdata:/var/lib/mysql mysql:latest
```

In this example, the `dbdata` volume is mounted to `/var/lib/mysql` in the MySQL container, ensuring that the database files are stored persistently.

**Q4. How can you use Docker Compose to manage multiple services in a single application?**

Docker Compose is a tool for defining and running multi-container Docker applications. It uses a YAML file to configure the services, networks, and volumes required by the application. Here’s how you can use Docker Compose:

1. **Create a `docker-compose.yml` file**: This file defines the services, networks, and volumes for your application. For example:

```yaml
version: '3'
services:
  web:
    build: ./web
    ports:
      - "8000:8000"
  redis:
    image: "redis:alpine"
```

In this example, there are two services: `web` and `redis`. The `web` service is built from a `Dockerfile` located in the `./web` directory, and it exposes port 8000. The `redis` service uses the `redis:alpine` image.

2. **Build and run the services**: Use the `docker-compose` command to build and run the services defined in the `docker-compose.yml` file:

```bash
docker-compose up --build
```

This command builds the images if necessary and starts the services.

3. **Manage the services**: Docker Compose provides commands to manage the services, such as stopping, restarting, and scaling them:

```bash
docker-compose stop
docker-compose restart
docker-compose scale web=3
```

These commands stop all services, restart all services, and scale the `web` service to three replicas, respectively.

**Q5. Describe how you would set up a private Docker registry using Nexus Repository Manager.**

Nexus Repository Manager is a powerful tool for managing repositories, including Docker registries. Here’s how you can set up a private Docker registry using Nexus:

1. **Install Nexus**: Download and install Nexus Repository Manager on a server. Ensure that the server has Docker installed and running.

2. **Deploy Nexus as a Docker container**: Use Docker to run Nexus as a container:

```bash
docker run -d -p 8081:8081 -p 8082:8082 -p 8083:8083 --name nexus sonatype/nexus3
```

This command runs Nexus on ports 8081, 8082, and 8083.

3. **Configure Nexus for Docker**: Log in to the Nexus UI and configure a new Docker Hosted repository:
   - Go to `Repositories` > `Create repository`.
   - Select `Docker Hosted` and fill in the details, such as the name and HTTP port.
   - Save the configuration.

4. **Push Docker images to the Nexus registry**: Tag and push your Docker images to the Nexus registry:

```bash
docker tag my-app localhost:8081/my-app
docker push localhost:8081/my-app
```

This command tags the local `my-app` image with the Nexus registry URL and pushes it to the Nexus repository.

5. **Fetch Docker images from the Nexus registry**: Pull images from the Nexus registry:

```bash
docker pull localhost:8081/my-app
```

This command pulls the `my-app` image from the Nexus registry.

By following these steps, you can set up a private Docker registry using Nexus Repository Manager, enabling you to manage and distribute Docker images securely within your organization.

---
<!-- nav -->
[[DevOps/DevOps Bootcamp/05-Containerization (Docker)/06-Docker Containers Fundamentals And Practical Use/08-Conclusion|Conclusion]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/06-Docker Containers Fundamentals And Practical Use/00-Overview|Overview]]
