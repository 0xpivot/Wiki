---
course: DevSecOps
topic: Automating Infrastructure Security Testing
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain what an infrastructure scanner can identify and provide an example of a common misconfiguration it might detect.**

An infrastructure scanner can identify several types of issues including known misconfigurations, missing hardening measures, and published vulnerabilities. A common misconfiguration it might detect is an open directory browsing feature on a web server. This allows anyone to browse through the directory structure and potentially access sensitive files that should be protected. For example, if a directory on a web server is configured to allow directory listing, an infrastructure scanner would flag this as a potential security risk.

**Q2. How does an infrastructure scanner detect known vulnerabilities in software components?**

An infrastructure scanner detects known vulnerabilities by fingerprinting the software components used in the infrastructure. This involves analyzing headers, version numbers, and other identifiers to determine the specific software and its version. The scanner then compares these details against a database of known vulnerabilities. For instance, if a web server is using an old version of Apache that has known vulnerabilities, the scanner will flag this issue. Recent examples include vulnerabilities like CVE-2021-41773 in Microsoft Exchange Server, where scanners would identify the vulnerable version and alert the user.

**Q3. Why is it important for an infrastructure scanner to allow suppression of false positives?**

It is crucial for an infrastructure scanner to allow suppression of false positives because extensive testing often leads to numerous alerts, some of which may not represent actual security risks. False positives can overwhelm security teams and lead to alert fatigue, causing genuine threats to be overlooked. By allowing suppression, the scanner helps maintain focus on true security issues. For example, if a scanner frequently flags a non-critical service as vulnerable due to outdated software, but the team knows it's not a risk, they can suppress these alerts to avoid unnecessary attention.

**Q4. At what stages of the DevSecOps lifecycle should infrastructure scanning be performed?**

Infrastructure scanning should be performed at multiple stages of the DevSecOps lifecycle to ensure comprehensive security coverage:

- **Build Phase**: When the application or container is built and ready for deployment, a scanner can check for any misconfigurations or vulnerabilities before the artifact is deployed.
- **Deploy Phase**: Immediately after deployment, when the application or infrastructure is running, a scanner can verify that the deployed environment is secure.
- **Continuous Monitoring**: Post-deployment, ongoing monitoring can detect new vulnerabilities or changes in the environment that might affect security.

By integrating scanning into these phases, organizations can catch and address security issues early in the development cycle, reducing the risk of vulnerabilities making it to production.

**Q5. Why is it recommended to test the environment that is closest to production, even though shifting security left is encouraged?**

While shifting security left is encouraged to catch issues early, testing the environment that is closest to production is critical because it ensures that the actual configuration and behavior of the system in production are accurately assessed. Development and test environments may differ significantly from production due to differences in configurations, dependencies, and operational settings. Testing in an environment that closely mimics production helps identify issues that might arise only in the live environment. However, if a staging or acceptance environment can be made to perfectly replicate the production setup, testing there is equally effective.

**Q6. Describe the sidecar testing pattern and how it is used in the context of infrastructure scanning.**

The sidecar testing pattern involves using separate containers to run and scan applications dynamically. Here’s how it works:

1. **Application Container**: A container is spun up to run the application or service that needs to be tested.
2. **Scanner Containers**: Other containers are used to perform various types of scans, such as network scans, vulnerability scans, or security compliance checks.
3. **Dynamic Scans**: Once the application is running, the scanner containers perform their respective scans to identify any security issues.
4. **Cleanup**: After the scans are completed, the application container is shut down to clean up resources.

This approach allows for isolated and controlled testing of the application in a dynamic environment, ensuring that the scans are accurate and do not interfere with the production system. Tools like Nikto and OWASP ZAP can be used within these scanner containers to perform comprehensive security assessments.

**Q7. How can tools like Nikto and OWASP ZAP be integrated into a CI/CD pipeline for automated security testing?**

Tools like Nikto and OWASP ZAP can be integrated into a CI/CD pipeline to automate security testing as follows:

- **Nikto Integration**: Nikto can be run as part of a pipeline step after the application is deployed. The pipeline script can invoke Nikto to scan the web server for known vulnerabilities and misconfigurations. Results can be logged and analyzed for any security issues.
  
  ```bash
  nikto -h http://localhost:8080
  ```

- **OWASP ZAP Integration**: OWASP ZAP can be set up to automatically scan the application once it is deployed. ZAP can be configured to run in headless mode and generate reports that can be reviewed by the security team.

  ```bash
  zap-cli -t http://localhost:8080 -r report.html
  ```

By automating these steps, the pipeline ensures that every deployment undergoes a security scan, helping to maintain a high level of security throughout the development and deployment processes.

---
<!-- nav -->
[[03-Infrastructure Scanning|Infrastructure Scanning]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/01-Automating Infrastructure Security Testing/04-Infrastructure Scanning/00-Overview|Overview]]
