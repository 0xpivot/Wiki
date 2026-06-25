---
course: DevSecOps
topic: Introduction to Kubernetes Security
tags: [devsecops]
---

## Introduction to Kubernetes Security Best Practices

Kubernetes is a powerful platform for managing containerized applications at scale. However, with great power comes great responsibility, especially when it comes to security. This section will delve into some of the key security best practices for Kubernetes, focusing on image scanning and privilege management.

### Image Scanning Tools in CI/CD Pipeline

One of the foundational aspects of securing Kubernetes deployments is ensuring that the container images used are free from vulnerabilities. This is achieved through the use of image scanning tools integrated into the Continuous Integration/Continuous Deployment (CI/CD) pipeline.

#### What is Image Scanning?

Image scanning involves analyzing container images for known vulnerabilities, insecure configurations, and other security issues. These tools typically check for:

- **Insecure Tools or Packages**: Identifying outdated or vulnerable libraries and dependencies.
- **Dependencies with Vulnerabilities**: Checking for known vulnerabilities in the software packages used.
- **Insecure Configuration**: Ensuring that the image does not contain misconfigurations that could lead to security risks.
- **Hard-Coded Secrets**: Detecting sensitive information such as API keys, passwords, or other secrets embedded directly in the image.

#### Why Image Scanning Matters

Without proper image scanning, you risk deploying containers that could be exploited due to known vulnerabilities. This can lead to serious security breaches, including unauthorized access to sensitive data or even complete system compromise.

#### How Image Scanning Works

Image scanning tools work by comparing the contents of the container image against a database of known vulnerabilities. This database is continuously updated as new vulnerabilities are discovered. Here’s a step-by-step breakdown of the process:

1. **Image Build**: The container image is built using a Dockerfile or similar build definition.
2. **Scanning Command**: Once the image is built, a scanning command is executed. This command checks the image against the vulnerability database.
3. **Vulnerability Check**: The tool identifies any vulnerabilities present in the image.
4. **Security Scan**: The tool also checks for insecure configurations and hard-coded secrets.
5. **Pass/Fail Decision**: If the image passes the scan, it can be pushed to the repository. If it fails, the image should be rebuilt and re-scanned.

#### Example of Image Scanning

Let’s consider an example using `Clair`, a popular open-source image scanner. Suppose we have a Docker image named `myapp:v1`.

```bash
# Build the Docker image
docker build -t myapp:v1 .

# Run the Clair scanner
clair-scanner --app=myapp:v1
```

The output might look something like this:

```plaintext
Image: myapp:v1
Total vulnerabilities found: 3
Critical: 0
High: 1
Medium: 2
Low: 0
Negligible: 0
```

If the image passes the scan, it can be pushed to the repository:

```bash
docker push myapp:v1
```

### Regular Scanning of Images in the Repository

Even if an image passes the initial scan during the CI/CD pipeline, new vulnerabilities may be discovered after the image is pushed to the repository. Therefore, it is crucial to perform regular scans of images stored in the repository.

#### Why Regular Scanning is Necessary

New vulnerabilities are discovered frequently, and an image that was secure at the time of deployment may become vulnerable later. Regular scanning ensures that any newly discovered vulnerabilities are identified and addressed promptly.

#### How Regular Scanning Works

Many image registries, such as Docker Hub, offer built-in scanning capabilities. These tools continuously monitor the images in the repository and alert you if a new vulnerability is discovered.

For example, Docker Hub provides a feature called "Security Scanning," which automatically scans images for vulnerabilities and sends notifications if any are found.

#### Example of Regular Scanning

Suppose you have an image `myapp:v1` stored in Docker Hub. Docker Hub’s Security Scanning feature will periodically scan this image and notify you if any new vulnerabilities are discovered.

```plaintext
Notification: New vulnerability found in myapp:v1
Vulnerability ID: CVE-2023-XXXXX
Severity: High
Description: A critical vulnerability has been discovered in one of the dependencies of the image.
```

Upon receiving such a notification, you should immediately take action to update the image and redeploy it.

### Avoiding Root User in Containers

Running containers with elevated privileges, particularly as the root user, significantly increases the risk of security breaches. If a container is compromised and it is running as root, the attacker can gain full control over the host system.

#### Why Avoiding Root User is Important

Containers running as root have full access to the underlying host system. If an attacker gains access to a container running as root, they can potentially escape the container and access the host system, leading to a complete system compromise.

#### How to Avoid Running as Root

To mitigate this risk, you should configure your containers to run as non-root users. This can be done by specifying a user in the Dockerfile or by setting the `securityContext` in the Kubernetes Pod specification.

#### Example of Running as Non-Root User

Here’s an example of a Dockerfile that specifies a non-root user:

```Dockerfile
FROM python:3.9-slim

# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set the working directory
WORKDIR /app

# Copy the application files
COPY . /app

# Switch to the non-root user
USER appuser

# Run the application
CMD ["python", "app.py"]
```

In this example, the container runs as the `appuser` instead of root.

#### Kubernetes Pod Specification

You can also specify the user in the Kubernetes Pod specification using the `securityContext` field:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-pod
spec:
  containers:
  - name: myapp-container
    image: myapp:v1
    securityContext:
      runAsUser: 1000
      runAsGroup: 3000
```

In this example, the container runs as user `11000` and group `3000`.

### Real-World Examples and Recent CVEs

#### CVE-2023-XXXXX: Insecure Configuration in Docker Images

A recent CVE, CVE-2023-XXXXX, highlighted an insecure configuration issue in Docker images. This vulnerability allowed attackers to escalate their privileges within the container, leading to potential host system compromise.

**Detection**: The vulnerability was detected using an image scanning tool like `Trivy`. The tool flagged the insecure configuration and provided details about the issue.

**Prevention**: To prevent this vulnerability, ensure that your Docker images are configured securely. Use non-root users and avoid hard-coding sensitive information in the images.

#### CVE-2023-YYYYY: Hard-Coded Secrets in Container Images

Another recent CVE, CVE-2023-YYYYY, involved hard-coded secrets in container images. This vulnerability allowed attackers to extract sensitive information, such as API keys and passwords, from the images.

**Detection**: The vulnerability was detected using an image scanning tool like `Anchore Engine`. The tool flagged the hard-coded secrets and provided details about the issue.

**Prevention**: To prevent this vulnerability, avoid hard-coding sensitive information in your container images. Use environment variables or secrets management solutions like Kubernetes Secrets.

### How to Prevent / Defend

#### Detection

To detect vulnerabilities in your container images, use image scanning tools like `Clair`, `Trivy`, or `Anchore Engine`. These tools can be integrated into your CI/CD pipeline to ensure that images are scanned before deployment.

#### Prevention

To prevent vulnerabilities, follow these best practices:

1. **Use Non-Root Users**: Configure your containers to run as non-root users.
2. **Avoid Hard-Coded Secrets**: Use environment variables or secrets management solutions to store sensitive information.
3. **Regular Scanning**: Perform regular scans of images in the repository to detect newly discovered vulnerabilities.

#### Secure Coding Fixes

Here’s an example of a vulnerable Dockerfile and its secure counterpart:

**Vulnerable Dockerfile**:

```Dockerfile
FROM python:3.9-slim

# Copy the application files
COPY . /app

# Run the application
CMD ["python", "app.py"]
```

**Secure Dockerfile**:

```Dockerfile
FROM python:3.9-slim

# Create a non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Set the working directory
WORKDIR /app

# Copy the application files
COPY . /app

# Switch to the non-root user
USER appuser

# Run the application
CMD ["python", "app.py"]
```

#### Configuration Hardening

To harden your Kubernetes configurations, use the `securityContext` field in the Pod specification to specify non-root users and groups.

**Vulnerable Pod Specification**:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-pod
spec:
  containers:
  - name: myapp-container
    image: myapp:v1
```

**Secure Pod Specification**:

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: myapp-pod
spec:
  containers:
  - name: myapp-container
    image: myapp:v1
    securityContext:
      runAsUser: 1000
      runAsGroup: 3000
```

### Conclusion

Securing Kubernetes deployments requires a multi-faceted approach, including image scanning and privilege management. By following these best practices, you can significantly reduce the risk of security breaches and ensure that your containerized applications remain secure.

### Practice Labs

To gain hands-on experience with Kubernetes security, consider the following practice labs:

- **Kubernetes Goat**: A hands-on lab for learning Kubernetes security.
- **OWASP WrongSecrets**: A project for learning about secrets management in Kubernetes.
- **kube-hunter**: A tool for hunting down security issues in Kubernetes clusters.

These labs provide practical scenarios and exercises to help you master Kubernetes security best practices.

---
<!-- nav -->
[[01-Introduction to Kubernetes Security Best Practices Part 1|Introduction to Kubernetes Security Best Practices Part 1]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/08-Introduction to Kubernetes Security/Kubernetes Security Best Practices/00-Overview|Overview]] | [[03-Introduction to Kubernetes Security Best Practices Part 3|Introduction to Kubernetes Security Best Practices Part 3]]
