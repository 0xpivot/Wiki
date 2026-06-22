---
course: Web Security
topic: Clickjacking
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what a clickjacking vulnerability is and how it works.**

Clickjacking, also known as UI redressing, is an attack where a user is tricked into clicking on a hidden UI element that performs an unintended action. The attacker overlays a legitimate-looking interface on top of a hidden iframe containing the target application. When the user interacts with the visible elements, they inadvertently interact with the hidden iframe, performing actions like deleting an account or liking a post on a social media platform. This can lead to various malicious outcomes, such as data theft or unauthorized actions.

**Q2. How can you identify if an application is vulnerable to clickjacking attacks from a black box perspective?**

To identify if an application is vulnerable to clickjacking attacks from a black box perspective, you should:

1. Map the application by visiting all accessible pages.
2. Check the HTTP response headers for the presence of `X-Frame-Options` and `Content-Security-Policy` headers.
   - `X-Frame-Options`: Should be set to `DENY` or `SAMEORIGIN`.
   - `Content-Security-Policy`: Should include the `frame-ancestors` directive set to `none` or `self`.

If these headers are missing or set insecurely, the application may be vulnerable to clickjacking attacks.

**Q3. How can you exploit a clickjacking vulnerability? Provide an example.**

To exploit a clickjacking vulnerability, follow these steps:

1. Identify a vulnerable page with an actionable item (e.g., a delete account button).
2. Create an HTML page with an iframe that loads the vulnerable page.
3. Use CSS to hide the iframe and overlay it with a malicious interface.
4. Ensure the malicious interface aligns with the actionable item in the iframe.

Here’s an example payload:

```html
<!DOCTYPE html>
<html>
<head>
<style>
  iframe {
    position: absolute;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    z-index: 2;
    opacity: 0.00001;
  }
  .overlay {
    position: absolute;
    top: 50px; /* Adjust to match the position of the delete button */
    left: 50px; /* Adjust to match the position of the delete button */
    z-index: 1;
  }
</style>
</head>
<body>
<iframe src="http://vulnerable-app.com/delete-account"></iframe>
<div class="overlay">
  <button onclick="alert('Clicked!')">Click Me</button>
</div>
</body>
</html>
```

When a user clicks on the "Click Me" button, they are actually clicking on the delete account button in the hidden iframe.

**Q4. What are some recent real-world examples of clickjacking attacks?**

One notable example is the clickjacking worm that affected Facebook in 2009. Users were tricked into posting spam messages on their profiles by clicking on a seemingly innocent "continue" button. The attack used an invisible iframe to load the user's active Facebook session and posted a spam message when the user clicked the button. This led to hundreds of thousands of users unknowingly spreading the spam message.

Another example is the clickjacking attack on LinkedIn in 2016, where users were tricked into joining groups by clicking on a button that appeared to be a "like" button. Instead, the click resulted in joining a group, which could be used for phishing or other malicious activities.

**Q5. How can you prevent clickjacking vulnerabilities?**

To prevent clickjacking vulnerabilities, you can use the following defense mechanisms:

1. **X-Frame-Options Header**: Set this header to `DENY` or `SAMEORIGIN` to prevent the page from being framed.
   ```http
   X-Frame-Options: DENY
   ```

2. **Content Security Policy (CSP)**: Use the `frame-ancestors` directive to control who can frame the page.
   ```http
   Content-Security-Policy: frame-ancestors 'none'
   ```

3. **SameSite Cookies**: Set the `SameSite` attribute to `Strict` or `Lax` to prevent the browser from sending cookies in cross-site requests.
   ```http
   Set-Cookie: name=value; SameSite=Strict
   ```

By combining these defenses, you can create a robust protection against clickjacking attacks.

---
<!-- nav -->
[[Web Security (PortSwigger)/05-Clickjacking/01-Clickjacking Complete Guide/19-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/05-Clickjacking/01-Clickjacking Complete Guide/00-Overview|Overview]]
