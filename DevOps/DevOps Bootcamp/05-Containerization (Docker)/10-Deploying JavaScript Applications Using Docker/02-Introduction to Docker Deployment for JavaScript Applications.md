---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Introduction to Docker Deployment for JavaScript Applications

Docker is a powerful tool for deploying applications consistently across different environments. In this chapter, we will explore how to deploy a JavaScript application using Docker. We'll cover the basics of Dockerfiles, the `RUN`, `COPY`, and `CMD` commands, and how these commands interact with both the host and container environments. By the end of this chapter, you should have a solid understanding of how to create a Dockerfile for your JavaScript application and deploy it effectively.

### Understanding Docker Containers and Images

Before diving into the specifics of Dockerfiles, let's briefly review what Docker containers and images are:

- **Docker Image**: A Docker image is a lightweight, standalone, executable package that includes everything needed to run a piece of software, including the code, a runtime, libraries, environment variables, and configuration files.
  
- **Docker Container**: A Docker container is a runnable instance of a Docker image. Containers are isolated from each other and the host system, ensuring that the application runs consistently regardless of the underlying infrastructure.

### Dockerfile Basics

A Dockerfile is a text file that contains instructions for building a Docker image. Each instruction in the Dockerfile corresponds to a layer in the Docker image. Here are some key concepts:

- **Layers**: Each instruction in the Dockerfile creates a new layer in the Docker image. Layers are immutable, meaning once created, they cannot be changed. This allows Docker to cache layers and speed up the build process.
  
- **Build Context**: The build context is the set of files that are available to the Docker daemon during the build process. Typically, this is the directory containing the Dockerfile.

### Common Dockerfile Commands

The Dockerfile supports several commands, each serving a specific purpose. We will focus on three key commands: `RUN`, `COPY`, and `CMD`.

#### RUN Command

The `RUN` command is used to execute any command within the Docker container. This command is executed during the build process and is used to install dependencies, configure the environment, or perform any setup required for the application.

**Syntax**:
```dockerfile
RUN <command>
```

**Example**:
```dockerfile
RUN apt-get update && apt-get install -y nodejs npm
```

This command updates the package list and installs Node.js and npm within the container.

**Why Use RUN?**
- **Environment Setup**: The `RUN` command allows you to set up the environment within the container. This ensures that the container has all the necessary dependencies and configurations to run the application.
- **Consistency**: By using the `RUN` command, you ensure that the environment is consistent across different deployments. This helps avoid issues related to missing dependencies or configuration differences.

**Pitfalls**:
- **Layer Size**: Each `RUN` command creates a new layer in the Docker image. If the command installs large packages or performs operations that generate a lot of output, it can significantly increase the size of the image.
- **Cache Invalidation**: If the `RUN` command changes frequently, it can invalidate the cache for subsequent layers, leading to longer build times.

**How to Prevent / Defend**:
- **Minimize Layer Size**: Use multi-stage builds to minimize the size of the final image. For example, you can use a separate stage to install dependencies and then copy only the necessary files to the final stage.
- **Use Cache Effectively**: Ensure that the `RUN` commands that change infrequently are placed at the beginning of the Dockerfile. This allows Docker to reuse cached layers and speed up the build process.

#### COPY Command

The `COPY` command is used to copy files from the build context to the Docker image. Unlike the `RUN` command, which executes within the container, the `COPY` command operates on the host machine and copies files into the container.

**Syntax**:
```dockerfile
COPY <src>... <dest>
```

**Example**:
```dockerfile
COPY . /home/app
```

This command copies all files from the current directory (`.`) to the `/home/app` directory within the container.

**Why Use COPY?**
- **File Transfer**: The `COPY` command allows you to transfer files from the host machine to the container. This is useful for copying application code, configuration files, or any other files required by the application.
- **Separation of Concerns**: By using the `COPY` command, you can keep the host and container environments separate. This ensures that the container has only the necessary files and dependencies, reducing the risk of unintended side effects.

**Pitfalls**:
- **Security Risks**: Copying files from the host to the container can introduce security risks if the files contain sensitive information or malicious code.
- **Build Context Size**: The build context includes all files in the directory containing the Dockerfile. If the build context is large, it can slow down the build process and increase the size of the Docker image.

**How to Prevent / Defend**:
- **Limit Build Context**: Restrict the build context to only the necessary files. You can use a `.dockerignore` file to exclude unnecessary files from the build context.
- **Validate Files**: Before copying files to the container, validate their contents to ensure they do not contain sensitive information or malicious code.

#### CMD Command

The `CMD` command specifies the default command to run when the container starts. This command is executed after the Docker image is built and the container is started.

**Syntax**:
```dockerfile
CMD ["executable", "param1", "param2"]
```

**Example**:
```dockerfile
CMD ["node", "server.js"]
```

This command starts the Node.js server by executing `node server.js` within the container.

**Why Use CMD?**
- **Entry Point**: The `CMD` command defines the entry point for the container. This ensures that the container starts the application correctly.
- **Default Behavior**: The `CMD` command provides a default behavior for the container. If the user does not specify a command when starting the container, the `CMD` command is executed.

**Pitfalls**:
- **Overriding CMD**: Users can override the `CMD` command when starting the container. This can lead to unexpected behavior if the user specifies a different command.
- **Dependency Issues**: If the `CMD` command depends on certain files or configurations that are not present in the container, it can fail to start the application.

**How to Prevent / Defend**:
- **Ensure Dependencies**: Ensure that all dependencies required by the `CMD` command are present in the container. Use the `COPY` command to copy necessary files and the `RUN` command to install dependencies.
- **Provide Documentation**: Provide clear documentation on how to start the container and any additional steps required to run the application.

### Example Dockerfile for a JavaScript Application

Let's put all these concepts together and create a Dockerfile for a simple JavaScript application.

**Directory Structure**:
```
.
├── Dockerfile
└── src
    ├── server.js
    └── package.json
```

**Dockerfile**:
```dockerfile
# Use an official Node.js runtime as a parent image
FROM node:14-alpine

# Set the working directory in the container
WORKDIR /home/app

# Copy the package.json and package-lock.json files to the container
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the application code to the container
COPY . .

# Specify the default command to run when the container starts
CMD ["node", "server.js"]
```

### Explanation of the Dockerfile

- **Base Image**: We start with an official Node.js runtime image (`node:14-alpine`). This image includes Node.js and npm pre-installed.
  
- **Working Directory**: We set the working directory in the container to `/home/app`. This is where we will copy the application code.

- **Copy Package Files**: We copy the `package.json` and `package-lock.json` files to the container. These files are used to install the application dependencies.

- **Install Dependencies**: We use the `RUN` command to install the application dependencies using `npm install`. This ensures that the container has all the necessary dependencies to run the application.

- **Copy Application Code**: We copy the entire application code to the container using the `COPY` command. This includes the `server.js` file and any other files required by the application.

- **Start the Application**: We specify the default command to run when the container starts using the `CMD` command. This command starts the Node.js server by executing `node server.js`.

### Building and Running the Docker Image

To build and run the Docker image, follow these steps:

1. **Build the Docker Image**:
   ```sh
   docker build -t my-node-app .
   ```

2. **Run the Docker Container**:
   ```sh
   docker run -p 3000:3000 my-node-app
   ```

This command maps port 3000 on the host machine to port 3000 in the container, allowing you to access the application running in the container.

### Real-World Examples and Security Considerations

While Docker provides a consistent and isolated environment for deploying applications, it is important to consider security best practices. Here are some recent real-world examples and security considerations:

- **CVE-2021-21366**: This vulnerability affects Docker versions prior to 20.10.7 and 19.03.15. It allows an attacker to escalate privileges and gain root access to the host machine. To mitigate this vulnerability, ensure that you are using the latest version of Docker and apply security patches regularly.

- **CVE-2021-41519**: This vulnerability affects Docker versions prior to 20.10.8 and 19.03.15. It allows an attacker to bypass the `--read-only` flag and modify the filesystem of the container. To mitigate this vulnerability, ensure that you are using the latest version of Docker and apply security patches regularly.

### How to Prevent / Defend

- **Keep Docker Updated**: Regularly update Docker to the latest version to ensure that you have the latest security patches and improvements.
- **Use Secure Base Images**: Use official base images from trusted sources to ensure that the images are secure and do not contain known vulnerabilities.
- **Limit Privileges**: Run the container with the least privileges necessary to reduce the risk of privilege escalation attacks.
- **Use Security Tools**: Use security tools such as Docker Security Scanning to identify and mitigate vulnerabilities in your Docker images.

### Conclusion

In this chapter, we explored how to deploy a JavaScript application using Docker. We covered the basics of Dockerfiles, the `RUN`, `COPY`, and `CMD` commands, and how these commands interact with both the host and container environments. We also provided a complete example Dockerfile and explained how to build and run the Docker image. Finally, we discussed real-world examples and security considerations to help you deploy your application securely.

### Practice Labs

For hands-on practice, consider the following labs:

- **PortSwigger Web Security Academy**: This lab provides a comprehensive set of exercises to learn about web security and Docker deployment.
- **OWASP Juice Shop**: This lab provides a vulnerable web application that you can deploy using Docker to learn about common web vulnerabilities.
- **DVWA (Damn Vulnerable Web Application)**: This lab provides a vulnerable web application that you can deploy using Docker to learn about common web vulnerabilities.

By completing these labs, you can gain practical experience in deploying JavaScript applications using Docker and learn about common security considerations.

---
<!-- nav -->
[[01-Introduction to Deploying JavaScript Applications Using Docker|Introduction to Deploying JavaScript Applications Using Docker]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/10-Deploying JavaScript Applications Using Docker/00-Overview|Overview]] | [[03-Introduction to Docker Files and Images|Introduction to Docker Files and Images]]
