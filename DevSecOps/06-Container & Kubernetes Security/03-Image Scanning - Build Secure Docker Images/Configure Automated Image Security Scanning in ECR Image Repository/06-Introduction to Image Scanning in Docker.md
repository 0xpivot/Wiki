---
course: DevSecOps
topic: Image Scanning - Build Secure Docker Images
tags: [devsecops]
---

## Introduction to Image Scanning in Docker

Image scanning is a critical component of DevSecOps practices, ensuring that Docker images are free from vulnerabilities and malicious components before deployment. This process involves analyzing the contents of Docker images to identify known security issues, such as vulnerabilities in the underlying operating system, libraries, or applications. By integrating automated image scanning into your Continuous Integration/Continuous Deployment (CI/CD) pipeline, you can ensure that your Docker images remain secure throughout their lifecycle.

### Why Image Scanning Matters

Docker images are composed of layers, each of which can contain various components such as base images, libraries, and application code. These layers can introduce vulnerabilities if they are based on outdated or compromised sources. For instance, a base image might be derived from a publicly available image that has been identified as having security issues. Similarly, libraries and third-party software included in the image can also introduce vulnerabilities.

#### Real-World Example: CVE-2021-44228 (Log4j)

One of the most significant recent vulnerabilities is CVE-2021-44228, commonly known as Log4Shell. This vulnerability affected the Apache Log4j logging framework, which is widely used in Java applications. Many Docker images that included Log4j were found to be vulnerable, leading to widespread exploitation. This example underscores the importance of continuous image scanning to detect and mitigate such vulnerabilities.

### Tools for Image Scanning

Several tools are available for image scanning, including:

- **Trivy**: An open-source vulnerability scanner for container images, including Docker images.
- **Snyk**: A commercial tool that provides comprehensive security scanning for various types of software artifacts, including Docker images.
- **Clair**: An open-source project by CoreOS that scans Docker images for vulnerabilities.

These tools work by comparing the contents of the Docker image against a database of known vulnerabilities. They can identify specific versions of libraries or components that are known to be vulnerable and provide recommendations for remediation.

### How Image Scanning Works

When you build a Docker image, the tool performs a scan of each layer in the image. This involves checking the following components:

- **Base Images**: The foundational layer of the Docker image, often derived from a public repository.
- **Libraries and Dependencies**: Any additional software or libraries included in the image.
- **Application Code**: The actual application code that runs within the container.

Each of these components is checked against a database of known vulnerabilities. If a vulnerability is detected, the tool reports it along with details about the nature of the vulnerability and potential mitigation strategies.

#### Example: Trivy Scan Output

Here is an example of a Trivy scan output for a Docker image:

```bash
$ trivy image my-docker-image:latest
2023-10-01T12:00:00Z    INFO    Detecting OS packages in my-docker-image:latest
2023-10-01T12:00:00Z    INFO    Number of language-specific files: 0
2023-10-01T12:00:00Z    INFO    Detecting Alpine vulnerabilities...
2023-10-01T12:00:00Z    INFO    Checking for updates of 1 packages (alpine:3.14)
2023-10-01T12:00:00Z    INFO    Found 1 vulnerabilities

my-docker-image:latest (alpine 3.14)
-------------------------------------------------------------------------------
Total: 1 (UNKNOWN: 0, LOW: 0, MEDIUM: 0, HIGH: 1, CRITICAL: 0)

+--------------------------+------------------+----------+-------------------+--------------------------------------+
| VULNERABILITY            | SEVERITY         | STATUS   | PACKAGE           | FIXED IN                            |
+--------------------------+------------------+----------+-------------------+--------------------------------------+
| CVE-2023-12345           | HIGH             | UNFIXED  | libcurl           | 7.80.0                             |
+--------------------------+------------------+----------+-------------------+--------------------------------------+

2023-10-01T12:00:00Z    INFO    Detected Alpine vulnerabilities in my-docker-image:latest
```

In this example, Trivy detects a high-severity vulnerability (`CVE-2023-12345`) in the `libcurl` package. The output includes details about the severity, status, and recommended fix.

### Automating Image Scanning in ECR

Amazon Elastic Container Registry (ECR) provides built-in support for automated image scanning. This feature allows you to automatically scan Docker images stored in ECR for known vulnerabilities.

#### Configuring Automated Image Scanning in ECR

To configure automated image scanning in ECR, follow these steps:

1. **Enable Image Scanning**:
   - Navigate to the ECR console in the AWS Management Console.
   - Select the repository where you want to enable image scanning.
   - Click on the "Scan" tab and enable image scanning.

2. **Configure Scan Settings**:
   - You can configure the scan settings to specify the frequency of scans and the types of vulnerabilities to detect.
   - For example, you can set up a scan to run every time a new image is pushed to the repository.

#### Example: Enabling Image Scanning via AWS CLI

You can also enable image scanning using the AWS Command Line Interface (CLI):

```bash
aws ecr put-image-scanning-configuration --repository-name my-repo --image-scanning-configuration scanOnPush=true
```

This command enables image scanning for the specified repository (`my-repo`) and sets the `scanOnPush` parameter to `true`, meaning that images will be scanned every time they are pushed to the repository.

### Handling Vulnerabilities in Docker Images

Once vulnerabilities are detected, it is crucial to address them promptly to ensure the security of your Docker images. Here are some steps to handle vulnerabilities:

1. **Identify Vulnerable Components**:
   - Review the scan results to identify the specific components that are vulnerable.
   - Determine the severity of each vulnerability and prioritize remediation efforts accordingly.

2. **Update Vulnerable Components**:
   - Update the vulnerable components to the latest, patched versions.
   - For example, if a vulnerability is found in a library, update the library to the latest version that addresses the vulnerability.

3. **Rebuild and Rescan the Image**:
   - After updating the vulnerable components, rebuild the Docker image.
   - Run the image through the scanner again to ensure that the vulnerabilities have been resolved.

#### Example: Updating a Vulnerable Library

Suppose the Trivy scan identifies a vulnerability in the `libcurl` package. To address this vulnerability, you would update the `libcurl` package to the latest version and rebuild the Docker image.

```Dockerfile
# Original Dockerfile
FROM alpine:3.14

RUN apk add --no-cache libcurl=7.79.1

# Updated Dockerfile
FROM alpine:3.14

RUN apk add --no-cache libcurl=7.80.0
```

After updating the `libcurl` package, rebuild the Docker image:

```bash
docker build -t my-docker-image:latest .
```

Then, rescan the updated image:

```bash
trivy image my-docker-image:latest
```

### Continuous Monitoring and Remediation

Even after addressing known vulnerabilities, new vulnerabilities may be discovered in the future. Therefore, it is essential to implement continuous monitoring and remediation processes.

#### Continuous Monitoring

- **Regular Scans**: Schedule regular scans of your Docker images to detect new vulnerabilities.
- **Real-Time Alerts**: Set up alerts to notify you when new vulnerabilities are detected in your images.

#### Real-Time Example: Using AWS ECR Events

AWS ECR supports events that can trigger actions when new images are pushed to the repository. You can use these events to trigger automated scans and send notifications when vulnerabilities are detected.

```json
{
  "source": "aws.ecr",
  "detail-type": "ECR Image Scan",
  "detail": {
    "scan-status": "COMPLETE",
    "finding-severity-counts": {
      "CRITICAL": 0,
      "HIGH": 1,
      "MEDIUM": 0,
      "LOW": 0,
      "INFORMATIONAL": 0,
      "UNDEFINED": 0
    }
  }
}
```

This event can be configured to trigger an AWS Lambda function that sends an alert when a new vulnerability is detected.

### How to Prevent / Defend Against Vulnerabilities

To effectively prevent and defend against vulnerabilities in Docker images, consider the following strategies:

#### Secure Coding Practices

- **Use Secure Base Images**: Choose base images from trusted sources and regularly update them.
- **Minimize Image Size**: Keep the image size minimal by removing unnecessary components and dependencies.
- **Use Official Repositories**: Whenever possible, use official repositories for libraries and dependencies.

#### Configuration Hardening

- **Disable Unnecessary Services**: Disable services that are not required for the application to run.
- **Use Least Privilege Principle**: Ensure that the container runs with the least privileges necessary to perform its tasks.

#### Example: Secure Dockerfile

Here is an example of a secure Dockerfile:

```Dockerfile
# Use a minimal base image
FROM alpine:3.14

# Install only necessary packages
RUN apk add --no-cache curl=7.80.0

# Copy application code
COPY app /app

# Set working directory
WORKDIR /app

# Expose port
EXPOSE 8080

# Run the application
CMD ["./app"]
```

#### Detection and Prevention

- **Automated Scanning**: Integrate automated scanning into your CI/CD pipeline to detect vulnerabilities early.
- **Regular Audits**: Conduct regular audits of your Docker images to ensure they remain secure.

#### Real-World Example: CVE-2021-44228 (Log4j)

For the Log4j vulnerability (CVE-2021-44228), you can take the following steps to prevent and defend against the vulnerability:

1. **Update Log4j**: Ensure that all instances of Log4j are updated to the latest, patched version.
2. **Monitor for Exploits**: Monitor your systems for signs of exploitation, such as unusual network traffic or unauthorized access attempts.
3. **Implement Network Segmentation**: Segment your network to limit the spread of attacks.

### Conclusion

Image scanning is a vital practice in DevSecOps, ensuring that Docker images are free from vulnerabilities and malicious components. By integrating automated image scanning into your CI/CD pipeline and following secure coding practices, you can significantly enhance the security of your Docker images. Regular monitoring and continuous improvement are key to maintaining a secure environment.

### Practice Labs

To gain hands-on experience with image scanning and securing Docker images, consider the following practice labs:

- **PortSwigger Web Security Academy**: Offers a variety of labs focused on web application security, including Docker image scanning.
- **OWASP Juice Shop**: A deliberately insecure web application that can be used to practice identifying and fixing security vulnerabilities.
- **Docker Security Workshop**: Provides a series of exercises and challenges to help you understand and implement secure Docker practices.

By combining theoretical knowledge with practical experience, you can become proficient in securing Docker images and maintaining a robust DevSecOps environment.

---
<!-- nav -->
[[05-Introduction to Image Scanning in Docker Part 1|Introduction to Image Scanning in Docker Part 1]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Configure Automated Image Security Scanning in ECR Image Repository/00-Overview|Overview]] | [[07-Introduction to Image Scanning in ECR|Introduction to Image Scanning in ECR]]
