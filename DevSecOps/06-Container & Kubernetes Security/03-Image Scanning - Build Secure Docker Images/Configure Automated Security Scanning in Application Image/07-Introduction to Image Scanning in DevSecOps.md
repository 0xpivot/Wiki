---
course: DevSecOps
topic: Image Scanning - Build Secure Docker Images
tags: [devsecops]
---

## Introduction to Image Scanning in DevSecOps

In the realm of DevSecOps, ensuring the security of Docker images is paramount. Docker images are composed of layers, each containing specific instructions and dependencies. These layers can introduce vulnerabilities if not properly managed. To effectively identify and mitigate these vulnerabilities, automated security scanning tools are essential. This chapter will delve into the concepts, tools, and practices involved in configuring automated security scanning for Docker images.

### Understanding Docker Networking and Layers

Before diving into the specifics of image scanning, it's crucial to understand the underlying principles of Docker networking and layers.

#### Docker Networking

Docker networking allows containers to communicate with each other and with external networks. Containers can be connected to different types of networks, including:

- **Bridge Network**: The default network type, which connects containers to a virtual bridge.
- **Host Network**: Shares the host’s network stack with the container.
- **Overlay Network**: Used for multi-host networking in swarm mode.

Understanding Docker networking helps in identifying potential security risks, such as unauthorized access or data leakage between containers.

#### Docker Image Layers

A Docker image is composed of multiple layers, each representing a specific instruction in the `Dockerfile`. Each layer adds a new file system layer on top of the previous one. This layered structure allows for efficient storage and distribution of images.

For example, consider the following `Dockerfile`:

```dockerfile
FROM ubuntu:20.04
RUN apt-get update && apt-get install -y curl
COPY app.py /app.py
CMD ["python", "/app.py"]
```

This `Dockerfile` creates four layers:
1. Base image (`ubuntu:20.04`)
2. Update and install `curl`
3. Copy `app.py`
4. Set the command to run `app.py`

Each layer can potentially contain vulnerabilities, especially if the base image or installed packages are outdated.

### Importance of Image Scanning

Image scanning is crucial because it helps identify and mitigate security vulnerabilities in Docker images. Without proper scanning, developers might unknowingly deploy images with critical vulnerabilities, leading to potential security breaches.

#### Real-World Example: CVE-2021-44228 (Log4j)

The Log4j vulnerability (CVE-2021-44228) affected numerous applications and services. Many Docker images contained vulnerable versions of Log4j, leading to widespread exploitation. Automated scanning tools could have identified these vulnerabilities during the build process, preventing their deployment.

### Tools for Image Scanning

Several tools are available for scanning Docker images, both open-source and commercial. Some popular options include:

- **Docker Scout**
- **Trivy**
- **Clair**
- **Anchore**

These tools analyze Docker images to identify known vulnerabilities, misconfigurations, and other security issues.

#### Docker Scout

Docker Scout is a built-in tool provided by Docker for scanning images. It checks for dependencies in image layers that have known security vulnerabilities.

To use Docker Scout, you can run the following command:

```bash
docker scout quickstart
```

This command sets up Docker Scout and starts scanning your images.

#### Trivy

Trivy is an open-source tool that scans Docker images for vulnerabilities. It supports various package managers and provides detailed reports.

To install Trivy, you can use the following command:

```bash
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/scripts/install.sh | sh -s -- -b /usr/local/bin v0.36.0
```

To scan a Docker image with Trivy, you can use:

```bash
trivy image <image-name>
```

### Configuring Automated Security Scanning

Automated security scanning should be integrated into the CI/CD pipeline to ensure that images are scanned during the build process. This can be achieved using tools like Docker Scout or Trivy.

#### Using Trivy in a CI/CD Pipeline

To integrate Trivy into a CI/CD pipeline, you can create a job that runs Trivy after the image is built. Here’s an example using GitLab CI/CD:

```yaml
stages:
  - build
  - scan

build_image:
  stage: build
  script:
    - docker build -t my-image .
  artifacts:
    paths:
      - my-image.tar

scan_image:
  stage: scan
  script:
    - docker load -i my-image.tar
    - trivy image my-image
```

This pipeline first builds the Docker image and then loads it for scanning using Trivy.

### How to Prevent / Defend Against Vulnerabilities

To prevent and defend against vulnerabilities in Docker images, follow these best practices:

#### Secure Coding Practices

Ensure that the code and dependencies used in the Docker image are secure. Regularly update dependencies and use secure coding practices.

#### Hardening Configuration

Harden the Docker image configuration to minimize attack surfaces. For example, avoid using root users and restrict unnecessary permissions.

#### Regular Scanning

Regularly scan Docker images using tools like Trivy or Docker Scout to identify and mitigate vulnerabilities.

#### Example: Secure vs. Vulnerable Dockerfile

Here’s an example of a vulnerable `Dockerfile` and its secure counterpart:

**Vulnerable Dockerfile:**

```dockerfile
FROM python:3.8-slim
RUN pip install flask==1.1.1
COPY app.py /app.py
CMD ["python", "/app.py"]
```

**Secure Dockerfile:**

```dockerfile
FROM python:3.8-slim
RUN pip install --upgrade pip
RUN pip install flask==2.0.1
COPY app.py /app.py
USER nobody
CMD ["python", "/app.py"]
```

In the secure version, the `pip` package manager is upgraded, the latest version of Flask is installed, and the user is set to `nobody` to reduce privileges.

### Conclusion

Automated security scanning is a critical component of DevSecOps. By integrating tools like Docker Scout or Trivy into the CI/CD pipeline, organizations can ensure that Docker images are free from vulnerabilities. Understanding Docker networking and layers, and following best practices for secure coding and configuration, can significantly enhance the security of Docker images.

### Practice Labs

To gain hands-on experience with image scanning, consider the following practice labs:

- **PortSwigger Web Security Academy**: Offers exercises on securing Docker images.
- **OWASP Juice Shop**: Provides a vulnerable application that can be containerized and scanned.
- **Docker Scout Quickstart Guide**: Follow the official guide to set up and use Docker Scout.

By combining theoretical knowledge with practical experience, you can become proficient in building and securing Docker images in a DevSecOps environment.

---
<!-- nav -->
[[06-Introduction to Image Scanning in DevSecOps Part 5|Introduction to Image Scanning in DevSecOps Part 5]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Configure Automated Security Scanning in Application Image/00-Overview|Overview]] | [[08-Configuring Automated Security Scanning in Application Image|Configuring Automated Security Scanning in Application Image]]
