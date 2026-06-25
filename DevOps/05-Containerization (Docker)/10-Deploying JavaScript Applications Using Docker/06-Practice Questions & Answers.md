---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Practice Questions & Answers

**Q1. Explain the process of deploying a JavaScript application using Docker, including the role of Jenkins in the CI/CD pipeline.**

Jenkins plays a crucial role in the Continuous Integration and Continuous Deployment (CI/CD) pipeline for deploying a JavaScript application using Docker. Here’s a step-by-step breakdown:

1. **Development and Testing**: The developer writes and tests the JavaScript application locally.
2. **Committing Code**: Once the code is tested and ready, it is committed to the version control system (e.g., Git).
3. **Triggering Jenkins**: The commit triggers Jenkins to start the CI/CD pipeline.
4. **Building the Application**: Jenkins uses `npm` to build the JavaScript application.
5. **Creating Docker Image**: Jenkins reads the `Dockerfile` and builds a Docker image containing the application.
6. **Pushing to Docker Repository**: The built Docker image is pushed to a Docker registry (e.g., Docker Hub).
7. **Deployment**: The Docker image can then be pulled and deployed to the desired environment (development, staging, production).

**Q2. How do you create a Dockerfile for a JavaScript application that uses Node.js as its runtime? Provide an example.**

To create a Dockerfile for a JavaScript application that uses Node.js, follow these steps:

1. **Base Image**: Start with a Node.js base image.
2. **Environment Variables**: Set any required environment variables.
3. **Working Directory**: Define the working directory within the container.
4. **Copy Application Files**: Copy the necessary application files into the container.
5. **Install Dependencies**: Install npm dependencies.
6. **Entry Point**: Specify the command to run the application.

Here’s an example Dockerfile:

```dockerfile
# Use the official Node.js image as the base image
FROM node:13-alpine

# Set the working directory inside the container
WORKDIR /home/app

# Copy the package.json and package-lock.json files
COPY package*.json ./

# Install npm dependencies
RUN npm install

# Copy the rest of the application files
COPY . .

# Set environment variables
ENV MONGO_USERNAME=myuser
ENV MONGO_PASSWORD=mypassword

# Expose the port the app runs on
EXPOSE 3000

# Command to run the application
CMD ["node", "server.js"]
```

**Q3. Why is it important to use a specific version of a Node.js image in your Dockerfile?**

Using a specific version of a Node.js image in your Dockerfile is important for several reasons:

1. **Consistency**: Ensures that the application is built and runs consistently across different environments.
2. **Reproducibility**: Allows others to reproduce the exact environment used during development and testing.
3. **Security**: Avoids potential security vulnerabilities present in newer versions that may not have been fully vetted.
4. **Compatibility**: Ensures compatibility with dependencies that may not work correctly with newer versions of Node.js.

For example, specifying `node:13-alpine` ensures that the application will use Node.js version 13 with the Alpine Linux distribution, which is known for being lightweight and secure.

**Q4. How would you modify the Dockerfile to include a MongoDB container and ensure that the JavaScript application can communicate with it?**

To include a MongoDB container and ensure that the JavaScript application can communicate with it, you would typically use Docker Compose. However, you can also modify the Dockerfile to set up environment variables that the application can use to connect to MongoDB.

Here’s an example of how to modify the Dockerfile:

```dockerfile
# Use the official Node.js image as the base image
FROM node:13-alpine

# Set the working directory inside the container
WORKDIR /home/app

# Copy the package.json and package-lock.json files
COPY package*.json ./

# Install npm dependencies
RUN npm install

# Copy the rest of the application files
COPY . .

# Set environment variables for MongoDB connection
ENV MONGO_HOST=mongodb
ENV MONGO_PORT=27017
ENV MONGO_USERNAME=myuser
ENV MONGO_PASSWORD=mypassword

# Expose the port the app runs on
EXPOSE 3000

# Command to run the application
CMD ["node", "server.js"]
```

Additionally, you would need to use Docker Compose to manage both the Node.js and MongoDB containers:

```yaml
version: '3'
services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      MONGO_HOST: mongodb
      MONGO_PORT: 27017
      MONGO_USERNAME: myuser
      MONGO_PASSWORD: mypassword
  mongodb:
    image: mongo:latest
    ports:
      - "27017:27017"
```

**Q5. What is the difference between the `RUN` and `CMD` instructions in a Dockerfile? Provide an example to illustrate the difference.**

The `RUN` and `CMD` instructions in a Dockerfile serve different purposes:

- **RUN**: Executes a command during the build process. It is used to set up the environment, install dependencies, etc.
- **CMD**: Specifies the default command to run when the container starts. It is overridden by the command passed when the container is started.

Here’s an example to illustrate the difference:

```dockerfile
# Use the official Node.js image as the base image
FROM node:13-alpine

# Set the working directory inside the container
WORKDIR /home/app

# Copy the package.json and package-lock.json files
COPY package*.json ./

# Install npm dependencies
RUN npm install

# Copy the rest of the application files
COPY . .

# Set environment variables
ENV MONGO_USERNAME=myuser
ENV MONGO_PASSWORD=mypassword

# Expose the port the app runs on
EXPOSE 3000

# Default command to run the application
CMD ["node", "server.js"]
```

In this example, `RUN npm install` is used to install npm dependencies during the build process, while `CMD ["node", "server.js"]` specifies the default command to run the application when the container starts.

**Q6. How would you troubleshoot a situation where a Docker container fails to start due to missing files?**

If a Docker container fails to start due to missing files, you can follow these troubleshooting steps:

1. **Check Dockerfile**: Ensure that the `COPY` instruction in the Dockerfile correctly copies the necessary files into the container.
2. **Verify File Paths**: Check that the paths specified in the `COPY` instruction are correct and that the files exist in the specified locations.
3. **Inspect Container**: Use `docker exec` to inspect the container and verify that the files are present in the expected directories.
4. **Rebuild Image**: If the files are missing, rebuild the Docker image to ensure that the files are correctly included.

Example of inspecting the container:

```sh
docker exec -it <container_id> /bin/sh
ls /home/app
```

Ensure that the necessary files (e.g., `server.js`, `package.json`) are present in `/home/app`.

**Q7. How can you optimize the size of a Docker image for a JavaScript application?**

Optimizing the size of a Docker image for a JavaScript application involves several strategies:

1. **Use Multi-Stage Builds**: Use multi-stage builds to reduce the final image size by separating the build process and the runtime environment.
2. **Minimize Layers**: Minimize the number of layers in the Dockerfile to reduce the image size.
3. **Use Lightweight Base Images**: Use lightweight base images such as `alpine` to reduce the overall size.
4. **Remove Unnecessary Files**: Remove unnecessary files and dependencies before building the final image.

Example of a multi-stage build:

```dockerfile
# Stage 1: Build the application
FROM node:13-alpine AS builder
WORKDIR /home/app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Create the final image
FROM node:13-alpine
WORKDIR /home/app
COPY --from=builder /home/app/dist ./dist
COPY --from=builder /home/app/node_modules ./node_modules
COPY --from=builder /home/app/package*.json ./
CMD ["node", "dist/server.js"]
```

This approach ensures that only the necessary files and dependencies are included in the final image, reducing its size significantly.

---
<!-- nav -->
[[05-Introduction to Docker and Node.js Deployment|Introduction to Docker and Node.js Deployment]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/10-Deploying JavaScript Applications Using Docker/00-Overview|Overview]]
