---
course: DevSecOps
topic: Image Scanning - Build Secure Docker Images
tags: [devsecops]
---

## Introduction to Docker Image Scanning and Secure Builds

Docker images are the core components of containerized applications, providing a lightweight, portable environment for running software. However, the process of building these images can introduce vulnerabilities if not handled carefully. One critical aspect of securing Docker images is ensuring that only necessary components are included in the final image. This chapter delves into the best practices for building secure Docker images, focusing on the removal of unnecessary build-time artifacts.

### Understanding Build-Time Artifacts

When building a Docker image from a Dockerfile, various artifacts are created during the build process. These artifacts include:

- **Development Tools and Libraries**: Necessary for compiling the application.
- **Dependencies for Unit Tests**: Required to run unit tests.
- **Temporary Files**: Created during the build process and often discarded after compilation.

These artifacts are essential during the build phase but are typically unnecessary for running the final application. Retaining these artifacts in the final image can lead to several issues:

- **Increased Image Size**: Larger images consume more storage and take longer to transfer.
- **Increased Attack Surface**: Unnecessary components can introduce vulnerabilities that attackers can exploit.

#### Example: Package Management Files

Consider a Node.js application that uses `package.json` to manage dependencies. During the build process, `npm install` reads `package.json` to download and install dependencies. Once the dependencies are installed, `package.json` is no longer needed to run the application. However, if `package.json` remains in the final image, it increases the image size and potentially exposes sensitive information about the application's dependencies.

```json
{
  "name": "my-node-app",
  "version": "1.0.0",
  "dependencies": {
    "express": "^4.17.1",
    "body-parser": "^1.19.0"
  }
}
```

### Java-Based Applications

Java-based applications present a similar challenge. During the build process, the Java Development Kit (JDK) is used to compile Java source code. However, the final application only requires the Java Runtime Environment (JRE) to run. Additionally, tools like Maven or Gradle, used for building the application, are not needed in the final image.

#### Example: Maven Build Process

Maven is a popular build automation tool for Java projects. It uses a `pom.xml` file to define project metadata and dependencies. During the build process, Maven downloads and installs dependencies specified in `pom.xml`. Once the dependencies are installed, `pom.xml` is no longer needed to run the application.

```xml
<project xmlns="http://maven.apache.org/POM/4.0.0"
         xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
         xsi:schemaLocation="http://maven.apache.org/POM/4..0.0 http://maven.apache.org/xsd/maven-4.0.0.xsd">
    <modelVersion>4.0.0</modelVersion>
    <groupId>com.example</groupId>
    <artifactId>my-java-app</artifactId>
    <version>1.0-SNAPSHOT</version>
    <dependencies>
        <dependency>
            <groupId>org.springframework.boot</groupId>
            <artifactId>spring-boot-starter-web</artifactId>
            <version>2.5.4</version>
        </dependency>
    </dependencies>
</project>
```

### Multi-Stage Builds

To address the issue of unnecessary build-time artifacts, Docker introduced multi-stage builds. Multi-stage builds allow you to separate the build process into distinct stages, each with its own Dockerfile instructions. Only the necessary components are copied to the final image, reducing its size and attack surface.

#### Example: Multi-Stage Build for a Node.js Application

Here’s an example of a multi-stage build for a Node.js application:

```dockerfile
# Stage 1: Build the application
FROM node:14 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Create the final image
FROM node:14-alpine
WORKDIR /dist
COPY --from=builder /app/dist .
CMD ["node", "index.js"]
```

In this example, the first stage (`builder`) uses the `node:14` image to install dependencies and build the application. The second stage uses a smaller `node:14-alpine` image and copies only the built application from the first stage.

### Real-World Examples and CVEs

Several real-world examples and CVEs highlight the importance of removing unnecessary build-time artifacts:

- **CVE-2021-44228 (Log4Shell)**: This vulnerability affected Java applications that included the Log4j library. Many applications inadvertently included the entire Log4j library in their final images, increasing the attack surface.
- **CVE-2022-22965 (Spring Framework RCE)**: This vulnerability affected Spring Framework applications that included unnecessary dependencies in their final images.

### How to Prevent / Defend

To prevent vulnerabilities related to unnecessary build-time artifacts, follow these best practices:

#### Detection

Use tools like `trivy`, `clair`, or `anchore` to scan Docker images for vulnerabilities. These tools can identify unnecessary dependencies and potential security issues.

```bash
# Using Trivy to scan a Docker image
trivy image my-node-app:latest
```

#### Prevention

1. **Use Multi-Stage Builds**: As demonstrated earlier, multi-stage builds help remove unnecessary build-time artifacts.
2. **Minimize Base Images**: Use minimal base images like `alpine` instead of larger images like `ubuntu`.
3. **Remove Temporary Files**: Ensure that temporary files are removed during the build process.
4. **Secure Coding Practices**: Follow secure coding practices to avoid including unnecessary dependencies.

#### Secure Code Fix

Compare the vulnerable and secure versions of a Dockerfile:

**Vulnerable Version:**

```dockerfile
FROM node:14
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
CMD ["node", "index.js"]
```

**Secure Version:**

```dockerfile
# Stage 1: Build the application
FROM node:14 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Create the final image
FROM node:14-alpine
WORKDIR /dist
COPY --from=builder /app/dist .
CMD ["node", "index.js"]
```

### Hands-On Labs

To practice these concepts, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on Docker security and image scanning.
- **OWASP Juice Shop**: Provides a vulnerable web application that can be containerized and scanned for vulnerabilities.
- **CloudGoat**: Focuses on cloud security and includes scenarios for securing Docker images.

By following these best practices and using the appropriate tools, you can significantly reduce the risk of vulnerabilities in your Docker images.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Docker Security Best Practices/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Docker Security Best Practices/02-Choosing the Right Docker Image|Choosing the Right Docker Image]]
