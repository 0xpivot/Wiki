---
tags: [reporting, vapt, professional, template]
difficulty: advanced
module: "42 - VAPT Reporting"
topic: "42.15 Sample Full Report"
---

# 15 - Sample Full Report

## Introduction

A comprehensive VAPT report is the final, tangible deliverable provided to the client. It must balance high-level strategic summaries for executive leadership with deep technical details for engineering teams.
This document outlines the standard structure of a professional, full-length Vulnerability Assessment and Penetration Testing report, providing templates and guidance for each section.
The quality of this report directly impacts the client's ability to understand their risk posture and take meaningful corrective action.

## Report Structure Overview

A professional report generally follows this structure to ensure logic and flow:

1.  **Document Control**
2.  **Executive Summary**
3.  **Assessment Methodology**
4.  **Scope and Constraints**
5.  **Attack Narrative (Story of the Hack)**
6.  **Summary of Findings**
7.  **Detailed Technical Findings**
8.  **Appendices**

## ASCII Diagram: Report Consumption

```text
+---------------------------------------------------------+
|                  The VAPT Report Audience               |
+---------------------------------------------------------+
                             |
+----------------------------+----------------------------+
|                            |                            |
v                            v                            v
+--------------+             +--------------+             +--------------+
| Executives   |             | Management   |             | Engineering  |
| (CISO, CEO)  |             | (IT/Sec Mgrs)|             | (Devs, Ops)  |
+--------------+             +--------------+             +--------------+
| Reads:       |             | Reads:       |             | Reads:       |
| - Exec       |             | - Methodology|             | - Technical  |
|   Summary    |             | - Scope      |             |   Findings   |
| - High-Level |             | - Finding    |             | - PoCs       |
|   Risk       |             |   Summary    |             | - Remediation|
+--------------+             +--------------+             +--------------+
```

## Section-by-Section Breakdown

### 1. Document Control

This section manages the report's metadata, ensuring version control and confidentiality.

-   **Confidentiality Statement:** "This document contains sensitive information regarding the security posture of [Client Name]. Distribution must be strictly controlled."
-   **Version History:** Table tracking version, date, author, and changes.
-   **Contact Information:** Details of the testing team leads.

### 2. Executive Summary

This is the most critical section for non-technical stakeholders. It must summarize the entire engagement in 1-2 pages.

-   **Objective:** Briefly state the goal of the assessment.
-   **High-Level Risk Statement:** A clear, concise statement of the overall risk (e.g., "The overall risk to the in-scope environment is considered HIGH due to the presence of easily exploitable vulnerabilities allowing complete system compromise.")
-   **Key Findings Summary:** A high-level overview of the most critical issues, devoid of excessive jargon.
-   **Strategic Recommendations:** Broad recommendations for improving the security posture (e.g., "Implement a robust patch management lifecycle," "Deploy a centralized authentication system.")

### 3. Assessment Methodology

Detail *how* the test was conducted. This builds trust and proves the rigor of the assessment.

-   **Frameworks Used:** Mention industry standards like OWASP, PTES, or OSSTMM.
-   **Phases:** Briefly describe the phases: Reconnaissance, Scanning, Exploitation, Post-Exploitation, Reporting.
-   **Tooling:** Provide a high-level list of commercial and open-source tools utilized (e.g., Burp Suite Pro, Nessus, Nmap).

### 4. Scope and Constraints

Clearly define what was tested and what limitations were in place.

-   **In-Scope Assets:** List IP addresses, URLs, API endpoints, and specific applications.
-   **Out-of-Scope Assets:** Explicitly list what was NOT tested to prevent misunderstandings.
-   **Constraints:** Note any limitations, such as "Testing was restricted to non-production hours," or "Denial of Service (DoS) testing was explicitly prohibited."

### 5. Attack Narrative

This section tells the "Story of the Hack," demonstrating the real-world impact of chained vulnerabilities.

*See [[12 - Attack Narrative]] for detailed guidance on constructing this section.*

Include descriptions of:
-   Initial Reconnaissance
-   Gaining Initial Access
-   Lateral Movement
-   Privilege Escalation
-   Action on Objectives (Exfiltration/Impact)

### 6. Summary of Findings

Provide a quick, scannable overview of all discovered vulnerabilities.

-   **Risk Matrix:** A visual representation (e.g., a table or chart) showing the distribution of findings by severity (Critical, High, Medium, Low, Informational).
-   **Findings Table:** A list containing the Finding ID, Title, Severity, and Status.

*Example Table:*
| ID | Finding Title | Severity | Status |
|---|---|---|---|
| F-01 | Unauthenticated SQL Injection in Login Portal | Critical | Open |
| F-02 | Stored Cross-Site Scripting (XSS) in User Profile | High | Open |
| F-03 | Missing HTTP Security Headers | Low | Open |

### 7. Detailed Technical Findings

This is the core of the report for the engineering teams. Each finding must be meticulously documented.

*See [[14 - Sample Finding — SQL Injection]] for a complete template.*

Each finding must include:
-   Title and Severity
-   Detailed Description
-   Impact Statement
-   Step-by-Step Proof of Concept (PoC)
-   Actionable Remediation Guidance (See [[11 - Remediation Guidance]])
-   References

### 8. Appendices

Include supplementary material that supports the report but is too bulky for the main body.

-   **Appendix A: Risk Rating Methodology:** Explain exactly how severity scores (e.g., CVSS vectors) are calculated.
-   **Appendix B: Raw Tool Output:** (Optional) Provide lengthy command outputs or scan results if requested by the client.
-   **Appendix C: Glossary of Terms:** Define technical acronyms and jargon for less technical readers.

## Quality Assurance (QA) Checklist

Before delivering the report, ensure it passes a rigorous QA process:

- [ ] Has the Executive Summary been reviewed for clarity and absence of jargon?
- [ ] Do the technical findings align with the high-level risk statement?
- [ ] Are all PoCs reproducible based *only* on the provided documentation?
- [ ] Is the remediation guidance practical and actionable?
- [ ] Has the document been checked for spelling, grammar, and formatting consistency?
- [ ] Are all sensitive client details appropriately handled and redacted where necessary?

## The Importance of Tone

The tone of the report should be professional, objective, and constructive. Avoid accusatory language ("The developers failed to...") and focus on factual statements ("The application does not adequately sanitize..."). The goal is to partner with the client to improve security, not to assign blame. A supportive tone ensures a long-term partnership with the client.

## Conclusion

A well-written VAPT report is a critical asset for any organization. It transforms technical vulnerabilities into actionable business intelligence, driving meaningful improvements in the client's security posture. It is not just a document; it is a catalyst for change.

## Chaining Opportunities

-   The Full Report serves as the foundational document that triggers the [[13 - Retesting Methodology]] phase.
-   The Executive Summary heavily relies on the business context established in the [[12 - Attack Narrative]].
-   Without the Full Report, the remediation process lacks direction.

## Related Notes

-   [[11 - Remediation Guidance]]
-   [[12 - Attack Narrative]]
-   [[13 - Retesting Methodology]]
-   [[14 - Sample Finding — SQL Injection]]
