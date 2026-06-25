---
course: DevSecOps
topic: Secure Continuous Deployment & DAST
tags: [devsecops]
---

## Introduction to Secure Continuous Deployment and Dynamic Application Security Testing (DAST)

In the realm of DevSecOps, ensuring continuous deployment is secure is paramount. One critical aspect of this process is integrating Dynamic Application Security Testing (DAST) into the Continuous Integration and Continuous Deployment (CI/CD) pipeline. This ensures that applications are scanned for vulnerabilities dynamically during runtime, providing a comprehensive security assessment.

### What is DAST?

Dynamic Application Security Testing (DAST) is a type of security testing performed on a running application. Unlike Static Application Security Testing (SAST), which analyzes the source code, DAST simulates attacks on a live application to identify security vulnerabilities. This includes testing for SQL injection, cross-site scripting (XSS), and other common web application vulnerabilities.

### Why Integrate DAST in CI/CD?

Integrating DAST into the CI/CD pipeline ensures that security testing is automated and consistent. This helps in identifying and fixing security issues early in the development cycle, reducing the risk of vulnerabilities making it to production. Additionally, it provides a continuous feedback loop, allowing developers to address security concerns promptly.

### How DAST Works

DAST tools simulate various types of attacks on the application, such as:

- **SQL Injection**: Attempting to inject malicious SQL queries to manipulate database operations.
- **Cross-Site Scripting (XSS)**: Injecting malicious scripts into web pages viewed by other users.
- **Cross-Site Request Forgery (CSRF)**: Forcing authenticated users to perform unwanted actions on a web application.
- **Broken Authentication**: Exploiting weaknesses in authentication mechanisms.
- **Sensitive Data Exposure**: Identifying data leaks through insecure configurations or coding practices.

### Example of a Real-World Breach

One notable example is the Equifax breach in 2017, where attackers exploited a vulnerability in the Apache Struts framework. This breach resulted in the theft of sensitive personal information of approximately 147 million people. Integrating DAST could have helped identify and mitigate such vulnerabilities earlier.

### Configuring Automated DAST Scans in CI/CD Pipeline

To integrate DAST into the CI/CD pipeline, we need to configure the pipeline to run DAST scans automatically. This involves setting up the necessary tools and scripts to perform the scans and integrate the results into the build process.

#### Step-by-Step Configuration

1. **Choose a DAST Tool**: Select a DAST tool that suits your needs. Popular choices include OWASP ZAP, Burp Suite, and Arachni.
2. **Install the Tool**: Install the chosen DAST tool in your CI/CD environment. Ensure it is accessible from your build scripts.
3. **Configure Build Scripts**: Modify your build scripts to include steps for running DAST scans. This typically involves invoking the DAST tool with appropriate parameters.
4. **Integrate Results**: Integrate the results of the DAST scans into your build process. Fail the build if any critical vulnerabilities are found.

### Example Configuration Using OWASP ZAP

Let's walk through an example configuration using OWASP ZAP, a popular open-source DAST tool.

#### Installing OWASP ZAP

First, install OWASP ZAP in your CI/CD environment. You can download it from the official website or use a package manager like `apt` or `brew`.

```bash
# Using apt (Ubuntu/Debian)
sudo apt-get update
sudo apt-get install owasp-zap

# Using brew (macOS)
brew install owasp/zap/owasp-zap
```

#### Configuring Build Scripts

Next, modify your build scripts to include steps for running OWASP ZAP. Here’s an example using a shell script:

```bash
#!/bin/bash

# Run OWASP ZAP scan
zap-baseline.py -t http://localhost:3000 -r report.html

# Check if any critical vulnerabilities were found
if grep -q "Critical" report.html; then
  echo "Critical vulnerabilities found. Build failed."
  exit 1
fi

echo "Build succeeded."
exit 0
```

This script runs OWASP ZAP against the application running on `http://localhost:3000` and generates a report. If any critical vulnerabilities are found, the build fails.

### Example Code: Adding Security Middleware in Node.js

Let's consider a Node.js application and add security middleware to protect against common vulnerabilities. We'll use the `Helmet` library, which provides various security-related HTTP headers.

#### Background Theory

Middleware in Node.js is a function that has access to the request object (`req`), the response object (`res`), and the next middleware function in the application’s request-response cycle. Middleware functions can execute any code, make changes to the request and response objects, end the request-response cycle, and call the next middleware function in the stack.

#### Adding Content Security Policy (CSP) Middleware

We'll add a Content Security Policy (CSP) middleware to our Node.js application using the `Helmet` library.

```javascript
// server.ts
import express from 'express';
import helmet from 'helmet';

const app = express();

// Add security middleware
app.use(helmet());

// Set CSP header
app.use(helmet.contentSecurityPolicy({
  directives: {
    defaultSrc: ["'self'"],
    scriptSrc: ["'self'", "'unsafe-inline'"],
    styleSrc: ["'self'", "'unsafe-inline'"],
    imgSrc: ["'self'", 'data:', 'https://*'],
    fontSrc: ["'self'", 'data:', 'https://*'],
    connectSrc: ["'self'"],
    frameSrc: ["'none'"],
    objectSrc: ["'none'"],
    mediaSrc: ["'self'"],
    childSrc: ["'self'"]
  }
}));

// Define routes
app.get('/', (req, res) => {
  res.send('Hello, World!');
});

// Start server
app.listen(3000, () => {
  console.log('Server is running on port 3000');
});
```

#### Explanation of the Code

- **Helmet**: The `Helmet` library provides various security-related HTTP headers. We use it to set the Content Security Policy (CSP).
- **Content Security Policy (CSP)**: CSP is a security feature that helps prevent cross-site scripting (XSS), clickjacking, and other code injection attacks. It specifies which sources of content are allowed to be loaded on a page.
- **Directives**: The `directives` object defines the policies for different types of content. For example, `defaultSrc` specifies the default sources for all content, `scriptSrc` specifies the sources for scripts, and so on.

#### Raw HTTP Response with CSP Header

When the server responds to a request, it includes the CSP header in the HTTP response. Here’s an example of the raw HTTP response:

```http
HTTP/1.1 200 OK
Date: Mon, 20 Mar 2023 12:00:00 GMT
Content-Type: text/html; charset=utf-8
Content-Length: 13
Connection: keep-alive
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
X-Frame-Options: SAMEORIGIN
Strict-Transport-Security: max-age=31536000; includeSubDomains
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https://*; font-src 'self' data: https://*; connect-src 'self'; frame-src 'none'; object-src 'none'; media-src 'self'; child-src 'self'

Hello, World!
```

#### Explanation of Each Header

- **Content-Security-Policy**: Specifies the Content Security Policy for the response. This header enforces the policies defined in the `directives` object.
- **X-Content-Type-Options**: Prevents MIME type sniffing, which can lead to XSS attacks.
- **X-XSS-Protection**: Enables the browser's built-in XSS filtering.
- **X-Frame-Options**: Prevents clickjacking attacks by specifying whether the page can be framed.
- **Strict-Transport-Security**: Forces the browser to use HTTPS for future connections.

### Common Pitfalls and Best Practices

#### Common Pitfalls

1. **Overly Permissive Policies**: Setting overly permissive policies can leave your application vulnerable to attacks. Always start with strict policies and gradually relax them as needed.
2. **Ignoring Non-Critical Vulnerabilities**: While critical vulnerabilities should be addressed immediately, non-critical vulnerabilities should not be ignored. They can often be chained together to create more severe issues.
3. **Manual Testing**: Relying solely on automated DAST scans can miss certain types of vulnerabilities. Manual testing and penetration testing should complement automated scans.

#### Best Practices

1. **Regular Updates**: Keep your DAST tools and libraries up-to-date to ensure you are protected against the latest vulnerabilities.
2. **Automated Scanning**: Automate DAST scans as part of your CI/CD pipeline to ensure continuous security testing.
3. **Secure Coding Practices**: Follow secure coding practices to minimize the risk of introducing vulnerabilities in the first place.

### How to Prevent / Defend Against DAST Vulnerabilities

#### Detection

- **Automated Scans**: Regularly run automated DAST scans to identify vulnerabilities.
- **Manual Testing**: Perform manual testing and penetration testing to identify vulnerabilities that automated scans might miss.

#### Prevention

- **Secure Coding Practices**: Follow secure coding practices to minimize the risk of introducing vulnerabilities.
- **Regular Updates**: Keep your DAST tools and libraries up-to-date to ensure you are protected against the latest vulnerabilities.
- **Configuration Hardening**: Harden your application’s configuration to reduce the attack surface.

#### Secure Coding Fixes

Here’s an example of a vulnerable code snippet and its secure counterpart:

**Vulnerable Code**

```javascript
// server.ts
import express from 'express';

const app = express();

// Define routes
app.get('/', (req, res) => {
  res.send(req.query.message);
});

// Start server
app.listen(3000, () => {
  console.log('Server is running on port  3000');
});
```

**Secure Code**

```javascript
// server.ts
import express from 'express';
import helmet from 'helmet';

const app = express();

// Add security middleware
app.use(helmet());

// Define routes
app.get('/', (req, res) => {
  const message = req.query.message || 'Hello, World!';
  res.send(message);
});

// Start server
app.listen(3000, () => {
  console.log('Server is running on port 3000');
});
```

#### Explanation

- **Vulnerable Code**: The original code directly sends the `message` parameter from the query string, which can lead to XSS attacks.
- **Secure Code**: The secure code checks if the `message` parameter is present and defaults to a safe value if it is not. This prevents XSS attacks.

### Hands-On Labs for Practice

To practice configuring DAST scans in your CI/CD pipeline, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs for learning web security concepts, including DAST.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities for educational purposes.

These labs provide a practical way to apply the concepts learned in this chapter.

### Conclusion

Integrating DAST into your CI/CD pipeline is crucial for ensuring the security of your applications. By automating DAST scans and following secure coding practices, you can significantly reduce the risk of vulnerabilities making it to production. Regular updates and configuration hardening further enhance the security of your applications.

By following the steps outlined in this chapter, you can effectively configure DAST scans in your CI/CD pipeline and ensure that your applications are secure.

---
<!-- nav -->
[[03-Introduction to Dynamic Application Security Testing (DAST)|Introduction to Dynamic Application Security Testing (DAST)]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/Configure Automated DAST Scans in CICD Pipeline/00-Overview|Overview]] | [[05-Introduction to Secure Continuous Deployment and Dynamic Application Security Testing (DAST) Part 2|Introduction to Secure Continuous Deployment and Dynamic Application Security Testing (DAST) Part 2]]
