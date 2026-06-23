---
course: DevSecOps
topic: Image Scanning - Build Secure Docker Images
tags: [devsecops]
---

## Introduction to Image Scanning in Docker Registries

### Background Theory

In the realm of DevSecOps, ensuring the security of containerized applications is paramount. One critical aspect of this is the scanning of Docker images for vulnerabilities and compliance issues. Docker images are essentially packages that contain all the necessary components to run an application, including the application code, libraries, and dependencies. These images are stored in Docker registries, such as Amazon Elastic Container Registry (ECR), Docker Hub, and others.

Image scanning is the process of analyzing these images to identify potential security vulnerabilities, such as known exploits, misconfigurations, and compliance violations. This is crucial because a compromised image can lead to serious security breaches, such as data exfiltration, unauthorized access, and denial of service attacks.

### Why Regular Scanning is Necessary

Regular scanning of Docker images is essential for several reasons:

1. **New Vulnerabilities**: New vulnerabilities are constantly being discovered. An image that was considered secure yesterday might be vulnerable today due to newly identified exploits.
   
2. **Compliance Requirements**: Many organizations are subject to regulatory requirements that mandate regular security assessments of their systems. Regular image scanning helps ensure compliance with these regulations.

3. **Continuous Integration/Continuous Deployment (CI/CD)**: In CI/CD pipelines, images are frequently updated and redeployed. Regular scanning ensures that any new vulnerabilities introduced during these updates are promptly detected and addressed.

### How to Implement Regular Scanning

There are several ways to implement regular scanning of Docker images:

1. **Manual Scanning**: This involves manually triggering scans using tools like Trivy, Clair, or Aqua Security. While this method provides flexibility, it is not practical for large-scale operations.

2. **Automated Scanning**: This involves configuring automated scanning in the Docker registry itself. Most modern Docker registries, including ECR, support this feature.

### Configuring Automated Scanning in ECR

Amazon Elastic Container Registry (ECR) is a fully managed Docker registry provided by AWS. ECR supports automated image scanning, which can be configured to run when images are pushed to the registry and at regular intervals.

#### Step-by-Step Configuration

To configure automated image scanning in ECR, follow these steps:

1. **Enable Image Scanning**:
   - Navigate to the ECR console in the AWS Management Console.
   - Select the repository where you want to enable image scanning.
   - Click on the "Scan" tab and enable image scanning.

2. **Configure Scan Settings**:
   - Set the scan type to "On push" to automatically scan images when they are pushed to the repository.
   - Optionally, set up scheduled scans to run at regular intervals (e.g., daily, weekly).

3. **View Scan Results**:
   - After enabling scanning, you can view the results in the ECR console.
   - The results will show any vulnerabilities found in the images, along with details about the severity and recommended actions.

#### Example Configuration

Here is an example of how to enable image scanning using the AWS CLI:

```bash
aws ecr put-image-scanning-configuration --repository-name my-repo --image-scanning-configuration scanOnPush=true
```

This command enables image scanning for the `my-repo` repository and sets the `scanOnPush` flag to `true`.

### Using Trivy for Image Scanning

Trivy is an open-source tool for scanning container images for vulnerabilities. It supports various package managers and can be integrated into CI/CD pipelines.

#### Installing Trivy

To install Trivy, you can use the following command:

```bash
curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/install.sh | sh -s -- -b /usr/local/bin v0.35.0
```

#### Scanning an Image

To scan a Docker image using Trivy, you can use the following command:

```bash
trivy image my-repo:latest
```

This command will scan the `my-repo:latest` image and output any vulnerabilities found.

### Real-World Examples

#### Recent CVEs and Breaches

One notable example of a vulnerability found in a Docker image is the CVE-2021-44228 (Log4Shell) vulnerability. This vulnerability affected many Java-based applications and was found in numerous Docker images. Regular scanning would have helped detect and mitigate this vulnerability before it could be exploited.

Another example is the CVE-2022-22963 vulnerability in Spring Framework, which affected many Java-based applications. This vulnerability was also found in Docker images, highlighting the importance of regular scanning.

### Common Pitfalls and Best Practices

#### Common Pitfalls

1. **Ignoring Scan Results**: One common pitfall is ignoring scan results. It is crucial to review and address any vulnerabilities found in the images.
   
2. **Incomplete Scanning**: Another pitfall is incomplete scanning. Ensure that all images and their versions are scanned, including those used in development and staging environments.

3. **Outdated Scanning Tools**: Using outdated scanning tools can result in missing new vulnerabilities. Ensure that your scanning tools are up-to-date.

#### Best Practices

1. **Regular Scanning**: Implement regular scanning of all images, both on push and at regular intervals.
   
2. **Review and Address Vulnerabilities**: Regularly review scan results and address any vulnerabilities found.
   
3. **Use Multiple Scanning Tools**: Use multiple scanning tools to ensure comprehensive coverage. Different tools may detect different types of vulnerabilities.

### How to Prevent / Defend

#### Detection

To detect vulnerabilities in Docker images, you can use automated scanning tools like Trivy, Clair, or Aqua Security. These tools can be integrated into CI/CD pipelines to automatically scan images when they are built or pushed to the registry.

#### Prevention

To prevent vulnerabilities in Docker images, follow these best practices:

1. **Use Secure Base Images**: Use base images from trusted sources and ensure they are up-to-date.
   
2. **Minimize Image Size**: Minimize the size of your images by removing unnecessary files and dependencies.
   
3. **Use Multi-Stage Builds**: Use multi-stage builds to reduce the size of your final image and remove build-time dependencies.

#### Secure Coding Fixes

Here is an example of a vulnerable Dockerfile and its secure version:

**Vulnerable Dockerfile**

```Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "app.py"]
```

**Secure Dockerfile**

```Dockerfile
# Stage 1: Build the application
FROM python:3.9-slim AS builder

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Run the application
FROM python:3.9-slim

WORKDIR /app

COPY --from=builder /app .

CMD ["python", "app.py"]
```

In the secure version, a multi-stage build is used to reduce the size of the final image and remove build-time dependencies.

### Conclusion

Regular scanning of Docker images is essential for ensuring the security of containerized applications. By implementing automated scanning in Docker registries like ECR and using tools like Trivy, you can detect and mitigate vulnerabilities before they can be exploited. Following best practices and secure coding techniques can further enhance the security of your Docker images.

### Practice Labs

For hands-on practice with image scanning, consider the following labs:

- **PortSwigger Web Security Academy**: Offers labs on container security, including image scanning.
- **OWASP Juice Shop**: A deliberately insecure web app for practicing security skills, including container security.
- **CloudGoat**: A series of labs for learning AWS security best practices, including image scanning in ECR.

These labs provide real-world scenarios and challenges to help you master the concepts covered in this chapter.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Configure Automated Image Security Scanning in ECR Image Repository/01-Introduction to Image Scanning in Docker Images|Introduction to Image Scanning in Docker Images]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Configure Automated Image Security Scanning in ECR Image Repository/00-Overview|Overview]] | [[03-Introduction to Image Scanning in Docker Repositories Part 1|Introduction to Image Scanning in Docker Repositories Part 1]]
