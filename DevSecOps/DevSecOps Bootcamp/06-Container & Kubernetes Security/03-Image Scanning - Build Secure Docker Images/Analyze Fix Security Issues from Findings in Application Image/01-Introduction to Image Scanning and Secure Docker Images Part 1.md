---
course: DevSecOps
topic: Image Scanning - Build Secure Docker Images
tags: [devsecops]
---

## Introduction to Image Scanning and Secure Docker Images

Image scanning is a critical component of DevSecOps practices, ensuring that Docker images used in applications are free from vulnerabilities and malicious components. This process involves analyzing Docker images to identify potential security issues, such as outdated libraries, known vulnerabilities, and misconfigurations. By addressing these issues, developers can build more secure and reliable applications.

### Why Image Scanning Matters

In the context of containerized applications, Docker images serve as the foundational building blocks. These images contain the necessary software and configurations required to run an application. However, if these images are compromised or contain vulnerabilities, the entire application stack can be at risk. Image scanning helps mitigate these risks by identifying and addressing security issues early in the development lifecycle.

### High-Level Findings and Their Importance

When scanning a Docker image, the scanner typically provides a list of findings categorized by severity. In the given scenario, the scan results indicate four high-level findings. These findings are critical because they represent significant security vulnerabilities that could potentially be exploited by attackers.

#### Example of High-Level Findings

Consider a recent CVE (Common Vulnerabilities and Exposures) such as **CVE-2021-44228**, also known as Log4Shell. This vulnerability affected the Apache Log4j library, which is widely used in Java applications. If a Docker image contains an outdated version of Log4j, it could be exploited by attackers to gain unauthorized access to the system. Image scanning tools can identify such vulnerabilities and flag them for remediation.

### Fixing High-Level Findings

To address the high-level findings, it is essential to understand the root cause of the issue and apply appropriate fixes. In the given scenario, the findings are related to the Debian base image used in the Dockerfile. The Debian base image contains libraries with known vulnerabilities, necessitating an update to a newer version.

#### Updating the Base Image

Updating the base image is a straightforward process that involves modifying the Dockerfile to reference a newer version of the base image. This ensures that the image includes the latest security patches and updates.

```Dockerfile
# Original Dockerfile
FROM debian:buster

# Updated Dockerfile
FROM debian:bullseye
```

### Detailed Steps to Update the Base Image

1. **Identify the Current Base Image**: Determine the current base image being used in the Dockerfile. In this case, it is `debian:buster`.

2. **Check for Available Updates**: Visit the Docker Hub or the official repository for the base image to check for available updates. For Debian, this would involve checking the available tags on the Docker Hub.

3. **Update the Dockerfile**: Modify the Dockerfile to use the updated base image. Ensure that the new base image is compatible with the rest of the Dockerfile instructions.

4. **Rebuild the Docker Image**: After updating the Dockerfile, rebuild the Docker image to incorporate the changes.

```bash
docker build -t myapp .
```

5. **Retest the Application**: Verify that the application still functions correctly with the updated base image. This step is crucial to ensure that the update does not introduce any compatibility issues.

### Handling Dependencies and Testing

While updating the base image is generally simpler than updating application code, it is still important to test the updated image thoroughly. This involves verifying that all dependencies are correctly resolved and that the application behaves as expected.

#### Dependency Management

Ensure that all dependencies specified in the Dockerfile are compatible with the updated base image. This may involve updating package versions or adjusting configuration settings.

```Dockerfile
# Original Dockerfile
FROM debian:buster
RUN apt-get update && apt-get install -y nodejs=14.17.0

# Updated Dockerfile
FROM debian:bullseye
RUN apt-get update && apt-get install -y nodejs=16.13.0
```

### Real-World Example: Log4Shell Vulnerability

Consider the Log4Shell vulnerability (CVE-2021-44228) mentioned earlier. This vulnerability affected the Apache Log4j library, which is commonly used in Java applications. If a Docker image contains an outdated version of Log4j, it could be exploited by attackers to gain unauthorized access to the system.

#### Vulnerable Code Example

```java
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class Log4jExample {
    private static final Logger logger = LogManager.getLogger(Log4jExample.class);

    public void logMessage(String message) {
        logger.info(message);
    }
}
```

#### Secure Code Example

To mitigate the Log4Shell vulnerability, update the Log4j library to a version that includes the necessary security patches.

```java
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class Log4jExample {
    private static final Logger logger = LogManager.getLogger(Log4jExample.class);

    public void logMessage(String message) {
        logger.info(message);
    }
}
```

### How to Prevent / Defend Against Vulnerabilities

#### Detection

Use image scanning tools such as Trivy, Clair, or Aqua Security to regularly scan Docker images for vulnerabilities. These tools provide detailed reports of identified issues, including their severity and recommended actions.

#### Prevention

1. **Regularly Update Base Images**: Keep the base images up-to-date with the latest security patches.
2. **Use Secure Coding Practices**: Follow secure coding guidelines to minimize the risk of introducing vulnerabilities.
3. **Implement Security Policies**: Enforce security policies within the organization to ensure that all Docker images meet the required security standards.

#### Secure-Coding Fixes

Compare the vulnerable and secure versions of the code to highlight the necessary changes.

**Vulnerable Version**

```Dockerfile
FROM debian:buster
RUN apt-get update && apt-get install -y nodejs=14.17.0
```

**Secure Version**

```Dockerfile
FROM debian:bullseye
RUN apt-get update && apt-get install -y nodejs=16.13.0
```

### Complete Example of Request, Response, and Result

#### Full HTTP Request

```http
POST /api/v1/images/scan HTTP/1.1
Host: scanner.example.com
Content-Type: application/json
Authorization: Bearer <token>

{
  "image": "myapp:latest"
}
```

#### Full HTTP Response

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "success",
  "findings": [
    {
      "severity": "high",
      "description": "Outdated Debian base image with known vulnerabilities",
      "recommendation": "Update to Debian:bullseye"
    }
  ]
}
```

#### Expected Result

The Docker image is successfully scanned, and the findings are reported. The high-level finding indicates that the Debian base image needs to be updated to a newer version.

### Hands-On Labs for Practice

For hands-on practice with image scanning and secure Docker images, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to learn about various web security concepts, including container security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including container security.
- **Docker Security Workshops**: Official Docker workshops that cover various aspects of Docker security, including image scanning and secure image creation.

By following these steps and utilizing the provided resources, developers can build more secure Docker images and mitigate potential security risks in their applications.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Analyze Fix Security Issues from Findings in Application Image/00-Overview|Overview]] | [[02-Introduction to Image Scanning and Secure Docker Images Part 2|Introduction to Image Scanning and Secure Docker Images Part 2]]
