---
course: DevSecOps
topic: Image Scanning - Build Secure Docker Images
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the significance of CVEs in the context of third-party libraries and dependencies.**

CVEs (Common Vulnerabilities and Exposures) are identifiers for publicly known vulnerabilities in software. In the context of third-party libraries and dependencies, CVEs provide a standardized way to track and communicate about security flaws. This is crucial because many applications rely on external libraries and dependencies, and vulnerabilities in these components can affect the overall security of the application. By referencing CVEs, developers and security teams can quickly identify and prioritize the necessary actions to mitigate risks associated with known vulnerabilities.

**Q2. How would you exploit a vulnerability in a Debian Docker image, and what steps can be taken to mitigate this risk?**

To exploit a vulnerability in a Debian Docker image, an attacker might leverage a known vulnerability listed in a CVE, such as a buffer overflow or a weak cryptographic implementation. They could craft a payload that targets the specific flaw, potentially gaining unauthorized access or executing arbitrary code within the container.

To mitigate this risk, the following steps can be taken:

1. **Regularly Update Images**: Ensure that the base images used in Docker containers are regularly updated to the latest versions that include security patches.
2. **Use Trusted Sources**: Use official and trusted repositories for downloading Docker images.
3. **Security Scanning Tools**: Utilize security scanning tools like Trivy to detect vulnerabilities in the Docker images and address them proactively.
4. **Least Privilege Principle**: Run containers with the least privileges necessary to perform their tasks, reducing the potential impact of a successful attack.

**Q3. Why is it important to update dependencies in `package.json` files, and what challenges might arise during this process?**

Updating dependencies in `package.json` files is crucial because it ensures that the application uses the latest versions of its dependencies, which often contain important security patches and bug fixes. This helps in mitigating risks associated with known vulnerabilities.

Challenges that might arise during this process include:

1. **Breaking Changes**: Major version updates can introduce breaking changes that require significant refactoring of the application code.
2. **Dependency Conflicts**: Updating one dependency might cause conflicts with other dependencies that rely on older versions.
3. **Testing Requirements**: After updating dependencies, extensive testing is required to ensure that the application continues to function correctly and securely.

**Q4. What is the purpose of secret scanning in Docker images, and how can it be performed effectively?**

Secret scanning in Docker images aims to detect sensitive information, such as API keys, passwords, and private keys, that might have been inadvertently included in the image. This is important because exposing such secrets can lead to unauthorized access and compromise the security of the system.

Effective secret scanning can be performed using tools like Trivy, which can scan Docker images for secrets and report findings. To perform secret scanning effectively:

1. **Integrate Scanning into CI/CD Pipeline**: Automate secret scanning as part of the continuous integration and delivery (CI/CD) pipeline to catch issues early.
2. **Use Comprehensive Scanning Tools**: Employ tools that support a wide range of secret patterns and formats.
3. **Review and Remediate**: Regularly review the findings and take appropriate action to remove or protect sensitive data.

**Q5. Explain how to fix a high-severity issue in a Docker image, referencing a recent real-world example.**

To fix a high-severity issue in a Docker image, follow these steps:

1. **Identify the Vulnerability**: Use a security scanning tool like Trivy to identify the specific vulnerability and its severity.
2. **Update the Base Image**: If the vulnerability is in the base image, update it to a newer version that includes the necessary security patches.
3. **Test the Updated Image**: Thoroughly test the updated image to ensure that it functions correctly and securely.

A recent real-world example is the OpenSSL vulnerability (CVE-2022-3602) that affected several versions of OpenSSL. To fix this, one would need to update the Docker image to use a version of OpenSSL that includes the patch for this vulnerability. For instance, if the Docker image was using an outdated version of OpenSSL, updating the base image to a more recent version would resolve the issue.

**Q6. How would you handle a situation where a security issue has no known fix yet, and what are some alternative strategies to mitigate the risk?**

When a security issue has no known fix yet, the following strategies can be employed to mitigate the risk:

1. **Workarounds**: Implement temporary workarounds, such as modifying firewall rules or adjusting configurations to limit exposure.
2. **Monitoring**: Increase monitoring efforts to detect any unusual activity that might indicate exploitation of the vulnerability.
3. **Isolation**: Isolate the affected component to minimize the potential impact of a successful attack.
4. **Alternative Solutions**: Explore alternative solutions or software that do not have the same vulnerability.

For example, if a library has a high-severity issue with no known fix, one could temporarily disable the feature that relies on the vulnerable library or switch to an alternative library that does not have the same vulnerability.

**Q7. Describe the process of fixing a high-level issue in a third-party library used in an application, and provide an example.**

To fix a high-level issue in a third-party library used in an application, follow these steps:

1. **Identify the Vulnerability**: Use a tool like RetireJS to identify the specific vulnerability in the library.
2. **Update the Library Version**: Update the version of the library in the `package.json` file to a version that addresses the vulnerability.
3. **Test the Application**: Thoroughly test the application to ensure that the update does not break any existing functionality.
4. **Verify Dependencies**: Check if the updated library version affects any other dependencies and update them accordingly.

An example is fixing a vulnerability in the JSON WebToken library. Suppose the application uses JSON WebToken version 0.4.0, which has critical and high-level issues. The process would involve:

1. Identifying the specific issues using RetireJS.
2. Updating the JSON WebToken version to a newer version that addresses the issues.
3. Testing the application to ensure that the update does not break any existing functionality.
4. Checking and updating any other dependencies that rely on JSON WebToken.

By following these steps, the application can be made more secure against known vulnerabilities in third-party libraries.

---
<!-- nav -->
[[10-Image Scanning and Building Secure Docker Images|Image Scanning and Building Secure Docker Images]] | [[DevSecOps/DevSecOps Bootcamp/06-Container & Kubernetes Security/03-Image Scanning - Build Secure Docker Images/Analyze Fix Security Issues from Findings in Application Image/00-Overview|Overview]]
