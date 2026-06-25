---
course: DevSecOps
topic: Getting Started with the DevSecOps Bootcamp
tags: [devsecops]
---

## Introduction to DevSecOps

### What is DevSecOps?

DevSecOps is a set of practices that integrates security into the DevOps process. Traditionally, security was often treated as a separate phase in the software development lifecycle (SDLC), but with DevSecOps, security is embedded throughout the entire development and deployment pipeline. This approach ensures that security is not an afterthought but a continuous part of the development process.

#### Why is DevSecOps Important?

In today’s fast-paced software development environment, organizations are increasingly adopting agile methodologies and DevOps practices to deliver software quickly and efficiently. However, this speed can sometimes come at the cost of security. DevSecOps aims to bridge this gap by ensuring that security is considered at every stage of the development process.

### Core Application Security Concepts

Before diving into the specifics of DevSecOps, it is crucial to understand some fundamental application security concepts. These concepts form the basis of DevSecOps and help developers and non-developers alike to grasp the importance of security in the context of applications and systems.

#### Understanding Security Threats

Security threats can take many forms, including:

- **Injection Attacks**: SQL injection, cross-site scripting (XSS), etc.
- **Broken Authentication**: Weak password policies, session management vulnerabilities.
- **Sensitive Data Exposure**: Inadequate encryption, improper handling of sensitive data.
- **Cross-Site Request Forgery (CSRF)**: Exploiting trusted relationships between users and web applications.
- **Security Misconfiguration**: Improperly configured servers, frameworks, databases, etc.
- **Insecure Deserialization**: Malicious input leading to remote code execution.
- **Insufficient Logging & Monitoring**: Lack of proper logging and monitoring mechanisms.

These threats can lead to significant security breaches, such as the Equifax breach in 2017, which exposed sensitive data of over 143 million people due to a vulnerability in Apache Struts. Understanding these threats is essential for implementing effective security measures.

### Learning Security Concepts Before Tools

One of the key differences between DevSecOps and traditional security training is the emphasis on understanding the underlying security concepts before diving into the tools. Many courses focus solely on teaching how to use security scanning tools, but without a solid understanding of the security principles, developers may not fully appreciate why certain actions are necessary.

#### Example: SQL Injection

Consider the following example of a SQL injection attack:

```sql
SELECT * FROM users WHERE username = 'admin' OR '1'='1';
```

This query bypasses authentication by exploiting a vulnerability in the SQL statement. A developer who understands the concept of SQL injection would know to use parameterized queries to prevent such attacks:

```sql
SELECT * FROM users WHERE username = ?;
```

Here, `?` is a placeholder for a parameter, which is then safely substituted by the database driver.

### DevSecOps Concepts

#### Continuous Integration and Continuous Deployment (CI/CD)

Continuous Integration (CI) and Continuous Deployment (CD) are integral parts of DevSecOps. CI involves automatically building and testing code changes, while CD extends this to automatically deploying the code to production. Integrating security into these processes ensures that security checks are performed continuously.

#### Security Scanning Types

There are several types of security scans that can be automated in a DevSecOps pipeline:

- **Static Application Security Testing (SAST)**: Analyzes the source code for security vulnerabilities.
- **Dynamic Application Security Testing (DAST)**: Tests the running application for security vulnerabilities.
- **Interactive Application Security Testing (IAST)**: Combines elements of both SAST and DAST to provide more comprehensive coverage.
- **Dependency Check**: Ensures that third-party libraries used in the application are free from known vulnerabilities.

### Automation Tools in DevSecOps

#### Static Application Security Testing (SAST)

SAST tools analyze the source code to identify potential security vulnerabilities. One popular SAST tool is SonarQube. Here is an example of how to configure SonarQube:

```yaml
sonar.projectKey=my_project
sonar.sources=src
sonar.language=java
```

This configuration specifies the project key, the source directory, and the language.

#### Dynamic Application Security Testing (DAST)

DAST tools test the running application to identify security vulnerabilities. One popular DAST tool is OWASP ZAP. Here is an example of how to run ZAP from the command line:

```bash
zap.sh -cmd -config api.key=your_api_key -t http://localhost:8080 -r report.html
```

This command runs ZAP against the specified URL and generates a report.

### How to Prevent / Defend Against Security Threats

#### Secure Coding Practices

Secure coding practices are essential for preventing security threats. Here are some best practices:

- **Input Validation**: Validate all user inputs to ensure they meet expected formats and lengths.
- **Parameterized Queries**: Use parameterized queries to prevent SQL injection attacks.
- **Error Handling**: Implement proper error handling to avoid exposing sensitive information.
- **Encryption**: Use strong encryption algorithms to protect sensitive data.

#### Example: Secure Input Validation

Consider the following insecure code snippet:

```python
username = request.form['username']
password = request.form['password']

# Insecure query
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
```

This code is vulnerable to SQL injection. The secure version uses parameterized queries:

```python
from flask import request
import sqlite3

username = request.form['username']
password = request.form['password']

conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# Secure query
query = "SELECT * FROM users WHERE username = ? AND password = ?"
cursor.execute(query, (username, password))
```

#### Configuration Hardening

Configuration hardening involves securing the environment in which the application runs. This includes securing servers, databases, and other infrastructure components.

##### Example: Securing an Nginx Server

Here is an example of an Nginx configuration file with security hardening:

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        root /var/www/html;
        index index.html index.htm;
    }

    # Disable directory listing
    autoindex off;

    # Enable HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

    # Enable Content Security Policy
    add_header Content-Security-Policy "default-src 'self'";
}
```

This configuration disables directory listing, enables HTTP Strict Transport Security (HSTS), and sets a Content Security Policy (CSP).

### Real-World Examples

#### Equifax Breach (CVE-2017-5638)

The Equifax breach in 2017 was caused by a vulnerability in Apache Struts. The attackers exploited a flaw in the REST plugin, which allowed them to execute arbitrary code on the server. This breach highlights the importance of keeping third-party libraries up to date and performing regular security audits.

#### Capital One Breach (CVE-2019-11510)

The Capital One breach in 2019 was caused by a misconfigured web application firewall (WAF). The attacker exploited a vulnerability in the WAF to access sensitive customer data. This breach underscores the importance of proper configuration management and regular security assessments.

### Hands-On Labs

To gain practical experience with DevSecOps, consider the following hands-on labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice web application security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security skills.
- **DVWA (Damn Vulnerable Web Application)**: Another intentionally vulnerable web application for security training.
- **WebGoat**: An interactive training application for learning about web application security.

### Conclusion

Understanding the core concepts of application security is essential for anyone involved in the development process. By integrating security into the DevOps pipeline through DevSecOps, organizations can ensure that security is a continuous part of the development process. This approach not only helps in identifying and mitigating security threats but also fosters a culture of security awareness among developers and non-developers alike.

---
<!-- nav -->
[[08-Introduction to DevSecOps Part 1|Introduction to DevSecOps Part 1]] | [[DevSecOps/DevSecOps Bootcamp/01-DevSecOps Introduction/05-Getting Started with the DevSecOps Bootcamp/DevSecOps Bootcamp Curriculum Overview/00-Overview|Overview]] | [[10-Introduction to Kubernetes Platform Security|Introduction to Kubernetes Platform Security]]
