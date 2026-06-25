---
course: DevSecOps
topic: Image Scanning - Build Secure Docker Images
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Why is it recommended to use an official and verified Docker image instead of creating a custom one?**

Using an official and verified Docker image ensures that the image has been built following best practices and has undergone scrutiny for security and reliability. This reduces the risk of introducing vulnerabilities and ensures consistency across deployments. Additionally, official images often come with regular updates and patches, which help maintain the security posture of the deployed application.

**Q2. What is the problem with using the `latest` tag for Docker images, and how can this issue be mitigated?**

Using the `latest` tag for Docker images can lead to unpredictability because it may pull a different version of the image each time, potentially causing unexpected behavior or breaking the application. This issue can be mitigated by specifying a fixed version tag for the image. For example, instead of using `node:latest`, one should use a specific version like `node:14.17.0`. This ensures that the exact same version is used consistently across builds and deployments.

**Q3. How does choosing a smaller base image, such as Alpine, contribute to better security and performance?**

Choosing a smaller base image, such as Alpine, contributes to better security and performance in several ways:
- **Security**: Smaller images have fewer pre-installed packages, reducing the attack surface. They typically include fewer known vulnerabilities compared to full-fledged OS distributions like Ubuntu or CentOS.
- **Performance**: Smaller images consume less disk space and memory, leading to faster deployment times and reduced resource usage. This is particularly beneficial in environments with limited resources or high concurrency requirements.

**Q4. Explain how to use a `.dockerignore` file to reduce the size of Docker images.**

A `.dockerignore` file is used to exclude certain files and directories from being included in the Docker image. This helps reduce the image size by excluding unnecessary files that are not required for the application to run. Here’s an example of how to use it:

```plaintext
# .dockerignore file
/target/
/build/
*.log
*.tmp
```

This configuration will exclude the `/target/` and `/build/` directories, as well as all `.log` and `.tmp` files from being included in the Docker image.

**Q5. Describe how multi-stage builds can be used to minimize the size and security risks of Docker images.**

Multi-stage builds allow developers to create Docker images in multiple steps, discarding intermediate build artifacts to produce a minimal final image. This approach reduces the image size and minimizes the attack surface. Here’s an example:

```Dockerfile
# Stage 1: Build the application
FROM maven:3.6-jdk-8 AS builder
WORKDIR /app
COPY pom.xml .
RUN mvn dependency:resolve
COPY src ./src
RUN mvn package -DskipTests

# Stage 2: Create the final image
FROM tomcat:9.0-jdk8-openjdk-alpine
COPY --from=builder /app/target/myapp.war /usr/local/tomcat/webapps/
CMD ["catalina.sh", "run"]
```

In this example, the first stage (`builder`) compiles the Java application using Maven, while the second stage creates a minimal Tomcat image containing only the compiled WAR file. All build-time dependencies are discarded, resulting in a smaller and more secure final image.

**Q6. Why is it considered a best practice to run Docker containers with a non-root user?**

Running Docker containers with a non-root user enhances security by limiting the potential damage an attacker can cause if they manage to exploit the application. When a container runs as root, it has full access to the host system, enabling an attacker to escalate privileges and compromise the entire host. By using a non-root user, the scope of any potential breach is confined to the container itself, significantly reducing the risk.

For example, the Node.js image includes a generic user called `node` that can be used to run the application without root privileges:

```Dockerfile
FROM node:14.17.0
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
USER node
CMD [ "npm", "start" ]
```

This configuration ensures that the application runs with limited permissions, enhancing the overall security of the containerized application.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Docker Security Best Practices/09-Conclusion|Conclusion]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Docker Security Best Practices/00-Overview|Overview]]
