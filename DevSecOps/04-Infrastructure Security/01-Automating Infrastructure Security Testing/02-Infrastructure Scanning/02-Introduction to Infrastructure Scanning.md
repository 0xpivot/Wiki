---
course: DevSecOps
topic: Automating Infrastructure Security Testing
tags: [devsecops]
---

## Introduction to Infrastructure Scanning

Infrastructure scanning is a critical component of DevSecOps, enabling teams to identify vulnerabilities and security issues within their infrastructure as part of their continuous integration and delivery processes. This chapter focuses on two prominent tools: Nikto and OWASP ZAP (Zed Attack Proxy). Both tools are open-source and widely used in the industry for web application security testing.

### Nikto: Comprehensive Web Server Scanner

Nikto is an open-source web server scanner that checks for over 6700 potentially dangerous files/CGIs, versions, and issues on web servers. It can be used to find default files, outdated software, and other potential security risks.

#### Why Use Nikto?

Nikto is particularly useful because it can quickly scan a large number of web servers and provide detailed reports on potential vulnerabilities. This makes it ideal for organizations that need to maintain a high level of security across multiple web servers.

#### How Nikto Works

Nikto operates by sending HTTP requests to the target web server and analyzing the responses. It uses a database of known vulnerabilities and patterns to identify potential issues. Here’s a step-by-step breakdown of how Nikto works:

1. **Initialization**: Nikto starts by connecting to the target web server and gathering basic information such as the server type and version.
2. **Scanning**: Nikto sends a series of HTTP requests to the server, checking for specific files, directories, and CGI scripts that may indicate vulnerabilities.
3. **Analysis**: Based on the responses, Nikto determines whether the server is vulnerable to known issues and generates a report.

#### Example Usage of Nikto

To demonstrate how Nikto works, let's consider a simple example. Suppose we want to scan a web server at `http://example.com`.

```bash
nikto -h http://example.com
```

This command will initiate a scan of the specified web server. Nikto will then output a detailed report of any vulnerabilities found.

#### Real-World Example: CVE-2021-3504

CVE-2021-3504 is a vulnerability in the Apache Struts framework that allows remote attackers to execute arbitrary code. Nikto can help identify if a server is using an outdated version of Apache Struts that is vulnerable to this issue.

```bash
nikto -h http://example.com | grep "Apache Struts"
```

If Nikto detects an outdated version of Apache Struts, it will alert you to the potential vulnerability.

#### How to Prevent / Defend Against Nikto Findings

To defend against vulnerabilities identified by Nikto, follow these steps:

1. **Update Software**: Ensure all web server software and dependencies are up-to-date.
2. **Secure Configuration**: Harden the configuration of your web server to minimize exposure to known vulnerabilities.
3. **Regular Scans**: Schedule regular scans with Nikto to catch new vulnerabilities as they emerge.

#### Secure Coding Fixes

Here’s an example of how to update a vulnerable version of Apache Struts:

**Vulnerable Code:**
```java
// Vulnerable code using old version of Apache Struts
import org.apache.struts2.dispatcher.ng.filter.StrutsPrepareAndExecuteFilter;

public class MyApplication {
    public void init() {
        // Initialize Struts filter
        FilterRegistration.Dynamic strutsFilter = servletContext.addFilter("struts", StrutsPrepareAndExecuteFilter.class);
        strutsFilter.addMappingForUrlPatterns(EnumSet.of(DispatcherType.REQUEST), true, "/*");
    }
}
```

**Fixed Code:**
```java
// Fixed code using updated version of Apache Struts
import org.apache.struts2.dispatcher.ng.filter.StrutsPrepareAndExecuteFilter;

public class MyApplication {
    public void init() {
        // Initialize Struts filter
        FilterRegistration.Dynamic strutsFilter = servletContext.addFilter("struts", StrutsPrepareAndExecuteFilter.class);
        strutsFilter.addMappingForUrlPatterns(EnumSet.of(  DispatcherType.REQUEST), true, "/*");
    }
}
```

### OWASP ZAP: Automated Security Testing Tool

OWASP ZAP (Zed Attack Proxy) is another powerful tool for web application security testing. It is designed to be highly flexible and can be integrated into continuous integration pipelines to automate security testing.

#### Why Use OWASP ZAP?

OWASP ZAP is widely used because it provides a comprehensive set of features for identifying and exploiting vulnerabilities in web applications. It supports both manual and automated testing, making it suitable for a wide range of use cases.

#### How OWASP ZAP Works

OWASP ZAP operates by intercepting and modifying HTTP requests and responses between the client and the server. It can be configured to automatically test for a variety of vulnerabilities, including SQL injection, cross-site scripting (XSS), and others.

#### Example Usage of OWASP ZAP

To demonstrate how OWASP ZAP works, let's consider a scenario where we want to scan a web application at `http://example.com`.

1. **Start ZAP**: Launch OWASP ZAP and configure it to listen on a proxy port (e.g., 8080).
2. **Configure Browser**: Set your browser to use the ZAP proxy.
3. **Scan Application**: Navigate through the web application using your browser. ZAP will intercept and analyze the traffic.
4. **Generate Report**: Once the scan is complete, generate a report to review the findings.

Here’s a sample command to start ZAP in headless mode:

```bash
zap.sh -cmd -port 8080 -host 0.0.0.0 -config api.key=your_api_key -config api.addrs.addr.name=.* -config api.addrs.addr.regex=true -config view.mode=full
```

#### Real-World Example: CVE-2022-22965

CVE-2022-22965 is a vulnerability in the Log4j library that allows remote code execution. OWASP ZAP can help identify if a web application is using a vulnerable version of Log4j.

```bash
zap-cli --apikey your_api_key spider -u http://example.com
zap-cli --apikey your_api_key scan -u http://example.com
zap-cli --apikey your_api_key report -o report.html -t html
```

These commands will initiate a spider scan, followed by an active scan, and finally generate a report.

#### How to Prevent / Defend Against OWASP ZAP Findings

To defend against vulnerabilities identified by OWASP ZAP, follow these steps:

1. **Patch Vulnerabilities**: Apply patches for known vulnerabilities in libraries and frameworks.
2. **Input Validation**: Implement strict input validation to prevent injection attacks.
3. **Security Headers**: Configure security headers such as Content-Security-Policy (CSP) to mitigate XSS attacks.

#### Secure Coding Fixes

Here’s an example of how to update a vulnerable version of Log4j:

**Vulnerable Code:**
```java
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class MyApplication {
    private static final Logger logger = LogManager.getLogger(MyApplication.class);

    public void logMessage(String message) {
        logger.info(message);
    }
}
```

**Fixed Code:**
```java
import org.apache.logging.log4j.LogManager;
import org.apache.logging.log4j.Logger;

public class MyApplication {
    private static final Logger logger = LogManager.getLogger(MyApplication.class);

    public void logMessage(String message) {
        logger.info(message.replaceAll("\\$", ""));
    }
}
```

### Integrating Nikto and OWASP ZAP into CI/CD Pipelines

Integrating Nikto and OWASP ZAP into continuous integration and delivery (CI/CD) pipelines ensures that security testing is performed automatically and consistently.

#### Example CI/CD Pipeline

Here’s an example of how to integrate Nikto and OWASP ZAP into a CI/CD pipeline using Jenkins:

1. **Install Tools**: Ensure Nikto and OWASP ZAP are installed on the Jenkins agent.
2. **Pipeline Script**: Create a Jenkins pipeline script to run the security tests.

```groovy
pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                sh 'mvn clean package'
            }
        }
        stage('Security Test') {
            steps {
                sh 'nikto -h http://example.com > nikto_report.txt'
                sh 'zap-cli --apikey your_api_key spider -u http://example.com'
                sh 'zap-cli --apikey your_api_key scan -u http://example.com'
                sh 'zap-cli --apikey your_api_key report -o zap_report.html -t html'
            }
        }
    }
    post {
        always {
            archiveArtifacts artifacts: 'nikto_report.txt, zap_report.html', allowEmptyArchive: true
        }
    }
}
```

This pipeline script performs a build, runs Nikto and OWASP ZAP security tests, and archives the reports.

### Conclusion

Automating infrastructure security testing with tools like Nikto and OWASP ZAP is essential for maintaining a secure web application environment. By integrating these tools into your CI/CD pipeline, you can ensure that security testing is performed consistently and automatically, helping to catch and address vulnerabilities early in the development process.

### Practice Labs

For hands-on practice with Nikto and OWASP ZAP, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs for learning web security concepts, including the use of Nikto and OWASP ZAP.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills, including the use of security scanners.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for practicing security testing techniques.

By completing these labs, you can gain practical experience with Nikto and OWASP ZAP, enhancing your ability to identify and mitigate security vulnerabilities in web applications.

---
<!-- nav -->
[[01-Introduction to Infrastructure Scanning in DevSecOps|Introduction to Infrastructure Scanning in DevSecOps]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/01-Automating Infrastructure Security Testing/04-Infrastructure Scanning/00-Overview|Overview]] | [[03-Infrastructure Scanning|Infrastructure Scanning]]
