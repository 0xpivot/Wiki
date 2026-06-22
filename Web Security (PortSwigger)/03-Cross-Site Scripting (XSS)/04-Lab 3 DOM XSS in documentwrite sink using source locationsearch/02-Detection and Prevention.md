---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Detection and Prevention

### How to Detect DOM-Based XSS

Detecting DOM-based XSS requires a thorough analysis of the client-side code. Here are some steps to identify potential vulnerabilities:

1. **Review Client-Side Code**: Look for any instances where untrusted input is used to construct DOM nodes or attributes.
2. **Use Developer Tools**: Utilize browser developer tools to inspect the DOM and monitor network traffic.
3. **Automated Scanning**: Use automated tools like Burp Suite, OWASP ZAP, or commercial scanners to identify potential vulnerabilities.

### How to Prevent DOM-Based XSS

Preventing DOM-based XSS involves ensuring that all untrusted input is properly sanitized before being used in the DOM. Here are some best practices:

1. **Sanitize Input**: Use a library or framework that provides built-in sanitization functions. For example, in JavaScript, you can use libraries like DOMPurify.
2. **Escape Output**: Ensure that any user input is properly escaped before being written to the DOM. This can be done using methods like `textContent` instead of `innerHTML`.
3. **Content Security Policy (CSP)**: Implement a Content Security Policy to restrict the sources from which scripts can be loaded. This can help mitigate the impact of XSS attacks.

### Secure Code Example

Here is an example of how to securely handle user input in the context of `document.write` and `location.search`:

```javascript
// Secure code
var searchTerm = location.search.substring(1); // Extract the query string
var imgElement = document.createElement('img');
imgElement.src = 'resources/images/tracker.gif';
imgElement.alt = searchTerm;
document.body.appendChild(imgElement);
```

In this example, we create an `img` element and set its `src` and `alt` attributes separately. This ensures that the user input is not directly written into the HTML document, reducing the risk of XSS.

### Content Security Policy (CSP)

Implementing a Content Security Policy (CSP) can further enhance the security of your web application. CSP allows you to specify trusted sources of content, making it harder for attackers to inject malicious scripts.

Here is an example of a CSP header:

```http
Content-Security-Policy: default-src 'self'; script-src 'self' https://trusted.cdn.com; img-src 'self' data:;
```

This CSP header specifies that scripts can only be loaded from the same origin or from a trusted CDN, and images can only be loaded from the same origin or from data URIs.

### Real-World Example of CSP

In 2020, a major e-commerce platform implemented a strict CSP to mitigate the risk of XSS attacks. By specifying trusted sources for scripts and images, the platform was able to significantly reduce the attack surface and protect its users from malicious scripts.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/04-Lab 3 DOM XSS in documentwrite sink using source locationsearch/01-Introduction to Cross-Site Scripting (XSS)|Introduction to Cross-Site Scripting (XSS)]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/04-Lab 3 DOM XSS in documentwrite sink using source locationsearch/00-Overview|Overview]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/04-Lab 3 DOM XSS in documentwrite sink using source locationsearch/03-Hands-On Practice|Hands-On Practice]]
