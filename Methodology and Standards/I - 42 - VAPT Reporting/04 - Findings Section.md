---
tags: [reporting, vapt, professional]
difficulty: beginner
module: "42 - VAPT Reporting"
topic: "42.04 Findings Section"
---

# Findings Section

## 1. Introduction

While the Executive Summary is carefully tailored for the C-Suite, the **Detailed Findings Section** is the true operational and technical heart of the Vulnerability Assessment and Penetration Testing (VAPT) report. This section is aggressively consumed by developers, system administrators, security engineers, and DevOps teams. Their goal is simple and pragmatic: understand exactly what is broken, verify that it is actually broken in their environment, and figure out how to fix it permanently.

A poorly written findings section leads to an immediate breakdown in the remediation process. If developers cannot effortlessly reproduce the vulnerability based on your report, they will confidently mark it as a "False Positive," the Jira ticket will be closed, and the system will remain dangerously vulnerable in production. Precision, absolute clarity, and comprehensive, unassailable documentation are non-negotiable here.

In this deep dive, we will construct the perfect template for a technical finding, thoroughly examine the necessary components of a Proof of Concept (PoC), and discuss how to write actionable, code-level remediation advice.

## 2. The Anatomy of a Single Finding

Every individual vulnerability identified during the engagement must be documented using a strict, unvarying, standardized format. Consistency allows the remediation teams to parse the massive document quickly and integrate it into their bug-tracking workflows.

A standard finding consists of the following critical components:

```text
+---------------------------------------------------------------------------------+
|                              The Standard Finding Template                      |
+---------------------------------------------------------------------------------+
|                                                                                 |
|  [ FINDING-001 ] Title of the Specific Vulnerability                            |
|  Severity: Critical | CVSS Score: 9.8 | Status: Open                            |
|                                                                                 |
|  1. Technical Description                                                       |
|     (What is the precise technical nature of the flaw?)                         |
|                                                                                 |
|  2. Business Impact                                                             |
|     (What is the worst-case scenario if successfully exploited?)                |
|                                                                                 |
|  3. Affected Assets                                                             |
|     (Specific URLs, IP addresses, vulnerable Parameters, file paths)            |
|                                                                                 |
|  4. Proof of Concept (PoC)                                                      |
|     (Step-by-step reproduction guide + Raw HTTP Requests + Screenshots)         |
|                                                                                 |
|  5. Remediation Recommendations                                                 |
|     (How to fix it - specific code snippets, config changes, architecture)      |
|                                                                                 |
|  6. References                                                                  |
|     (Links to CVEs, OWASP documentation, Official Vendor Patches)               |
|                                                                                 |
+---------------------------------------------------------------------------------+
```

## 3. Breaking Down the Components

Let us explore each sub-section in excruciating detail, using a classic "SQL Injection" vulnerability as our running technical example.

### 3.1 Title and Meta-Data
The title must be highly descriptive and completely unambiguous. Do not just write lazy titles like "SQL Injection" or "XSS." Provide immediate context.
- **Bad Title:** SQL Injection found on the website.
- **Good Title:** Unauthenticated Blind Time-Based SQL Injection in the `/api/v1/password_reset` Email Parameter.
- **Meta-Data:** Include the assigned qualitative Severity (e.g., High), the exact numerical CVSS v3.1 score (e.g., 8.5), the CVSS Vector string, and a unique tracking ID (e.g., FINDING-03) for easy integration into Jira or ServiceNow.

### 3.2 Description
This section explains the technical nature of the vulnerability. It actively assumes the reader has deep technical knowledge. Explain exactly *why* the flaw exists at the code or architecture level.
**Example:** "The web application fails to properly sanitize user-supplied input provided within the `email` JSON parameter of the `/api/v1/password_reset` endpoint. The raw input is concatenated directly into a backend PostgreSQL query without the use of prepared statements or parameterized queries. This architectural flaw allows an attacker to manipulate the fundamental structure of the SQL statement, forcing the database to execute arbitrary commands."

### 3.3 Business Impact
Developers need to understand the absolute worst-case scenario to prioritize the fix among their other sprint tasks.
**Example:** "Successful exploitation of this vulnerability allows an unauthenticated, remote attacker to slowly extract the entire contents of the backend database. This includes plain-text user PII, bcrypt password hashes, and administrative session tokens. Compromise of this data could lead to complete account takeover for all users, severe reputational damage, and heavy regulatory fines under the GDPR."

### 3.4 Affected Assets
Be exhaustively specific. Do not just list a root domain.
- **URL:** `https://api.acme.com/v1/password_reset`
- **Method:** `POST`
- **Vulnerable Parameter:** `email`
- **IP Address:** `192.168.1.55:443`

### 3.5 Proof of Concept (PoC)
This is the most critical part of the finding. **If they cannot reproduce it, they will not fix it.** 
The PoC must be a foolproof, step-by-step guide that a junior developer can follow blindly and achieve the exploit.

**Step 1:** Intercept the legitimate password reset request using an interception proxy (e.g., Burp Suite).
**Step 2:** Inject the following malicious SQL payload directly into the `email` parameter: `' OR pg_sleep(10)-- -`
**Step 3:** Send the request and strictly observe that the server response is artificially delayed by exactly 10 seconds, conclusively confirming the execution of the injected SQL sleep command.

**Provide the exact raw HTTP Request:**
```http
POST /api/v1/password_reset HTTP/1.1
Host: api.acme.com
Content-Type: application/json
User-Agent: Mozilla/5.0

{"email": "admin@acme.com' OR pg_sleep(10)-- -"}
```

**Provide the exact raw HTTP Response:** (Highlighting the relevant output if applicable, though for blind SQLi, noting the response time is sufficient).

**Screenshots:** Include clean, high-resolution screenshots of Burp Suite or the terminal. 
*Crucial Rule for Screenshots:* Highlight the injected payload and the resulting output with clear red boxes. Crop the image to show only the relevant data, removing clutter like taskbars and other tabs.

### 3.6 Remediation Recommendations
Telling a developer "Fix the SQL Injection" is severely insufficient and unprofessional. You must provide highly actionable, specific advice. Give them the exact methodology to fix the root cause.
**Example:** 
"To properly remediate this vulnerability, the development team must completely avoid concatenating user input directly into SQL queries. 
1. **Primary Fix:** Implement parameterized queries (Prepared Statements) for all database interactions. This ensures the database treats the input as data, not executable code.
2. **Alternative Fix:** Utilize an Object-Relational Mapper (ORM) such as Entity Framework, Hibernate, or Prisma, which natively handles input sanitization by default.
3. **Defense-in-Depth:** Enforce strict input validation on the `email` parameter, ensuring it matches a rigorous standard email Regex format before the server even attempts to process the database query."

### 3.7 References
Provide external validation for your finding. Developers respect authoritative external sources.
- Link to the OWASP Top 10 documentation for Injection.
- Link to the specific language/framework documentation (e.g., secure coding practices for PHP/PDO, Python/SQLAlchemy, or Node.js).
- Link to relevant CVEs if the flaw involves a known vulnerable third-party component (e.g., a vulnerable version of Apache Struts).

## 4. Best Practices for Writing Technical Findings

Writing high-quality technical findings requires strict discipline and attention to detail.

### 4.1 Remove "I" and "We"
Write in an objective, passive, or third-party voice.
**Bad:** "I sent a payload and I saw the server crash."
**Good:** "A malicious payload was sent, resulting in an immediate server crash."

### 4.2 Validate All Findings (Zero False Positives)
Automated scanners generate massive amounts of false positives. A professional VAPT report must NEVER contain a false positive. Every single finding must be manually verified and confirmed by the penetration tester. Submitting a report full of Nessus scanner noise destroys trust entirely and wastes the client's valuable time.

### 4.3 Redact Sensitive Information
During the PoC, you may uncover highly sensitive, real-world data (e.g., actual customer credit cards, real passwords, AWS access keys). **Never put live, sensitive data in the report.** 
Mask the data: `password = MySecretPass123` should be strictly documented as `password = MySec********`.
The goal is to prove the vulnerability exists, not to store stolen data in a PDF that could later be intercepted.

### 4.4 Chain Vulnerabilities Logically
If you used a Low severity Information Disclosure to find a hidden endpoint, which you then hit with a High severity SSRF, document them as entirely separate findings, but explicitly reference the chain in the description. "This vulnerable endpoint was discovered by leveraging the path disclosure vulnerability documented in FINDING-08."

## 5. Integrating Findings with CI/CD and Tracking Systems
Modern organizations will rarely read a 300-page PDF cover to cover. They require the findings to be immediately exportable into their internal tracking systems (Jira, GitHub Issues, ServiceNow).
When drafting findings, assume that the "Title" will become the Ticket Subject, and the "Description", "PoC", and "Remediation" will become the body of the ticket. If your findings are formatted consistently, many consulting firms use Python scripts to automatically parse their Markdown or JSON reports directly into the client's Jira board via API. Therefore, maintaining strict structural formatting across all findings is not just an aesthetic choice; it enables automation.

## 6. Example 2: Insecure Direct Object Reference (IDOR) Mock Finding

To further illustrate the expected depth of a finding, consider this mock IDOR vulnerability format:

**[ FINDING-014 ] Authenticated Insecure Direct Object Reference (IDOR) Leading to Unintended Invoice Access**
**Severity:** HIGH | **CVSS Score:** 7.5 | **CVSS Vector:** `CVSS:3.1/AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N`

**Description:**
The application fails to perform robust, server-side authorization checks on the `/api/v2/invoices/{invoice_id}` endpoint. An authenticated user can easily enumerate the sequential `invoice_id` parameter to view PDF invoices belonging to other registered tenant users within the application. 

**Business Impact:**
Exploiting this vulnerability allows a malicious tenant or disgruntled employee to systematically download hundreds of thousands of confidential billing invoices. These invoices contain PII (Names, Addresses, Phone Numbers) and specific billing amounts, constituting a severe data breach and violating customer confidentiality agreements.

**Proof of Concept:**
1. Authenticate to the application as standard 'User A'.
2. Navigate to the 'My Billing' tab and observe a legitimate request made to download an invoice: `GET /api/v2/invoices/10055 HTTP/1.1`.
3. Intercept the request using Burp Suite and maliciously modify the invoice ID from `10055` to `10056` (which belongs to a different customer account).
4. Observe that the server responds with an HTTP 200 OK and successfully returns the PDF content for the unauthorized invoice, completely bypassing tenant isolation controls.

**Remediation:**
Relying on hard-to-guess identifiers or client-side UI hiding is insufficient. 
1. Implement strict server-side, role-based authorization checks for every single API request. Ensure that the currently authenticated session token explicitly owns the requested `invoice_id` before querying the database.
2. Consider transitioning from easily guessable sequential integers to cryptographically secure Universally Unique Identifiers (UUIDv4) for all object references (e.g., `GET /api/v2/invoices/f47ac10b-58cc-4372-a567-0e02b2c3d479`).

## 7. Conclusion

The Detailed Findings Section is the true operational product of a penetration test. It is the highly technical blueprint required to secure the environment. By providing crystal-clear descriptions, effortlessly reproducible PoCs, and authoritative, framework-specific remediation advice, you empower the client's engineering teams to fix the issues efficiently, ultimately fulfilling the core purpose of the VAPT engagement.

---

### Chaining Opportunities
- **[[02 - VAPT Report Structure]]**: The Findings Section is the core technical component of the overarching report architecture.
- **[[05 - Severity Ratings]]**: Every finding must be assigned an objective severity rating, which dictates how it is prioritized in this section.
- **[[01 - Why Reporting Matters]]**: A poorly written Findings Section directly leads to wasted developer time, a key consequence discussed in the introductory module.
- **[[03 - Executive Summary]]**: The technical details painstakingly documented here must map accurately to the high-level business risks presented to executives.

### Related Notes
- [[Common Vulnerability Scoring System (CVSS)]]
- [[Proof of Concept (PoC) Development]]
- [[Secure Coding Practices for Developers]]
- [[OWASP Top 10 Vulnerabilities]]
