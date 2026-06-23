---
course: DevSecOps
topic: Image Scanning - Build Secure Docker Images
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the importance of securing the Docker image in addition to securing the application code.**

The Docker image represents the entire runtime environment of the application, including the operating system and all installed dependencies. Even if the application code is secure, vulnerabilities in the Docker image can expose the application to attacks. For instance, an insecure Docker image might contain outdated libraries with known vulnerabilities, allowing attackers to exploit these weaknesses. This is akin to placing a secure application in an insecure environment, which negates the security measures implemented in the code. Therefore, securing the Docker image is crucial to ensure the overall security of the application.

**Q2. How would you exploit a Docker image with known vulnerabilities?**

To exploit a Docker image with known vulnerabilities, an attacker would typically follow these steps:

1. **Identify Vulnerabilities**: Use tools like Docker Scout, Trivy, or other security scanners to identify known vulnerabilities in the Docker image.
   
2. **Exploit Known Vulnerabilities**: Once vulnerabilities are identified, the attacker can use exploits corresponding to those vulnerabilities. For example, if the Docker image contains a library with a known buffer overflow vulnerability, the attacker can craft input data to trigger the overflow and gain unauthorized access or execute arbitrary code.

3. **Gain Access**: Exploiting the vulnerability can lead to gaining unauthorized access to the container or the host system, depending on the nature of the vulnerability and the privileges of the container.

4. **Escalate Privileges**: After gaining initial access, the attacker might attempt to escalate their privileges to perform more damaging actions, such as stealing sensitive data or deploying malicious software.

**Q3. What is Docker Scout and how does it help in securing Docker images?**

Docker Scout is a tool provided by Docker that helps in scanning Docker images for security vulnerabilities. It checks the image layers for any dependencies that have known security vulnerabilities. By integrating Docker Scout into the CI/CD pipeline, developers can automatically detect and address security issues early in the development process. This ensures that the Docker images are free from known vulnerabilities before deployment, thereby enhancing the security posture of the application.

**Q4. How would you configure a pipeline to use Trivy for scanning Docker images?**

To configure a pipeline to use Trivy for scanning Docker images, follow these steps:

1. **Add a Job for Trivy Scan**: Add a new job in your pipeline configuration file (e.g., `.gitlab-ci.yml`) that runs Trivy to scan the Docker image.

```yaml
stages:
  - build
  - scan
  - deploy

build_image:
  stage: build
  script:
    - docker build -t myapp .
    - docker tag myapp $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG

scan_image:
  stage: scan
  image: trivyci/trivy:latest
  services:
    - docker:dind
  script:
    - docker login -u $CI_REGISTRY_USER -p $CI_REGISTRY_PASSWORD $CI_REGISTRY
    - trivy image --exit-code 1 --severity CRITICAL,HIGH $CI_REGISTRY_IMAGE:$CI_COMMIT_REF_SLUG
  dependencies:
    - build_image
  allow_failure: true
```

2. **Configure Dependencies**: Ensure that the Trivy job depends on the `build_image` job to run after the image is built.

3. **Set Exit Code and Severity Levels**: Configure Trivy to fail the job if it finds critical or high-severity vulnerabilities (`--exit-code 1 --severity CRITICAL,HIGH`).

4. **Allow Failure**: Set `allow_failure: true` to prevent the pipeline from failing if the scan detects issues, allowing developers to address them without blocking the workflow.

**Q5. Why is it important to configure security scanning tools to fail the build when critical vulnerabilities are found?**

Configuring security scanning tools to fail the build when critical vulnerabilities are found is crucial because it enforces a strict security policy. When a build fails due to critical vulnerabilities, it immediately alerts the development team to address the issues before proceeding further. This prevents insecure code from being deployed, reducing the risk of security breaches. Additionally, it promotes a culture of security awareness and responsibility among developers, ensuring that security is an integral part of the development process.

**Q6. What recent real-world examples highlight the importance of securing Docker images?**

One notable example is the Log4j vulnerability (CVE-2021-44228), which affected numerous applications and systems, including Docker images. Many Docker images contained vulnerable versions of Log4j, leading to potential remote code execution attacks. This incident highlighted the importance of regularly scanning Docker images for known vulnerabilities and keeping dependencies up-to-date. Another example is the exploitation of vulnerabilities in Kubernetes clusters, where insecure Docker images played a significant role in enabling attacks. These incidents underscore the necessity of robust security practices in managing Docker images.

---
<!-- nav -->
[[09-Image Scanning - Build Secure Docker Images|Image Scanning - Build Secure Docker Images]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Configure Automated Security Scanning in Application Image/00-Overview|Overview]]
