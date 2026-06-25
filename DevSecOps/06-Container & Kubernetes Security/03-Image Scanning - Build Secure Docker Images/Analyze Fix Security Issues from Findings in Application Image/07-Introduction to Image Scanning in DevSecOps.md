---
course: DevSecOps
topic: Image Scanning - Build Secure Docker Images
tags: [devsecops]
---

## Introduction to Image Scanning in DevSecOps

Image scanning is a critical component of DevSecOps, ensuring that Docker images used in applications are free from vulnerabilities and adhere to security best practices. This process involves analyzing Docker images to identify potential security risks, such as outdated libraries, misconfigurations, and known vulnerabilities. By integrating image scanning into the CI/CD pipeline, organizations can proactively address these issues before deploying the application to production environments.

### Why Image Scanning Matters

In today’s fast-paced development environment, security cannot be an afterthought. With the rise of containerization technologies like Docker, the importance of securing the underlying images becomes paramount. Vulnerabilities in Docker images can lead to serious security breaches, such as unauthorized access, data theft, and denial-of-service attacks. Therefore, image scanning is essential to ensure that the images used in applications are secure and reliable.

### How Image Scanning Works

Image scanning tools analyze Docker images to identify potential security issues. These tools typically perform the following steps:

1. **Dependency Analysis**: Identify all dependencies within the image, including libraries, frameworks, and other components.
2. **Vulnerability Scanning**: Check these dependencies against known vulnerabilities databases, such as the National Vulnerability Database (NVD) and Common Vulnerabilities and Exposures (CVE).
3. **Configuration Review**: Evaluate the image configuration for security best practices, such as setting appropriate permissions, disabling unnecessary services, and ensuring secure communication protocols.
4. **Compliance Checks**: Verify that the image adheres to organizational security policies and compliance requirements.

### Tools for Image Scanning

Several tools are available for image scanning, including:

- **Trivy**: An open-source vulnerability scanner for containers and other artifacts.
- **Clair**: A static analyzer for vulnerabilities in application containers.
- **Anchore Engine**: A container image analysis engine that provides detailed insights into the security posture of images.
- **Snyk**: A cloud-native security platform that includes image scanning capabilities.

### Example: Using Trivy for Image Scanning

Let’s walk through an example using Trivy, an open-source tool for scanning Docker images for vulnerabilities.

#### Step 1: Install Trivy

First, install Trivy on your system. You can download it from the official repository:

```bash
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/install.sh | sh -s -- -b /usr/local/bin v0.37.0
```

#### Step 2: Scan a Docker Image

Once Trivy is installed, you can scan a Docker image using the following command:

```bash
trivy image <image-name>
```

For example, to scan the `node:18` image:

```bash
trivy image node:18
```

This command will output a list of vulnerabilities found in the image, along with their severity levels and details.

### Analyzing and Researching Security Issues

When Trivy or any other scanning tool identifies vulnerabilities, it is crucial to analyze and research these findings to understand their implications and determine the appropriate course of action.

#### Example: Outdated Image with Vulnerabilities

Consider a scenario where Trivy identifies vulnerabilities in an outdated Docker image. The initial image might be based on an older version of Node.js, which contains known vulnerabilities.

```bash
trivy image myapp:latest
```

Output:

```
2023-10-01T12:00:00Z    INFO    Completed scanning myapp:latest
2023-10-01T12:00:00Z    INFO    Vulnerable packages found: 4
2023-10-01T12:00:00Z    INFO    Total: 4 (UNKNOWN: 0, LOW: 0, MEDIUM: 0, HIGH: 4, CRITICAL: 0)
```

The report indicates that the image contains four high-severity vulnerabilities. To address these issues, you need to update the base image to a more recent version.

### Updating the Base Image

To mitigate the identified vulnerabilities, you can update the base image to a more recent version. For instance, changing from an older version of Node.js to the latest stable version.

#### Dockerfile Example

Here is an example of a Dockerfile using an outdated base image:

```Dockerfile
# Outdated Dockerfile
FROM node:14

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
CMD ["npm", "start"]
```

To update the base image, modify the Dockerfile as follows:

```Dockerfile
# Updated Dockerfile
FROM node:18-slim

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
CMD ["npm", "start"]
```

### Committing Changes and Re-running the Pipeline

After updating the Dockerfile, commit the changes and re-run the CI/CD pipeline to ensure that the new image is built and scanned.

```bash
git add Dockerfile
git commit -m "Update base image to node:18-slim"
git push
```

The pipeline will automatically build the new image and run Trivy to scan for vulnerabilities.

### Analyzing New Scan Results

Once the pipeline completes, review the new scan results to verify that the vulnerabilities have been resolved.

```bash
trivy image myapp:latest
```

Output:

```
2023-10-01T12:00:00Z    INFO    Completed scanning myapp:latest
2023-10-01T12:00:00Z    INFO    Vulnerable packages found: 1
2023-10-01T12:00:00Z    INFO    Total: 1 (UNKNOWN: 0, LOW: 0, MEDIUM: 0, HIGH: 1, CRITICAL: 0)
```

The new scan results indicate that one high-severity vulnerability remains, related to the Pearl Base library.

### Handling Remaining Vulnerabilities

Even after updating the base image, new vulnerabilities may be introduced. In this case, the Pearl Base library has a known vulnerability that has not yet been fixed.

#### Steps to Address Remaining Vulnerabilities

1. **Evaluate the Impact**: Assess the severity and potential impact of the remaining vulnerability.
2. **Monitor for Updates**: Keep an eye on updates to the Pearl Base library and apply them as soon as they become available.
3. **Implement Workarounds**: If possible, implement workarounds to mitigate the risk until a fix is available.

### How to Prevent / Defend Against Image Vulnerabilities

#### Detection

Regularly scan Docker images using tools like Trivy to identify vulnerabilities. Integrate these scans into the CI/CD pipeline to ensure that vulnerabilities are detected early in the development cycle.

#### Prevention

1. **Use Up-to-date Base Images**: Always use the latest stable versions of base images to minimize the risk of known vulnerabilities.
2. **Minimize Image Size**: Use slim versions of base images to reduce the number of dependencies and potential vulnerabilities.
3. **Secure Configuration**: Ensure that the image configuration adheres to security best practices, such as setting appropriate permissions and disabling unnecessary services.

#### Secure Coding Fixes

Compare the vulnerable and fixed versions of the Dockerfile to illustrate the necessary changes:

**Vulnerable Dockerfile**

```Dockerfile
FROM node:14

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
CMD ["npm", "start"]
```

**Fixed Dockerfile**

```Dockerfile
FROM node:18-slim

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
CMD ["npm", "start"]
```

### Real-World Examples and Recent CVEs

#### Example: CVE-2021-44228 (Log4j)

One of the most significant recent vulnerabilities was CVE-2021-44228, also known as Log4Shell. This vulnerability affected the Apache Log4j library, which is widely used in Java applications. Docker images containing vulnerable versions of Log4j were at risk of exploitation.

By regularly scanning Docker images and updating base images, organizations could mitigate the risk of this vulnerability.

#### Example: CVE-2022-22965 (Spring Framework)

Another notable vulnerability was CVE-2022-22965, affecting the Spring Framework. This vulnerability allowed attackers to execute arbitrary code on affected systems. Docker images containing vulnerable versions of the Spring Framework were at risk.

Regular image scanning and updating base images helped organizations stay protected against this vulnerability.

### Conclusion

Image scanning is a vital component of DevSecOps, ensuring that Docker images are secure and free from vulnerabilities. By integrating image scanning into the CI/CD pipeline and regularly updating base images, organizations can proactively address security issues and protect their applications from potential threats.

### Hands-On Practice

To gain practical experience with image scanning, consider the following labs:

- **PortSwigger Web Security Academy**: Offers hands-on exercises for web application security, including Docker image scanning.
- **OWASP Juice Shop**: Provides a vulnerable web application for practicing security testing, including Docker image analysis.
- **DVWA (Damn Vulnerable Web Application)**: Another resource for practicing web application security, including Docker image scanning.

These labs provide real-world scenarios and challenges to help you master the skills required for effective image scanning and security management in DevSecOps.

---
<!-- nav -->
[[06-Introduction to Image Scanning and Secure Docker Images|Introduction to Image Scanning and Secure Docker Images]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Analyze Fix Security Issues from Findings in Application Image/00-Overview|Overview]] | [[08-Dependency Management and Vulnerability Scanning in Docker Images|Dependency Management and Vulnerability Scanning in Docker Images]]
