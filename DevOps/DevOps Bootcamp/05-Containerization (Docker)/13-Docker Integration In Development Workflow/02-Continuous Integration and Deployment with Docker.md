---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Continuous Integration and Deployment with Docker

### Introduction to Continuous Integration (CI)

Continuous Integration (CI) is a development practice where developers frequently integrate their code into a shared repository, typically several times a day. Each integration is verified by an automated build and tests to detect integration errors as quickly as possible. This helps teams identify and resolve bugs early, reducing the time and cost associated with fixing issues later in the development cycle.

In the context of modern DevOps practices, CI is often integrated with Continuous Delivery (CD) and Continuous Deployment (CDeploy). These practices ensure that code changes can be reliably released to production at any time, with minimal manual intervention.

### Jenkins and CI

Jenkins is a widely used open-source automation server that provides extensive support for implementing CI/CD pipelines. Jenkins allows developers to automate the building, testing, and deployment of applications. When a change is made to the codebase, Jenkins can automatically trigger a build process, run tests, and deploy the application if the tests pass.

#### Jenkins Build Process

When a Jenkins build is triggered, it performs the following steps:

1. **Checkout Code**: Retrieves the latest code from the version control system (VCS).
2. **Build Application**: Compiles the code and generates the necessary artifacts.
3. **Run Tests**: Executes unit tests, integration tests, and other types of tests to ensure the code works as expected.
4. **Generate Artifacts**: Creates deployable artifacts such as JAR files, WAR files, or Docker images.

### Building a JavaScript Application

In the given scenario, the application is a JavaScript application. The build process for a JavaScript application typically involves the following steps:

1. **Install Dependencies**: Using `npm` or `yarn`, install all the required dependencies specified in the `package.json` file.
2. **Compile Source Code**: Transpile the source code using tools like Babel to ensure compatibility across different environments.
3. **Run Linters and Formatters**: Use tools like ESLint to check for coding standards and formatting issues.
4. **Run Unit Tests**: Execute unit tests to verify the correctness of the code.

Here is an example of a `package.json` file and a `Dockerfile` for a JavaScript application:

```json
{
  "name": "my-javascript-app",
  "version": "1.0.0",
  "scripts": {
    "start": "node index.js",
    "build": "npm install && npm run lint && npm run test",
    "lint": "eslint .",
    "test": "jest"
  },
  "dependencies": {
    "express": "^4.17.1",
    "mongodb": "^3.6.4"
  },
  "devDependencies": {
    "eslint": "^7.32.0",
    "jest": "^26.6.3"
  }
}
```

```dockerfile
# Dockerfile
FROM node:14-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

CMD ["npm", "run", "start"]
```

### Creating a Docker Image

Once the JavaScript application is built, the next step is to create a Docker image. Docker allows you to package the application along with its dependencies into a lightweight, portable container. This ensures consistency across different environments and simplifies deployment.

The `Dockerfile` specifies the base image, copies the application code, installs dependencies, and sets the entry point for the application.

### Pushing Docker Images to a Private Repository

After creating the Docker image, it needs to be pushed to a private Docker repository. A private repository is essential for maintaining the confidentiality and integrity of the application's components. Common private repositories include Docker Hub (with private repositories), Amazon ECR, and Google Container Registry.

#### Example of Pushing to Docker Hub

To push the Docker image to Docker Hub, you need to tag the image with your Docker Hub username and repository name, and then push it.

```bash
docker tag my-javascript-app:latest <username>/my-javascript-app:latest
docker push <username>/my-javascript-app:latest
```

### Deploying Docker Images to a Development Server

Once the Docker image is pushed to the private repository, it can be deployed to a development server. The development server pulls the image from the private repository and runs it as a container.

#### Example of Pulling and Running Containers

```bash
docker pull <username>/my-javascript-app:latest
docker run -d --name my-javascript-app -p 3000:3000 <username>/my-javascript-app:latest
```

Additionally, the development server also needs to pull the MongoDB container from Docker Hub and run it alongside the application container.

```bash
docker pull mongo:latest
docker run -d --name mongodb -p 27017:27017 mongo:latest
```

### Configuring Communication Between Containers

For the application and MongoDB containers to communicate, they need to be connected via a network. Docker provides networking capabilities to facilitate communication between containers.

#### Example of Connecting Containers

```bash
docker network create my-network
docker run -d --name my-javascript-app --network my-network -p 3000:3000 <username>/my-javascript-app:latest
docker run -d --name mongodb --network my-network -p 27017:27017 mongo:latest
```

### Testing the Application

Once the containers are up and running, testers or developers can log in to the development server and test the application. This ensures that the application behaves as expected in a controlled environment before being deployed to production.

### Real-World Examples and Security Considerations

#### Recent CVEs and Breaches

One notable breach involving Docker was the **CVE-2019-14287** vulnerability in Docker for Mac, which allowed attackers to escape the container and gain root access to the host machine. This highlights the importance of keeping Docker and related tools up to date and applying security patches promptly.

#### Secure Coding Practices

To prevent such vulnerabilities, it is crucial to follow secure coding practices and implement proper security measures. Here are some best practices:

1. **Use Non-root Users**: Avoid running containers as root users. Use non-root users to reduce the attack surface.
2. **Limit Capabilities**: Use the `--cap-drop` option to limit the capabilities of the container.
3. **Network Isolation**: Use Docker networks to isolate containers and restrict unnecessary network traffic.
4. **Regular Updates**: Keep Docker and all dependencies up to date with the latest security patches.

#### Secure Configuration Example

Here is an example of a secure `Dockerfile` and `docker-compose.yml`:

```dockerfile
# Dockerfile
FROM node:14-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

USER node
CMD ["npm", "run", "start"]
```

```yaml
# docker-compose.yml
version: '3'
services:
  app:
    image: <username>/my-javascript-app:latest
    user: node
    ports:
      - "3000:3000"
    networks:
      - my-network
  db:
    image: mongo:latest
    ports:
      - "27017:27017"
    networks:
      - my-network
networks:
  my-network:
```

### Hands-On Labs

To get hands-on experience with Docker integration in a development workflow, consider the following labs:

- **PortSwigger Web Security Academy**: Offers practical exercises on securing web applications.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.
- **WebGoat**: An interactive, gamified training application for learning about web application security.

These labs provide a comprehensive environment to practice and understand the concepts discussed in this chapter.

### Conclusion

Integrating Docker into a development workflow significantly enhances the efficiency and reliability of the development process. By automating the build, test, and deployment processes, developers can focus on writing high-quality code while ensuring that the application remains secure and functional. Following best practices and using secure configurations can help mitigate potential vulnerabilities and ensure a robust development environment.

---
<!-- nav -->
[[01-Introduction to Docker Integration in Development Workflow|Introduction to Docker Integration in Development Workflow]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/13-Docker Integration In Development Workflow/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/13-Docker Integration In Development Workflow/03-Practice Questions & Answers|Practice Questions & Answers]]
