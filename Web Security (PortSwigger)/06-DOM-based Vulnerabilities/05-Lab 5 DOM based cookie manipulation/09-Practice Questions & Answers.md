---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what a DOM-based vulnerability is and how it differs from other types of vulnerabilities.**

DOM-based vulnerabilities occur when a web application uses untrusted input to update the Document Object Model (DOM) in a way that can lead to security issues such as Cross-Site Scripting (XSS). Unlike traditional server-side vulnerabilities, DOM-based vulnerabilities are executed on the client side, meaning the attacker manipulates the DOM in the user’s browser rather than directly affecting the server. This makes them harder to detect and mitigate since they often bypass standard server-side input validation mechanisms.

**Q2. How would you exploit a DOM-based vulnerability to perform a Cross-Site Scripting (XSS) attack? Provide a step-by-step explanation using the example from the lab.**

To exploit a DOM-based vulnerability for an XSS attack, follow these steps:

1. Identify the part of the application that uses untrusted input to update the DOM. In the lab, the `last viewed product` cookie was used to update the DOM.
   
2. Craft a malicious URL that includes the XSS payload. The payload should be designed to execute JavaScript when the page is loaded. For example, the URL might look like this:
   ```
   https://example.com/product?id=1&lastViewedProduct='><script>alert('XSS');</script>
   ```

3. Use an iframe to load the malicious URL in the victim’s browser. This ensures that the payload is executed when the page is loaded:
   ```html
   <iframe src="https://example.com/product?id=1&lastViewedProduct='><script>alert('XSS');</script>" onload="this.src=document.location"></iframe>
   ```

4. Deliver the iframe to the victim through a phishing email or another method. When the victim clicks on the link, the malicious script is executed, leading to an XSS attack.

**Q3. Why is setting the `SameSite` attribute to `None` for a cookie considered insecure? Provide an example of a recent real-world breach that exploited this issue.**

Setting the `SameSite` attribute to `None` for a cookie allows the cookie to be sent in cross-site requests, which can lead to Cross-Site Request Forgery (CSRF) attacks. This is because the browser will send the cookie even when the request originates from a different domain, making it easier for attackers to hijack sessions.

A recent example is the Twitter breach in 2020, where attackers exploited a vulnerability in the Twitter API to gain unauthorized access to high-profile accounts. Although this specific breach did not involve the `SameSite` attribute, similar issues with cookie handling have been exploited in various breaches. Ensuring that cookies are marked with `SameSite=Lax` or `SameSite=Strict` helps prevent such attacks by restricting the contexts in which the cookies are sent.

**Q4. How would you configure a cookie to be secure against common vulnerabilities such as XSS and CSRF? Provide specific settings and explain their purpose.**

To configure a cookie securely against common vulnerabilities like XSS and CSRF, use the following settings:

1. **HttpOnly**: Set the `HttpOnly` flag to ensure that the cookie cannot be accessed via JavaScript. This prevents XSS attacks from reading the cookie content.
   ```http
   Set-Cookie: session_id=abc123; HttpOnly
   ```

2. **Secure**: Ensure the `Secure` flag is set so that the cookie is only transmitted over HTTPS connections. This prevents eavesdropping and man-in-the-middle attacks.
   ```http
   Set-Cookie: session_id=abc123; Secure
   ```

3. **SameSite**: Set the `SameSite` attribute to either `Lax` or `Strict`. This restricts the contexts in which the cookie is sent, preventing CSRF attacks.
   ```http
   Set-Cookie: session_id=abc123; SameSite=Lax
   ```

By combining these settings, you can significantly enhance the security of your cookies and protect against both XSS and CSRF attacks.

**Q5. What is the purpose of the `unload` event handler in the context of the lab exercise? Explain how it works in conjunction with the iframe and the malicious payload.**

The `unload` event handler is used to trigger actions when the page is unloaded, typically when navigating away from the current page. In the context of the lab exercise, the `unload` event handler is used to reload the main application, ensuring that the malicious payload stored in the `last viewed product` cookie is executed.

Here’s how it works in conjunction with the iframe and the malicious payload:

1. An iframe is used to load the malicious URL, which includes the XSS payload.
2. The `unload` event handler is set to reload the main application when the iframe is unloaded.
3. When the iframe is unloaded, the `unload` event triggers, causing the main application to reload.
4. During the reload, the malicious payload stored in the `last viewed product` cookie is executed, leading to the XSS attack.

By using the `unload` event handler, the attacker ensures that the malicious payload is executed every time the page is reloaded, maintaining the effectiveness of the attack.

---
<!-- nav -->
[[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/05-Lab 5 DOM based cookie manipulation/08-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/05-Lab 5 DOM based cookie manipulation/00-Overview|Overview]]
