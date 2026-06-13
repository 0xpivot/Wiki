---
tags: [interview, web-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Web Security"
topic: "QnA - Web Module 21"
---

# Web QnA - Module 21 - Open Redirects and Clickjacking

```text
    [ Victim User ]
           |
           | (1) Clicks malicious link
           v
  +------------------+
  | Attacker Site    |  <=== (2) Hidden iframe loads Target Site
  | (Clickjacking)   |
  |                  |
  |  [Play Video]    |  <=== (3) User thinks they are clicking "Play Video"
  |   (Invisible)    |  <===     But actually clicking "Delete Account"
  |  [Delete Acct]   |           on Target Site iframe
  +------------------+
           |
           | (4) Or clicks Open Redirect
           v
  [ Target Site ] ?redirect=https://attacker.com
           |
           | (5) Bypasses filter via \/attacker.com or //attacker.com
           v
  [ Attacker Site ] (Phishing / Token Exfiltration)
```

## Formal Technical Questions

**Q1: Explain the fundamental difference between DOM-based Open Redirects and Server-Side Open Redirects. How do the mitigation strategies differ?**
**Answer:**
A server-side open redirect occurs when the backend server processes an HTTP request containing user-controlled input and uses it in a `Location` header to redirect the user (e.g., `HTTP/1.1 302 Found\nLocation: [USER_INPUT]`). The vulnerability resides purely in the server's routing or redirection logic. 
DOM-based open redirect, on the other hand, happens entirely on the client side. The vulnerability is in the JavaScript code executing in the user's browser, taking input from sources like `location.hash`, `location.search`, or `window.name` and passing it to sinks like `window.location`, `window.location.replace()`, or `window.open()`.
*Mitigation differences:* For server-side, you must validate input on the backend against an exact allowlist of absolute URLs or relative paths. For DOM-based, mitigation involves secure coding practices in frontend JavaScript—avoiding unsafe sinks or heavily sanitizing the sink inputs using DOMPurify or strict regex validations before assigning them to `window.location`.

**Q2: Clickjacking (UI Redressing) is typically mitigated using `X-Frame-Options` or `Content-Security-Policy: frame-ancestors`. Describe a scenario where `frame-ancestors` is implemented, but a Clickjacking vulnerability still exists.**
**Answer:**
If a web application implements `CSP: frame-ancestors 'self' trusted.com`, it restricts embedding to the same origin and `trusted.com`. However, a clickjacking vulnerability can still exist in several scenarios:
1. **XSS on `trusted.com`:** If `trusted.com` has an XSS vulnerability or allows users to upload custom HTML, an attacker can host the malicious framing code on `trusted.com`, bypassing the CSP.
2. **Open Redirect on `trusted.com` combined with framing:** If the trusted site is vulnerable, the attacker might chain it.
3. **Subdomain Takeover:** If `trusted.com` or a subdomain is hijacked, the attacker can host the clickjacking payload there.
4. **Framing a vulnerable page within the same application:** If the application has a page that allows user-controlled HTML or reflects input without framing protections, it could frame another sensitive page of the same application.
5. **Drag-and-Drop Clickjacking (Cross-Origin Data Leakage):** Instead of tricking a click, the attacker frames the target page and tricks the user into dragging sensitive text (like a CSRF token or PI) from the iframe into an attacker-controlled text box.

**Q3: How can Open Redirects be utilized to bypass SSRF protections?**
**Answer:**
When an application has SSRF protections, it typically resolves the target URL to an IP address, checks if the IP belongs to an internal range (like `10.0.0.0/8`), and blocks the request if it is internal. However, if the attacker points the SSRF payload to an external server they control, or a trusted external server that contains an Open Redirect, the SSRF protection mechanism might validate the initial URL as "safe" (external IP). Once the initial HTTP request is made, the external server responds with a `302 Found` pointing to an internal IP (e.g., `Location: http://169.254.169.254/latest/meta-data/`). If the backend HTTP client automatically follows redirects without reapplying the SSRF filter to the new `Location` target, the application will successfully fetch the internal resource, bypassing the SSRF defense.

## Scenario-Based Questions

**Q4: You are on a Red Team engagement. You find an open redirect on the primary authentication portal: `https://auth.target.com/login?next=https://app.target.com`. The redirect validation uses a regex that checks if the `next` parameter ends with `.target.com`. How do you bypass this?**
**Answer:**
If the validation merely checks if the string *ends with* `.target.com`, there are several bypass techniques:
1. **Parameter pollution / Fragment injection:** `https://attacker.com#www.target.com` or `https://attacker.com?.target.com`. The backend sees it ends with `.target.com`, but the browser resolves the host as `attacker.com`.
2. **Subdomain creation:** I can register `attacker-target.com` or create a subdomain `app.target.com.attacker.com`. The string ends with `.target.com` (or `target.com`), satisfying the regex, but directs the user to my server.
3. **Authentication bypass via `@`:** `https://attacker.com@app.target.com`. Wait, the browser treats everything before `@` as credentials and `app.target.com` as the host. If the validation just looks for `.target.com`, an attacker URL like `https://app.target.com@attacker.com/folder.target.com` could work depending on how the parser works. But for "ends with", I would use `https://attacker.com/redirect?.target.com` because the browser will navigate to `attacker.com`.

**Q5: During a penetration test, you discover a page that cannot be framed due to `X-Frame-Options: DENY`. However, the client wants to know if there's any way an attacker could still exploit UI redressing or overlay tactics on this specific page. What alternative techniques would you investigate?**
**Answer:**
If iframe-based Clickjacking is blocked, I would look for:
1. **Tabnabbing (Reverse Tabnabbing):** If the target page contains links with `target="_blank"` and lacks `rel="noopener noreferrer"`, an attacker site could be opened. The attacker site can then manipulate the `window.opener.location` to redirect the original target page to a phishing page that perfectly mimics it, capturing credentials when the user switches back to the tab.
2. **Window Injection / DOM Clobbering:** If the page relies on `window.name` for sensitive operations, an attacker can open the page using `window.open('https://target.com', 'malicious_payload')` to inject data.
3. **Cursor Spoofing or CSS Overlays (if XSS is present):** If I have even minor HTML/CSS injection, I can draw elements over the UI. 
4. **Pop-under / Pop-up UI Redressing:** Opening the target site in a small pop-up right under the user's cursor, hoping for an accidental click, although modern browsers heavily restrict this.

## Deep-Dive Defensive Questions

**Q6: You are architecting the OAuth 2.0 flow for a microservices environment. How do you design the `redirect_uri` validation to completely eliminate Open Redirect vulnerabilities that could lead to authorization code leakage?**
**Answer:**
1. **Exact Match Allowlisting:** Never use regex, wildcards, or "starts with/ends with" logic for `redirect_uri` validation. Implement strict, exact string matching. The registered `redirect_uri` in the database must match the requested `redirect_uri` byte-for-byte.
2. **State Parameter Binding:** Bind the `state` parameter to the user's session and ensure it is cryptographically secure and unguessable. This prevents CSRF on the authorization response but also makes exploiting an open redirect harder since the attacker cannot force the flow easily.
3. **PKCE (Proof Key for Code Exchange):** Mandate PKCE for all clients (confidential and public). Even if an attacker steals the authorization code via an open redirect, they cannot exchange it for an access token without the `code_verifier`, which is stored in the victim's local browser memory and never transmitted during the redirect.
4. **Token Binding/DPoP:** Implement Demonstrating Proof-of-Possession (DPoP) at the application layer so that tokens are bound to the client's private key.
5. **No Dynamic Redirects:** Ensure the application does not take user-supplied `redirect_uri` parameters that aren't pre-registered.

**Q7: Explain the defense-in-depth approach to preventing Clickjacking for a highly sensitive financial application. Why is `X-Frame-Options` alone insufficient?**
**Answer:**
`X-Frame-Options` is deprecated in modern architectures, though still used for legacy support. It has limited granularity (only `DENY` or `SAMEORIGIN`) and doesn't allow specific third-party framing easily.
A defense-in-depth approach requires:
1. **Content-Security-Policy (CSP):** `Content-Security-Policy: frame-ancestors 'self'`. This is the modern standard, enforced by all current browsers. It is highly granular.
2. **SameSite Cookies:** Set session cookies to `SameSite=Lax` or `SameSite=Strict`. If a page is framed by an attacker, the browser treats it as a cross-site context. With `SameSite=Lax/Strict`, the browser will not send the session cookie in the iframe (unless it's a top-level navigation). This means the framed page will be unauthenticated, rendering the clickjacking attack useless since the sensitive actions cannot be performed.
3. **Frame-Busting JavaScript (Legacy/Fallback):** As a final fallback for extremely old browsers, include frame-busting scripts: `if (top !== self) top.location.replace(self.location.href);`. (Note: This can sometimes be bypassed using HTML5 `sandbox` attributes on the iframe, which is why headers are mandatory).
4. **Re-authentication/Sudo Mode:** Require the user to re-enter their password, perform MFA, or solve a CAPTCHA for sensitive actions (e.g., transferring funds). Clickjacking cannot easily automate password entry.

## Defensive Coding Examples

**Insecure Implementation (Node.js/Express Open Redirect):**
```javascript
app.get('/login', (req, res) => {
    // VULNERABLE: Takes user input directly and passes to Location header
    const returnUrl = req.query.return_url;
    // ... authentication logic ...
    res.redirect(returnUrl); 
});
```

**Secure Implementation (Node.js/Express):**
```javascript
app.get('/login', (req, res) => {
    const returnUrl = req.query.return_url;
    
    // SAFE: Strict allowlist validation
    const allowedUrls = [
        'https://app.target.com/dashboard',
        'https://app.target.com/profile'
    ];
    
    // ... authentication logic ...
    
    if (allowedUrls.includes(returnUrl)) {
        res.redirect(returnUrl);
    } else {
        // Fallback to default safe URL
        res.redirect('https://app.target.com/dashboard');
    }
});
```

**Secure Clickjacking Defense (Nginx Configuration):**
```nginx
# Add proper security headers to prevent framing
server {
    listen 443 ssl;
    server_name myapp.internal;

    # Modern defense
    add_header Content-Security-Policy "frame-ancestors 'self' https://trusted-partner.com;" always;
    
    # Legacy fallback
    add_header X-Frame-Options "SAMEORIGIN" always;
}
```

## Bonus Practical Exercises

1. **Set up a local testing lab for Open Redirects:**
   - Write a simple Flask or Express application with a vulnerable `/redirect?url=` endpoint.
   - Test various payload bypasses: `//attacker.com`, `\/\/attacker.com`, `https:attacker.com`.
   - Implement regex filters and attempt to bypass them using techniques like `@` and fragment identifiers.
2. **Set up a Clickjacking Demo:**
   - Create an HTML file containing a vulnerable target application with a "Delete Account" button.
   - Create an attacker HTML file containing an `iframe` that loads the vulnerable application.
   - Use CSS (`opacity: 0.0001; position: absolute; z-index: 999;`) to overlay the invisible "Delete Account" button on top of a decoy "Win a Prize" button.
   - Validate that clicking the decoy triggers the actual action.

## Tooling & Automation

- **Burp Suite Professional:** Use the Active Scanner to automatically identify Open Redirects. Use the DOM Invader extension to find DOM-based Open Redirect sinks.
- **Nuclei:** Utilize the `open-redirect` template tags to scan massive attack surfaces for common bypasses.
- **Custom Scripts:** Write Python scripts using `requests` to test endpoints and check if the `response.url` matches your external domain, indicating a successful redirect.

## Real-World Attack Scenario

**Scenario:** The target application is an SSO provider using SAML and OAuth.
1. The attacker discovers an Open Redirect in the logout flow: `https://sso.target.com/logout?return_url=https://attacker.com`.
2. The attacker crafts a payload targeting an OAuth client application that relies on the SSO provider. The client app uses `response_type=token` (Implicit Flow) for a legacy Single Page Application (SPA).
3. The attacker sends a link to the victim: `https://sso.target.com/authorize?client_id=123&response_type=token&redirect_uri=https://app.target.com/callback&state=payload`.
4. However, the attacker notices that the SPA's callback page (`https://app.target.com/callback`) has a DOM-based open redirect. It reads the `state` parameter and redirects the user if an error occurs.
5. The attacker modifies the authorization request so that it triggers an error on the callback page, setting the `state` parameter to the SSO logout Open Redirect.
6. The flow executes: The user authorizes -> SSO redirects to `app.target.com/callback#access_token=USER_TOKEN&state=https://sso.target.com/logout?return_url=https://attacker.com`.
7. The SPA JavaScript parses the URL, hits the error condition, and uses `window.location = state_value`.
8. The browser navigates to `https://sso.target.com/logout?return_url=https://attacker.com#access_token=USER_TOKEN`. (Browsers preserve URL fragments across redirects).
9. The SSO logs the user out and performs the server-side Open Redirect to `https://attacker.com#access_token=USER_TOKEN`.
10. The attacker successfully steals the OAuth access token from the URL fragment on their server.

## Chaining Opportunities

- **Open Redirect -> OAuth Token Theft:** As demonstrated in the scenario above, an open redirect can be used to steal authorization codes or implicit access tokens.
- **Open Redirect -> SSRF Bypass:** Using an open redirect on an external trusted domain to bounce a server-side request into an internal network (`169.254.169.254`).
- **Open Redirect -> XSS (JavaScript Pseudo-protocol):** If the redirect sink accepts `javascript:` URIs (e.g., `Location: javascript:alert(1)` doesn't work server-side, but DOM-based `window.location = 'javascript:...'` leads to XSS).
- **Clickjacking -> CSRF:** When standard CSRF tokens are in place, Clickjacking can be used to trick the user into manually submitting the form, thereby bypassing anti-CSRF tokens because the request originates from the legitimate UI.
- **Clickjacking -> Self-XSS to Stored XSS:** Tricking a user into copying and pasting a malicious payload into a form field (Drag-and-Drop Clickjacking), turning a non-exploitable Self-XSS into an exploitable attack.

## Related Notes

- [[02 - Cross-Site Scripting (XSS)]]
- [[04 - Server-Side Request Forgery (SSRF)]]
- [[12 - OAuth 2.0 and OIDC Vulnerabilities]]
- [[15 - SameSite Cookies and CORS]]
