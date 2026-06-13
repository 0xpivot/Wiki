---
tags: [owasp, standards, framework, vapt]
difficulty: intermediate
module: "57 - OWASP Frameworks and Standards"
topic: "57.04 OWASP Testing Guide OTG"
---

# OWASP Web Security Testing Guide (WSTG) Full Walkthrough

## Executive Summary
The OWASP Web Security Testing Guide (WSTG) is the premier, comprehensive cybersecurity testing manual for web applications. Unlike the OWASP Top 10, which is an awareness document listing the most critical risks, the WSTG provides a rigorous, methodical framework outlining exactly *how* to test for thousands of different security vulnerabilities. It forms the standard baseline for structured Web Application Penetration Testing and Vulnerability Assessments worldwide.

The WSTG encompasses the entire testing lifecycle, from initial reconnaissance to deep business logic exploitation.

## ASCII Architecture Diagram of the Testing Lifecycle
```text
+-------------------------------------------------------------------------+
|                  WSTG Penetration Testing Lifecycle                     |
+-------------------------------------------------------------------------+
|                                                                         |
|  [ 1. Recon & Info Gathering ] -----> [ 2. Configuration & Deployment ] |
|  (WSTG-INFO)                          (WSTG-CONF)                       |
|           |                                       |                     |
|           v                                       v                     |
|  [ 3. Identity & Auth Testing ] ----> [ 4. Session Management Testing ] |
|  (WSTG-IDNT, WSTG-ATHN, WSTG-ATHZ)    (WSTG-SESS)                       |
|           |                                       |                     |
|           v                                       v                     |
|  [ 5. Input Validation Testing ] ---> [ 6. Business Logic Testing ]     |
|  (WSTG-INPV)                          (WSTG-BUSL)                       |
|           |                                       |                     |
|           v                                       v                     |
|  [ 7. Client-Side Testing ]           [ 8. Error/Crypto/Routing ]       |
|  (WSTG-CLNT)                          (WSTG-ERRH, WSTG-CRYP)            |
+-------------------------------------------------------------------------+
```

## Deep Dive into the WSTG Categories

### 1. Information Gathering (WSTG-INFO)
Reconnaissance is critical. The more you know about the application architecture, the more effectively you can attack it.
- **Key Tests**:
  - **Search Engine Discovery**: Using Google Dorks to find exposed administrative interfaces or sensitive files.
  - **Fingerprinting Web Server/App Framework**: Analyzing HTTP headers, error pages, and cookies to identify technologies (e.g., Apache, Nginx, React, Spring Boot).
  - **Reviewing Webpage Source and Metadata**: Extracting developer comments, hidden fields, and JavaScript maps.
  - **Identifying Application Entry Points**: Mapping all inputs, parameters, headers, and API endpoints.

### 2. Configuration and Deployment Management Testing (WSTG-CONF)
Assessing the infrastructure and deployment mechanisms hosting the web application.
- **Key Tests**:
  - **Network Infrastructure**: Port scanning, reviewing firewall rules.
  - **Application Platform Configuration**: Testing for exposed admin interfaces (e.g., Tomcat Manager), default credentials, and verbose error messages.
  - **File Extensions Handling**: Ensuring the server correctly parses or blocks dangerous extensions (`.php`, `.jsp`, `.exe`).
  - **Cross-Site Tracing (XST)**: Testing if the `TRACE` HTTP method is enabled.
  - **Cloud Storage**: Checking for misconfigured S3 buckets or Azure Blobs.

### 3. Identity Management Testing (WSTG-IDNT)
Testing the processes by which the application provisions, manages, and destroys user identities.
- **Key Tests**:
  - **Role Definitions**: Ensuring privilege separation exists and is well-defined.
  - **User Registration Process**: Testing for identity spoofing, weak verification, and user enumeration during registration.
  - **Account Provisioning Process**: Checking how accounts are created and if default credentials are used.

### 4. Authentication Testing (WSTG-ATHN)
Verifying that the application effectively confirms the user is who they claim to be.
- **Key Tests**:
  - **Credentials Transport**: Ensuring passwords are only sent over TLS.
  - **Brute Force/Credential Stuffing**: Testing for the presence of rate-limiting or account lockouts.
  - **Bypassing Authentication**: Modifying parameters or using SQL injection on login forms.
  - **Password Reset Features**: Testing for token predictability, token expiration, and user enumeration on "Forgot Password" endpoints.
  - **Multi-Factor Authentication (MFA)**: Evaluating the implementation and testing for bypass techniques.

### 5. Authorization Testing (WSTG-ATHZ)
Once authenticated, testing what the user is allowed to do.
- **Key Tests**:
  - **Directory Traversal / Local File Inclusion (LFI)**: Attempting to access underlying OS files (e.g., `../../../etc/passwd`).
  - **Bypassing Authorization Schema**: Escalating privileges (Vertical Privilege Escalation) or accessing peers' data (Horizontal Privilege Escalation / IDOR).
  - **Insecure Direct Object References**: Manipulating object IDs in parameters.

### 6. Session Management Testing (WSTG-SESS)
Ensuring the application securely handles the state of an authenticated user.
- **Key Tests**:
  - **Session Management Schema**: Analyzing token generation randomness and structure.
  - **Cookie Attributes**: Verifying the presence of `Secure`, `HttpOnly`, and `SameSite` flags.
  - **Session Fixation**: Testing if the application accepts a session ID injected by the attacker.
  - **Exposed Session Variables**: Ensuring tokens are not passed in URLs (e.g., via `GET` parameters).
  - **Logout Functionality**: Verifying that sessions are invalidated server-side upon logout and timeout.

### 7. Input Validation Testing (WSTG-INPV)
The largest category. Testing how the application handles malformed or malicious input.
- **Key Tests**:
  - **Cross-Site Scripting (XSS)**: Testing Reflected, Stored, and DOM-based XSS.
  - **SQL Injection**: Testing boolean-based, time-based, error-based, and union-based SQLi.
  - **Command Injection**: Attempting to execute OS commands.
  - **XML External Entity (XXE)**: Injecting external entities into XML parsers.
  - **Server-Side Request Forgery (SSRF)**: Forcing the server to make arbitrary HTTP requests.
  - **HTTP Parameter Pollution / Smuggling**: Manipulating how proxies and backend servers interpret requests.

### 8. Testing for Error Handling (WSTG-ERRH)
Assessing what the application reveals when something goes wrong.
- **Key Tests**:
  - **Analysis of Error Codes**: Triggering errors to see if stack traces, SQL syntax errors, or internal IP addresses are leaked.
  - **Testing for Stack Traces**: Ensuring a generic error page is presented in production.

### 9. Testing for Weak Cryptography (WSTG-CRYP)
Evaluating the cryptographic implementation.
- **Key Tests**:
  - **Weak Transport Layer Security**: Testing for deprecated protocols (SSLv3, TLS 1.0) and weak ciphers.
  - **Padding Oracle Attacks**: Testing block cipher implementations.
  - **Sensitive Information in Plaintext**: Checking if credit cards or passwords are stored or transmitted unencrypted.

### 10. Business Logic Testing (WSTG-BUSL)
Testing flaws inherent to the specific application's design that automated scanners cannot detect.
- **Key Tests**:
  - **Test Business Logic Data Validation**: Attempting to bypass business constraints (e.g., ordering negative quantities of an item to reduce the total cart price).
  - **Test Defenses Against Application Misuse**: Circumventing workflow steps (e.g., skipping the payment step and going straight to the confirmation step).
  - **Test for Unexpected File Types**: Uploading a `.php` file in a profile picture upload feature.

### 11. Client-Side Testing (WSTG-CLNT)
Testing vulnerabilities that execute within the user's browser.
- **Key Tests**:
  - **DOM-Based XSS**: Tracing data from sources (`location.hash`) to sinks (`innerHTML`).
  - **Cross-Site Flashing / HTML5 Storage**: Testing insecure usage of `localStorage` or `sessionStorage`.
  - **Clickjacking**: Testing if the application can be framed (`X-Frame-Options` or CSP `frame-ancestors`).
  - **Cross-Origin Resource Sharing (CORS)**: Analyzing permissive CORS configurations.

## Chaining Opportunities
- **WSTG-INFO (Information Gathering) + WSTG-INPV (Input Validation)**: Discovering hidden, undocumented debug parameters (`?debug=true` or `?cmd=`) during recon, and leveraging them to achieve Command Injection.
- **WSTG-BUSL (Business Logic) + WSTG-ATHZ (Authorization)**: Skipping a crucial payment workflow step (Business Logic) combined with an IDOR (Authorization) to apply another user's payment method to your cart.
- **WSTG-SESS (Session Management) + WSTG-CLNT (Client-Side Testing)**: Discovering a missing `HttpOnly` flag on a session cookie, allowing a successful Stored XSS attack to cleanly exfiltrate the administrative session token.

## Related Notes
- [[01 - OWASP Top 10 2021 Full Walkthrough]]
- [[05 - OWASP ASVS Application Security Verification Standard]]
- [[18 - Penetration Testing Execution Standard PTES]]
- [[19 - Common Vulnerability Scoring System CVSS Guide]]
