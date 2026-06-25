---
course: DevSecOps
topic: Image Scanning - Build Secure Docker Images
tags: [devsecops]
---

## Introduction to Image Scanning in DevSecOps

In the realm of DevSecOps, ensuring the security of container images is paramount. One of the key practices is to perform automated security scanning on Docker images during the build process. This ensures that any vulnerabilities are identified and addressed before the images are deployed into production environments. In this section, we will delve into the specifics of configuring automated security scanning using Trivy, a popular open-source tool for container image scanning.

### What is Trivy?

Trivy is an open-source tool designed to scan container images, local files, and Git repositories for vulnerabilities. It supports various package managers and can integrate seamlessly with CI/CD pipelines. Trivy is particularly useful in DevSecOps workflows because it helps identify known vulnerabilities in the dependencies used within Docker images.

### Why Use Trivy?

Using Trivy in your CI/CD pipeline offers several benefits:

1. **Early Detection**: Identifies vulnerabilities early in the development cycle, reducing the risk of deploying insecure code.
2. **Comprehensive Coverage**: Supports a wide range of package managers and ecosystems, ensuring thorough scanning.
3. **Integration**: Can be easily integrated into existing CI/CD pipelines, making it a practical choice for continuous security checks.

### How Trivy Works

Trivy operates by analyzing the contents of Docker images and comparing them against a database of known vulnerabilities. Here’s a high-level overview of the process:

1. **Image Pull**: Trivy pulls the Docker image from a registry (such as Amazon ECR).
2. **Vulnerability Scan**: It scans the image for known vulnerabilities using its database.
3. **Report Generation**: Trivy generates a report detailing any vulnerabilities found.

### Configuring Trivy in Your Pipeline

To configure Trivy in your CI/CD pipeline, you need to follow these steps:

1. **Install Trivy**: Ensure Trivy is installed in your CI/CD environment. You can download it from the official GitHub repository.
2. **Pull the Image**: Use the `docker pull` command to fetch the image from the registry.
3. **Scan the Image**: Execute the `trivy image` command to scan the image.

Here is an example of how to configure Trivy in a GitLab CI/CD pipeline:

```yaml
image: docker:latest

services:
  - docker:dind

stages:
  - build
  - scan

build_image:
  stage: build
  script:
    - docker build -t my-image .
    - docker tag my-image $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_NAME
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_NAME

scan_image:
  stage: scan
  script:
    - apk add --no-cache curl
    - curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin v0.29.1
    - trivy image --exit-code 1 $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_NAME
```

### Understanding the Trivy Command

The `trivy image` command is used to scan a Docker image for vulnerabilities. Here’s a breakdown of the command:

- `trivy image`: Specifies that Trivy should scan a Docker image.
- `--exit-code 1`: Ensures that Trivy returns a non-zero exit code if vulnerabilities are found. This is crucial for failing the pipeline if vulnerabilities are detected.

### Example of Trivy Output

When Trivy runs, it outputs detailed information about any vulnerabilities found. Here is an example of what the output might look like:

```plaintext
2023-09-15T12:00:00Z        INFO    Vulnerability details for my-image:latest
2023-09-15T12:00:00Z        INFO    Total: 2 (UNKNOWN: 0, LOW: 0, MEDIUM: 1, HIGH: 1, CRITICAL: 0)
2023-09-15T12:00:00Z        INFO    CVE-2023-12345: Medium severity vulnerability in package 'openssl'
2023-09-15T12:00:00Z        INFO    CVE-2023-67890: High severity vulnerability in package 'nginx'
```

### Handling Exit Codes

One of the critical aspects of integrating Trivy into your CI/CD pipeline is handling exit codes correctly. By default, Trivy does not fail the build even if vulnerabilities are found. To ensure that the pipeline fails when vulnerabilities are detected, you need to set the `--exit-code` flag to `1`.

#### Vulnerable Configuration

```yaml
# Vulnerable configuration
scan_image:
  stage: scan
  script:
    - trivy image $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_NAME
```

#### Secure Configuration

```yaml
# Secure configuration
scan_image:
  stage: scan
  script:
    - trivy image --exit-code 1 $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_NAME
```

### Real-World Examples and Recent CVEs

Recent vulnerabilities in Docker images have highlighted the importance of continuous security scanning. For instance, the CVE-2023-12345 vulnerability in OpenSSL was discovered in many Docker images. This vulnerability could allow attackers to execute arbitrary code, leading to potential data breaches.

### How to Prevent / Defend

To prevent such vulnerabilities, you should:

1. **Regularly Update Dependencies**: Keep all dependencies up-to-date to mitigate known vulnerabilities.
2. **Use Secure Base Images**: Choose base images that are regularly maintained and audited for security.
3. **Automate Scanning**: Integrate Trivy or similar tools into your CI/CD pipeline to automatically scan images for vulnerabilities.

### Complete Example with Raw HTTP Messages

While Trivy primarily operates at the command-line level, it can also be integrated into more complex systems where HTTP requests and responses are involved. Here is an example of how Trivy might be invoked via an API call:

```http
POST /api/v1/scans HTTP/1.1
Host: trivy.example.com
Content-Type: application/json

{
  "image": "my-image:latest",
  "exit_code": 1
}
```

Response:

```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "success",
  "vulnerabilities": [
    {
      "id": "CVE-2023-12345",
      "severity": "MEDIUM",
      "package": "openssl"
    },
    {
      "id": "CVE-2023-67890",
      "severity": "HIGH",
      "package": "nginx"
    }
  ]
}
```

### Common Pitfalls and Best Practices

#### Common Pitfalls

- **Ignoring Low-Severity Issues**: Even low-severity issues can be exploited in combination with other vulnerabilities.
- **Failing to Update Dependencies**: Outdated dependencies can introduce known vulnerabilities.
- **Manual Scanning**: Relying solely on manual scanning can lead to missed vulnerabilities.

#### Best Practices

- **Automate Scanning**: Integrate Trivy into your CI/CD pipeline to ensure continuous scanning.
- **Regular Updates**: Keep all dependencies up-to-date.
- **Secure Base Images**: Use base images that are regularly audited for security.

### Hands-On Labs

For hands-on practice with Trivy, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive course on web security, including sections on container security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing.
- **DVWA (Damn Vulnerable Web Application)**: Another popular tool for learning web application security.

These labs provide practical experience in identifying and mitigating vulnerabilities in Docker images.

### Conclusion

Configuring automated security scanning with Trivy is a critical step in ensuring the security of Docker images in a DevSecOps workflow. By integrating Trivy into your CI/CD pipeline and properly handling exit codes, you can effectively detect and address vulnerabilities early in the development cycle. This not only enhances the security of your applications but also aligns with best practices in modern software development.

---
<!-- nav -->
[[04-Introduction to Image Scanning in DevSecOps Part 3|Introduction to Image Scanning in DevSecOps Part 3]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Configure Automated Security Scanning in Application Image/00-Overview|Overview]] | [[06-Introduction to Image Scanning in DevSecOps Part 5|Introduction to Image Scanning in DevSecOps Part 5]]
