---
course: DevSecOps
topic: Automating Infrastructure Security Testing
tags: [devsecops]
---

## Automating Infrastructure Security Testing

### Introduction to Infrastructure Security Testing

Automating infrastructure security testing is a critical component of DevSecOps practices. It ensures that security checks are integrated into the continuous integration and deployment (CI/CD) pipeline, allowing teams to identify and mitigate vulnerabilities early in the development lifecycle. One popular tool for automating web application security testing is **Nikto**. In this section, we will explore how to integrate Nikto into your CI/CD pipeline using the sidecar testing pattern.

### What is Nikto?

Nikto is an open-source web server scanner that performs comprehensive security checks on web servers. It can detect various types of vulnerabilities, including misconfigurations, outdated software, and known vulnerabilities. Nikto is widely used because of its ease of use and effectiveness in identifying potential security issues.

#### Why Use Nikto?

- **Comprehensive Scanning**: Nikto performs a wide range of tests, covering both common and less common vulnerabilities.
- **Ease of Integration**: Nikto can be easily integrated into CI/CD pipelines, making it a valuable tool for automated security testing.
- **Open Source**: Being open source, Nikto benefits from community contributions and continuous improvements.

### Setting Up Nikto in Your CI/CD Pipeline

To integrate Nikto into your CI/CD pipeline, you need to follow these steps:

1. **Add Nikto to Your Repository**: Include the necessary scripts and configurations for running Nikto in your Git repository.
2. **Commit and Push Changes**: Commit the changes to your local repository and push them to the remote Git server.
3. **Trigger the Build**: Ensure that the build process is triggered automatically after pushing the changes.
4. **Run Nikto**: Configure the build process to run Nikto during the appropriate stage.

#### Example Workflow

Let's walk through an example workflow using a hypothetical CI/CD pipeline setup with GitLab CI/CD.

```yaml
stages:
  - build
  - test

build_job:
  stage: build
  script:
    - echo "Building the application..."
    - make build

test_job:
  stage: test
  script:
    - echo "Running Nikto security tests..."
    - nikto -h http://localhost:8080 > nikto_report.txt
  artifacts:
    paths:
      - nikto_report.txt
```

In this example, the `test_job` runs Nikto against the web application hosted at `http://localhost:8080`. The results are saved to `nikto_report.txt`, which is then stored as an artifact for review.

### The Sidecar Testing Pattern

The sidecar testing pattern is a design approach where a separate container (the sidecar) is used to perform security tests on the main application container. This pattern ensures that the security tests do not interfere with the main application's functionality.

#### Benefits of the Sidecar Pattern

- **Isolation**: The sidecar container isolates the security tests from the main application, reducing the risk of interference.
- **Flexibility**: The sidecar can be configured to run different types of security tests, depending on the requirements.
- **Scalability**: The sidecar pattern can be easily scaled to accommodate more complex testing scenarios.

#### Example Sidecar Configuration

Here’s an example of a Docker Compose file that uses the sidecar pattern:

```yaml
version: '3'
services:
  app:
    image: my-web-app:latest
    ports:
      - "8080:80"
  sidecar:
    image: nikto:latest
    depends_on:
      - app
    command: ["nikto", "-h", "http://app:80"]
```

In this example, the `sidecar` service runs Nikto against the `app` service. The `depends_on` directive ensures that the `app` service is up and running before the `sidecar` service starts.

### Health Checks and Operational Readiness

Before performing security tests, it is crucial to ensure that the sidecar is up and running and operational. This can be achieved by implementing health checks and readiness probes.

#### Health Check Example

Here’s an example of a health check for the sidecar container:

```yaml
version: '3'
services:
  app:
    image: my-web-app:latest
    ports:
      - "8080:80"
  sidecar:
    image: nikto:latest
    depends_on:
      - app
    command: ["nikto", "-h", "http://app:80"]
    healthcheck:
      test: ["CMD-SHELL", "nikto --help | grep 'Nikto Web Server Scanner V'"]
      interval: 30s
      timeout: 10s
      retries: 3
```

In this example, the `healthcheck` directive ensures that the sidecar container is operational by checking if Nikto is available.

### Running Nikto and Analyzing Results

Once the sidecar is up and running, you can proceed with running Nikto and analyzing the results.

#### Example Nikto Scan

Here’s an example of a Nikto scan output:

```plaintext
- Nikto Web Server Scanner V2.1.6
+ Target IP:          127.0.0.1
+ Target Hostname:    localhost
+ Target Port:        8080
+ Start Time:         Thu Aug  3 14:45:00 2023

+ Server: Apache/2.4.41 (Ubuntu)
+ Server leaks inodes via ETags, header found with file /etc/passwd.
+ The anti-clickjacking X-Frame-Options header is not present.
+ Uncommon header 'ms-security-authorization' found, with contents: Negotiate
+ Uncommon header 'ms-security-authorization' found, with contents: NTLM
+ The X-XSS-Protection header is not defined. This header can hint to the user agent to protect against some forms of XSS.
+ The X-Content-Type-Options header is not set. This could allow the user agent to render the content of the site in a different fashion to the MIME type.
+ Uncommon header 'ms-security-authorization' found, with contents: Negotiate
+ Uncommon header 'ms-security-authorization' found, with contents: NTLM
+ Uncommon header 'ms-security-authorization' found, with contents: Negotiate
+ Uncommon header 'ms-security-authorization' found, with contents: NTLM
+ Uncommon header 'ms-security-authorization' found, with contents: Negotiate
+ Uncommon header 'ms-security-authorization' found, with contents: NT
+ Uncommon header 'ms-security-authorization' found, with contents: NTLM
+ Uncommon header 'ms-security-authorization' found, with contents: Negotiate
+ Uncommon header 'ms-security-authorization' found, with contents: NTLM
+ Uncommon header 'ms-security-authorization' found, with contents: Negotiate
+ Uncommon header 'ms-security-authorization' found, with contents: NTLM
+ Uncommon header 'ms-security-authorization' found, with contents: Negotiate
+ Uncommon header 'ms-security-authorization' found, with contents: NTLM
+ Uncommon header 'ms-security-authorization' found, with contents: Negotiate
+ Uncommon header 'ms-security-authorization' found, with contents: NTLM
+ Uncommon header 'ms-security-authorization' found, with contents: Negotiate
+ Uncommon header 'ms-security-authorization' found, with contents: NTLM
+ Uncommon header 'ms-security-authorization' found, with contents: Negotiate
+ Uncommon header 'ms-security-authorization'
```

#### Analyzing the Report

After running Nikto, you should analyze the report to identify any potential security issues. In the example above, several headers are flagged as uncommon, which might indicate misconfigurations or potential vulnerabilities.

### Handling False Positives

False positives are common in security scanning tools like Nikto. It is important to filter out these false positives to focus on actual security issues.

#### Example of Filtering False Positives

Here’s an example of filtering out false positives:

```bash
nikto -h http://localhost:8080 | grep -v "Uncommon header"
```

This command filters out lines containing "Uncommon header," which are often false positives.

### Real-World Examples and Recent Breaches

Recent breaches and CVEs highlight the importance of automated security testing. For instance, the **CVE-2021-26084** vulnerability in Apache Tomcat allowed attackers to bypass authentication mechanisms. By integrating Nikto into your CI/CD pipeline, you can catch such vulnerabilities early.

### How to Prevent / Defend

#### Detection

To detect vulnerabilities identified by Nikto, you can:

- **Regularly Run Nikto**: Schedule regular scans to catch new vulnerabilities.
- **Integrate with CI/CD**: Integrate Nikto into your CI/CD pipeline to catch vulnerabilities early.

#### Prevention

To prevent vulnerabilities identified by Nikto, you can:

- **Update Software**: Keep all software components up to date.
- **Configure Security Headers**: Ensure that security headers like `X-Frame-Options`, `X-XSS-Protection`, and `X-Content-Type-Options` are correctly configured.
- **Use Secure Configurations**: Follow secure configuration guidelines for your web server and applications.

#### Secure Coding Fixes

Here’s an example of securing a web server configuration:

**Vulnerable Configuration:**

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        root /var/www/html;
        index index.html;
    }
}
```

**Secure Configuration:**

```nginx
server {
    listen 80;
    server_name example.com;

    location / {
        root /var/www/html;
        index index.html;
    }

    add_header X-Frame-Options DENY;
    add_header X-XSS-Protection "1; mode=block";
    add_header X-Content-Type-Options nosniff;
}
```

### Conclusion

Automating infrastructure security testing with tools like Nikto and the sidecar testing pattern is essential for maintaining robust security in modern DevSecOps environments. By integrating these practices into your CI/CD pipeline, you can catch and mitigate vulnerabilities early, ensuring the security of your applications.

### Practice Labs

For hands-on practice with Nikto and the sidecar testing pattern, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs for learning web security concepts, including Nikto usage.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing techniques.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

These labs provide practical experience in integrating security testing into your CI/CD pipeline and applying the sidecar testing pattern effectively.

---
<!-- nav -->
[[03-Automating Infrastructure Security Testing Part 1|Automating Infrastructure Security Testing Part 1]] | [[DevSecOps/DevSecOps Bootcamp/04-Infrastructure Security/01-Automating Infrastructure Security Testing/Demo Running Nikto and Using the Sidecar Testing Pattern/00-Overview|Overview]] | [[05-Automating Infrastructure Security Testing|Automating Infrastructure Security Testing]]
