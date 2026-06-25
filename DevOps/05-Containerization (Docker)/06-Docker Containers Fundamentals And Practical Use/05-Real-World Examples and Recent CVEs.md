---
course: DevOps
topic: DevOps Bootcamp
tags: [devops]
---

## Real-World Examples and Recent CVEs

### Example: Docker Image Vulnerabilities

One of the most significant risks associated with Docker images is the presence of vulnerabilities. For instance, the CVE-2021-21366 vulnerability in the `libcurl` library affected many Docker images, leading to potential remote code execution.

#### How to Prevent / Defend

- **Image Scanning**: Use tools like Trivy or Clair to scan Docker images for vulnerabilities.
- **Regular Updates**: Keep Docker images up-to-date with the latest security patches.

### Example: Unauthorized Access to Nexus Repository

Unauthorized access to a Nexus repository can lead to data theft or tampering. For example, in 2022, a breach occurred where unauthorized users gained access to a Nexus repository and downloaded sensitive artifacts.

#### How to Prevent / Defend

- **Strong Authentication**: Use strong authentication mechanisms, such as multi-factor authentication (MFA).
- **Access Controls**: Implement strict access controls and regularly review user permissions.

---
<!-- nav -->
[[05-Pushing and Fetching Docker Images tofrom Nexus|Pushing and Fetching Docker Images tofrom Nexus]] | [[DevOps/DevOps Bootcamp/05-Containerization (Docker)/06-Docker Containers Fundamentals And Practical Use/00-Overview|Overview]] | [[07-Setting Up Nexus as a Docker Container|Setting Up Nexus as a Docker Container]]
