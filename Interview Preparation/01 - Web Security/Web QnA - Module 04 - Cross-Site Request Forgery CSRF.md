---
tags: [interview, web-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Web Security"
topic: "QnA - Web Module 04"
---

# Web Security Interview Preparation: Module 04 - Cross-Site Request Forgery (CSRF)

Welcome to the expert-level interview preparation guide for Cross-Site Request Forgery (CSRF). In this module, you will demonstrate a deep understanding of browser cookie mechanics, session handling, state-changing requests, and modern preventative measures.

While sometimes considered a legacy vulnerability due to modern browser defenses, CSRF remains devastating when applications mishandle authentication tokens, misconfigure SameSite cookie attributes, or fail to implement robust synchronization mechanisms.

---

## Formal Technical Questions

### Q1: What is the fundamental difference in the attack mechanics between CSRF and XSS? Why does CSRF require the user to be pre-authenticated?
**Answer:**
Cross-Site Scripting (XSS) and Cross-Site Request Forgery (CSRF) are fundamentally different in execution and scope.
- **XSS:** The attacker injects malicious scripts into the target website itself. The browser executes this script in the context of the trusted domain. XSS exploits the user's trust in a specific site.
- **CSRF:** The attacker hosts malicious code on an external, attacker-controlled domain. This code forces the victim's browser to make an unintended HTTP request to the target site. CSRF exploits the web application's trust in the user's browser to automatically attach ambient credentials (like cookies).
- *Pre-authentication Requirement:* CSRF attacks cannot read the response of the forged request (due to the Same-Origin Policy). The attack is purely "blind" execution of a state-changing action (e.g., transferring funds). For the target server to process the request, the victim's browser must automatically attach a valid session cookie. If the victim is not actively logged in, the server will reject the forged request as unauthenticated.

### Q2: Explain the `SameSite` cookie attribute. Discuss the differences between `Strict`, `Lax`, and `None`, and explain how they impact CSRF vulnerabilities.
**Answer:**
The `SameSite` attribute instructs the browser on whether to append a cookie to cross-site requests. This is the primary modern defense against CSRF.
- **SameSite=Strict:** The cookie is only sent if the request originates from the same site as the target URL. If a user clicks a link from an email or a different domain, the cookie is withheld. This provides absolute CSRF protection but breaks usability (users arriving via external links appear logged out).
- **SameSite=Lax (Modern Default):** The cookie is withheld for cross-site POST requests (preventing form-based CSRF). However, the cookie *is* sent for top-level navigations (like clicking a link) that use safe HTTP methods (GET). This balances security and usability.
- **SameSite=None:** The cookie is sent with all cross-site requests, effectively disabling SameSite protection. To use `None`, the cookie must also have the `Secure` flag (HTTPS only). This is required for SSO providers or embedded third-party widgets but leaves the application vulnerable to CSRF if traditional tokens are not implemented.

### Q3: What is the Double Submit Cookie pattern? What are its inherent security flaws compared to the Synchronizer Token pattern?
**Answer:**
The Double Submit Cookie pattern requires the client to send a random, session-unique token in two places simultaneously: as a cookie, and as a hidden form parameter (or custom header). The server validates the request by verifying that the token in the cookie matches the token in the parameter.
- *Mechanism:* This avoids storing tokens on the server (stateless architecture). Because an attacker cannot read or set cookies on the target domain (Same-Origin Policy), they cannot force the two values to match in their forged request.
- *Security Flaws:* 
  1. **Subdomain Vulnerabilities:** If an attacker compromises a subdomain (e.g., `blog.target.com`), they can force a cookie onto the parent domain (`.target.com`). They can then set their *own* chosen CSRF token in the victim's cookie, and include that same token in the forged request parameter. This bypasses the protection completely (Token Fixation).
  2. **Man-in-the-Middle (MITM):** If the application does not strictly enforce HSTS, an attacker intercepting unencrypted HTTP traffic can inject the cookie, achieving the same token fixation. The Synchronizer Token pattern (storing the valid token server-side) entirely prevents these bypasses.

---

## Scenario-Based Questions

### Scenario 1: Bypassing Weak Anti-CSRF Implementations
**Prompt:** You are analyzing a web application's password change functionality. It utilizes a CSRF token. However, you suspect the implementation is flawed. Walk through the methodology you would use to systematically attempt to bypass the CSRF token validation.

**Expert Answer:**
CSRF token implementations often contain logical flaws. My methodology would involve checking the following bypass conditions:
1. **HTTP Method Downgrade:** The server might validate the token for POST requests but fail to check it for GET requests. I would intercept the POST request, change the method to GET, append the parameters to the URL, and drop the token. If it executes, CSRF is possible via a simple `<img>` tag.
2. **Token Omission:** I would completely remove the CSRF token parameter (or the header) from the request. Some frameworks only validate the token *if* it is present, defaulting to valid if it is entirely missing.
3. **Null / Blank Token Verification:** I would submit an empty token (e.g., `csrf_token=`). Poorly written server-side logic might equate a null input with a null session value.
4. **Token Fixation / Session Independence:** I would obtain a valid CSRF token from my own attacker account, and insert it into the exploit crafted for the victim. If the server only checks if the token is mathematically valid, but fails to tie the token to the specific user's session, the attack succeeds.

### Scenario 2: Referer Header Validation Bypass
**Prompt:** A target application does not use CSRF tokens. Instead, it relies solely on checking the HTTP `Referer` header to ensure the request originated from `target.com`. How would you attempt to bypass this protection to execute a CSRF attack?

**Expert Answer:**
Relying on the `Referer` header is notoriously fragile. My attack strategy focuses on tricking the validation logic:
1. **Omission Bypass:** Browsers often omit the Referer header for privacy reasons (e.g., moving from HTTPS to HTTP). I would use the meta tag `<meta name="referrer" content="no-referrer">` on my malicious page. If the server allows requests with an absent Referer header, the bypass is successful.
2. **Regex Flaws in Validation:** If the server checks that the Referer *contains* the domain, I would register a domain like `target.com.attacker.com` or create a directory like `attacker.com/target.com/`. The server's weak validation (`if "target.com" in referer`) will pass.
3. **Open Redirect Pivot:** If I find an Open Redirect vulnerability on the target site (e.g., `target.com/redirect?url=attacker.com`), I can use it to launch the CSRF. The request flow would be: Malicious Site -> Open Redirect -> State Change Action. Because the Open Redirect is hosted on `target.com`, the final state-changing request will legitimately carry `target.com` as its Referer.

---

## Deep-Dive Defensive Questions

### D1: How does designing an application as a Single Page Application (SPA) communicating via custom HTTP headers inherently mitigate traditional CSRF attacks?
**Answer:**
Traditional CSRF attacks rely on HTML elements (`<form>`, `<img>`, `<script>`) to force the browser to issue requests automatically. These elements can only issue standard GET or POST requests and cannot append custom headers.
- *The SPA Advantage:* SPAs heavily utilize `fetch` or `XMLHttpRequest` (AJAX) to communicate with the backend. By designing the server to strictly require a custom header for state-changing operations (e.g., `X-Requested-With: XMLHttpRequest` or `Content-Type: application/json`), traditional HTML-based CSRF attacks fail. 
- *CORS Enforcement:* For an attacker's domain to issue an AJAX request with custom headers to the target domain, the browser enforces Cross-Origin Resource Sharing (CORS) preflight checks. The browser sends an `OPTIONS` request first. Unless the server explicitly whitelists the attacker's origin in the CORS policy, the browser will block the actual POST request, preventing the CSRF completely.

### D2: What is the Synchronizer Token Pattern? Detail how state synchronization is maintained securely.
**Answer:**
The Synchronizer Token Pattern is the gold standard for CSRF defense.
- *Mechanism:* When a user authenticates, the server generates a cryptographically strong, random token and stores it in the user's active session data on the backend. When rendering forms, the server injects this token into a hidden field. 
- *Validation:* Upon form submission, the application compares the token submitted in the request parameter against the token stored in the backend session. If they match, the request proceeds.
- *Security Advantage:* Because the token is stored securely on the server and injected into the HTML response, an attacker cannot guess it. Furthermore, because of the Same-Origin Policy, the attacker cannot use client-side scripts to read the token from the victim's HTML. The synchronization strictly binds the intent of the HTTP request to the established session.

---

## Real-World Attack Scenario

### CSRF to Complete Account Takeover
During a review of a financial technology application, I analyzed the "Update Email" endpoint (`/api/profile/email`). 
The application utilized strict CORS policies and `SameSite=Lax` cookies. However, the developers implemented a fallback mechanism: if the request method was changed to GET, it would accept the parameters directly from the URL to accommodate legacy mobile clients.

Furthermore, the application lacked any password confirmation prompt for email updates. 

I crafted a payload hosted on a seemingly innocuous blog post. The payload contained a hidden image tag:
`<img src="https://fintech.target.com/api/profile/email?new_email=attacker@evil.com" style="display:none;">`

When the authenticated victim loaded my blog post, their browser automatically attempted to fetch the image, issuing a GET request to the target endpoint. Because it was a top-level GET request (an image fetch), the browser attached the `SameSite=Lax` session cookie.

The server processed the GET request and updated the victim's account email to my attacker-controlled email address. Once the email was updated, I immediately navigated to the login page, requested a "Password Reset", received the reset link to my email, and achieved total account takeover. 

---

## Custom ASCII Diagram: Cross-Site Request Forgery (CSRF) Flow

```mermaid
sequenceDiagram
    participant V as Victim User
    participant B as Vulnerable Bank (bank.com)
    participant A as Attacker Server (evil.com)

    Note over V, B: 1. The Setup
    V->>B: Authenticates to Bank Site.
    B-->>V: Returns Session Cookie
    Note left of V: (Cookie stored locally)

    Note over V, A: 2. The Trap
    V->>A: Browses the Internet, visits Evil Site
    A-->>V: Returns HTML with hidden payload.

    Note over V: 3. The Execution (Invisible to User)<br/>Browser processes evil HTML:<br/><form action="https://bank.com/transfer" method="POST"><br/>  <input type="hidden" name="to" value="AttackerAcct"><br/>  <input type="hidden" name="amount" value="5000"><br/></form><br/><script>document.forms[0].submit();</script>

    V->>B: (Browser AUTO-ATTACHES bank.com Session Cookie)
    Note over B: 4. The Exploit<br/>Receives POST request with valid session cookie.<br/>Lacks CSRF Token validation.<br/>Trusts the request and executes the fund transfer.
```

---

## Chaining Opportunities
CSRF is highly effective when chained with vulnerabilities that require authenticated state execution:
1. **CSRF to Self-XSS to Full XSS:** A user profile page might have a Self-XSS vulnerability (only the user can see their own XSS payload). An attacker uses CSRF to forge a request that injects the XSS payload into the victim's profile. When the victim views their profile, the Self-XSS executes against them, granting the attacker full DOM control.
2. **CSRF to Account Takeover (ATO):** Forcing a state-changing request to update the user's recovery email or disable Multi-Factor Authentication (MFA).
3. **CSRF to SSRF:** Forcing an authenticated administrator to submit a form containing an internal URL, leveraging the admin's privileges to trigger a Server-Side Request Forgery against the internal network.

---

## Related Notes
- [[02 - Cross-Site Scripting XSS]]
- [[08 - CORS and Cross-Origin Protections]]
- [[13 - HTML5 Security Features]]
- [[22 - Session Fixation and Management]]

