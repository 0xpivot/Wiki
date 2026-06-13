---
tags: [vapt, methodology, owasp, beginner]
difficulty: beginner
module: "04 - VAPT Methodology"
topic: "04.11 OWASP Testing Guide Overview"
---

# 04.11 — OWASP Testing Guide Overview

## What is it?

The OWASP Testing Guide (OTG) is the de facto standard methodology for web application security testing. It provides a structured, comprehensive checklist of security tests organized by category. Version 4.2 (2020) contains over 90 test cases covering every aspect of web security.

---

## OWASP Testing Guide Structure

```
OTG-INFO: Information Gathering (10 tests)
  INFO-01: Search engine discovery
  INFO-02: Web server fingerprinting
  INFO-03: Web application fingerprinting
  INFO-04: Application entry points
  INFO-05: Review content for sensitive data
  INFO-06: Identify application entry points
  INFO-07: Map execution paths
  INFO-08: Fingerprint web framework
  INFO-09: Fingerprint web application
  INFO-10: Map application architecture

OTG-CONF: Configuration and Deployment (11 tests)
  CONF-01: Network/infrastructure configuration
  CONF-02: Application platform configuration
  CONF-03: File extension handling
  CONF-04: Backup and unreferenced files
  CONF-05: HTTP methods
  CONF-06: HTTP Strict Transport Security
  CONF-07: HTTP policy (security headers)
  CONF-08: RIA cross-domain policy
  CONF-09: File permission
  CONF-10: Subdomain takeover
  CONF-11: Cloud storage

OTG-IDNT: Identity Management (5 tests)
  IDNT-01: Role definitions
  IDNT-02: User registration process
  IDNT-03: Account provisioning process
  IDNT-04: Account enumeration
  IDNT-05: Weak/unenforced username policy

OTG-ATHN: Authentication (10 tests)
  ATHN-01: Credentials over encrypted channel
  ATHN-02: Default credentials
  ATHN-03: Account lockout
  ATHN-04: Authentication bypass
  ATHN-05: Vulnerable "remember password"
  ATHN-06: Browser cache weaknesses
  ATHN-07: Password policy
  ATHN-08: Security questions
  ATHN-09: Weak authentication
  ATHN-10: Stronger authentication

OTG-AUTHZ: Authorization (4 tests)
  AUTHZ-01: Directory traversal/file include
  AUTHZ-02: Bypassing authorization schema
  AUTHZ-03: Privilege escalation
  AUTHZ-04: IDOR

OTG-SESS: Session Management (8 tests)
  SESS-01: Cookie attributes (flags)
  SESS-02: Cookie attributes (scope)
  SESS-03: Session fixation
  SESS-04: Exposed session variables
  SESS-05: CSRF
  SESS-06: Logout functionality
  SESS-07: Session timeout
  SESS-08: Session puzzling

OTG-INPV: Input Validation (19 tests)
  INPV-01: Reflected XSS
  INPV-02: Stored XSS
  INPV-03: HTTP verb tampering
  INPV-04: HTTP parameter pollution
  INPV-05: SQL injection (multiple subtypes)
  INPV-07: XML injection
  INPV-08: SSI injection
  INPV-09: XPath injection
  INPV-10: IMAP/SMTP injection
  INPV-11: Code injection
  INPV-12: Command injection (OS)
  INPV-13: Buffer overflow
  INPV-14: Format string
  INPV-15: HTTP smuggling
  INPV-16: HTTP splitting/smuggling
  INPV-17: Template injection (SSTI)
  INPV-18: XXE
  INPV-19: SSRF

OTG-ERRH: Error Handling (2 tests)
OTG-CRYP: Weak Cryptography (4 tests)
OTG-BUSL: Business Logic (9 tests)
OTG-CLIENT: Client-Side (12 tests)
  DOM XSS, JavaScript execution, WebSocket, CSS injection, etc.
OTG-APIT: API Testing (separate section)
```

---

## How to Use OTG During Testing

```
CHECKLIST APPROACH:
  For each test case:
  [ ] Test applicable? (if endpoint exists)
  [ ] Test executed?
  [ ] Finding? (Yes/No/N/A)
  [ ] Documented?
  
  Example checklist entry:
  INPV-05.1 SQL Injection (classic)
  [ ] Tested URL parameters
  [ ] Tested POST body
  [ ] Tested HTTP headers
  [ ] Tested cookies
  Finding: YES - /api/user?id= parameter vulnerable
  Severity: Critical

TOOL MAPPING:
  OTG-INFO-01 (search engines) → Google dorks, Shodan
  OTG-CONF-05 (HTTP methods) → curl -X OPTIONS, nmap
  OTG-ATHN-02 (default creds) → hydra, manual testing
  OTG-INPV-05 (SQLi) → sqlmap, manual
  OTG-INPV-01/02 (XSS) → Burp scanner, manual
  OTG-SESS-05 (CSRF) → Burp CSRF PoC generator
```

---

## OWASP Top 10 vs OWASP Testing Guide

```
OWASP TOP 10 (2021):
  → Awareness document
  → "These are the most important risk categories"
  → 10 broad categories (A01-A10)
  → What to fix, not how to find

OWASP TESTING GUIDE (v4.2):
  → Detailed testing methodology
  → "Here's HOW to find each type of vulnerability"
  → 90+ specific test cases
  → Checklists, test cases, example payloads

USE BOTH:
  Top 10 → prioritize what to test
  OTG → how to test each category
```

---

## Beginner Testing Priorities (By Impact)

```
START HERE (highest impact, most learnable):

1. IDOR (OTG-AUTHZ-04):
   - Change ID numbers in requests
   - Access other users' data
   - Quick win, high reward in bug bounty

2. SQLi (OTG-INPV-05):
   - Test all parameters with ' and SQL keywords
   - Critical finding if found

3. XSS (OTG-INPV-01/02):
   - Test all inputs for <script> reflection
   - Important for session hijacking

4. Authentication Bypass (OTG-ATHN-04):
   - Test without credentials
   - Test with modified tokens

5. Broken Access Control (OTG-AUTHZ-02):
   - Change user IDs, role values
   - Test unprivileged user on admin functions

6. Security Misconfiguration (OTG-CONF):
   - Default credentials
   - Exposed admin panels
   - Debug mode enabled
```

---

## Related Notes
- [[05 - Vulnerability Identification Phase]] — using OTG in practice
- [[12 - Legal and Ethical Considerations]] — scope of testing
- [[Module 06 - Web Vulnerabilities]] — detailed testing for each vuln type
