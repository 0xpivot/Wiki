---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Container Repository Management

A container repository is a storage location for container images. These repositories allow teams to store, manage, and distribute container images efficiently.

### Types of Repositories

There are two main types of container repositories:

1. **Public Repositories**: Open to everyone, such as Docker Hub.
2. **Private Repositories**: Restricted to specific organizations or teams, often hosted internally.

### Public Repositories: Docker Hub

Docker Hub is the largest public registry of container images. It allows users to store and share images publicly or privately.

#### Example: Pushing an Image to Docker Hub

To push an image to Docker Hub, you first need to tag it with your Docker Hub username and repository name:

```bash
docker tag myapp:latest myusername/myapp:latest
```

Then, log in to Docker Hub:

```bash
docker login
```

Finally, push the image:

```bash
docker push myusername/myapp:latest
```

### Private Repositories: Harbor

Harbor is an open-source container registry that extends the functionality of Docker Registry. It provides additional features such as security scanning, user management, and replication.

#### Example: Setting Up Harbor

To set up Harbor, you can use a Helm chart:

```bash
helm repo add harbor https://helm.hub.rancher.com
helm install harbor harbor/harbor
```

Once installed, you can push images to Harbor using similar commands as Docker Hub:

```bash
docker tag myapp:latest localhost:8080/myproject/myapp:latest
docker push localhost:8080/myproject/myapp:latest
```

### Real-World Example: CVE-2021-21315

CVE-2021-21315 is a vulnerability in Docker that allows attackers to escalate privileges and execute arbitrary code. This highlights the importance of keeping container images and the underlying systems up-to-date.

### How to Prevent / Defend

1. **Regular Updates**: Keep container images and the underlying systems updated to the latest versions.
   
2. **Security Scanning**: Use tools like Clair or Trivy to scan container images for known vulnerabilities.

3. **Access Controls**: Implement strict access controls to ensure only authorized personnel can push or pull images.

### Complete Example: Full Workflow

Here’s a complete example of building, tagging, pushing, and pulling a container image:

#### Building and Tagging

```bash
docker build -t myapp:latest .
docker tag myapp:latest myusername/myapp:latest
```

#### Logging In and Pushing

```bash
docker login
docker push myusername/myapp:latest
```

#### Pulling the Image

```bash
docker pull myusername/myapp:latest
```

### How to Prevent / Defend

1. **Secure Build Process**: Ensure the build process is secure and free from vulnerabilities.
   
2. **Immutable Infrastructure**: Treat container images as immutable artifacts to avoid unexpected changes.

3. **Automated Testing**: Integrate automated testing into the CI/CD pipeline to catch issues early.

### Conclusion

Containers provide a powerful solution for packaging and deploying applications consistently across different environments. By leveraging container repositories, teams can efficiently manage and distribute container images. Understanding the underlying technologies and best practices is essential for effective and secure containerization.

### Practice Labs

For hands-on experience with containerization and repository management, consider the following labs:

- **Kubernetes Goat**: Focuses on Kubernetes security and container orchestration.
- **OWASP WrongSecrets**: Provides challenges related to securing containerized applications.
- **CloudGoat**: Offers scenarios for securing cloud-based container deployments.

These labs will help solidify your understanding and practical skills in containerization and repository management.

---
<!-- nav -->
[[04-What is a Container|What is a Container]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/03-Containerization Fundamentals And Repository Management/00-Overview|Overview]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/03-Containerization Fundamentals And Repository Management/06-Practice Questions & Answers|Practice Questions & Answers]]
