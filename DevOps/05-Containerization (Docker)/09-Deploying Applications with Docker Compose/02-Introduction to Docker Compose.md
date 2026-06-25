---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Docker Compose

Docker Compose is a tool for defining and running multi-container Docker applications. With Compose, you can create a `docker-compose.yml` file to configure your application’s services. Then, using a single command, you can create and start all the services from your configuration. This makes it easier to manage complex applications that require multiple containers to function properly.

### What is Docker Compose?

Docker Compose is a tool that allows you to define and run multi-container Docker applications. It uses a YAML file (`docker-compose.yml`) to describe the services, networks, and volumes that make up your application. This file contains all the necessary information to set up and run your application in a consistent and reproducible manner.

#### Why Use Docker Compose?

1. **Consistency**: Docker Compose ensures that your application runs consistently across different environments (development, testing, production).
2. **Ease of Use**: It simplifies the process of managing multiple containers, making it easier to start, stop, and scale your application.
3. **Reproducibility**: By defining your application in a YAML file, you ensure that anyone can set up the same environment by simply running `docker-compose up`.

### How Docker Compose Works

When you run `docker-compose up`, Docker Compose reads the `docker-compose.yml` file and starts all the services defined in it. Each service corresponds to a container, and Docker Compose manages the dependencies between these containers.

#### Example `docker-compose.yml` File

```yaml
version: '3'
services:
  myapp:
    image: ewsdocker/myapp:1.0
    ports:
      - "8080:80"
    depends_on:
      - mongodb
      - mongo-express
  mongodb:
    image: mongo:latest
    volumes:
      - ./data:/data/db
  mongo-express:
    image: mongo-express:latest
    ports:
      - "8081:8081"
    environment:
      ME_CONFIG_MONGODB_URL: mongodb://mongodb:27017/
```

### Components of a `docker-compose.yml` File

1. **Version**: Specifies the version of the Docker Compose file format.
2. **Services**: Defines the services that make up your application.
3. **Image**: Specifies the Docker image to use for the service.
4. **Ports**: Maps ports from the host to the container.
5. **Depends On**: Specifies the dependencies between services.
6. **Volumes**: Mounts volumes from the host to the container.
7. **Environment**: Sets environment variables for the container.

### Deploying an Application with Docker Compose

Let's walk through the process of deploying an application using Docker Compose. We'll assume you have already built and pushed your Docker images to a private repository.

#### Step 1: Define Your Services

First, you need to define the services that make up your application. In our example, we have three services: `myapp`, `mongodb`, and `mongo-express`.

```yaml
version: '3'
services:
  myapp:
    image: ewsdocker/myapp:1.0
    ports:
      - "8080:80"
    depends_on:
      - mongodb
      - mongo-express
  mongodb:
    image: mongo:latest
    volumes:
      - ./data:/data/db
  mongo-express:
    image: mongo-express:latest
    ports:
      - "8081:8081"
    environment:
      ME_CONFIG_MONGODB_URL: mongodb://mongodb:27017/
```

#### Step 2: Pull the Images

Before starting the services, Docker Compose will pull the required images from the specified repositories. In our case, `myapp` will be pulled from the private repository `ewsdocker`, and `mongodb` and `mongo-express` will be pulled from Docker Hub.

#### Step 3: Start the Services

Run the following command to start the services:

```sh
docker-compose up
```

This command will start all the services defined in the `docker-compose.yml` file. Docker Compose will handle the dependencies and ensure that the services are started in the correct order.

### Real-World Example: Recent Breaches

In recent years, there have been several high-profile breaches involving Docker and containerized applications. One notable example is the 2021 breach of a Docker registry, which exposed sensitive data and allowed unauthorized access to Docker images.

#### CVE-2021-29427

CVE-2021-29427 is a vulnerability in Docker that allows attackers to bypass authentication and gain unauthorized access to Docker registries. This vulnerability highlights the importance of securing your Docker environment and ensuring that your images are properly protected.

#### Secure Coding Practices

To prevent such vulnerabilities, it is crucial to follow secure coding practices and implement proper security measures. Here are some best practices:

1. **Use Strong Authentication**: Ensure that your Docker registry uses strong authentication mechanisms, such as TLS and mutual authentication.
2. **Limit Access**: Restrict access to your Docker images and ensure that only authorized users can pull and push images.
3. **Regular Audits**: Perform regular audits of your Docker environment to identify and mitigate potential security risks.

### How to Prevent / Defend

#### Detection

To detect potential security issues in your Docker environment, you can use tools such as Trivy, Clair, and Aqua Security. These tools scan your Docker images for known vulnerabilities and provide detailed reports.

#### Prevention

To prevent security issues, follow these steps:

1. **Secure Your Registry**: Use a secure Docker registry and ensure that it is properly configured with strong authentication mechanisms.
2. **Use Secure Images**: Use trusted and verified Docker images from reputable sources.
3. **Implement Network Policies**: Use network policies to restrict communication between containers and limit exposure to external threats.

#### Secure-Coding Fixes

Here is an example of a vulnerable `docker-compose.yml` file and its secure counterpart:

**Vulnerable Version**

```yaml
version: '3'
services:
  myapp:
    image: ewsdocker/myapp:1.0
    ports:
      - "8080:80"
    depends_on:
      - mongodb
      - mongo-express
  mongodb:
    image: mongo:latest
    volumes:
      - ./data:/data/db
  mongo-express:
    image: mongo-express:latest
    ports:
      - "8081:8081"
    environment:
      ME_CONFIG_MONGODB_URL: mongodb://mongodb:27017/
```

**Secure Version**

```yaml
version: '3'
services:
  myapp:
    image: ewsdocker/myapp:1.0
    ports:
      - "8080:80"
    depends_on:
      - mongodb
      - mongo-express
    environment:
      - APP_SECRET=your_secret_key
  mongodb:
    image: mongo:latest
    volumes:
      - ./data:/data/db
    environment:
      - MONGO_INITDB_ROOT_USERNAME=root
      - MONGO_INITDB_ROOT_PASSWORD=your_password
  mongo-express:
    image: mongo-express:latest
    ports:
      - "8081:8081"
    environment:
      ME_CONFIG_MONGODB_URL: mongodb://root:your_password@mongodb:27017/
```

### Complete Example: Full HTTP Request and Response

Here is a complete example of a full HTTP request and response for deploying an application using Docker Compose:

#### HTTP Request

```http
POST /v1.41/containers/create HTTP/1.1
Host: localhost:2375
Content-Type: application/json

{
  "Image": "ewsdocker/myapp:1.0",
  "ExposedPorts": {
    "80/tcp": {}
  },
  "Env": [
    "APP_SECRET=your_secret_key"
  ]
}
```

#### HTTP Response

```http
HTTP/1.1 201 Created
Content-Type: application/json

{
  "Id": "container_id",
  "Warnings": null
}
```

### Mermaid Diagrams

#### Service Architecture

```mermaid
graph TD
  A[Development Server] --> B[MyApp Container]
  A --> C[MongoDB Container]
  A --> D[MongoExpress Container]
  B --> C
  B --> D
```

#### Request/Response Flow

```mermaid
sequenceDiagram
  participant User
  participant DockerCompose
  participant MyAppContainer
  participant MongoDBContainer
  participant MongoExpressContainer

  User->>DockerCompose: docker-compose up
  DockerCompose->>MyAppContainer: Start MyApp
  DockerCompose->>MongoDBContainer: Start MongoDB
  DockerCompose->>MongoExpressContainer: Start MongoExpress
  MyAppContainer->>MongoDBContainer: Connect to MongoDB
  MyAppContainer->>MongoExpressContainer: Connect to MongoExpress
```

### Practice Labs

For hands-on practice with Docker Compose, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a series of labs that cover various aspects of web application security, including Docker and containerization.
- **OWASP Juice Shop**: A deliberately insecure web application that teaches web security principles. It includes a Docker Compose setup for easy deployment.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for learning web security. It also supports Docker Compose for deployment.

By following these steps and best practices, you can effectively deploy and manage your applications using Docker Compose while ensuring the security and consistency of your environment.

---
<!-- nav -->
[[01-Introduction to Docker Compose and Network Management|Introduction to Docker Compose and Network Management]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/09-Deploying Applications with Docker Compose/00-Overview|Overview]] | [[03-Deploying Applications with Docker Compose|Deploying Applications with Docker Compose]]
