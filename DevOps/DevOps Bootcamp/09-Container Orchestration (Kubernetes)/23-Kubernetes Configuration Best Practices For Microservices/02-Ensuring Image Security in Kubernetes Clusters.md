---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Ensuring Image Security in Kubernetes Clusters

### Background Theory

When deploying applications in a Kubernetes cluster, one of the primary concerns is ensuring that the container images used are free from vulnerabilities. Container images often contain libraries and tools that may have known vulnerabilities, which can be exploited by attackers to compromise the entire cluster. Therefore, it is crucial to perform thorough security and vulnerability scans on these images before deploying them.

### Vulnerability Scanning

#### What is Vulnerability Scanning?

Vulnerability scanning is the process of identifying and assessing security weaknesses in software components. In the context of container images, this involves scanning the image for known vulnerabilities in the underlying libraries and tools.

#### Why is Vulnerability Scanning Important?

Without vulnerability scanning, an attacker could exploit a known vulnerability in a library or tool within the container image. This could lead to unauthorized access, data theft, or even complete control over the host system. By performing regular vulnerability scans, you can identify and mitigate these risks proactively.

#### How Does Vulnerability Scanning Work?

Vulnerability scanning typically involves the following steps:

1. **Image Analysis**: The scanner analyzes the contents of the container image, including all the files, libraries, and dependencies.
2. **Vulnerability Database Check**: The scanner compares the identified components against a database of known vulnerabilities.
3. **Report Generation**: The scanner generates a report detailing any vulnerabilities found, along with their severity and potential impact.

### Tools for Vulnerability Scanning

Several tools are available for performing vulnerability scans on container images:

- **Trivy**: An open-source vulnerability scanner that supports various package managers and container registries.
- **Clair**: A static analyzer for vulnerabilities in application containers.
- **Snyk**: A commercial tool that provides continuous monitoring and automated remediation for container images.

#### Example Using Trivy

Here’s an example of how to use Trivy to scan a container image:

```sh
trivy image my-image:latest
```

This command will scan the `my-image:latest` container image and output any vulnerabilities found.

### Real-World Examples

#### Recent CVEs and Breaches

One notable example is the Log4j vulnerability (CVE-2021-44228), which affected many Java-based applications. If a container image contained a vulnerable version of Log4j, it could be exploited to gain remote code execution. Regular vulnerability scanning would have helped identify and mitigate this risk.

### Scanning Third-Party Images

It is also essential to scan third-party images downloaded from public repositories such as Docker Hub. These images might contain vulnerabilities that could affect your cluster.

#### Example Using Clair

To scan a third-party image using Clair, you can use the following command:

```sh
clair-scanner --app-name my-app --image docker.io/library/nginx:latest
```

This command will scan the `nginx:latest` image from Docker Hub and generate a report.

### How to Prevent / Defend

#### Detection

Regularly scan all container images using tools like Trivy or Clair. Integrate these scans into your CI/CD pipeline to ensure that vulnerabilities are detected early.

#### Prevention

1. **Use Official Images**: Whenever possible, use official images from trusted sources.
2. **Automate Scans**: Automate vulnerability scans as part of your CI/CD pipeline.
3. **Patch Management**: Keep all libraries and tools up-to-date with the latest security patches.

### Code Example

Here’s an example of integrating Trivy into a CI/CD pipeline using GitHub Actions:

```yaml
name: Vulnerability Scan

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout code
      uses: actions/checkout@v2

    - name: Set up Docker Buildx
      uses: docker/setup-buildx-action@v1

    - name: Build and push Docker image
      id: docker_build
      uses: docker/build-push-action@v2
      with:
        context: .
        push: false
        tags: ${{ github.repository }}:latest

    - name: Run Trivy Scan
      run: |
        trivy image ${{ github.repository }}:latest
```

### Non-Root User Containers

### Background Theory

Another critical security best practice is ensuring that containers do not run with root privileges. Running containers with root access poses significant security risks, as a compromised container with root access can potentially take control of the entire host system.

### Why Non-Root Users Matter

Running containers with non-root users minimizes the potential damage that can be caused by a compromised container. If a container is running with root access and is exploited, the attacker can gain full control over the host system. By contrast, a container running with a non-root user has limited permissions and cannot perform critical operations that could compromise the host.

### How to Ensure Non-Root Users

To ensure that containers run with non-root users, you can configure the container to run as a specific user. This can be done by setting the `USER` directive in the Dockerfile or by specifying the user when running the container.

#### Example Dockerfile

Here’s an example of a Dockerfile that sets the user to `nonroot`:

```Dockerfile
FROM python:3.9-slim

# Create a non-root user
RUN groupadd -r nonroot && useradd -r -g nonroot nonroot

# Switch to the non-root user
USER nonroot

# Copy the application code
COPY . /app
WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the application
CMD ["python", "app.py"]
```

### Real-World Examples

#### Recent CVEs and Breaches

In the Equifax breach (CVE-2017-5638), attackers exploited a vulnerability in Apache Struts to gain remote code execution. If the container running Apache Struts had been configured to run as a non-root user, the potential damage could have been significantly reduced.

### How to Prevent / Defend

#### Detection

Ensure that all containers are configured to run as non-root users. You can use tools like `kubectl` to inspect the security context of pods and verify that they are not running as root.

#### Prevention

1. **Configure Dockerfiles**: Always set the `USER` directive in Dockerfiles to a non-root user.
2. **Pod Security Policies**: Use Pod Security Policies in Kubernetes to enforce that containers run as non-root users.
3. **Security Contexts**: Configure security contexts in Kubernetes manifests to specify the user and group IDs for containers.

### Code Example

Here’s an example of a Kubernetes deployment manifest that specifies a non-root user:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
      - name: my-app-container
        image: my-image:latest
        securityContext:
          runAsUser: 1000
          runAsGroup: 3000
```

### Conclusion

Ensuring the security of container images and running containers with non-root users are critical best practices in Kubernetes. By following these guidelines, you can significantly reduce the risk of security breaches and protect your cluster from potential attacks. Regular vulnerability scanning and proper configuration of user permissions are essential steps in maintaining a secure Kubernetes environment.

### Practice Labs

For hands-on experience with Kubernetes security best practices, consider the following labs:

- **Kubernetes Goat**: A hands-on lab that simulates various Kubernetes security challenges.
- **OWASP WrongSecrets**: A series of challenges that focus on securing Kubernetes deployments.
- **kube-hunter**: A tool that helps identify security misconfigurations in Kubernetes clusters.

These labs provide practical scenarios and exercises to reinforce the concepts covered in this chapter.

---
<!-- nav -->
[[01-Introduction to Kubernetes Configuration Best Practices for Microservices|Introduction to Kubernetes Configuration Best Practices for Microservices]] | [[DevOps/DevOps Bootcamp/09-Container Orchestration (Kubernetes)/23-Kubernetes Configuration Best Practices For Microservices/00-Overview|Overview]] | [[03-Environment Variables in Kubernetes Pods|Environment Variables in Kubernetes Pods]]
