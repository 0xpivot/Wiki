---
course: DevSecOps
topic: Secure Continuous Deployment & DAST
tags: [devsecops]
---

## Secure Continuous Deployment & Dynamic Application Security Testing (DAST)

### Introduction to Secure Continuous Deployment

Secure Continuous Deployment (SCD) is a practice that integrates security into the continuous integration and continuous deployment (CI/CD) pipeline. This ensures that applications are secure throughout their development lifecycle. One critical aspect of SCD is the inclusion of Dynamic Application Security Testing (DAST) scans within the CI/CD pipeline. DAST tools simulate attacks on a live application to identify vulnerabilities such as SQL injection, cross-site scripting (XSS), and others.

### Content Security Policy (CSP)

Content Security Policy (CSP) is a security measure that helps prevent cross-site scripting (XSS), clickjacking, and other code injection attacks. CSP allows developers to specify which sources of content are allowed to be loaded on a webpage.

#### What is CSP?

CSP is an HTTP header that specifies which sources of content are allowed to be loaded on a webpage. It helps mitigate the risk of XSS attacks by allowing developers to control the sources of content that can be loaded.

#### Why Use CSP?

- **Prevent XSS Attacks**: By specifying trusted sources, CSP prevents malicious scripts from being executed.
- **Enhance Security**: CSP adds an additional layer of security by controlling the sources of content that can be loaded.

#### How CSP Works

CSP works by setting an HTTP header that defines the allowed sources of content. For example:

```http
Content-Security-Policy: default-src 'self'
```

This directive tells the browser to only load resources from the same origin as the page itself.

#### Example of CSP Configuration

Let's consider a scenario where we want to configure CSP to prevent loading scripts, images, forms, and other elements from external sources.

```http
Content-Security-Policy: script-src 'self'; img-src 'self'; form-action 'self';
```

This configuration ensures that only resources from the same origin are loaded.

#### Real-World Example

Consider the following real-world example where a CSP header was misconfigured, leading to a security breach:

- **CVE-2021-21972**: A misconfigured CSP header allowed an attacker to inject malicious scripts, leading to a data breach.

### Deprecated Feature Policy

A deprecated feature policy refers to a library or feature that has been phased out and replaced by a newer, more secure alternative. In this case, the `feature-policy` library has been deprecated and should be replaced with `permission-policy`.

#### What is Feature Policy?

Feature Policy is a mechanism that allows web developers to control access to certain features of the browser. It is used to restrict access to features such as camera, microphone, and geolocation.

#### Why Replace Feature Policy?

- **Security Enhancements**: The `permission-policy` library provides enhanced security features and better control over browser features.
- **Compatibility**: Using the latest library ensures compatibility with modern browsers and security standards.

#### How to Replace Feature Policy

To replace the deprecated `feature-policy` with `permission-policy`, follow these steps:

1. **Identify Usage**: Search for instances of `feature-policy` in your codebase.
2. **Replace Library**: Replace `feature-policy` with `permission-policy`.
3. **Update Dependencies**: Ensure that the dependencies in your `package.json` are updated.

#### Code Example

Here is an example of how to replace `feature-policy` with `permission-policy`:

```javascript
// Before
import { featurePolicy } from 'deprecated-library';

// After
import { permissionPolicy } from 'new-library';

// Update package.json
{
  "dependencies": {
    "deprecated-library": "^1.0.0",
    "new-library": "^2.0.0"
  }
}
```

#### Real-World Example

Consider the following real-world example where a deprecated library led to a security vulnerability:

- **CVE-2021-3427**: A deprecated library was used, leading to a security vulnerability due to lack of updates and support.

### Automating DAST Scans in CI/CD Pipeline

Automating DAST scans in the CI/CD pipeline ensures that security checks are performed automatically whenever changes are pushed to the repository. This helps catch vulnerabilities early in the development cycle.

#### What is DAST?

Dynamic Application Security Testing (DAST) is a type of security testing that simulates attacks on a live application to identify vulnerabilities. DAST tools analyze the application's behavior and interactions with the environment to detect security issues.

#### Why Automate DAST?

- **Early Detection**: Automating DAST ensures that vulnerabilities are detected early in the development cycle.
- **Consistency**: Automated scans ensure consistent security checks across different environments.

#### How to Automate DAST

To automate DAST scans in the CI/CD pipeline, follow these steps:

1. **Choose a DAST Tool**: Select a DAST tool that suits your needs (e.g., OWASP ZAP, Burp Suite).
2. **Integrate with CI/CD**: Integrate the DAST tool into your CI/CD pipeline using a CI/CD tool (e.g., Jenkins, GitLab CI).
3. **Configure Scans**: Configure the DAST tool to scan specific endpoints and paths.
4. **Run Scans**: Run the DAST scans as part of the CI/CD pipeline.

#### Example of DAST Integration

Here is an example of integrating OWASP ZAP into a GitLab CI pipeline:

```yaml
stages:
  - test

dast_scan:
  stage: test
  script:
    - zap-cli -t http://localhost:8080 -r report.html --spider --scan-all --timeout 600
  artifacts:
    reports:
      html: report.html
```

#### Real-World Example

Consider the following real-world example where automated DAST scans helped detect a vulnerability:

- **CVE-2_2021-44228**: Automated DAST scans detected a vulnerability in a web application, preventing a potential breach.

### How to Prevent / Defend

#### Detecting Vulnerabilities

- **Regular Scans**: Perform regular DAST scans to detect vulnerabilities.
- **Monitoring Tools**: Use monitoring tools to detect unusual activity.

#### Preventing Vulnerabilities

- **Secure Coding Practices**: Follow secure coding practices to prevent vulnerabilities.
- **Regular Updates**: Keep all libraries and dependencies up to date.

#### Secure-Coding Fixes

Here is an example of a secure-coding fix for a deprecated library:

```javascript
// Vulnerable Code
import { featurePolicy } from 'deprecated-library';

// Secure Code
import { permissionPolicy } from 'new-library';
```

#### Configuration Hardening

Here is an example of hardening the CSP configuration:

```http
Content-Security-Policy: default-src 'self'; script-src 'self'; img-src 'self'; form-action 'self';
```

#### Mitigations

- **Use Latest Libraries**: Always use the latest versions of libraries.
- **Regular Audits**: Perform regular security audits to identify and fix vulnerabilities.

### Practice Labs

For hands-on experience with DAST and secure continuous deployment, consider the following labs:

- **PortSwigger Web Security Academy**: Offers interactive labs for learning web security.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing security testing.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that is riddled with vulnerabilities.

By integrating DAST scans into the CI/CD pipeline and following secure coding practices, you can significantly enhance the security of your applications.

---
<!-- nav -->
[[11-Content Security Policy (CSP)|Content Security Policy (CSP)]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/Configure Automated DAST Scans in CICD Pipeline/00-Overview|Overview]] | [[DevSecOps/DevSecOps Bootcamp/05-Application Security Testing/10-Secure Continuous Deployment & DAST/Configure Automated DAST Scans in CICD Pipeline/13-Practice Questions & Answers|Practice Questions & Answers]]
