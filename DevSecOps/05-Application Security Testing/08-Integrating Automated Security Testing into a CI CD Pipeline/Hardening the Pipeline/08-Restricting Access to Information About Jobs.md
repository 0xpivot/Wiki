---
course: DevSecOps
topic: Integrating Automated Security Testing into a CI CD Pipeline
tags: [devsecops]
---

## Restricting Access to Information About Jobs

In the context of a CI/CD pipeline, one critical aspect of securing your environment is ensuring that sensitive information about your jobs is not accessible to unauthorized users. This includes details such as project names, branch names, and job names. Let's delve into why this is important and how to properly restrict access.

### Importance of Restricting Access

Consider the following scenario: an attacker gains access to your CI/CD pipeline and starts querying information about your jobs. They might be able to gather enough data to understand the structure of your project, identify critical branches, and potentially discover sensitive operations being performed by your jobs. This information can be used to craft targeted attacks, such as injecting malicious code into your build process or disrupting your deployment workflows.

### Example from Microsoft Documentation

Microsoft's documentation highlights a common issue where anonymous badge access is enabled by default in private projects. This means that even anonymous users can query information such as project names, branch names, and job names. This is a significant security risk because it exposes sensitive details about your project to anyone who knows the URL of the badge.

#### Code Example: Enabling Anonymous Badge Access

```yaml
# Example of a CI/CD pipeline configuration with anonymous badge access enabled
jobs:
  - job: Build
    pool:
      vmImage: 'ubuntu-latest'
    steps:
      - script: echo Hello, world!
        displayName: 'Display message'
```

#### How to Prevent / Defend

To mitigate this risk, you should disable anonymous badge access and ensure that only authenticated users have access to this information. Here’s how you can configure your pipeline to disable anonymous badge access:

#### Code Example: Disabling Anonymous Badge Access

```yaml
# Example of a CI/CD pipeline configuration with anonymous badge access disabled
jobs:
  - job: Build
    pool:
      vmImage: 'ubuntu-latest'
    steps:
      - script: echo Hello, world!
        displayName: 'Display message'
    permissions:
      anonymous: false
```

### Dynamic Test Environments

Another crucial aspect of securing your CI/CD pipeline is the use of dynamic test environments. These environments are spun up on demand and torn down after use, ensuring that sensitive data is not left exposed in a persistent environment.

#### Why Use Dynamic Environments?

Dynamic environments provide several benefits:
- **Isolation**: Each test runs in a fresh environment, reducing the risk of contamination from previous tests.
- **Resource Efficiency**: You only use resources when needed, saving costs.
- **Security**: Since the environment is destroyed after use, there is no residual data left behind.

#### Example: Spinning Up a Dynamic Environment

Let's consider a scenario where you need to spin up a dynamic environment for testing a web application. You can use tools like Docker or Kubernetes to manage these environments.

#### Code Example: Using Docker Compose for Dynamic Environments

```yaml
# docker-compose.yml
version: '3'
services:
  web:
    image: my-web-app:latest
    ports:
      - "8080:80"
  db:
    image: postgres:latest
    environment:
      POSTGRES_PASSWORD: mysecretpassword
```

#### How to Prevent / Defend

Ensure that access controls are in place for these dynamic environments. This includes:
- **Network Isolation**: Ensure that the test environment is isolated from other parts of your network.
- **Access Control**: Only allow authorized users to access the test environment.
- **Environment Hardening**: Ensure that the operating system and images used are up to date and free from known vulnerabilities.

#### Code Example: Securing a Docker Environment

```yaml
# docker-compose.yml
version: '3'
services:
  web:
    image: my-web-app:latest
    ports:
      - "8080:80"
    security_opt:
      - seccomp:unconfined
  db:
    image: postgres:latest
    environment:
      POSTGRES_PASSWORD: mysecretpassword
    security_opt:
      - seccomp:unconfined
```

### Network Communication

Ensuring that all communication within your CI/CD pipeline is secure is paramount. This includes both internal communication between different components of your pipeline and external communication with artifact registries and other services.

#### End-to-End Encryption

One of the most effective ways to secure network communication is through end-to-end encryption. This ensures that data is encrypted from the source to the destination, preventing eavesdropping and man-in-the-middle attacks.

#### Example: Using TLS for Artifact Transfer

When a build server builds an artifact and pushes it to a registry server, ensure that the transfer is encrypted using TLS. This prevents attackers from intercepting the artifact during transit.

#### Code Example: Configuring TLS for Artifact Transfer

```http
POST /v2/my-repo/my-image/upload HTTP/1.1
Host: registry.example.com
Authorization: Bearer <token>
Content-Type: application/octet-stream
Accept: application/json
User-Agent: Docker/19.03.12 go/go1.12.10 git-commit/48a6621 kernel/4.15.0-106-generic os/linux arch/amd64 Uploader/1.0
X-Docker-Checksum: sha256:<checksum>
X-Docker-Checksum-Payload: sha256:<payload_checksum>

<binary data>
```

#### How to Prevent / Defend

To ensure secure communication, follow these best practices:
- **Use Strong Certificates**: Avoid self-signed certificates and use certificates issued by trusted Certificate Authorities (CAs).
- **Validate Endpoints**: Ensure that the endpoints you are communicating with are trusted and validated.

#### Code Example: Validating Endpoints

```python
import requests

response = requests.get('https://registry.example.com/v2/', verify='/path/to/ca-bundle.crt')
print(response.status_code)
```

### Summary

Securing your CI/CD pipeline involves multiple layers of protection, including restricting access to job information, using dynamic test environments, and ensuring secure network communication. By implementing these measures, you can significantly reduce the risk of unauthorized access and protect your project's sensitive information.

### Practice Labs

For hands-on experience with integrating automated security testing into a CI/CD pipeline, consider the following labs:
- **PortSwigger Web Security Academy**: Offers comprehensive modules on securing CI/CD pipelines.
- **OWASP Juice Shop**: Provides a vulnerable web application that you can use to practice securing your pipeline.
- **DVWA (Damn Vulnerable Web Application)**: Another excellent resource for practicing security in CI/CD pipelines.

By following these guidelines and practicing with real-world scenarios, you can ensure that your CI/CD pipeline is robust and secure.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/08-Integrating Automated Security Testing into a CI CD Pipeline/Hardening the Pipeline/07-Keeping Software and Plugins Updated|Keeping Software and Plugins Updated]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/08-Integrating Automated Security Testing into a CI CD Pipeline/Hardening the Pipeline/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/08-Integrating Automated Security Testing into a CI CD Pipeline/Hardening the Pipeline/09-Restricting Access to Jobs|Restricting Access to Jobs]]
