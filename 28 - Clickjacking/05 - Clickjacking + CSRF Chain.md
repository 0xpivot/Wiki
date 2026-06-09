---
tags: [vapt, clickjacking, csrf, advanced]
difficulty: advanced
module: "28 - Clickjacking"
topic: "28.05 Clickjacking + CSRF Chain"
---

# 28.05 — Clickjacking + CSRF Chain

## What is it?
**Clickjacking** and **Cross-Site Request Forgery (CSRF)** are both client-side attacks that trick a victim into performing an unwanted action. However, they are often used to cover each other's weaknesses.

A **Clickjacking + CSRF Chain** occurs when a standard CSRF attack is blocked by an anti-CSRF token, but the application allows framing. Because the attacker cannot guess the CSRF token to forge a POST request in the background, they use Clickjacking to force the victim to manually click the legitimate button on the target page. Since the victim is clicking the real page (loaded in the iframe), the real anti-CSRF token is automatically included in the request!

Conversely, sometimes Clickjacking is used to bypass CORS restrictions or SameSite cookie limitations by forcing a state change that makes a subsequent CSRF attack possible.

Think of it like trying to wire money from someone's bank account. If the bank requires a unique, one-time passcode (CSRF Token) that you don't know, you can't just forge a forged transfer slip (Standard CSRF). Instead, you physically guide the victim's hand to push the "Approve Transfer" button on their own authenticated device (Clickjacking). The device automatically supplies the valid passcode.

## ASCII Diagram
```text
================================================================================
                    CHAINING CLICKJACKING TO BYPASS CSRF
================================================================================

[The Problem: Standard CSRF Fails]
Attacker sends a forged POST request to /update_email.
Target Server: "Where is the CSRF token?" -> HTTP 403 Forbidden.

[The Solution: The Clickjacking Chain]

1. Attacker creates `evil.html`.
2. Attacker loads the REAL `/update_email` form inside an invisible iframe.
   Because it is the real page, it contains the valid CSRF token in a hidden field.

+-------------------------------------------------+
| [Attacker's Page]                               |
|                                                 |
|  Take the IQ Test!                              |
|                                                 |
|  Type your name: [__________________]           | <-- Decoy Input
|                                                 |
|             [ SUBMIT TEST ]                     | <-- Decoy Button
+-------------------------------------------------+

[Inside the Invisible iframe directly underneath]
<form action="/update_email" method="POST">
    <input type="hidden" name="csrf_token" value="VALID_TOKEN_7734">
    <input type="text" name="email" value="hacker@evil.com">
    <button type="submit">Update</button>
</form>

[Result]
When the victim clicks "SUBMIT TEST", they actually click the hidden "Update" button.
The browser sends the POST request, including the valid `csrf_token`.
The server accepts it! CSRF protection is completely bypassed!
================================================================================
```

## How to Find It
- **Manual steps:**
  1. Find a sensitive state-changing action (like changing an email or password).
  2. Verify that it is protected against standard CSRF (e.g., it uses a random anti-CSRF token).
  3. Check the HTTP response headers of the form page. If `X-Frame-Options` or `Content-Security-Policy: frame-ancestors` is missing, you have a chainable vulnerability.
  4. **The Catch:** To make this work smoothly, you usually need the ability to pre-fill the form fields via URL parameters. For example, if the URL `https://bank.com/profile?email=hacker@evil.com` automatically populates the email field, you only need to clickjack the "Save" button.

## How to Exploit It
- **Step-by-step walkthrough:**
  1. **Pre-fill the data:** Find a way to load the target iframe with your malicious data already entered. This is often done via GET parameters (`?email=attacker@evil.com`).
  2. **Align the button:** Use CSS to align the decoy button exactly over the target's "Save" or "Update" button.
  3. **Execute:** Send the payload to the victim. When they click the button, the form is submitted with the pre-filled malicious data and the dynamically generated, perfectly valid CSRF token.

- **Advanced Exploitation: DOM XSS via CSRF via Clickjacking**
  Sometimes, you find a Stored XSS vulnerability in a profile field, but it's protected by CSRF. You use Clickjacking to force the victim to update their profile with the XSS payload. When their profile saves, the XSS executes in their authenticated session!

## Real-World Example
An attacker targeted a password manager web interface. Changing the master password required a CSRF token, making standard CSRF impossible. However, the site lacked `X-Frame-Options`. Furthermore, the password change form accepted the new password via a URL parameter (`/change_password?new=Hacked123`). The attacker framed this specific URL and clickjacked the "Confirm Change" button. When the victim clicked a decoy button on the attacker's site, the password was changed, bypassing the anti-CSRF token entirely.

## How to Fix It
- **Developer remediation:**
  1. **Frame Blocking:** Anti-CSRF tokens do not protect against UI Redressing. You must implement `Content-Security-Policy: frame-ancestors 'none'` to block framing.
  2. **SameSite Cookies:** Setting session cookies to `SameSite=Lax` or `Strict` ensures that even if the site is framed, the POST request triggered by the click will not contain the user's session cookie, causing the backend to reject the request as unauthenticated.

## Chaining Opportunities
- This vuln + [[10.01 What is CSRF?]] → The definitive bypass for anti-CSRF tokens when framing is allowed.
- This vuln + [[23.01 Stored XSS Basics]] → Using Clickjacking to force a victim to store an XSS payload on their own account.

## Related Notes
- [[28.02 Basic iframe Clickjacking]]
- [[28.06 Defense — X-Frame-Options, CSP frame-ancestors]]
