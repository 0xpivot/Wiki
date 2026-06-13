---
tags: [reporting, vapt, professional, cvss]
difficulty: intermediate
module: "42 - VAPT Reporting"
topic: "42.09 Proof of Concept"
---

# 42.09 Proof of Concept

## 1. The Core Purpose of a PoC

In the realm of Vulnerability Assessment and Penetration Testing (VAPT), a Proof of Concept (PoC) is the undeniable, empirical evidence that a vulnerability is not merely theoretical, but actual and exploitable. It is the crucial bridge between stating "a vulnerability exists in your software" and demonstrating exactly "how a threat actor abuses this vulnerability to cause harm."

A high-quality PoC serves three critical audiences within the client organization:
1.  **The Triage/Security Team:** To rapidly verify the finding, confirm it is not a scanner false positive, and assign it to the correct engineering queue.
2.  **The Development/Remediation Team:** To reproduce the issue locally in their development environment, understand the exact mechanics of the flaw, and test their subsequent patch against the PoC to ensure the fix is robust.
3.  **The Executive Team:** To understand the tangible impact of the vulnerability through a narrative they can comprehend (e.g., "See how we used this flaw to dump the customer database").

A VAPT report lacking clear, reproducible PoCs is essentially a glorified automated scanner output. Elite consultants craft PoCs that are elegant, minimal, highly readable, and perfectly deterministic.

## 2. Principles of an Elite PoC

Writing an excellent PoC requires adherence to several strict engineering principles:

### 2.1. Determinism and Reproducibility
A PoC must work consistently. If it relies on a highly specific race condition that only triggers 1 out of 100 times, or requires a specific phase of the moon, the remediation team will likely close the ticket as "cannot reproduce." You must isolate all variables. If a specific state is required (e.g., "User A must be logged in, the cart must contain exactly one item, and the billing address must be empty"), explicitly state those prerequisites before detailing the exploit steps.

### 2.2. Minimalism (Occam's Razor)
Strip the exploit down to its absolute bare minimum. Do not provide a massive, complex Python script if a single `curl` command or a basic Burp Suite request achieves the exact same result. The more complex the PoC, the harder it is for a developer to isolate the core flaw from your testing harness.
*   **Bad:** Sending a massive, multi-megabyte payload containing unnecessary obfuscation, custom headers, and redundant encoding.
*   **Good:** Sending the exact HTTP request containing only the required Host header, authorization token, and the precise malicious payload parameter.

### 2.3. Safety and Non-Destruction
A professional PoC must **never** cause damage, alter production data unnecessarily, or cause a Denial of Service (unless explicitly authorized by the client in writing).
*   **For SQL Injection:** Do not run `DROP TABLE` or `UPDATE users SET password='x'`. Run safe enumeration queries like `SELECT @@version` or `SELECT user()`.
*   **For RCE:** Do not run `rm -rf /` or install a persistent reverse shell in a production report. Run benign commands like `id`, `whoami`, or `hostname`.
*   **For XSS:** Do not use `alert('XSS')` (it's annoying, often blocked by modern browsers, and doesn't prove impact). Use `console.log(document.domain)` or create a subtle DOM element demonstrating script execution within the origin context.

## 3. Structuring the PoC Section in a Report

A professional report structures the PoC logically so the reader can seamlessly follow the attack chain from setup to execution to impact. The industry-standard structure is:

1.  **Prerequisites:** What must the attacker have before executing the PoC? (e.g., "A valid low-privileged user account", "Knowledge of the internal project ID").
2.  **Steps to Reproduce:** A highly explicit, numbered list of actions. (e.g., "1. Log in to the application. 2. Navigate to /profile. 3. Intercept the request...").
3.  **The Payload/Request:** The exact code, raw HTTP request, or command-line string used to trigger the vulnerability.
4.  **The Response/Impact:** The exact output or system state change demonstrating successful exploitation.

## 4. Visualizing the PoC Lifecycle

The following ASCII diagram shows the lifecycle of a PoC from initial discovery during the testing phase to remediation validation by the engineering team.

```text
+-----------------------------------------------------------------------------------------+
|                              THE PROOF OF CONCEPT LIFECYCLE                             |
+-----------------------------------------------------------------------------------------+
|                                                                                         |
|  1. DISCOVERY        2. REFINEMENT          3. REPORTING          4. VALIDATION         |
|  +-------------+     +-------------+        +-------------+       +-------------+       |
|  | Messy, raw  |     | Minimize    |        | Document    |       | Developer   |       |
|  | exploit     |     | payload.    |        | steps.      |       | runs PoC    |       |
|  | script or   |---->| Remove      |------->| Format HTTP |------>| to confirm  |       |
|  | complex UI  |     | unnecessary |        | req/res.    |       | the patch   |       |
|  | interaction |     | steps/data. |        | Add context.|       | works.      |       |
|  +-------------+     +-------------+        +-------------+       +-------------+       |
|         |                   |                      |                     |              |
|   (Hacker Mode)      (Engineering Mode)      (Writer Mode)         (Remediation Mode)   |
|                                                                                         |
+-----------------------------------------------------------------------------------------+
```

## 5. Examples of High-Quality PoCs

### Example 1: Insecure Direct Object Reference (IDOR)

**Prerequisites:**
*   Attacker account (User A: Auth Token A)
*   Victim account (User B: ID 1002)

**Steps to Reproduce:**
1.  Log in as the attacker, User A.
2.  Intercept the request to view the user profile: `GET /api/profile/1001`
3.  Modify the ID in the URI from `1001` to the victim's ID, `1002`.
4.  Forward the request. Observe that User B's highly sensitive PII is returned.

**HTTP Request (Attacker):**
```http
GET /api/profile/1002 HTTP/1.1
Host: api.target.com
Authorization: Bearer <User_A_Token>
```

**HTTP Response (Demonstrating Impact):**
```http
HTTP/1.1 200 OK
Content-Type: application/json

{
  "id": 1002,
  "name": "Victim User",
  "email": "victim@target.com",
  "ssn": "XXX-XX-1234"
}
```

### Example 2: Command Injection

**Prerequisites:** None (Unauthenticated External Attacker)

**Steps to Reproduce:**
1.  Navigate to the `/ping` network utility endpoint.
2.  Inject a bash command separator (`;`) followed by the `id` command into the `ip` parameter.
3.  Observe the command output seamlessly appended in the HTTP response.

**cURL Command:**
```bash
curl -X POST https://target.com/api/ping -d "ip=127.0.0.1; id"
```

**Output:**
```text
PING 127.0.0.1 (127.0.0.1): 56 data bytes
64 bytes from 127.0.0.1: icmp_seq=0 ttl=64 time=0.042 ms
uid=33(www-data) gid=33(www-data) groups=33(www-data)
```

## 6. Common Mistakes to Avoid in PoC Writing

1.  **"See attached video":** While a video can be a helpful supplemental piece of evidence for complex UI bugs or race conditions, it should **never** replace written steps and raw HTTP requests. Developers cannot copy-paste text from an MP4 video to build an automated regression test.
2.  **Assuming Context:** Saying "Exploit the parameter using standard SQLmap" is entirely unacceptable. You must provide the exact payload SQLmap generated, or the specific `sqlmap` command line string that works (e.g., `sqlmap -u "http://target" -p id --level 3 --risk 2`).
3.  **Over-Redaction:** While redacting actual passwords or real client PII is correct and necessary, over-redacting the PoC (like blurring out the vulnerable parameter name or the entire URI) makes the report useless for remediation. Redact data, not mechanics.

## Chaining Opportunities
*   A PoC for a chained attack must clearly demarcate the transition between vulnerabilities. E.g., "Step 1-4: Execute IDOR to leak internal JWT token. Step 5-8: Use the leaked JWT token to execute an authenticated RCE payload." This clearly shows how a low severity bug enables a critical one.

## Related Notes
*   [[06 - CVSS v3.1 Scoring]]
*   [[08 - Risk Rating vs CVSS]]
*   [[10 - Screenshots and Evidence]]
