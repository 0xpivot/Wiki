---
tags: [reporting, vapt, professional, cvss]
difficulty: intermediate
module: "42 - VAPT Reporting"
topic: "42.10 Screenshots and Evidence"
---

# 42.10 Screenshots and Evidence

## 1. The Critical Role of Visual Evidence

While a highly detailed, text-based Proof of Concept (PoC) is the absolute foundation of a technical finding, visual evidence in the form of well-crafted screenshots is crucial for contextualizing the attack. Screenshots serve as the visual "anchor" for the reader, providing immediate, undeniable confirmation of the vulnerability's existence and real-world impact.

Visual evidence bridges the gap between the technical reality and the human reader. A non-technical CISO or a product manager might not fully grasp the intricacies of a Burp Suite HTTP request containing a complex, serialized Java payload, but they will instantly understand the severity of a screenshot showing a root shell prompt (`root@prod-db-01:~#`) or an administrative dashboard accessed without providing a password.

However, capturing and presenting screenshots professionally is an art form. Poorly formatted, cluttered, unannotated, or confusing screenshots severely degrade the perceived quality and authority of a VAPT report.

## 2. Core Principles of Professional Screenshots

To create elite, report-ready screenshots, consultants must strictly adhere to the following principles:

### 2.1. Clarity, Focus, and Cropping
A single screenshot must illustrate exactly one point. Do not capture your entire 4K monitor showing your email client, Slack messages, terminal tabs, and Spotify player in the background. Crop the screenshot to focus entirely on the relevant window, terminal, or UI element. The reader should never have to hunt for the relevant information within a sea of pixels.

### 2.2. Highlighting and Annotation
Never assume the reader knows exactly where to look. Use professional annotation tools (like Snagit, Flameshot, or Greenshot) to draw immediate attention to the critical components.
*   **Red/Orange Boxes:** Use clean, thin-lined boxes to highlight the vulnerable input parameter, the injected payload, or the resulting impact (e.g., the `uid=0(root)` output in a terminal).
*   **Arrows:** Use clear arrows to show the flow of execution if it involves multiple UI steps or complex data flow.
*   **Obfuscation (Blur/Pixelate):** Use blur tools to redact sensitive client data (real PII, actual passwords, active session tokens, internal IP addresses of non-target systems) that are not strictly necessary to prove the mechanics of the vulnerability.

### 2.3. Contextual Sequencing
For complex vulnerabilities, a single screenshot is rarely sufficient. Use a sequence of screenshots that logically follow the written "Steps to Reproduce."
1.  **Screenshot 1:** The initial state, or the crafted payload being entered into the application UI.
2.  **Screenshot 2:** The intercepted request in Burp Suite (highlighting the modification of the parameter).
3.  **Screenshot 3:** The final execution or impact on the target system (e.g., the database data returned, or the shell execution).

## 3. Visualizing Screenshot Best Practices

The following ASCII diagram contrasts a poor, amateur screenshot approach with a professional, consultant-grade approach.

```text
+------------------------------------------------------------------------------------------+
|                            SCREENSHOT BEST PRACTICES                                     |
+------------------------------------------------------------------------------------------+
|                                                                                          |
|   [ AMATEUR SCREENSHOT ]                                                                 |
|   +------------------------------------------------------------------------------+       |
|   | [Spotify] [Slack: "Hey, order pizza"] [Browser: StackOverflow]               |       |
|   |                                                                              |       |
|   |   +----------------------------------------------------------------------+   |       |
|   |   | Terminal - full screen, tiny text.                                   |   |       |
|   |   | User typed something here, maybe an exploit?                         |   |       |
|   |   | Lots of irrelevant output...                                         |   |       |
|   |   | root@target:~# id                                                    |   |       |
|   |   | uid=0(root) gid=0(root)                                              |   |       |
|   |   | ...more irrelevant output...                                         |   |       |
|   |   +----------------------------------------------------------------------+   |       |
|   |                                                                              |       |
|   | (Reader has to zoom in 500% and search the entire screen to find the impact) |       |
|   +------------------------------------------------------------------------------+       |
|                                                                                          |
|   [ PROFESSIONAL SCREENSHOT ]                                                            |
|   +-------------------------------------------------------+                              |
|   | root@target-prod-db:~# id                             | <--- Cropped tightly.        |
|   | +---------------------------------------------------+ |                              |
|   | | uid=0(root) gid=0(root) groups=0(root)            | | <--- Highlight Box           |
|   | +---------------------------------------------------+ |      draws the eye           |
|   | root@target-prod-db:~# cat /etc/shadow | grep root    |      immediately.            |
|   | root:!!:19000:0:99999:7:::                            |                              |
|   +-------------------------------------------------------+                              |
|                                                                                          |
+------------------------------------------------------------------------------------------+
```

## 4. Specific Tooling Evidence Guidelines

Different types of evidence and tools require specific handling when integrated into professional reports.

### 4.1. Web Application Proxies (Burp Suite / OWASP ZAP)
When showing HTTP requests and responses from intercepting proxies:
*   Crop to show only the Request and Response panes. Exclude the Site Map tree or Proxy History list unless specifically demonstrating structure or a sequence of requests.
*   Highlight the specific HTTP header or parameter being injected.
*   Highlight the specific data leaked, or the stack trace error generated in the response.
*   Ensure word-wrap is enabled so long payloads aren't cut off at the right edge of the screen.

### 4.2. Command Line / Terminal Output
When showing reverse shells, command execution, or tool output (like Nmap, SQLmap, or custom Python scripts):
*   Increase the terminal font size before taking the screenshot. Terminal text is notoriously difficult to read when scaled down to fit within a PDF report margins.
*   Crop out empty, black terminal space.
*   Clear the screen (`clear` or `cls`) before executing the final PoC command to remove distracting prior commands, failed exploit attempts, or spelling errors.

### 4.3. Source Code (Whitebox Analysis / SAST)
When proving vulnerabilities found via source code review:
*   Use an IDE with proper syntax highlighting (e.g., VS Code, IntelliJ). Do not screenshot raw text files in basic Notepad.
*   Ensure line numbers are clearly visible in the screenshot to aid developers in locating the exact file and line.
*   Highlight the specific vulnerable line or function call (e.g., highlighting an unsafe `eval(userInput)` or `exec()` call).

## 5. Captions and Explicit Referencing

A screenshot floating randomly in a document without context is worse than useless; it is confusing. Every single piece of visual evidence must have a descriptive caption and be explicitly referenced in the preceding text.

**Example Implementation in a Report:**
> "...As demonstrated in Step 3, by appending the single quote character (`'`) to the `user_id` parameter, a syntax error is generated by the backend database. This confirms the presence of SQL Injection and reveals the underlying database engine."
>
> **Figure 1.3:** *Burp Suite Repeater showing the injected payload in the `user_id` parameter (left) and the resulting Microsoft SQL Server ODBC driver error in the HTTP response (right).*
>
> `[ SCREENSHOT INSERTED HERE ]`

## 6. The Danger of "Screenshot as PoC"

A critical failure mode for junior consultants is relying *solely* on screenshots as the Proof of Concept. Screenshots are **supplemental evidence**. They cannot be copied and pasted by developers attempting to reproduce the issue or build a unit test.

Always provide the raw, copy-pasteable text (the `curl` command, the raw HTTP request block, the exploit script code) in standard text format, and use the screenshot purely to *visually prove* that the text payload resulted in successful exploitation.

## Chaining Opportunities
*   When documenting complex chained exploits, visual evidence should clearly show the transition states. For example, a screenshot showing the extraction of an API key via Local File Inclusion (LFI), followed immediately by a screenshot of that specific key being used in a cURL request to authenticate to a sensitive administrative endpoint.

## Related Notes
*   [[08 - Risk Rating vs CVSS]]
*   [[09 - Proof of Concept]]
