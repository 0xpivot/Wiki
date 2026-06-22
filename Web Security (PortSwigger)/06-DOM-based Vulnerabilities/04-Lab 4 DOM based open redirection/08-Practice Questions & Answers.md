---
course: Web Security
topic: DOM-based Vulnerabilities
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain what a DOM-based open redirection vulnerability is and how it differs from traditional server-side open redirection vulnerabilities.**

DOM-based open redirection occurs when a web application uses untrusted input to construct a URL within the context of the Document Object Model (DOM). Unlike traditional server-side open redirection, where the server directly controls the redirection logic, DOM-based vulnerabilities rely on client-side JavaScript to process and redirect the user. This makes it harder to detect and mitigate since the redirection happens entirely on the client side.

**Q2. How would you exploit a DOM-based open redirection vulnerability? Provide a step-by-step guide.**

To exploit a DOM-based open redirection vulnerability, follow these steps:

1. Identify the JavaScript code that constructs URLs using user-controlled input.
2. Determine the specific parameter or variable used in the URL construction.
3. Craft a URL that includes the parameter with a value pointing to a malicious site.
4. Ensure the crafted URL triggers the JavaScript code responsible for the redirection.
5. Test the crafted URL by navigating to it and observing whether the redirection occurs as expected.

For example, if the JavaScript code uses `location.href` to redirect based on a query parameter `url`, you might craft a URL like `https://example.com/?url=https://malicious-site.com`.

**Q3. Why is it important to validate and sanitize user input in JavaScript code that constructs URLs?**

Validating and sanitizing user input in JavaScript code that constructs URLs is crucial because it prevents attackers from injecting malicious URLs that can redirect users to harmful sites. Without proper validation and sanitization, an attacker can manipulate the input to perform actions such as phishing attacks, spreading malware, or stealing sensitive information. By ensuring that only trusted and safe URLs are used, developers can protect their users from potential security threats.

**Q4. How can you prevent DOM-based open redirection vulnerabilities in your web applications?**

To prevent DOM-based open redirection vulnerabilities, consider the following best practices:

1. **Validate Input**: Always validate user input to ensure it conforms to expected formats and values.
2. **Sanitize Input**: Sanitize user input to remove or escape potentially dangerous characters or patterns.
3. **Use Trusted Sources**: Use trusted sources for URLs instead of relying on user-provided input.
4. **Content Security Policy (CSP)**: Implement a Content Security Policy to restrict the sources from which content can be loaded.
5. **Avoid Using User Input Directly**: Avoid using user input directly in URL construction; instead, use it to fetch predefined URLs from a secure source.

**Q5. Reference a recent real-world example of a DOM-based open redirection vulnerability and explain how it was exploited.**

One notable example is the DOM-based open redirection vulnerability found in various WordPress plugins. For instance, a vulnerability in the WP Travel plugin allowed attackers to craft URLs that would redirect users to malicious sites. The vulnerability was due to the plugin's JavaScript code using unvalidated user input to construct URLs.

To exploit this vulnerability, an attacker would create a URL like `https://vulnerable-site.com/?redirect=https://malicious-site.com`. When a user clicked on this link, the JavaScript code would execute and redirect the user to the malicious site, potentially leading to phishing attacks or other security issues.

This example highlights the importance of validating and sanitizing user input in JavaScript code to prevent such vulnerabilities.

---
<!-- nav -->
[[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/04-Lab 4 DOM based open redirection/07-Understanding DOM-Based Vulnerabilities|Understanding DOM-Based Vulnerabilities]] | [[Web Security (PortSwigger)/06-DOM-based Vulnerabilities/04-Lab 4 DOM based open redirection/00-Overview|Overview]]
