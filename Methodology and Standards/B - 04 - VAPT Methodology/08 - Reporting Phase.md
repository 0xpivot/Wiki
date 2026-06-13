---
tags: [vapt, methodology, reporting, beginner]
difficulty: beginner
module: "04 - VAPT Methodology"
topic: "04.08 Reporting Phase"
---

# 04.08 — Reporting Phase

## What is it?

The report is the primary deliverable of any penetration test — it's what the client pays for. A well-written report must communicate technical findings to both technical teams (who need to fix them) and management (who needs to understand business risk and approve resources). A finding that can't be explained clearly is a finding that won't get fixed.

---

## Report Structure

```
┌─────────────────────────────────────────────────────┐
│ PENETRATION TEST REPORT                             │
│                                                     │
│ 1. EXECUTIVE SUMMARY (1-2 pages)                    │
│    → For: CEO, CISO, Board                         │
│    → No technical jargon                           │
│    → Overall risk level, key findings, priorities  │
│                                                     │
│ 2. SCOPE AND METHODOLOGY                            │
│    → What was tested, tools used, dates             │
│    → Testing approach (black/grey/white box)        │
│                                                     │
│ 3. FINDINGS SUMMARY                                 │
│    → Table of all findings with severity            │
│    → Risk distribution chart                        │
│                                                     │
│ 4. DETAILED FINDINGS                                │
│    → One section per vulnerability                  │
│    → Steps to reproduce, PoC, screenshots          │
│    → Business impact, remediation                   │
│                                                     │
│ 5. REMEDIATION ROADMAP                              │
│    → Prioritized fix list                           │
│    → Short term (critical), medium, long term       │
│                                                     │
│ 6. APPENDICES                                       │
│    → Raw tool output, full request/response logs   │
│    → Methodology checklists                         │
└─────────────────────────────────────────────────────┘
```

---

## Executive Summary (Write This Last)

```
STRUCTURE:
  Paragraph 1: CONTEXT
    "We performed a [web application / network] penetration test of 
    [target.com] between [dates] to assess its security posture."
  
  Paragraph 2: OVERALL RISK
    "The assessment identified [X] critical, [Y] high, [Z] medium, 
    and [W] low severity findings. The overall risk rating is HIGH."
  
  Paragraph 3: KEY FINDINGS (top 3 max, non-technical)
    "The most critical finding was an unauthenticated access vulnerability 
    that allowed our team to access the customer database, which contained 
    [N] records including names, emails, and hashed passwords."
  
  Paragraph 4: RECOMMENDATIONS
    "We recommend immediate patching of critical findings within 30 days,
    followed by a retest to verify remediation effectiveness."
  
LANGUAGE:
  ✓ "An attacker could steal customer credit card data"
  ✗ "SQL injection vulnerability in the user parameter"
  
  Business language, not technical!
```

---

## Individual Finding Template

```
FINDING: SQL Injection in User Profile Endpoint
Severity: CRITICAL (CVSS: 9.8)
Status: Open (Unpatched)

DESCRIPTION:
  A SQL injection vulnerability exists in the /api/user/profile endpoint.
  The id parameter is not sanitized before being used in a database query,
  allowing an attacker to read arbitrary data from the database.

RISK:
  An unauthenticated attacker can extract all data from the database,
  including usernames, password hashes, email addresses, and payment 
  information for all [N] users. This constitutes a complete data breach.

STEPS TO REPRODUCE:
  1. Send the following HTTP request to the application:
     
     GET /api/user/profile?id=1' OR SLEEP(5)-- HTTP/1.1
     Host: target.com
     
  2. Observe the response delay of approximately 5 seconds, confirming 
     the injection is processed by the database.
  
  3. Extract database version using:
     GET /api/user/profile?id=1 UNION SELECT version(),2,3-- HTTP/1.1
     
     Response: MySQL 5.7.31

EVIDENCE:
  [Screenshot 1: Burp request with payload]
  [Screenshot 2: Response with 5-second delay]
  [Screenshot 3: UNION-based output with version string]

IMPACT:
  Confidentiality: HIGH (all customer data exposed)
  Integrity: HIGH (attacker can modify database records)
  Availability: MEDIUM (attacker could delete data)

REMEDIATION:
  Immediate: 
    Use parameterized queries / prepared statements:
    $stmt = $pdo->prepare("SELECT * FROM users WHERE id = ?");
    $stmt->execute([$id]);
  
  Additional:
    Implement input validation (id must be integer)
    Apply principle of least privilege to database user
    Enable MySQL query logging for audit trail

REFERENCES:
  OWASP: A03:2021 – Injection
  CWE-89: Improper Neutralization of Special Elements in SQL Query
```

---

## CVSS Scoring for Reports

```
CALCULATE CVSS SCORE:
  Online: https://www.first.org/cvss/calculator/3.1

EXAMPLE SCORES:
  SQLi (no auth, full read/write):
    AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H = 9.8 CRITICAL
  
  Stored XSS (auth required):
    AV:N/AC:L/PR:L/UI:R/S:C/C:L/I:L/A:N = 5.4 MEDIUM
  
  IDOR (auth required, user data):
    AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N = 6.5 MEDIUM
  
  Missing HSTS header:
    AV:N/AC:H/PR:N/UI:R/S:U/C:L/I:L/A:N = 4.2 MEDIUM (informational)
```

---

## Remediation Prioritization

```
PRIORITY MATRIX:
  
  CRITICAL (fix within 24-72 hours):
  - Unauthenticated RCE
  - Unauthenticated SQLi with database access
  - Authentication bypass to admin
  - Exposed credentials/secrets
  
  HIGH (fix within 30 days):
  - Authenticated SQLi
  - Stored XSS on admin pages
  - SSRF to internal systems
  - Broken access control (IDOR)
  
  MEDIUM (fix within 90 days):
  - Missing security headers
  - Reflected XSS (user interaction required)
  - Information disclosure
  - Weak session management
  
  LOW/INFORMATIONAL (fix in next development cycle):
  - SSL certificate issues
  - Outdated software (no public exploit)
  - Missing cookies flags (non-session cookies)
  - Verbose error messages
```

---

## Documentation During Testing

```
CAPTURE DURING TESTING (not after!):

FOR EVERY FINDING:
  □ Full HTTP request (Burp → copy as curl command)
  □ Full HTTP response
  □ Screenshot of the vulnerability
  □ Screenshot of the impact (data accessed, etc.)
  □ Timestamp (important for legal protection!)
  □ Tool command used

BURP SUITE: Save project → Export HTTP history
            Right-click request → Save item

NOTES FORMAT:
  ## [IP/URL] - [Port/Path] - [Vuln Name]
  Time: 2025-01-15 14:32:00 UTC
  Request:
  [paste request]
  Response:
  [paste relevant response]
  Note: [what this proves]
```

---

## Related Notes
- [[07 - Post-Exploitation Phase]] — data for the report
- [[Module 11 - Reporting Templates]] — full report templates
