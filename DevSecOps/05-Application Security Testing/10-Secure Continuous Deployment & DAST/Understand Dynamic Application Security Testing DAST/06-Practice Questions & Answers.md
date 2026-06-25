---
course: DevSecOps
topic: Secure Continuous Deployment & DAST
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. What is the difference between Static Application Security Testing (SAST) and Dynamic Application Security Testing (DAST)?**

Dynamic Application Security Testing (DAST) involves testing the security of an application while it is running, focusing on the external interfaces such as the UI, without accessing the internal code. This is akin to black box testing, where the tester interacts with the application as an end-user might, attempting to identify vulnerabilities by exploiting the application from the outside. 

Static Application Security Testing (SAST), on the other hand, involves analyzing the source code, binaries, or byte code of an application to identify potential security flaws. SAST is performed without executing the code, making it a white box approach where the internal workings of the application are thoroughly examined.

**Q2. How does a DAST tool like OWASP ZAP work?**

OWASP ZAP (Zed Attack Proxy) is a popular DAST tool that operates by interacting with the running application as an end-user would. After deploying the application on a server and making it publicly accessible, ZAP can be pointed at the website to perform security scans. ZAP performs various types of security checks, including SQL injection, cross-site scripting (XSS), and other common web vulnerabilities. It attempts different hacking techniques and reports where it succeeded or failed, providing a detailed summary of the security status of the application.

For example, if ZAP identifies that an application leaks sensitive information in error messages, it will report this finding, indicating that attackers could potentially use this information to further exploit the system.

**Q3. Why is integrating DAST into a CI/CD pipeline important?**

Integrating DAST into a CI/CD pipeline is crucial for ensuring that security vulnerabilities are identified and addressed early in the software development lifecycle. By performing DAST tests after deploying the application to a test environment, teams can catch security issues before the application reaches production. This helps prevent vulnerabilities from being exposed to the public, reducing the risk of breaches and associated costs.

For instance, if a recent vulnerability such as CVE-2021-44228 (Log4j) had been detected during DAST testing, the team could have fixed it before the application went live, avoiding potential exploitation by attackers.

**Q4. How can you configure a DAST step in a CI/CD pipeline using OWASP ZAP?**

To configure a DAST step using OWASP ZAP in a CI/CD pipeline, follow these steps:

1. **Deploy the Application**: Deploy the application to a test environment.
2. **Run ZAP Scan**: Configure a job in your pipeline to run ZAP against the deployed application.
3. **Check Results**: Analyze the results of the ZAP scan to determine if any security issues were found.
4. **Promote to Production**: If no critical issues are found, proceed to deploy the application to the production environment.

Here’s an example of how you might configure this in a Jenkins pipeline:

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                // Build steps
            }
        }
        stage('Deploy Test') {
            steps {
                sh 'deploy-to-test.sh'
            }
        }
        stage('DAST with ZAP') {
            steps {
                sh 'zap-baseline.py -t http://test-server-url -r zap-report.html'
            }
        }
        stage('Deploy Production') {
            when {
                expression { return currentBuild.result == 'SUCCESS' }
            }
            steps {
                sh 'deploy-to-prod.sh'
            }
        }
    }
}
```

In this example, `zap-baseline.py` is a script that runs ZAP against the specified URL (`http://test-server-url`) and generates a report (`zap-report.html`). The pipeline will only proceed to the production deployment if the DAST step completes successfully.

**Q5. What are some common vulnerabilities that DAST can help identify?**

DAST can help identify a variety of common web application vulnerabilities, including:

- **SQL Injection**: Exploiting vulnerabilities in the database layer to execute arbitrary SQL commands.
- **Cross-Site Scripting (XSS)**: Injecting malicious scripts into web pages viewed by other users.
- **Cross-Site Request Forgery (CSRF)**: Forcing an authenticated user to execute unwanted actions on a web application.
- **Sensitive Data Exposure**: Leaking sensitive data through error messages or improper handling of credentials.
- **Broken Authentication**: Weaknesses in authentication mechanisms that allow attackers to compromise passwords, keys, or session tokens.

By identifying these vulnerabilities, DAST helps ensure that the application is secure against common attack vectors. For example, the Heartbleed vulnerability (CVE-2014-0160) could have been detected earlier if DAST had been integrated into the development process, allowing for timely remediation before widespread exploitation.

---
<!-- nav -->
[[05-Understanding Static and Dynamic Application Security Testing|Understanding Static and Dynamic Application Security Testing]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/Understand Dynamic Application Security Testing DAST/00-Overview|Overview]]
