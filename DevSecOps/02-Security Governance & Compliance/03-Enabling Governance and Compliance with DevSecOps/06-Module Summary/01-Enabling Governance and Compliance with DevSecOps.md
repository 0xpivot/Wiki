---
course: DevSecOps
topic: Enabling Governance and Compliance with DevSecOps
tags: [devsecops]
---

## Enabling Governance and Compliance with DevSecOps

### Introduction to DevSecOps

DevSecOps is an approach that integrates security practices into the DevOps pipeline, ensuring that security is a continuous and integral part of the development process. This approach aims to improve the overall security posture of an organization by embedding security controls throughout the software development lifecycle (SDLC).

### Understanding the DevOps Pipeline

Before diving into DevSecOps, it's essential to understand the traditional DevOps Continuous Integration and Continuous Deployment (CI/CD) pipeline. The typical stages in a CI/CD pipeline include:

- **Source Control Management (SCM):** Version control systems like Git are used to manage the source code.
- **Build:** Automated build processes compile the source code into executable artifacts.
- **Test:** Automated testing ensures that the code meets functional and non-functional requirements.
- **Deploy:** Automated deployment processes push the code to production environments.
- **Operate:** Monitoring and maintenance of the deployed application.

### Transitioning to DevSecOps

In a DevSecOps pipeline, security is integrated into each of these stages. The goal is to identify and mitigate security risks early in the development cycle, reducing the cost and complexity of fixing vulnerabilities later.

#### Key Stages in a DevSecOps Pipeline

1. **Source Code Analysis:**
   - **Static Application Security Testing (SAST):** Tools like SonarQube, Fortify, and Checkmarx analyze the source code for potential security vulnerabilities.
   - **Dependency Scanning:** Tools like Snyk and WhiteSource scan for known vulnerabilities in third-party libraries and dependencies.

2. **Build Stage:**
   - **Security Policies:** Implement security policies using tools like Open Policy Agent (OPA) to ensure that builds comply with organizational security standards.
   - **Container Image Scanning:** Tools like Clair and Trivy scan container images for known vulnerabilities.

3. **Test Stage:**
   - **Dynamic Application Security Testing (DAST):** Tools like Burp Suite and ZAP test the application for runtime vulnerabilities.
   - **Interactive Application Security Testing (IAST):** Tools like Contrast Security and Arachni provide insights into the application’s behavior during testing.

4. **Deploy Stage:**
   - **Infrastructure as Code (IaC) Scanning:** Tools like Checkov and TFSec scan infrastructure definitions (e.g., Terraform, CloudFormation) for security misconfigurations.
   - **Configuration Management:** Ensure that configurations are secure using tools like Ansible and Puppet.

5. **Operate Stage:**
   - **Runtime Security:** Tools like Aqua Security and Twistlock monitor the application at runtime for security threats.
   - **Logging and Monitoring:** Implement centralized logging and monitoring using tools like ELK Stack and Prometheus to detect and respond to security incidents.

### Automation in DevSecOps

Automation is a cornerstone of DevSecOps. By automating security checks, organizations can ensure that security is consistently applied across the entire pipeline. However, it's important to recognize that not every stage can be fully automated.

#### Areas Suitable for High Levels of Automation

1. **Source Code Analysis:**
   - **Example Tool:** SonarQube
   - **Code Example:**
     ```yaml
     jobs:
       build:
         runs-on: ubuntu-latest
         steps:
           - name: Checkout code
             uses: actions/checkout@v2
           - name: Run SonarQube analysis
             uses: sonarsource/sonarcloud-github-action@v1
             with:
               token: ${{ secrets.SONAR_TOKEN }}
               args: |
                 -Dsonar.projectKey=my_project_key
                 -Dsonar.sources=.
     ```
   - **Explanation:** This GitHub Actions workflow integrates SonarQube into the CI/CD pipeline, automatically analyzing the source code for security vulnerabilities.

2. **Dependency Scanning:**
   - **Example Tool:** Snyk
   - **Code Example:**
     ```yaml
     jobs:
       build:
         runs-on: ubuntu-latest
         steps:
           - name: Checkout code
             uses: actions/checkout@v2
           - name: Install Snyk
             run: npm install -g snyk
           - name: Run Snyk scan
             run: snyk test --file=package.json
     ```
   - **Explanation:** This workflow integrates Snyk into the CI/CD pipeline, automatically scanning dependencies for known vulnerabilities.

#### Areas Still Reliant on Manual Checks

1. **Threat Modeling (TREP):**
   - **Explanation:** Threat modeling involves identifying potential threats and vulnerabilities in the system architecture. While tools like Microsoft's STRIDE and OWASP's Threat Modeling Framework can assist, the process often requires human expertise to accurately assess and mitigate threats.
   - **Mermaid Diagram:**
     ```mermaid
graph TD;
       A[Threat Modeling] --> B[Identify Assets];
       B --> C[Identify Threat Agents];
       C --> D[Identify Threats];
       D --> E[Assess Likelihood and Impact];
       E --> F[Develop Mitigation Strategies];
```

2. **Compliance Audits:**
   - **Explanation:** Compliance audits involve verifying that the system adheres to regulatory requirements. These audits often require detailed documentation and human review to ensure compliance.
   - **Example:** PCI DSS compliance requires regular audits to verify that the system meets the Payment Card Industry Data Security Standard.

### Implementing Security Controls

To effectively implement security controls in a DevSecOps pipeline, it's crucial to start with areas that can be highly automated and gradually expand to more complex areas.

#### Reporting Security Issues

The first step is to report any security issues identified during the pipeline. This can be achieved through:

- **Automated Reports:** Tools like SonarQube and Snyk generate reports detailing security vulnerabilities.
- **Integration with Issue Trackers:** Integrate security reports with issue trackers like Jira or GitHub Issues to ensure that security issues are tracked and addressed.

#### Blocking Controls

Once security issues are reported, the next step is to enforce blocking controls. This ensures that the pipeline does not proceed until security issues are resolved.

- **Example Tool:** GitHub Actions
- **Code Example:**
  ```yaml
  jobs:
    build:
      runs-on: ubuntu-latest
      steps:
        - name: Checkout code
          uses: actions/checkout@v2
        - name: Run SonarQube analysis
          uses: sonarsource/sonarcloud-github-action@v1
          with:
            token: ${{ secrets.SONAR_TOKEN }}
            args: |
              -Dsonar.projectKey=my_project_key
              -Dsonar.sources=.
        - name: Fail on security issues
          run: |
            if [ "$(curl -s https://sonarcloud.io/api/issues/search?project=my_project_key&statuses=OPEN&types=VULNERABILITY | jq '.total')" -gt 0 ]; then
              echo "Security issues found. Build failed."
              exit 1
            fi
  ```
- **Explanation:** This workflow fails the build if any security issues are found, ensuring that the pipeline does not proceed until the issues are resolved.

### Real-World Examples

#### Recent CVEs and Breaches

1. **CVE-2021-44228 (Log4j Vulnerability):**
   - **Explanation:** The Log4j vulnerability (CVE-2021-44228) affected millions of Java applications worldwide. Organizations that had implemented dependency scanning tools like Snyk were able to quickly identify and remediate the vulnerability.
   - **Code Example:**
     ```yaml
     jobs:
       build:
         runs-on: ubuntu-latest
         steps:
           - name: Checkout code
             uses: actions/checkout@v2
           - name: Install Snyk
             run: npm install -g snyk
           - name: Run Snyk scan
             run: snyk test --file=pom.xml
           - name: Fail on critical vulnerabilities
             run: |
               if [ "$(snyk test --file=pom.xml --json | jq '.testResult.vulnerabilities[] | select(.severity == "critical") | length')" -gt 0 ]; then
                 echo "Critical vulnerabilities found. Build failed."
                 exit 1
               fi
     ```
   - **Explanation:** This workflow fails the build if any critical vulnerabilities are found, ensuring that the pipeline does not proceed until the issues are resolved.

2. **SolarWinds Supply Chain Attack:**
   - **Explanation:** The SolarWinds supply chain attack compromised thousands of organizations by inserting malicious code into SolarWinds software updates. Organizations that had implemented strict dependency management and runtime security measures were less likely to be affected.
   - **Code Example:**
     ```yaml
     jobs:
       build:
         runs-on: ubuntu-latest
         steps:
           - name: Checkout code
             uses: actions/checkout@v2
           - name: Install Snyk
             run: npm install -g snyk
           - name: Run Snyk scan
             run: snyk test --file=pom.xml
           - name: Fail on critical vulnerabilities
             run: |
               if [ "$(snyk test --file=pom.xml --json | jq '.testResult.vulnerabilities[] | select(.severity == "critical") | length')" -gt 0 ]; then
                 echo "Critical vulnerabilities found. Build failed."
                 exit 1
               fi
     ```
   - **Explanation:** This workflow fails the build if any critical vulnerabilities are found, ensuring that the pipeline does not proceed until the issues are resolved.

### How to Prevent / Defend

#### Detection

To detect security issues in a DevSecOps pipeline, organizations should:

- **Implement Automated Security Scans:** Use tools like SonarQube, Snyk, and Trivy to automatically scan for security vulnerabilities.
- **Centralize Logging and Monitoring:** Use tools like ELK Stack and Prometheus to centralize logging and monitoring, enabling real-time detection of security incidents.

#### Prevention

To prevent security issues in a DevSecOps pipeline, organizations should:

- **Enforce Security Policies:** Use tools like Open Policy Agent (OPA) to enforce security policies across the pipeline.
- **Implement Secure Coding Practices:** Train developers in secure coding practices and use static analysis tools to identify and mitigate security vulnerabilities.

#### Secure-Coding Fixes

To demonstrate secure-coding fixes, consider the following example:

- **Vulnerable Code:**
  ```java
  public class User {
    private String password;

    public void setPassword(String password) {
      this.password = password;
    }

    public String getPassword() {
      return password;
    }
  }
  ```
- **Explanation:** This code stores passwords in plain text, which is a significant security vulnerability.
- **Secure Code:**
  ```java
  import java.security.MessageDigest;
  import java.security.NoSuchAlgorithmException;

  public class User {
    private String passwordHash;

    public void setPassword(String password) throws NoSuchAlgorithmException {
      MessageDigest md = MessageDigest.getInstance("SHA-256");
      byte[] hash = md.digest(password.getBytes());
      this.passwordHash = new String(hash);
    }

    public String getPasswordHash() {
      return passwordHash;
    }
  }
  ```
- **Explanation:** This code stores passwords as SHA-256 hashes, significantly improving security.

#### Configuration Hardening

To harden configurations in a DevSecOps pipeline, organizations should:

- **Use Infrastructure as Code (IaC) Scanning Tools:** Use tools like Checkov and TFSec to scan infrastructure definitions for security misconfigurations.
- **Implement Secure Configurations:** Use tools like Ansible and Puppet to enforce secure configurations across the pipeline.

### Conclusion

By integrating security into the DevOps pipeline, organizations can significantly improve their overall security posture. While not every stage can be fully automated, starting with areas that can be highly automated and gradually expanding to more complex areas is a practical approach. By implementing security controls, detecting and preventing security issues, and hardening configurations, organizations can effectively enable governance and compliance in a DevSecOps environment.

### Practice Labs

For hands-on experience with DevSecOps, consider the following practice labs:

- **PortSwigger Web Security Academy:** Focuses on web application security and includes modules on DevSecOps.
- **OWASP Juice Shop:** A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application):** A PHP/MySQL web application that demonstrates web application vulnerabilities.
- **WebGoat:** An interactive training application designed to teach web application security lessons.

These labs provide practical experience in implementing DevSecOps principles and can help solidify your understanding of the concepts covered in this module.

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/03-Enabling Governance and Compliance with DevSecOps/06-Module Summary/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/03-Enabling Governance and Compliance with DevSecOps/06-Module Summary/02-Practice Questions & Answers|Practice Questions & Answers]]
