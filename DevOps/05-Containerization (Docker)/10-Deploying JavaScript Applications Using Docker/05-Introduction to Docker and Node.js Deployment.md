---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Docker and Node.js Deployment

In this section, we will delve into deploying a JavaScript application using Docker, focusing on the nuances of Dockerfile creation and the differences between `RUN` and `CMD` commands. We'll start by explaining the basics of Docker and Node.js, then move on to creating a Dockerfile for a Node.js application, and finally discuss best practices and potential pitfalls.

### What is Docker?

Docker is a platform that allows developers to package their applications into lightweight, portable containers. Containers encapsulate an application along with its dependencies, ensuring consistent behavior across different environments. This is achieved through the use of Docker images, which are essentially snapshots of the application environment.

#### Why Use Docker?

1. **Consistency**: Docker ensures that the application runs the same way in development, testing, and production environments.
2. **Portability**: Docker containers can run on any system that supports Docker, making deployment easier.
3. **Isolation**: Each container runs in isolation, reducing conflicts between applications and improving security.

### What is Node.js?

Node.js is an open-source, cross-platform JavaScript runtime environment that executes JavaScript code outside of a web browser. It uses Google Chrome's V8 JavaScript engine and is designed to build scalable network applications.

#### Why Use Node.js?

1. **Event-driven and Non-blocking I/O**: Node.js is highly efficient for I/O-bound and data-intensive real-time applications.
2. **Single-threaded but Highly Scalable**: Despite being single-threaded, Node.js can handle thousands of concurrent connections efficiently.
3. **Large Ecosystem**: Node.js has a vast ecosystem of libraries and tools available via npm (Node Package Manager).

### Creating a Dockerfile for a Node.js Application

A Dockerfile is a text file that contains instructions to build a Docker image. These instructions are executed in order to create a reproducible environment for your application.

#### Basic Structure of a Dockerfile

```dockerfile
# Use an official Node.js runtime as a parent image
FROM node:13-alpine

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy the package.json and package-lock.json files
COPY package*.json ./

# Install app dependencies
RUN npm install

# Bundle app source
COPY . .

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV NODE_ENV=production

# Run the app
CMD ["node", "server.js"]
```

### Understanding `RUN` and `CMD` Commands

The `RUN` and `CMD` commands are two of the most commonly used instructions in a Dockerfile. They serve different purposes:

- **`RUN`**: Executes any commands in a new layer on top of the current image and commits the results. This is useful for installing dependencies, setting up the environment, etc.
- **`CMD`**: Provides defaults for an executing container. These defaults can include arguments for an executable. Unlike `ENTRYPOINT`, `CMD` can be overridden at runtime.

#### Example Usage

Consider the following Dockerfile snippet:

```dockerfile
FROM node:13-alpine

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install

COPY . .

CMD ["node", "server.js"]
```

Here, `RUN npm install` installs the dependencies specified in `package.json`. The `CMD` instruction specifies the default command to run when the container starts, which in this case is `node server.js`.

### Specifying Node.js Version

It's important to pin down the exact version of Node.js to ensure consistency across different environments. In the Dockerfile, we specify `node:13-alpine` to use Node.js version 13 with the Alpine Linux distribution.

#### Why Use Specific Versions?

Using specific versions helps avoid unexpected behavior due to changes in newer versions. It also ensures that the application runs consistently across different environments.

### Building and Running the Docker Image

To build the Docker image, navigate to the directory containing the Dockerfile and run:

```bash
docker build -t my-node-app .
```

This command builds the Docker image and tags it as `my-node-app`.

To run the container, use:

```bash
docker run -p 8080:8080 my-node-app
```

This maps port 8080 on the host to port 8080 in the container.

### Real-World Examples and Recent CVEs

#### Example: CVE-2021-21315

CVE-2021-21315 is a vulnerability in the Node.js `http-parser` module. This vulnerability allows attackers to cause a denial of service (DoS) by sending specially crafted HTTP requests.

**Impact**: An attacker could exploit this vulnerability to crash the Node.js server, leading to a loss of service.

**Mitigation**: Ensure that you are using a patched version of Node.js. The vulnerability was fixed in Node.js versions 14.17.0, 16.3.0, and 17.0.0.

### How to Prevent / Defend

#### Secure Coding Practices

1. **Use Specific Node.js Versions**: Pin down the exact version of Node.js to avoid unexpected behavior.
2. **Regular Updates**: Keep Node.js and other dependencies up-to-date to mitigate known vulnerabilities.
3. **Security Headers**: Use security headers in your HTTP responses to enhance security.

#### Example: Adding Security Headers

```javascript
const express = require('express');
const app = express();

app.use((req, res, next) => {
    res.setHeader('Content-Security-Policy', "default-src 'self'");
    res.setHeader('X-Frame-Options', 'SAMEORIGIN');
    res.setHeader('X-XSS-Protection', '1; mode=block');
    res.setHeader('X-Content-Type-Options', 'nosniff');
    next();
});

app.listen(8080, () => {
    console.log('Server is running on port  8080');
});
```

#### Hardening Docker Images

1. **Minimize Privileges**: Run containers with minimal privileges.
2. **Use Non-root Users**: Avoid running containers as root.
3. **Scan for Vulnerabilities**: Use tools like `trivy` to scan Docker images for vulnerabilities.

#### Example: Scanning Docker Images with Trivy

```bash
trivy image my-node-app
```

### Mermaid Diagrams

#### Dockerfile Execution Flow

```mermaid
graph TD;
    A[Start] --> B[FROM node:13-alpine];
    B --> C[WORKDIR /usr/src/app];
    C --> D[COPY package*.json ./];
    D --> E[RUN npm install];
    E --> F[COPY . .];
    F --> G[EXPOSE 8080];
    G --> H[CMD ["node", "server.js"]];
```

### Conclusion

Deploying a JavaScript application using Docker provides a consistent and portable environment. By understanding the nuances of Dockerfile creation and the differences between `RUN` and `CMD` commands, you can ensure that your application runs smoothly across different environments. Additionally, by following best practices and mitigating known vulnerabilities, you can enhance the security and reliability of your application.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on web security, including Docker-based scenarios.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: Another popular web application for security training.

These labs provide practical experience in deploying and securing applications using Docker and Node.js.

---
<!-- nav -->
[[04-Introduction to Docker and Deployment of JavaScript Applications|Introduction to Docker and Deployment of JavaScript Applications]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/10-Deploying JavaScript Applications Using Docker/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/10-Deploying JavaScript Applications Using Docker/06-Practice Questions & Answers|Practice Questions & Answers]]
