---
tags: [owasp, standards, framework, vapt]
difficulty: intermediate
module: "57 - OWASP Frameworks and Standards"
topic: "57.01 OWASP Top 10 2021 Full Walkthrough"
---

# OWASP Top 10 2021 Full Walkthrough

## Executive Summary
The OWASP Top 10 is a globally recognized standard awareness document for developers and web application security professionals. It represents a broad consensus about the most critical security risks to web applications. Organizations use the OWASP Top 10 to structure their security programs, build secure development lifecycles (SDLC), and evaluate the security posture of their applications through Penetration Testing and Vulnerability Assessments.

The 2021 update shifted focus towards architectural and design-level issues, acknowledging that we can no longer simply "test our way out" of security problems. This represents a mature shift in application security, prioritizing "shift-left" strategies over purely reactive bug-hunting.

## Evolution from 2017 to 2021
The transition from the 2017 to 2021 Top 10 introduced massive structural changes:
- **A04:2021 Insecure Design** was introduced as a new category, emphasizing the need for threat modeling and secure architectures.
- **A08:2021 Software and Data Integrity Failures** was added to address the rising threats in CI/CD pipelines, supply chains, and untrusted software updates.
- **Cross-Site Scripting (XSS)** was folded into **A03:2021 Injection**.
- **XML External Entities (XXE)** was absorbed into **A05:2021 Security Misconfiguration**.
- **Insecure Deserialization** was merged into **A08:2021 Software and Data Integrity Failures**.

## ASCII Architecture Diagram
```text
+-----------------------------------------------------------------------------------+
|                            OWASP Top 10 2021 Attack Surface                       |
+-----------------------------------------------------------------------------------+
|  [ A04: Insecure Design ] -------> [ A08: Software & Data Integrity Failures ]    |
|             |                                       |                             |
|             v                                       v                             |
|  [ A05: Security Misconfig ] ----> [ A06: Vulnerable & Outdated Components ]      |
+-----------------------------------------------------------------------------------+
|                               Application Layer                                   |
|   +-------------------+  +-------------------+  +-------------------+             |
|   | A01: Broken       |  | A02: Crypto       |  | A03: Injection    |             |
|   | Access Control    |  | Failures          |  |                   |             |
|   +-------------------+  +-------------------+  +-------------------+             |
|   +-------------------+  +-------------------+  +-------------------+             |
|   | A07: Auth         |  | A10: SSRF         |  | A09: Logging &    |             |
|   | Failures          |  |                   |  | Monitoring        |             |
|   +-------------------+  +-------------------+  +-------------------+             |
+-----------------------------------------------------------------------------------+
```

## Deep Dive into the Top 10

### A01:2021 - Broken Access Control
Access control enforces policies so users cannot act outside of their intended permissions. Failures typically lead to unauthorized information disclosure, modification, or destruction of all data, or performing a business function outside the user's limits.
- **Attack Scenarios**:
  - **Bypassing Access Control Checks**: An attacker forcefully browses to a target URL, e.g., `/admin_panel`, when they only have user privileges.
  - **Insecure Direct Object References (IDOR)**: Modifying a primary key in a parameter (`user_id=123` to `user_id=124`) to view someone else's account.
  - **Privilege Escalation**: Exploiting flawed logic to escalate from user to administrator.
  - **CORS Misconfiguration**: Allowing unauthorized API access by setting broad `Access-Control-Allow-Origin` headers.
- **Remediation**:
  - Model access controls around the principle of least privilege.
  - Enforce record ownership dynamically.
  - Disable web server directory listing.

### A02:2021 - Cryptographic Failures
Previously known as Sensitive Data Exposure, the focus here is failures related to cryptography, which often leads to sensitive data exposure or system compromise.
- **Attack Scenarios**:
  - **Plaintext Storage**: Passwords or credit card numbers stored without encryption.
  - **Weak Algorithms**: Using MD5 or SHA1 for hashing passwords, making them vulnerable to collision and rainbow table attacks.
  - **Improper Key Management**: Hardcoding encryption keys in source code or uploading `.env` files to GitHub repositories.
  - **Missing TLS**: Transmitting sensitive data over HTTP, making it vulnerable to Man-in-the-Middle (MitM) attacks.
- **Remediation**:
  - Apply strong encryption for data at rest (AES-256) and data in transit (TLS 1.2+).
  - Use proper key management systems (e.g., AWS KMS, HashiCorp Vault).
  - Implement strong password hashing functions like Argon2id or bcrypt.

### A03:2021 - Injection
Injection flaws occur when untrusted data is sent to an interpreter as part of a command or query. This now explicitly includes XSS.
- **Attack Scenarios**:
  - **SQL Injection**: Manipulating SQL queries via input fields to bypass authentication or dump databases.
  - **Command Injection**: Appending shell commands to input used in system calls.
  - **Cross-Site Scripting (XSS)**: Injecting malicious scripts into web pages viewed by other users to steal session tokens.
  - **LDAP/NoSQL Injection**: Modifying search filters to extract unintended records.
- **Remediation**:
  - Use parameterized queries and prepared statements.
  - Implement positive ("whitelist") server-side input validation.
  - Contextually encode output to prevent XSS.

### A04:2021 - Insecure Design
A new category emphasizing that if a system is insecure by design, no amount of testing or configuration can secure it perfectly. It highlights the absence of security controls in application logic.
- **Attack Scenarios**:
  - **Missing Business Logic Controls**: A theater application allowing group discounts without verifying the minimum number of tickets.
  - **Unprotected Credential Recovery**: Security questions that are easily guessable via OSINT (e.g., "What is your mother's maiden name?").
  - **Lack of Rate Limiting**: Allowing automated credential stuffing attacks due to missing anti-automation controls on critical endpoints.
- **Remediation**:
  - Conduct Threat Modeling during the design phase.
  - Integrate security language and controls into user stories and requirements.
  - Implement secure design patterns and reference architectures.

### A05:2021 - Security Misconfiguration
Encompasses unpatched flaws, unprotected files/directories, and insecure default settings. XXE is now included here.
- **Attack Scenarios**:
  - **Default Credentials**: Leaving default usernames and passwords on admin panels (e.g., Tomcat manager, default WordPress).
  - **Exposed Stack Traces**: Displaying detailed error messages to users, revealing internal server states and versions.
  - **Misconfigured Cloud Storage**: AWS S3 buckets allowing public read/write access.
  - **XXE**: XML parsers configured to resolve external entities, allowing local file inclusion (LFI) or SSRF.
- **Remediation**:
  - Establish a repeatable hardening process.
  - Send strict security directives to clients via HTTP Security Headers (HSTS, CSP).
  - Use Infrastructure as Code (IaC) to automate and enforce secure configurations.

### A06:2021 - Vulnerable and Outdated Components
If you do not know the versions of all components you use (both client-side and server-side), you are at risk.
- **Attack Scenarios**:
  - Using an outdated version of jQuery with known DOM XSS vulnerabilities.
  - A vulnerable version of Apache Struts or Log4j being exploited for Remote Code Execution (RCE).
  - Ignoring CVEs for backend databases or operating systems.
- **Remediation**:
  - Maintain a comprehensive Software Bill of Materials (SBOM).
  - Continuously inventory and monitor dependencies using SCA tools (e.g., OWASP Dependency-Check, Snyk).
  - Remove unused dependencies.

### A07:2021 - Identification and Authentication Failures
Focuses on failures in user identification, session management, and authentication workflows.
- **Attack Scenarios**:
  - **Credential Stuffing**: Using lists of known compromised passwords to test against the application.
  - **Session Fixation**: Accepting user-provided session IDs.
  - **Weak Passwords**: Permitting easily guessable passwords without enforcing complexity.
- **Remediation**:
  - Implement Multi-Factor Authentication (MFA).
  - Align password length, complexity, and expiration policies with NIST 800-63b guidelines.
  - Invalidate session tokens securely upon logout or timeout.

### A08:2021 - Software and Data Integrity Failures
Focuses on making assumptions related to software updates, critical data, and CI/CD pipelines without verifying integrity. Includes Insecure Deserialization.
- **Attack Scenarios**:
  - **Malicious Updates**: A compromised update server distributing a trojanized version of software (e.g., SolarWinds attack).
  - **Insecure Deserialization**: Exploiting Java or PHP deserialization to achieve RCE by manipulating serialized objects.
  - **Untrusted CI/CD**: An attacker modifying code in a pipeline before deployment.
- **Remediation**:
  - Use digital signatures to verify software/data integrity.
  - Ensure dependencies are consuming trusted, signed repositories.
  - Implement strict access control and separation of duties in CI/CD pipelines.

### A09:2021 - Security Logging and Monitoring Failures
Without effective logging and monitoring, breaches cannot be detected or investigated.
- **Attack Scenarios**:
  - Not logging failed login attempts or high-value transactions.
  - Storing logs locally where an attacker can easily wipe them after compromising the server.
  - Lacking automated alerts for suspicious activity (e.g., 100 failed logins per minute).
- **Remediation**:
  - Log all critical access control and server-side validation failures.
  - Forward logs securely to a centralized SIEM.
  - Establish effective monitoring and alerting rules to detect anomalies in real time.

### A10:2021 - Server-Side Request Forgery (SSRF)
SSRF occurs when a web application fetches a remote resource without validating the user-supplied URL.
- **Attack Scenarios**:
  - **Internal Network Scanning**: An attacker inputs a `localhost` or internal IP (e.g., `169.254.169.254` for AWS metadata) into a URL fetching feature to pivot into the internal network.
  - **Bypassing Firewalls**: Making the backend server send requests to services that are otherwise blocked by external firewalls.
- **Remediation**:
  - Enforce "deny by default" network policies or firewall rules.
  - Validate all client-supplied input data and use an allow-list for domains and schemas.
  - Do not send raw responses from remote requests back to clients.

## Chaining Opportunities
- **A05 (Security Misconfiguration) + A10 (SSRF)**: An SSRF vulnerability can be chained with an overly permissive AWS IAM role attached to the EC2 instance, allowing total environment takeover.
- **A03 (Injection) + A07 (Auth Failures)**: SQL injection can be used to bypass authentication mechanisms by altering the SQL query logic or dumping hashed credentials.
- **A06 (Vulnerable Components) + A08 (Integrity Failures)**: Exploiting an outdated deserialization library to achieve remote code execution, leveraging the lack of integrity checks on serialized data.
- **A04 (Insecure Design) + A01 (Broken Access Control)**: Flawed application architecture that inherently trusts user-supplied data leading to mass assignment and subsequent IDOR.

## Related Notes
- [[02 - OWASP API Security Top 10 2023]]
- [[03 - OWASP Mobile Top 10]]
- [[04 - OWASP Testing Guide OTG Web Application]]
- [[05 - OWASP ASVS Application Security Verification Standard]]
- [[10 - SSRF (Server-Side Request Forgery)]]
- [[01 - SQL Injection Core Concepts]]
