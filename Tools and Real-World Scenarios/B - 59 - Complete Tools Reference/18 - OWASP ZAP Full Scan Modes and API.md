---
tags: [tools, web-testing, scanner, vapt]
difficulty: intermediate
module: "59 - Complete Tools Reference"
topic: "59.18 OWASP ZAP Full Scan Modes"
---

# OWASP ZAP: Full Scan Modes, Automation, and API Reference

## 1. Introduction to the ZAP Ecosystem
The OWASP Zed Attack Proxy (ZAP) is a globally recognized, free, and open-source web application security scanner. Maintained by a dedicated international community, ZAP operates fundamentally as a man-in-the-middle (MitM) interception proxy, conceptually similar to Burp Suite. However, ZAP differentiates itself through its open-source philosophy, its deep integration capabilities for automated DevSecOps pipelines, and its unique approach to scanning modes and contexts.

ZAP is designed to be accessible to developers testing their own code, while retaining the depth required by seasoned penetration testers. It supports an extensive ecosystem of add-ons via its integrated marketplace.

## 2. Core Architecture and Context Management
ZAP's architecture revolves around intercepting traffic and building a comprehensive model of the target application.

### 2.1 The Interception Proxy
Like all proxies, ZAP sits between the browser and the server. It captures HTTP and HTTPS traffic (managing its own CA certificate for SSL/TLS decryption) and supports WebSockets natively.

### 2.2 Contexts: Defining the Scope
In ZAP, a "Context" is paramount. A context groups related URLs and defines the rules of engagement for that specific application.
*   **Authentication:** Defines how ZAP should log into the application (e.g., Form-based, HTTP Basic, JSON-based, Script-based).
*   **Session Management:** Defines how ZAP maintains a session (e.g., Cookie-based, Header-based).
*   **Authorization:** Defines how ZAP identifies if it is currently logged in or logged out (e.g., looking for a "Log Out" link or a specific HTTP status code).
*   **Technology Stack:** Defining the underlying technologies (OS, Web Server, Database) allows ZAP to optimize its active scanning payloads, preventing it from sending IIS exploits to an Apache server.

## 3. Comprehensive Scan Modes
ZAP features a unique dropdown menu in its main toolbar that dictates its overall operational behavior. Selecting the appropriate mode is critical for preventing accidental damage.

### 3.1 Safe Mode
*   **Behavior:** Completely read-only and passive.
*   **Capabilities:** ZAP will only proxy traffic and perform passive scanning. All offensive features (Active Scan, Spider, AJAX Spider, Fuzzer) are strictly disabled.
*   **Use Case:** Ideal for exploring highly sensitive production environments where any active modification or automated request could cause data corruption, trigger alarms, or disrupt service availability.

### 3.2 Protected Mode
*   **Behavior:** Limits offensive actions to a defined scope.
*   **Capabilities:** You can only run Active Scans, Spiders, or Fuzzers against URLs that are explicitly added to a "Context" and marked as "In Scope."
*   **Use Case:** The standard mode for targeted penetration testing engagements. It serves as a safety net, preventing accidental attacks against out-of-scope third-party services, analytics endpoints, or CDNs that the application might interact with.

### 3.3 Standard Mode
*   **Behavior:** The default, unrestricted operational mode.
*   **Capabilities:** Allows you to interact with and attack anything you want. You can initiate active scans against any URL visible in the Sites tree.
*   **Use Case:** Useful for local testing environments, staging servers, or broad-scope assessments where you have explicit authorization to test the entire infrastructure.

### 3.4 ATTACK Mode
*   **Behavior:** Highly aggressive, continuous, and automated.
*   **Capabilities:** As soon as a new URL is discovered—either by manually proxying traffic or via automated spidering—ZAP immediately and automatically initiates an Active Scan against it in the background.
*   **Use Case:** Useful for rapid, hands-off scanning of small, contained applications or specific API endpoints. It is strongly discouraged for large or production environments due to its indiscriminate and heavy network traffic footprint.

## 4. Discovery: Traditional vs. AJAX Spider
Mapping the application surface is the prerequisite for effective scanning.

### 4.1 Traditional ZAP Spider
This engine parses HTTP responses (HTML, CSS, JS) and extracts links using regex and DOM parsing. It is exceptionally fast and efficient but fails significantly on modern Single Page Applications (SPAs) built with frameworks like React, Angular, or Vue, where links and routes are generated dynamically by JavaScript in the browser.

### 4.2 AJAX Spider
The AJAX Spider solves the SPA problem by launching a headless browser (like Chrome or Firefox) via Selenium. It physically loads the page, clicks elements, fills out forms, and executes JavaScript. By monitoring the headless browser's network traffic, it discovers API endpoints and routes that are completely invisible to the traditional spider. It is computationally expensive and slow, but necessary for modern web apps.

## 5. Active and Passive Scanning Engines

### 5.1 Passive Scanning
Examines HTTP messages without altering them or sending new requests. It utilizes a rule engine to identify:
*   Missing security headers (`Strict-Transport-Security`, `X-Frame-Options`).
*   Information disclosure (internal IP addresses, stack traces, excessive data exposure).
*   Insecure cookie attributes (missing `Secure` or `HttpOnly` flags).
*   Known vulnerable JavaScript libraries (via Retire.js integration).

### 5.2 Active Scanning
Actively sends malicious payloads to test for vulnerabilities. ZAP utilizes a robust set of rule-based scanners organized into "Release" (stable), "Beta" (in testing), and "Alpha" (experimental) quality tiers.
It tests for all major injection flaws (SQLi, XSS, CMDi, Path Traversal) and logic flaws.

## 6. ZAP OAST capabilities
ZAP incorporates Out-of-Band Application Security Testing (OAST) through the BOAST platform and integrations with services like interactsh. This allows ZAP to detect blind vulnerabilities (like Blind SSRF or Blind OS Command Injection) where the payload triggers an outbound network connection rather than returning data in the immediate HTTP response.

## 7. ZAP Automation Framework (AF) and REST API
ZAP's greatest strength is its design for CI/CD integration.

### 7.1 The REST API
ZAP exposes a comprehensive REST API on its proxy port (e.g., `http://localhost:8080/UI`). Every action possible in the GUI can be triggered programmatically via HTTP requests. You can start spiders, trigger active scans, manage contexts, and retrieve JSON/HTML vulnerability reports.

### 7.2 ZAP Automation Framework (AF)
The Automation Framework provides a YAML-based configuration system. Instead of writing custom scripts against the REST API, you define a "plan" (a YAML file) that outlines a sequence of jobs.
ZAP can execute this plan from the command line in headless mode (`-cmd -autorun plan.yaml`), making it trivial to integrate into Jenkins, GitLab CI, or GitHub Actions.

```yaml
# Example ZAP Automation Plan snippet
env:
  contexts:
    - name: "Target API"
      urls:
        - "https://api.target.local"
jobs:
  - type: openapi
    parameters:
      targetUrl: "https://api.target.local/swagger.json"
  - type: activeScan
    parameters:
      policy: "API Specific Policy"
  - type: report
    parameters:
      template: "traditional-html"
      reportDir: "/workspace/reports"
```

## 8. Architecture Diagram: DevSecOps Automation

```ascii
+----------------+       +-------------------+       +-------------------+
|                |       |                   |       |                   |
| CI/CD Pipeline |       |  ZAP Automation   |       |  Target Staging   |
| (GitLab/GitHub)|------>|  Framework        |------>|  Environment      |
|                | YAML  |  (Headless Mode)  | HTTP  |  (API Backend)    |
+-------+--------+ Plan  +---------+---------+       +-------------------+
        |                          |                           |
        | 1. Trigger Build         | 2. Parse Swagger/OpenAPI  |
        |                          | 3. Execute Active Scan    |
        |                          |                           |
        |<-------------------------+                           |
        | 4. Return JUnit XML/JSON |                           |
+-------v--------+                 |                           |
| Build Failure  |                 |                           |
| if High Vulns  |                 |                           |
+----------------+                 |                           |
```

## 9. Advanced Scripting with Zest
For scenarios where standard rules fail, ZAP supports scripting in Zest (a visual scripting language developed by Mozilla), JavaScript, Groovy, and Python. Testers can write custom active scan rules, targeted payload generators, or scripts that execute dynamically when specific requests are processed by the proxy.

## 10. Chaining Opportunities
*   **[[16 - Burp Suite Pro Complete Feature Reference]]:** Export API definitions (OpenAPI/Swagger) discovered manually in Burp, and import them into ZAP to leverage ZAP's specific API active scanning rules via its CLI for regression automation.
*   **[[19 - ffuf Advanced Usage]]:** Use `ffuf` to rapidly identify hidden directories and API endpoints. Feed the resulting clean list of live URLs directly into ZAP's Active Scanner via the REST API, bypassing the need for a slow, comprehensive crawl.

## 11. Related Notes
*   [[04 - API4 — Unrestricted Resource Consumption]] - ZAP's fuzzer and active scanner can be utilized to test rate limiting and resource exhaustion vulnerabilities by sending high volumes of crafted requests.
*   [[07 - API7 — Server Side Request Forgery (SSRF)]] - ZAP's integrated OAST features and specific SSRF payloads are essential for discovering blind SSRF vulnerabilities.
*   [[10 - API10 — Unsafe Consumption of APIs]] - ZAP can be configured to proxy traffic from back-end microservices to test how they consume data from internal, less-trusted APIs.
