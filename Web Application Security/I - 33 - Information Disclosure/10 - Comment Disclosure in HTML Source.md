---
tags: [vapt, information-disclosure, reconnaissance, html, beginner]
difficulty: beginner
module: "33 - Information Disclosure"
topic: "33.10 Comment Disclosure in HTML Source"
---

# Comment Disclosure in HTML Source

## 1. Introduction

In the modern web development ecosystem, developers frequently utilize comments within their code to document functionality, leave notes for their team, quickly disable sections of code during testing, or keep track of to-do items. While comments are fundamentally an essential aspect of writing maintainable code, they can become a significant security vulnerability when they inadvertently bleed from the development environment into production.

Comment Disclosure in HTML (and associated client-side files like JavaScript, CSS, or Source Maps) represents one of the most classic, yet persistently common forms of Information Disclosure. Because the browser must parse and render these files on the client's local machine, any text embedded within them—including comments—is fully visible to anyone who chooses to simply "View Page Source" or inspect the application's resources.

This vulnerability rarely leads to direct system compromise on its own, but it serves as a critical phase in the reconnaissance lifecycle. Information gleaned from comments frequently accelerates the discovery of more severe vulnerabilities.

## 2. The Psychology and Mechanics of Developer Comments

### Why Do Developers Leave Comments?
To understand how to exploit comment disclosure, an attacker (or penetration tester) must understand the mind of the developer. Development is a collaborative, high-pressure, and deadline-driven process. The underlying reasons for leaving sensitive comments usually stem from:

1. **Debugging and Troubleshooting:** During an active bug-hunting session, a developer might temporarily hardcode a test credential or a bypass flag, wrap it in comments, and push it to a staging environment. When moving to production, they might forget to remove the commented-out code.
2. **Technical Debt and "TODOs":** Codebases are filled with notes like `<!-- TODO: remove old admin endpoint /api/v1/admin-legacy before launch -->`. These serve as breadcrumbs for attackers, explicitly highlighting deprecated or vulnerable endpoints.
3. **Template Boilerplates:** Many frameworks or enterprise CMS platforms generate massive amounts of boilerplate code, which includes verbose comments detailing the framework version, underlying file structure, or server architecture.
4. **Disabled Features:** Instead of branching or properly using feature flags, developers sometimes simply use HTML comments `<!-- -->` to hide a feature (like a new admin dashboard button) from the UI. However, the functionality might still exist on the backend, and the client-side code still reveals the API paths.
5. **Team Communication:** Notes between developers complaining about a specific hacky fix or acknowledging a known security issue (e.g., `<!-- Note to Sarah: The auth check here is broken but management wants it pushed today. Fix later. -->`).

### The Mechanics of the Bleed-Through
In an ideal CI/CD pipeline, build tools (like Webpack, Vite, or Gulp) minify code and strip comments before the artifacts are pushed to the production server. However, failures occur when:
*   The build step is bypassed (e.g., hotfixes applied directly via FTP/SSH).
*   The build configuration explicitly preserves certain comments (e.g., license preservation `/*! ... */` that accidentally catches sensitive block comments).
*   The application renders Server-Side components (like PHP, JSP, or ASP.NET) dynamically, injecting comments directly into the HTTP response stream where static minifiers cannot reach them.

## 3. Architecture of the Vulnerability

The following ASCII diagram illustrates how sensitive information bypasses intended security boundaries simply by being encapsulated in a comment structure.

```text
+---------------------+                            +-------------------------+
|  Dev Environment    |                            |   Production Server     |
|                     |                            |                         |
|  // TODO: remove    |   [CI/CD PIPELINE]         |  <html>                 |
|  // password:       |   (Misconfigured / No   -------> <!-- TODO: admin    |
|  // admin/12345     |    Minification step)      |       password:         |
|                     |                            |       admin/12345 -->   |
|  <div>Hello</div>   |                            |  <div>Hello</div>       |
+----------+----------+                            +-----------+-------------+
           |                                                   |
           |                                                   |
           | (Source Control)                                  | (HTTP GET)
           v                                                   v
+---------------------+                            +-------------------------+
|    Git Repository   |                            |      Attacker /         |
|                     |                            |      Pen-Tester         |
| Contains full       |                            |                         |
| history & comments  |                            | Uses:                   |
+---------------------+                            | 1. View Source          |
                                                   | 2. Burp Suite           |
                                                   | 3. cURL / Regex         |
                                                   +-------------------------+
```

## 4. Types of Sensitive Data Exposed

When conducting a penetration test, you are not merely looking for the existence of comments; you are looking for *actionable intelligence*. Key things to look for include:

*   **Credentials and Secrets:** Hardcoded passwords, API keys (e.g., AWS, Google Maps with extended permissions), internal tokens, or test account details.
*   **Internal IP Addresses and Hostnames:** References to `10.x.x.x` or `192.168.x.x` subnets, internal DNS names (e.g., `db-prod-01.internal.local`), which are invaluable for Server-Side Request Forgery (SSRF) exploitation.
*   **Hidden or Deprecated Endpoints:** References to endpoints like `/v1/debug`, `/admin_portal_test`, or `/api/graphql/explorer`.
*   **Business Logic Clues:** Comments explaining *how* a specific validation mechanism works, giving the attacker exactly what they need to bypass it (e.g., `<!-- Validates if user_id == 1 for admin -->`).
*   **Framework and Version Disclosures:** Detailed stack information that allows attackers to search for specific CVEs.
*   **Database Structure:** Sometimes developers leave commented-out SQL queries or table names that help an attacker craft successful SQL Injection payloads.

## 5. CSS Comments and Information Disclosure

It's a common misconception to only look for HTML and JS comments. CSS files are equally prone to leakage. 

Developers often use comments in CSS to:
1.  Temporarily hide certain UI elements without removing the code (`/* display: none; */`).
2.  Leave notes about internal branding guidelines.
3.  Store hidden image paths, some of which might be hosted on internal or undocumented infrastructure.

Example CSS leak:
```css
/* Note: the background image for the internal admin panel is located at
   https://internal-assets.target.local/img/admin-bg.png 
   Ensure this is only loaded on VPN.
*/
.admin-bg {
    /* background-image: url('...'); */
}
```
This instantly alerts the tester to an internal subdomain that they can target for SSRF or subdomain enumeration.

## 6. Discovery Methodology

### 6.1 Manual Inspection
The most straightforward approach is to right-click and "View Page Source" (Ctrl+U / Cmd+U) on the target webpage. However, modern applications are complex. You must also inspect:
*   Linked `.js` (JavaScript) files.
*   Linked `.css` (Cascading Style Sheets) files.
*   `.map` (Source Map) files, which often contain the *entire* unminified original source code, including all comments.
*   Dynamically loaded HTML templates fetched via XHR/Fetch API.

### 6.2 Automated Discovery with Burp Suite
Burp Suite Professional includes passive scanning capabilities that automatically flag sensitive comments.
*   **Engagement Tools -> Find Comments:** This tool allows you to extract all comments from a selected branch of the site map. You can export these to a text file for further grepping.
*   **Target Scope:** Ensure you have fully spidered the application and triggered various states (authenticated, unauthenticated, error states) to capture dynamically generated comments.

### 6.3 Command-Line Automation and Regex
For large scopes, downloading the site and using `grep` or `ripgrep` is highly efficient.

1.  **Mirror the site:**
    ```bash
    wget --recursive --no-clobber --page-requisites --html-extension --convert-links --domains target.com https://target.com/
    ```

2.  **Search for HTML Comments:**
    ```bash
    grep -Rni "<!--" ./target.com/
    ```

3.  **Search for specific keywords within comments:**
    ```bash
    grep -RniE "(password|pwd|admin|test|dev|TODO|FIXME|hack|API_KEY|token|secret|bug)" ./target.com/
    ```

4.  **Extracting JS Comments (Single line `//` and Multi-line `/* */`):**
    Finding JS comments is noisier. You can use regex to isolate them, though tools like `TruffleHog` or `gf` (Grep For) by Tomnomnom are better suited for finding secrets within those comments.

    ```bash
    # Basic search for TODOs in JS files
    find . -name "*.js" -exec grep -Hn "TODO" {} \;
    ```

### 6.4 Nuclei Templates for Comment Disclosure
Nuclei is an incredibly powerful tool for automating the detection of known comment disclosure patterns. You can write custom templates or use community templates that specifically search for developer breadcrumbs.

Example of a simple custom Nuclei template for finding hardcoded AWS keys in comments:
```yaml
id: aws-key-in-comments
info:
  name: AWS Access Key in Comments
  author: VAPT-Tester
  severity: high
requests:
  - method: GET
    path:
      - "{{BaseURL}}"
    matchers:
      - type: regex
        regex:
          - '<!--.*?AKIA[0-9A-Z]{16}.*?-->'
```

## 7. Exploitation and Impact Analysis

Comment disclosure is rarely a critical vulnerability in isolation (unless it leaks a live, high-privileged credential). It is predominantly a **reconnaissance and enumeration** stepping stone.

### Scenario 1: The Hidden Feature Flag
1.  An attacker inspects the source code of a standard user dashboard.
2.  They discover the following HTML comment:
    ```html
    <!-- 
      Disabled until Phase 2 rollout
      <li class="nav-item">
        <a class="nav-link" href="/admin/impersonate?user_id=">Impersonate User</a>
      </li>
    -->
    ```
3.  The attacker manually navigates to `https://target.com/admin/impersonate?user_id=123`.
4.  Because the developer only hid the UI element but failed to implement proper Server-Side Access Control (Authorization), the attacker successfully impersonates another user.

**Impact:** What started as an Information Disclosure (Low severity) escalated directly to Broken Object Level Authorization / Privilege Escalation (High/Critical severity).

### Scenario 2: Legacy Endpoints
1.  A tester is examining minified JavaScript. They notice a block comment that survived the minifier because it used `/*! ... */`.
2.  The comment reads: `/*! API v1 fallback: https://v1-legacy.api.target.com - DO NOT USE AFTER DEPRECATION */`.
3.  The tester switches their focus to the `v1-legacy` subdomain, which is likely running outdated code, unpatched against known CVEs.

## 8. Analyzing Code Snippets (Vulnerable vs Not Vulnerable)

### Vulnerable Example (PHP generating HTML)
```php
<?php
  // Database connection setup
  $db_host = '10.0.0.45'; // Internal DB Server
?>
<html>
<body>
  <h1>Welcome to the portal</h1>
  <!-- Debug info: Connected to <?php echo $db_host; ?> -->
</body>
</html>
```
*Why it's bad:* The server-side script dynamically injects an internal IP into an HTML comment, exposing internal network topology to the public internet.

### Secure Example (Proper Logging instead of HTML comments)
```php
<?php
  $db_host = '10.0.0.45';
  error_log("Debug info: Connected to " . $db_host); // Written to server logs, not the client
?>
<html>
<body>
  <h1>Welcome to the portal</h1>
</body>
</html>
```

## 9. Source Maps (The Ultimate Disclosure)
A modern variant of comment disclosure is the exposure of Source Maps (`.js.map`). When developers use TypeScript, React, or Vue, the code is transpiled and minified. Source maps act as a Rosetta Stone, allowing browsers to map the minified code back to the original source for debugging.

If a file like `app.min.js.map` is accessible in production, an attacker can reconstruct the *entire original codebase*, complete with all developer comments, internal variable names, and untranspiled logic. This completely bypasses any obfuscation or minification efforts.

Browsers usually append a comment at the bottom of minified files pointing to the map:
`//# sourceMappingURL=app.bundle.js.map`

An attacker simply navigates to that URL, downloads the JSON object, and uses tools like `sourcemapper` to unpack the entire frontend directory structure.

## 10. Conclusion

Comment disclosure highlights a fundamental breakdown in operational security and release management. While often dismissed by bug bounty triagers as "Informational," experienced VAPT professionals know that a single careless comment can be the thread that unravels an entire application's security posture.

## 11. Extended Case Study: The Forgotten Staging Branch

In a notable 2021 bug bounty report on a major e-commerce platform, a researcher discovered that while the main `www.` application was meticulously stripped of comments, a forgotten `beta.` staging environment was not. 
The researcher examined the HTML source of the login page on the beta environment and found:
```html
<!-- 
  [DEV-9921] - Bypass OTP for integration tests.
  If email == "qa-auto@internal.ecommerce.com", 
  use OTP: 000000 
-->
```
The researcher then went back to the production environment (`www.`), attempted to log in as `qa-auto@internal.ecommerce.com`, and entered `000000` as the OTP. The login succeeded, granting access to an administrative testing account that still had live privileges. This demonstrates how comment disclosure in one environment (staging) can directly compromise another (production) due to shared backend databases or legacy code paths.

## 12. Defensive Remediation Deep Dive
To truly eradicate this issue, developers must adopt a zero-trust approach to client-side code:
1. **Automated Enforcement:** Use ESLint rules (e.g., `eslint-plugin-no-secrets`) to prevent developers from committing sensitive data into the codebase in the first place, regardless of whether it's in a comment.
2. **Review Processes:** Enforce strict Pull Request reviews where HTML templates are checked for disabled UI elements that should be completely removed instead of commented out.
3. **Environment Separation:** Ensure that debugging features and verbose logging are explicitly bound to the `development` environment variables and physically cannot be compiled into production builds.

## Chaining Opportunities
*   **[[11 - API Response Over-Exposure]]**: Comments might reveal undocumented parameters that can be supplied to an API to trigger over-exposure.
*   **[[01 - Insecure Direct Object References (IDOR)]]**: Comments often reveal the exact parameter names required to exploit IDORs (e.g., `<!-- Note: send account_id in POST body to bypass UI -->`).
*   **[[05 - Server-Side Request Forgery (SSRF)]]**: Leaked internal IP addresses or hostnames provide exact targets for SSRF attacks.
*   **[[08 - Privilege Escalation]]**: Uncovering hidden admin endpoints or test credentials.

## Related Notes
*   [[02 - Reconnaissance Techniques]]
*   [[12 - Defense]]
*   [[15 - Discovering Hidden APIs]]
