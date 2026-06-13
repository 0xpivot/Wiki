---
tags: [reporting, vapt, professional, template]
difficulty: advanced
module: "42 - VAPT Reporting"
topic: "42.13 Retesting Methodology"
---

# 13 - Retesting Methodology

## Introduction

Retesting is the crucial final phase of the vulnerability management lifecycle within a VAPT engagement.
It is the process of verifying that the remediation strategies implemented by the client have effectively mitigated the vulnerabilities identified in the initial assessment.
Without rigorous retesting, an organization cannot confidently assert that their security posture has improved, and false assumptions about security can lead to disastrous breaches.
This document outlines a standardized, professional approach to conducting and reporting on post-remediation verification.

## The Importance of Retesting

1.  **Verification of Fixes:** Ensure that the implemented patch or configuration change actually addresses the root cause of the vulnerability.
2.  **Identification of Incomplete Fixes:** Often, developers will fix the specific instance of a vulnerability but miss other occurrences or related issues.
3.  **Discovery of New Vulnerabilities:** Sometimes, the process of fixing one issue inadvertently introduces a new one, breaking existing controls.
4.  **Compliance and Audit:** Many regulatory frameworks require proof of remediation, which is formally provided by a signed retesting report.

## The Retesting Lifecycle

The retesting process should be structured and methodical, mirroring the rigor of the initial assessment.

### 1. Preparation and Scoping

Before beginning the retest, ensure clear communication with the client.

-   **Confirm Scope:** Ensure you are only testing the vulnerabilities that the client claims have been fixed. Expanding the scope without authorization is problematic and can lead to scope creep.
-   **Review Remediation Evidence:** Request details from the client regarding how the fix was implemented (e.g., code diffs, configuration changes, patch versions).
-   **Prepare the Environment:** Ensure your testing environment is ready and that any necessary credentials or access have been provisioned exactly as they were during the initial test.

### 2. Execution Phase

The execution phase involves attempting to recreate the initial findings with the same tenacity as before.

-   **Replicate Initial Attack:** Follow the exact steps documented in the original report's proof of concept.
-   **Test for Bypasses:** If the initial attack fails, do not immediately assume the issue is fixed. Actively try to bypass the implemented control. For example, if a WAF rule was added, try different encoding techniques or protocol smuggling.
-   **Assess Related Vectors:** If a parameter was vulnerable to SQLi, check other parameters on the same endpoint, as they might share the same underlying logic.

### 3. Documentation and Reporting

Accurate documentation is critical during the retest.

-   **Update Status:** For each vulnerability, clearly state the new status: Fixed, Partially Fixed, or Not Fixed.
-   **Provide Evidence:** Include screenshots or logs demonstrating either the successful mitigation or the continued exploitability of the issue.
-   **Issue Updated Report:** Provide the client with a formal document detailing the results of the retest.

## ASCII Diagram: Retesting Workflow

```text
+-------------------+       +-------------------+       +-------------------+
| Initial VAPT      |       | Client            |       | Remediation       |
| Report Delivered  +------>+ Implementation    +------>+ Notification      |
|                   |       | Phase             |       | Sent to Testers   |
+-------------------+       +-------------------+       +---------+---------+
                                                                  |
                                                                  v
+-------------------+       +-------------------+       +---------+---------+
| Retesting Report  |       | Execute Retest    |       | Prepare for       |
| Generated &       +<------+ (Replicate,       +<------+ Retest (Review    |
| Delivered         |       | Bypass, Verify)   |       | Evidence)         |
+-------------------+       +---------+---------+       +-------------------+
                                      |
                                      v
                            +---------+---------+
                            | Update Status:    |
                            | - Fixed           |
                            | - Partially Fixed |
                            | - Not Fixed       |
                            +-------------------+
```

## Defining Retest Statuses

Clear definitions are necessary to avoid ambiguity in reporting. Stakeholders rely on these exact classifications.

### Status: Fixed

The vulnerability has been completely resolved. The root cause has been addressed, and all attempts to bypass the implemented controls have failed.

*Example:* A SQL injection vulnerability was remediated by implementing prepared statements. The tester cannot inject any SQL commands, regardless of encoding or payload variations.

### Status: Partially Fixed

The immediate vector has been addressed, but the underlying vulnerability or related issues remain. The risk is reduced but not completely eliminated.

*Example:* An XSS vulnerability was addressed by filtering the `<script>` tag. However, the tester was able to achieve execution using an `<img>` tag with an `onerror` attribute. The application is still vulnerable, but the initial PoC no longer works.

### Status: Not Fixed

The vulnerability remains exploitable using the original methods or trivial variations. The remediation effort was either not implemented or entirely ineffective.

*Example:* A vulnerable software version was supposed to be patched, but the server is still running the old, exploitable version, or the patch deployment failed silently.

## Common Retesting Scenarios and Challenges

### The "WAF Band-Aid"

Clients frequently implement Web Application Firewall (WAF) rules as a quick fix instead of addressing the underlying code flaw.

**Tester Action:** While a WAF provides a layer of defense, it does not fix the vulnerability. The tester must aggressively attempt to bypass the WAF using various encoding schemes, obfuscation techniques, and HTTP request smuggling methods. If the underlying code is still vulnerable, it should be marked as "Partially Fixed," with a note that a WAF is in place but the root cause remains.

### The "Client-Side Validation Only" Fix

Developers sometimes implement input validation only on the client side (e.g., using JavaScript in the browser), assuming this is sufficient.

**Tester Action:** Use an intercepting proxy (like Burp Suite) to bypass the client-side checks and send malicious payloads directly to the server. Demonstrate that the server still accepts and processes the invalid input. Mark as "Not Fixed."

### The "Whack-a-Mole" Fix

A vulnerability is fixed on one specific endpoint or parameter, but the same vulnerable code pattern exists elsewhere in the application.

**Tester Action:** Broaden the testing scope slightly to include similar endpoints or parameters. If the vulnerability is found elsewhere, mark the original finding as "Fixed" but raise a new finding or note that the systemic issue remains unresolved.

## Retesting Automation

While manual verification is always required for complex vulnerabilities, automation can assist and streamline the retesting process.

-   **Scanner Integration:** Re-run specific automated scans to quickly verify the patching of known CVEs or the resolution of simple misconfigurations (e.g., TLS issues).
-   **Custom Scripts:** Develop scripts to replay the exact HTTP requests used in the initial exploitation to check for expected responses quickly.

## The Final Output: The Retest Report

The retest report is typically shorter than the initial VAPT report. It should include:

-   **Executive Summary of Retest:** A brief overview of the results (e.g., "Out of 10 findings, 8 were fixed, 1 was partially fixed, and 1 remains unfixed").
-   **Status Matrix:** A clear table listing all original findings and their current status.
-   **Detailed Retest Notes:** For any finding that is "Partially Fixed" or "Not Fixed," detailed notes and evidence must be provided, explaining *why* the fix was insufficient.

## Conclusion

A robust retesting methodology is essential for ensuring that security assessments lead to meaningful improvements in a client's security posture. It requires diligence, creativity, and clear communication. Without it, the VAPT lifecycle is incomplete.

## Chaining Opportunities

-   During retesting, testers often discover that a "Partially Fixed" vulnerability can still be chained with other issues, necessitating an update to the [[12 - Attack Narrative]].
-   Effective retesting relies heavily on the quality of the original [[11 - Remediation Guidance]]. Poor guidance often leads to failed retests.

## Related Notes

-   [[11 - Remediation Guidance]]
-   [[12 - Attack Narrative]]
-   [[14 - Sample Finding — SQL Injection]]
-   [[15 - Sample Full Report]]
