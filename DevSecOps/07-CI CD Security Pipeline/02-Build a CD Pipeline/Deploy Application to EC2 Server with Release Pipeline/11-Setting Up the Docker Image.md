---
course: DevSecOps
topic: Build a CD Pipeline
tags: [devsecops]
---

## Setting Up the Docker Image

To create a Docker image, we first need to define a `Dockerfile`. This file contains instructions for building the Docker image.

```dockerfile
# Use the Debian Bullseye Slim base image
FROM debian:bullseye-slim

# Update the package list and install SSH client
RUN apt-get update && \
    apt-get install -y openssh-client && \
    apt-get clean

# Set the working directory
WORKDIR /app

# Copy the application files into the container
COPY . .

# Define the entrypoint or command to run the application
CMD ["bash"]
```

### Explanation of the Dockerfile

- **FROM debian:bullseye-slim**: Specifies the base image. Debian Bullseye Slim is a minimal version of Debian, which reduces the size of the final Docker image.
- **RUN apt-get update && apt-get install -y openssh-client && apt-get clean**: Updates the package list and installs the SSH client. The `apt-get clean` command removes unnecessary files to keep the image size small.
- **WORKDIR /app**: Sets the working directory inside the container.
- **COPY . .**: Copies the current directory contents into the container.
- **CMD ["bash"]**: Defines the default command to run when the container starts.

### Building the Docker Image

To build the Docker image, run the following command in the terminal:

```bash
docker build -t my-app-image .
```

This command builds the Docker image and tags it as `my-app-image`.

### Pushing the Docker Image to a Registry

To make the Docker image accessible from other machines, push it to a Docker registry such as Docker Hub.

```bash
docker login
docker tag my-app-image username/my-app-image
docker push username/my-app-image
```

Replace `username` with your Docker Hub username.

---
<!-- nav -->
[[10-Setting Up the Deployment Job|Setting Up the Deployment Job]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Deploy Application to EC2 Server with Release Pipeline/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/07-CI CD Security Pipeline/02-Build a CD Pipeline/Deploy Application to EC2 Server with Release Pipeline/12-Practice Questions & Answers|Practice Questions & Answers]]
