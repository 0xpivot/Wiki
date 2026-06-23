---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what a DOM-based XSS vulnerability is and how it differs from traditional XSS vulnerabilities.**

DOM-based Cross-Site Scripting (XSS) occurs when a web application incorporates untrusted data into the DOM without proper validation or escaping. Unlike traditional XSS attacks where the payload is injected via a server response, DOM-based XSS involves client-side scripts that manipulate the Document Object Model (DOM). This means the attack is executed entirely on the client side, often through user-controllable inputs like URL parameters.

**Q2. How does the jQuery `location.search` source contribute to a DOM-based XSS vulnerability?**

The `location.search` property in JavaScript returns the query string part of the URL, including the question mark. If a web application uses this value directly to modify the DOM, such as setting an attribute of an HTML element, and does not properly sanitize or escape the input, it can lead to a DOM-based XSS vulnerability. An attacker can inject malicious JavaScript code into the URL, which is then executed when the page loads.

**Q3. How would you exploit a DOM-based XSS vulnerability in the `href` attribute of an anchor tag using `location.search`?**

To exploit a DOM-based XSS vulnerability in the `href` attribute of an anchor tag using `location.search`, follow these steps:

1. Identify the parameter in the URL that is used to set the `href` attribute of the anchor tag.
2. Inject a JavaScript payload into this parameter. For example, if the URL is `http://example.com/?returnPath=http://example.com/page`, you can change it to `http://example.com/?returnPath=javascript:alert(document.cookie)`.

This will cause the `href` attribute of the anchor tag to be set to `javascript:alert(document.cookie)`. When the user clicks on the anchor tag, the JavaScript payload will execute, displaying the user’s cookies.

**Q4. What recent real-world examples or CVEs demonstrate the impact of DOM-based XSS vulnerabilities?**

One notable example is the CVE-2019-16758, which affected several versions of the popular web analytics tool Piwik (now known as Matomo). The vulnerability allowed attackers to inject arbitrary JavaScript code into the DOM via the `location.search` parameter, leading to potential theft of sensitive information such as session cookies. This demonstrates the importance of proper input sanitization and validation in web applications to prevent such vulnerabilities.

**Q5. How can developers mitigate the risk of DOM-based XSS vulnerabilities in their applications?**

Developers can mitigate the risk of DOM-based XSS vulnerabilities by implementing the following best practices:

1. **Input Validation**: Ensure that all user inputs are validated and sanitized before being incorporated into the DOM.
2. **Content Security Policy (CSP)**: Use CSP headers to restrict the sources from which scripts can be loaded, reducing the risk of executing unauthorized scripts.
3. **Escaping User Input**: Use libraries or functions that automatically escape user inputs to ensure they are treated as plain text rather than executable code.
4. **Code Reviews and Testing**: Regularly review and test code for security vulnerabilities, including automated testing with tools designed to detect XSS vulnerabilities.

By following these practices, developers can significantly reduce the risk of DOM-based XSS vulnerabilities in their applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/06-Lab 5 DOM XSS in jQuery anchor href attribute sink using locationsearch source/03-Understanding DOM-based XSS|Understanding DOM-based XSS]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/06-Lab 5 DOM XSS in jQuery anchor href attribute sink using locationsearch source/00-Overview|Overview]]
