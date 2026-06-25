---
course: DevSecOps
topic: Designing DevSecOps for Test, Release, and Operate SDLC Phases
tags: [devsecops]
---

## Hardening Images to the CIS Standard

### Background Theory

Hardening an image to the Center for Internet Security (CIS) standard is a critical practice in DevSecOps, particularly during the deploy phase. The CIS standard provides a set of benchmarks designed to enhance the security posture of systems and applications. By adhering to these standards, organizations can significantly reduce their attack surface and mitigate potential vulnerabilities.

The CIS standard covers various aspects of system security, including:

- **Configuration Management**: Ensuring that systems are configured securely and consistently.
- **Identity and Access Management**: Managing user accounts, permissions, and access controls.
- **System Maintenance**: Regularly updating and patching systems to address known vulnerabilities.
- **Monitoring and Logging**: Implementing logging and monitoring mechanisms to detect and respond to security incidents.

### Why Harden to CIS Standards?

Hardenning images to the CIS standard is crucial because it helps organizations achieve several key security objectives:

- **Reduced Attack Surface**: By following the CIS guidelines, unnecessary services, ports, and protocols are disabled, reducing the number of potential entry points for attackers.
- **Standardized Security Practices**: The CIS standard provides a widely recognized and accepted framework for security practices, making it easier to implement consistent security measures across different environments.
- **Compliance**: Many regulatory requirements and industry standards reference the CIS benchmarks as a best practice for securing systems.

### How to Harden Images to CIS Standards

To harden images to the CIS standard, you need to follow a systematic approach. This involves:

1. **Selecting a Base Image**: Choose a base image that is already hardened to the CIS standard. Many container registries offer such images.
2. **Applying CIS Benchmarks**: Apply the CIS benchmarks to the selected image. This typically involves configuring the image according to the CIS guidelines.
3. **Automating the Process**: Use automation tools to ensure that the hardening process is repeatable and consistent.

#### Example: Hardening a Docker Image

Let's walk through an example of hardening a Docker image to the CIS standard using a base image from the `CIS` registry.

```dockerfile
# Use a base image that is already hardened to the CIS standard
FROM cisco/cis-hardened-ubuntu:latest

# Install necessary packages
RUN apt-get update && \
    apt-get install -y <necessary-packages>

# Apply additional CIS hardening steps
RUN sed -i 's/^#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config && \
    systemctl restart sshd

# Expose only necessary ports
EXPOSE 80 443

# Run the application
CMD ["<application-command>"]
```

### Real-World Examples

Recent breaches and CVEs have highlighted the importance of hardening images to the CIS standard. For instance:

- **CVE-2021-44228 (Log4Shell)**: This vulnerability affected many systems due to unpatched and insecure configurations. Organizations that had hardened their images to the CIS standard were less likely to be impacted.
- **SolarWinds Supply Chain Attack (CVE-2020-1014)**: This attack exploited vulnerabilities in software supply chains. Hardened images would have made it more difficult for attackers to compromise systems.

### Common Pitfalls

While hardening images to the CIS standard is beneficial, there are some common pitfalls to avoid:

- **Over-reliance on Automated Tools**: While automation tools can help, they should not replace manual review and testing.
- **Ignoring Custom Configurations**: Custom configurations may introduce new vulnerabilities that are not covered by the CIS standard.
- **Neglecting Regular Updates**: Hardening is not a one-time task; regular updates and patches are essential to maintain security.

### How to Prevent / Defend

#### Detection

To detect whether an image is properly hardened to the CIS standard, you can use tools like:

- **CIS Benchmarks Scanners**: Tools like `cis-benchmark-scanner` can scan images and report compliance with the CIS benchmarks.
- **Container Security Scanners**: Tools like `Trivy`, `Clair`, and `Snyk` can scan images for vulnerabilities and misconfigurations.

#### Prevention

To prevent vulnerabilities, follow these steps:

- **Use Hardened Base Images**: Always start with a base image that is hardened to the CIS standard.
- **Apply CIS Benchmarks**: Ensure that all images are configured according to the CIS benchmarks.
- **Regular Audits**: Conduct regular audits to ensure ongoing compliance with the CIS standard.

#### Secure-Coding Fixes

Here’s an example of a vulnerable configuration and its secure counterpart:

**Vulnerable Configuration:**

```dockerfile
FROM ubuntu:latest

RUN apt-get update && \
    apt-get install -y openssh-server

RUN echo "PermitRootLogin yes" >> /etc/ssh/sshd_config

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
```

**Secure Configuration:**

```dockerfile
FROM cisco/cis-hardened-ubuntu:latest

RUN apt-get update && \
    apt-get install -y openssh-server

RUN sed -i 's/^#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config && \
    systemctl restart sshd

EXPOSE 22

CMD ["/usr/sbin/sshd", "-D"]
```

### Configuration Hardening

To further harden the configuration, consider the following steps:

- **Disable Unnecessary Services**: Disable any services that are not required for the application to function.
- **Configure SELinux/AppArmor**: Use SELinux or AppArmor to enforce strict security policies.
- **Enable Logging and Monitoring**: Configure logging and monitoring to detect and respond to security incidents.

### Complete Example

Here’s a complete example of a hardened Docker image and its corresponding deployment script:

#### Dockerfile

```dockerfile
# Use a base image that is already hardened to the CIS standard
FROM cisco/cis-hardened-ubuntu:latest

# Install necessary packages
RUN apt-get update && \
    apt-get install -y nginx

# Apply additional CIS hardening steps
RUN sed -i 's/^#PermitRootLogin yes/PermitRootLogin no/' /etc/ssh/sshd_config && \
    systemctl restart sshd

# Expose only necessary ports
EXPOSE 80 443

# Run the application
CMD ["nginx", "-g", "daemon off;"]
```

#### Deployment Script

```bash
#!/bin/bash

# Build the Docker image
docker build -t my-secure-image .

# Push the image to a registry
docker push my-secure-image

# Deploy the image to a Kubernetes cluster
kubectl apply -f deployment.yaml
```

#### Kubernetes Deployment YAML

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-secure-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-secure-app
  template:
    metadata:
      labels:
        app: my-secure-app
    spec:
      containers:
      - name: my-secure-container
        image: my-secure-image
        ports:
        - containerPort: 80
```

### Conclusion

Hardening images to the CIS standard is a critical practice in DevSecOps. By following the CIS benchmarks, organizations can significantly reduce their attack surface and mitigate potential vulnerabilities. Regular audits and updates are essential to maintain security. Using hardened base images and applying CIS benchmarks consistently can help ensure that your deployments are secure.

### Practice Labs

For hands-on experience with hardening images to the CIS standard, consider the following labs:

- **PortSwigger Web Security Academy**: Offers modules on securing web applications, including hardening Docker images.
- **OWASP Juice Shop**: Provides a vulnerable web application that can be used to practice hardening techniques.
- **CloudGoat**: Focuses on cloud security and includes scenarios for hardening images in cloud environments.

By practicing these techniques in real-world scenarios, you can gain a deeper understanding of how to effectively harden images to the CIS standard.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/09-Miscellaneous/03-Designing DevSecOps for Test, Release, and Operate SDLC Phases/01-DevSecOps in the Deploy Phase/00-Overview|Overview]] | [[02-Testing Security Certificates in the Deploy Phase|Testing Security Certificates in the Deploy Phase]]
