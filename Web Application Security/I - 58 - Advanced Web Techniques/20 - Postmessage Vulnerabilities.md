---
tags: [web-exploitation, advanced, vapt]
difficulty: advanced
module: "58 - Advanced Web Techniques"
topic: "58.20 Postmessage Vulnerabilities"
---

# PostMessage Vulnerabilities

## Introduction to PostMessage

The `window.postMessage` API was introduced in HTML5 to allow safe, controlled communication between different browser contexts, such as a parent window and an iframe, or between two different tabs. 

Historically, the **Same-Origin Policy (SOP)** strictly prohibited scripts from one origin (e.g., `https://attacker.com`) from reading or modifying the DOM of a different origin (e.g., `https://bank.com`). While SOP is critical for web security, developers often have legitimate reasons to pass data across domains—for example, embedding a third-party payment gateway iframe or a cross-domain SSO widget.

`postMessage` solves this by providing a secure messaging channel. However, the security of this channel relies entirely on the developer implementing strict validation checks on the receiving end. If an application listens for incoming messages but fails to properly verify *who* sent the message, or mishandles the data *inside* the message, it creates severe vulnerabilities, primarily resulting in DOM-based Cross-Site Scripting (DOM XSS), data exfiltration, or PostMessage CSRF.

## Core Mechanics of postMessage

A `postMessage` implementation requires two components: the Sender and the Receiver.

### The Sender
The sender calls the `postMessage` method on a reference to the target window (e.g., an iframe or a popup).
```javascript
// windowRef is a reference to the target iframe
windowRef.postMessage('{"action":"login", "user":"admin"}', 'https://target-domain.com');
```
The second argument is the `targetOrigin`. This is a security feature on the sender's side. If the target window has navigated away to a different domain, the browser will block the message from being sent, preventing accidental leakage of sensitive data. **Using `*` as the targetOrigin is dangerous** if the data is sensitive.

### The Receiver
The receiver sets up an event listener to catch incoming messages.
```javascript
window.addEventListener("message", function(event) {
    // Process the event.data
});
```
The `event` object contains three crucial properties:
1. `event.data`: The actual payload sent by the sender.
2. `event.origin`: The origin of the sender (e.g., `https://sender.com`).
3. `event.source`: A reference to the sender's window object.

## ASCII Architecture Diagram: PostMessage Flow

```text
+-------------------------------------------------------------+
|                     ATTACKER WEBSITE                        |
|                     https://evil.com                        |
|                                                             |
|  <iframe id="target" src="https://bank.com/widget"></iframe>|
|                                                             |
|  <script>                                                   |
|    let iframe = document.getElementById("target").contentWindow;
|    // Send malicious payload to the vulnerable iframe       |
|    iframe.postMessage("javascript:alert(1)", "*");          |
|  </script>                                                  |
+-------------------------------------------------------------+
                              |
                     Message Dispatched
                     event.origin = "https://evil.com"
                     event.data   = "javascript:alert(1)"
                              |
                              V
+-------------------------------------------------------------+
|                     VICTIM APPLICATION                      |
|                     https://bank.com/widget                 |
|                                                             |
|  window.addEventListener("message", (e) => {                |
|      // VULNERABILITY: Missing origin check!                |
|      // The app assumes messages only come from itself      |
|      window.location.href = e.data;                         |
|  });                                                        |
+-------------------------------------------------------------+
                              |
                              V
                       DOM XSS TRIGGERED
                  (Browser executes alert(1))
```

## Vulnerability 1: Missing Origin Verification

The most common and devastating flaw is when the receiver completely fails to check `event.origin`. 

Because `window.addEventListener("message", ...)` listens globally, *any* website that embeds the vulnerable application in an iframe (or opens it in a popup) can send it a message. If the application takes the `event.data` and passes it into a dangerous sink (like `eval()`, `innerHTML`, or `window.location`), an attacker achieves instant DOM XSS.

**Vulnerable Code:**
```javascript
window.addEventListener("message", function(event) {
    let message = JSON.parse(event.data);
    if (message.action === "updateDOM") {
        document.getElementById("output").innerHTML = message.html; // DOM XSS
    }
});
```

## Vulnerability 2: Insecure Origin Verification (Regex Bypasses)

Developers often implement origin checks, but do so incorrectly. A classic mistake is using flawed string matching or poorly constructed regular expressions to validate the origin.

**Flawed Example 1: `indexOf()`**
```javascript
window.addEventListener("message", function(event) {
    // Developer intended to allow https://trusted.com
    if (event.origin.indexOf("trusted.com") !== -1) {
        // ... dangerous sink ...
    }
});
```
**Bypass:** An attacker simply registers `https://attacker-trusted.com` or `https://trusted.com.evil.com`. The `indexOf` check will return true, bypassing the restriction.

**Flawed Example 2: Unescaped Dot in Regex**
```javascript
window.addEventListener("message", function(event) {
    if (event.origin.match(/^https:\/\/www.trusted.com$/)) {
        // ... dangerous sink ...
    }
});
```
**Bypass:** In regex, an unescaped dot (`.`) matches *any* character. An attacker can register `https://wwwatrusted.com`.

**Flawed Example 3: Missing Anchors in Regex**
```javascript
window.addEventListener("message", function(event) {
    if (event.origin.match(/https:\/\/(.*\.)?trusted\.com/)) {
        // ... dangerous sink ...
    }
});
```
**Bypass:** Because there is no end anchor (`$`), the attacker can host the exploit on `https://trusted.com.evil.com`.

## Vulnerability 3: Insecure Data Handling

Even if the origin check is perfectly implemented, vulnerabilities can still arise if the data handling logic is flawed. Sometimes, attackers can bypass origin checks by finding an XSS vulnerability on a trusted subdomain. 

For instance, if `https://app.example.com` securely checks that a message came from `https://marketing.example.com`, but the marketing subdomain has a stored XSS vulnerability, the attacker can use the marketing site to send the malicious `postMessage` to the main application, chaining the vulnerabilities.

Furthermore, if the application uses `eval(event.data)`, it executes arbitrary code. If it uses `document.location = event.data.url`, it can lead to Open Redirects or JavaScript execution via `javascript:` URIs.

## Vulnerability 4: Information Leakage

If the sender window uses a wild-card target origin (`*`) when dispatching sensitive data, any malicious iframe that intercepts the message can read the data.

```javascript
// Vulnerable Sender
window.parent.postMessage({"token": "session_12345"}, "*");
```
If the parent window is controlled by an attacker (e.g., the victim was phished into visiting the attacker's site, which frames the vulnerable application), the attacker's site can simply listen for the message and steal the session token.

## Methodology for Finding PostMessage Vulnerabilities

During a VAPT engagement, identifying these flaws requires dynamic analysis and code review.

1. **Browser DevTools:** Open Chrome DevTools, go to the "Sources" tab, and look at the "Global Listeners" pane. Expand the "message" event to see all scripts listening for `postMessage` events.
2. **Static Analysis:** Search the minified JavaScript files for keywords like `addEventListener('message'`, `addEventListener("message"`, or `.onmessage`.
3. **Tracing Sinks:** Once a listener is found, trace the flow of `event.data`. Does it reach a dangerous sink like `innerHTML`, `jQuery()`, `eval()`, `setTimeout()`, or `location.href`?
4. **Analyzing the Filter:** Trace `event.origin`. Is there a check? Can it be bypassed using regex manipulation or `indexOf` tricks?

## Detailed Remediation Strategies

Securing postMessage requires a defense-in-depth approach covering both the sender and receiver.

1. **Strict Origin Checks (Receiver):**
   Always verify the `event.origin` using exact string equality. Do not use regex or `indexOf` unless absolutely necessary, and if used, ensure it is thoroughly tested for bypasses.
   ```javascript
   window.addEventListener("message", function(event) {
       if (event.origin !== "https://trusted-partner.com") {
           return; // Drop the message entirely
       }
       // Safe to process data
   });
   ```

2. **Explicit Target Origins (Sender):**
   Never use `*` as the `targetOrigin` when sending sensitive data. Always specify the exact domain you expect the receiver to be hosted on.
   ```javascript
   window.parent.postMessage(secretData, "https://secure-dashboard.com");
   ```

3. **Schema Validation:**
   Even from a trusted origin, treat `event.data` as untrusted input. Validate the structure and type of the incoming message. If expecting JSON, parse it safely and ensure all expected keys are present and contain safe types (e.g., strings, not executable objects).

4. **Use Safe Sinks:**
   Avoid passing `event.data` directly into sinks that can evaluate code. Use `innerText` or `textContent` instead of `innerHTML`.

## Chaining Opportunities

- **[[03 - Cross-Site Scripting (XSS)]]**: PostMessage is one of the most common vectors for achieving DOM-based XSS in modern Single Page Applications (SPAs).
- **[[04 - Cross-Site Request Forgery (CSRF)]]**: If an application uses a postMessage to perform a state-changing action (like updating an email address) without origin checks, it functions identically to CSRF.
- **[[15 - Open Redirects]]**: Passing unsanitized `event.data.url` to `window.location`.

## Related Notes

- [[02 - Input Validation and Sanitization]]
- [[26 - DOM Clobbering]]
- [[12 - HTTP Protocol Fundamentals]]

---
*End of Document*
