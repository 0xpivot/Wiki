---
course: DevSecOps
topic: Image Scanning - Build Secure Docker Images
tags: [devsecops]
---

## Introduction to Image Scanning in DevSecOps

In the realm of DevSecOps, ensuring the security of Docker images is paramount. One of the key practices is to integrate automated security scanning into the Continuous Integration/Continuous Deployment (CI/CD) pipeline. This ensures that vulnerabilities are detected early in the development lifecycle, reducing the risk of deploying insecure applications.

### What is Image Scanning?

Image scanning involves analyzing Docker images for known vulnerabilities, misconfigurations, and other security issues. This process is typically automated and integrated into the CI/CD pipeline to ensure that images are scanned as part of the build process.

### Why is Image Scanning Important?

- **Early Detection**: Detecting vulnerabilities early in the development cycle allows teams to address them promptly, reducing the risk of deploying insecure applications.
- **Compliance**: Many organizations are required to comply with regulatory standards that mandate regular security assessments of their software.
- **Security Posture**: Regularly scanning images helps maintain a strong security posture by identifying and mitigating potential threats.

### How Does Image Scanning Work?

Image scanning tools analyze Docker images for known vulnerabilities using databases such as the National Vulnerability Database (NVD) and Common Vulnerabilities and Exposures (CVE). They also check for misconfigurations and other security issues.

### Tools for Image Scanning

Several tools are available for image scanning, including:

- **Trivy**: An open-source tool that scans container images, file systems, and Git repositories for vulnerabilities.
- **Clair**: A static analyzer for vulnerabilities in application containers.
- **Anchore**: A comprehensive solution for securing container images.

For this discussion, we will focus on Trivy, an open-source tool that is widely used for image scanning.

---
<!-- nav -->
[[02-Introduction to Image Scanning in DevSecOps Part 1|Introduction to Image Scanning in DevSecOps Part 1]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Configure Automated Security Scanning in Application Image/00-Overview|Overview]] | [[04-Introduction to Image Scanning in DevSecOps Part 3|Introduction to Image Scanning in DevSecOps Part 3]]
