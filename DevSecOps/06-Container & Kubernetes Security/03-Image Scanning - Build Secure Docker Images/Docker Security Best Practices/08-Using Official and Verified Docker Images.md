---
course: DevSecOps
topic: Image Scanning - Build Secure Docker Images
tags: [devsecops]
---

## Using Official and Verified Docker Images

### Background Theory

When building Docker images for applications, it is crucial to start with a reliable and secure base image. An official Docker image is one that is maintained and supported by the community or the original software developers. These images are typically more secure and up-to-date compared to unofficial images, which can be less reliable and potentially contain vulnerabilities.

For instance, if you are developing a Node.js application, using the official `node` image ensures that you are starting with a well-maintained and secure base. This image is regularly updated and patched, reducing the risk of introducing known vulnerabilities into your application.

### Why Use Official Images?

Using official images provides several benefits:

1. **Security**: Official images are more likely to be free from known vulnerabilities and are regularly updated with security patches.
2. **Consistency**: Official images ensure that everyone using the same image is working with the same environment, reducing inconsistencies across development, testing, and production environments.
3. **Maintenance**: Official images are maintained by the community or the original software developers, ensuring that they are kept up-to-date and reliable.

### How to Use Official Images

To use an official Docker image, you simply specify the image name in your Dockerfile. For example, to use the official `node` image, you would write:

```Dockerfile
FROM node:14
```

This specifies that the base image is the `node` image with version `14`.

### Example: Building a Node.js Application

Let's walk through an example of building a simple Node.js application using the official `node` image.

#### Step 1: Create a Dockerfile

Create a `Dockerfile` in your project directory:

```Dockerfile
# Use the official Node.js image as the base image
FROM node:14

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application files to the working directory
COPY . .

# Expose port 3000
EXPOSE 3000

# Command to run the application
CMD ["npm", "start"]
```

#### Step 2: Build the Docker Image

Build the Docker image using the following command:

```bash
docker build -t my-node-app .
```

This command builds the Docker image and tags it as `my-node-app`.

#### Step 3: Run the Docker Container

Run the Docker container using the following command:

```bash
docker run -p 3000:3000 my-node-app
```

This command maps port `3000` of the container to port `3000` of the host machine and starts the application.

### Fixating the Version

Using the `latest` tag for the base image can lead to unpredictability and potential issues. The `latest` tag does not guarantee that you will get the same version of the image each time you build your application. This can result in unexpected behavior or even breakages if the new version of the image introduces changes that affect your application.

To avoid this, it is recommended to fixate the version of the base image. This ensures that you always use the same version of the image, providing consistency and predictability.

### How to Fixate the Version

To fixate the version of the base image, specify the exact version number in the `FROM` statement of your Dockerfile. For example:

```Dockerfile
FROM node:14.17.0
```

This specifies that the base image is the `node` image with version `14.17.0`.

### Example: Fixating the Version

Let's modify the previous example to fixate the version of the base image.

#### Step 1: Update the Dockerfile

Update the `Dockerfile` to fixate the version of the base image:

```Dockerfile
# Use the official Node.js image with a specific version as the base image
FROM node:14.17.0

# Set the working directory inside the container
WORKDIR /app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the rest of the application files to the working directory
COPY . .

# Expose port 3000
EXPOSE 3000

# Command to run the application
CMD ["npm", "start"]
```

#### Step 2: Build the Docker Image

Build the Docker image using the following command:

```bash
docker build -t my-node-app .
```

#### Step 3: Run the Docker Container

Run the Docker container using the following command:

```bash
docker run -p 3000:3000 my-node-app
```

### Real-World Examples

#### CVE-2021-21315

In 2021, a critical vulnerability was discovered in the `node` image (CVE-2021-21315). This vulnerability allowed attackers to execute arbitrary code on systems running affected versions of Node.js. By using a specific version of the `node` image, you can ensure that you are not using a version that contains this vulnerability.

#### Example Vulnerable Code

Consider the following vulnerable Dockerfile:

```Dockerfile
# Vulnerable Dockerfile
FROM node:latest

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000
CMD ["npm", "start"]
```

#### Example Fixed Code

Now consider the fixed Dockerfile:

```Dockerfile
# Fixed Dockerfile
FROM node:14.17.0

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000
CMD ["npm", "start"]
```

### How to Prevent / Defend

#### Detection

To detect the use of the `latest` tag in your Dockerfiles, you can use static analysis tools such as `Hadolint`. Hadolint is a linter for Dockerfiles that checks for common issues and best practices.

Install Hadolint using the following command:

```bash
curl -L https://github.com/hadolint/hadolint/releases/download/v2.10.0/hadolint-Linux-x86_64 -o hadolint
chmod +x hadolint
sudo mv hadolint /usr/local/bin/
```

Run Hadolint on your Dockerfile:

```bash
hadolint Dockerfile
```

Hadolint will flag the use of the `latest` tag and provide recommendations to fix it.

#### Prevention

To prevent the use of the `latest` tag, you can enforce the use of specific versions in your CI/CD pipeline. For example, you can use a pre-commit hook to check the Dockerfile before committing changes.

Here is an example of a pre-commit hook that checks for the use of the `latest` tag:

```bash
#!/bin/bash

# Check for the use of the latest tag
if grep -q "FROM .*:latest" Dockerfile; then
  echo "Error: The latest tag is used in the Dockerfile."
  exit 1
fi

echo "Dockerfile is valid."
exit 0
```

Make sure to make the script executable:

```bash
chmod +x pre-commit-hook.sh
```

Add the script to your `.git/hooks/pre-commit` file:

```bash
#!/bin/bash

./pre-commit-hook.sh
```

Make sure to make the `.git/hooks/pre-commit` file executable:

```bash
chmod +x .git/hooks/pre-commit
```

#### Secure Coding Fixes

Compare the vulnerable and fixed Dockerfiles side by side:

**Vulnerable Dockerfile**

```Dockerfile
FROM node:latest

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000
CMD ["npm", "start"]
```

**Fixed Dockerfile**

```Dockerfile
FROM node:14.17.0

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000
CMD ["npm", "start"]
```

### Configuration Hardening

To further harden your Docker images, you can implement additional security measures such as:

1. **Using a minimal base image**: Choose a minimal base image that contains only the necessary components.
2. **Disabling unnecessary services**: Disable any services that are not required for your application.
3. **Running as a non-root user**: Avoid running your application as the root user. Instead, create a non-root user and run your application as that user.
4. **Using a security scanner**: Use a security scanner such as `Clair` or `Trivy` to scan your Docker images for vulnerabilities.

### Real-World Labs

To practice these concepts, you can use the following labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs related to Docker security and DevSecOps.
- **OWASP Juice Shop**: A deliberately insecure web application that you can use to practice securing Docker images.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application that you can use to practice Docker security.

By following these best practices and using the provided resources, you can build more secure and reliable Docker images for your applications.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Docker Security Best Practices/07-Understanding Container Privileges and Risks|Understanding Container Privileges and Risks]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Docker Security Best Practices/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Docker Security Best Practices/09-Conclusion|Conclusion]]
