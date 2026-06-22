---
course: DevSecOps
topic: Secure Continuous Deployment & DAST
tags: [devsecops]
---

## Practice Questions & Answers

**Q1. Explain the purpose of integrating ZAP (Zed Attack Proxy) into a CI/CD pipeline and describe how it contributes to the security of web applications.**

The purpose of integrating ZAP into a CI/CD pipeline is to automate the process of identifying security vulnerabilities in web applications during the development lifecycle. By incorporating ZAP, teams can detect security issues early, ensuring that the application remains secure throughout its development and deployment stages. ZAP performs dynamic analysis, which involves actively probing the application to identify potential security weaknesses such as SQL injection, cross-site scripting (XSS), and others. This proactive approach helps in mitigating risks and enhancing the overall security posture of the application.

**Q2. How would you configure a ZAP baseline scan in a CI/CD pipeline using a Docker image? Provide an example of the necessary commands and configurations.**

To configure a ZAP baseline scan in a CI/CD pipeline using a Docker image, follow these steps:

1. Define a stage in the pipeline where the ZAP scan will be executed.
2. Ensure the application is deployed and running before initiating the ZAP scan.
3. Use the official ZAP Docker image (`owasp/zap2docker-stable`).
4. Set the target URL of the application to be scanned.
5. Run the ZAP baseline scan with specific parameters.

Here is an example configuration:

```yaml
stages:
  - deploy
  - scan

deploy_test:
  stage: deploy
  script:
    - echo "Deploying application..."
  artifacts:
    paths:
      - /path/to/deployed/app

zap_scan:
  stage: scan
  dependencies:
    - deploy_test
  image: owasp/zap2docker-stable
  script:
    - zap-baseline.py -t http://<public_ip>:<port> -g -I -x baseline.xml
  artifacts:
    paths:
      - baseline.xml
```

In this example, `zap-baseline.py` is used to run the baseline scan. The `-t` flag specifies the target URL, `-g` generates the default configuration file, `-I` ignores warnings, and `-x` outputs the report in XML format.

**Q3. Why is it important to regenerate the default configuration file for ZAP, and how does this affect the scan process?**

Regenerating the default configuration file for ZAP is important to ensure that the scan process uses a consistent and known configuration. This is particularly useful when there is an existing `.ZAP` folder with custom configurations that might interfere with the scan process. By regenerating the default configuration file, you avoid potential conflicts and ensure that the scan is performed under controlled conditions. This step helps in maintaining the reliability and accuracy of the scan results.

**Q4. How would you handle the ZAP report generation and export it as an artifact in a CI/CD pipeline?**

Handling ZAP report generation and exporting it as an artifact involves the following steps:

1. Ensure the ZAP scan generates the report in the desired format (e.g., XML).
2. Copy the report from ZAP's working directory to the current directory of the job execution environment.
3. Specify the report file in the pipeline's artifacts configuration to ensure it is exported.

Here is an example of how to achieve this:

```yaml
zap_scan:
  stage: scan
  dependencies:
    - deploy_test
  image: owasp/zap2docker-stable
  script:
    - mkdir -p /zap/wrk
    - zap-baseline.py -t http://<public_ip>:<port> -g -I -x /zap/wrk/baseline.xml
    - cp /zap/wrk/baseline.xml .
  artifacts:
    paths:
      - baseline.xml
```

In this example, the report is generated in `/zap/wrk/baseline.xml`, and then copied to the current directory (`.`) to be included in the artifacts.

**Q5. Describe the difference between a baseline scan and a full scan in ZAP, and explain why you might choose one over the other in a CI/CD pipeline.**

A baseline scan in ZAP is a quick, shallow scan designed to identify obvious and easily detectable security issues. It is less resource-intensive and faster, making it suitable for frequent integration into a CI/CD pipeline. A full scan, on the other hand, is more comprehensive and thorough, involving active probing and testing of the application. Full scans are typically more time-consuming and can potentially alter the application state.

In a CI/CD pipeline, you might choose a baseline scan for regular, automated checks to quickly identify and address common security issues. For more detailed and thorough security assessments, you might opt for a full scan in a dedicated pipeline that runs periodically or on specific occasions, ensuring it does not slow down the main development workflow.

**Q6. How would you fix the issue of a missing Content Security Policy (CSP) header in a web application, and explain the importance of CSP in web security?**

To fix the issue of a missing Content Security Policy (CSP) header, you can add the CSP header to your web application's responses. Here’s an example using the Helmet middleware in a Node.js application:

```javascript
const helmet = require('helmet');
const express = require('express');
const app = express();

app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'", "'unsafe-inline'"], // Adjust as needed
    styleSrc: ["'self'", "'unsafe-inline'"], // Adjust as needed
    imgSrc: ["'self'", 'data:', 'https://*'], // Adjust as needed
  }
}));

// Other middleware and routes...

app.listen(3000, () => {
  console.log('Server is running on port 3000');
});
```

CSP is crucial in web security because it helps mitigate various types of attacks, including cross-site scripting (XSS). By defining a strict policy, you can control which sources of content are allowed to be loaded in the browser, thereby reducing the risk of malicious scripts being injected and executed. This enhances the overall security of the web application by providing an additional layer of defense against common web vulnerabilities.

---
<!-- nav -->
[[12-Secure Continuous Deployment & Dynamic Application Security Testing (DAST)|Secure Continuous Deployment & Dynamic Application Security Testing (DAST)]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/Configure Automated DAST Scans in CICD Pipeline/00-Overview|Overview]]
