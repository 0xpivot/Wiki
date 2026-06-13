---
tags: [API, VAPT, API9, Inventory, Shadow-API, Zombie-API, Documentation]
difficulty: beginner
module: "31 - API Security"
topic: "31.09 API9 - Improper Inventory Management"
---

# API9:2023 — Improper Inventory Management

## 1. Executive Summary

Improper Inventory Management (API9:2023, previously known as Improper Assets Management in 2019) highlights the risks associated with blind spots in an organization's API ecosystem. You cannot secure what you do not know exists. As organizations embrace microservices and rapid CI/CD deployment models, the number of API endpoints, versions, and environments multiplies exponentially. 

When documentation lags behind deployment, organizations suffer from **Shadow APIs** (undocumented, unknown APIs) and **Zombie APIs** (deprecated but still active APIs). These forgotten endpoints often lack modern security controls, rate limiting, and authorization checks present in the current production versions, making them highly attractive, low-hanging fruit for attackers.

## 2. Deep Dive: Core Concepts

The root cause of API9 is the failure to treat APIs as first-class IT assets with a defined lifecycle (Design -> Deploy -> Maintain -> Deprecate -> Retire).

### Shadow APIs vs. Zombie APIs
*   **Shadow APIs:** These are endpoints that were deployed without the knowledge of the security or operations teams. They might be spun up by developers for testing, created as quick workarounds, or deployed outside the official API Gateway. Because they bypass governance, they are rarely monitored by Web Application Firewalls (WAFs) or SIEMs.
*   **Zombie APIs:** These are old versions of APIs (e.g., `/api/v1/`) that were supposed to be retired when a newer version (e.g., `/api/v2/`) was released. However, they are left running "just in case" some legacy clients still depend on them. Over time, the security team focuses on patching `v2`, leaving `v1` exposed to unpatched vulnerabilities.

### Third-Party Data Exposure
Improper inventory isn't just about internal endpoints. It also includes failing to inventory which third-party APIs share data with your systems, and what data your APIs are broadcasting out to integrated partners.

### Visualizing the Inventory Blind Spot

```ascii
    [ Attack Surface of Poor Inventory Management ]

    Public Internet
          |
    +-----+---------------------------------------------------------------+
    |                                                                     |
    |  [ WAF / API Gateway ] (Secured, Monitored)                         |
    |         |                                                           |
    |         v                                                           |
    |  [ POST /api/v3/users ] -> Strict Auth, Rate Limited, Audited       |
    |                                                                     |
    |---------------------------------------------------------------------|
    |                                                                     |
    |                  [ The "Blind Spot" Bypass ]                        |
    |                                                                     |
    |  --> [ POST /api/v1/users ] -> (Zombie) BOLA vuln, unpatched!       |
    |                                                                     |
    |  --> [ GET /beta/admin_debug ] -> (Shadow) No Auth! Developer test. |
    |                                                                     |
    |  --> [ qa-api.target.com ] -> (Staging) Connected to Prod DB!       |
    +---------------------------------------------------------------------+
```

## 3. Real-World Exploitation Scenarios

### Scenario A: The Zombie API (Version Rollback Attack)
A mobile application was recently updated to use `/api/v2/auth/login`, which implements strict rate-limiting and requires Multi-Factor Authentication (MFA).

**The Flaw:** The backend server still hosts and routes `/api/v1/auth/login`, which only requires a username and password and lacks rate limiting.
**The Exploit:** An attacker intercepts the mobile app traffic, notices the `/v2/` endpoint, and guesses the existence of `/v1/`. They point their automated credential stuffing tool at `POST /api/v1/auth/login`. Because it lacks MFA and rate limits, the attacker successfully compromises thousands of accounts, bypassing all the security investments made in `v2`.

### Scenario B: Shadow API Discovered via Mobile App Reversing
A company develops a new "hidden" feature intended for an upcoming release. They push the backend endpoints to production but hide the UI elements in the web application.
**The Exploit:** An attacker decompiles the company's Android APK (`.apk`) using tools like `apktool` and `jadx`. Inside the source code, they find hardcoded strings pointing to `https://api.target.com/v1/internal/feature_preview`. Since the developer assumed nobody knew the URL, they didn't implement authorization checks. The attacker accesses the endpoint and leaks unreleased product data.

### Scenario C: The Staging Environment Blunder
Developers set up `staging-api.target.com` to test a new database migration. To ensure the tests are accurate, they connect the staging API directly to a read-replica of the **Production Database**.
**The Flaw:** The staging environment does not have the WAF enabled, uses weak default API keys, and has verbose error logging enabled.
**The Exploit:** The attacker runs a subdomain enumeration tool (like `Amass` or `Sublist3r`), discovers the staging subdomain, and exploits a simple SQL Injection vulnerability that was caught by the WAF in production, but successfully executes in staging, dumping the entire production user table.

## 4. Detection and Identification

Finding Shadow and Zombie APIs requires an attacker mindset—enumerating the infrastructure from the outside in.

1.  **Subdomain Enumeration:** Hunting for environments like `dev.api.`, `qa.`, `uat.`, `staging.`.
2.  **Directory Brute-forcing & Fuzzing:** Using tools like Kiterunner or ffuf to guess API paths:
    *   Fuzzing versions: `/api/v1/`, `/api/v2/`, `/api/v3/`
    *   Fuzzing environments: `/api/mobile/`, `/api/web/`, `/api/internal/`
3.  **OSINT and Historical Data:** Searching the Wayback Machine or AlienVault OTX for endpoints that existed months or years ago to see if they still respond.
4.  **Reverse Engineering Client Apps:** Decompiling Mobile Apps (iOS/Android), inspecting Thick Clients (Electron apps), or analyzing Webpack bundles (`.js.map` files) in Single Page Applications (SPAs) to find undocumented routing maps.
5.  **Exposed Documentation:** Finding accidentally exposed Swagger (`/swagger.json`, `/v2/api-docs`), OpenAPI specs, or GraphQL Introspection queries that map the entire API surface.

## 5. Defense in Depth and Mitigation

To properly secure an API inventory, organizations must merge process, governance, and technology.

### Process & Governance
1.  **API Lifecycle Management:** Establish a strict policy for deprecating APIs. When `v3` is released, a timeline must be enforced to retire `v1`. Send warnings to clients using `v1` (via headers or emails) and eventually return HTTP `410 Gone`.
2.  **Environment Separation:** Never connect staging, QA, or development APIs to production databases. Data masking and synthetic data should be used for lower environments.
3.  **Documentation as Code:** Require developers to define the API schema (e.g., OpenAPI v3) before writing the code. Generate code from the spec, or generate the spec from the code automatically during the CI/CD pipeline. No undocumented API should be allowed to compile and deploy.

### Technical Controls
1.  **API Gateway Enforcement:** Route *all* API traffic through a centralized API Gateway. Configure the gateway to reject requests to paths that are not explicitly defined in the deployed OpenAPI specification (Positive Security Model).
2.  **Automated Discovery Tools:** Deploy API Security Posture Management (ASPM) tools (like Noname Security, Salt Security, or Traceable AI). These tools ingest traffic mirrors from load balancers and Kubernetes clusters to build a real-time, dynamic inventory of every endpoint actually receiving traffic, instantly highlighting Shadow APIs.
3.  **Continuous External Attack Surface Management (EASM):** Continuously scan your organization's external footprint to identify forgotten subdomains or exposed developer environments.

## 6. Chaining Opportunities

Improper Inventory Management frequently opens the door to older, unmitigated vulnerabilities:
*   **[[01 - API1 — Broken Object Level Authorization (BOLA)]]:** Zombie APIs often contain unpatched BOLA flaws that were fixed in newer versions.
*   **[[03 - API3 — Broken Object Property Level Authorization]]:** Undocumented internal endpoints are notorious for exposing excessive data properties.
*   **[[08 - API8 — Security Misconfiguration]]:** Staging environments often have debugging enabled and WAFs disabled.

## 7. Related Notes
- [[API Documentation Security (Swagger & OpenAPI)]]
- [[External Attack Surface Management (EASM)]]
- [[Reverse Engineering Mobile APIs]]
- [[Subdomain Enumeration Techniques]]

---
*End of Note*
