---
course: Web Security
topic: Clickjacking
tags: [web-security]
---

## Frame-Busting Scripts

Frame-busting scripts are designed to prevent a webpage from being loaded within an `<iframe>`. These scripts typically check if the current window is the topmost window and, if not, redirect the user to the top-level window. However, these scripts are considered a weak defense due to their limitations.

### What Are Frame-Busting Scripts?

Frame-busting scripts are JavaScript functions that check if the current webpage is being loaded within an `<iframe>`. If it detects that it is being framed, the script redirects the user to the top-level window, effectively breaking out of the frame.

#### Example of a Frame-Busting Script

```javascript
if (top !== self) {
    top.location = self.location;
}
```

This script checks if the `top` window is different from the `self` window. If they are different, it means the page is being loaded within an `<iframe>`, and the script redirects the `top` window to the current URL.

### Why Are Frame-Busting Scripts Considered Weak?

Despite their intentions, frame-busting scripts are often ineffective against determined attackers. There are several reasons for this:

1. **JavaScript Can Be Disabled**: Users can disable JavaScript in their browsers, rendering the frame-busting script useless.
2. **CSS Manipulation**: Attackers can use CSS to hide the frame-busting script or make it less effective.
3. **Sandbox Attribute**: The `sandbox` attribute in the `<iframe>` element can neutralize the effect of frame-busting scripts.

### Real-World Example of Frame-Busting Scripts

In 2[... truncated for brevity ...]

### How to Prevent / Defend Against Clickjacking

Defending against clickjacking requires a combination of server-side and client-side measures. Here are some effective strategies:

#### Server-Side Measures

1. **X-Frame-Options Header**:
   - The `X-Frame-Options` header is a simple and effective way to prevent clickjacking. It instructs the browser whether to allow a page to be rendered within a frame.
   - Possible values include `DENY`, `SAMEORIGIN`, and `ALLOW-FROM uri`.

   ```http
   HTTP/1.1 200 OK
   Content-Type: text/html
   X-Frame-Options: DENY
   ```

2. **Content Security Policy (CSP)**:
   - CSP provides a more granular control over the resources that can be loaded within a frame.
   - The `frame-ancestors` directive specifies which origins are allowed to embed the resource.

   ```http
   HTTP/1.1 200 OK
   Content-Type: text/html
   Content-Security-Policy: frame-ancestors 'none';
   ```

#### Client-Side Measures

1. **JavaScript Frame-Busting**:
   - While not foolproof, JavaScript frame-busting can still provide an additional layer of protection.
   - Ensure that the script is placed at the beginning of the document to maximize its effectiveness.

   ```javascript
   if (top !== self) {
       top.location = self.location;
   }
   ```

2. **CSS Styling**:
   - Use CSS to ensure that the `<iframe>` is not hidden or manipulated by attackers.
   - Avoid using `display: none;` or `visibility: hidden;` unless absolutely necessary.

#### Secure Coding Practices

1. **Input Validation**:
   - Validate all user inputs to prevent malicious data from being processed.
   - Use server-side validation to ensure that inputs are safe and valid.

2. **Output Encoding**:
   - Encode all outputs to prevent XSS attacks.
   - Use libraries like `OWASP Java Encoder` or `Microsoft AntiXSS Library` to encode outputs.

#### Detection and Prevention Tools

1. **Web Application Vulnerability Scanners**:
   - Automated tools like Burp Suite, OWASP ZAP, and Acunetix can help detect clickjacking vulnerabilities.
   - These tools crawl your web application and identify potential security issues.

2. **Security Headers**:
   - Use tools like `securityheaders.com` to check the security headers of your website.
   - Ensure that `X-Frame-Options` and `Content-Security-Policy` headers are correctly configured.

### Hands-On Experience with Clickjacking

To gain practical experience with clickjacking, consider the following labs:

- **PortSwigger Web Security Academy**: Offers a comprehensive course on web security, including clickjacking.
- **OWASP Juice Shop**: A deliberately insecure web application for practicing web security skills.
- **DVWA (Damn Vulnerable Web Application)**: A PHP/MySQL web application that demonstrates insecure coding practices.
- **WebGoat**: An interactive training application that teaches web security principles.

By working through these labs, you can gain a deeper understanding of how clickjacking works and how to defend against it.

### Conclusion

Clickjacking is a sophisticated attack vector that exploits the trust users have in their web browsers and the websites they visit. By understanding the mechanics of clickjacking and implementing robust defensive measures, you can significantly reduce the risk of falling victim to these attacks. Always stay vigilant and keep your web applications secure.

---

This expanded chapter covers the essential aspects of clickjacking, providing a deep dive into the concepts, real-world examples, and practical defenses. The detailed explanations and code snippets ensure a comprehensive understanding of the topic.

---
<!-- nav -->
[[10-Finding Clickjacking Vulnerabilities|Finding Clickjacking Vulnerabilities]] | [[Web Security (PortSwigger)/05-Clickjacking/01-Clickjacking Complete Guide/00-Overview|Overview]] | [[12-Hands-On Labs|Hands-On Labs]]
