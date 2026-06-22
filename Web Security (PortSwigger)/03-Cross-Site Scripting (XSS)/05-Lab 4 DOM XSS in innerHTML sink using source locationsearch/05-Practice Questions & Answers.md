---
course: Web Security
topic: Cross-Site Scripting (XSS)
tags: [web-security]
---

## Practice Questions & Answers

**Q1. Explain the concept of DOM-based XSS and why it is different from traditional XSS attacks.**

DOM-based Cross-Site Scripting (XSS) occurs when a web application generates dynamic content using user-supplied input without proper validation or sanitization. Unlike traditional XSS attacks where the malicious script is stored on the server or injected via a third-party source, DOM-based XSS relies solely on the client-side JavaScript. The attacker manipulates the DOM elements directly, often through URL parameters or other client-side inputs, to inject malicious scripts into the page.

**Q2. How would you identify a potential DOM-based XSS vulnerability in a web application?**

To identify a potential DOM-based XSS vulnerability, follow these steps:

1. **Map the Application**: Understand the structure and flow of the application.
2. **Inject Test Strings**: Input unique strings into various fields (like search boxes) and observe if they are reflected back in the page.
3. **Inspect the Page Source**: Use browser developer tools to inspect the page source and see if the input is being used in JavaScript to modify the DOM.
4. **Check for User-Controlled Inputs**: Look for any user-controlled inputs that are used in JavaScript to manipulate the DOM, such as `innerHTML`, `document.write`, etc.

For example, if you input a unique string into a search box and see it reflected in the page source within a JavaScript context, it may indicate a potential vulnerability.

**Q3. How would you exploit a DOM-based XSS vulnerability using the `location.search` parameter?**

To exploit a DOM-based XSS vulnerability using the `location.search` parameter, you need to craft a payload that will be executed when the page loads. Here’s a step-by-step guide:

1. **Identify the Vulnerable Parameter**: Determine which parameter in the URL is being used to modify the DOM.
2. **Craft the Payload**: Create a payload that will be executed when the page loads. For example, to trigger an alert, you can use an image tag with an `onerror` attribute:

   ```html
   <img src="nonexistent.jpg" onerror="alert('XSS')">
   ```

3. **Inject the Payload**: Append the crafted payload to the `location.search` parameter in the URL. For instance:

   ```
   http://example.com/search?query=<img%20src=%22nonexistent.jpg%22%20onerror=%22alert(%27XSS%27)%22>
   ```

4. **Test the Exploit**: Navigate to the URL with the injected payload and verify that the alert is triggered.

**Q4. What recent real-world examples or CVEs demonstrate the impact of DOM-based XSS vulnerabilities?**

One notable example is the DOM-based XSS vulnerability found in the popular web analytics tool Google Tag Manager (GTM). In 2020, researchers discovered that GTM could be exploited to inject malicious scripts into websites using GTM. This vulnerability allowed attackers to bypass certain security measures and execute arbitrary JavaScript code on affected sites.

Another example is CVE-2021-21972, which was a DOM-based XSS vulnerability in the WordPress plugin WPML. Attackers could exploit this vulnerability by injecting malicious scripts into the URL parameters, leading to unauthorized actions on the site.

These examples highlight the importance of properly validating and sanitizing user inputs in JavaScript to prevent such vulnerabilities.

**Q5. How would you configure a web application to mitigate DOM-based XSS vulnerabilities?**

To mitigate DOM-based XSS vulnerabilities, follow these best practices:

1. **Input Validation**: Validate all user inputs to ensure they conform to expected formats and values.
2. **Sanitize Inputs**: Sanitize user inputs before using them in JavaScript to modify the DOM. Use libraries like DOMPurify to sanitize HTML content.
3. **Use Content Security Policy (CSP)**: Implement a strict CSP to limit the sources from which scripts can be loaded and executed.
4. **Escape Output**: Escape user inputs when inserting them into the DOM to prevent them from being interpreted as executable code. Use methods like `textContent` instead of `innerHTML`.
5. **Regular Audits**: Regularly audit your application for potential vulnerabilities using automated tools and manual testing.

By following these practices, you can significantly reduce the risk of DOM-based XSS attacks in your web applications.

---
<!-- nav -->
[[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/05-Lab 4 DOM XSS in innerHTML sink using source locationsearch/04-Conclusion|Conclusion]] | [[Web Security (PortSwigger)/03-Cross-Site Scripting (XSS)/05-Lab 4 DOM XSS in innerHTML sink using source locationsearch/00-Overview|Overview]]
