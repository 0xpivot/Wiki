---
course: DevSecOps
topic: Applying Compliance as Code in DevSecOps
tags: [devsecops]
---

## Code Building and Testing Stage

### Static Application Security Testing (SAST)

#### What is SAST?

Static Application Security Testing (SAST) is a type of security testing that analyzes the source code of an application without executing it. SAST tools scan the code for potential security vulnerabilities, such as SQL injection, cross-site scripting (XSS), and buffer overflows.

#### Why is SAST Important?

SAST is crucial because it allows developers to identify and fix security issues early in the development cycle. By catching vulnerabilities during the coding phase, teams can avoid costly and time-consuming fixes later in the process.

#### How Does SAST Work?

SAST tools analyze the codebase using predefined rules and patterns. They can detect potential security issues based on the code structure and logic. For example, a SAST tool might flag a function that constructs a SQL query using user input, which could lead to SQL injection.

#### Real-World Example: CVE-2021-21972

CVE-2021-21972 is a vulnerability in the Apache Struts framework that allows attackers to execute arbitrary code via a crafted Content-Type header. A SAST tool could have detected this vulnerability by analyzing the code that processes HTTP headers and identifying insecure handling of user input.

#### Tools for SAST

Some popular SAST tools include:

- **SonarQube**
- **Fortify**
- **Veracode**
- **Checkmarx**

#### Example Configuration: SonarQube

```yaml
sonar.projectKey=myproject
sonar.projectName=My Project
sonar.projectVersion=1.0
sonar.sources=src
sonar.language=java
```

### Software Composition Analysis (SCA)

#### What is SCA?

Software Composition Analysis (SCA) is a process that identifies open-source components and their licenses in a software project. SCA tools help ensure that the software does not contain any vulnerable or non-compliant components.

#### Why is SCA Important?

SCA is important because many software projects rely on open-source libraries and frameworks. These components can introduce security risks if they are outdated or contain known vulnerabilities. SCA helps teams stay informed about the components they use and ensures compliance with licensing requirements.

#### How Does SCA Work?

SCA tools scan the project dependencies and compare them against a database of known vulnerabilities and licenses. For example, an SCA tool might identify that a project uses an outdated version of a library that contains a known vulnerability.

#### Real-World Example: Log4j Vulnerability (CVE-2021-44228)

The Log4j vulnerability (CVE-2021-44228) affected millions of applications worldwide. An SCA tool could have identified the presence of the vulnerable Log4j library and alerted the team to update it.

#### Tools for SCA

Some popular SCA tools include:

- **Snyk**
- **WhiteSource**
- **Black Duck**
- **JFrog Xray**

#### Example Configuration: Snyk

```yaml
name: My Project
version: 1.0.0
dependencies:
  - name: log4j
    version: 2.14.1
```

### Vulnerability Scanning

#### What is Vulnerability Scanning?

Vulnerability scanning is a process that identifies security weaknesses in a system or application. Vulnerability scanners can detect issues such as misconfigurations, missing patches, and known vulnerabilities.

#### Why is Vulnerability Scanning Important?

Vulnerability scanning is important because it helps teams identify and remediate security issues before they can be exploited. Regular vulnerability scans can ensure that the system remains secure and compliant with industry standards.

#### How Does Vulnerability Scanning Work?

Vulnerability scanners typically perform two types of scans:

1. **Network Scans**: These scans check for vulnerabilities in network devices and services.
2. **Application Scans**: These scans check for vulnerabilities in the application code and configurations.

#### Real-World Example: Heartbleed Bug (CVE-2014-0160)

The Heartbleed bug (CVE-2014-0160) affected OpenSSL and allowed attackers to steal sensitive information from servers. A vulnerability scanner could have detected this issue by checking for the presence of the vulnerable OpenSSL version.

#### Tools for Vulnerability Scanning

Some popular vulnerability scanning tools include:

- **Nessus**
- **Qualys**
- **OpenVAS**
- **Tenable.io**

#### Example Configuration: Nessus

```yaml
scan:
  name: My Scan
  targets:
    - 192.168.1.1
  plugins:
    - id: 12345
      name: SSL Heartbleed
```

---
<!-- nav -->
[[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/02-Build Phase|Build Phase]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/02-Security Governance & Compliance/01-Applying Compliance as Code in DevSecOps/Course Summary/04-Example from Wild Brain Coffee|Example from Wild Brain Coffee]]
