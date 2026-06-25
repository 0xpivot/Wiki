---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Docker Files and Images

When deploying applications using Docker, the primary artifacts are Docker images and Dockerfiles. A Dockerfile is a script that contains a series of instructions to build a Docker image. This image can then be used to create Docker containers, which are lightweight, portable, and self-sufficient units of software that contain everything needed to run an application.

### What is a Docker Image?

A Docker image is a read-only template that contains the necessary components to run an application. These components typically include the application code, runtime environment, libraries, and dependencies. Docker images are stored in registries such as Docker Hub, and they can be pulled and run on any system that supports Docker.

#### Example: Node.js Application

Consider a simple Node.js application that consists of three files: `app.js`, `package.json`, and `Dockerfile`. The `app.js` file contains the application logic, `package.json` lists the dependencies, and `Dockerfile` specifies how to build the Docker image.

```json
{
  "name": "my-node-app",
  "version": "1.0.0",
  "main": "app.js",
  "scripts": {
    "start": "node app.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  }
}
```

```javascript
// app.js
const express = require('express');
const app = express();

app.get('/', (req, res) => {
  res.send('Hello, World!');
});

app.listen(3000, () => {
  console.log('Server is running on port 3000');
});
```

### What is a Dockerfile?

A Dockerfile is a text file that contains a series of instructions to build a Docker image. Each instruction corresponds to a layer in the Docker image. The syntax of a Dockerfile is straightforward and consists of commands followed by arguments.

#### Basic Structure of a Dockerfile

The basic structure of a Dockerfile includes:

1. **FROM**: Specifies the base image to start with.
2. **COPY**: Copies files from the local filesystem to the filesystem of the image.
3. **RUN**: Executes commands within the image.
4. **CMD**: Specifies the default command to run when starting a container.
5. **EXPOSE**: Indicates the ports that the container will listen on.

#### Example Dockerfile

Here is an example Dockerfile for a Node.js application:

```dockerfile
# Use the official Node.js runtime as a parent image
FROM node:14

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install the application's dependencies
RUN npm install

# Copy the rest of the application code to the working directory
COPY . .

# Expose the port that the application runs on
EXPOSE 3000

# Specify the default command to run when starting the container
CMD ["npm", "start"]
```

### Understanding the FROM Instruction

The `FROM` instruction specifies the base image to start with. This is crucial because it determines the environment in which your application will run. For a Node.js application, you might choose a Node.js base image.

#### Example: Choosing a Base Image

```dockerfile
FROM node:14
```

This line tells Docker to use the `node:14` image as the base. This image already includes Node.js and npm, so you don't need to install them manually.

### Understanding the COPY Instruction

The `COPY` instruction copies files from the local filesystem to the filesystem of the image. This is useful for including your application code and configuration files.

#### Example: Copying Application Code

```dockerfile
COPY . .
```

This line copies all files from the current directory (`.`) to the working directory in the image (`.`).

### Understanding the RUN Instruction

The `RUN` instruction executes commands within the image. This is useful for installing dependencies or performing other setup tasks.

#### Example: Installing Dependencies

```dockerfile
RUN npm install
```

This line installs the dependencies listed in `package.json`.

### Understanding the CMD Instruction

The `CMD` instruction specifies the default command to run when starting a container. This is important because it determines how the container behaves when it starts.

#### Example: Starting the Application

```dockerfile
CMD ["npm", "start"]
```

This line tells Docker to run `npm start` when starting the container.

### Understanding the EXPOSE Instruction

The `EXPOSE` instruction indicates the ports that the container will listen on. This is useful for specifying which ports should be accessible from outside the container.

#### Example: Exposing a Port

```dockerfile
EXPOSE 3000
```

This line tells Docker that the container will listen on port 3000.

### Building the Docker Image

To build the Docker image, you can use the following command:

```bash
docker build -t my-node-app .
```

This command builds the Docker image and tags it as `my-node-app`.

### Running the Docker Container

To run the Docker container, you can use the following command:

```bash
docker run -p 3000:3000 my-node-app
```

This command maps port 3000 on the host to port 3000 on the container and starts the container.

### Real-World Examples and Security Considerations

#### Example: CVE-2021-44228 (Log4Shell)

The Log4Shell vulnerability (CVE-2021-44228) affected many Java applications and demonstrated the importance of keeping dependencies up-to-date. This vulnerability could be exploited by attackers to execute arbitrary code on the server.

#### Secure Coding Practices

To prevent such vulnerabilities, it is essential to keep dependencies up-to-date and to use secure coding practices. Here is an example of a vulnerable `package.json` and its secure counterpart:

**Vulnerable `package.json`:**

```json
{
  "dependencies": {
    "log4j": "2.14.1"
  }
}
```

**Secure `package.json`:**

```json
{
  "dependencies": {
    "log4j": "2.17.1"
  }
}
```

### How to Prevent / Defend

#### Detection

To detect outdated dependencies, you can use tools like `npm audit` or `snyk`.

```bash
npm audit
```

This command checks for known vulnerabilities in the dependencies and provides a report.

#### Prevention

To prevent vulnerabilities, you should:

1. Keep dependencies up-to-date.
2. Use secure coding practices.
3. Regularly review and update dependencies.

#### Secure-Coding Fixes

Here is an example of a vulnerable Dockerfile and its secure counterpart:

**Vulnerable Dockerfile:**

```dockerfile
FROM node:14

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
```

**Secure Dockerfile:**

```dockerfile
FROM node:14

WORKDIR /usr/src/app

COPY package*.json ./
RUN npm install --production

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
```

### Hands-On Labs

For hands-on practice, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn about web security.
- **OWASP Juice Shop**: A deliberately insecure web application for security training.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.
- **WebGoat**: An interactive, gamified web security training application.

These labs provide practical experience in deploying and securing applications using Docker.

### Conclusion

Deploying JavaScript applications using Docker involves creating a Dockerfile that specifies the steps to build a Docker image. This image can then be used to create Docker containers, which are lightweight and portable units of software. By following secure coding practices and regularly updating dependencies, you can ensure the security of your applications.

---
<!-- nav -->
[[02-Introduction to Docker Deployment for JavaScript Applications|Introduction to Docker Deployment for JavaScript Applications]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/10-Deploying JavaScript Applications Using Docker/00-Overview|Overview]] | [[04-Introduction to Docker and Deployment of JavaScript Applications|Introduction to Docker and Deployment of JavaScript Applications]]
