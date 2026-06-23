---
course: DevSecOps
topic: Image Scanning - Build Secure Docker Images
tags: [devsecops]
---

## Choosing the Right Docker Image

When building Docker images, one of the critical decisions is choosing the appropriate base image. Base images serve as the foundation upon which your application is built. They come in various flavors, including full-blown operating systems like Ubuntu or CentOS, and minimalistic ones like Alpine Linux. Each choice has implications for the size of the image, storage requirements, transfer times, and, importantly, security.

### Full-Blown Operating Systems vs. Minimalistic Distributions

#### Full-Blown Operating Systems

Full-blown operating systems like Ubuntu or CentOS provide a comprehensive set of tools and utilities out-of-the-box. This makes them versatile and easy to work with, especially for developers familiar with these environments. However, this comes at a cost:

1. **Image Size**: These images are significantly larger due to the inclusion of numerous packages and tools that may not be necessary for your application.
2. **Storage Requirements**: Larger images require more storage space both in the image repository and on deployment servers.
3. **Transfer Times**: Larger images take longer to pull and push from the repository, which can slow down development and deployment processes.
4. **Security Risks**: Full-blown operating systems often contain hundreds of known vulnerabilities. Each package included in the image increases the attack surface, making it easier for attackers to exploit vulnerabilities.

#### Minimalistic Distributions

Minimalistic distributions like Alpine Linux offer a leaner alternative. These images are designed to be small and lightweight, containing only the essential components needed to run your application. Key benefits include:

1. **Smaller Image Size**: Minimalistic images are much smaller, reducing storage requirements and improving transfer times.
2. **Reduced Attack Surface**: By including fewer packages, these images minimize the number of potential vulnerabilities, thereby reducing the attack surface.
3. **Improved Security**: Smaller images are generally more secure because they have fewer dependencies and less code to maintain.

### Real-World Examples

#### Recent CVEs and Breaches

One notable example of the security risks associated with full-blown operating systems is the Log4j vulnerability (CVE-2021-44228). Many applications using full-blown OS images were affected because the vulnerability was present in the underlying operating system. In contrast, applications using minimalistic images were less likely to be impacted.

Another example is the Heartbleed bug (CVE-2014-0160), which affected OpenSSL. Applications using full-blown OS images with outdated OpenSSL versions were vulnerable, whereas those using minimalistic images with carefully curated dependencies were less exposed.

### How to Choose the Right Base Image

To choose the right base image, consider the following factors:

1. **Application Requirements**: Determine the specific tools and libraries required by your application.
2. **Security Needs**: Assess the security posture of the base image. Minimalistic images generally offer better security.
3. **Performance Considerations**: Evaluate the performance implications of larger versus smaller images.

### Example: Building a Node.js Application

Let's walk through an example of building a Node.js application using both a full-blown OS image and a minimalistic image.

#### Using Ubuntu as the Base Image

```Dockerfile
# Using Ubuntu as the base image
FROM ubuntu:latest

# Install Node.js
RUN apt-get update && \
    apt-get install -y nodejs npm

# Set working directory
WORKDIR /app

# Copy application files
COPY . .

# Install dependencies
RUN npm install

# Expose port
EXPOSE 3000

# Start the application
CMD ["node", "app.js"]
```

#### Using Alpine Linux as the Base Image

```Dockerfile
# Using Alpine Linux as the base image
FROM alpine:latest

# Install Node.js
RUN apk add --no-cache nodejs npm

# Set working directory
WORKDIR /app

# Copy application files
COPY . .

# Install dependencies
RUN npm install

# Expose port
EXPOSE 3000

# Start the application
CMD ["node", "app.js"]
```

### Comparison

| Feature          | Ubuntu Image        | Alpine Image         |
|------------------|---------------------|----------------------|
| Image Size       | Larger              | Smaller              |
| Storage          | Higher              | Lower                |
| Transfer Time    | Longer              | Shorter              |
| Attack Surface   | Larger              | Smaller              |
| Security Risk    | Higher              | Lower                |

### How to Prevent / Defend

#### Detection

1. **Image Scanning Tools**: Use tools like Trivy, Clair, or Aqua Security to scan Docker images for vulnerabilities.
2. **Dependency Management**: Regularly audit and update dependencies to ensure they are secure.

#### Prevention

1. **Use Minimalistic Base Images**: Opt for minimalistic distributions like Alpine Linux to reduce the attack surface.
2. **Regular Updates**: Keep the base image and all dependencies up-to-date with the latest security patches.
3. **Secure Configuration**: Harden the base image by removing unnecessary services and configurations.

#### Secure Code Fix

**Vulnerable Dockerfile**

```Dockerfile
FROM ubuntu:latest

RUN apt-get update && \
    apt-get install -y nodejs npm

WORKDIR /app

COPY . .

RUN npm install

EXPOSE 3000

CMD ["node", "app.js"]
```

**Fixed Dockerfile**

```Dockerfile
FROM alpine:latest

RUN apk add --no-cache nodejs npm

WORKDIR /app

COPY . .

RUN npm install

EXPOSE 3000

CMD ["node", "app.js"]
```

### Conclusion

Choosing the right base image is crucial for building secure and efficient Docker images. While full-blown operating systems offer convenience, they come with significant security risks and performance drawbacks. Minimalistic distributions provide a more secure and efficient alternative. By carefully selecting the base image and regularly updating dependencies, you can significantly improve the security and performance of your Docker images.

### Practice Labs

For hands-on practice with Docker security best practices, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs on securing Docker images.
- **OWASP Juice Shop**: Provides a vulnerable web application that can be containerized and secured using Docker best practices.
- **Kubernetes Goat**: Focuses on securing Kubernetes deployments, including Docker images.

These labs will help you apply the concepts learned in this chapter and gain practical experience in building secure Docker images.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Docker Security Best Practices/01-Introduction to Docker Image Scanning and Secure Builds|Introduction to Docker Image Scanning and Secure Builds]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Docker Security Best Practices/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Docker Security Best Practices/03-Excluding Unnecessary Content|Excluding Unnecessary Content]]
