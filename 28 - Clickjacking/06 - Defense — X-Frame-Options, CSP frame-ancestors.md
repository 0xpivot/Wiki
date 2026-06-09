---
tags: [vapt, clickjacking, defense, beginner]
difficulty: beginner
module: "28 - Clickjacking"
topic: "28.06 Defense — X-Frame-Options, CSP frame-ancestors"
---

# 28.06 — Defense: X-Frame-Options, CSP frame-ancestors

## What is it?
Defending against Clickjacking relies almost entirely on preventing your web application from being rendered inside an `<iframe>`, `<frame>`, `<object>`, or `<embed>` tag by a malicious, third-party website.

Because the attack relies on the browser overlaying the target site on top of the attacker's site, you must instruct the victim's browser to refuse to render your site if it detects it is being framed. 

There are two primary HTTP response headers used to achieve this: the modern **Content-Security-Policy (CSP) `frame-ancestors`** directive, and the legacy **`X-Frame-Options` (XFO)** header. 

Think of it like a vampire. A vampire cannot enter a house unless explicitly invited. By default, older web browsers let anyone frame your website. By implementing these headers, you are turning your website into a vampire—it will refuse to enter an iframe unless the parent domain explicitly matches an "invited" list.

## Key Defensive Strategies

### 1. CSP: frame-ancestors (The Modern Standard)
The `Content-Security-Policy` header is the most robust and flexible way to control framing. The `frame-ancestors` directive specifies which parent URLs may frame the current resource.

- **Block all framing (Most Secure):**
  If your application never needs to be embedded anywhere, block it completely.
  `Content-Security-Policy: frame-ancestors 'none';`

- **Allow framing only by your own site:**
  If your application uses iframes internally (e.g., `dashboard.com` framing `dashboard.com/widget`), use the `self` directive.
  `Content-Security-Policy: frame-ancestors 'self';`

- **Allow framing by specific trusted domains:**
  If you are building a widget meant to be embedded on specific partner sites, explicitly whitelist them.
  `Content-Security-Policy: frame-ancestors https://trusted-partner.com https://another-partner.com;`

### 2. X-Frame-Options (The Legacy Fallback)
Before CSP was standardized, browsers used the `X-Frame-Options` header. While CSP is superior (it supports multiple domains and exact path matching), you should still include XFO to protect users on very old browsers (like IE11). Modern browsers will prioritize CSP `frame-ancestors` if both are present.

- **Block all framing:**
  `X-Frame-Options: DENY`

- **Allow framing only by your own site:**
  `X-Frame-Options: SAMEORIGIN`

*(Note: The `ALLOW-FROM` directive for XFO is deprecated and ignored by most modern browsers. If you need to allow specific domains, you MUST use CSP).*

### 3. SameSite Cookies (Defense in Depth)
Clickjacking relies on the fact that when the victim clicks the hidden iframe, the browser automatically attaches their session cookie to the request. 

By setting the `SameSite` attribute on your session cookies, you prevent the browser from sending the cookie if the request originates from a third-party context (like an attacker's iframe).
- **The Fix:** Set `Set-Cookie: session=123; SameSite=Lax; Secure; HttpOnly`.
- **The Result:** Even if the attacker successfully frames your site and the user clicks the button, the resulting POST request will not contain the session cookie. The backend will treat the request as unauthenticated and reject it.

## ASCII Diagram
```text
================================================================================
                    HOW BROWSER DEFENSES BLOCK CLICKJACKING
================================================================================

[Attacker's Server]
Hosts: `evil.html`
Contains: `<iframe src="https://bank.com/transfer"></iframe>`

[Victim's Browser (Processing evil.html)]

1. Browser reads `<iframe src="...">`
2. Browser sends HTTP GET request to `https://bank.com/transfer`
3. Bank.com responds with HTML and Headers:
   HTTP/1.1 200 OK
   Content-Security-Policy: frame-ancestors 'none'
   X-Frame-Options: DENY

4. Browser Security Check:
   Browser asks: "Who is the parent window?"
   Answer: "evil.com"
   Browser asks: "Does the CSP allow evil.com?"
   Answer: "No, it says 'none'."

5. Action Taken:
   The browser REFUSES to render the HTML. 
   Instead of the bank page, the iframe displays a blank screen or a browser error:
   [ x ] "bank.com refused to connect."

[Result]
The attacker's UI Redressing illusion is broken. The attack fails completely.
================================================================================
```

## Developer Checklist
- [ ] Is `Content-Security-Policy: frame-ancestors 'none'` (or `'self'`) applied globally across all HTML responses?
- [ ] Is `X-Frame-Options: DENY` (or `SAMEORIGIN`) applied globally as a fallback for legacy browsers?
- [ ] Are session cookies protected with the `SameSite=Lax` or `SameSite=Strict` attribute?
- [ ] Have you ensured that the headers are applied to *all* pages, not just the login page? (Clickjacking often targets account settings or transaction pages).

## Related Notes
- [[28.01 What is Clickjacking?]]
- [[28.02 Basic iframe Clickjacking]]
```

I will create `28.02`, `28.03`, `28.04`, `28.05`, `28.06` and update `VAPT-Vault-Plan.md`. Then I will proceed to Module 29: WebSockets. 

Let's do Module 28 first. 
The files are created. Now I'll update the plan file. Then I'll look at Module 29.
Tools needed: `replace_file_content`.
