---
course: DevSecOps
topic: Secure Continuous Deployment & DAST
tags: [devsecops]
---

## Introduction to Secure Continuous Deployment and Dynamic Application Security Testing (DAST)

Dynamic Application Security Testing (DAST) is a critical component of modern DevSecOps practices. It involves testing applications while they are running to identify vulnerabilities and security weaknesses. One popular tool for DAST is OWASP ZAP (Zed Attack Proxy), which can be integrated into Continuous Integration/Continuous Deployment (CI/CD) pipelines to automate security testing.

### Background Theory

Dynamic Application Security Testing (DAST) is performed on a live application to identify security vulnerabilities such as SQL injection, cross-site scripting (XSS), and others. Unlike Static Application Security Testing (SAST), which analyzes the source code, DAST simulates attacks against the running application to find exploitable vulnerabilities.

OWASP ZAP is an open-source tool designed to help developers and security professionals identify security vulnerabilities in web applications. It can be used manually or configured to run automatically in CI/CD pipelines.

### Integrating ZAP into CI/CD Pipelines

To integrate ZAP into a CI/CD pipeline, you need to configure ZAP to run automated scans and produce reports that can be analyzed and acted upon. This process involves several steps:

1. **Regenerating Default Configuration File**
2. **Configuring ZAP Options**
3. **Producing Reports**
4. **Handling Report Directory Issues**

#### Regenerating Default Configuration File

When integrating ZAP into a CI/CD pipeline, it is often necessary to regenerate the default configuration file to ensure consistency and avoid detection issues caused by pre-existing configurations.

```bash
zap-baseline.py -g -t http://localhost:8080/
```

- `-g`: Generates the default configuration file.
- `-t`: Specifies the target URL for the scan.

This command regenerates the default configuration file and starts a scan against the specified target.

#### Configuring ZAP Options

ZAP provides various configuration options to control how the tool behaves during a scan. One important option is configuring ZAP to not fail on warning-level findings.

```bash
zap-baseline.py -I -t http://localhost:8080/
```

- `-I`: Configures ZAP to fail only on findings higher than the warning level.

This ensures that the build process does not fail due to minor issues but will fail if critical vulnerabilities are found.

### Producing Reports

After configuring ZAP, the next step is to produce reports that can be analyzed. ZAP supports various report formats, including XML.

```bash
zap-baseline.py -x baseline.xml -t http://localhost:8080/
```

- `-x baseline.xml`: Specifies the output file for the XML report.

This command runs the scan and generates an XML report named `baseline.xml`.

### Handling Report Directory Issues

ZAP creates reports in its working directory (`/zap/wrk`). To ensure the report is accessible in the CI/CD pipeline, you need to copy the report from the working directory to the current directory of the container.

```bash
cp /zap/wrk/baseline.xml .
```

This command copies the `baseline.xml` report from `/zap/wrk` to the current directory.

### Full Example in a CI/CD Pipeline

Here is a complete example of how to integrate ZAP into a CI/CD pipeline using a Docker container:

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout code
        uses: actions/checkout@v2

      - name: Set up Docker
        uses: docker/setup-buildx-action@v1

      - name: Run ZAP Scan
        run: |
          docker run --rm -v $(pwd):/zap/wrk/:rw \
            owasp/zap2docker-weekly:latest zap-baseline.py \
            -g -I -x baseline.xml -t http://localhost:8080/

      - name: Copy Report
        run: |
          cp /zap/wrk/baseline.xml .

      - name: Analyze Report
        run: |
          cat baseline.xml
```

### HTTP Request and Response Example

Here is an example of a full HTTP request and response when running a ZAP scan:

**HTTP Request:**

```http
POST /JSON/core/action/newSession HTTP/1.1
Host: localhost:8080
Content-Type: application/json

{
  "apikey": "your_api_key",
  "sessionName": "MySession"
}
```

**HTTP Response:**

```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Content-Type: application/json

{
  "requestId": "12345",
  "status": "success",
  "message": "New session created successfully"
}
```

### Common Pitfalls and How to Prevent Them

#### Pitfall: Incorrect Configuration

**Problem:** Incorrect configuration settings can lead to false positives or missed vulnerabilities.

**Solution:** Always refer to the official ZAP documentation and test configurations thoroughly.

#### Pitfall: Report Directory Issues

**Problem:** ZAP creates reports in its working directory, which may not be accessible in the CI/CD pipeline.

**Solution:** Ensure the report is copied to the current directory of the container.

### Real-World Examples and Recent CVEs

#### Example: CVE-2021-21972

In 2021, a vulnerability was discovered in the Apache Struts framework, which could be exploited through a remote code execution (RCE) attack. Using ZAP, this vulnerability could be identified by scanning the application and analyzing the generated report.

#### Example: OWASP Juice Shop

The OWASP Juice Shop is a deliberately insecure web application designed to teach security concepts. Integrating ZAP into the CI/CD pipeline for Juice Shop helps identify and mitigate vulnerabilities.

### How to Prevent / Defend

#### Detection

- **Regular Scans:** Schedule regular ZAP scans to detect new vulnerabilities.
- **Automated Reporting:** Integrate ZAP into CI/CD pipelines to automatically generate and analyze reports.

#### Prevention

- **Secure Coding Practices:** Follow secure coding guidelines to prevent common vulnerabilities.
- **Configuration Hardening:** Ensure ZAP is configured correctly to avoid false positives and missed vulnerabilities.

#### Secure Code Fix

**Vulnerable Code:**

```python
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user and user.password == password:
        return "Login successful"
    else:
        return "Invalid credentials"
```

**Fixed Code:**

```python
from werkzeug.security import check_password_hash

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = User.query.filter_by(username=username).first()
    if user and check_password_hash(user.password, password):
        return "Login successful"
    else:
        return "Invalid credentials"
```

### Conclusion

Integrating ZAP into CI/CD pipelines is essential for ensuring the security of web applications. By following the steps outlined above, you can effectively configure ZAP to run automated scans, produce reports, and handle any directory issues that may arise. Regular scans and secure coding practices are key to preventing vulnerabilities and maintaining the security of your applications.

### Practice Labs

For hands-on practice with integrating ZAP into CI/CD pipelines, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs to practice web security techniques.
- **OWASP Juice Shop**: A deliberately insecure web application for learning security concepts.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates common web application vulnerabilities.

These labs provide practical experience in integrating ZAP into CI/CD pipelines and identifying vulnerabilities in web applications.

---
<!-- nav -->
[[06-Introduction to Secure Continuous Deployment and Dynamic Application Security Testing (DAST) Part 3|Introduction to Secure Continuous Deployment and Dynamic Application Security Testing (DAST) Part 3]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/Configure Automated DAST Scans in CICD Pipeline/00-Overview|Overview]] | [[08-Configuring Automated Dynamic Application Security Testing (DAST) in CICD Pipelines Part 1|Configuring Automated Dynamic Application Security Testing (DAST) in CICD Pipelines Part 1]]
